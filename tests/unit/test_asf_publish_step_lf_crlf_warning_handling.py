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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def make_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    return repo


def write_config(tmp_path: Path, repo: Path, bridge: Path) -> Path:
    config = {
        "step": "0923",
        "name": "LF_CRLF_Warning_Test",
        "repo_path": str(repo),
        "bridge_root": str(bridge),
        "branch": "step-0923-lf-crlf-warning-test",
        "commit_message": "0923 test lf crlf warning handling",
        "pr_title": "0923 test lf crlf warning handling",
        "pr_body": "Test-only config for LF/CRLF warning handling.",
        "next_step": "0930) External Repo Push Pattern Generalization",
        "expected_files": ["README.md"],
        "phase_a_checks": [
            {"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]},
            {"name": "Diff check", "argv": ["git", "--no-pager", "diff", "--check"]},
        ],
        "phase_c_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
        "allow_no_github_checks_reported": True,
        "log_max_count": 3,
    }
    path = tmp_path / "publish_config.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def write_fake_git(tmp_path: Path) -> tuple[Path, Path]:
    tools = tmp_path / "fake_tools"
    tools.mkdir()
    log = tmp_path / "fake_git_calls.log"
    python_exe = sys.executable

    fake_py = tools / "git_fake.py"
    fake_py.write_text(
        """from __future__ import annotations

import os
import sys

args = sys.argv[1:]
scenario = os.environ.get("ASF_FAKE_GIT_WARNING_SCENARIO", "")
log_path = os.environ.get("ASF_FAKE_GIT_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write("git " + " ".join(args) + "\\n")


def warn_lf_to_crlf() -> None:
    print(
        "warning: in the working copy of 'scripts/asf_publish_step.ps1', "
        "LF will be replaced by CRLF the next time Git touches it",
        file=sys.stderr,
    )


def warn_crlf_to_lf() -> None:
    print(
        "warning: in the working copy of 'scripts/asf_next_step.py', "
        "CRLF will be replaced by LF the next time Git touches it",
        file=sys.stderr,
    )


if args == ["branch", "--show-current"]:
    print("main")
    sys.exit(0)

if len(args) >= 1 and args[0] == "status":
    print(" M README.md")
    sys.exit(0)

if args == ["--no-pager", "diff", "--name-only", "--"]:
    if scenario == "discovery_crlf_to_lf":
        warn_crlf_to_lf()
    print("README.md")
    sys.exit(0)

if args == ["--no-pager", "diff", "--cached", "--name-only", "--"]:
    sys.exit(0)

if args == ["ls-files", "--others", "--exclude-standard", "--"]:
    sys.exit(0)

if args == ["--no-pager", "diff", "--check"]:
    if scenario == "diff_lf_to_crlf":
        warn_lf_to_crlf()
        sys.exit(0)
    if scenario == "diff_crlf_to_lf":
        warn_crlf_to_lf()
        sys.exit(0)
    if scenario == "diff_warning_nonzero":
        warn_lf_to_crlf()
        sys.exit(1)
    if scenario == "diff_unexpected_stderr":
        print("warning: credential helper failed", file=sys.stderr)
        sys.exit(0)
    if scenario == "diff_whitespace_error":
        print("README.md:1: trailing whitespace.")
        sys.exit(1)
    sys.exit(0)

sys.exit(0)
""",
        encoding="utf-8",
    )

    git_cmd = tools / "git.cmd"
    git_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                f"\"{python_exe}\" \"%~dp0git_fake.py\" %*",
                "exit /b %ERRORLEVEL%",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    git_sh = tools / "git"
    git_sh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env sh",
                f"exec \"{python_exe}\" \"$(dirname \"$0\")/git_fake.py\" \"$@\"",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    git_sh.chmod(0o755)

    return tools, log


def run_phase_a(tmp_path: Path, scenario: str) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    repo = make_fake_repo(tmp_path)
    bridge = tmp_path / "bridge"
    config = write_config(tmp_path, repo, bridge)
    tools, log = write_fake_git(tmp_path)

    env = os.environ.copy()
    env["PATH"] = str(tools) + os.pathsep + env.get("PATH", "")
    env["ASF_FAKE_GIT_LOG"] = str(log)
    env["ASF_FAKE_GIT_WARNING_SCENARIO"] = scenario

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
            "A",
            "-BridgeRoot",
            str(bridge),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return result, log, bridge


def combined_output(result: subprocess.CompletedProcess[str], bridge: Path) -> str:
    parts = [result.stdout, result.stderr]
    for path in sorted(bridge.glob("*Output_Compatto*.md")):
        parts.append(read(path))
    for path in sorted(bridge.glob("*Output_Completo*.txt")):
        parts.append(read(path))
    return "\n".join(parts)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_diff_check_lf_to_crlf_warning_with_zero_exit_is_non_blocking(tmp_path: Path) -> None:
    result, log, bridge = run_phase_a(tmp_path, "diff_lf_to_crlf")
    combined = combined_output(result, bridge)

    assert result.returncode == 0, combined
    assert "LF will be replaced by CRLF" in combined
    assert "stderr warning treated as non-blocking" in combined
    assert "PHASE A completed" in combined
    assert "git --no-pager diff --check" in read(log)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_diff_check_crlf_to_lf_warning_with_zero_exit_is_non_blocking(tmp_path: Path) -> None:
    result, _, bridge = run_phase_a(tmp_path, "diff_crlf_to_lf")
    combined = combined_output(result, bridge)

    assert result.returncode == 0, combined
    assert "CRLF will be replaced by LF" in combined
    assert "stderr warning treated as non-blocking" in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_path_discovery_lf_crlf_warning_with_zero_exit_is_non_blocking(tmp_path: Path) -> None:
    result, _, bridge = run_phase_a(tmp_path, "discovery_crlf_to_lf")
    combined = combined_output(result, bridge)

    assert result.returncode == 0, combined
    assert "Git unstaged changed files stderr warning treated as non-blocking" in combined
    assert "Changed paths detected: 1" in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_diff_check_lf_crlf_warning_with_nonzero_exit_is_blocking(tmp_path: Path) -> None:
    result, _, bridge = run_phase_a(tmp_path, "diff_warning_nonzero")
    combined = combined_output(result, bridge)

    assert result.returncode == 1
    assert "Native command failed. Label=Diff check" in combined
    assert "stderr warning treated as non-blocking" not in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_diff_check_unexpected_stderr_with_zero_exit_is_blocking(tmp_path: Path) -> None:
    result, _, bridge = run_phase_a(tmp_path, "diff_unexpected_stderr")
    combined = combined_output(result, bridge)

    assert result.returncode == 1
    assert "Git command wrote unexpected stderr. Label=Diff check" in combined
    assert "credential helper failed" in combined


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_diff_check_whitespace_error_with_nonzero_exit_is_blocking(tmp_path: Path) -> None:
    result, _, bridge = run_phase_a(tmp_path, "diff_whitespace_error")
    combined = combined_output(result, bridge)

    assert result.returncode == 1
    assert "Native command failed. Label=Diff check" in combined
    assert "README.md:1: trailing whitespace." in combined
