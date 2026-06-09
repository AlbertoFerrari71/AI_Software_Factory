from __future__ import annotations

import json
import os
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
    "Set-" + "Cl" + "ipboard",
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


def run_pwsh(*args: str | Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=run_env,
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


def write_state_file(tmp_path: Path, *, step: str = "0750", current_state: str = "READY_TO_PUBLISH") -> Path:
    path = tmp_path / f"{step}_state.json"
    path.write_text(
        json.dumps(
            {
                "schema": "asf_step_state_machine.v1",
                "step": step,
                "current_state": current_state,
                "history": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def read_state_events(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [entry["event"] for entry in payload["history"]]


def make_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("fake repo\n", encoding="utf-8")
    return repo


def write_fake_tooling(tmp_path: Path) -> tuple[Path, Path]:
    tools = tmp_path / "fake_tools"
    tools.mkdir()
    log = tmp_path / "fake_tool_calls.log"

    git_cmd = tools / "git.cmd"
    git_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "echo GIT %*>>\"%ASF_FAKE_TOOL_LOG%\"",
                "if \"%1\"==\"branch\" if \"%2\"==\"--show-current\" (echo main& exit /b 0)",
                "if \"%1\"==\"status\" (exit /b 0)",
                "if \"%1\"==\"rev-parse\" (exit /b 1)",
                "if \"%ASF_FAKE_GIT_FAIL%\"==\"commit\" if \"%1\"==\"commit\" (exit /b 7)",
                "if \"%1\"==\"--no-pager\" if \"%2\"==\"log\" (echo 9894a5c fake log& exit /b 0)",
                "exit /b 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    gh_cmd = tools / "gh.cmd"
    gh_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "echo GH %*>>\"%ASF_FAKE_TOOL_LOG%\"",
                "if \"%ASF_FAKE_GH_FAIL%\"==\"merge\" if \"%1\"==\"pr\" if \"%2\"==\"merge\" (exit /b 9)",
                "if \"%1\"==\"pr\" if \"%2\"==\"list\" (echo 123& exit /b 0)",
                "if \"%1\"==\"pr\" if \"%2\"==\"create\" (echo https://github.com/example/repo/pull/123& exit /b 0)",
                "if \"%1\"==\"pr\" if \"%2\"==\"checks\" (echo checks ok& exit /b 0)",
                "if \"%1\"==\"pr\" if \"%2\"==\"view\" (echo PR 123& exit /b 0)",
                "if \"%1\"==\"pr\" if \"%2\"==\"merge\" (echo merged& exit /b 0)",
                "exit /b 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    git_sh = tools / "git"
    git_sh.write_text(
        """#!/usr/bin/env sh
printf 'GIT %s\n' "$*" >> "$ASF_FAKE_TOOL_LOG"
if [ "$1" = "branch" ] && [ "$2" = "--show-current" ]; then echo main; exit 0; fi
if [ "$1" = "status" ]; then exit 0; fi
if [ "$1" = "rev-parse" ]; then exit 1; fi
if [ "$ASF_FAKE_GIT_FAIL" = "commit" ] && [ "$1" = "commit" ]; then exit 7; fi
if [ "$1" = "--no-pager" ] && [ "$2" = "log" ]; then echo 9894a5c fake log; exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    gh_sh = tools / "gh"
    gh_sh.write_text(
        """#!/usr/bin/env sh
printf 'GH %s\n' "$*" >> "$ASF_FAKE_TOOL_LOG"
if [ "$ASF_FAKE_GH_FAIL" = "merge" ] && [ "$1" = "pr" ] && [ "$2" = "merge" ]; then exit 9; fi
if [ "$1" = "pr" ] && [ "$2" = "list" ]; then echo 123; exit 0; fi
if [ "$1" = "pr" ] && [ "$2" = "create" ]; then echo https://github.com/example/repo/pull/123; exit 0; fi
if [ "$1" = "pr" ] && [ "$2" = "checks" ]; then echo checks ok; exit 0; fi
if [ "$1" = "pr" ] && [ "$2" = "view" ]; then echo PR 123; exit 0; fi
if [ "$1" = "pr" ] && [ "$2" = "merge" ]; then echo merged; exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    git_sh.chmod(0o755)
    gh_sh.chmod(0o755)
    return tools, log


def fake_tool_env(tools: Path, log: Path, **updates: str) -> dict[str, str]:
    env = {
        "PATH": str(tools) + os.pathsep + os.environ.get("PATH", ""),
        "ASF_FAKE_TOOL_LOG": str(log),
    }
    env.update(updates)
    return env


def write_state_hook_config(
    tmp_path: Path,
    *,
    repo_path: Path,
    state_file: Path,
    state_bridge_root: Path | None = None,
    **updates: object,
) -> Path:
    config = load_config()
    config.update(
        {
            "step": "0750",
            "name": "State_Machine_Publish_Runner_Event_Hooks_Test",
            "repo_path": str(repo_path),
            "bridge_root": str(tmp_path / "runner_bridge"),
            "branch": "step-0750-state-machine-publish-runner-event-hooks-test",
            "commit_message": "0750 test state hooks",
            "pr_title": "0750 test state hooks",
            "pr_body": "Test-only config for local fake publish runner hooks.",
            "next_step": "0760) MVP Real Step Pilot 2 with State Hooks",
            "expected_files": ["README.md"],
            "phase_a_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
            "phase_c_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
            "allow_no_github_checks_reported": True,
            "log_max_count": 3,
            "state_machine_enabled": True,
            "state_file": str(state_file),
            "state_step": "0750",
            "state_fail_on_hook_error": True,
            "state_expected_before_phase_b": "READY_TO_PUBLISH",
            "state_expected_before_phase_c": "PR_CREATED",
            "state_emit_main_verified": True,
            "state_close_on_phase_c_success": False,
        }
    )
    if state_bridge_root is not None:
        config["state_write_bridge"] = True
        config["state_bridge_root"] = str(state_bridge_root)
    else:
        config["state_write_bridge"] = False
    for profile_field in [
        "verification_profile",
        "profile_selector_expected_profile",
        "risk_level",
        "changed_files",
        "verification_phase",
        "allow_profile_check_reduction",
        "profile_selector_input",
    ]:
        config.pop(profile_field, None)
    config.update(updates)
    path = tmp_path / "publish_config_state_hooks.json"
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
    assert "Copy-FileTo" + "Cl" + "ipboard" not in content
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
def test_publish_runner_state_hooks_phase_b_success_records_started_passed_and_pr_created(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_file = write_state_file(tmp_path, current_state="READY_TO_PUBLISH")
    config = write_state_hook_config(tmp_path, repo_path=repo, state_file=state_file)

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "B",
        "-ApprovePublish",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    events = read_state_events(state_file)
    assert events == ["phase_b_started", "phase_b_passed", "pr_created"]
    compact = read(tmp_path / "runner_bridge" / "0750-Output_Compatto_State_Machine_Publish_Runner_Event_Hooks_Test.md")
    assert "State machine enabled: True" in compact
    assert "Last state event emitted: pr_created" in compact
    assert "Final state: PR_CREATED" in compact
    assert "GIT commit" in read(log)
    assert "GH pr list" in read(log)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_state_hooks_phase_b_failure_records_failed(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_file = write_state_file(tmp_path, current_state="READY_TO_PUBLISH")
    config = write_state_hook_config(tmp_path, repo_path=repo, state_file=state_file)

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "B",
        "-ApprovePublish",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log, ASF_FAKE_GIT_FAIL="commit"),
    )

    assert result.returncode == 1
    events = read_state_events(state_file)
    assert events == ["phase_b_started", "phase_b_failed"]
    assert json.loads(state_file.read_text(encoding="utf-8"))["current_state"] == "RECOVERY_REQUIRED"
    assert "phase_b_passed" not in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_state_hooks_phase_c_success_records_started_passed_main_verified_and_bridge(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_bridge_root = tmp_path / "state_bridge"
    state_file = write_state_file(tmp_path, current_state="PR_CREATED")
    config = write_state_hook_config(
        tmp_path,
        repo_path=repo,
        state_file=state_file,
        state_bridge_root=state_bridge_root,
    )

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "C",
        "-ApproveMerge",
        "-PrNumber",
        "123",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    events = read_state_events(state_file)
    assert events == ["phase_c_started", "phase_c_passed", "main_verified"]
    assert json.loads(state_file.read_text(encoding="utf-8"))["current_state"] == "CLOSED"
    assert (state_bridge_root / "LAST-State.json").exists()
    assert (state_bridge_root / "LAST-Event.json").exists()
    compact = read(tmp_path / "runner_bridge" / "0750-Output_Compatto_State_Machine_Publish_Runner_Event_Hooks_Test.md")
    assert f"State bridge root: {state_bridge_root}" in compact
    assert "Last state event emitted: main_verified" in compact
    assert "Final state: CLOSED" in compact
    assert "GH pr merge" in read(log)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_state_hooks_phase_c_close_step_is_explicit(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_file = write_state_file(tmp_path, current_state="PR_CREATED")
    config = write_state_hook_config(
        tmp_path,
        repo_path=repo,
        state_file=state_file,
        state_close_on_phase_c_success=True,
    )

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "C",
        "-ApproveMerge",
        "-PrNumber",
        "123",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert read_state_events(state_file) == ["phase_c_started", "phase_c_passed", "main_verified", "close_step"]
    compact = read(tmp_path / "runner_bridge" / "0750-Output_Compatto_State_Machine_Publish_Runner_Event_Hooks_Test.md")
    assert "Close step emitted: True" in compact


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_state_hooks_phase_c_failure_records_failed(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_file = write_state_file(tmp_path, current_state="PR_CREATED")
    config = write_state_hook_config(tmp_path, repo_path=repo, state_file=state_file)

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "C",
        "-ApproveMerge",
        "-PrNumber",
        "123",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log, ASF_FAKE_GH_FAIL="merge"),
    )

    assert result.returncode == 1
    assert read_state_events(state_file) == ["phase_c_started", "phase_c_failed"]
    assert json.loads(state_file.read_text(encoding="utf-8"))["current_state"] == "RECOVERY_REQUIRED"
    assert "PHASE C completed" not in (result.stdout + result.stderr)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_state_hooks_mismatch_fails_closed_before_phase_b_operations(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    tools, log = write_fake_tooling(tmp_path)
    state_file = write_state_file(tmp_path, current_state="LOCAL_VERIFIED")
    config = write_state_hook_config(tmp_path, repo_path=repo, state_file=state_file)

    result = run_pwsh(
        "-Config",
        config,
        "-Phase",
        "B",
        "-ApprovePublish",
        "-BridgeRoot",
        tmp_path / "runner_bridge",
        env=fake_tool_env(tools, log),
    )

    assert result.returncode == 1
    assert "State hook expected READY_TO_PUBLISH before Phase B but found LOCAL_VERIFIED" in (
        result.stdout + result.stderr
    )
    assert read_state_events(state_file) == []
    assert not log.exists() or "commit" not in read(log)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_shell_execution_still_rejected(tmp_path: Path) -> None:
    config_data = load_config()
    config_data["phase_a_checks"][0]["shell"] = True
    config = tmp_path / "publish_config_shell.json"
    config.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    result = run_pwsh("-Config", config, "-Phase", "Plan", "-BridgeRoot", tmp_path / "bridge")

    assert result.returncode == 1
    assert "requests shell execution" in (result.stdout + result.stderr)
