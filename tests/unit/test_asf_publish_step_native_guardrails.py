from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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
        "Test-GitLfCrlfWarningLine",
        "Write-NonBlockingGitLfCrlfWarning",
        "Test-ArgvCommandIsStageExpectedFilesGitAdd",
        "AllowGitSwitchInformationalStderrWithZeroExit",
        "Test-GitSwitchInformationalStderrLine",
        "Write-NonBlockingGitSwitchInformationalStderr",
        "AllowGitPushInformationalStderrWithZeroExit",
        "Test-GitPushInformationalStderrLine",
        "Write-NonBlockingGitPushInformationalStderr",
        "Git command wrote unexpected stderr",
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


def write_phase_b_config(tmp_path: Path, repo: Path, bridge: Path, branch: str) -> Path:
    config = tmp_path / "publish_config.json"
    config.write_text(
        json.dumps(
            {
                "step": "0923",
                "name": "Git_Switch_Stderr_Test",
                "repo_path": str(repo),
                "bridge_root": str(bridge),
                "branch": branch,
                "commit_message": "0923 test git switch stderr",
                "pr_title": "0923 test git switch stderr",
                "pr_body": "Test-only config for safe git switch stderr handling.",
                "next_step": "0930) External Repo Push Pattern Generalization",
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
    return config


def write_phase_b_fake_tools(tmp_path: Path) -> tuple[Path, Path]:
    tools = tmp_path / "tools"
    tools.mkdir()
    log = tmp_path / "tool_calls.log"
    python_exe = sys.executable

    git_fake = tools / "git_fake.py"
    git_fake.write_text(
        """from __future__ import annotations

import os
import sys

args = sys.argv[1:]
scenario = os.environ.get("ASF_FAKE_GIT_SWITCH_SCENARIO", "safe_create")
branch = os.environ.get("ASF_FAKE_GIT_BRANCH", "step-0923-git-switch-stderr-test")
log_path = os.environ.get("ASF_FAKE_TOOL_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write("git " + " ".join(args) + "\\n")

if args == ["branch", "--show-current"]:
    print("main")
    sys.exit(0)

if len(args) >= 1 and args[0] == "status":
    print(" M README.md")
    sys.exit(0)

if args == ["--no-pager", "diff", "--name-only", "--"]:
    print("README.md")
    sys.exit(0)

if args == ["--no-pager", "diff", "--cached", "--name-only", "--"]:
    sys.exit(0)

if args == ["ls-files", "--others", "--exclude-standard", "--"]:
    sys.exit(0)

if args == ["--no-pager", "diff", "--check"]:
    sys.exit(0)

if args == ["--no-pager", "diff", "--cached", "--check"]:
    sys.exit(0)

if args == ["rev-parse", "--verify", branch]:
    sys.exit(0 if scenario == "safe_existing" else 1)

if args == ["switch", branch]:
    if scenario == "safe_existing":
        print(f"Switched to branch '{branch}'", file=sys.stderr)
        sys.exit(0)
    sys.exit(0)

if args == ["switch", "-c", branch]:
    if scenario in {"safe_create", "add_lf_crlf", "add_unexpected", "add_nonzero"}:
        print(f"Switched to a new branch '{branch}'", file=sys.stderr)
        sys.exit(0)
    if scenario == "unexpected_create":
        print("warning: credential helper failed", file=sys.stderr)
        sys.exit(0)
    if scenario == "nonzero_create":
        print(f"Switched to a new branch '{branch}'", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

if args == ["add", "--", "README.md"]:
    if scenario == "add_lf_crlf":
        print(
            "warning: in the working copy of 'scripts/asf_publish_step.ps1', "
            "LF will be replaced by CRLF the next time Git touches it",
            file=sys.stderr,
        )
        sys.exit(0)
    if scenario == "add_unexpected":
        print("warning: credential helper failed", file=sys.stderr)
        sys.exit(0)
    if scenario == "add_nonzero":
        print(
            "warning: in the working copy of 'scripts/asf_publish_step.ps1', "
            "LF will be replaced by CRLF the next time Git touches it",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)

if len(args) >= 1 and args[0] == "commit":
    sys.exit(0)

if args == ["push", "-u", "origin", branch]:
    if scenario == "push_info":
        print("remote:", file=sys.stderr)
        print(f"remote: Create a pull request for '{branch}' on GitHub by visiting:", file=sys.stderr)
        print(f"remote:      https://github.com/AlbertoFerrari71/AI_Software_Factory/pull/new/{branch}", file=sys.stderr)
        print("remote:", file=sys.stderr)
        print("To https://github.com/AlbertoFerrari71/AI_Software_Factory.git", file=sys.stderr)
        print(f" * [new branch]      {branch} -> {branch}", file=sys.stderr)
        print(f"branch '{branch}' set up to track 'origin/{branch}'.", file=sys.stderr)
        sys.exit(0)
    if scenario == "push_unexpected":
        print("fatal: credential helper failed", file=sys.stderr)
        sys.exit(0)
    if scenario == "push_nonzero":
        print(f" * [new branch]      {branch} -> {branch}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

sys.exit(0)
""",
        encoding="utf-8",
    )

    gh_fake = tools / "gh_fake.py"
    gh_fake.write_text(
        """from __future__ import annotations

import os
import sys

args = sys.argv[1:]
log_path = os.environ.get("ASF_FAKE_TOOL_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write("gh " + " ".join(args) + "\\n")

if args[:2] == ["pr", "list"]:
    print("123")
    sys.exit(0)

sys.exit(0)
""",
        encoding="utf-8",
    )

    for tool_name in ["git", "gh"]:
        fake_name = f"{tool_name}_fake.py"
        cmd_tool = tools / f"{tool_name}.cmd"
        cmd_tool.write_text(
            "\n".join(
                [
                    "@echo off",
                    f"\"{python_exe}\" \"%~dp0{fake_name}\" %*",
                    "exit /b %ERRORLEVEL%",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        sh_tool = tools / tool_name
        sh_tool.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env sh",
                    f"exec \"{python_exe}\" \"$(dirname \"$0\")/{fake_name}\" \"$@\"",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        sh_tool.chmod(0o755)

    return tools, log


def run_phase_b_with_fake_git_switch(
    tmp_path: Path, scenario: str
) -> tuple[subprocess.CompletedProcess[str], Path, Path, str]:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    bridge = tmp_path / "bridge"
    branch = "step-0923-git-switch-stderr-test"
    config = write_phase_b_config(tmp_path, repo, bridge, branch)
    tools, log = write_phase_b_fake_tools(tmp_path)

    env = os.environ.copy()
    env["PATH"] = str(tools) + os.pathsep + env.get("PATH", "")
    env["ASF_FAKE_TOOL_LOG"] = str(log)
    env["ASF_FAKE_GIT_BRANCH"] = branch
    env["ASF_FAKE_GIT_SWITCH_SCENARIO"] = scenario

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
            "B",
            "-ApprovePublish",
            "-BridgeRoot",
            str(bridge),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return result, log, bridge, branch


def phase_b_combined_output(result: subprocess.CompletedProcess[str], bridge: Path) -> str:
    parts = [result.stdout, result.stderr]
    for path in sorted(bridge.glob("*Output_Compatto*.md")):
        parts.append(read(path))
    for path in sorted(bridge.glob("*Output_Completo*.txt")):
        parts.append(read(path))
    return "\n".join(parts)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
@pytest.mark.parametrize(
    ("scenario", "expected_call", "expected_message"),
    [
        ("safe_create", "git switch -c step-0923-git-switch-stderr-test", "Switched to a new branch"),
        ("safe_existing", "git switch step-0923-git-switch-stderr-test", "Switched to branch"),
    ],
)
def test_phase_b_git_switch_safe_stderr_with_zero_exit_is_non_blocking(
    tmp_path: Path, scenario: str, expected_call: str, expected_message: str
) -> None:
    result, log, bridge, branch = run_phase_b_with_fake_git_switch(tmp_path, scenario)
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 0, combined
    assert expected_call in calls
    assert f"{expected_message} '{branch}'" in combined
    assert "stderr info treated as non-blocking" in combined
    assert "Git command wrote unexpected stderr" not in combined
    assert "git commit -m 0923 test git switch stderr" in calls
    assert "git push -u origin step-0923-git-switch-stderr-test" in calls
    assert "PHASE B completed" in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_switch_unexpected_stderr_with_zero_exit_is_blocking(tmp_path: Path) -> None:
    result, log, bridge, _ = run_phase_b_with_fake_git_switch(tmp_path, "unexpected_create")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert "Git command wrote unexpected stderr. Label=Create branch" in combined
    assert "credential helper failed" in combined
    assert "stderr info treated as non-blocking" not in combined
    assert "git commit" not in calls
    assert "git push" not in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_switch_nonzero_exit_remains_blocking(tmp_path: Path) -> None:
    result, log, bridge, _ = run_phase_b_with_fake_git_switch(tmp_path, "nonzero_create")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert "Native command failed. Label=Create branch" in combined
    assert "stderr info treated as non-blocking" not in combined
    assert "git commit" not in calls
    assert "git push" not in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_add_lf_crlf_warning_with_zero_exit_is_non_blocking(tmp_path: Path) -> None:
    result, log, bridge, _ = run_phase_b_with_fake_git_switch(tmp_path, "add_lf_crlf")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 0, combined
    assert "git add -- README.md" in calls
    assert "LF will be replaced by CRLF" in combined
    assert "Stage expected files stderr warning treated as non-blocking" in combined
    assert "Git command wrote unexpected stderr. Label=Stage expected files" not in combined
    assert "git commit -m 0923 test git switch stderr" in calls
    assert "git push -u origin step-0923-git-switch-stderr-test" in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_add_unexpected_stderr_with_zero_exit_is_blocking(tmp_path: Path) -> None:
    result, log, bridge, _ = run_phase_b_with_fake_git_switch(tmp_path, "add_unexpected")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert "Git command wrote unexpected stderr. Label=Stage expected files" in combined
    assert "credential helper failed" in combined
    assert "Stage expected files stderr warning treated as non-blocking" not in combined
    assert "git commit" not in calls
    assert "git push" not in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_add_lf_crlf_warning_with_nonzero_exit_is_blocking(tmp_path: Path) -> None:
    result, log, bridge, _ = run_phase_b_with_fake_git_switch(tmp_path, "add_nonzero")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert "Native command failed. Label=Stage expected files" in combined
    assert "Stage expected files stderr warning treated as non-blocking" not in combined
    assert "git commit" not in calls
    assert "git push" not in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_push_informational_stderr_with_zero_exit_is_non_blocking(tmp_path: Path) -> None:
    result, log, bridge, branch = run_phase_b_with_fake_git_switch(tmp_path, "push_info")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 0, combined
    assert f"git push -u origin {branch}" in calls
    assert "remote: Create a pull request" in combined
    assert f"* [new branch]      {branch} -> {branch}" in combined
    assert f"branch '{branch}' set up to track 'origin/{branch}'." in combined
    assert "Push branch stderr info treated as non-blocking" in combined
    assert "Git command wrote unexpected stderr. Label=Push branch" not in combined
    assert "gh pr list" in calls
    assert "PHASE B completed" in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_push_unexpected_stderr_with_zero_exit_is_blocking(tmp_path: Path) -> None:
    result, log, bridge, branch = run_phase_b_with_fake_git_switch(tmp_path, "push_unexpected")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert f"git push -u origin {branch}" in calls
    assert "Git command wrote unexpected stderr. Label=Push branch" in combined
    assert "credential helper failed" in combined
    assert "Push branch stderr info treated as non-blocking" not in combined
    assert "gh pr list" not in calls


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_phase_b_git_push_informational_stderr_with_nonzero_exit_is_blocking(tmp_path: Path) -> None:
    result, log, bridge, branch = run_phase_b_with_fake_git_switch(tmp_path, "push_nonzero")
    combined = phase_b_combined_output(result, bridge)
    calls = read(log)

    assert result.returncode == 1
    assert f"git push -u origin {branch}" in calls
    assert "Native command failed. Label=Push branch" in combined
    assert "Push branch stderr info treated as non-blocking" not in combined
    assert "gh pr list" not in calls
