from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
PROFILES = {"docs-only", "code-unit", "motor-core", "publish", "final-main", "high-risk"}

MOTOR_CORE_FILES = {
    "scripts/asf_publish_step.ps1",
    "scripts/asf_publish_config_generator.py",
    "scripts/asf_dry_run_loop_runner.py",
    "scripts/asf_risk_classifier.py",
    "scripts/asf_gate_decision_report.py",
    "scripts/asf_verification_profile_selector.py",
    "scripts/asf_step_state_machine.py",
    "scripts/asf_e2e_mvp_smoke.py",
    "scripts/check_workflow_health.py",
}

SCRIPT_TESTS = {
    "scripts/asf_publish_step.ps1": "python -m pytest tests/unit/test_asf_publish_step_runner.py -q",
    "scripts/asf_publish_config_generator.py": "python -m pytest tests/unit/test_asf_publish_config_generator.py -q",
    "scripts/asf_dry_run_loop_runner.py": "python -m pytest tests/unit/test_asf_dry_run_loop_runner.py -q",
    "scripts/asf_risk_classifier.py": "python -m pytest tests/unit/test_asf_risk_classifier.py -q",
    "scripts/asf_gate_decision_report.py": "python -m pytest tests/unit/test_asf_gate_decision_report.py -q",
    "scripts/asf_verification_profile_selector.py": "python -m pytest tests/unit/test_asf_verification_profile_selector.py -q",
    "scripts/asf_step_state_machine.py": "python -m pytest tests/unit/test_asf_step_state_machine.py -q",
    "scripts/asf_e2e_mvp_smoke.py": "python -m pytest tests/unit/test_asf_e2e_mvp_smoke.py -q",
    "scripts/check_workflow_health.py": "python -m pytest tests/unit/test_workflow_health_check.py -q",
}

INDEXED_DOC_PATHS = {
    "README.md",
    "CHANGELOG.md",
    "docs/10_ROADMAP.md",
    "docs/11_DECISIONS.md",
    "docs/34_PROJECT_WORKFLOW_INDEX.md",
    "docs/35_WORKFLOW_HEALTH_CHECK.md",
    "docs/motor/0570_MVP_MOTOR_ROADMAP.md",
    "docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md",
    "docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",
    "docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md",
    "docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md",
    "docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md",
    "docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md",
    "docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md",
    "docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md",
    "docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md",
}

PUBLISH_INTENT_KEYWORDS = (
    "commit",
    "push",
    "pull request",
    "open pr",
    "create pr",
    "publish",
    "publication",
    "approvepublish",
    "phase b",
)

FINAL_PHASE_KEYWORDS = ("final", "final-main", "post-merge", "phase c", "main verification")

HIGH_RISK_KEYWORDS = (
    "deploy",
    "production",
    "prod",
    "delete",
    "remove",
    "destructive",
    "destroy",
    "wipe",
    "purge",
    "drop table",
    "secret",
    "secrets",
    "token",
    "credential",
    "password",
    "private key",
    "external side effect",
    "live provider",
    "network call",
    "merge",
)


@dataclass(frozen=True)
class SelectorInput:
    risk_level: str = ""
    changed_files: tuple[str, ...] = ()
    step_type: str = ""
    phase: str = "local"
    intent: tuple[str, ...] = ()
    checks_already_run: tuple[str, ...] = ()
    provided_gates: tuple[str, ...] = ()


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
        items: list[str] = []
        for item in value:
            text = compact_string(item)
            if text:
                items.append(text)
        return items
    text = compact_string(value)
    return [text] if text else []


def collect_string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        collected: list[str] = []
        for item in value:
            collected.extend(collect_string_values(item))
        return collected
    if isinstance(value, dict):
        collected = []
        for item in value.values():
            collected.extend(collect_string_values(item))
        return collected
    return []


def first_string(*values: Any, fallback: str = "") -> str:
    for value in values:
        text = compact_string(value)
        if text:
            return text
    return fallback


def nested_value(raw: dict[str, Any], *keys: str) -> Any:
    current: Any = raw
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def list_from_json_field(raw: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    collected: list[str] = []
    for name in names:
        if name in raw:
            collected.extend(collect_string_values(raw[name]))
    return tuple(dict.fromkeys(item.strip() for item in collected if item.strip()))


def normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def normalize_check(value: str) -> str:
    return " ".join(value.casefold().replace("\\", "/").split())


def dedupe(items: list[str] | tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def selector_input_from_json(raw: dict[str, Any]) -> SelectorInput:
    risk_level = first_string(
        raw.get("risk_level"),
        nested_value(raw, "risk", "risk_level"),
        nested_value(raw, "risk_report", "risk", "risk_level"),
        nested_value(raw, "risk_checkpoint", "risk", "risk_level"),
        nested_value(raw, "risk_result", "risk_level"),
    )

    changed_files = list_from_json_field(
        raw,
        (
            "changed_files",
            "files_changed",
            "modified_files",
            "file_paths",
            "files",
            "files_in_scope",
            "allowed_scope",
            "expected_files",
        ),
    )
    changed_files += tuple(compact_list(nested_value(raw, "request", "allowed_scope")))
    changed_files += tuple(compact_list(nested_value(raw, "normalized_request", "allowed_scope")))

    intent = list_from_json_field(
        raw,
        (
            "intent",
            "intents",
            "actions",
            "operation_keywords",
            "objective",
            "summary",
            "description",
            "title",
            "notes",
        ),
    )

    checks = list_from_json_field(
        raw,
        (
            "checks_already_run",
            "completed_checks",
            "checks_executed",
            "reported_checks",
            "check_results",
            "verification_results",
        ),
    )
    gates = list_from_json_field(raw, ("provided_gates", "declared_gates", "satisfied_gates"))

    return SelectorInput(
        risk_level=risk_level,
        changed_files=tuple(dedupe([normalize_path(item) for item in changed_files])),
        step_type=compact_string(raw.get("step_type")),
        phase=first_string(raw.get("phase"), raw.get("requested_phase"), fallback="local"),
        intent=tuple(dedupe(list(intent))),
        checks_already_run=tuple(dedupe(list(checks))),
        provided_gates=tuple(dedupe(list(gates))),
    )


def read_input_file(path: Path) -> SelectorInput:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {path}: {exc}") from exc

    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Input file is not valid JSON: {path}: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Input JSON must be an object.")
    return selector_input_from_json(raw)


def merge_inputs(left: SelectorInput, right: SelectorInput) -> SelectorInput:
    return SelectorInput(
        risk_level=left.risk_level or right.risk_level,
        changed_files=tuple(dedupe(list(right.changed_files) + list(left.changed_files))),
        step_type=left.step_type or right.step_type,
        phase=left.phase if left.phase != "local" else right.phase,
        intent=tuple(dedupe(list(right.intent) + list(left.intent))),
        checks_already_run=tuple(dedupe(list(right.checks_already_run) + list(left.checks_already_run))),
        provided_gates=tuple(dedupe(list(right.provided_gates) + list(left.provided_gates))),
    )


def is_doc_file(path: str) -> bool:
    normalized = normalize_path(path)
    return normalized.endswith(".md") and (
        normalized.startswith("docs/")
        or normalized in {"README.md", "CHANGELOG.md", "AGENTS.md"}
    )


def is_code_or_test_file(path: str) -> bool:
    normalized = normalize_path(path)
    return normalized.startswith("tests/") or normalized.endswith((".py", ".ps1"))


def has_indexed_docs(paths: tuple[str, ...]) -> bool:
    return any(path in INDEXED_DOC_PATHS or path.startswith("docs/motor/") for path in paths)


def contains_keyword(values: tuple[str, ...] | list[str], keywords: tuple[str, ...]) -> bool:
    text = " ".join(values).casefold()
    return any(keyword in text for keyword in keywords)


def targeted_test_checks(paths: tuple[str, ...]) -> list[str]:
    checks: list[str] = []
    for path in paths:
        normalized = normalize_path(path)
        if normalized.startswith("tests/") and normalized.endswith(".py"):
            checks.append(f"python -m pytest {normalized} -q")
            continue
        if normalized in SCRIPT_TESTS:
            checks.append(SCRIPT_TESTS[normalized])
            continue
        if normalized.startswith("scripts/") and normalized.endswith(".py"):
            stem = Path(normalized).stem
            checks.append(f"python -m pytest tests/unit/test_{stem}.py -q")
    return dedupe(checks)


def already_run(check: str, checks_already_run: tuple[str, ...]) -> bool:
    normalized = normalize_check(check)
    for item in checks_already_run:
        current = normalize_check(item)
        if not current:
            continue
        if normalized == current or normalized in current or current in normalized:
            return True
    return False


def remove_already_run(checks: list[str], checks_already_run: tuple[str, ...]) -> tuple[list[str], list[str]]:
    remaining: list[str] = []
    skipped: list[str] = []
    for check in checks:
        if already_run(check, checks_already_run):
            skipped.append(f"already executed: {check}")
        else:
            remaining.append(check)
    return remaining, skipped


def base_packet(
    *,
    profile: str,
    risk_level: str,
    confidence: str,
    recommended_checks: list[str],
    required_checks: list[str],
    optional_checks: list[str],
    skipped_checks: list[str],
    reasons: list[str],
    warnings: list[str],
    estimated_cost: str,
    safety_notes: list[str],
    fail_closed: bool,
    recommended_next_action: str,
) -> dict[str, Any]:
    return {
        "profile": profile,
        "risk_level": risk_level or "UNKNOWN",
        "confidence": confidence,
        "recommended_checks": dedupe(recommended_checks),
        "skipped_checks": dedupe(skipped_checks),
        "required_checks": dedupe(required_checks),
        "optional_checks": dedupe(optional_checks),
        "reasons": dedupe(reasons),
        "warnings": dedupe(warnings),
        "estimated_cost": estimated_cost,
        "safety_notes": dedupe(safety_notes),
        "fail_closed": fail_closed,
        "recommended_next_action": recommended_next_action,
    }


def fail_closed_packet(risk_level: str, reason: str) -> dict[str, Any]:
    return base_packet(
        profile="high-risk",
        risk_level=risk_level or "UNKNOWN",
        confidence="high",
        recommended_checks=[
            "manual review",
            "elevated manual approval",
            "python -m pytest -q",
            "python scripts/check_workflow_health.py",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1",
            "git --no-pager diff --check",
            "git status --short --untracked-files=all",
        ],
        required_checks=[
            "manual review",
            "elevated manual approval",
            "full local verification",
        ],
        optional_checks=[],
        skipped_checks=["no automation shortcut allowed"],
        reasons=[reason],
        warnings=["Input is empty, ambiguous, invalid, or high-risk; selector fails closed."],
        estimated_cost="high",
        safety_notes=[
            "Do not publish, merge, deploy, delete, or touch secrets from this recommendation.",
            "Use a separate human approval path before any operational action.",
        ],
        fail_closed=True,
        recommended_next_action="Stop and complete manual review before choosing any reduced verification profile.",
    )


def build_docs_only(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    required = ["git --no-pager diff --check"]
    recommended = list(required)
    optional = ["python -m pytest -q"]
    skipped = ["full pytest not required for ordinary docs-only changes"]
    if has_indexed_docs(data.changed_files):
        required.append("python scripts/check_workflow_health.py")
        recommended.append("python scripts/check_workflow_health.py")
        optional.append("pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1")
    recommended, already = remove_already_run(recommended, data.checks_already_run)
    skipped.extend(already)
    if not risk_level:
        warnings.append("risk_level not provided; docs-only recommendation is based on file scope only.")
    return base_packet(
        profile="docs-only",
        risk_level=risk_level,
        confidence="high",
        recommended_checks=recommended,
        required_checks=required,
        optional_checks=optional,
        skipped_checks=skipped,
        reasons=reasons,
        warnings=warnings,
        estimated_cost="low",
        safety_notes=[
            "Documentation-only profile is a recommendation, not a publication approval.",
            "Escalate to motor-core if docs change critical workflow behavior or indexed contracts.",
        ],
        fail_closed=False,
        recommended_next_action="Run the required docs checks; use full verification only if the docs change workflow behavior.",
    )


def build_code_unit(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    target_checks = targeted_test_checks(data.changed_files) or ["python -m pytest tests/unit -q"]
    required = target_checks + ["git --no-pager diff --check"]
    recommended = list(required)
    optional = [
        "python -m pytest -q",
        "python scripts/check_workflow_health.py",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1",
    ]
    if has_indexed_docs(data.changed_files):
        required.append("python scripts/check_workflow_health.py")
        recommended.append("python scripts/check_workflow_health.py")
    recommended, skipped = remove_already_run(recommended, data.checks_already_run)
    return base_packet(
        profile="code-unit",
        risk_level=risk_level,
        confidence="medium",
        recommended_checks=recommended,
        required_checks=required,
        optional_checks=optional,
        skipped_checks=skipped,
        reasons=reasons,
        warnings=warnings,
        estimated_cost="medium",
        safety_notes=[
            "Use targeted tests first for local iteration.",
            "Escalate to motor-core if the touched module controls runner, gate, risk, publish, or workflow health behavior.",
        ],
        fail_closed=False,
        recommended_next_action="Run targeted tests and diff check; run full pytest before broad review or if confidence drops.",
    )


def build_motor_core(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    target_checks = targeted_test_checks(data.changed_files)
    linked = [
        "python -m pytest tests/unit/test_asf_gate_decision_report.py -q",
        "python -m pytest tests/unit/test_asf_dry_run_loop_runner.py -q",
        "python -m pytest tests/unit/test_asf_risk_classifier.py -q",
    ]
    if "scripts/asf_verification_profile_selector.py" in data.changed_files:
        linked.insert(0, "python -m pytest tests/unit/test_asf_verification_profile_selector.py -q")
    required = dedupe(target_checks + linked + ["python -m pytest -q", "python scripts/check_workflow_health.py", "git --no-pager diff --check"])
    recommended = required + ["pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1"]
    optional = ["Phase C final verification on main before merge closure"]
    recommended, skipped = remove_already_run(recommended, data.checks_already_run)
    return base_packet(
        profile="motor-core",
        risk_level=risk_level,
        confidence="high",
        recommended_checks=recommended,
        required_checks=required,
        optional_checks=optional,
        skipped_checks=skipped,
        reasons=reasons,
        warnings=warnings,
        estimated_cost="high",
        safety_notes=[
            "Motor-core changes keep full verification in the recommended path.",
            "Do not use reduced docs-only or code-unit gates for runner, gate, risk, publish, or workflow health files.",
        ],
        fail_closed=False,
        recommended_next_action="Run targeted regression tests, full pytest, workflow health, diff check, and verify gate.",
    )


def build_publish(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    required = [
        "explicit publish approval",
        "publish runner Phase B",
        "git status --short --untracked-files=all",
    ]
    recommended = list(required)
    optional = ["Phase C final verification after merge"]
    skipped = ["do not run Phase A separately when Phase B already reruns it"]
    recommended, already = remove_already_run(recommended, data.checks_already_run)
    skipped.extend(already)
    fail_closed = not any(gate.casefold() in {"explicit_publish_approval", "approve_publish"} for gate in data.provided_gates)
    if fail_closed:
        warnings.append("explicit_publish_approval was not declared; publish profile remains fail-closed.")
    return base_packet(
        profile="publish",
        risk_level=risk_level,
        confidence="high",
        recommended_checks=recommended,
        required_checks=required,
        optional_checks=optional,
        skipped_checks=skipped,
        reasons=reasons,
        warnings=warnings,
        estimated_cost="medium",
        safety_notes=[
            "Use the versioned publish runner instead of manual duplicate checks.",
            "Publication remains human-gated and is not executed by this selector.",
        ],
        fail_closed=fail_closed,
        recommended_next_action="Use Phase B of scripts/asf_publish_step.ps1 only after explicit approval and clean local evidence.",
    )


def build_final_main(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    required = [
        "publish runner Phase C",
        "python scripts/check_workflow_health.py",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1",
        "git --no-pager diff --check",
        "git status --short --untracked-files=all",
    ]
    recommended, skipped = remove_already_run(list(required), data.checks_already_run)
    return base_packet(
        profile="final-main",
        risk_level=risk_level,
        confidence="high",
        recommended_checks=recommended,
        required_checks=required,
        optional_checks=["python -m pytest -q if verify.ps1 was not already run in the same final gate"],
        skipped_checks=skipped,
        reasons=reasons,
        warnings=warnings,
        estimated_cost="high",
        safety_notes=[
            "Final-main verification is the compensation gate for earlier conditional checks.",
            "Working tree must be clean after final verification.",
        ],
        fail_closed=False,
        recommended_next_action="Run Phase C and final local gates on main; stop on dirty tree or failing checks.",
    )


def build_high_risk(data: SelectorInput, risk_level: str, reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    elevated = any(gate.casefold() in {"elevated_manual_approval", "manual_approval"} for gate in data.provided_gates)
    packet = fail_closed_packet(risk_level, reasons[0] if reasons else "High-risk signal detected.")
    packet["reasons"] = dedupe(reasons)
    packet["warnings"] = dedupe(warnings + packet["warnings"])
    packet["fail_closed"] = not elevated
    if elevated:
        packet["warnings"].append("Elevated approval declared, but high-risk actions still require separate manual review.")
        packet["recommended_next_action"] = "Keep automation disabled and complete separate manual review with rollback planning."
    return packet


def select_profile(data: SelectorInput) -> dict[str, Any]:
    paths = tuple(normalize_path(path) for path in data.changed_files)
    risk_level = data.risk_level.upper()
    reasons: list[str] = []
    warnings: list[str] = []
    signal_values = paths + data.intent + (data.step_type, data.phase)
    intent_values = data.intent + (data.step_type, data.phase)
    high_risk_values = paths + data.intent + (data.step_type,)

    if risk_level and risk_level not in RISK_LEVELS:
        return fail_closed_packet(risk_level, f"Unknown risk_level `{data.risk_level}`; refusing to infer safety.")
    if not any(compact_string(item) for item in signal_values) and not risk_level:
        return fail_closed_packet(risk_level, "Input is empty; refusing to infer a verification profile.")

    if risk_level == "L4" or contains_keyword(high_risk_values, HIGH_RISK_KEYWORDS):
        reasons.append("L4 or high-risk intent detected.")
        return build_high_risk(data, risk_level, reasons, warnings)

    if contains_keyword((data.phase, data.step_type), FINAL_PHASE_KEYWORDS):
        reasons.append("Final or post-merge verification phase requested.")
        return build_final_main(data, risk_level, reasons, warnings)

    if risk_level == "L3" or contains_keyword(intent_values, PUBLISH_INTENT_KEYWORDS):
        reasons.append("L3 risk or publication intent detected.")
        return build_publish(data, risk_level or "L3", reasons, warnings)

    if any(path in MOTOR_CORE_FILES for path in paths):
        reasons.append("Runner, gate, risk, publish, workflow health, or verification selector file changed.")
        return build_motor_core(data, risk_level or "L2", reasons, warnings)

    if paths and all(is_doc_file(path) for path in paths):
        reasons.append("Changed files are documentation-only.")
        return build_docs_only(data, risk_level, reasons, warnings)

    if paths and any(is_code_or_test_file(path) for path in paths):
        reasons.append("Changed files include scoped source or tests outside motor-core.")
        return build_code_unit(data, risk_level or "L2", reasons, warnings)

    if contains_keyword(data.intent, ("docs only", "documentation", "read-only", "inspect")):
        reasons.append("Intent is documentation or read-only oriented.")
        return build_docs_only(data, risk_level, reasons, warnings)

    return fail_closed_packet(risk_level, "Input is ambiguous or does not match a known low-risk profile.")


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def bullets(items: list[Any], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(packet: dict[str, Any]) -> str:
    return f"""# Verification Profile Recommendation

## Summary

- profile: `{packet["profile"]}`
- risk_level: `{packet["risk_level"]}`
- confidence: `{packet["confidence"]}`
- estimated_cost: `{packet["estimated_cost"]}`
- fail_closed: `{str(packet["fail_closed"]).lower()}`

## Recommended checks

{bullets(packet["recommended_checks"])}

## Required checks

{bullets(packet["required_checks"])}

## Optional checks

{bullets(packet["optional_checks"])}

## Skipped checks

{bullets(packet["skipped_checks"])}

## Reasons

{bullets(packet["reasons"])}

## Warnings

{bullets(packet["warnings"])}

## Safety notes

{bullets(packet["safety_notes"])}

## Next action

{packet["recommended_next_action"]}
"""


def render_text(packet: dict[str, Any]) -> str:
    return (
        f"profile: {packet['profile']}\n"
        f"risk_level: {packet['risk_level']}\n"
        f"confidence: {packet['confidence']}\n"
        f"estimated_cost: {packet['estimated_cost']}\n"
        f"fail_closed: {str(packet['fail_closed']).lower()}\n"
        f"recommended_next_action: {packet['recommended_next_action']}\n"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a prudent ASF verification profile from risk, files, phase and intent.",
    )
    parser.add_argument("--input-file", help="Input JSON with risk_level, changed_files, phase, intent and checks.")
    parser.add_argument("--risk-level", help="Risk level L0-L4.")
    parser.add_argument("--changed-files", nargs="*", default=[], help="Changed file paths.")
    parser.add_argument("--step-type", default="", help="Step type, such as docs, code, motor, publish or final.")
    parser.add_argument("--phase", default="local", help="Requested phase: local, publish or final-main.")
    parser.add_argument("--intent", action="append", default=[], help="Intent text. Can be passed more than once.")
    parser.add_argument("--check-executed", action="append", default=[], help="Already executed check.")
    parser.add_argument("--provided-gate", action="append", default=[], help="Provided gate token.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown output.")
    return parser.parse_args(argv)


def input_from_args(args: argparse.Namespace) -> SelectorInput:
    return SelectorInput(
        risk_level=compact_string(args.risk_level),
        changed_files=tuple(normalize_path(item) for item in compact_list(args.changed_files)),
        step_type=compact_string(args.step_type),
        phase=compact_string(args.phase) or "local",
        intent=tuple(compact_list(args.intent)),
        checks_already_run=tuple(compact_list(args.check_executed)),
        provided_gates=tuple(compact_list(args.provided_gate)),
    )


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    data = input_from_args(args)
    if args.input_file:
        try:
            data = merge_inputs(data, read_input_file(Path(args.input_file)))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_INPUT_ERROR

    packet = select_profile(data)
    if args.json:
        print(render_json(packet), end="")
    elif args.markdown:
        print(render_markdown(packet), end="")
    else:
        print(render_text(packet), end="")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
