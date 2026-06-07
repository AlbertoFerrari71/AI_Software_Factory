from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_publish_config_generator.py"
RUNNER = ROOT / "scripts" / "asf_publish_step.ps1"
SELECTOR = ROOT / "scripts" / "asf_verification_profile_selector.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_publish_config_generator", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def base_input(tmp_path: Path, **updates: object) -> dict[str, object]:
    data: dict[str, object] = {
        "step": "0650",
        "name": "Verification_Profile_Driven_Publish_Config_Generator",
        "repo_path": ".",
        "bridge_root": str(tmp_path / "bridge"),
        "branch": "step-0650-verification-profile-driven-publish-config-generator",
        "commit_message": "0650 add verification profile driven publish config generator",
        "pr_title": "0650 add verification profile driven publish config generator",
        "pr_body": "Implements STEP 0650. The generator creates a reviewed config draft and does not run publication actions.",
        "next_step": "0660) Publish Config Generator Bridge Output Integration",
        "expected_files": [
            "scripts/asf_publish_config_generator.py",
            "tests/unit/test_asf_publish_config_generator.py",
        ],
        "changed_files": [
            "scripts/asf_publish_config_generator.py",
            "tests/unit/test_asf_publish_config_generator.py",
        ],
        "risk_level": "L2",
        "verification_phase": "local",
        "intent": ["generate publish config draft"],
        "provided_gates": [],
        "allow_profile_check_reduction": False,
        "checks_already_run": [],
        "allow_no_github_checks_reported": True,
        "log_max_count": 12,
    }
    data.update(updates)
    return data


def generate(tmp_path: Path, **updates: object):
    module = load_module()
    return module.generate(base_input(tmp_path, **updates), out_dir=tmp_path / "out", strict_required=True)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def command_texts(commands: list[dict[str, object]]) -> list[str]:
    return [" ".join(str(item) for item in command["argv"]) for command in commands]


def test_generates_valid_docs_only_config(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        expected_files=["docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md"],
        changed_files=["docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md"],
        risk_level="L0",
        intent=["documentation update"],
        allow_profile_check_reduction=True,
    )

    assert result.status == "ok", result.errors
    config = read_json(result.config_path)
    assert config["verification_profile"] == "docs-only"
    assert any("check_workflow_health.py" in text for text in command_texts(config["phase_a_checks"]))
    assert not any(text == "python -m pytest -q" for text in command_texts(config["phase_a_checks"]))


def test_generates_valid_code_unit_config(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        expected_files=["scripts/show_workflow_status.py", "tests/unit/test_workflow_status_dashboard.py"],
        changed_files=["scripts/show_workflow_status.py", "tests/unit/test_workflow_status_dashboard.py"],
        risk_level="L2",
        intent=["local code update"],
    )

    assert result.status == "ok", result.errors
    config = read_json(result.config_path)
    assert config["verification_profile"] == "code-unit"
    assert any("test_workflow_status_dashboard.py" in text for text in command_texts(config["phase_a_checks"]))


def test_generates_prudent_motor_core_config(tmp_path: Path) -> None:
    result = generate(tmp_path)

    assert result.status == "ok", result.errors
    config = read_json(result.config_path)
    assert config["verification_profile"] == "motor-core"
    phase_a = command_texts(config["phase_a_checks"])
    assert any("test_asf_publish_config_generator.py" in text for text in phase_a)
    assert any("test_asf_verification_profile_selector.py" in text for text in phase_a)
    assert any("test_asf_publish_step_runner.py" in text for text in phase_a)
    assert any("check_workflow_health.py" in text for text in phase_a)
    assert any("verify.ps1" in text for text in phase_a)


def test_includes_runner_profile_fields(tmp_path: Path) -> None:
    result = generate(tmp_path)
    config = read_json(result.config_path)

    for field in [
        "verification_profile",
        "risk_level",
        "changed_files",
        "verification_phase",
        "allow_profile_check_reduction",
        "profile_selector_expected_profile",
        "intent",
        "checks_already_run",
        "provided_gates",
    ]:
        assert field in config


def test_deduces_targeted_tests_from_changed_files() -> None:
    module = load_module()
    tests, warnings = module.deduce_targeted_tests(("scripts/asf_gate_decision_report.py",))

    assert tests == ["tests/unit/test_asf_gate_decision_report.py"]
    assert warnings == []


def test_missing_required_fields_blocks_without_valid_config(tmp_path: Path) -> None:
    module = load_module()
    result = module.generate({"step": "0650"}, out_dir=tmp_path / "out", strict_required=True)

    assert result.status == "blocked"
    assert result.config_path is None
    assert any("Missing required input fields" in error for error in result.errors)
    assert (tmp_path / "out" / "unknown_publish_config_summary.md").exists()


def test_high_risk_fails_closed(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        risk_level="L4",
        expected_files=["README.md"],
        changed_files=["README.md"],
        intent=["touch production configuration"],
    )

    assert result.status == "blocked"
    assert result.config_path is None
    assert any("L4" in error or "high-risk" in error for error in result.errors)


def test_selector_fail_closed_blocks_generation(tmp_path: Path) -> None:
    result = generate(tmp_path, risk_level="L9")

    assert result.status == "blocked"
    assert result.config_path is None
    assert any("Selector failed closed" in error for error in result.errors)


def test_phase_c_stays_robust(tmp_path: Path) -> None:
    result = generate(tmp_path)
    config = read_json(result.config_path)
    phase_c = command_texts(config["phase_c_checks"])

    assert any(text == "python -m pytest -q" for text in phase_c)
    assert any("check_workflow_health.py" in text for text in phase_c)
    assert any("verify.ps1" in text for text in phase_c)


def test_json_stdout_is_valid(tmp_path: Path) -> None:
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(base_input(tmp_path), indent=2), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input-file", str(input_file), "--out-dir", str(tmp_path / "out"), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["verification_profile"] == "motor-core"
    assert Path(payload["config_path"]).exists()
    assert Path(payload["summary_path"]).exists()


def test_write_bridge_creates_progressive_last_and_valid_config(tmp_path: Path) -> None:
    input_file = tmp_path / "input.json"
    bridge_root = tmp_path / "bridge"
    input_file.write_text(json.dumps(base_input(tmp_path), indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--write-bridge",
            "--bridge-root",
            str(bridge_root),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert (bridge_root / "0650-01-Richiesta_Generazione_Verification_Profile_Driven_Publish_Config_Generator.txt").exists()
    assert (bridge_root / "0650-01-Publish_Config_Verification_Profile_Driven_Publish_Config_Generator.json").exists()
    assert (bridge_root / "0650-01-Output_Compatto_Verification_Profile_Driven_Publish_Config_Generator.md").exists()
    assert (bridge_root / "0650-01-Output_Completo_Verification_Profile_Driven_Publish_Config_Generator.txt").exists()
    assert (bridge_root / "LAST-Richiesta_Generazione.txt").exists()
    assert (bridge_root / "LAST-Publish_Config.json").exists()
    assert (bridge_root / "LAST-Output_Compatto.md").exists()
    assert (bridge_root / "LAST-Output_Completo.txt").exists()
    config = read_json(bridge_root / "LAST-Publish_Config.json")
    assert config["step"] == "0650"
    assert config["verification_profile"] == "motor-core"


def test_bridge_compact_and_full_outputs_are_operational(tmp_path: Path) -> None:
    input_file = tmp_path / "input.json"
    bridge_root = tmp_path / "bridge"
    input_file.write_text(json.dumps(base_input(tmp_path), indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--write-bridge",
            "--bridge-root",
            str(bridge_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    compact = (bridge_root / "LAST-Output_Compatto.md").read_text(encoding="utf-8")
    full = (bridge_root / "LAST-Output_Completo.txt").read_text(encoding="utf-8")
    assert "-Phase B" in compact
    assert "-Phase C" in compact
    assert "-ApprovePublish" in compact
    assert "-ApproveMerge" in compact
    assert "Normalized input" in full
    assert "Generated config" in full
    assert "Plan validation not executed" in full


def test_validate_plan_invokes_only_runner_phase_plan(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []

    class Completed:
        returncode = 0
        stdout = "PLAN - config validated. No GitHub or publish action executed."
        stderr = ""

    def fake_run(argv: list[str], **_: object) -> Completed:
        calls.append(argv)
        return Completed()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    result = module.run_plan_validation(tmp_path / "config.json", tmp_path / "plan_bridge")

    assert result.status == "passed"
    assert len(calls) == 1
    assert "-Phase" in calls[0]
    assert calls[0][calls[0].index("-Phase") + 1] == "Plan"
    assert "B" not in calls[0]
    assert "C" not in calls[0]
    assert "-ApprovePublish" not in calls[0]
    assert "-ApproveMerge" not in calls[0]


def test_validate_plan_failure_makes_cli_nonzero_and_writes_bridge(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_module()
    input_file = tmp_path / "input.json"
    bridge_root = tmp_path / "bridge"
    input_file.write_text(json.dumps(base_input(tmp_path), indent=2), encoding="utf-8")

    def fake_validate(config_path: Path, validation_bridge_root: Path):
        return module.PlanValidationResult(
            executed=True,
            status="failed",
            command=("pwsh", "-Phase", "Plan", "-Config", str(config_path)),
            returncode=1,
            stdout="PLAN failed",
            stderr="invalid plan",
            bridge_root=validation_bridge_root,
        )

    monkeypatch.setattr(module, "run_plan_validation", fake_validate)
    code = module.run(
        [
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--write-bridge",
            "--bridge-root",
            str(bridge_root),
            "--validate-plan",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert code == module.EXIT_INPUT_ERROR
    assert payload["status"] == "blocked"
    assert payload["plan_validation"]["status"] == "failed"
    compact = (bridge_root / "LAST-Output_Compatto.md").read_text(encoding="utf-8")
    assert "Phase Plan validation failed" in compact
    assert "-Phase B" in compact
    assert "-Phase C" in compact


def test_markdown_summary_contains_step_profile_checks_and_warnings(tmp_path: Path) -> None:
    result = generate(tmp_path)
    summary = result.summary_path.read_text(encoding="utf-8")

    for fragment in ["0650", "motor-core", "Phase A checks", "Phase C checks", "Warnings"]:
        assert fragment in summary


def test_cli_base_with_derived_publish_metadata(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--step",
            "0650",
            "--name",
            "Verification_Profile_Driven_Publish_Config_Generator",
            "--risk-level",
            "L2",
            "--verification-phase",
            "local",
            "--expected-files",
            "scripts/asf_publish_config_generator.py",
            "tests/unit/test_asf_publish_config_generator.py",
            "--out-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    config = read_json(Path(payload["config_path"]))
    assert config["branch"] == "step-0650-verification-profile-driven-publish-config-generator"
    assert config["verification_profile"] == "motor-core"


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_generated_config_is_accepted_by_runner_plan(tmp_path: Path) -> None:
    result = generate(tmp_path)

    runner_result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUNNER),
            "-Config",
            str(result.config_path),
            "-Phase",
            "Plan",
            "-BridgeRoot",
            str(tmp_path / "runner_bridge"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert runner_result.returncode == 0, runner_result.stdout + runner_result.stderr
    assert "PLAN - config validated" in runner_result.stdout
    assert "commit" not in runner_result.stdout.casefold()


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_0640_plan_regression_still_works(tmp_path: Path) -> None:
    config = ROOT / "examples" / "publish_step" / "0640_publish_config_motor_core.example.json"
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUNNER),
            "-Config",
            str(config),
            "-Phase",
            "Plan",
            "-BridgeRoot",
            str(tmp_path / "bridge"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Verification profile validation" in result.stdout


def test_selector_0630_regression_still_recommends_motor_core() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SELECTOR),
            "--risk-level",
            "L2",
            "--changed-files",
            "scripts/asf_publish_step.ps1",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "motor-core"
