from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

SCHEMA_VERSION = "asf_motor_run_manifest.v1"
DEFAULT_OUT_DIR = "tmp/motor_run_manifest"
DEFAULT_BRIDGE_ROOT = (
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\motor_run"
)

READY_DECISION = "READY_TO_PUBLISH"
BLOCKED_DECISION = "BLOCKED"
FAIL_CLOSED_DECISION = "FAIL_CLOSED"
INCOMPLETE_DECISION = "INCOMPLETE"
REVIEW_DECISION = "REVIEW_REQUIRED"

PASS_STATUSES = {"PASS", "PASSED", "OK", "SUCCESS", "SUCCEEDED"}


@dataclass(frozen=True)
class ArtifactSpec:
    name: str
    filename: str
    kind: str
    description: str


KNOWN_ARTIFACTS = (
    ArtifactSpec("input_step", "input_step.json", "input", "Smoke input step payload."),
    ArtifactSpec("risk_report", "risk_report.json", "risk", "Risk classifier report."),
    ArtifactSpec("dry_run_report", "dry_run_report.json", "dry_run", "Dry-run loop runner report."),
    ArtifactSpec(
        "gate_decision_packet",
        "gate_decision_packet.json",
        "gate",
        "Human approval gate decision packet.",
    ),
    ArtifactSpec(
        "verification_profile",
        "verification_profile.json",
        "verification",
        "Verification profile selector output.",
    ),
    ArtifactSpec("publish_config", "publish_config.json", "publish_config", "Generated publish config."),
    ArtifactSpec("state_before", "state_before.json", "state", "State machine state before generation."),
    ArtifactSpec("state_after", "state_after.json", "state", "State machine state after generation."),
    ArtifactSpec(
        "evidence_summary_md",
        "evidence_summary.md",
        "summary_markdown",
        "Readable smoke evidence summary.",
    ),
    ArtifactSpec(
        "evidence_summary_json",
        "evidence_summary.json",
        "summary_json",
        "Machine-readable smoke evidence summary.",
    ),
    ArtifactSpec(
        "negative_fail_closed",
        "negative_fail_closed.json",
        "fail_closed",
        "Negative scenario fail-closed evidence.",
    ),
)

POSITIVE_REQUIRED = {
    "input_step",
    "risk_report",
    "dry_run_report",
    "gate_decision_packet",
    "verification_profile",
    "publish_config",
    "state_before",
    "state_after",
    "evidence_summary_json",
}

NEGATIVE_REQUIRED = {
    "input_step",
    "state_before",
    "state_after",
    "negative_fail_closed",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._-")
    return text or "motor_run"


def compact_string(value: Any, *, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return value.strip() or fallback
    return str(value).strip() or fallback


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [compact_string(item) for item in value if compact_string(item)]
    if isinstance(value, tuple):
        return [compact_string(item) for item in value if compact_string(item)]
    text = compact_string(value)
    return [text] if text else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return payload


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def display_path(path: Path, *, root: Path | None = None) -> str:
    base = root or Path.cwd()
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def make_run_id(step: str, scenario: str, created_at: str) -> str:
    stamp = created_at.replace(":", "").replace("-", "").replace("+0000", "Z")
    stamp = stamp.replace("Z", "")
    return f"run-{slugify(step)}-{slugify(scenario)}-{stamp}"


def artifact_from_path(
    *,
    name: str,
    path: Path,
    kind: str,
    required: bool,
    description: str,
    root: Path | None = None,
) -> dict[str, Any]:
    exists = path.is_file()
    item: dict[str, Any] = {
        "name": name,
        "path": display_path(path, root=root),
        "kind": kind,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "sha256": sha256_file(path) if exists else None,
        "required": required,
        "description": description,
    }
    return item


def normalize_input_artifact(item: Any, *, base_dir: Path) -> dict[str, Any]:
    raw = as_dict(item)
    path_text = compact_string(raw.get("path"))
    physical_path = (base_dir / path_text) if path_text and not Path(path_text).is_absolute() else Path(path_text)
    physical_exists = bool(path_text) and physical_path.is_file()
    declared_exists = raw.get("exists")
    exists = physical_exists if path_text and physical_exists else bool(declared_exists)
    size = physical_path.stat().st_size if physical_exists else int(raw.get("size_bytes") or 0)
    checksum = sha256_file(physical_path) if physical_exists else raw.get("sha256")
    name = compact_string(raw.get("name"), fallback=Path(path_text).stem if path_text else "artifact")
    return {
        "name": name,
        "path": path_text or compact_string(raw.get("name"), fallback=name),
        "kind": compact_string(raw.get("kind"), fallback="artifact"),
        "exists": exists,
        "size_bytes": size,
        "sha256": checksum if exists else None,
        "required": bool(raw.get("required", False)),
        "description": compact_string(raw.get("description"), fallback="Input manifest artifact."),
    }


def normalize_check(item: Any) -> dict[str, Any]:
    raw = as_dict(item)
    if not raw and isinstance(item, str):
        raw = {"name": item, "command": item, "status": "UNKNOWN", "required": True}
    command_value = raw.get("command")
    if isinstance(command_value, list):
        command = " ".join(compact_string(part) for part in command_value)
    else:
        command = compact_string(command_value)
    name = compact_string(raw.get("name"), fallback=command or "check")
    exit_code = raw.get("exit_code")
    return {
        "name": name,
        "status": compact_string(raw.get("status"), fallback="UNKNOWN").upper(),
        "command": command or None,
        "exit_code": exit_code if isinstance(exit_code, int) else None,
        "required": bool(raw.get("required", True)),
        "description": compact_string(raw.get("description"), fallback="Manifest check evidence."),
    }


def required_artifact_names(*, scenario: str, evidence_dir: Path) -> set[str]:
    negative_present = (evidence_dir / "negative_fail_closed.json").is_file()
    negative_scenario = "invalid" in scenario.casefold() or "fail_closed" in scenario.casefold()
    return NEGATIVE_REQUIRED if negative_present or negative_scenario else POSITIVE_REQUIRED


def artifacts_from_evidence_dir(evidence_dir: Path, *, scenario: str, root: Path) -> list[dict[str, Any]]:
    required_names = required_artifact_names(scenario=scenario, evidence_dir=evidence_dir)
    return [
        artifact_from_path(
            name=spec.name,
            path=evidence_dir / spec.filename,
            kind=spec.kind,
            required=spec.name in required_names,
            description=spec.description,
            root=root,
        )
        for spec in KNOWN_ARTIFACTS
    ]


def load_evidence_payloads(evidence_dir: Path) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    payloads: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    blockers: list[str] = []
    spec_by_name = {spec.name: spec for spec in KNOWN_ARTIFACTS}
    for name, spec in spec_by_name.items():
        path = evidence_dir / spec.filename
        if not path.is_file() or path.suffix.lower() != ".json":
            continue
        try:
            payloads[name] = read_json_object(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            blockers.append(f"Artifact {spec.filename} is not readable JSON: {exc}")
    summary = payloads.get("evidence_summary_json", {})
    warnings.extend(compact_list(summary.get("warnings")))
    blockers.extend(compact_list(summary.get("blockers")))
    return payloads, warnings, blockers


def checks_from_evidence(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    seen: set[str] = set()
    seen_commands: set[str] = set()
    gate = payloads.get("gate_decision_packet", {})
    for key in ("checks_reported", "check_results", "checks"):
        values = gate.get(key)
        if isinstance(values, list):
            for value in values:
                check = normalize_check(value)
                if check["name"] not in seen:
                    checks.append(check)
                    seen.add(check["name"])
                    if check.get("command"):
                        seen_commands.add(compact_string(check.get("command")))
    required = compact_list(gate.get("checks_required"))
    if not required:
        required = compact_list(payloads.get("input_step", {}).get("checks"))
    for command in required:
        if command not in seen and command not in seen_commands:
            checks.append(
                normalize_check(
                    {
                        "name": command,
                        "command": command,
                        "status": "UNKNOWN",
                        "required": True,
                        "description": "Required check declared but not reported in evidence.",
                    }
                )
            )
            seen.add(command)
    return checks


def missing_required_artifacts(artifacts: list[dict[str, Any]]) -> list[str]:
    return [item["name"] for item in artifacts if item.get("required") and not item.get("exists")]


def failed_required_checks(checks: list[dict[str, Any]]) -> list[str]:
    failed: list[str] = []
    for check in checks:
        if not check.get("required"):
            continue
        status = compact_string(check.get("status")).upper()
        if status not in PASS_STATUSES:
            failed.append(compact_string(check.get("name"), fallback="check"))
    return failed


def current_state(state: dict[str, Any]) -> str:
    after = as_dict(state.get("after"))
    before = as_dict(state.get("before"))
    return compact_string(after.get("current_state"), fallback=compact_string(before.get("current_state"), fallback="UNKNOWN"))


def normalize_decision(value: Any) -> str:
    decision = compact_string(value).upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "READY": READY_DECISION,
        "OK": READY_DECISION,
        "FAILCLOSED": FAIL_CLOSED_DECISION,
        "FAIL_CLOSED": FAIL_CLOSED_DECISION,
        "BLOCKED": BLOCKED_DECISION,
        "INCOMPLETE": INCOMPLETE_DECISION,
        "REVIEW": REVIEW_DECISION,
        "REVIEW_REQUIRED": REVIEW_DECISION,
    }
    return aliases.get(decision, decision)


def decide(
    *,
    explicit_decision: Any,
    fail_closed: bool,
    blockers: list[str],
    missing_artifacts: list[str],
    failed_checks: list[str],
    state: dict[str, Any],
    source_status: str,
) -> str:
    if fail_closed:
        return FAIL_CLOSED_DECISION
    if blockers:
        return BLOCKED_DECISION
    if missing_artifacts or failed_checks:
        return INCOMPLETE_DECISION
    explicit = normalize_decision(explicit_decision)
    if explicit in {READY_DECISION, BLOCKED_DECISION, FAIL_CLOSED_DECISION, INCOMPLETE_DECISION, REVIEW_DECISION}:
        return explicit
    if current_state(state) == READY_DECISION or source_status.casefold() in {"ok", "ready", "ready_to_publish"}:
        return READY_DECISION
    return REVIEW_DECISION


def status_from_decision(decision: str) -> str:
    return {
        READY_DECISION: "ready_to_publish",
        BLOCKED_DECISION: "blocked",
        FAIL_CLOSED_DECISION: "fail_closed",
        INCOMPLETE_DECISION: "incomplete",
        REVIEW_DECISION: "review_required",
    }.get(decision, "review_required")


def recommended_next_action(decision: str) -> str:
    if decision == READY_DECISION:
        return "Review the manifest, then publish through scripts/asf_publish_step.ps1 with the standard human gates."
    if decision == FAIL_CLOSED_DECISION:
        return "Review the fail-closed evidence and regenerate the run only after the ambiguity is resolved."
    if decision == BLOCKED_DECISION:
        return "Resolve blockers, then regenerate the manifest before any publication step."
    if decision == INCOMPLETE_DECISION:
        return "Regenerate the evidence pack because required artifacts or checks are missing."
    return "Review the run manually before deciding whether it can move toward publication."


def build_machine_readable(
    *,
    artifacts: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    missing_artifacts: list[str],
    failed_checks: list[str],
    decision: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_count": len(artifacts),
        "required_artifacts_missing": missing_artifacts,
        "required_checks_failed": failed_checks,
        "checks_count": len(checks),
        "decision": decision,
        "publication_actions_executed": False,
        "phase_b_executed": False,
        "phase_c_executed": False,
    }


def human_summary(manifest: dict[str, Any]) -> str:
    return (
        f"Run {manifest['run_id']} for step {manifest['step']} is "
        f"{manifest['status']} with decision {manifest['decision']}."
    )


def fail_closed_manifest_for_error(
    *,
    error: str,
    source_type: str,
    source_path: str,
    step: str,
    scenario: str,
    run_id: str | None,
    created_at: str | None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    step_value = compact_string(step, fallback="unknown")
    scenario_value = compact_string(scenario, fallback="unknown")
    blockers = [f"Input could not be normalized: {error}"]
    decision = FAIL_CLOSED_DECISION
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or make_run_id(step_value, scenario_value, created),
        "created_at": created,
        "step": step_value,
        "scenario": scenario_value,
        "source": {"type": source_type, "path": source_path},
        "status": status_from_decision(decision),
        "decision": decision,
        "risk": {},
        "gate": {},
        "verification_profile": {},
        "state": {"current_state": "UNKNOWN"},
        "publish_config": {},
        "artifacts": [],
        "checks": [],
        "warnings": [],
        "blockers": blockers,
        "recommended_next_action": recommended_next_action(decision),
        "fail_closed": True,
        "human_summary": "",
        "machine_readable": build_machine_readable(
            artifacts=[],
            checks=[],
            missing_artifacts=[],
            failed_checks=[],
            decision=decision,
        ),
    }
    manifest["human_summary"] = human_summary(manifest)
    return manifest


def manifest_from_evidence_dir(
    *,
    evidence_dir: Path,
    step: str,
    scenario: str,
    run_id: str | None,
    created_at: str | None,
    root: Path,
) -> dict[str, Any]:
    created = created_at or utc_now()
    payloads, warnings, blockers = load_evidence_payloads(evidence_dir)
    input_step = payloads.get("input_step", {})
    summary = payloads.get("evidence_summary_json", {})
    scenario_value = compact_string(scenario, fallback=compact_string(summary.get("scenario"), fallback=compact_string(input_step.get("scenario"), fallback="unknown")))
    step_value = compact_string(step, fallback=compact_string(input_step.get("step"), fallback="unknown"))
    artifacts = artifacts_from_evidence_dir(evidence_dir, scenario=scenario_value, root=root)
    checks = checks_from_evidence(payloads)
    missing = missing_required_artifacts(artifacts)
    failed = failed_required_checks(checks)
    state = {
        "before": payloads.get("state_before", {}),
        "after": payloads.get("state_after", {}),
        "current_state": current_state({"before": payloads.get("state_before", {}), "after": payloads.get("state_after", {})}),
    }
    negative = payloads.get("negative_fail_closed", {})
    fail_closed = bool(negative.get("observed_fail_closed")) or compact_string(summary.get("status")).casefold() == "fail_closed"
    decision = decide(
        explicit_decision=summary.get("decision"),
        fail_closed=fail_closed,
        blockers=blockers,
        missing_artifacts=missing,
        failed_checks=failed,
        state=state,
        source_status=compact_string(summary.get("status")),
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or make_run_id(step_value, scenario_value, created),
        "created_at": created,
        "step": step_value,
        "scenario": scenario_value,
        "source": {"type": "evidence_dir", "path": display_path(evidence_dir, root=root)},
        "status": status_from_decision(decision),
        "decision": decision,
        "risk": payloads.get("risk_report", {}),
        "gate": payloads.get("gate_decision_packet", {}),
        "verification_profile": payloads.get("verification_profile", {}),
        "state": state,
        "publish_config": payloads.get("publish_config", {}),
        "artifacts": artifacts,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "recommended_next_action": recommended_next_action(decision),
        "fail_closed": fail_closed,
        "human_summary": "",
        "machine_readable": build_machine_readable(
            artifacts=artifacts,
            checks=checks,
            missing_artifacts=missing,
            failed_checks=failed,
            decision=decision,
        ),
    }
    manifest["human_summary"] = human_summary(manifest)
    return manifest


def manifest_from_input_file(
    *,
    input_file: Path,
    run_id: str | None,
    created_at: str | None,
) -> dict[str, Any]:
    raw = read_json_object(input_file)
    created = created_at or compact_string(raw.get("created_at"), fallback=utc_now())
    artifacts = [normalize_input_artifact(item, base_dir=input_file.parent) for item in raw.get("artifacts", [])]
    checks = [normalize_check(item) for item in raw.get("checks", [])]
    state = as_dict(raw.get("state"))
    if "current_state" not in state:
        state = {**state, "current_state": current_state(state)}
    warnings = compact_list(raw.get("warnings"))
    blockers = compact_list(raw.get("blockers"))
    missing = missing_required_artifacts(artifacts)
    failed = failed_required_checks(checks)
    fail_closed = bool(raw.get("fail_closed")) or normalize_decision(raw.get("decision")) == FAIL_CLOSED_DECISION
    decision = decide(
        explicit_decision=raw.get("decision"),
        fail_closed=fail_closed,
        blockers=blockers,
        missing_artifacts=missing,
        failed_checks=failed,
        state=state,
        source_status=compact_string(raw.get("status")),
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or compact_string(raw.get("run_id"), fallback=make_run_id(compact_string(raw.get("step"), fallback="unknown"), compact_string(raw.get("scenario"), fallback="unknown"), created)),
        "created_at": created,
        "step": compact_string(raw.get("step"), fallback="unknown"),
        "scenario": compact_string(raw.get("scenario"), fallback="unknown"),
        "source": {"type": "input_file", "path": str(input_file)},
        "status": status_from_decision(decision),
        "decision": decision,
        "risk": as_dict(raw.get("risk")),
        "gate": as_dict(raw.get("gate")),
        "verification_profile": as_dict(raw.get("verification_profile")),
        "state": state,
        "publish_config": as_dict(raw.get("publish_config")),
        "artifacts": artifacts,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "recommended_next_action": compact_string(raw.get("recommended_next_action"), fallback=recommended_next_action(decision)),
        "fail_closed": fail_closed,
        "human_summary": compact_string(raw.get("human_summary")),
        "machine_readable": build_machine_readable(
            artifacts=artifacts,
            checks=checks,
            missing_artifacts=missing,
            failed_checks=failed,
            decision=decision,
        ),
    }
    if not manifest["human_summary"]:
        manifest["human_summary"] = human_summary(manifest)
    return manifest


def markdown_bullets(items: list[str], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(manifest: dict[str, Any]) -> str:
    artifacts = manifest.get("artifacts", [])
    checks = manifest.get("checks", [])
    artifact_lines = [
        "| name | kind | required | exists | size_bytes | sha256 | path |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for item in artifacts:
        checksum = compact_string(item.get("sha256"), fallback="-")
        if checksum != "-":
            checksum = checksum[:16]
        artifact_lines.append(
            "| {name} | {kind} | {required} | {exists} | {size} | {sha} | `{path}` |".format(
                name=item.get("name"),
                kind=item.get("kind"),
                required=str(bool(item.get("required"))).lower(),
                exists=str(bool(item.get("exists"))).lower(),
                size=item.get("size_bytes"),
                sha=checksum,
                path=item.get("path"),
            )
        )
    check_lines = [
        "| name | status | required | exit_code | command |",
        "|---|---|---:|---:|---|",
    ]
    for check in checks:
        check_lines.append(
            "| {name} | {status} | {required} | {exit_code} | `{command}` |".format(
                name=check.get("name"),
                status=check.get("status"),
                required=str(bool(check.get("required"))).lower(),
                exit_code=check.get("exit_code") if check.get("exit_code") is not None else "-",
                command=check.get("command") or "-",
            )
        )
    risk_level = compact_string(as_dict(manifest.get("risk")).get("risk_level"), fallback="-")
    gate_decision = compact_string(as_dict(manifest.get("gate")).get("decision"), fallback="-")
    profile = compact_string(as_dict(manifest.get("verification_profile")).get("profile"), fallback="-")
    return f"""# ASF Motor Run Summary

## Run

- run id: `{manifest.get("run_id")}`
- step: `{manifest.get("step")}`
- scenario: `{manifest.get("scenario")}`
- status: `{manifest.get("status")}`
- decision: `{manifest.get("decision")}`
- state: `{current_state(as_dict(manifest.get("state")))}`
- risk: `{risk_level}`
- gate: `{gate_decision}`
- verification profile: `{profile}`
- fail closed: `{str(bool(manifest.get("fail_closed"))).lower()}`

## Artifacts

{chr(10).join(artifact_lines)}

## Checks

{chr(10).join(check_lines)}

## Warnings

{markdown_bullets(compact_list(manifest.get("warnings")))}

## Blockers

{markdown_bullets(compact_list(manifest.get("blockers")))}

## Recommended Next Action

{manifest.get("recommended_next_action")}

## Human Summary

{manifest.get("human_summary")}
"""


def output_complete_text(manifest: dict[str, Any], markdown: str) -> str:
    return (
        "# ASF Motor Run Output Completo\n\n"
        + markdown
        + "\n## Manifest JSON\n\n```json\n"
        + json.dumps(manifest, indent=2, sort_keys=True)
        + "\n```\n"
    )


def write_local_outputs(out_dir: Path, manifest: dict[str, Any], markdown: str) -> dict[str, str]:
    manifest_path = out_dir / "motor_run_manifest.json"
    summary_path = out_dir / "motor_run_summary.md"
    write_json(manifest_path, manifest)
    write_text(summary_path, markdown)
    return {"manifest": str(manifest_path), "summary": str(summary_path)}


def write_bridge_outputs(bridge_root: Path, manifest: dict[str, Any], markdown: str) -> dict[str, str]:
    stem = slugify(compact_string(manifest.get("run_id"), fallback="motor_run"))
    manifest_path = bridge_root / f"0710-Run_Manifest_{stem}.json"
    summary_path = bridge_root / f"0710-Run_Summary_{stem}.md"
    complete_path = bridge_root / f"0710-Output_Completo_{stem}.txt"
    last_manifest = bridge_root / "LAST-Run_Manifest.json"
    last_summary = bridge_root / "LAST-Run_Summary.md"
    last_complete = bridge_root / "LAST-Output_Completo.txt"
    complete = output_complete_text(manifest, markdown)
    write_json(manifest_path, manifest)
    write_json(last_manifest, manifest)
    write_text(summary_path, markdown)
    write_text(last_summary, markdown)
    write_text(complete_path, complete)
    write_text(last_complete, complete)
    return {
        "manifest": str(manifest_path),
        "summary": str(summary_path),
        "complete": str(complete_path),
        "last_manifest": str(last_manifest),
        "last_summary": str(last_summary),
        "last_complete": str(last_complete),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an ASF motor run manifest and evidence summary.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--evidence-dir", help="Existing evidence directory to scan.")
    source.add_argument("--input-file", help="Input manifest JSON to normalize.")
    parser.add_argument("--step", default="", help="Step identifier for evidence-dir mode.")
    parser.add_argument("--scenario", default="", help="Scenario name for evidence-dir mode.")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Local output directory.")
    parser.add_argument("--run-id", default="", help="Optional explicit run id.")
    parser.add_argument("--created-at", default="", help="Optional ISO timestamp for deterministic output.")
    parser.add_argument("--write-bridge", action="store_true", help="Write manifest outputs to a Bridge root.")
    parser.add_argument("--bridge-root", default=DEFAULT_BRIDGE_ROOT, help="Bridge root for optional output.")
    parser.add_argument("--json", action="store_true", help="Print manifest JSON.")
    parser.add_argument("--markdown", action="store_true", help="Print summary Markdown.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out_dir)
    root = Path.cwd()
    try:
        if args.evidence_dir:
            manifest = manifest_from_evidence_dir(
                evidence_dir=Path(args.evidence_dir),
                step=args.step,
                scenario=args.scenario,
                run_id=compact_string(args.run_id) or None,
                created_at=compact_string(args.created_at) or None,
                root=root,
            )
        else:
            manifest = manifest_from_input_file(
                input_file=Path(args.input_file),
                run_id=compact_string(args.run_id) or None,
                created_at=compact_string(args.created_at) or None,
            )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        manifest = fail_closed_manifest_for_error(
            error=str(exc),
            source_type="evidence_dir" if args.evidence_dir else "input_file",
            source_path=args.evidence_dir or args.input_file,
            step=args.step,
            scenario=args.scenario,
            run_id=compact_string(args.run_id) or None,
            created_at=compact_string(args.created_at) or None,
        )
        markdown = render_markdown(manifest)
        write_local_outputs(out_dir, manifest, markdown)
        if args.write_bridge:
            write_bridge_outputs(Path(args.bridge_root), manifest, markdown)
        if args.json:
            print(json.dumps(manifest, indent=2, sort_keys=True))
        elif args.markdown:
            print(markdown, end="")
        else:
            print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    markdown = render_markdown(manifest)
    local_paths = write_local_outputs(out_dir, manifest, markdown)
    bridge_paths: dict[str, str] = {}
    if args.write_bridge:
        bridge_paths = write_bridge_outputs(Path(args.bridge_root), manifest, markdown)

    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown, end="")
    else:
        print(f"decision: {manifest['decision']}")
        print(f"manifest: {local_paths['manifest']}")
        print(f"summary: {local_paths['summary']}")
        if bridge_paths:
            print(f"bridge: {bridge_paths['last_manifest']}")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
