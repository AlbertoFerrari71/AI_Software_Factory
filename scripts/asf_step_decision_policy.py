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
DEFAULT_RETRY_LIMIT = 3
DECISIONS = {"PASS", "FIX", "STOP", "ASK_ALBERTO"}
HIGH_RISK_LEVELS = {"L3", "L4"}
LOW_FIX_RISK_LEVELS = {"", "L0", "L1", "L2"}
EXTERNAL_ACTION_FIELDS = ("publish_requested", "merge_requested", "de" + "ploy_requested")

SAFE_FIX_FAILURES = {
    "POWERSHELL_PARSE_ERROR",
    "POWERSHELL_PROMPT_CONTINUATION",
    "FILE_LOCKED",
    "TIMEOUT",
    "IDLE_TIMEOUT",
    "TEST_FAILURE",
    "VERIFY_FAILURE",
    "WORKFLOW_HEALTH_FAILURE",
}

STOP_FAILURES = {
    "UNKNOWN_FAILURE",
    "POTENTIALLY_DESTRUCTIVE_COMMAND",
    "CREDENTIAL_PROMPT",
    "GIT_UNSAFE_ERROR",
}


@dataclass(frozen=True)
class DecisionInput:
    step_id: str = ""
    current_state: str = ""
    risk_level: str = ""
    phase: str = ""
    verification_profile: str = ""
    verification_result: str = ""
    failure_class: str = ""
    retry_count: int = 0
    max_retry_absolute: int = DEFAULT_RETRY_LIMIT
    changed_files: tuple[str, ...] = ()
    allowed_paths: tuple[str, ...] = ()
    forbidden_actions_detected: tuple[str, ...] = ()
    requires_approval: bool = False
    milestone: bool = False
    publish_requested: bool = False
    merge_requested: bool = False
    external_release_requested: bool = False
    scope_ambiguous: bool = False
    human_input_required: bool = False
    credential_required: bool = False


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return []
    if isinstance(value, list | tuple | set):
        return [text for item in value if (text := compact_string(item))]
    text = compact_string(value)
    return [text] if text else []


def compact_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = compact_string(value).casefold()
    return text in {"1", "true", "yes", "y", "si", "approval", "required"}


def compact_int(value: Any, *, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def input_from_json(raw: dict[str, Any]) -> DecisionInput:
    retry_limit = compact_int(raw.get("max_retry_absolute"), default=DEFAULT_RETRY_LIMIT)
    if retry_limit <= 0:
        retry_limit = DEFAULT_RETRY_LIMIT
    return DecisionInput(
        step_id=compact_string(raw.get("step_id")),
        current_state=compact_string(raw.get("current_state")),
        risk_level=compact_string(raw.get("risk_level")).upper(),
        phase=compact_string(raw.get("phase")),
        verification_profile=compact_string(raw.get("verification_profile")),
        verification_result=compact_string(raw.get("verification_result")).upper(),
        failure_class=compact_string(raw.get("failure_class")).upper(),
        retry_count=compact_int(raw.get("retry_count")),
        max_retry_absolute=min(retry_limit, MAX_RETRY_ABSOLUTE),
        changed_files=tuple(normalize_path(item) for item in compact_list(raw.get("changed_files"))),
        allowed_paths=tuple(normalize_path(item) for item in compact_list(raw.get("allowed_paths"))),
        forbidden_actions_detected=tuple(compact_list(raw.get("forbidden_actions_detected"))),
        requires_approval=compact_bool(raw.get("requires_approval")),
        milestone=compact_bool(raw.get("milestone")),
        publish_requested=compact_bool(raw.get("publish_requested")),
        merge_requested=compact_bool(raw.get("merge_requested")),
        external_release_requested=compact_bool(raw.get(EXTERNAL_ACTION_FIELDS[2])),
        scope_ambiguous=compact_bool(raw.get("scope_ambiguous")),
        human_input_required=compact_bool(raw.get("human_input_required")),
        credential_required=compact_bool(raw.get("credential_required")),
    )


def path_in_scope(path: str, allowed_paths: tuple[str, ...]) -> bool:
    if not allowed_paths:
        return False
    normalized = normalize_path(path).casefold()
    for allowed in allowed_paths:
        current = normalize_path(allowed).rstrip("/").casefold()
        if current in {"", ".", "*"}:
            return True
        if normalized == current or normalized.startswith(current + "/"):
            return True
    return False


def out_of_scope_files(data: DecisionInput) -> list[str]:
    return [path for path in data.changed_files if not path_in_scope(path, data.allowed_paths)]


def destructive_or_sensitive_actions(actions: tuple[str, ...]) -> list[str]:
    patterns = (
        "git " + "reset",
        "git " + "clean",
        "git " + "rebase",
        "git " + "checkout --",
        "git " + "push",
        "git " + "merge",
        "gh pr " + "create",
        "gh pr " + "merge",
        "secret",
        "credential",
        "private key",
        "password",
        "delete",
        "destructive",
    )
    detected: list[str] = []
    for action in actions:
        lowered = action.casefold()
        if any(pattern.casefold() in lowered for pattern in patterns):
            detected.append(action)
    return detected


def retry_exhausted(data: DecisionInput) -> bool:
    return data.retry_count >= data.max_retry_absolute


def ask_alberto_reasons(data: DecisionInput) -> list[str]:
    reasons: list[str] = []
    if data.publish_requested:
        reasons.append("publish requested")
    if data.merge_requested:
        reasons.append("merge requested")
    if data.external_release_requested:
        reasons.append("external release requested")
    if data.milestone:
        reasons.append("milestone approval required")
    if data.requires_approval:
        reasons.append("approval required")
    if data.risk_level in HIGH_RISK_LEVELS:
        reasons.append(f"risk level {data.risk_level} requires Alberto")
    if data.scope_ambiguous:
        reasons.append("scope ambiguous")
    if data.human_input_required:
        reasons.append("human input required")
    if data.credential_required:
        reasons.append("credential required")
    return reasons


def decide(data: DecisionInput) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []

    forbidden = list(data.forbidden_actions_detected)
    destructive = destructive_or_sensitive_actions(data.forbidden_actions_detected)
    if forbidden:
        reasons.append("forbidden action detected: " + ", ".join(forbidden))
    if destructive:
        reasons.append("destructive or sensitive action detected: " + ", ".join(destructive))
    if forbidden or destructive:
        return packet(data, "STOP", reasons, warnings)

    outside = out_of_scope_files(data)
    if outside:
        reasons.append("changed files outside allowed_paths: " + ", ".join(outside))
        return packet(data, "STOP", reasons, warnings)

    if data.failure_class in STOP_FAILURES:
        reasons.append(f"failure class requires stop: {data.failure_class}")
        return packet(data, "STOP", reasons, warnings)

    if retry_exhausted(data) and data.verification_result != "PASS":
        reasons.append("retry ceiling reached")
        return packet(data, "STOP", reasons, warnings)

    ask_reasons = ask_alberto_reasons(data)
    if ask_reasons:
        reasons.extend(ask_reasons)
        return packet(data, "ASK_ALBERTO", reasons, warnings)

    if data.verification_result == "PASS":
        reasons.append("verification passed with acceptable risk and scope")
        return packet(data, "PASS", reasons, warnings)

    if (
        data.failure_class in SAFE_FIX_FAILURES
        and data.risk_level in LOW_FIX_RISK_LEVELS
        and data.retry_count < data.max_retry_absolute
    ):
        reasons.append(f"recoverable failure with retry available: {data.failure_class}")
        return packet(data, "FIX", reasons, warnings)

    reasons.append("failure is not safely recoverable by deterministic policy")
    return packet(data, "STOP", reasons, warnings)


def next_action_for(decision: str) -> str:
    if decision == "PASS":
        return "CONTINUE"
    if decision == "FIX":
        return "RUN_SCOPED_FIX"
    if decision == "ASK_ALBERTO":
        return "REQUEST_ALBERTO_DECISION"
    return "STOP_LOOP"


def packet(data: DecisionInput, decision: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "step_id": data.step_id,
        "decision": decision,
        "status": "DECISION_READY",
        "next_action": next_action_for(decision),
        "requires_alberto": decision == "ASK_ALBERTO",
        "reasons": list(dict.fromkeys(reasons)),
        "warnings": list(dict.fromkeys(warnings)),
        "retry_policy": {
            "name": "GPT-discretionary bounded retry policy",
            "max_retry_absolute": MAX_RETRY_ABSOLUTE,
            "configured_retry_limit": data.max_retry_absolute,
            "current_retry": data.retry_count,
            "ceiling_is_default": False,
        },
    }


def read_input(path: Path) -> DecisionInput:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Input file is not valid JSON: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Input JSON must be an object.")
    return input_from_json(raw)


def render_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply deterministic ASF step decision policy.")
    parser.add_argument("--input-file", required=True, help="Decision input JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = decide(read_input(Path(args.input_file)))
    except ValueError as exc:
        result = {
            "step_id": "",
            "decision": "STOP",
            "status": "DECISION_BLOCKED",
            "next_action": "STOP_LOOP",
            "requires_alberto": False,
            "reasons": [str(exc)],
            "warnings": [],
        }
        print(render_json(result), end="")
        return EXIT_INPUT_ERROR

    if args.json:
        print(render_json(result), end="")
    else:
        print(result["decision"])
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
