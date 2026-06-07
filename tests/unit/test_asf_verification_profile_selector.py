from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_verification_profile_selector.py"
GATE_DECISION_REPORT = ROOT / "scripts" / "asf_gate_decision_report.py"
DRY_RUN_RUNNER = ROOT / "scripts" / "asf_dry_run_loop_runner.py"
RISK_CLASSIFIER = ROOT / "scripts" / "asf_risk_classifier.py"
EXAMPLES = ROOT / "examples" / "verification_profiles"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_verification_profile_selector", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def select(**kwargs: object) -> dict[str, object]:
    module = load_module()
    data = module.SelectorInput(**kwargs)
    return module.select_profile(data)


def test_docs_only_profile_is_recognized() -> None:
    packet = select(risk_level="L0", changed_files=("docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md",))

    assert packet["profile"] == "docs-only"
    assert packet["estimated_cost"] == "low"
    assert "git --no-pager diff --check" in packet["required_checks"]
    assert packet["fail_closed"] is False


def test_code_unit_profile_is_recognized_for_non_core_python_and_test() -> None:
    packet = select(
        risk_level="L2",
        changed_files=("scripts/show_workflow_status.py", "tests/unit/test_workflow_status_dashboard.py"),
    )

    assert packet["profile"] == "code-unit"
    assert any("test_workflow_status_dashboard.py" in check for check in packet["recommended_checks"])
    assert packet["fail_closed"] is False


def test_motor_core_profile_is_recognized_for_runner_gate_risk_and_workflow_files() -> None:
    for path in [
        "scripts/asf_publish_step.ps1",
        "scripts/asf_dry_run_loop_runner.py",
        "scripts/asf_risk_classifier.py",
        "scripts/asf_gate_decision_report.py",
        "scripts/check_workflow_health.py",
    ]:
        packet = select(risk_level="L2", changed_files=(path,))
        assert packet["profile"] == "motor-core", path
        assert "python -m pytest -q" in packet["required_checks"]


def test_publish_profile_is_recognized_for_l3_or_publish_intent() -> None:
    by_risk = select(risk_level="L3", changed_files=("docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",))
    by_intent = select(
        risk_level="L2",
        changed_files=("docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",),
        intent=("commit, push and open PR after review",),
    )

    assert by_risk["profile"] == "publish"
    assert by_intent["profile"] == "publish"
    assert by_risk["fail_closed"] is True


def test_final_main_profile_is_recognized_for_final_phase() -> None:
    packet = select(risk_level="L2", phase="final-main", changed_files=("docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",))

    assert packet["profile"] == "final-main"
    assert any("verify.ps1" in check for check in packet["required_checks"])


def test_high_risk_profile_is_recognized_for_l4_and_dangerous_keywords() -> None:
    for kwargs in [
        {"risk_level": "L4", "changed_files": ("README.md",)},
        {"risk_level": "L2", "intent": ("deploy to production",)},
        {"risk_level": "L2", "intent": ("delete generated data",)},
        {"risk_level": "L2", "intent": ("read secrets from .env",)},
        {"risk_level": "L2", "intent": ("run destructive cleanup",)},
    ]:
        packet = select(**kwargs)
        assert packet["profile"] == "high-risk", kwargs
        assert packet["fail_closed"] is True


def test_empty_or_ambiguous_input_fails_closed() -> None:
    empty = select()
    ambiguous = select(intent=("handle the thing",))

    assert empty["profile"] == "high-risk"
    assert empty["fail_closed"] is True
    assert ambiguous["profile"] == "high-risk"
    assert ambiguous["fail_closed"] is True


def test_json_output_is_valid_and_contains_required_fields() -> None:
    module = load_module()
    packet = select(risk_level="L2", changed_files=("scripts/asf_verification_profile_selector.py",))
    payload = json.loads(module.render_json(packet))

    for field in [
        "profile",
        "risk_level",
        "confidence",
        "recommended_checks",
        "skipped_checks",
        "required_checks",
        "optional_checks",
        "reasons",
        "warnings",
        "estimated_cost",
        "safety_notes",
        "fail_closed",
        "recommended_next_action",
    ]:
        assert field in payload


def test_markdown_output_is_readable_without_cosmetic_assertions() -> None:
    module = load_module()
    packet = select(risk_level="L2", changed_files=("scripts/asf_verification_profile_selector.py",))
    markdown = module.render_markdown(packet)

    for fragment in ["## Summary", "## Recommended checks", "## Required checks", "## Safety notes", "## Next action"]:
        assert fragment in markdown
    assert "motor-core" in markdown


def test_cli_base_json_and_markdown_work() -> None:
    result = run_cli(
        "--risk-level",
        "L2",
        "--changed-files",
        "scripts/asf_gate_decision_report.py",
        "tests/unit/test_asf_gate_decision_report.py",
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "motor-core"

    result = run_cli("--input-file", EXAMPLES / "sample_motor_core.json", "--markdown")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Verification Profile Recommendation" in result.stdout
    assert "motor-core" in result.stdout


def test_examples_cover_required_profiles() -> None:
    expected = {
        "sample_docs_only.json": "docs-only",
        "sample_code_unit.json": "code-unit",
        "sample_motor_core.json": "motor-core",
        "sample_publish.json": "publish",
        "sample_final_main.json": "final-main",
        "sample_high_risk.json": "high-risk",
        "sample_ambiguous_fail_closed.json": "high-risk",
    }

    for name, profile in expected.items():
        result = run_cli("--input-file", EXAMPLES / name, "--json")
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        assert payload["profile"] == profile
    ambiguous = json.loads(run_cli("--input-file", EXAMPLES / "sample_ambiguous_fail_closed.json", "--json").stdout)
    assert ambiguous["fail_closed"] is True


def test_gate_decision_report_0620_regression_help_still_works() -> None:
    result = subprocess.run(
        [sys.executable, str(GATE_DECISION_REPORT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "--input-file" in result.stdout


def test_dry_run_runner_0610_regression_help_still_works() -> None:
    result = subprocess.run(
        [sys.executable, str(DRY_RUN_RUNNER), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "--request-json" in result.stdout


def test_risk_classifier_0600_regression_sample_still_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RISK_CLASSIFIER),
            "--input-file",
            str(ROOT / "examples" / "risk_classifier" / "sample_l3_publish.json"),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["risk_level"] == "L3"
    assert payload["required_gate"] == "explicit_publish_approval"
