from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_publish_step.ps1"
CONFIG = ROOT / "examples" / "publish_step" / "0590_publish_config.example.json"
DOC = ROOT / "docs" / "motor" / "0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md"


REQUIRED_CONFIG_FIELDS = [
    "step",
    "name",
    "repo_path",
    "bridge_root",
    "branch",
    "commit_message",
    "pr_title",
    "pr_body",
    "next_step",
    "expected_files",
    "phase_a_checks",
    "phase_c_checks",
    "allow_no_github_checks_reported",
    "log_max_count",
]


FORBIDDEN_SCRIPT_PATTERNS = [
    "Invoke-Expression",
    "Set-Clipboard -Path",
    "git reset --hard",
    "git clean",
    "Remove-Item -Recurse",
    "rm -rf",
    "danger-full-access",
    "setx PATH",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_config() -> dict[str, object]:
    return json.loads(read(CONFIG))


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def run_pwsh(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_config(tmp_path: Path, **updates: object) -> Path:
    config = load_config()
    config["step"] = "0640"
    config["name"] = updates.pop("name", "Verification_Profile_Integration_Test")
    config["branch"] = "step-0640-verification-profile-integration-test"
    config["next_step"] = "0650) Verification Profile Driven Publish Config Generator"
    config.update(updates)
    path = tmp_path / "publish_config.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def assert_docx_valid(path: Path) -> None:
    assert path.exists(), path
    assert zipfile.is_zipfile(path)
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        assert "[Content_Types].xml" in names
        assert "word/document.xml" in names


def test_publish_step_runner_files_exist() -> None:
    assert SCRIPT.exists()
    assert CONFIG.exists()
    assert DOC.exists()


def test_publish_config_contains_required_fields() -> None:
    config = load_config()

    for field in REQUIRED_CONFIG_FIELDS:
        assert field in config
    assert config["step"] == "0590"
    assert config["name"] == "Stable_PowerShell_Publish_Runner"
    assert config["branch"] == "step-0590-stable-powershell-publish-runner"
    assert config["next_step"] == "0600) Risk Classifier + Gate Policy"


def test_publish_config_expected_files_are_non_empty_and_cover_core_outputs() -> None:
    expected_files = load_config()["expected_files"]

    assert isinstance(expected_files, list)
    assert expected_files
    for required_path in [
        "scripts/asf_publish_step.ps1",
        "examples/publish_step/0590_publish_config.example.json",
        "tests/unit/test_asf_publish_step_runner.py",
        "docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md",
    ]:
        assert required_path in expected_files


def test_publish_config_commands_use_argv_arrays() -> None:
    config = load_config()

    for section in ["phase_a_checks", "phase_c_checks"]:
        commands = config[section]
        assert isinstance(commands, list)
        assert commands
        for command in commands:
            assert isinstance(command["name"], str)
            assert isinstance(command["argv"], list)
            assert command["argv"]
            assert all(isinstance(item, str) and item for item in command["argv"])
            assert command.get("shell") in (None, False)


def test_publish_runner_static_safety_contract() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_SCRIPT_PATTERNS:
        assert pattern not in content
    assert "Get-Content -Path $File -Raw | Set-Clipboard" in content
    assert "PSNativeCommandUseErrorActionPreference" in content
    assert "no checks reported" in content
    assert "allow_no_github_checks_reported" in content
    assert "Write-MinimalDocx" in content
    assert "System.IO.Compression.ZipArchive" in content


def test_publish_runner_documents_short_commands_and_phases() -> None:
    doc = read(DOC)

    for fragment in [
        "FASE A",
        "FASE B",
        "FASE C",
        "ApprovePublish",
        "ApproveMerge",
        "no checks reported",
        "Bridge",
        "0600) Risk Classifier + Gate Policy",
    ]:
        assert fragment in doc


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_selftest_generates_valid_bridge_docx(tmp_path: Path) -> None:
    bridge_root = tmp_path / "Bridge Root With Spaces"

    result = run_pwsh("-SelfTest", "-BridgeRoot", bridge_root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (bridge_root / "0000-Richiesta_Generazione_SelfTest.txt").exists()
    assert (bridge_root / "0000-Comando_Eseguito_SelfTest.ps1").exists()
    assert (bridge_root / "0000-Output_Completo_SelfTest.txt").exists()
    assert (bridge_root / "0000-Output_Compatto_SelfTest.md").exists()
    assert_docx_valid(bridge_root / "0000-Output_Compatto_SelfTest.docx")
    assert (bridge_root / "LAST-Richiesta_Generazione.txt").exists()
    assert (bridge_root / "LAST-Comando_Eseguito.ps1").exists()
    assert (bridge_root / "LAST-Output_Completo.txt").exists()
    assert (bridge_root / "LAST-Output_Compatto.md").exists()
    assert_docx_valid(bridge_root / "LAST-Output_Compatto.docx")


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_plan_phase_generates_short_command_without_github(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_pwsh("-Config", CONFIG, "-Phase", "Plan", "-BridgeRoot", bridge_root)

    assert result.returncode == 0, result.stdout + result.stderr
    command_file = bridge_root / "0590-Comando_Eseguito_Stable_PowerShell_Publish_Runner.ps1"
    compact = bridge_root / "0590-Output_Compatto_Stable_PowerShell_Publish_Runner.md"
    assert command_file.exists()
    assert compact.exists()
    command_text = read(command_file)
    assert "scripts\\asf_publish_step.ps1" in command_text
    assert "-Phase Plan" in command_text
    assert "gh pr" not in command_text
    assert "Verification profile validation: not configured" in read(compact)
    assert_docx_valid(bridge_root / "0590-Output_Compatto_Stable_PowerShell_Publish_Runner.docx")


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_profile_consistent_passes_plan_and_reports_bridge(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    config = write_config(
        tmp_path,
        verification_profile="motor-core",
        risk_level="L2",
        changed_files=["scripts/asf_publish_step.ps1", "tests/unit/test_asf_publish_step_runner.py"],
        verification_phase="local",
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", bridge_root)

    assert result.returncode == 0, result.stdout + result.stderr
    compact = bridge_root / "0640-Output_Compatto_Verification_Profile_Integration_Test.md"
    text = read(compact)
    assert "Verification profile validation: pass" in text
    assert "Declared verification profile: motor-core" in text
    assert "Recommended verification profile: motor-core" in text
    assert "Profile check reduction allowed: False" in text


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_profile_mismatch_fails_closed(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="docs-only",
        risk_level="L2",
        changed_files=["scripts/asf_publish_step.ps1"],
        verification_phase="local",
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "lighter than selector recommendation" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_l4_cannot_use_light_profile(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="docs-only",
        risk_level="L4",
        changed_files=["docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md"],
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "Risk level L4 requires verification_profile high-risk" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_selector_fail_closed_blocks(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="high-risk",
        risk_level="L9",
        changed_files=["README.md"],
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "selector failed closed" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_unknown_profile_blocks(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="tiny",
        risk_level="L1",
        changed_files=["README.md"],
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "Unknown verification profile" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_reduction_not_authorized_for_motor_core(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="motor-core",
        risk_level="L2",
        changed_files=["scripts/asf_publish_step.ps1"],
        allow_profile_check_reduction=True,
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "allow_profile_check_reduction is allowed only" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_authorized_reduction_keeps_phase_c_disabled(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    config = write_config(
        tmp_path,
        verification_profile="docs-only",
        risk_level="L0",
        changed_files=["docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md"],
        allow_profile_check_reduction=True,
    )

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", bridge_root)

    assert result.returncode == 0, result.stdout + result.stderr
    text = read(bridge_root / "0640-Output_Compatto_Verification_Profile_Integration_Test.md")
    assert "Profile check reduction allowed: True" in text
    assert "Phase C reduction: disabled" in text
    assert "Recommended verification profile: docs-only" in text


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_phase_b_still_requires_approve_publish(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="docs-only",
        risk_level="L0",
        changed_files=["docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md"],
    )

    result = run_pwsh("-Config", config, "-Phase", "B", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "Phase B requires -ApprovePublish" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_phase_c_still_requires_approve_merge(tmp_path: Path) -> None:
    config = write_config(
        tmp_path,
        verification_profile="docs-only",
        risk_level="L0",
        changed_files=["docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md"],
    )

    result = run_pwsh("-Config", config, "-Phase", "C", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "Phase C requires -ApproveMerge" in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_shell_execution_still_rejected(tmp_path: Path) -> None:
    config_data = load_config()
    config_data["phase_a_checks"][0]["shell"] = True
    config = tmp_path / "publish_config_shell.json"
    config.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "requests shell execution" in (result.stdout + result.stderr)
