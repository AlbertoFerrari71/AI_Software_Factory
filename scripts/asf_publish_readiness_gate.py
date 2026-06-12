from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from asf_latest_report_resolver import resolve_latest_report


DEFAULT_BRIDGE = r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command"
PASS_STATUSES = {"PASS"}
FAIL_STATUSES = {"FAIL", "STOP", "INCOHERENT_REPORT", "AMBIGUOUS_REPORT", "MISSING_REPORT", "MISSING_BRIDGE"}


def run_git_status(root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "--no-pager", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {"available": False, "exit_code": None, "entries": [], "error": str(exc)}
    entries = [line for line in result.stdout.splitlines() if line.strip()]
    return {"available": True, "exit_code": result.returncode, "entries": entries, "error": result.stderr.strip()}


def has_failed_checks(report: dict[str, Any] | None) -> bool:
    if not report:
        return True
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        return True
    for check in checks:
        if not isinstance(check, dict):
            return True
        status = str(check.get("status", "")).upper()
        if status not in {"PASS", "PASSED", "OK", "WARNING", "SKIPPED"}:
            return True
    return False


def mentions_raw_payload(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    text = json.dumps(report, sort_keys=True).casefold()
    blocked = ("raw provider payload", "raw request", "raw response", "authorization:", "bearer ")
    return any(fragment in text for fragment in blocked)


def evaluate_readiness(
    *,
    bridge: Path,
    expected_step: str | None = None,
    report_json: Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    root = root or Path.cwd()
    if report_json:
        payload = json.loads(report_json.read_text(encoding="utf-8"))
        resolver = {
            "resolution_status": "FOUND",
            "status": str(payload.get("status", "UNKNOWN")).upper(),
            "selected_report": str(report_json),
            "selected_markdown": payload.get("report_markdown_path"),
            "latest_step": payload.get("step_range") or payload.get("step"),
            "warnings": [],
            "report": payload,
            "bridge": str(bridge),
            "expected_step": expected_step,
            "candidates": [],
        }
    else:
        resolver = resolve_latest_report(bridge, expected_step=expected_step)

    report = resolver.get("report") if isinstance(resolver.get("report"), dict) else None
    warnings = list(resolver.get("warnings", []))
    reasons: list[str] = []
    status = str(resolver.get("status") or "").upper()
    resolution = str(resolver.get("resolution_status") or "")
    git_status = run_git_status(root)

    if resolution in {"MISSING", "AMBIGUOUS", "INCOHERENT"} or status in FAIL_STATUSES:
        semaphore = "RED"
        reasons.append("Codex report is missing, ambiguous, incoherent or failed.")
    elif status not in PASS_STATUSES:
        semaphore = "RED"
        reasons.append(f"Codex report status is not PASS: {status or 'UNKNOWN'}.")
    elif has_failed_checks(report):
        semaphore = "RED"
        reasons.append("Report checks are missing or include a failure.")
    elif mentions_raw_payload(report):
        semaphore = "RED"
        reasons.append("Report appears to mention raw provider payload or sensitive authorization text.")
    else:
        semaphore = "GREEN"
        reasons.append("Report is PASS, checks are declared, and no raw payload marker was found.")

    if semaphore == "GREEN" and resolution == "DEGRADED":
        semaphore = "YELLOW"
        reasons.append("Markdown-only report is acceptable for review but not a full JSON sidecar PASS.")
    if semaphore == "GREEN" and report and not bool(report.get("human_gate_required", True)):
        semaphore = "YELLOW"
        reasons.append("human_gate_required is not true; publish still requires Alberto approval.")
    if git_status["available"] and git_status["exit_code"] != 0:
        semaphore = "YELLOW" if semaphore == "GREEN" else semaphore
        warnings.append("git status did not complete cleanly: " + git_status["error"])

    return {
        "semaphore": semaphore,
        "status": status,
        "resolution_status": resolution,
        "reasons": reasons,
        "warnings": warnings,
        "report_path": resolver.get("selected_report"),
        "markdown_path": resolver.get("selected_markdown"),
        "latest_step": resolver.get("latest_step"),
        "human_approval_required_for_publish": True,
        "publish_command_allowed": False,
        "git_status": git_status,
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"publish_readiness: {payload['semaphore']}",
        f"status: {payload['status']}",
        f"resolution_status: {payload['resolution_status']}",
        f"report_path: {payload.get('report_path') or ''}",
        "reasons:",
    ]
    lines.extend(f"- {reason}" for reason in payload["reasons"])
    if payload["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    lines.append("publish_command_allowed: false")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate ASF publish readiness without publishing.")
    parser.add_argument("--bridge", default=DEFAULT_BRIDGE, help="Bridge codex_command folder.")
    parser.add_argument("--expected-step", help="Expected step or range.")
    parser.add_argument("--report-json", help="Explicit Codex report JSON file.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    payload = evaluate_readiness(
        bridge=Path(args.bridge),
        expected_step=args.expected_step,
        report_json=Path(args.report_json) if args.report_json else None,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
