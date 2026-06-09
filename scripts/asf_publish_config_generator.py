from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

REQUIRED_INPUT_FIELDS = (
    "step",
    "name",
    "branch",
    "commit_message",
    "pr_title",
    "pr_body",
    "next_step",
    "expected_files",
    "risk_level",
    "verification_phase",
    "intent",
    "provided_gates",
    "allow_profile_check_reduction",
)

DEFAULT_RUNNER_BRIDGE_ROOT = r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
DEFAULT_PUBLISH_CONFIG_BRIDGE_ROOT = (
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\publish_config"
)
DEFAULT_BRIDGE_ROOT = DEFAULT_RUNNER_BRIDGE_ROOT
BLOCKED_PROFILES = {"final-main", "high-risk"}

TARGET_TESTS = {
    "scripts/asf_publish_config_generator.py": "tests/unit/test_asf_publish_config_generator.py",
    "scripts/asf_verification_profile_selector.py": "tests/unit/test_asf_verification_profile_selector.py",
    "scripts/asf_gate_decision_report.py": "tests/unit/test_asf_gate_decision_report.py",
    "scripts/asf_dry_run_loop_runner.py": "tests/unit/test_asf_dry_run_loop_runner.py",
    "scripts/asf_risk_classifier.py": "tests/unit/test_asf_risk_classifier.py",
    "scripts/asf_publish_step.ps1": "tests/unit/test_asf_publish_step_runner.py",
    "scripts/asf_step_state_machine.py": "tests/unit/test_asf_step_state_machine.py",
    "scripts/asf_e2e_mvp_smoke.py": "tests/unit/test_asf_e2e_mvp_smoke.py",
    "scripts/check_workflow_health.py": "tests/unit/test_workflow_health_check.py",
    "scripts/show_workflow_status.py": "tests/unit/test_workflow_status_dashboard.py",
}

LINKED_MOTOR_CORE_TESTS = (
    "tests/unit/test_asf_publish_config_generator.py",
    "tests/unit/test_asf_verification_profile_selector.py",
    "tests/unit/test_asf_publish_step_runner.py",
    "tests/unit/test_asf_step_state_machine.py",
    "tests/unit/test_asf_e2e_mvp_smoke.py",
)

INDEXED_DOCS = {
    "README.md",
    "CHANGELOG.md",
    "docs/10_ROADMAP.md",
    "docs/11_DECISIONS.md",
    "docs/34_PROJECT_WORKFLOW_INDEX.md",
    "docs/35_WORKFLOW_HEALTH_CHECK.md",
    "docs/motor/0570_MVP_MOTOR_ROADMAP.md",
    "docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",
    "docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md",
    "docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md",
    "docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md",
    "docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md",
    "docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md",
    "docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md",
    "docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md",
    "docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md",
}

CONFIG_DRAFT_INTENT_PATTERNS = (
    (re.compile(r"\bpublish\s+config\b", re.IGNORECASE), "runner config"),
    (re.compile(r"\bconfig\s+publish\b", re.IGNORECASE), "runner config"),
    (re.compile(r"\bpublish\s+runner\b", re.IGNORECASE), "runner"),
)


@dataclass(frozen=True)
class GeneratorInput:
    step: str
    name: str
    branch: str
    commit_message: str
    pr_title: str
    pr_body: str
    next_step: str
    expected_files: tuple[str, ...]
    risk_level: str
    verification_phase: str
    intent: tuple[str, ...]
    provided_gates: tuple[str, ...]
    allow_profile_check_reduction: bool
    repo_path: str = "."
    bridge_root: str = DEFAULT_BRIDGE_ROOT
    changed_files: tuple[str, ...] = ()
    checks_already_run: tuple[str, ...] = ()
    profile_selector_expected_profile: str = ""
    log_max_count: int = 12
    allow_no_github_checks_reported: bool = True


@dataclass(frozen=True)
class GenerationResult:
    status: str
    config: dict[str, Any] | None
    selector_packet: dict[str, Any] | None
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    config_path: Path | None = None
    summary_path: Path | None = None


@dataclass(frozen=True)
class PreparedGeneration:
    data: GeneratorInput | None
    selector_packet: dict[str, Any] | None
    config: dict[str, Any] | None
    warnings: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class StateIntegrationResult:
    enabled: bool = False
    state_file: Path | None = None
    state_bridge_root: Path | None = None
    state_before: str = ""
    state_after: str = ""
    event: str = ""
    allowed: bool | None = None
    fail_closed: bool = False
    packet: dict[str, Any] | None = None
    bridge_files: tuple[Path, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanValidationResult:
    executed: bool
    status: str
    command: tuple[str, ...] = ()
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    bridge_root: Path | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


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


def normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def dedupe(items: list[str] | tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def slugify(value: str, *, separator: str = "-") -> str:
    text = re.sub(r"[^A-Za-z0-9]+", separator, value).strip(separator).lower()
    return text or "publish-config"


def normalize_intent_for_selector(items: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        text = item
        for pattern, replacement in CONFIG_DRAFT_INTENT_PATTERNS:
            text = pattern.sub(replacement, text)
        normalized.append(text.strip())
    return dedupe(normalized)


def parse_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    raise ValueError(f"Config field must be boolean: {field}")


def parse_int(value: Any, *, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config field must be integer: {field}") from exc
    if number < 1:
        raise ValueError(f"Config field must be positive: {field}")
    return number


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {path}: {exc}") from exc
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Input file is not valid JSON: {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object.")
    return payload


def load_selector_module() -> Any:
    selector_path = Path(__file__).with_name("asf_verification_profile_selector.py")
    spec = importlib.util.spec_from_file_location("asf_verification_profile_selector", selector_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Unable to load selector module: {selector_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_state_machine_module() -> Any:
    state_machine_path = Path(__file__).with_name("asf_step_state_machine.py")
    spec = importlib.util.spec_from_file_location("asf_step_state_machine", state_machine_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Unable to load state machine module: {state_machine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def merge_cli_values(raw: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    merged = dict(raw)
    simple_fields = (
        "step",
        "name",
        "branch",
        "commit_message",
        "pr_title",
        "pr_body",
        "next_step",
        "repo_path",
        "risk_level",
        "verification_phase",
        "profile_selector_expected_profile",
        "log_max_count",
    )
    for field in simple_fields:
        value = getattr(args, field, None)
        if value is not None and compact_string(value):
            merged[field] = value

    list_fields = ("expected_files", "changed_files", "checks_already_run")
    for field in list_fields:
        value = getattr(args, field, None)
        if value is not None:
            merged[field] = compact_list(value)

    intent_items = compact_list(getattr(args, "intent", None))
    if intent_items:
        merged["intent"] = intent_items

    provided = compact_list(getattr(args, "provided_gates", None))
    provided.extend(compact_list(getattr(args, "provided_gate", None)))
    if provided:
        merged["provided_gates"] = provided

    runner_bridge_root = compact_string(getattr(args, "runner_bridge_root", None))
    cli_bridge_root = compact_string(getattr(args, "bridge_root", None))
    if runner_bridge_root:
        merged["bridge_root"] = runner_bridge_root
    elif cli_bridge_root and not getattr(args, "write_bridge", False):
        merged["bridge_root"] = cli_bridge_root

    if args.allow_profile_check_reduction is not None:
        merged["allow_profile_check_reduction"] = args.allow_profile_check_reduction
    if args.allow_no_github_checks_reported is not None:
        merged["allow_no_github_checks_reported"] = args.allow_no_github_checks_reported
    return merged


def apply_cli_defaults(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    step = compact_string(data.get("step"))
    name = compact_string(data.get("name"))
    if step and name:
        slug = slugify(name)
        data.setdefault("branch", f"step-{step}-{slug}")
        data.setdefault("commit_message", f"{step} {name.replace('_', ' ')}")
        data.setdefault("pr_title", f"{step} {name.replace('_', ' ')}")
        data.setdefault("pr_body", f"Implements STEP {step}. Review the generated publish config before using the runner.")
        data.setdefault("next_step", "TBD")
        data.setdefault("intent", ["config draft generation"])
        data.setdefault("provided_gates", [])
        data.setdefault("allow_profile_check_reduction", False)
    data.setdefault("repo_path", ".")
    data.setdefault("bridge_root", DEFAULT_BRIDGE_ROOT)
    data.setdefault("log_max_count", 12)
    data.setdefault("allow_no_github_checks_reported", True)
    if "changed_files" not in data and "expected_files" in data:
        data["changed_files"] = data["expected_files"]
    return data


def missing_required_fields(raw: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_INPUT_FIELDS:
        if field not in raw:
            missing.append(field)
            continue
        if field == "allow_profile_check_reduction":
            continue
        value = raw[field]
        if isinstance(value, list | tuple | set):
            if not compact_list(value) and field != "provided_gates":
                missing.append(field)
        elif field != "provided_gates" and not compact_string(value):
            missing.append(field)
    return missing


def build_input(raw: dict[str, Any], *, strict_required: bool) -> GeneratorInput:
    data = dict(raw)
    if not strict_required:
        data = apply_cli_defaults(data)

    missing = missing_required_fields(data)
    if missing:
        raise ValueError("Missing required input fields: " + ", ".join(missing))

    expected_files = tuple(dedupe([normalize_path(item) for item in compact_list(data["expected_files"])]))
    if not expected_files:
        raise ValueError("expected_files must not be empty.")

    changed_files = tuple(dedupe([normalize_path(item) for item in compact_list(data.get("changed_files"))]))
    if not changed_files:
        changed_files = expected_files

    intent = tuple(normalize_intent_for_selector(compact_list(data["intent"])))

    return GeneratorInput(
        step=compact_string(data["step"]),
        name=compact_string(data["name"]),
        branch=compact_string(data["branch"]),
        commit_message=compact_string(data["commit_message"]),
        pr_title=compact_string(data["pr_title"]),
        pr_body=compact_string(data["pr_body"]),
        next_step=compact_string(data["next_step"]),
        expected_files=expected_files,
        risk_level=compact_string(data["risk_level"]).upper(),
        verification_phase=compact_string(data["verification_phase"]) or "local",
        intent=intent,
        provided_gates=tuple(dedupe(compact_list(data.get("provided_gates")))),
        allow_profile_check_reduction=parse_bool(
            data["allow_profile_check_reduction"],
            field="allow_profile_check_reduction",
        ),
        repo_path=compact_string(data.get("repo_path")) or ".",
        bridge_root=compact_string(data.get("bridge_root")) or DEFAULT_BRIDGE_ROOT,
        changed_files=changed_files,
        checks_already_run=tuple(dedupe(compact_list(data.get("checks_already_run")))),
        profile_selector_expected_profile=compact_string(data.get("profile_selector_expected_profile")),
        log_max_count=parse_int(data.get("log_max_count", 12), field="log_max_count"),
        allow_no_github_checks_reported=parse_bool(
            data.get("allow_no_github_checks_reported", True),
            field="allow_no_github_checks_reported",
        ),
    )


def command(name: str, *argv: str) -> dict[str, Any]:
    return {"name": name, "argv": list(argv)}


def pytest_command(test_path: str) -> dict[str, Any]:
    return command(f"pytest {Path(test_path).name}", "python", "-m", "pytest", test_path, "-q")


def workflow_health_command() -> dict[str, Any]:
    return command("Workflow Health Check", "python", "scripts/check_workflow_health.py")


def verify_command() -> dict[str, Any]:
    return command("Verification Gate", "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\\verify.ps1")


def full_pytest_command() -> dict[str, Any]:
    return command("Full pytest", "python", "-m", "pytest", "-q")


def dedupe_commands(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, ...]] = set()
    result: list[dict[str, Any]] = []
    for item in commands:
        argv = tuple(str(part) for part in item["argv"])
        if argv in seen:
            continue
        seen.add(argv)
        result.append(item)
    return result


def docs_are_indexed(paths: tuple[str, ...]) -> bool:
    return any(path in INDEXED_DOCS or path.startswith("docs/motor/") for path in paths)


def is_code_file(path: str) -> bool:
    return path.startswith("scripts/") and path.endswith((".py", ".ps1"))


def deduce_targeted_tests(paths: tuple[str, ...], *, root: Path | None = None) -> tuple[list[str], list[str]]:
    root = repo_root() if root is None else root
    tests: list[str] = []
    warnings: list[str] = []
    for path in paths:
        normalized = normalize_path(path)
        if normalized.startswith("tests/") and normalized.endswith(".py"):
            tests.append(normalized)
            continue
        if normalized in TARGET_TESTS:
            tests.append(TARGET_TESTS[normalized])
            continue
        if normalized.startswith("scripts/") and normalized.endswith(".py"):
            guessed = f"tests/unit/test_{Path(normalized).stem}.py"
            if (root / guessed).is_file():
                tests.append(guessed)
            else:
                warnings.append(f"No targeted unit test deduced for {normalized}; verify.ps1 will stay in Phase A.")
        elif normalized.startswith("scripts/") and normalized.endswith(".ps1"):
            warnings.append(f"No targeted unit test deduced for {normalized}; verify.ps1 will stay in Phase A.")
    return dedupe(tests), dedupe(warnings)


def select_profile(data: GeneratorInput) -> dict[str, Any]:
    selector = load_selector_module()
    selector_input = selector.SelectorInput(
        risk_level=data.risk_level,
        changed_files=data.changed_files,
        phase=data.verification_phase,
        intent=data.intent,
        checks_already_run=data.checks_already_run,
        provided_gates=data.provided_gates,
    )
    return selector.select_profile(selector_input)


def phase_a_checks(profile: str, data: GeneratorInput, targeted_tests: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if profile == "docs-only":
        if docs_are_indexed(data.changed_files):
            checks.append(workflow_health_command())
        return dedupe_commands(checks or [workflow_health_command()])

    if profile == "code-unit":
        checks.extend(pytest_command(test_path) for test_path in targeted_tests)
        if not targeted_tests and any(is_code_file(path) for path in data.changed_files):
            warnings.append("Code-unit scope has no deduced targeted test; Phase A includes verify.ps1.")
            checks.append(verify_command())
        if docs_are_indexed(data.changed_files):
            checks.append(workflow_health_command())
        return dedupe_commands(checks or [workflow_health_command()])

    if profile == "motor-core":
        motor_tests = dedupe(targeted_tests + list(LINKED_MOTOR_CORE_TESTS))
        checks.extend(pytest_command(test_path) for test_path in motor_tests)
        checks.append(workflow_health_command())
        checks.append(verify_command())
        return dedupe_commands(checks)

    if profile == "publish":
        checks.append(workflow_health_command())
        if any(path in {"scripts/asf_publish_step.ps1", "scripts/asf_publish_config_generator.py"} for path in data.changed_files):
            for test_path in dedupe(targeted_tests + ["tests/unit/test_asf_publish_step_runner.py"]):
                checks.append(pytest_command(test_path))
        checks.append(verify_command())
        return dedupe_commands(checks)

    return dedupe_commands([workflow_health_command(), verify_command()])


def phase_c_checks() -> list[dict[str, Any]]:
    return [
        full_pytest_command(),
        workflow_health_command(),
        verify_command(),
    ]


def build_publish_config(data: GeneratorInput, selector_packet: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    profile = compact_string(selector_packet["profile"])
    targeted_tests, test_warnings = deduce_targeted_tests(data.changed_files)
    warnings.extend(test_warnings)
    expected_profile = data.profile_selector_expected_profile or profile

    return {
        "step": data.step,
        "name": data.name,
        "repo_path": data.repo_path,
        "bridge_root": data.bridge_root,
        "branch": data.branch,
        "commit_message": data.commit_message,
        "pr_title": data.pr_title,
        "pr_body": data.pr_body,
        "next_step": data.next_step,
        "expected_files": list(data.expected_files),
        "phase_a_checks": phase_a_checks(profile, data, targeted_tests, warnings),
        "phase_c_checks": phase_c_checks(),
        "allow_no_github_checks_reported": data.allow_no_github_checks_reported,
        "log_max_count": data.log_max_count,
        "verification_profile": profile,
        "risk_level": data.risk_level,
        "changed_files": list(data.changed_files),
        "verification_phase": data.verification_phase,
        "allow_profile_check_reduction": data.allow_profile_check_reduction,
        "profile_selector_expected_profile": expected_profile,
        "intent": list(data.intent),
        "checks_already_run": list(data.checks_already_run),
        "provided_gates": list(data.provided_gates),
    }


def validate_generation(data: GeneratorInput, selector_packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    profile = compact_string(selector_packet.get("profile")).lower()
    if selector_packet.get("fail_closed"):
        errors.append(f"Selector failed closed for profile {profile or 'unknown'}.")
    if profile in BLOCKED_PROFILES:
        errors.append(f"Profile {profile} is not eligible for ordinary generated publish config.")
    if data.risk_level == "L4":
        errors.append("Risk level L4 requires separate manual review; config generation is blocked.")
    if data.allow_profile_check_reduction and profile not in {"docs-only", "code-unit"}:
        errors.append("allow_profile_check_reduction is allowed only for docs-only or code-unit profiles.")
    expected = data.profile_selector_expected_profile
    if expected and expected.lower() != profile:
        errors.append("profile_selector_expected_profile disagrees with selector recommendation.")
    return errors


def state_options_active(args: argparse.Namespace) -> bool:
    return any(
        [
            bool(args.state_file),
            bool(args.state_bridge_root),
            bool(args.state_event),
            bool(args.update_state),
            bool(args.require_state),
            bool(args.state_expected_current),
            bool(args.state_target_after),
            bool(args.write_state_bridge),
            bool(args.state_allow_recovery),
        ]
    )


def split_state_values(values: list[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for part in str(value).split(","):
            text = compact_string(part)
            if text:
                items.append(text.upper())
    return dedupe(items)


def state_file_from_generator_args(args: argparse.Namespace, state_machine: Any) -> Path | None:
    if args.state_file:
        return Path(args.state_file)
    if args.state_bridge_root:
        return Path(args.state_bridge_root) / "LAST-State.json"
    if args.write_state_bridge:
        return Path(state_machine.DEFAULT_STATE_MACHINE_BRIDGE_ROOT) / "LAST-State.json"
    return None


def target_state_for_event(args: argparse.Namespace, event: str) -> str:
    target = compact_string(args.state_target_after).upper()
    if event in {"recovery_completed", "manual_unblock"}:
        return target
    return ""


def expected_state_after(args: argparse.Namespace, event: str) -> str:
    declared = compact_string(args.state_target_after).upper()
    if declared:
        return declared
    if args.update_state:
        return "READY_TO_PUBLISH"
    return ""


def default_allowed_current_states(args: argparse.Namespace) -> set[str]:
    allowed = {"LOCAL_VERIFIED", "READY_TO_PUBLISH"}
    if args.state_allow_recovery:
        allowed.add("RECOVERY_REQUIRED")
    return allowed


def validate_loaded_state_for_generation(
    *,
    data: GeneratorInput,
    state: dict[str, Any],
    args: argparse.Namespace,
    state_machine: Any,
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    state_step = compact_string(state.get("step"))
    current_state = state_machine.normalize_state(state.get("current_state"))

    if state_step != data.step:
        if state_machine.is_combined_step(state_step) and data.step in state_machine.step_parts(state_step):
            if args.state_allow_recovery:
                warnings.append(
                    "State file step is combined and input step is one part; recovery/publication evidence must stay explicit."
                )
            else:
                errors.append("State file uses a combined step but --state-allow-recovery was not provided.")
        else:
            errors.append(f"State file step {state_step or 'UNKNOWN'} does not match generator step {data.step}.")

    if state_machine.is_combined_step(state_step or data.step) and not args.state_allow_recovery:
        errors.append("Combined/recovery step detected but --state-allow-recovery was not provided.")

    expected_current = split_state_values(args.state_expected_current)
    if expected_current and current_state not in expected_current:
        errors.append(
            "State current_state "
            f"{current_state or 'UNKNOWN'} does not match --state-expected-current {', '.join(expected_current)}."
        )

    allowed_current = default_allowed_current_states(args)
    if current_state not in allowed_current:
        errors.append(
            "State current_state "
            f"{current_state or 'UNKNOWN'} is not eligible for ready publish config generation."
        )

    if current_state == "RECOVERY_REQUIRED":
        if args.state_allow_recovery:
            warnings.append("Recovery state accepted only because --state-allow-recovery was declared.")
        else:
            errors.append("RECOVERY_REQUIRED state requires explicit --state-allow-recovery.")

    return warnings, errors


def state_bridge_args(
    *,
    args: argparse.Namespace,
    data: GeneratorInput,
    event: str,
    target_state: str,
) -> argparse.Namespace:
    return argparse.Namespace(
        step=data.step,
        event=event,
        state_file=str(args.state_file) if args.state_file else "",
        initial_state="PLANNED",
        target_state=target_state,
        config_step=data.step,
        branch=data.branch,
        expected_branch=data.branch,
        step_title=data.name,
        next_step=data.next_step,
        write_bridge=bool(args.write_state_bridge),
        bridge_root=compact_string(args.state_bridge_root),
        dry_run=False,
        json=False,
        markdown=False,
    )


def state_context_payload(context: StateIntegrationResult | None) -> dict[str, Any] | None:
    if context is None or not context.enabled:
        return None
    return {
        "enabled": context.enabled,
        "state_file": str(context.state_file) if context.state_file else None,
        "state_bridge_root": str(context.state_bridge_root) if context.state_bridge_root else None,
        "state_before": context.state_before,
        "event": context.event,
        "state_after": context.state_after,
        "allowed": context.allowed,
        "fail_closed": context.fail_closed,
        "warnings": list(context.warnings),
        "errors": list(context.errors),
        "bridge_files": [str(path) for path in context.bridge_files],
        "packet": context.packet,
    }


def state_last_path(context: StateIntegrationResult | None) -> Path | None:
    if context is None:
        return None
    for path in context.bridge_files:
        if path.name == "LAST-State.json":
            return path
    if context.state_bridge_root:
        return context.state_bridge_root / "LAST-State.json"
    return None


def apply_state_integration(
    *,
    data: GeneratorInput,
    args: argparse.Namespace,
    perform_update: bool,
) -> StateIntegrationResult:
    if not state_options_active(args):
        return StateIntegrationResult()

    warnings: list[str] = []
    errors: list[str] = []
    bridge_files: tuple[Path, ...] = ()
    packet: dict[str, Any] | None = None
    state_after = ""
    event = compact_string(args.state_event) or ("publish_config_generated" if args.update_state else "")
    try:
        state_machine = load_state_machine_module()
    except ValueError as exc:
        return StateIntegrationResult(enabled=True, event=event, errors=(str(exc),), fail_closed=True)

    state_bridge_root = Path(args.state_bridge_root or state_machine.DEFAULT_STATE_MACHINE_BRIDGE_ROOT)
    state_file = state_file_from_generator_args(args, state_machine)
    if state_file is None:
        errors.append("--state-file or --state-bridge-root is required when state integration is enabled.")
        return StateIntegrationResult(
            enabled=True,
            state_bridge_root=state_bridge_root,
            event=event,
            errors=tuple(errors),
            fail_closed=True,
        )

    if not state_file.exists():
        errors.append(f"State file required but missing: {state_file}")
        return StateIntegrationResult(
            enabled=True,
            state_file=state_file,
            state_bridge_root=state_bridge_root,
            event=event,
            errors=tuple(errors),
            fail_closed=True,
        )

    try:
        state_payload = json.loads(state_file.read_text(encoding="utf-8"))
        state = state_machine.validate_state_payload(state_payload)
    except json.JSONDecodeError as exc:
        errors.append(f"State file is not valid JSON: {state_file}: {exc.msg}")
        return StateIntegrationResult(
            enabled=True,
            state_file=state_file,
            state_bridge_root=state_bridge_root,
            event=event,
            errors=tuple(errors),
            fail_closed=True,
        )
    except (OSError, state_machine.StateFileError) as exc:
        errors.append(f"State file could not be loaded: {state_file}: {exc}")
        return StateIntegrationResult(
            enabled=True,
            state_file=state_file,
            state_bridge_root=state_bridge_root,
            event=event,
            errors=tuple(errors),
            fail_closed=True,
        )

    state_before = state_machine.normalize_state(state.get("current_state"))
    validation_warnings, validation_errors = validate_loaded_state_for_generation(
        data=data,
        state=state,
        args=args,
        state_machine=state_machine,
    )
    warnings.extend(validation_warnings)
    errors.extend(validation_errors)

    if args.update_state:
        normalized_event = state_machine.normalize_event(event or "publish_config_generated")
        target_state = target_state_for_event(args, normalized_event)
        packet, updated = state_machine.apply_event(
            state,
            event=normalized_event,
            target_state=target_state,
            config_step=data.step,
            branch=data.branch,
            expected_branch=data.branch,
            state_file=state_file,
        )
        state_after = compact_string(packet.get("next_state"))
        warnings.extend([str(item) for item in packet.get("warnings", [])])
        if packet.get("fail_closed") or updated is None:
            errors.extend([str(item) for item in packet.get("reasons", [])])
        expected_after = expected_state_after(args, normalized_event)
        if expected_after and state_after != expected_after:
            errors.append(f"State after event is {state_after}; expected {expected_after}.")
        if perform_update and not errors and updated is not None:
            try:
                state_machine.save_state(state_file, updated)
                if args.write_state_bridge:
                    bridge_args = state_bridge_args(
                        args=args,
                        data=data,
                        event=normalized_event,
                        target_state=target_state,
                    )
                    bridge_files = tuple(
                        state_machine.write_bridge_outputs(
                            packet=packet,
                            state_for_bridge=updated,
                            state_file=state_file,
                            args=bridge_args,
                        )
                    )
            except OSError as exc:
                errors.append(f"State machine write failed: {exc}")
    else:
        normalized_event = state_machine.normalize_event(event) if event else ""
        state_after = state_before
        if args.write_state_bridge:
            errors.append("--write-state-bridge requires --update-state so an event packet can be written.")

    return StateIntegrationResult(
        enabled=True,
        state_file=state_file,
        state_bridge_root=state_bridge_root,
        state_before=state_before,
        state_after=state_after,
        event=normalized_event,
        allowed=bool(packet.get("allowed")) if packet else None,
        fail_closed=bool(errors) or bool(packet.get("fail_closed")) if packet else bool(errors),
        packet=packet,
        bridge_files=bridge_files,
        warnings=tuple(dedupe(warnings)),
        errors=tuple(dedupe(errors)),
    )


def render_summary(
    *,
    data: GeneratorInput | None,
    selector_packet: dict[str, Any] | None,
    config: dict[str, Any] | None,
    warnings: list[str],
    errors: list[str],
    state_integration: StateIntegrationResult | None = None,
) -> str:
    step = data.step if data else "unknown"
    name = data.name if data else "unknown"
    profile = selector_packet.get("profile", "unknown") if selector_packet else "unknown"
    fail_closed = selector_packet.get("fail_closed", "unknown") if selector_packet else "unknown"
    phase_a = config.get("phase_a_checks", []) if config else []
    phase_c = config.get("phase_c_checks", []) if config else []

    def render_checks(items: list[dict[str, Any]]) -> str:
        if not items:
            return "- none"
        return "\n".join(f"- {item['name']}: {' '.join(item['argv'])}" for item in items)

    warning_lines = "\n".join(f"- {item}" for item in warnings) if warnings else "- none"
    error_lines = "\n".join(f"- {item}" for item in errors) if errors else "- none"
    reasons = selector_packet.get("reasons", []) if selector_packet else []
    reason_lines = "\n".join(f"- {item}" for item in reasons) if reasons else "- none"
    if state_integration and state_integration.enabled:
        state_lines = "\n".join(
            [
                f"- state_file: `{state_integration.state_file}`",
                f"- state_before: `{state_integration.state_before or 'unknown'}`",
                f"- state_event: `{state_integration.event or 'none'}`",
                f"- state_after: `{state_integration.state_after or 'unknown'}`",
                f"- state_fail_closed: `{str(state_integration.fail_closed).lower()}`",
            ]
        )
    else:
        state_lines = "- not enabled"

    return f"""# Publish Config Generator Summary

## Step

- step: `{step}`
- name: `{name}`
- status: `{"blocked" if errors else "ok"}`

## Verification profile

- profile: `{profile}`
- selector_fail_closed: `{str(fail_closed).lower()}`
- risk_level: `{data.risk_level if data else "unknown"}`
- verification_phase: `{data.verification_phase if data else "unknown"}`
- allow_profile_check_reduction: `{str(data.allow_profile_check_reduction).lower() if data else "unknown"}`

## Phase A checks

{render_checks(phase_a)}

## Phase C checks

{render_checks(phase_c)}

## Selector reasons

{reason_lines}

## State machine integration

{state_lines}

## Warnings

{warning_lines}

## Errors

{error_lines}
"""


def write_outputs(
    *,
    out_dir: Path,
    data: GeneratorInput | None,
    config: dict[str, Any] | None,
    selector_packet: dict[str, Any] | None,
    warnings: list[str],
    errors: list[str],
    state_integration: StateIntegrationResult | None = None,
) -> tuple[Path | None, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    step = data.step if data else "unknown"
    config_path = out_dir / f"{step}_publish_config.json"
    summary_path = out_dir / f"{step}_publish_config_summary.md"
    if config is not None and not errors:
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        config_path = None
    summary = render_summary(
        data=data,
        selector_packet=selector_packet,
        config=config,
        warnings=warnings,
        errors=errors,
        state_integration=state_integration,
    )
    summary_path.write_text(summary, encoding="utf-8")
    return config_path, summary_path


def safe_file_stem(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._-")
    return text or "publish_config"


def next_bridge_index(root: Path, step: str) -> int:
    if not root.exists():
        return 1
    pattern = re.compile(rf"^{re.escape(step)}-(\d\d)-")
    indexes: list[int] = []
    for path in root.iterdir():
        match = pattern.match(path.name)
        if match:
            indexes.append(int(match.group(1)))
    return (max(indexes) + 1) if indexes else 1


def timestamp_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalized_input_payload(data: GeneratorInput | None) -> dict[str, Any] | None:
    if data is None:
        return None
    payload = asdict(data)
    for key, value in list(payload.items()):
        if isinstance(value, tuple):
            payload[key] = list(value)
    return payload


def argv_to_display(argv: list[str] | tuple[str, ...]) -> str:
    parts: list[str] = []
    for item in argv:
        text = str(item)
        if not text:
            parts.append('""')
        elif any(char.isspace() for char in text) or '"' in text:
            parts.append('"' + text.replace('"', '\\"') + '"')
        else:
            parts.append(text)
    return " ".join(parts)


def powershell_quote(value: str) -> str:
    return '"' + value.replace('"', '`"') + '"'


def short_runner_command(config_path: Path | None, phase: str) -> str:
    config_text = str(config_path) if config_path else "<path-config>"
    items = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "scripts\\asf_publish_step.ps1",
        "-Config",
        powershell_quote(config_text),
        "-Phase",
        phase,
    ]
    if phase == "B":
        items.append("-ApprovePublish")
    if phase == "C":
        items.extend(["-PrNumber", "<PR_NUMBER>", "-ApproveMerge"])
    return " ".join(items)


def plan_validation_not_executed() -> PlanValidationResult:
    return PlanValidationResult(executed=False, status="not_executed")


def run_plan_validation(config_path: Path, validation_bridge_root: Path) -> PlanValidationResult:
    runner = repo_root() / "scripts" / "asf_publish_step.ps1"
    argv = (
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(runner),
        "-Config",
        str(config_path),
        "-Phase",
        "Plan",
        "-BridgeRoot",
        str(validation_bridge_root),
    )
    try:
        completed = subprocess.run(
            list(argv),
            cwd=repo_root(),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return PlanValidationResult(
            executed=True,
            status="failed",
            command=argv,
            returncode=None,
            stdout="",
            stderr=str(exc),
            bridge_root=validation_bridge_root,
        )
    status = "passed" if completed.returncode == 0 else "failed"
    return PlanValidationResult(
        executed=True,
        status=status,
        command=argv,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        bridge_root=validation_bridge_root,
    )


def plan_validation_payload(plan_validation: PlanValidationResult) -> dict[str, Any]:
    return {
        "executed": plan_validation.executed,
        "status": plan_validation.status,
        "command": list(plan_validation.command),
        "returncode": plan_validation.returncode,
        "stdout": plan_validation.stdout,
        "stderr": plan_validation.stderr,
        "bridge_root": str(plan_validation.bridge_root) if plan_validation.bridge_root else None,
    }


def render_plan_validation_text(plan_validation: PlanValidationResult) -> str:
    if not plan_validation.executed:
        return "Plan validation not executed."
    return "\n".join(
        [
            f"status: {plan_validation.status}",
            f"returncode: {plan_validation.returncode}",
            f"command: {argv_to_display(plan_validation.command)}",
            f"bridge_root: {plan_validation.bridge_root}",
            "stdout:",
            plan_validation.stdout.strip() or "none",
            "stderr:",
            plan_validation.stderr.strip() or "none",
        ]
    )


def render_bridge_request(
    *,
    data: GeneratorInput | None,
    selector_packet: dict[str, Any] | None,
    config_command: str,
    created_at: str,
) -> str:
    expected_files = list(data.expected_files) if data else []
    profile = selector_packet.get("profile", "unknown") if selector_packet else "unknown"
    return "\n".join(
        [
            "ASF Publish Config Generator - generation request",
            f"Timestamp: {created_at}",
            f"Step: {data.step if data else 'unknown'}",
            f"Name: {data.name if data else 'unknown'}",
            f"Risk level: {data.risk_level if data else 'unknown'}",
            f"Verification profile: {profile}",
            "Expected files:",
            *(f"- {item}" for item in expected_files),
            f"Next step: {data.next_step if data else 'unknown'}",
            f"Generator command: {config_command or 'not available'}",
            "Safety note: the generator prepares a publish config and audit files only.",
            "Safety note: the generator does not run Phase B, Phase C, commit, push, PR, merge, or deploy actions.",
            "",
        ]
    )


def render_bridge_compact(
    *,
    data: GeneratorInput | None,
    selector_packet: dict[str, Any] | None,
    config_path: Path | None,
    last_publish_config_path: Path | None,
    warnings: list[str],
    errors: list[str],
    plan_validation: PlanValidationResult,
    state_integration: StateIntegrationResult | None = None,
) -> str:
    profile = selector_packet.get("profile", "unknown") if selector_packet else "unknown"
    warning_lines = "\n".join(f"- {item}" for item in warnings) if warnings else "- none"
    error_lines = "\n".join(f"- {item}" for item in errors) if errors else "- none"
    state_last = state_last_path(state_integration)
    if state_integration and state_integration.enabled:
        state_lines = "\n".join(
            [
                f"- State file used: `{state_integration.state_file}`",
                f"- State before: `{state_integration.state_before or 'unknown'}`",
                f"- Event applied: `{state_integration.event or 'none'}`",
                f"- State after: `{state_integration.state_after or 'unknown'}`",
                f"- LAST-State.json: `{state_last if state_last else 'not written'}`",
                f"- LAST-Publish_Config.json: `{last_publish_config_path if last_publish_config_path else 'not generated'}`",
                f"- Next action: `{state_integration.packet.get('recommended_next_action') if state_integration.packet else 'review state manually'}`",
            ]
        )
    else:
        state_lines = "- State machine integration not enabled."
    return f"""# ASF Publish Config Generator

## Summary

- Step: `{data.step if data else "unknown"}`
- Name: `{data.name if data else "unknown"}`
- Verification profile: `{profile}`
- Risk level: `{data.risk_level if data else "unknown"}`
- Config path: `{str(config_path) if config_path else "not generated"}`
- LAST-Publish_Config.json: `{str(last_publish_config_path) if last_publish_config_path else "not generated"}`
- Next step: `{data.next_step if data else "unknown"}`
- Plan validation: `{plan_validation.status}`

## State Machine

{state_lines}

## Phase B

```powershell
{short_runner_command(config_path, "B")}
```

## Phase C

```powershell
{short_runner_command(config_path, "C")}
```

## Safety

- Phase B requires `-ApprovePublish`.
- Phase C requires `-ApproveMerge`.
- This generator does not run Phase B, Phase C, commit, push, PR, merge, or deploy actions.

## Warnings

{warning_lines}

## Errors

{error_lines}

## Bridge files

Compact output is written to Bridge files only.
"""


def render_bridge_full(
    *,
    data: GeneratorInput | None,
    selector_packet: dict[str, Any] | None,
    config: dict[str, Any] | None,
    warnings: list[str],
    errors: list[str],
    plan_validation: PlanValidationResult,
    generated_config_path: Path | None,
    generated_summary_path: Path | None,
    written_paths: dict[str, Path],
    state_integration: StateIntegrationResult | None = None,
) -> str:
    phase_a = config.get("phase_a_checks", []) if config else []
    phase_c = config.get("phase_c_checks", []) if config else []
    paths_text = "\n".join(f"- {key}: {path}" for key, path in written_paths.items()) or "- none"
    warning_lines = "\n".join(f"- {item}" for item in warnings) if warnings else "- none"
    error_lines = "\n".join(f"- {item}" for item in errors) if errors else "- none"
    return "\n".join(
        [
            "ASF Publish Config Generator - full output",
            "",
            "Generated out-dir paths:",
            f"- config: {generated_config_path if generated_config_path else 'not generated'}",
            f"- summary: {generated_summary_path if generated_summary_path else 'not generated'}",
            "",
            "Normalized input:",
            json.dumps(normalized_input_payload(data), indent=2, sort_keys=True),
            "",
            "Selected profile:",
            json.dumps(selector_packet, indent=2, sort_keys=True),
            "",
            "Generated checks:",
            json.dumps({"phase_a_checks": phase_a, "phase_c_checks": phase_c}, indent=2, sort_keys=True),
            "",
            "Generated config:",
            json.dumps(config, indent=2, sort_keys=True),
            "",
            "State machine transition result:",
            json.dumps(state_context_payload(state_integration), indent=2, sort_keys=True),
            "",
            "Warnings:",
            warning_lines,
            "",
            "Errors:",
            error_lines,
            "",
            "Phase Plan validation:",
            render_plan_validation_text(plan_validation),
            "",
            "Written Bridge paths:",
            paths_text,
            "",
        ]
    )


def write_bridge_outputs(
    *,
    bridge_root: Path,
    data: GeneratorInput | None,
    config: dict[str, Any] | None,
    selector_packet: dict[str, Any] | None,
    warnings: list[str],
    errors: list[str],
    plan_validation: PlanValidationResult,
    generated_config_path: Path | None,
    generated_summary_path: Path | None,
    generator_command: str,
    state_integration: StateIntegrationResult | None = None,
) -> dict[str, Path]:
    bridge_root.mkdir(parents=True, exist_ok=True)
    step = data.step if data else "unknown"
    name = safe_file_stem(data.name if data else "unknown")
    index = next_bridge_index(bridge_root, step)
    prefix = f"{step}-{index:02d}"

    numbered_paths = {
        "request": bridge_root / f"{prefix}-Richiesta_Generazione_{name}.txt",
        "config": bridge_root / f"{prefix}-Publish_Config_{name}.json",
        "compact": bridge_root / f"{prefix}-Output_Compatto_{name}.md",
        "full": bridge_root / f"{prefix}-Output_Completo_{name}.txt",
    }
    last_paths = {
        "last_request": bridge_root / "LAST-Richiesta_Generazione.txt",
        "last_config": bridge_root / "LAST-Publish_Config.json",
        "last_compact": bridge_root / "LAST-Output_Compatto.md",
        "last_full": bridge_root / "LAST-Output_Completo.txt",
    }
    all_paths = {**numbered_paths, **last_paths}
    created_at = timestamp_text()

    config_output_path = numbered_paths["config"] if config is not None else generated_config_path
    request_text = render_bridge_request(
        data=data,
        selector_packet=selector_packet,
        config_command=generator_command,
        created_at=created_at,
    )
    compact_text = render_bridge_compact(
        data=data,
        selector_packet=selector_packet,
        config_path=config_output_path,
        last_publish_config_path=last_paths["last_config"] if config is not None else None,
        warnings=warnings,
        errors=errors,
        plan_validation=plan_validation,
        state_integration=state_integration,
    )
    full_text = render_bridge_full(
        data=data,
        selector_packet=selector_packet,
        config=config,
        warnings=warnings,
        errors=errors,
        plan_validation=plan_validation,
        generated_config_path=generated_config_path,
        generated_summary_path=generated_summary_path,
        written_paths=all_paths,
        state_integration=state_integration,
    )

    numbered_paths["request"].write_text(request_text, encoding="utf-8")
    numbered_paths["compact"].write_text(compact_text, encoding="utf-8")
    numbered_paths["full"].write_text(full_text, encoding="utf-8")
    if config is not None:
        numbered_paths["config"].write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    shutil.copyfile(numbered_paths["request"], last_paths["last_request"])
    shutil.copyfile(numbered_paths["compact"], last_paths["last_compact"])
    shutil.copyfile(numbered_paths["full"], last_paths["last_full"])
    if config is not None:
        shutil.copyfile(numbered_paths["config"], last_paths["last_config"])
    return all_paths


def prepare_generation(
    raw: dict[str, Any],
    *,
    strict_required: bool,
    extra_warnings: tuple[str, ...] = (),
    extra_errors: tuple[str, ...] = (),
) -> PreparedGeneration:
    warnings: list[str] = list(extra_warnings)
    try:
        data = build_input(raw, strict_required=strict_required)
        selector_packet = select_profile(data)
        errors = list(extra_errors) + validate_generation(data, selector_packet)
        config = None if errors else build_publish_config(data, selector_packet, warnings)
    except ValueError as exc:
        errors = list(extra_errors) + [str(exc)]
        return PreparedGeneration(None, None, None, tuple(warnings), tuple(errors))
    return PreparedGeneration(data, selector_packet, config, tuple(warnings), tuple(errors))


def generate(
    raw: dict[str, Any],
    *,
    out_dir: Path,
    strict_required: bool,
    state_integration: StateIntegrationResult | None = None,
) -> GenerationResult:
    prepared = prepare_generation(raw, strict_required=strict_required)
    warnings = list(prepared.warnings)
    errors = list(prepared.errors)
    config_path, summary_path = write_outputs(
        out_dir=out_dir,
        data=prepared.data,
        config=prepared.config,
        selector_packet=prepared.selector_packet,
        warnings=warnings,
        errors=errors,
        state_integration=state_integration,
    )
    status = "blocked" if errors else "ok"
    return GenerationResult(
        status,
        prepared.config,
        prepared.selector_packet,
        tuple(warnings),
        tuple(errors),
        config_path,
        summary_path,
    )


def result_payload(result: GenerationResult) -> dict[str, Any]:
    return result_payload_with_context(result)


def result_payload_with_context(
    result: GenerationResult,
    *,
    status: str | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    bridge_paths: dict[str, Path] | None = None,
    plan_validation: PlanValidationResult | None = None,
    state_integration: StateIntegrationResult | None = None,
) -> dict[str, Any]:
    return {
        "status": status or result.status,
        "config_path": str(result.config_path) if result.config_path else None,
        "summary_path": str(result.summary_path) if result.summary_path else None,
        "verification_profile": result.config.get("verification_profile") if result.config else None,
        "selector": result.selector_packet,
        "warnings": warnings if warnings is not None else list(result.warnings),
        "errors": errors if errors is not None else list(result.errors),
        "bridge_paths": {key: str(path) for key, path in bridge_paths.items()} if bridge_paths else {},
        "plan_validation": plan_validation_payload(plan_validation or plan_validation_not_executed()),
        "state_machine": state_context_payload(state_integration),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a cautious ASF publish runner config from a verification profile.")
    parser.add_argument("--input-file", help="Input JSON with publish config metadata and selector fields.")
    parser.add_argument("--out-dir", default="tmp/publish_config", help="Output directory for generated config and summary.")
    parser.add_argument("--step")
    parser.add_argument("--name")
    parser.add_argument("--branch")
    parser.add_argument("--commit-message", dest="commit_message")
    parser.add_argument("--pr-title", dest="pr_title")
    parser.add_argument("--pr-body", dest="pr_body")
    parser.add_argument("--next-step", dest="next_step")
    parser.add_argument("--repo-path", dest="repo_path")
    parser.add_argument(
        "--bridge-root",
        dest="bridge_root",
        help=(
            "Bridge root for publish-config audit output when --write-bridge is used; "
            "legacy runner bridge_root override otherwise."
        ),
    )
    parser.add_argument(
        "--runner-bridge-root",
        dest="runner_bridge_root",
        help="Bridge root to embed in the generated publish runner config.",
    )
    parser.add_argument("--risk-level", dest="risk_level")
    parser.add_argument("--verification-phase", dest="verification_phase")
    parser.add_argument("--expected-files", nargs="+", dest="expected_files")
    parser.add_argument("--changed-files", nargs="+", dest="changed_files")
    parser.add_argument("--intent", action="append")
    parser.add_argument("--checks-already-run", nargs="+", dest="checks_already_run")
    parser.add_argument("--provided-gates", nargs="*", dest="provided_gates")
    parser.add_argument("--provided-gate", action="append", dest="provided_gate")
    parser.add_argument("--profile-selector-expected-profile", dest="profile_selector_expected_profile")
    parser.add_argument("--log-max-count", dest="log_max_count")
    parser.add_argument("--allow-profile-check-reduction", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--allow-no-github-checks-reported", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--write-bridge", action="store_true", help="Write generator audit outputs to the Bridge.")
    parser.add_argument("--validate-plan", action="store_true", help="Validate the generated config with runner -Phase Plan only.")
    parser.add_argument("--state-file", help="Existing state machine JSON file to read or update.")
    parser.add_argument("--state-event", help="State machine event to apply when --update-state is used.")
    parser.add_argument(
        "--state-bridge-root",
        help="Bridge root for state machine LAST-State/LAST-Event files; used for reading LAST-State when --state-file is omitted.",
    )
    parser.add_argument("--update-state", action="store_true", help="Apply the state event after a valid config is prepared.")
    parser.add_argument("--require-state", action="store_true", help="Fail closed if the state file is missing or incoherent.")
    parser.add_argument(
        "--state-expected-current",
        nargs="+",
        help="Allowed current state values expected before generation; comma-separated values are accepted.",
    )
    parser.add_argument("--state-target-after", help="Expected state after the event; default is READY_TO_PUBLISH for --update-state.")
    parser.add_argument(
        "--write-state-bridge",
        action="store_true",
        help="Write state machine Bridge outputs after a successful --update-state transition.",
    )
    parser.add_argument(
        "--state-allow-recovery",
        action="store_true",
        help="Allow explicit recovery or combined-step state contexts; otherwise recovery is fail-closed.",
    )
    parser.add_argument("--json", action="store_true", help="Print a machine-readable result to stdout.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    strict_required = bool(args.input_file)
    raw: dict[str, Any] = {}
    if args.input_file:
        try:
            raw = load_json_object(Path(args.input_file))
        except ValueError as exc:
            result = GenerationResult("blocked", None, None, (), (str(exc),), None, None)
            if args.json:
                print(json.dumps(result_payload(result), indent=2, sort_keys=True))
            else:
                print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_INPUT_ERROR
    raw = merge_cli_values(raw, args)
    out_dir = Path(args.out_dir)
    prepared = prepare_generation(raw, strict_required=strict_required)
    state_integration = StateIntegrationResult()
    if prepared.data is not None and state_options_active(args) and not prepared.errors:
        state_integration = apply_state_integration(
            data=prepared.data,
            args=args,
            perform_update=bool(args.update_state),
        )

    warnings = list(prepared.warnings) + list(state_integration.warnings)
    errors = list(prepared.errors) + list(state_integration.errors)
    config = prepared.config if not errors else None
    config_path, summary_path = write_outputs(
        out_dir=out_dir,
        data=prepared.data,
        config=config,
        selector_packet=prepared.selector_packet,
        warnings=warnings,
        errors=errors,
        state_integration=state_integration,
    )
    result = GenerationResult(
        "blocked" if errors else "ok",
        config,
        prepared.selector_packet,
        tuple(warnings),
        tuple(errors),
        config_path,
        summary_path,
    )
    plan_validation = plan_validation_not_executed()
    bridge_paths: dict[str, Path] | None = None

    bridge_root = Path(args.bridge_root or DEFAULT_PUBLISH_CONFIG_BRIDGE_ROOT)
    if args.validate_plan:
        if result.config_path is None:
            plan_validation = PlanValidationResult(
                executed=False,
                status="skipped_no_config",
                stderr="Plan validation skipped because no valid config was generated.",
            )
            errors.append("Plan validation skipped because no valid config was generated.")
        else:
            plan_bridge_root = (bridge_root if args.write_bridge else out_dir) / "plan_validation"
            plan_validation = run_plan_validation(result.config_path, plan_bridge_root)
            if plan_validation.status != "passed":
                errors.append("Phase Plan validation failed.")

    final_status = "blocked" if errors else result.status
    if args.write_bridge:
        try:
            try:
                bridge_data = build_input(raw, strict_required=strict_required)
            except ValueError:
                bridge_data = None
            bridge_paths = write_bridge_outputs(
                bridge_root=bridge_root,
                data=bridge_data,
                config=result.config,
                selector_packet=result.selector_packet,
                warnings=warnings,
                errors=errors,
                plan_validation=plan_validation,
                generated_config_path=result.config_path,
                generated_summary_path=result.summary_path,
                generator_command=argv_to_display(["python", "scripts/asf_publish_config_generator.py", *argv]),
                state_integration=state_integration,
            )
        except OSError as exc:
            warnings.append(f"Bridge output failed: {exc}")
    if args.json:
        print(
            json.dumps(
                result_payload_with_context(
                    result,
                    status=final_status,
                    warnings=warnings,
                    errors=errors,
                    bridge_paths=bridge_paths,
                    plan_validation=plan_validation,
                    state_integration=state_integration,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    elif final_status == "ok":
        print(f"Generated config: {result.config_path}")
        print(f"Generated summary: {result.summary_path}")
        if bridge_paths:
            print(f"Bridge output: {bridge_root}")
        if plan_validation.executed:
            print(f"Plan validation: {plan_validation.status}")
    else:
        print("ERROR: publish config generation blocked.", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        if result.summary_path:
            print(f"Summary: {result.summary_path}", file=sys.stderr)
        if bridge_paths:
            print(f"Bridge output: {bridge_root}", file=sys.stderr)
    return EXIT_SUCCESS if final_status == "ok" else EXIT_INPUT_ERROR


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
