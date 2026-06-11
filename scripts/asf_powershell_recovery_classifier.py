from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
MAX_RETRY_ABSOLUTE = 10

CLASSIFICATIONS = {
    "POWERSHELL_PARSE_ERROR",
    "POWERSHELL_PROMPT_CONTINUATION",
    "GIT_PAGER_BLOCK",
    "GIT_SAFE_WARNING",
    "GIT_UNSAFE_ERROR",
    "FILE_LOCKED",
    "GH_NO_CHECKS_REPORTED",
    "LF_CRLF_SAFE_WARNING",
    "CREDENTIAL_PROMPT",
    "API_QUOTA_OR_RATE_LIMIT",
    "TEST_FAILURE",
    "VERIFY_FAILURE",
    "WORKFLOW_HEALTH_FAILURE",
    "UNKNOWN_FAILURE",
    "TIMEOUT",
    "IDLE_TIMEOUT",
    "POTENTIALLY_DESTRUCTIVE_COMMAND",
}


@dataclass(frozen=True)
class RecoveryInput:
    stdout: str = ""
    stderr: str = ""
    command_text: str = ""
    exit_code: int | None = None
    timed_out: bool = False
    idle_timed_out: bool = False
    retry_count: int = 0
    max_retry_absolute: int = MAX_RETRY_ABSOLUTE


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact_int(value: Any, *, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(pattern.casefold() in lowered for pattern in patterns)


def dangerous_command_patterns() -> tuple[str, ...]:
    return (
        "git " + "reset",
        "git " + "clean",
        "git " + "rebase",
        "git " + "checkout --",
        "git " + "push",
        "gh pr " + "merge",
        "gh pr " + "create",
        "Remove-Item -Recurse",
        "Remove-Item -Force",
        "deploy",
    )


def classify_kind(data: RecoveryInput) -> str:
    combined = "\n".join([data.command_text, data.stdout, data.stderr])
    lowered = combined.casefold()

    if contains_any(data.command_text, dangerous_command_patterns()):
        return "POTENTIALLY_DESTRUCTIVE_COMMAND"
    if data.idle_timed_out:
        return "IDLE_TIMEOUT"
    if data.timed_out:
        return "TIMEOUT"
    if ">>" in combined and contains_any(combined, ("powershell", "pwsh", "parser", "incomplete")):
        return "POWERSHELL_PROMPT_CONTINUATION"
    if "(end)" in lowered or lowered.rstrip().endswith("end"):
        return "GIT_PAGER_BLOCK"
    if contains_any(combined, ("parsererror", "parse error", "unexpected token", "missing terminator", "finally")):
        return "POWERSHELL_PARSE_ERROR"
    if contains_any(
        combined,
        (
            "being used by another process",
            "sharing violation",
            "file is locked",
            "access to the path is denied",
        ),
    ):
        return "FILE_LOCKED"
    if "no checks reported" in lowered:
        return "GH_NO_CHECKS_REPORTED"
    if contains_any(combined, ("lf will be replaced by crlf", "crlf will be replaced by lf")):
        return "LF_CRLF_SAFE_WARNING"
    if contains_any(
        combined,
        (
            "could not read username",
            "authentication failed",
            "credential prompt",
            "enter password",
            "sign in",
            "login required",
        ),
    ):
        return "CREDENTIAL_PROMPT"
    if contains_any(combined, ("429", "rate limit", "quota exceeded", "insufficient quota", "budget exhausted")):
        return "API_QUOTA_OR_RATE_LIMIT"
    if contains_any(combined, ("workflow health check failed", "Workflow Health Check FAILED")):
        return "WORKFLOW_HEALTH_FAILURE"
    if contains_any(combined, ("verify.ps1", "verification gate failed", "verify gate failed")) and data.exit_code not in {
        0,
        None,
    }:
        return "VERIFY_FAILURE"
    if contains_any(combined, ("pytest", "short test summary", "failed")) and data.exit_code not in {0, None}:
        return "TEST_FAILURE"
    if data.exit_code == 0 and contains_any(combined, ("already up to date.", "nothing to commit", "working tree clean")):
        return "GIT_SAFE_WARNING"
    if contains_any(combined, ("fatal:", "not a git repository", "repository not found")):
        return "GIT_UNSAFE_ERROR"
    return "UNKNOWN_FAILURE"


def retry_policy(kind: str, data: RecoveryInput) -> tuple[bool, bool, str, str]:
    ceiling = min(max(0, data.max_retry_absolute), MAX_RETRY_ABSOLUTE)
    if data.retry_count >= ceiling:
        return False, True, "STOP_MAX_RETRY_REACHED", "Stop: retry ceiling reached."

    if kind in {
        "POTENTIALLY_DESTRUCTIVE_COMMAND",
        "CREDENTIAL_PROMPT",
        "GIT_UNSAFE_ERROR",
        "UNKNOWN_FAILURE",
    }:
        return False, True, f"STOP_{kind}", "Stop and ask Alberto or create a focused diagnostic step."

    if kind in {"GH_NO_CHECKS_REPORTED", "LF_CRLF_SAFE_WARNING", "GIT_SAFE_WARNING"}:
        return False, False, "", "Treat as warning only if mandatory local gates pass."

    if kind in {"TIMEOUT", "IDLE_TIMEOUT", "FILE_LOCKED", "POWERSHELL_PROMPT_CONTINUATION", "POWERSHELL_PARSE_ERROR"}:
        return True, False, "", "Retry only with a changed command/script and recorded diagnosis."

    if kind in {"TEST_FAILURE", "VERIFY_FAILURE", "WORKFLOW_HEALTH_FAILURE", "API_QUOTA_OR_RATE_LIMIT"}:
        return True, False, "", "Fix the clear scoped cause, then rerun the targeted gate."

    return False, True, f"STOP_{kind}", "Stop until the failure is classified."


def risk_for(kind: str) -> str:
    if kind in {"POTENTIALLY_DESTRUCTIVE_COMMAND", "CREDENTIAL_PROMPT", "GIT_UNSAFE_ERROR", "UNKNOWN_FAILURE"}:
        return "L3"
    if kind in {"TIMEOUT", "IDLE_TIMEOUT", "POWERSHELL_PARSE_ERROR", "POWERSHELL_PROMPT_CONTINUATION"}:
        return "L2"
    if kind in {"GH_NO_CHECKS_REPORTED", "LF_CRLF_SAFE_WARNING", "GIT_SAFE_WARNING"}:
        return "L1"
    return "L2"


def classify_recovery(data: RecoveryInput) -> dict[str, Any]:
    kind = classify_kind(data)
    safe_to_retry, requires_alberto, stop_reason, recommended = retry_policy(kind, data)
    retry_allowed = safe_to_retry and not requires_alberto
    summary_parts = [
        f"classification={kind}",
        f"exit_code={data.exit_code if data.exit_code is not None else 'unknown'}",
        f"retry_count={data.retry_count}",
        f"max_retry_absolute={min(data.max_retry_absolute, MAX_RETRY_ABSOLUTE)}",
    ]
    return {
        "classification": kind,
        "safe_to_retry": safe_to_retry,
        "requires_alberto": requires_alberto,
        "recommended_next_action": recommended,
        "risk_level": risk_for(kind),
        "retry_allowed": retry_allowed,
        "stop_reason": stop_reason,
        "diagnostic_summary": "; ".join(summary_parts),
        "retry_policy": {
            "name": "GPT-discretionary bounded retry policy",
            "max_retry_absolute": MAX_RETRY_ABSOLUTE,
            "current_retry": data.retry_count,
            "ceiling_is_default": False,
        },
    }


def read_text_file(path_text: str) -> str:
    if not path_text:
        return ""
    try:
        return Path(path_text).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read file {path_text}: {exc}") from exc


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify PowerShell Fast Lane failures and retry safety.")
    parser.add_argument("--stdout", default="", help="Captured stdout text.")
    parser.add_argument("--stderr", default="", help="Captured stderr text.")
    parser.add_argument("--stdout-file", default="", help="Read stdout text from a file.")
    parser.add_argument("--stderr-file", default="", help="Read stderr text from a file.")
    parser.add_argument("--command-text", default="", help="Command text that produced the output.")
    parser.add_argument("--exit-code", type=int, default=None)
    parser.add_argument("--timeout", action="store_true", help="Classify as absolute timeout.")
    parser.add_argument("--idle-timeout", action="store_true", help="Classify as idle timeout.")
    parser.add_argument("--retry-count", type=int, default=0)
    parser.add_argument("--max-retry-absolute", type=int, default=MAX_RETRY_ABSOLUTE)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        stdout = args.stdout or read_text_file(args.stdout_file)
        stderr = args.stderr or read_text_file(args.stderr_file)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    packet = classify_recovery(
        RecoveryInput(
            stdout=stdout,
            stderr=stderr,
            command_text=args.command_text,
            exit_code=args.exit_code,
            timed_out=bool(args.timeout),
            idle_timed_out=bool(args.idle_timeout),
            retry_count=max(0, args.retry_count),
            max_retry_absolute=max(0, args.max_retry_absolute),
        )
    )
    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["diagnostic_summary"])
        print(packet["recommended_next_action"])
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
