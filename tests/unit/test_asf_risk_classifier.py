from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_risk_classifier.py"
DOC = ROOT / "docs" / "motor" / "0600_RISK_CLASSIFIER_GATE_POLICY.md"
EXAMPLES = ROOT / "examples" / "risk_classifier"
DRY_RUN_RUNNER = ROOT / "scripts" / "asf_dry_run_loop_runner.py"
PYPROJECT = ROOT / "pyproject.toml"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_risk_classifier", SCRIPT)
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


def classify_text(text: str, *gates: str) -> dict[str, object]:
    module = load_module()
    return module.classify(module.ClassifierInput(text_items=(text,)), provided_gates=set(gates))


def test_docs_only_and_readonly_are_low_risk() -> None:
    result = classify_text("modify docs only and inspect README.md")

    assert result["risk_level"] == "L0"
    assert result["allowed"] is True
    assert result["required_gate"] == "none"
    assert result["fail_closed"] is False


def test_source_and_test_changes_are_at_least_l2() -> None:
    module = load_module()
    result = module.classify(
        module.ClassifierInput(
            text_items=("Implement local classifier code and tests",),
            file_items=("scripts/asf_risk_classifier.py", "tests/unit/test_asf_risk_classifier.py"),
        )
    )

    assert result["risk_level"] == "L2"
    assert result["allowed"] is False
    assert result["required_gate"] == "local_verification"


def test_l2_allows_after_local_verification_gate() -> None:
    result = classify_text("implement a script and unit tests", "local_verification")

    assert result["risk_level"] == "L2"
    assert result["allowed"] is True
    assert result["required_gate"] == "local_verification"


def test_repository_publication_is_l3_and_requires_publish_approval() -> None:
    result = classify_text("commit changes, push branch and open PR")

    assert result["risk_level"] == "L3"
    assert result["allowed"] is False
    assert result["required_gate"] == "explicit_publish_approval"
    assert any(match["risk_level"] == "L3" for match in result["matched_rules"])


def test_repository_publication_allows_only_with_publish_gate() -> None:
    result = classify_text("commit changes and open pull request", "approve_publish")

    assert result["risk_level"] == "L3"
    assert result["allowed"] is True


def test_l4_signals_are_highest_risk() -> None:
    for text in [
        "merge the PR automatically",
        "deploy to production",
        "delete generated data",
        "read secret token from .env",
        "perform a live provider network call",
    ]:
        result = classify_text(text)
        assert result["risk_level"] == "L4", text
        assert result["allowed"] is False
        assert result["required_gate"] == "elevated_manual_approval"


def test_empty_or_ambiguous_input_fails_closed() -> None:
    empty = classify_text("")
    ambiguous = classify_text("handle the thing")

    assert empty["risk_level"] == "L4"
    assert empty["fail_closed"] is True
    assert empty["allowed"] is False
    assert ambiguous["risk_level"] == "L4"
    assert ambiguous["fail_closed"] is True
    assert ambiguous["allowed"] is False


def test_cli_json_output_is_valid() -> None:
    result = run_cli("--text", "commit and push branch", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["risk_level"] == "L3"
    assert payload["required_gate"] == "explicit_publish_approval"
    assert isinstance(payload["matched_rules"], list)


def test_cli_input_file_json_is_supported() -> None:
    result = run_cli("--input-file", EXAMPLES / "sample_l4_deploy_or_destructive.json", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["risk_level"] == "L4"
    assert payload["allowed"] is False


def test_examples_cover_l0_l2_l3_l4() -> None:
    expected = {
        "sample_l0_docs_only.json": "L0",
        "sample_l2_code_change.json": "L2",
        "sample_l3_publish.json": "L3",
        "sample_l4_deploy_or_destructive.json": "L4",
    }

    for name, risk_level in expected.items():
        result = run_cli("--input-file", EXAMPLES / name, "--json")
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        assert payload["risk_level"] == risk_level


def test_files_docs_and_examples_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert DRY_RUN_RUNNER.exists()
    for name in [
        "sample_l0_docs_only.json",
        "sample_l2_code_change.json",
        "sample_l3_publish.json",
        "sample_l4_deploy_or_destructive.json",
    ]:
        assert (EXAMPLES / name).exists()


def test_dry_run_runner_uses_classifier_without_copying_rules() -> None:
    content = DRY_RUN_RUNNER.read_text(encoding="utf-8")

    assert "from asf_risk_classifier import ClassifierInput, classify" in content
    assert "def classify_risk" not in content
    assert "RiskRule(" not in content
    assert "l4_destructive_action" not in content


def test_no_runtime_dependency_was_added() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    assert "dependencies = []" in pyproject
    assert "requests" not in SCRIPT.read_text(encoding="utf-8")
