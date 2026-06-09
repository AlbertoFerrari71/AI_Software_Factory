from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_publish_step.ps1"
DOC = ROOT / "docs" / "motor" / "0810_PUBLISH_RUNNER_SCOPE_DISCOVERY_RECOVERY_UX_AND_NO_FALSE_COMPLETED_GUARD.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(content: str, start: str, end: str) -> str:
    start_index = content.index(start)
    end_index = content.index(end, start_index)
    return content[start_index:end_index]


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def git_available() -> bool:
    return shutil.which("git") is not None


def make_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, text=True, capture_output=True, check=True)
    return repo


def write_untracked(repo: Path, relative_path: str, text: str = "changed\n") -> None:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_pwsh_from_repo(repo: Path, *args: str | Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *(str(arg) for arg in args)],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_scope_discovery_uses_stdout_only_name_only_commands() -> None:
    content = read(SCRIPT)
    discovery = section(content, "function Get-RepositoryChangedFiles", "function Get-GitStatusPaths")
    stdout_wrapper = section(content, "function Invoke-NativeStdoutChecked", "function Test-RepositoryChangedFileCandidate")

    for fragment in [
        "function Get-RepositoryChangedFiles",
        '"diff", "--name-only"',
        '"diff", "--cached", "--name-only"',
        '"ls-files", "--others", "--exclude-standard"',
        "Sort-Object -Unique",
    ]:
        assert fragment in discovery

    assert "2>&1" not in discovery
    assert "git status --short" not in discovery
    assert '"status"' not in discovery
    assert "RedirectStandardOutput = $true" in stdout_wrapper
    assert "RedirectStandardError = $true" in stdout_wrapper
    assert "stderr ignored for path discovery" in stdout_wrapper


def test_warning_lines_are_not_repository_changed_file_candidates() -> None:
    content = read(SCRIPT)
    candidate = section(content, "function Test-RepositoryChangedFileCandidate", "function Get-RepositoryChangedFiles")

    for fragment in [
        '"warning:"',
        '"fatal:"',
        '"error:"',
        "[System.IO.Path]::IsPathRooted",
        'StartsWith("../")',
    ]:
        assert fragment in candidate


def test_prepare_config_static_contract_contains_required_fields() -> None:
    content = read(SCRIPT)
    prepare = section(content, "function New-DraftPublishConfig", "function Get-ProfileValidationSummaryLines")

    for fragment in [
        '[ValidateSet("Plan", "PrepareConfig", "A", "B", "C")]',
        "Invoke-PrepareConfig",
        "expected_files = @($ChangedFiles)",
        "changed_files = @($ChangedFiles)",
        "verification_profile",
        "risk_level",
        "verification_phase",
        "profile_selector_expected_profile",
        "intent = @(\"publish_step\", \"human_gated\")",
        "provided_gates = @()",
        "phase_a_checks",
        "phase_c_checks",
        "allow_no_github_checks_reported = $true",
        "log_max_count = 12",
        "DRAFT_REVIEW_REQUIRED",
        "Do not publish automatically",
    ]:
        assert fragment in prepare or fragment in content


@pytest.mark.skipif(not (pwsh_available() and git_available()), reason="pwsh or git executable not available")
def test_prepare_config_generates_draft_config_without_warning_paths(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    write_untracked(repo, "README.md")
    write_untracked(repo, "docs/new_scope.md")
    write_untracked(repo, "tests/unit/new_scope_test.py")
    bridge = tmp_path / "bridge"

    result = run_pwsh_from_repo(
        repo,
        "-Phase",
        "PrepareConfig",
        "-StepNumber",
        "0810",
        "-StepName",
        "Publish_Runner_Scope_Discovery_Test",
        "-BranchName",
        "step-0810-test",
        "-CommitMessage",
        "0810 test",
        "-PrTitle",
        "0810 test",
        "-NextStep",
        "0820) Next test",
        "-BridgeRoot",
        bridge,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    config_path = bridge / "0810-Publish_Config_Draft_Publish_Runner_Scope_Discovery_Test.json"
    review_path = bridge / "0810-PrepareConfig_Review_Publish_Runner_Scope_Discovery_Test.md"
    assert config_path.exists()
    assert review_path.exists()
    assert config_path.read_bytes()[:3] != b"\xef\xbb\xbf"

    config = json.loads(read(config_path))
    assert sorted(config["expected_files"]) == sorted(
        [
            "README.md",
            "docs/new_scope.md",
            "tests/unit/new_scope_test.py",
        ]
    )
    assert config["changed_files"] == config["expected_files"]
    assert sorted(config["changed_files"]) == sorted(
        [
            "README.md",
            "docs/new_scope.md",
            "tests/unit/new_scope_test.py",
        ]
    )
    assert not any(item.startswith("warning:") for item in config["expected_files"])
    assert config["verification_profile"] == "publish"
    assert config["risk_level"] == "L1"
    assert config["allow_no_github_checks_reported"] is True
    assert "No commit, push, PR, merge, deploy or tag was executed." in read(review_path)


@pytest.mark.skipif(not (pwsh_available() and git_available()), reason="pwsh or git executable not available")
def test_out_of_scope_blocks_and_writes_recovery_suggested_config(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    write_untracked(repo, "README.md")
    write_untracked(repo, "docs/out_of_scope.md")
    write_untracked(repo, "tests/unit/new_scope_test.py")
    bridge = tmp_path / "bridge"
    config_path = tmp_path / "publish_config.json"
    config_path.write_text(
        json.dumps(
            {
                "step": "0810",
                "name": "Out_Of_Scope_Test",
                "repo_path": str(repo),
                "bridge_root": str(bridge),
                "branch": "step-0810-test",
                "commit_message": "0810 test",
                "pr_title": "0810 test",
                "pr_body": "test",
                "next_step": "0820) Next test",
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

    result = run_pwsh_from_repo(repo, "-Config", config_path, "-Phase", "A", "-BridgeRoot", bridge)

    assert result.returncode == 1
    combined_output = result.stdout + result.stderr
    assert "Out-of-scope changes detected" in combined_output
    assert "Review the suggested config" in combined_output

    recovery_report = bridge / "0810-Recovery_Out_Of_Scope_Out_Of_Scope_Test.md"
    suggested_config = bridge / "0810-Recovery_Out_Of_Scope_Suggested_Config_Out_Of_Scope_Test.json"
    assert recovery_report.exists()
    assert suggested_config.exists()
    assert suggested_config.read_bytes()[:3] != b"\xef\xbb\xbf"
    suggested = json.loads(read(suggested_config))
    assert sorted(suggested["expected_files"]) == sorted(
        [
            "README.md",
            "docs/out_of_scope.md",
            "tests/unit/new_scope_test.py",
        ]
    )
    assert "The runner remains fail-closed" in read(recovery_report)
    assert "No commit, push, PR, merge or deploy was executed" in read(recovery_report)


def test_no_false_completed_and_docx_best_effort_are_documented_in_runner() -> None:
    content = read(SCRIPT)
    phase_b = section(content, "function Invoke-PhaseB", "function Assert-PrNumberText")
    phase_c = section(content, "function Invoke-PhaseC", "function Escape-Xml")
    bridge = section(content, "function Write-BridgeOutputs", "function New-SelfTestConfig")
    main = section(content, "try {", "exit 0\n} catch")

    assert "Phase B did not resolve a non-empty numeric PR number" in phase_b
    assert "$number = Get-PrNumber -PublishConfig $PublishConfig" in phase_c
    assert phase_c.index("$number = Get-PrNumber") < phase_c.index("Invoke-Gh")
    assert 'Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "PASS"' in main
    assert main.index("Invoke-PhaseC -PublishConfig $publishConfig -RepoPath $repoPath") < main.index(
        'Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "PASS"'
    )

    for fragment in [
        "COMPLETATO CON WARNING NON BLOCCANTE",
        "TXT and Markdown are primary outputs",
        "DOCX is best-effort",
        "DOCX accessory output failed without blocking",
        "LAST-Output_Compatto.docx.failed.txt",
    ]:
        assert fragment in bridge or fragment in content


def test_step_0810_document_covers_policy() -> None:
    assert DOC.exists()
    doc = read(DOC)
    for fragment in [
        "0800",
        "0805",
        "expected_files",
        "PrepareConfig",
        "recovery report",
        "LF/CRLF",
        "fail-closed",
        "COMPLETATO CON WARNING NON BLOCCANTE",
        "DOCX",
        "best-effort",
    ]:
        assert fragment in doc
