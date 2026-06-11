from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

POSITIVE_STATES = [
    "IDLE",
    "PLAN_REQUESTED",
    "GPT_PLANNING",
    "GPT_PLAN_READY",
    "CODEX_READY",
    "CODEX_DONE",
    "REVIEW_REQUESTED",
    "REVIEW_PASS",
    "VERIFY_RUNNING",
    "VERIFY_PASS",
    "COMPLETED",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_sibling(name: str) -> Any:
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def append_event(event_log: Path, event: dict[str, Any]) -> None:
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def transition(
    *,
    state_path: Path,
    event_log: Path,
    state: dict[str, Any],
    next_state: str,
    actor: str,
    reason: str,
    event_number: int,
) -> dict[str, Any]:
    previous = state["state"]
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state = dict(state)
    state["state"] = next_state
    state["actor"] = actor
    state["last_event_id"] = f"evt-{event_number:04d}"
    state["last_update_utc"] = timestamp
    write_json(state_path, state)
    append_event(
        event_log,
        {
            "event_id": f"evt-{event_number:04d}",
            "timestamp_utc": timestamp,
            "step_id": state["step_id"],
            "from_state": previous,
            "to_state": next_state,
            "actor": actor,
            "reason": reason,
            "stop_reason": state.get("stop_reason", ""),
            "approval_reason": state.get("approval_reason", ""),
        },
    )
    return state


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_initial_state(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1010.1",
        "project": "AI_Software_Factory",
        "bridge_root": str(root / "bridge_simulated"),
        "state_file": "state.json",
        "event_log": "events.jsonl",
        "step_id": "1010-smoke-docs-step",
        "state": "IDLE",
        "lane": "mock-supervised-loop",
        "actor": "smoke",
        "last_event_id": None,
        "last_update_utc": None,
        "stop_reason": "",
        "approval_reason": "",
        "retry_policy": {
            "name": "GPT-discretionary bounded retry policy",
            "max_retry_absolute": 10,
            "current_retry": 0,
            "retry_remaining": 10,
            "ceiling_is_default": False,
        },
        "verification": {
            "selected_profile": None,
            "required_commands": [],
            "passed_commands": [],
            "failed_commands": [],
        },
        "artifacts": {},
    }


def make_task_runner_envelope(root: Path) -> dict[str, Any]:
    return {
        "task_id": "1010-smoke-fast-lane",
        "working_directory": str(root),
        "command_kind": "native_read_only",
        "script_path": "",
        "arguments": ["python", "-m", "pytest", "tests/unit/test_workflow_health_check.py"],
        "allowed_paths": [str(root)],
        "forbidden_patterns": ["destructive_reset"],
        "timeout_seconds": 60,
        "idle_timeout_seconds": 0,
        "stdout_path": "runner/stdout.txt",
        "stderr_path": "runner/stderr.txt",
        "full_output_path": "runner/full.log",
        "compact_output_path": "runner/compact.md",
    }


def run_smoke(root: Path) -> dict[str, Any]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    bridge_root = root / "bridge_simulated"
    state_path = root / "state.json"
    event_log = root / "events.jsonl"
    if event_log.exists():
        event_log.unlink()

    prompt_generator = load_sibling("asf_gpt_prompt_generator")
    codex_adapter = load_sibling("asf_codex_exec_adapter")
    decision_policy = load_sibling("asf_step_decision_policy")
    selector = load_sibling("asf_verification_profile_selector")
    task_runner = load_sibling("asf_powershell_task_runner")
    recovery = load_sibling("asf_powershell_recovery_classifier")

    state = build_initial_state(root)
    write_json(state_path, state)

    plan_path = root / "1010-smoke-step-plan.json"
    write_json(
        plan_path,
        {
            "step_id": "1010-smoke-docs-step",
            "title": "Synthetic docs-only smoke step",
            "objective": "Exercise the supervised loop adapters in mock and dry-run mode.",
            "risk_level": "L1",
            "phase": "smoke",
            "allowed_paths": ["docs/motor"],
            "forbidden_actions": [],
        },
    )

    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="PLAN_REQUESTED",
        actor="smoke",
        reason="synthetic plan requested",
        event_number=1,
    )
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="GPT_PLANNING",
        actor="gpt_prompt_generator",
        reason="mock prompt generation started",
        event_number=2,
    )

    prompt_path = bridge_root / "codex_command" / "1010-smoke-generated-prompt.md"
    prompt_packet = prompt_generator.generate_prompt(plan_path, output_path=prompt_path, mode="mock")
    state["artifacts"]["prompt"] = prompt_packet["prompt_path"]
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="GPT_PLAN_READY",
        actor="gpt_prompt_generator",
        reason="mock prompt ready",
        event_number=3,
    )

    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="CODEX_READY",
        actor="codex_exec_adapter",
        reason="prompt ready for dry-run adapter",
        event_number=4,
    )
    codex_packet = codex_adapter.prepare_codex_exec(
        codex_adapter.CodexExecRequest(
            step_id="1010-smoke-docs-step",
            prompt_path=Path(prompt_packet["prompt_path"]),
            working_directory=repo_root(),
            allowed_paths=(repo_root(), Path(prompt_packet["prompt_path"]).parent),
            envelope_output=root / "codex_exec_envelope.json",
            report_output=root / "codex_exec_report.md",
        )
    )
    state["artifacts"]["codex_envelope"] = codex_packet.get("envelope_path")
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="CODEX_DONE",
        actor="codex_exec_adapter",
        reason="CODEX_DRY_RUN_DONE",
        event_number=5,
    )

    task_validation = task_runner.validate_envelope(make_task_runner_envelope(root))
    task_packet = task_runner.dry_run_packet(make_task_runner_envelope(root), task_validation)
    recovery_packet = recovery.classify_recovery(
        recovery.RecoveryInput(stderr="ParserError: unexpected token", exit_code=1, retry_count=0)
    )
    verification_packet = selector.select_profile(
        selector.SelectorInput(
            risk_level="L2",
            changed_files=("scripts/asf_gpt_prompt_generator.py", "scripts/asf_codex_exec_adapter.py"),
            phase="local",
        )
    )
    state["verification"]["selected_profile"] = verification_packet["selected_profile"]
    state["verification"]["required_commands"] = verification_packet["required_commands"]

    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="REVIEW_REQUESTED",
        actor="decision_policy",
        reason="review requested after dry-run",
        event_number=6,
    )
    positive_decision = decision_policy.decide(
        decision_policy.input_from_json(
            {
                "step_id": "1010-smoke-docs-step",
                "risk_level": "L1",
                "verification_result": "PASS",
                "changed_files": ["docs/motor/1010_FINAL_END_TO_END_SMOKE_TEST.md"],
                "allowed_paths": ["docs/motor"],
                "forbidden_actions_detected": [],
                "max_retry_absolute": 3,
            }
        )
    )
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="REVIEW_PASS",
        actor="decision_policy",
        reason="PASS",
        event_number=7,
    )
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="VERIFY_RUNNING",
        actor="verification_selector",
        reason="adaptive verification profile selected",
        event_number=8,
    )
    state["verification"]["passed_commands"] = [
        "mock prompt generation",
        "codex adapter dry-run",
        "task runner dry-run validation",
    ]
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="VERIFY_PASS",
        actor="smoke",
        reason="mock gates passed",
        event_number=9,
    )
    state = transition(
        state_path=state_path,
        event_log=event_log,
        state=state,
        next_state="COMPLETED",
        actor="smoke",
        reason="positive smoke completed",
        event_number=10,
    )

    ask_decision = decision_policy.decide(
        decision_policy.input_from_json(
            {
                "step_id": "1010-smoke-ask",
                "risk_level": "L1",
                "verification_result": "PASS",
                "changed_files": ["docs/motor/1010_FINAL_END_TO_END_SMOKE_TEST.md"],
                "allowed_paths": ["docs/motor"],
                "publish_requested": True,
            }
        )
    )
    fix_decision = decision_policy.decide(
        decision_policy.input_from_json(
            {
                "step_id": "1010-smoke-fix",
                "risk_level": "L1",
                "verification_result": "FAIL",
                "failure_class": "POWERSHELL_PARSE_ERROR",
                "retry_count": 0,
                "max_retry_absolute": 3,
                "changed_files": ["docs/motor/1010_FINAL_END_TO_END_SMOKE_TEST.md"],
                "allowed_paths": ["docs/motor"],
            }
        )
    )
    stop_decision = decision_policy.decide(
        decision_policy.input_from_json(
            {
                "step_id": "1010-smoke-stop",
                "risk_level": "L1",
                "verification_result": "FAIL",
                "forbidden_actions_detected": ["git " + "reset --hard"],
                "changed_files": ["docs/motor/1010_FINAL_END_TO_END_SMOKE_TEST.md"],
                "allowed_paths": ["docs/motor"],
            }
        )
    )

    artifacts = [
        plan_path,
        Path(prompt_packet["prompt_path"]),
        Path(codex_packet["envelope_path"]),
        Path(codex_packet["dry_run_report_path"]),
        state_path,
        event_log,
    ]
    result = {
        "step_id": "1010-smoke-docs-step",
        "status": "COMPLETED" if state["state"] == "COMPLETED" and positive_decision["decision"] == "PASS" else "FAILED",
        "final_state": state["state"],
        "states": POSITIVE_STATES,
        "state_path": str(state_path),
        "event_log_path": str(event_log),
        "artifacts": [str(path) for path in artifacts],
        "writes_within_smoke_root": all(path_is_within(path, root) for path in artifacts),
        "components": {
            "gpt_prompt_generator": prompt_packet,
            "codex_exec_adapter": codex_packet,
            "powershell_task_runner": task_packet,
            "recovery_classifier": recovery_packet,
            "verification_selector": verification_packet,
        },
        "scenarios": {
            "positive": positive_decision,
            "ask_alberto": ask_decision,
            "fix": fix_decision,
            "stop": stop_decision,
        },
    }
    write_json(root / "smoke_result.json", result)
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ASF supervised loop end-to-end smoke in mock mode.")
    parser.add_argument("--root", default=str(repo_root() / "tmp" / "asf_supervised_loop_smoke"), help="Smoke root.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run_smoke(Path(args.root))
    except Exception as exc:  # pragma: no cover - CLI safety net
        packet = {"status": "FAILED", "error": str(exc)}
        print(json.dumps(packet, indent=2, sort_keys=True) + "\n", end="")
        return EXIT_INPUT_ERROR
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True) + "\n", end="")
    else:
        print(result["status"])
    return EXIT_SUCCESS if result["status"] == "COMPLETED" else EXIT_INPUT_ERROR


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
