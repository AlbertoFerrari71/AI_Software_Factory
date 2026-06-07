from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

SCHEMA = "asf_e2e_mvp_smoke.v1"
SCENARIO_POSITIVE = "code-unit-to-ready-to-publish"
SCENARIO_NEGATIVE = "invalid-state-to-publish-config"
DEFAULT_OUT_DIR = "tmp/e2e_mvp_smoke"
DEFAULT_BRIDGE_ROOT = (
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\e2e_smoke"
)

STEP = "0700-smoke"
STEP_NAME = "End_To_End_MVP_Smoke_Scenario"
NEXT_STEP = "0710) Motor Run Manifest and Evidence Pack"
SIMULATED_FILES = (
    "scripts/example_component.py",
    "tests/unit/test_example_component.py",
)
LOCAL_CHECKS = (
    "python -m pytest tests/unit/test_example_component.py",
    "python scripts/check_workflow_health.py",
)

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


@dataclass(frozen=True)
class SmokeResult:
    scenario: str
    status: str
    summary: dict[str, Any]
    markdown: str
    evidence_pack: dict[str, Any]
    exit_code: int


def load_components() -> dict[str, Any]:
    try:
        import asf_dry_run_loop_runner as dry_run
        import asf_gate_decision_report as gate_report
        import asf_risk_classifier as risk_classifier
        import asf_step_state_machine as state_machine
        import asf_verification_profile_selector as selector
    except Exception as exc:  # pragma: no cover - defensive CLI path
        raise RuntimeError(f"Unable to import ASF smoke components: {exc}") from exc

    return {
        "dry_run": dry_run,
        "gate_report": gate_report,
        "risk_classifier": risk_classifier,
        "state_machine": state_machine,
        "selector": selector,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object in {path}.")
    return payload


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._-")
    return text or "e2e_smoke"


def path_text(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def safe_command(argv: list[str]) -> list[str]:
    display = []
    for item in argv:
        path = Path(item)
        if path.name == "asf_publish_config_generator.py":
            display.append("scripts/asf_publish_config_generator.py")
        else:
            display.append(str(item))
    return display


def guardrails_payload(generator_command: list[str] | None = None) -> dict[str, Any]:
    return {
        "phase_b_executed": False,
        "phase_c_executed": False,
        "commit_executed": False,
        "push_executed": False,
        "pull_request_created": False,
        "merge_executed": False,
        "deploy_executed": False,
        "github_operation_executed": False,
        "external_api_call_executed": False,
        "subprocesses": [safe_command(generator_command)] if generator_command else [],
    }


def build_input_step(*, scenario: str) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.input",
        "scenario": scenario,
        "step": STEP,
        "name": STEP_NAME,
        "step_type": "code-unit",
        "risk_level_declared": "L2",
        "changed_files": list(SIMULATED_FILES),
        "checks": list(LOCAL_CHECKS),
        "provided_gates": ["local_verification"],
        "mode": "local-smoke-only",
        "forbidden_runtime_actions": [
            "phase_b",
            "phase_c",
            "commit",
            "push",
            "pull_request",
            "merge",
            "deploy",
            "github_operation",
            "external_api_call",
        ],
    }


def build_generator_input(*, bridge_root: Path) -> dict[str, Any]:
    return {
        "step": STEP,
        "name": STEP_NAME,
        "repo_path": ".",
        "bridge_root": str(bridge_root),
        "branch": "step-0700-end-to-end-mvp-smoke-scenario",
        "commit_message": "0700 add end-to-end mvp smoke scenario",
        "pr_title": "0700 add end-to-end mvp smoke scenario",
        "pr_body": (
            "Implements STEP 0700. The smoke creates local evidence only; "
            "review the generated config before any publication runner use."
        ),
        "next_step": NEXT_STEP,
        "expected_files": list(SIMULATED_FILES),
        "changed_files": list(SIMULATED_FILES),
        "risk_level": "L2",
        "verification_phase": "local",
        "intent": ["local code unit", "generator config draft"],
        "provided_gates": ["local_verification"],
        "allow_profile_check_reduction": False,
        "checks_already_run": list(LOCAL_CHECKS),
        "profile_selector_expected_profile": "code-unit",
        "allow_no_github_checks_reported": True,
        "log_max_count": 12,
    }


def build_risk_report(components: dict[str, Any]) -> dict[str, Any]:
    risk_classifier = components["risk_classifier"]
    classifier_input = risk_classifier.ClassifierInput(
        text_items=(
            "Local code-unit smoke scenario.",
            "Implement a simulated local Python code unit and its tests.",
        ),
        file_items=SIMULATED_FILES,
        command_items=LOCAL_CHECKS,
        keyword_items=("code-unit", "local verification"),
    )
    return risk_classifier.classify(classifier_input, provided_gates={"local_verification"})


def build_dry_run_report(components: dict[str, Any]) -> dict[str, Any]:
    dry_run = components["dry_run"]
    request = dry_run.LoopRequest(
        project_name="AI_Software_Factory",
        repo_path=".",
        step=STEP,
        title="Local code-unit MVP smoke",
        branch="step-0700-end-to-end-mvp-smoke-scenario",
        objective="Produce local evidence for a simulated Python code unit and its tests.",
        allowed_scope=SIMULATED_FILES,
        forbidden_actions=(
            "phase_b",
            "phase_c",
            "commit",
            "push",
            "pull_request",
            "merge",
            "deploy",
            "github_operation",
            "external_api_call",
        ),
        checks=LOCAL_CHECKS,
        provided_gates=("local_verification",),
    )
    plan = dry_run.default_plan(request)
    risk_checkpoint = dry_run.build_risk_checkpoint(request, plan, [])
    review = {
        "verdict": "PASS",
        "step": request.step,
        "blocking_findings": [],
        "warnings": ["Synthetic e2e smoke review; no target repository writes are performed."],
        "checks": {
            "risk_pass": risk_checkpoint["status"] == "PASS",
            "target_status_unchanged": True,
            "artifacts_present": True,
            "live_provider_absent": True,
            "publication_absent": True,
        },
    }
    gate = dry_run.decide_gate(review)
    return {
        "schema": f"{SCHEMA}.dry_run",
        "component": "asf_dry_run_loop_runner",
        "request": {
            "project_name": request.project_name,
            "repo_path": request.repo_path,
            "step": request.step,
            "title": request.title,
            "branch": request.branch,
            "objective": request.objective,
            "allowed_scope": list(request.allowed_scope),
            "forbidden_actions": list(request.forbidden_actions),
            "checks": list(request.checks),
            "provided_gates": list(request.provided_gates),
        },
        "plan": plan,
        "risk_checkpoint": risk_checkpoint,
        "independent_review": review,
        "gate_decision": gate,
        "dry_run_only": True,
    }


def build_gate_packet(
    *,
    components: dict[str, Any],
    risk_report: dict[str, Any],
    dry_run_report: dict[str, Any],
) -> dict[str, Any]:
    gate_report = components["gate_report"]
    raw = {
        "step": STEP,
        "title": "Local code-unit MVP smoke",
        "risk_report": {
            "risk": risk_report,
            "gate": dry_run_report["risk_checkpoint"]["gate"],
            "dry_run": dry_run_report["risk_checkpoint"]["dry_run"],
        },
        "files_in_scope": list(SIMULATED_FILES),
        "checks_required": list(LOCAL_CHECKS),
        "checks_reported": [{"name": check, "status": "PASSED"} for check in LOCAL_CHECKS],
        "provided_gates": ["local_verification"],
        "warnings": ["Checks are represented as local smoke evidence for this e2e scenario."],
    }
    return gate_report.build_approval_packet(raw)


def build_verification_profile(components: dict[str, Any], risk_report: dict[str, Any]) -> dict[str, Any]:
    selector = components["selector"]
    data = selector.SelectorInput(
        risk_level=risk_report["risk_level"],
        changed_files=SIMULATED_FILES,
        step_type="code-unit",
        phase="local",
        intent=("local code unit",),
        checks_already_run=LOCAL_CHECKS,
        provided_gates=("local_verification",),
    )
    return selector.select_profile(data)


def apply_pre_publish_state(components: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    state_machine = components["state_machine"]
    state = state_machine.initial_state(STEP, current_state="PLANNED")
    packets: list[dict[str, Any]] = []
    for event in ("prompt_saved", "codex_completed", "local_checks_passed"):
        packet, updated = state_machine.apply_event(state, event=event)
        packets.append(packet)
        if updated is None:
            raise RuntimeError(f"State machine failed before publish config generation on event {event}.")
        state = updated
    return state, packets


def run_generator_cli(
    *,
    input_file: Path,
    out_dir: Path,
    state_file: Path,
    expected_current: str,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None, list[str]]:
    argv = [
        sys.executable,
        str(SCRIPT_DIR / "asf_publish_config_generator.py"),
        "--input-file",
        str(input_file),
        "--out-dir",
        str(out_dir),
        "--state-file",
        str(state_file),
        "--state-event",
        "publish_config_generated",
        "--update-state",
        "--require-state",
        "--state-expected-current",
        expected_current,
        "--state-target-after",
        "READY_TO_PUBLISH",
        "--state-allow-recovery",
        "--json",
    ]
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = None
    errors: list[str] = []
    try:
        payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        if payload is not None and not isinstance(payload, dict):
            errors.append("Generator JSON output is not an object.")
            payload = None
    except json.JSONDecodeError as exc:
        errors.append(f"Generator stdout is not valid JSON: {exc.msg}.")
    return completed, payload, argv


def render_markdown(summary: dict[str, Any]) -> str:
    artifacts = summary.get("artifacts", {})
    components = summary.get("components_traversed", [])
    guardrails = summary.get("guardrails", {})
    blockers = summary.get("blockers", [])
    warnings = summary.get("warnings", [])
    return f"""# ASF E2E MVP Smoke Evidence Summary

## Summary

- scenario: `{summary.get("scenario")}`
- status: `{summary.get("status")}`
- final-state: `{summary.get("final_state")}`
- ready-config-produced: `{summary.get("ready_config_produced")}`

## Components Traversed

{markdown_bullets(components)}

## Artifacts

{markdown_bullets([f"{key}: {value}" for key, value in artifacts.items()])}

## Guardrails

- Phase B executed: `{guardrails.get("phase_b_executed")}`
- Phase C executed: `{guardrails.get("phase_c_executed")}`
- commit executed: `{guardrails.get("commit_executed")}`
- push executed: `{guardrails.get("push_executed")}`
- pull request created: `{guardrails.get("pull_request_created")}`
- merge executed: `{guardrails.get("merge_executed")}`
- deploy executed: `{guardrails.get("deploy_executed")}`
- external API call executed: `{guardrails.get("external_api_call_executed")}`

## Blockers

{markdown_bullets(blockers)}

## Warnings

{markdown_bullets(warnings)}
"""


def markdown_bullets(items: list[Any], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def artifact_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "input_step": out_dir / "input_step.json",
        "risk_report": out_dir / "risk_report.json",
        "dry_run_report": out_dir / "dry_run_report.json",
        "gate_decision_packet": out_dir / "gate_decision_packet.json",
        "verification_profile": out_dir / "verification_profile.json",
        "publish_config": out_dir / "publish_config.json",
        "state_before": out_dir / "state_before.json",
        "state_after": out_dir / "state_after.json",
        "evidence_summary_md": out_dir / "evidence_summary.md",
        "evidence_summary_json": out_dir / "evidence_summary.json",
        "evidence_pack": out_dir / "evidence_pack.json",
        "negative_fail_closed": out_dir / "negative_fail_closed.json",
    }


def write_summary_outputs(
    *,
    out_dir: Path,
    summary: dict[str, Any],
    markdown: str,
    evidence_pack: dict[str, Any],
) -> None:
    paths = artifact_paths(out_dir)
    write_json(paths["evidence_summary_json"], summary)
    write_json(paths["evidence_pack"], evidence_pack)
    paths["evidence_summary_md"].write_text(markdown, encoding="utf-8", newline="\n")


def bridge_index(bridge_root: Path) -> int:
    if not bridge_root.exists():
        return 1
    indexes: list[int] = []
    pattern = re.compile(r"^0700-(\d\d)-Evidence_")
    for path in bridge_root.iterdir():
        match = pattern.match(path.name)
        if match:
            indexes.append(int(match.group(1)))
    return (max(indexes) + 1) if indexes else 1


def write_bridge_outputs(
    *,
    bridge_root: Path,
    scenario: str,
    markdown: str,
    evidence_pack: dict[str, Any],
) -> dict[str, str]:
    bridge_root.mkdir(parents=True, exist_ok=True)
    idx = bridge_index(bridge_root)
    stem = slugify(scenario)
    summary_path = bridge_root / f"0700-{idx:02d}-Evidence_Summary_{stem}.md"
    pack_path = bridge_root / f"0700-{idx:02d}-Evidence_Pack_{stem}.json"
    last_summary = bridge_root / "LAST-Evidence_Summary.md"
    last_pack = bridge_root / "LAST-Evidence_Pack.json"

    summary_path.write_text(markdown, encoding="utf-8", newline="\n")
    last_summary.write_text(markdown, encoding="utf-8", newline="\n")
    write_json(pack_path, evidence_pack)
    write_json(last_pack, evidence_pack)
    return {
        "summary": str(summary_path),
        "pack": str(pack_path),
        "last_summary": str(last_summary),
        "last_pack": str(last_pack),
    }


def run_positive(out_dir: Path, *, write_bridge: bool, bridge_root: Path) -> SmokeResult:
    components = load_components()
    paths = artifact_paths(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_step = build_input_step(scenario=SCENARIO_POSITIVE)
    risk_report = build_risk_report(components)
    dry_run_report = build_dry_run_report(components)
    gate_packet = build_gate_packet(
        components=components,
        risk_report=risk_report,
        dry_run_report=dry_run_report,
    )
    verification_profile = build_verification_profile(components, risk_report)
    state_before, state_packets = apply_pre_publish_state(components)

    generator_input = build_generator_input(bridge_root=out_dir / "runner_bridge_placeholder")
    generator_input_path = out_dir / "publish_config_input.json"
    generator_state_path = out_dir / "state_working.json"
    generator_out_dir = out_dir / "publish_generator"
    write_json(generator_input_path, generator_input)
    write_json(generator_state_path, state_before)

    completed, generator_payload, generator_argv = run_generator_cli(
        input_file=generator_input_path,
        out_dir=generator_out_dir,
        state_file=generator_state_path,
        expected_current="LOCAL_VERIFIED",
    )

    blockers: list[str] = []
    warnings = []
    if completed.returncode != 0:
        blockers.append(f"Publish config generator returned {completed.returncode}.")
    if generator_payload is None:
        blockers.append("Publish config generator did not produce JSON payload.")
    elif generator_payload.get("status") != "ok":
        blockers.extend(str(item) for item in generator_payload.get("errors", []))
    if risk_report.get("risk_level") != "L2":
        blockers.append(f"Risk classifier returned {risk_report.get('risk_level')} instead of L2.")
    if dry_run_report["risk_checkpoint"]["status"] != "PASS":
        blockers.append("Dry-run risk checkpoint is not PASS.")
    if gate_packet.get("decision") != "APPROVE_LOCAL_ONLY":
        blockers.append(f"Gate decision is {gate_packet.get('decision')} instead of APPROVE_LOCAL_ONLY.")
    if verification_profile.get("profile") != "code-unit":
        blockers.append(f"Verification profile is {verification_profile.get('profile')} instead of code-unit.")

    publish_config: dict[str, Any] | None = None
    state_after: dict[str, Any] | None = None
    if generator_payload and generator_payload.get("config_path"):
        config_path = Path(str(generator_payload["config_path"]))
        if config_path.is_file():
            publish_config = read_json(config_path)
            write_json(paths["publish_config"], publish_config)
        else:
            blockers.append(f"Generated config path is missing: {config_path}")
    else:
        blockers.append("No ready publish config path was produced.")

    if generator_state_path.is_file():
        state_after = read_json(generator_state_path)
    else:
        blockers.append("State working file is missing after generator execution.")
    final_state = str((state_after or {}).get("current_state", "UNKNOWN"))
    if final_state != "READY_TO_PUBLISH":
        blockers.append(f"Final state is {final_state} instead of READY_TO_PUBLISH.")

    write_json(paths["input_step"], input_step)
    write_json(paths["risk_report"], risk_report)
    write_json(paths["dry_run_report"], dry_run_report)
    write_json(paths["gate_decision_packet"], gate_packet)
    write_json(paths["verification_profile"], verification_profile)
    write_json(paths["state_before"], state_before)
    if state_after is not None:
        write_json(paths["state_after"], state_after)

    artifacts = {
        "input_step": path_text(paths["input_step"]),
        "risk_report": path_text(paths["risk_report"]),
        "dry_run_report": path_text(paths["dry_run_report"]),
        "gate_decision_packet": path_text(paths["gate_decision_packet"]),
        "verification_profile": path_text(paths["verification_profile"]),
        "publish_config": path_text(paths["publish_config"]) if publish_config else None,
        "state_before": path_text(paths["state_before"]),
        "state_after": path_text(paths["state_after"]) if state_after else None,
        "generator_summary": path_text(generator_out_dir / f"{STEP}_publish_config_summary.md"),
    }
    status = "ok" if not blockers else "blocked"
    summary = {
        "schema": SCHEMA,
        "scenario": SCENARIO_POSITIVE,
        "status": status,
        "ready_config_produced": publish_config is not None and not blockers,
        "final_state": final_state,
        "components_traversed": [
            "asf_step_state_machine",
            "asf_risk_classifier",
            "asf_dry_run_loop_runner",
            "asf_gate_decision_report",
            "asf_verification_profile_selector",
            "asf_publish_config_generator",
        ],
        "artifacts": artifacts,
        "state_events_before_generator": state_packets,
        "generator_returncode": completed.returncode,
        "generator_payload": generator_payload,
        "guardrails": guardrails_payload(generator_argv),
        "blockers": blockers,
        "warnings": warnings,
    }
    evidence_pack = {
        "summary": summary,
        "input_step": input_step,
        "risk_report": risk_report,
        "dry_run_report": dry_run_report,
        "gate_decision_packet": gate_packet,
        "verification_profile": verification_profile,
        "publish_config": publish_config,
        "state_before": state_before,
        "state_after": state_after,
    }
    markdown = render_markdown(summary)
    write_summary_outputs(out_dir=out_dir, summary=summary, markdown=markdown, evidence_pack=evidence_pack)
    if write_bridge:
        bridge_paths = write_bridge_outputs(
            bridge_root=bridge_root,
            scenario=SCENARIO_POSITIVE,
            markdown=markdown,
            evidence_pack=evidence_pack,
        )
        summary["bridge_paths"] = bridge_paths
        write_summary_outputs(out_dir=out_dir, summary=summary, markdown=markdown, evidence_pack=evidence_pack)
    return SmokeResult(SCENARIO_POSITIVE, status, summary, markdown, evidence_pack, EXIT_SUCCESS if status == "ok" else EXIT_INPUT_ERROR)


def run_negative(out_dir: Path, *, write_bridge: bool, bridge_root: Path) -> SmokeResult:
    components = load_components()
    state_machine = components["state_machine"]
    paths = artifact_paths(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_step = build_input_step(scenario=SCENARIO_NEGATIVE)
    state_before = state_machine.initial_state(STEP, current_state="IMPLEMENTED")
    generator_input = build_generator_input(bridge_root=out_dir / "runner_bridge_placeholder")
    generator_input_path = out_dir / "publish_config_input.json"
    generator_state_path = out_dir / "state_working.json"
    generator_out_dir = out_dir / "publish_generator"
    write_json(generator_input_path, generator_input)
    write_json(generator_state_path, state_before)

    completed, generator_payload, generator_argv = run_generator_cli(
        input_file=generator_input_path,
        out_dir=generator_out_dir,
        state_file=generator_state_path,
        expected_current="LOCAL_VERIFIED",
    )
    state_after = read_json(generator_state_path)
    config_path = None
    if generator_payload:
        config_path = generator_payload.get("config_path")
    ready_config_produced = bool(config_path and Path(str(config_path)).is_file())
    fail_closed = (
        completed.returncode == EXIT_INPUT_ERROR
        and generator_payload is not None
        and generator_payload.get("status") == "blocked"
        and not ready_config_produced
        and state_after.get("current_state") != "READY_TO_PUBLISH"
    )
    blockers = []
    if generator_payload:
        blockers.extend(str(item) for item in generator_payload.get("errors", []))
    if not fail_closed:
        blockers.append("Negative scenario did not fail closed as expected.")

    negative_payload = {
        "schema": f"{SCHEMA}.negative",
        "scenario": SCENARIO_NEGATIVE,
        "expected_fail_closed": True,
        "observed_fail_closed": fail_closed,
        "generator_returncode": completed.returncode,
        "generator_payload": generator_payload,
        "ready_config_produced": ready_config_produced,
        "state_before": state_before,
        "state_after": state_after,
        "stdout_present": bool(completed.stdout.strip()),
        "stderr": completed.stderr,
    }

    write_json(paths["input_step"], input_step)
    write_json(paths["state_before"], state_before)
    write_json(paths["state_after"], state_after)
    write_json(paths["negative_fail_closed"], negative_payload)

    status = "fail_closed" if fail_closed else "error"
    summary = {
        "schema": SCHEMA,
        "scenario": SCENARIO_NEGATIVE,
        "status": status,
        "ready_config_produced": ready_config_produced,
        "final_state": state_after.get("current_state", "UNKNOWN"),
        "components_traversed": [
            "asf_step_state_machine",
            "asf_publish_config_generator",
        ],
        "artifacts": {
            "input_step": path_text(paths["input_step"]),
            "state_before": path_text(paths["state_before"]),
            "state_after": path_text(paths["state_after"]),
            "negative_fail_closed": path_text(paths["negative_fail_closed"]),
            "publish_config": None,
            "generator_summary": path_text(generator_out_dir / f"{STEP}_publish_config_summary.md"),
        },
        "generator_returncode": completed.returncode,
        "generator_payload": generator_payload,
        "guardrails": guardrails_payload(generator_argv),
        "blockers": blockers,
        "warnings": [],
    }
    evidence_pack = {
        "summary": summary,
        "input_step": input_step,
        "negative_fail_closed": negative_payload,
        "state_before": state_before,
        "state_after": state_after,
    }
    markdown = render_markdown(summary)
    write_summary_outputs(out_dir=out_dir, summary=summary, markdown=markdown, evidence_pack=evidence_pack)
    if write_bridge:
        bridge_paths = write_bridge_outputs(
            bridge_root=bridge_root,
            scenario=SCENARIO_NEGATIVE,
            markdown=markdown,
            evidence_pack=evidence_pack,
        )
        summary["bridge_paths"] = bridge_paths
        write_summary_outputs(out_dir=out_dir, summary=summary, markdown=markdown, evidence_pack=evidence_pack)
    return SmokeResult(
        SCENARIO_NEGATIVE,
        status,
        summary,
        markdown,
        evidence_pack,
        EXIT_SUCCESS if fail_closed else EXIT_INPUT_ERROR,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local ASF End-to-End MVP smoke scenario.")
    parser.add_argument(
        "--scenario",
        choices=[SCENARIO_POSITIVE, SCENARIO_NEGATIVE],
        default=SCENARIO_POSITIVE,
        help="Smoke scenario to execute.",
    )
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Local evidence output directory.")
    parser.add_argument("--write-bridge", action="store_true", help="Write evidence summary and pack to a Bridge root.")
    parser.add_argument("--bridge-root", default=DEFAULT_BRIDGE_ROOT, help="Bridge root for optional evidence output.")
    parser.add_argument("--json", action="store_true", help="Print evidence summary JSON.")
    parser.add_argument("--markdown", action="store_true", help="Print evidence summary Markdown.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out_dir)
    bridge_root = Path(args.bridge_root)
    if args.scenario == SCENARIO_POSITIVE:
        result = run_positive(out_dir, write_bridge=bool(args.write_bridge), bridge_root=bridge_root)
    else:
        result = run_negative(out_dir, write_bridge=bool(args.write_bridge), bridge_root=bridge_root)

    if args.json:
        print(json.dumps(result.summary, indent=2, sort_keys=True))
    elif args.markdown:
        print(result.markdown, end="")
    else:
        print(f"{result.scenario}: {result.status}")
        print(f"Evidence: {out_dir}")
    return result.exit_code


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
