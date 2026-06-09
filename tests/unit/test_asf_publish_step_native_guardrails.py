from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_publish_step.ps1"
DOC = ROOT / "docs" / "motor" / "0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(content: str, start: str, end: str) -> str:
    start_index = content.index(start)
    end_index = content.index(end, start_index)
    return content[start_index:end_index]


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def test_native_checked_wrapper_is_fail_closed() -> None:
    content = read(SCRIPT)
    wrapper = section(content, "function Invoke-NativeChecked", "function Invoke-ArgvCommand")

    for fragment in [
        "function Invoke-NativeChecked",
        "Assert-NonEmptyString -Value $Command",
        "Native command arguments are null",
        "Native command argument $index is null",
        "Native command argument $index is empty",
        "AllowedExitCodes",
        "Set-PSNativeCommandUseErrorActionPreferenceSafe -Value $false",
        "Restore-PSNativeCommandUseErrorActionPreferenceSafe -State $nativePrefState",
        "$exitCode = $LASTEXITCODE",
        "AllowedExitCodes -notcontains $exitCode",
        "Native command failed.",
    ]:
        assert fragment in wrapper

    assert "$oldPref = $PSNativeCommandUseErrorActionPreference" not in wrapper
    assert "$PSNativeCommandUseErrorActionPreference = $oldPref" not in wrapper


def test_critical_native_commands_flow_through_wrapper() -> None:
    content = read(SCRIPT)
    argv_wrapper = section(content, "function Invoke-ArgvCommand", "function Invoke-Git")
    git_wrapper = section(content, "function Invoke-Git", "function Invoke-Gh")
    gh_wrapper = section(content, "function Invoke-Gh", "function Invoke-ConfiguredChecks")
    checks_wrapper = section(content, "function Invoke-GhPrChecks", "function Invoke-PhaseC")

    assert "Invoke-NativeChecked" in argv_wrapper
    assert '("git") + $ArgList' in git_wrapper
    assert "Invoke-ArgvCommand" in git_wrapper
    assert '("gh") + $ArgList' in gh_wrapper
    assert "Invoke-ArgvCommand" in gh_wrapper
    assert 'Invoke-NativeChecked -Command "gh"' in checks_wrapper
    assert 'Invoke-ArgvCommand -Name "Verification profile selector"' in content

    assert "& git" not in content
    assert "& gh" not in content
    assert "& python" not in content
    assert "& pwsh" not in content


def test_phase_c_requires_non_empty_pr_number_before_pr_commands() -> None:
    content = read(SCRIPT)
    pr_number = section(content, "function Get-PrNumber", "function Get-NativeOutputText")
    phase_c = section(content, "function Invoke-PhaseC", "function Escape-Xml")

    assert "Phase C requires a non-empty -PrNumber or config pr_number" in pr_number
    assert "gh" not in pr_number
    assert "pr list" not in pr_number
    assert phase_c.index("$number = Get-PrNumber") < phase_c.index("phase_c_started")
    assert phase_c.index("$number = Get-PrNumber") < phase_c.index("Invoke-Gh")


def test_pass_report_is_written_only_after_phase_dispatch() -> None:
    content = read(SCRIPT)

    phase_c_index = content.index("Invoke-PhaseC -PublishConfig $publishConfig -RepoPath $repoPath")
    pass_output_index = content.index(
        'Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "PASS"'
    )
    fail_output_index = content.index(
        'Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "FAIL"'
    )

    assert phase_c_index < pass_output_index
    assert pass_output_index < fail_output_index


def test_expected_files_and_scope_guardrails_are_present() -> None:
    content = read(SCRIPT)
    doc = read(DOC)

    for fragment in [
        "function Assert-ExpectedFiles",
        "function Assert-NoOutOfScopeFiles",
        "expected_files must not be empty",
        "Out-of-scope changes detected",
        "Assert-NoOutOfScopeFiles -RepoPath $RepoPath -ExpectedFiles @($PublishConfig.expected_files)",
    ]:
        assert fragment in content

    for fragment in ["expected_files", "file fuori scope", "Assert-NoOutOfScopeFiles"]:
        assert fragment in doc


def test_gh_pr_checks_watch_warning_policy_is_preserved() -> None:
    content = read(SCRIPT)
    checks_wrapper = section(content, "function Invoke-GhPrChecks", "function Invoke-PhaseC")
    doc = read(DOC)

    for fragment in [
        "AllowAnyExitCode",
        "no checks reported",
        "allow_no_github_checks_reported",
        "Get-GhPrHeadSha",
        "Get-GhWorkflowRunsForHeadSha",
        "completed/success workflow run",
        "Add-WarningLine",
        "gh pr checks failed with exit code",
    ]:
        assert fragment in checks_wrapper

    assert "gh pr checks --watch" in doc
    assert "warning" in doc.lower()


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_c_without_pr_number_fails_before_calling_gh(tmp_path: Path) -> None:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("fake\n", encoding="utf-8")

    bridge = tmp_path / "bridge"
    config = tmp_path / "publish_config.json"
    config.write_text(
        json.dumps(
            {
                "step": "0800",
                "name": "Native_Guardrail_Test",
                "repo_path": str(repo),
                "bridge_root": str(bridge),
                "branch": "step-0800-native-guardrail-test",
                "commit_message": "0800 test",
                "pr_title": "0800 test",
                "pr_body": "0800 test",
                "next_step": "0810) Publish Runner Recovery UX and No-False-Completed Guard",
                "expected_files": ["README.md"],
                "phase_a_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
                "phase_c_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
                "allow_no_github_checks_reported": True,
                "log_max_count": 3,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    tools = tmp_path / "tools"
    tools.mkdir()
    tool_log = tmp_path / "tool_calls.log"
    for tool_name in ["gh", "git"]:
        tool = tools / tool_name
        tool.write_text(
            "#!/usr/bin/env sh\n"
            f"printf '{tool_name} %s\\n' \"$*\" >> \"$ASF_FAKE_TOOL_LOG\"\n"
            "exit 0\n",
            encoding="utf-8",
        )
        tool.chmod(0o755)
        cmd_tool = tools / f"{tool_name}.cmd"
        cmd_tool.write_text(
            "@echo off\n"
            f"echo {tool_name} %*>>\"%ASF_FAKE_TOOL_LOG%\"\n"
            "exit /b 0\n",
            encoding="utf-8",
        )

    env = os.environ.copy()
    env["PATH"] = str(tools) + os.pathsep + env.get("PATH", "")
    env["ASF_FAKE_TOOL_LOG"] = str(tool_log)

    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Config",
            str(config),
            "-Phase",
            "C",
            "-ApproveMerge",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 1
    assert "Phase C requires a non-empty -PrNumber or config pr_number" in (result.stdout + result.stderr)
    assert not tool_log.exists()
