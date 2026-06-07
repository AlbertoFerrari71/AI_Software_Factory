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
STATE_MACHINE = ROOT / "scripts" / "asf_step_state_machine.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_publish_config_generator", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_state_module():
    spec = importlib.util.spec_from_file_location("asf_step_state_machine", STATE_MACHINE)
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


def write_state_file(tmp_path: Path, *, step: str = "0650", current_state: str = "LOCAL_VERIFIED") -> Path:
    state_module = load_state_module()
    state = state_module.initial_state(step, current_state=current_state)
    path = tmp_path / "state" / f"{step.replace('-', '_')}_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return path


def command_texts(commands: list[dict[str, object]]) -> list[str]:
    return [" ".join(str(item) for item in command["argv"]) for command in commands]


def run_generator_json(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    *extra_args: object,
    input_data: dict[str, object] | None = None,
) -> tuple[object, dict[str, object]]:
    module = load_module()
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(input_data or base_input(tmp_path), indent=2), encoding="utf-8")
    code = module.run(
        [
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--json",
            *(str(item) for item in extra_args),
        ]
    )
    captured = capsys.readouterr()
    return code, json.loads(captured.out)


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


def test_state_integration_reads_valid_required_state(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, current_state="LOCAL_VERIFIED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
    )

    assert code == 0
    assert payload["status"] == "ok"
    assert payload["state_machine"]["state_before"] == "LOCAL_VERIFIED"
    assert payload["state_machine"]["state_after"] == "LOCAL_VERIFIED"
    assert Path(payload["config_path"]).exists()


def test_state_integration_required_missing_state_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing_state = tmp_path / "missing_state.json"

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        missing_state,
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["config_path"] is None
    assert "State file required but missing" in "\n".join(payload["errors"])


def test_state_integration_corrupt_state_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = tmp_path / "corrupt_state.json"
    state_file.write_text("{not valid json", encoding="utf-8")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["config_path"] is None
    assert "not valid JSON" in "\n".join(payload["errors"])


def test_state_integration_blocks_ineligible_current_state(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, current_state="IMPLEMENTED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["config_path"] is None
    assert "not eligible" in "\n".join(payload["errors"])


def test_state_integration_applies_publish_config_generated_event(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, current_state="LOCAL_VERIFIED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
        "--state-event",
        "publish_config_generated",
        "--update-state",
        "--state-target-after",
        "READY_TO_PUBLISH",
    )

    saved = read_json(state_file)
    assert code == 0
    assert payload["status"] == "ok"
    assert payload["state_machine"]["event"] == "publish_config_generated"
    assert payload["state_machine"]["state_before"] == "LOCAL_VERIFIED"
    assert payload["state_machine"]["state_after"] == "READY_TO_PUBLISH"
    assert saved["current_state"] == "READY_TO_PUBLISH"
    assert saved["last_event"] == "publish_config_generated"


def test_state_integration_step_mismatch_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, step="0670", current_state="LOCAL_VERIFIED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["config_path"] is None
    assert "does not match generator step" in "\n".join(payload["errors"])


def test_state_integration_generator_bridge_contains_state_references(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, current_state="LOCAL_VERIFIED")
    bridge_root = tmp_path / "publish_config_bridge"
    state_bridge_root = tmp_path / "state_machine_bridge"

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--require-state",
        "--state-file",
        state_file,
        "--state-event",
        "publish_config_generated",
        "--update-state",
        "--write-state-bridge",
        "--state-bridge-root",
        state_bridge_root,
    )

    assert code == 0
    compact = (bridge_root / "LAST-Output_Compatto.md").read_text(encoding="utf-8")
    assert "State Machine" in compact
    assert str(state_file) in compact
    assert "LOCAL_VERIFIED" in compact
    assert "READY_TO_PUBLISH" in compact
    assert "LAST-State.json" in compact
    assert "LAST-Publish_Config.json" in compact
    assert (state_bridge_root / "LAST-State.json").is_file()
    assert (state_bridge_root / "LAST-Event.json").is_file()
    assert payload["state_machine"]["bridge_files"]


def test_state_integration_combined_recovery_requires_explicit_flag(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, step="0650-0660", current_state="LOCAL_VERIFIED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert "combined step" in "\n".join(payload["errors"]).casefold()


def test_state_integration_combined_recovery_flag_generates_warning(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = write_state_file(tmp_path, step="0650-0660", current_state="LOCAL_VERIFIED")

    code, payload = run_generator_json(
        capsys,
        tmp_path,
        "--require-state",
        "--state-file",
        state_file,
        "--state-allow-recovery",
    )

    assert code == 0
    assert payload["status"] == "ok"
    assert "combined" in "\n".join(payload["warnings"]).casefold()


def test_state_integration_does_not_run_publish_runner_or_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_module()
    state_file = write_state_file(tmp_path, current_state="LOCAL_VERIFIED")
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(base_input(tmp_path), indent=2), encoding="utf-8")

    def fail_if_called(*_: object, **__: object) -> object:
        raise AssertionError("No subprocess should run without --validate-plan or clipboard copy.")

    monkeypatch.setattr(module.subprocess, "run", fail_if_called)
    code = module.run(
        [
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--state-file",
            str(state_file),
            "--update-state",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status"] == "ok"
    assert read_json(state_file)["current_state"] == "READY_TO_PUBLISH"


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
