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
HEAD_SHA = "378d439b7daaf4662df882e7aded6301bed45b48"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def make_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("fake repo\n", encoding="utf-8")
    return repo


def write_config(tmp_path: Path, repo: Path, bridge: Path) -> Path:
    config = {
        "step": "0922",
        "name": "Gh_Checks_Fallback_Test",
        "repo_path": str(repo),
        "bridge_root": str(bridge),
        "branch": "step-0922-gh-checks-fallback-test",
        "commit_message": "0922 test gh checks fallback",
        "pr_title": "0922 test gh checks fallback",
        "pr_body": "Test-only config for gh checks fallback.",
        "next_step": "0930) External Repo Push Pattern Generalization",
        "expected_files": ["README.md"],
        "phase_a_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
        "phase_c_checks": [{"name": "Noop", "argv": ["pwsh", "-NoProfile", "-Command", "Write-Output noop"]}],
        "allow_no_github_checks_reported": True,
        "log_max_count": 3,
    }
    path = tmp_path / "publish_config.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def write_fake_tooling(tmp_path: Path) -> tuple[Path, Path]:
    tools = tmp_path / "fake_tools"
    tools.mkdir()
    log = tmp_path / "fake_tool_calls.log"
    python_exe = sys.executable

    git_fake_py = tools / "git_fake.py"
    git_fake_py.write_text(
        """from __future__ import annotations

import os
import sys

args = sys.argv[1:]
log_path = os.environ.get("ASF_FAKE_TOOL_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write("GH_TEST_GIT " + " ".join(args) + "\\n")
if len(args) >= 2 and args[0] == "--no-pager" and args[1] == "log":
    print("9894a5c fake log")
sys.exit(0)
""",
        encoding="utf-8",
    )
    gh_fake_py = tools / "gh_fake.py"
    gh_fake_py.write_text(
        """from __future__ import annotations

import json
import os
import sys

args = sys.argv[1:]
scenario = os.environ.get("ASF_FAKE_GH_CHECKS_SCENARIO", "")
head_sha = os.environ.get("ASF_FAKE_GH_HEAD_SHA", "")
log_path = os.environ.get("ASF_FAKE_TOOL_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write("GH " + " ".join(args) + "\\n")

if args[:2] == ["pr", "view"]:
    if len(args) >= 4 and args[3] == "--json":
        print(head_sha)
    else:
        print("PR 123")
    sys.exit(0)

if args[:2] == ["pr", "checks"]:
    if scenario == "checks_success":
        print("checks ok")
        sys.exit(0)
    if scenario == "checks_failed":
        print("one check failed")
        sys.exit(1)
    print("no checks reported on the branch")
    sys.exit(1)

if args[:2] == ["run", "list"]:
    if scenario == "no_checks_success":
        print(
            json.dumps(
                [
                    {
                        "status": "completed",
                        "conclusion": "success",
                        "name": "Unit",
                        "databaseId": 123,
                        "workflowName": "CI",
                        "headSha": head_sha,
                        "url": "https://example.test/run/123",
                    }
                ]
            )
        )
    else:
        print("[]")
    sys.exit(0)

if args[:2] == ["pr", "merge"]:
    print("merged")
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

    gh_cmd = tools / "gh.cmd"
    gh_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                f"\"{python_exe}\" \"%~dp0gh_fake.py\" %*",
                "exit /b %ERRORLEVEL%",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    git_sh = tools / "git"
    git_sh.write_text(
        """#!/usr/bin/env sh
printf 'GH_TEST_GIT %s\n' "$*" >> "$ASF_FAKE_TOOL_LOG"
if [ "$1" = "--no-pager" ] && [ "$2" = "log" ]; then echo 9894a5c fake log; exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    gh_sh = tools / "gh"
    gh_sh.write_text(
        """#!/usr/bin/env sh
printf 'GH %s\n' "$*" >> "$ASF_FAKE_TOOL_LOG"
if [ "$1" = "pr" ] && [ "$2" = "view" ]; then
    if [ "$4" = "--json" ]; then printf '%s\n' "$ASF_FAKE_GH_HEAD_SHA"; exit 0; fi
    echo PR 123
    exit 0
fi
if [ "$1" = "pr" ] && [ "$2" = "checks" ]; then
    if [ "$ASF_FAKE_GH_CHECKS_SCENARIO" = "checks_success" ]; then echo checks ok; exit 0; fi
    if [ "$ASF_FAKE_GH_CHECKS_SCENARIO" = "checks_failed" ]; then echo one check failed; exit 1; fi
    echo no checks reported on the branch
    exit 1
fi
if [ "$1" = "run" ] && [ "$2" = "list" ]; then
    if [ "$ASF_FAKE_GH_CHECKS_SCENARIO" = "no_checks_success" ]; then
        printf '[{"status":"completed","conclusion":"success","name":"Unit","databaseId":123,"workflowName":"CI","headSha":"%s","url":"https://example.test/run/123"}]\n' "$ASF_FAKE_GH_HEAD_SHA"
        exit 0
    fi
    printf '[]\n'
    exit 0
fi
if [ "$1" = "pr" ] && [ "$2" = "merge" ]; then echo merged; exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    git_sh.chmod(0o755)
    gh_sh.chmod(0o755)

    return tools, log


def run_phase_c(tmp_path: Path, scenario: str) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    repo = make_fake_repo(tmp_path)
    bridge = tmp_path / "bridge"
    config = write_config(tmp_path, repo, bridge)
    tools, log = write_fake_tooling(tmp_path)
    env = os.environ.copy()
    env.update(
        {
            "PATH": str(tools) + os.pathsep + env.get("PATH", ""),
            "ASF_FAKE_TOOL_LOG": str(log),
            "ASF_FAKE_GH_CHECKS_SCENARIO": scenario,
            "ASF_FAKE_GH_HEAD_SHA": HEAD_SHA,
        }
    )
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
            "-PrNumber",
            "123",
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


def output_text(result: subprocess.CompletedProcess[str], bridge: Path) -> str:
    compact = bridge / "0922-Output_Compatto_Gh_Checks_Fallback_Test.md"
    compact_text = read(compact) if compact.exists() else ""
    return result.stdout + result.stderr + compact_text


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_pr_checks_success_passes_without_workflow_run_fallback(tmp_path: Path) -> None:
    result, log, bridge = run_phase_c(tmp_path, "checks_success")

    assert result.returncode == 0, output_text(result, bridge)
    tool_log = read(log)
    assert "GH pr checks 123 --watch" in tool_log
    assert "GH run list" not in tool_log
    assert "GH pr merge 123 --squash" in tool_log


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_no_checks_reported_with_successful_workflow_run_passes_with_warning(tmp_path: Path) -> None:
    result, log, bridge = run_phase_c(tmp_path, "no_checks_success")

    combined = output_text(result, bridge)
    assert result.returncode == 0, combined
    assert "gh pr checks returned no checks reported; attempting GitHub workflow-run fallback" in combined
    assert "completed/success workflow run(s)" in combined
    tool_log = read(log)
    assert f"GH run list --commit {HEAD_SHA}" in tool_log
    assert "GH pr merge 123 --squash" in tool_log


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_no_checks_reported_without_successful_workflow_run_fails(tmp_path: Path) -> None:
    result, log, bridge = run_phase_c(tmp_path, "no_checks_empty")

    combined = output_text(result, bridge)
    assert result.returncode == 1
    assert "no completed/success GitHub workflow run was found" in combined
    tool_log = read(log)
    assert f"GH run list --commit {HEAD_SHA}" in tool_log
    assert "GH pr merge" not in tool_log


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_failed_pr_checks_remain_blocking_and_do_not_use_fallback(tmp_path: Path) -> None:
    result, log, bridge = run_phase_c(tmp_path, "checks_failed")

    combined = output_text(result, bridge)
    assert result.returncode == 1
    assert "gh pr checks failed with exit code 1" in combined
    tool_log = read(log)
    assert "GH run list" not in tool_log
    assert "GH pr merge" not in tool_log
