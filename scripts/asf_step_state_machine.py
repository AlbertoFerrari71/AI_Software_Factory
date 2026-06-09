from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

SCHEMA = "asf_step_state_machine.v1"
DEFAULT_STATE_MACHINE_BRIDGE_ROOT = (
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\state_machine"
)
NO_OPERATIONAL_ACTION_NOTE = (
    "No Phase B, Phase C, GitHub, publish, commit, push, PR, merge, or deploy action was executed."
)

STATES = {
    "PLANNED",
    "PROMPT_PREPARED",
    "CODEX_RUNNING",
    "IMPLEMENTED",
    "LOCAL_VERIFIED",
    "READY_TO_PUBLISH",
    "PUBLISHING",
    "PR_CREATED",
    "MERGING",
    "PUBLISHED",
    "CLOSED",
    "BLOCKED",
    "FAILED",
    "RECOVERY_REQUIRED",
}

EVENTS = {
    "prompt_saved",
    "codex_started",
    "codex_completed",
    "local_checks_passed",
    "local_checks_failed",
    "publish_config_generated",
    "phase_b_started",
    "phase_b_passed",
    "phase_b_failed",
    "pr_created",
    "phase_c_started",
    "phase_c_passed",
    "phase_c_failed",
    "main_verified",
    "manual_block",
    "manual_unblock",
    "recovery_started",
    "recovery_completed",
    "close_step",
}

NORMAL_TRANSITIONS = {
    ("PLANNED", "prompt_saved"): "PROMPT_PREPARED",
    ("PROMPT_PREPARED", "codex_started"): "CODEX_RUNNING",
    ("CODEX_RUNNING", "codex_completed"): "IMPLEMENTED",
    ("IMPLEMENTED", "local_checks_passed"): "LOCAL_VERIFIED",
    ("LOCAL_VERIFIED", "publish_config_generated"): "READY_TO_PUBLISH",
    ("READY_TO_PUBLISH", "phase_b_started"): "PUBLISHING",
    ("PUBLISHING", "phase_b_passed"): "PR_CREATED",
    ("PUBLISHING", "pr_created"): "PR_CREATED",
    ("PR_CREATED", "pr_created"): "PR_CREATED",
    ("PR_CREATED", "phase_c_started"): "MERGING",
    ("MERGING", "phase_c_passed"): "PUBLISHED",
    ("PUBLISHED", "main_verified"): "CLOSED",
    ("PUBLISHED", "close_step"): "CLOSED",
    ("CLOSED", "close_step"): "CLOSED",
    ("CLOSED", "main_verified"): "CLOSED",
}

OPERATIONAL_STATES = STATES - {"CLOSED"}
RECOVERY_TARGET_STATES = {
    "LOCAL_VERIFIED",
    "READY_TO_PUBLISH",
    "PR_CREATED",
    "PUBLISHED",
    "CLOSED",
}

NEXT_GATES_BY_STATE = {
    "PLANNED": ["prompt_saved"],
    "PROMPT_PREPARED": ["codex_started"],
    "CODEX_RUNNING": ["codex_completed"],
    "IMPLEMENTED": ["local_checks_passed"],
    "LOCAL_VERIFIED": ["publish_config_generated"],
    "READY_TO_PUBLISH": ["phase_b_started"],
    "PUBLISHING": ["phase_b_passed or pr_created"],
    "PR_CREATED": ["phase_c_started"],
    "MERGING": ["phase_c_passed"],
    "PUBLISHED": ["main_verified or close_step"],
    "FAILED": ["recovery_started"],
    "RECOVERY_REQUIRED": ["recovery_completed with sufficient target_state evidence"],
    "BLOCKED": ["manual_unblock or recovery_started"],
    "CLOSED": [],
}

RECOMMENDED_ACTION_BY_STATE = {
    "PLANNED": "Save the Codex prompt before starting implementation.",
    "PROMPT_PREPARED": "Start the Codex implementation run.",
    "CODEX_RUNNING": "Wait for Codex completion evidence before local verification.",
    "IMPLEMENTED": "Run local checks and record local_checks_passed or local_checks_failed.",
    "LOCAL_VERIFIED": "Generate or review the publish config before publication.",
    "READY_TO_PUBLISH": "Use the standard publish runner Phase B only after explicit approval.",
    "PUBLISHING": "Wait for Phase B result; do not report completion before runner success.",
    "PR_CREATED": "Run Phase C only with the correct PR/config and explicit merge approval.",
    "MERGING": "Wait for Phase C result; a failure requires recovery.",
    "PUBLISHED": "Verify main or close the step with explicit evidence.",
    "CLOSED": "Step is closed; no further action required for this state file.",
    "FAILED": "Start recovery and capture blockers before retrying.",
    "RECOVERY_REQUIRED": "Keep the step in recovery until sufficient target-state evidence is provided.",
    "BLOCKED": "Resolve the blocker manually, then unblock or start recovery.",
}


class StateFileError(ValueError):
    pass


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalize_state(value: str) -> str:
    return compact_string(value).upper()


def normalize_event(value: str) -> str:
    return compact_string(value).casefold()


def sanitize_step_for_path(step: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", step).strip("_") or "step"


def bridge_artifact_name(step: str) -> str:
    return f"step_{sanitize_step_for_path(step)}"


def is_combined_step(step: str) -> bool:
    return "-" in step and len([part for part in step.split("-") if part.strip()]) > 1


def step_parts(step: str) -> set[str]:
    return {part.strip() for part in step.split("-") if part.strip()}


def initial_state(step: str, *, current_state: str = "PLANNED") -> dict[str, Any]:
    state = normalize_state(current_state) or "PLANNED"
    if state not in STATES:
        raise StateFileError(f"Unknown initial state: {current_state}")
    now = timestamp()
    return {
        "schema": SCHEMA,
        "step": step,
        "current_state": state,
        "history": [],
        "timestamps": {
            "created_at": now,
            "last_update": now,
        },
        "last_event": None,
        "last_update": now,
        "warnings": [],
        "blockers": [],
    }


def validate_state_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StateFileError("State file JSON must be an object.")
    step = compact_string(payload.get("step"))
    if not step:
        raise StateFileError("State file is missing step.")
    current_state = normalize_state(payload.get("current_state"))
    if current_state not in STATES:
        raise StateFileError(f"State file has unknown current_state: {payload.get('current_state')}")
    history = payload.get("history")
    if not isinstance(history, list):
        raise StateFileError("State file history must be a list.")
    payload["current_state"] = current_state
    payload.setdefault("schema", SCHEMA)
    payload.setdefault("timestamps", {})
    if not isinstance(payload["timestamps"], dict):
        raise StateFileError("State file timestamps must be an object.")
    now = timestamp()
    payload["timestamps"].setdefault("created_at", now)
    payload["timestamps"].setdefault("last_update", payload.get("last_update") or now)
    payload.setdefault("last_event", None)
    payload.setdefault("last_update", payload["timestamps"]["last_update"])
    payload.setdefault("warnings", [])
    payload.setdefault("blockers", [])
    if not isinstance(payload["warnings"], list) or not isinstance(payload["blockers"], list):
        raise StateFileError("State file warnings and blockers must be lists.")
    return payload


def load_or_initialize_state(path: Path, *, step: str | None, initial: str = "PLANNED") -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        if not step:
            raise StateFileError("State file does not exist and --step was not provided.")
        return initial_state(step, current_state=initial), [f"State file did not exist; initialized from {initial}."]

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateFileError(f"State file is not valid JSON: {exc.msg}") from exc
    except OSError as exc:
        raise StateFileError(f"Unable to read state file: {exc}") from exc

    state = validate_state_payload(payload)
    if step and step != state["step"]:
        raise StateFileError(f"CLI step {step} does not match state file step {state['step']}.")
    return state, []


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bridge_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.bridge_root or DEFAULT_STATE_MACHINE_BRIDGE_ROOT)


def bridge_paths(bridge_root: Path, step: str) -> dict[str, Path]:
    prefix = sanitize_step_for_path(step)
    name = bridge_artifact_name(step)
    return {
        "state_progressive": bridge_root / f"{prefix}-State_{name}.json",
        "event_progressive": bridge_root / f"{prefix}-Event_{name}.json",
        "compact_progressive": bridge_root / f"{prefix}-Output_Compatto_{name}.md",
        "complete_progressive": bridge_root / f"{prefix}-Output_Completo_{name}.txt",
        "state_last": bridge_root / "LAST-State.json",
        "event_last": bridge_root / "LAST-Event.json",
        "compact_last": bridge_root / "LAST-Output_Compatto.md",
        "complete_last": bridge_root / "LAST-Output_Completo.txt",
    }


def path_text(path: Path | None) -> str:
    return "" if path is None else str(path)


def observed_events(history: list[dict[str, Any]]) -> set[str]:
    events = set()
    for entry in history:
        event = compact_string(entry.get("event"))
        if event:
            events.add(event)
    return events


def missing_gates_for_state(next_state: str, history: list[dict[str, Any]]) -> list[str]:
    gates = NEXT_GATES_BY_STATE.get(next_state, [])
    seen = observed_events(history)
    missing: list[str] = []
    for gate in gates:
        alternatives = [part.strip() for part in gate.split(" or ")]
        alternatives = [part.split(" with ", 1)[0].strip() for part in alternatives]
        if alternatives and any(item in seen for item in alternatives):
            continue
        missing.append(gate)
    return missing


def history_entry(
    *,
    step: str,
    event: str,
    from_state: str,
    to_state: str,
    allowed: bool,
    reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "timestamp": timestamp(),
        "step": step,
        "event": event,
        "from_state": from_state,
        "to_state": to_state,
        "allowed": allowed,
        "reasons": reasons,
        "warnings": warnings,
    }


def make_result(
    *,
    state: dict[str, Any],
    event: str,
    next_state: str,
    allowed: bool,
    fail_closed: bool,
    reasons: list[str],
    warnings: list[str],
    history: list[dict[str, Any]],
    state_file: Path | None = None,
) -> dict[str, Any]:
    required_gates = NEXT_GATES_BY_STATE.get(next_state, [])
    return {
        "step": state.get("step"),
        "current_state": state.get("current_state"),
        "event": event,
        "next_state": next_state,
        "allowed": allowed,
        "fail_closed": fail_closed,
        "reasons": list(dict.fromkeys(reasons)),
        "warnings": list(dict.fromkeys(warnings)),
        "required_gates": required_gates,
        "missing_gates": missing_gates_for_state(next_state, history),
        "recommended_next_action": recommended_action(next_state, allowed=allowed, fail_closed=fail_closed),
        "history": history,
        "machine_readable": {
            "schema": SCHEMA,
            "version": 1,
        },
        "state_file": str(state_file) if state_file else None,
    }


def recommended_action(state: str, *, allowed: bool, fail_closed: bool) -> str:
    if fail_closed:
        return "Stop. Do not advance the workflow; resolve ambiguity or start explicit recovery."
    if not allowed:
        return "Stop. The requested transition is not allowed from the current state."
    return RECOMMENDED_ACTION_BY_STATE.get(state, "Review state manually before continuing.")


def context_blockers(
    *,
    step: str,
    config_step: str = "",
    branch: str = "",
    expected_branch: str = "",
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    blockers: list[str] = []
    if is_combined_step(step):
        warnings.append("Combined step identifier detected; keep recovery evidence explicit and reviewed.")

    config = compact_string(config_step)
    if config:
        if config == step:
            pass
        elif is_combined_step(step) and config in step_parts(step):
            warnings.append("Config step is part of a combined step; recovery/publication must stay explicit.")
        else:
            blockers.append(f"Config step {config} does not match expected step {step}.")

    actual_branch = compact_string(branch)
    expected = compact_string(expected_branch)
    if actual_branch and expected and actual_branch != expected:
        blockers.append(f"Branch {actual_branch} does not match expected branch {expected}.")
    return warnings, blockers


def transition_for_event(
    *,
    current_state: str,
    event: str,
    step: str,
    history: list[dict[str, Any]],
    target_state: str = "",
) -> tuple[str, bool, bool, list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    target = normalize_state(target_state)

    if event not in EVENTS:
        return current_state, False, True, [f"Unknown event: {event}."], warnings

    if event == "manual_block":
        reasons.append("Manual block recorded.")
        return "BLOCKED", True, False, reasons, warnings

    if event == "manual_unblock":
        if current_state != "BLOCKED":
            return current_state, False, True, ["manual_unblock is allowed only from BLOCKED."], warnings
        if target:
            if target not in STATES:
                return current_state, False, True, [f"Unknown target_state: {target}."], warnings
            reasons.append(f"Manual unblock target state declared: {target}.")
            return target, True, False, reasons, warnings
        warnings.append("manual_unblock without target_state moves to RECOVERY_REQUIRED.")
        return "RECOVERY_REQUIRED", True, False, reasons, warnings

    if event == "local_checks_failed" and current_state in OPERATIONAL_STATES:
        reasons.append("Local verification failed; workflow moves to FAILED.")
        return "FAILED", True, False, reasons, warnings

    if event == "phase_b_failed" and current_state == "PUBLISHING":
        reasons.append("Phase B failed; workflow requires recovery before any completion claim.")
        warnings.append("Do not report the step as completed after Phase B failure.")
        return "RECOVERY_REQUIRED", True, False, reasons, warnings

    if event == "phase_c_failed" and current_state == "MERGING":
        reasons.append("Phase C failed; final publication is not complete.")
        warnings.append("Do not report the step as completed after Phase C failure.")
        return "RECOVERY_REQUIRED", True, False, reasons, warnings

    if event == "recovery_started":
        reasons.append("Explicit recovery started.")
        return "RECOVERY_REQUIRED", True, False, reasons, warnings

    if event == "recovery_completed":
        if current_state not in {"RECOVERY_REQUIRED", "FAILED", "BLOCKED", "PLANNED"} and not is_combined_step(step):
            return current_state, False, True, ["recovery_completed requires recovery context or a combined step."], warnings
        if target:
            if target not in RECOVERY_TARGET_STATES:
                return current_state, False, True, [f"Invalid recovery target_state: {target}."], warnings
            reasons.append(f"Recovery completed with target state {target}.")
            return target, True, False, reasons, warnings
        reasons.append("Recovery completion recorded without sufficient target evidence.")
        warnings.append("Recovery target_state missing; keeping RECOVERY_REQUIRED fail-safe state.")
        return "RECOVERY_REQUIRED", True, False, reasons, warnings

    if current_state == "PROMPT_PREPARED" and event == "codex_completed":
        reasons.append("Codex completion evidence accepted without separate codex_started event.")
        warnings.append("codex_started missing in history; keep Codex run evidence attached to the step report.")
        return "IMPLEMENTED", True, False, reasons, warnings

    key = (current_state, event)
    if key in NORMAL_TRANSITIONS:
        next_state = NORMAL_TRANSITIONS[key]
        reasons.append(f"Allowed transition: {current_state} + {event} -> {next_state}.")
        if event == "close_step" and "main_verified" not in observed_events(history):
            warnings.append("close_step used without separate main_verified event in history.")
        return next_state, True, False, reasons, warnings

    if event == "phase_c_started":
        return current_state, False, True, ["phase_c_started requires current_state PR_CREATED."], warnings
    if event == "close_step":
        return current_state, False, True, ["close_step requires PUBLISHED or prior CLOSED state."], warnings
    if event == "publish_config_generated":
        return current_state, False, True, ["READY_TO_PUBLISH requires LOCAL_VERIFIED or explicit recovery target."], warnings

    return current_state, False, True, [f"Event {event} is not allowed from {current_state}."], warnings


def apply_event(
    state: dict[str, Any],
    *,
    event: str,
    target_state: str = "",
    config_step: str = "",
    branch: str = "",
    expected_branch: str = "",
    state_file: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    normalized = normalize_event(event)
    current_state = normalize_state(state["current_state"])
    history = list(state.get("history", []))
    warnings, blockers = context_blockers(
        step=state["step"],
        config_step=config_step,
        branch=branch,
        expected_branch=expected_branch,
    )

    if blockers:
        reasons = blockers + ["Context mismatch suggests RECOVERY_REQUIRED before continuing."]
        result = make_result(
            state=state,
            event=normalized,
            next_state="RECOVERY_REQUIRED",
            allowed=False,
            fail_closed=True,
            reasons=reasons,
            warnings=warnings,
            history=history,
            state_file=state_file,
        )
        return result, None

    next_state, allowed, fail_closed, reasons, transition_warnings = transition_for_event(
        current_state=current_state,
        event=normalized,
        step=state["step"],
        history=history,
        target_state=target_state,
    )
    warnings.extend(transition_warnings)

    if allowed:
        entry = history_entry(
            step=state["step"],
            event=normalized,
            from_state=current_state,
            to_state=next_state,
            allowed=True,
            reasons=reasons,
            warnings=warnings,
        )
        history.append(entry)
        updated = dict(state)
        now = timestamp()
        updated["current_state"] = next_state
        updated["history"] = history
        updated["last_event"] = normalized
        updated["last_update"] = now
        updated.setdefault("timestamps", {})
        updated["timestamps"]["last_update"] = now
        updated["warnings"] = list(dict.fromkeys(list(updated.get("warnings", [])) + warnings))
        updated["blockers"] = []
    else:
        updated = None

    result = make_result(
        state=state,
        event=normalized,
        next_state=next_state,
        allowed=allowed,
        fail_closed=fail_closed,
        reasons=reasons,
        warnings=warnings,
        history=history,
        state_file=state_file,
    )
    return result, updated


def fail_closed_result(
    *,
    step: str,
    current_state: str,
    event: str,
    reason: str,
    state_file: Path | None,
) -> dict[str, Any]:
    state = {
        "step": step or "UNKNOWN",
        "current_state": current_state or "UNKNOWN",
        "history": [],
    }
    return make_result(
        state=state,
        event=normalize_event(event),
        next_state="RECOVERY_REQUIRED",
        allowed=False,
        fail_closed=True,
        reasons=[reason],
        warnings=["State is ambiguous; refusing to advance."],
        history=[],
        state_file=state_file,
    )


def bullets(items: list[Any], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def render_markdown(packet: dict[str, Any]) -> str:
    return f"""# Step Execution State Machine

## Summary

- step: `{packet["step"]}`
- current_state: `{packet["current_state"]}`
- event: `{packet["event"]}`
- next_state: `{packet["next_state"]}`
- allowed: `{str(packet["allowed"]).lower()}`
- fail_closed: `{str(packet["fail_closed"]).lower()}`

## Reasons

{bullets(packet["reasons"])}

## Warnings

{bullets(packet["warnings"])}

## Required Gates

{bullets(packet["required_gates"])}

## Missing Gates

{bullets(packet["missing_gates"])}

## Recommended Next Action

{packet["recommended_next_action"]}

## History

{bullets([f'{item.get("event")} : {item.get("from_state")} -> {item.get("to_state")}' for item in packet["history"]])}
"""


def bridge_event_timestamp(packet: dict[str, Any], state_for_bridge: dict[str, Any]) -> str:
    history = state_for_bridge.get("history")
    if isinstance(history, list) and history:
        last_entry = history[-1]
        if isinstance(last_entry, dict):
            value = compact_string(last_entry.get("timestamp"))
            if value:
                return value
    history = packet.get("history")
    if isinstance(history, list) and history:
        last_entry = history[-1]
        if isinstance(last_entry, dict):
            value = compact_string(last_entry.get("timestamp"))
            if value:
                return value
    return timestamp()


def bridge_blockers(packet: dict[str, Any]) -> list[str]:
    if packet.get("fail_closed") or not packet.get("allowed"):
        return list(packet.get("reasons", []))
    return []


def build_bridge_event_payload(
    *,
    packet: dict[str, Any],
    state_for_bridge: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": packet.get("step"),
        "event": packet.get("event"),
        "from_state": packet.get("current_state"),
        "to_state": packet.get("next_state"),
        "allowed": packet.get("allowed"),
        "fail_closed": packet.get("fail_closed"),
        "timestamp": bridge_event_timestamp(packet, state_for_bridge),
        "reasons": packet.get("reasons", []),
        "warnings": packet.get("warnings", []),
        "required_gates": packet.get("required_gates", []),
        "missing_gates": packet.get("missing_gates", []),
    }


def build_bridge_state_payload(
    *,
    packet: dict[str, Any],
    state_for_bridge: dict[str, Any],
    event_payload: dict[str, Any],
    state_file: Path | None,
    bridge_root: Path,
    args: argparse.Namespace,
    written_paths: list[Path],
) -> dict[str, Any]:
    current_state = normalize_state(state_for_bridge.get("current_state"))
    if not current_state or current_state == "UNKNOWN":
        current_state = normalize_state(packet.get("next_state")) or "RECOVERY_REQUIRED"

    history = state_for_bridge.get("history", packet.get("history", []))
    warnings = list(dict.fromkeys(list(state_for_bridge.get("warnings", [])) + list(packet.get("warnings", []))))
    blockers = list(dict.fromkeys(list(state_for_bridge.get("blockers", [])) + bridge_blockers(packet)))

    payload = dict(state_for_bridge)
    payload.update(
        {
            "schema": state_for_bridge.get("schema", SCHEMA),
            "step": packet.get("step") or state_for_bridge.get("step") or "UNKNOWN",
            "current_state": current_state,
            "last_event": packet.get("event"),
            "last_update": event_payload["timestamp"],
            "history": history,
            "warnings": warnings,
            "blockers": blockers,
            "recommended_next_action": packet.get("recommended_next_action"),
            "fail_closed": packet.get("fail_closed"),
            "step_title": compact_string(args.step_title),
            "next_step": compact_string(args.next_step),
            "source": "scripts/asf_step_state_machine.py",
            "state_file": path_text(state_file),
            "bridge_root": str(bridge_root),
            "bridge_files": [str(path) for path in written_paths],
        }
    )
    payload.setdefault("timestamps", {})
    if isinstance(payload["timestamps"], dict):
        payload["timestamps"]["last_update"] = event_payload["timestamp"]
    return payload


def render_bridge_compact_markdown(
    *,
    state_payload: dict[str, Any],
    event_payload: dict[str, Any],
    paths: dict[str, Path],
) -> str:
    return f"""# ASF State Machine Bridge Output

## Summary

- step: `{state_payload["step"]}`
- current_state: `{state_payload["current_state"]}`
- last_event: `{state_payload["last_event"]}`
- transition: `{event_payload["from_state"]} -> {event_payload["to_state"]}`
- allowed: `{str(event_payload["allowed"]).lower()}`
- fail_closed: `{str(event_payload["fail_closed"]).lower()}`

## Warnings

{bullets(state_payload["warnings"])}

## Blockers

{bullets(state_payload["blockers"])}

## Recommended Next Action

{state_payload["recommended_next_action"]}

## Bridge Pointers

- LAST-State.json: `{paths["state_last"]}`
- LAST-Output_Completo.txt: `{paths["complete_last"]}`
- LAST-Output_Compatto.md: `{paths["compact_last"]}`
"""


def render_bridge_complete_text(
    *,
    packet: dict[str, Any],
    state_payload: dict[str, Any],
    event_payload: dict[str, Any],
    paths: dict[str, Path],
    args: argparse.Namespace,
) -> str:
    input_payload = {
        "step": compact_string(args.step) or state_payload.get("step"),
        "event": normalize_event(args.event),
        "state_file": state_payload.get("state_file"),
        "initial_state": normalize_state(args.initial_state),
        "target_state": normalize_state(args.target_state),
        "config_step": compact_string(args.config_step),
        "branch": compact_string(args.branch),
        "expected_branch": compact_string(args.expected_branch),
        "write_bridge": bool(args.write_bridge),
        "bridge_root": state_payload.get("bridge_root"),
        "dry_run": bool(args.dry_run),
    }
    files = [str(path) for path in paths.values()]
    return "\n".join(
        [
            "ASF Step Execution State Machine - Bridge complete output",
            "",
            "Input normalizzato:",
            json.dumps(input_payload, indent=2, sort_keys=True),
            "",
            "Stato precedente:",
            compact_string(packet.get("current_state")),
            "",
            "Evento applicato:",
            compact_string(packet.get("event")),
            "",
            "Stato successivo:",
            compact_string(packet.get("next_state")),
            "",
            "Event JSON:",
            json.dumps(event_payload, indent=2, sort_keys=True),
            "",
            "State JSON:",
            json.dumps(state_payload, indent=2, sort_keys=True),
            "",
            "History completa:",
            json.dumps(state_payload.get("history", []), indent=2, sort_keys=True),
            "",
            "Warning:",
            "\n".join(f"- {item}" for item in state_payload.get("warnings", [])) or "- none",
            "",
            "Blocker:",
            "\n".join(f"- {item}" for item in state_payload.get("blockers", [])) or "- none",
            "",
            "File Bridge scritti:",
            "\n".join(f"- {item}" for item in files),
            "",
            "Nota sicurezza:",
            NO_OPERATIONAL_ACTION_NOTE,
            "",
        ]
    )


def write_bridge_outputs(
    *,
    packet: dict[str, Any],
    state_for_bridge: dict[str, Any],
    state_file: Path | None,
    args: argparse.Namespace,
) -> list[Path]:
    bridge_root = bridge_root_from_args(args)
    step = compact_string(packet.get("step")) or compact_string(state_for_bridge.get("step")) or "UNKNOWN"
    paths = bridge_paths(bridge_root, step)
    ordered_paths = [
        paths["state_progressive"],
        paths["state_last"],
        paths["event_progressive"],
        paths["event_last"],
        paths["compact_progressive"],
        paths["compact_last"],
        paths["complete_progressive"],
        paths["complete_last"],
    ]

    bridge_root.mkdir(parents=True, exist_ok=True)
    event_payload = build_bridge_event_payload(packet=packet, state_for_bridge=state_for_bridge)
    event_payload["bridge_files"] = [str(path) for path in ordered_paths]
    state_payload = build_bridge_state_payload(
        packet=packet,
        state_for_bridge=state_for_bridge,
        event_payload=event_payload,
        state_file=state_file,
        bridge_root=bridge_root,
        args=args,
        written_paths=ordered_paths,
    )
    compact = render_bridge_compact_markdown(state_payload=state_payload, event_payload=event_payload, paths=paths)
    complete = render_bridge_complete_text(
        packet=packet,
        state_payload=state_payload,
        event_payload=event_payload,
        paths=paths,
        args=args,
    )

    state_text = json.dumps(state_payload, indent=2, sort_keys=True) + "\n"
    event_text = json.dumps(event_payload, indent=2, sort_keys=True) + "\n"
    for path, content in (
        (paths["state_progressive"], state_text),
        (paths["state_last"], state_text),
        (paths["event_progressive"], event_text),
        (paths["event_last"], event_text),
        (paths["compact_progressive"], compact),
        (paths["compact_last"], compact),
        (paths["complete_progressive"], complete),
        (paths["complete_last"], complete),
    ):
        path.write_text(content, encoding="utf-8")

    packet["bridge_root"] = str(bridge_root)
    packet["bridge_files"] = [str(path) for path in ordered_paths]
    return ordered_paths


def render_text(packet: dict[str, Any]) -> str:
    return (
        f"step={packet['step']} "
        f"current_state={packet['current_state']} "
        f"event={packet['event']} "
        f"next_state={packet['next_state']} "
        f"allowed={str(packet['allowed']).lower()} "
        f"fail_closed={str(packet['fail_closed']).lower()} "
        f"recommended_next_action={packet['recommended_next_action']}\n"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track and validate ASF step execution state transitions.")
    parser.add_argument("--step", help="Step id, for example 0670 or 0650-0660.")
    parser.add_argument("--event", required=True, help="Event to apply to the state machine.")
    parser.add_argument("--state-file", help="JSON state file. Defaults to tmp/state_machine/<step>_state.json.")
    parser.add_argument("--initial-state", default="PLANNED", help="Initial state when the state file does not exist.")
    parser.add_argument("--target-state", help="Target state for recovery_completed or manual_unblock.")
    parser.add_argument("--config-step", help="Declared step in an external config, when available.")
    parser.add_argument("--branch", help="Declared/current branch, when available.")
    parser.add_argument("--expected-branch", help="Expected branch, when available.")
    parser.add_argument("--step-title", help="Optional human-readable step title for Bridge state metadata.")
    parser.add_argument("--next-step", help="Optional next recommended step for Bridge state metadata.")
    parser.add_argument("--write-bridge", action="store_true", help="Write state, event and reports to the ASF Bridge.")
    parser.add_argument(
        "--bridge-root",
        help=(
            "Bridge root for --write-bridge. Defaults to the ASF state_machine Bridge folder. "
            "When --state-file is omitted with --write-bridge, LAST-State.json under this root is used as state file."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and render the transition without writing state.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--markdown", action="store_true", help="Print readable Markdown.")
    return parser.parse_args(argv)


def state_file_from_args(args: argparse.Namespace) -> Path:
    if args.state_file:
        return Path(args.state_file)
    if args.write_bridge:
        return bridge_root_from_args(args) / "LAST-State.json"
    if not args.step:
        raise StateFileError("--step is required when --state-file is omitted.")
    return Path("tmp") / "state_machine" / f"{sanitize_step_for_path(args.step)}_state.json"


def print_packet(packet: dict[str, Any], args: argparse.Namespace) -> None:
    if args.json:
        print(render_json(packet), end="")
    elif args.markdown:
        print(render_markdown(packet), end="")
    else:
        print(render_text(packet), end="")


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        state_file = state_file_from_args(args)
        state, load_warnings = load_or_initialize_state(
            state_file,
            step=compact_string(args.step) or None,
            initial=args.initial_state,
        )
        packet, updated = apply_event(
            state,
            event=args.event,
            target_state=compact_string(args.target_state),
            config_step=compact_string(args.config_step),
            branch=compact_string(args.branch),
            expected_branch=compact_string(args.expected_branch),
            state_file=state_file,
        )
        packet["warnings"] = list(dict.fromkeys(load_warnings + packet["warnings"]))
        if updated is not None and not args.dry_run:
            save_state(state_file, updated)
        elif updated is not None and args.dry_run:
            packet["warnings"] = list(dict.fromkeys(packet["warnings"] + ["dry_run enabled; state file not written."]))
        if args.write_bridge:
            bridge_state = updated if updated is not None and not args.dry_run else state
            write_bridge_outputs(packet=packet, state_for_bridge=bridge_state, state_file=state_file, args=args)
    except StateFileError as exc:
        fallback_step = compact_string(args.step)
        fallback_state = "UNKNOWN"
        fallback_state_file = Path(args.state_file) if args.state_file else None
        if args.write_bridge and fallback_state_file is None:
            fallback_state_file = bridge_root_from_args(args) / "LAST-State.json"
        packet = fail_closed_result(
            step=fallback_step,
            current_state=fallback_state,
            event=args.event,
            reason=str(exc),
            state_file=fallback_state_file,
        )
        if args.write_bridge:
            fallback_state_payload = {
                "schema": SCHEMA,
                "step": fallback_step or "UNKNOWN",
                "current_state": "RECOVERY_REQUIRED",
                "history": [],
                "timestamps": {
                    "created_at": timestamp(),
                    "last_update": timestamp(),
                },
                "last_event": normalize_event(args.event),
                "last_update": timestamp(),
                "warnings": packet["warnings"],
                "blockers": packet["reasons"],
            }
            write_bridge_outputs(
                packet=packet,
                state_for_bridge=fallback_state_payload,
                state_file=fallback_state_file,
                args=args,
            )
        print_packet(packet, args)
        return EXIT_INPUT_ERROR

    print_packet(packet, args)
    return EXIT_SUCCESS if not packet["fail_closed"] else EXIT_INPUT_ERROR


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
