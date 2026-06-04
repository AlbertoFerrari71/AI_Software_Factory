from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_invoke.py"
DOC = ROOT / "docs" / "52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_codex_readonly_invocation_template.md"

FORBIDDEN_PATTERNS = [
    "git commit",
    "git push",
    "gh pr create",
    "gh pr merge",
    "gh release",
    "git merge",
    "git reset --hard",
    "git clean",
    "Set-ExecutionPolicy",
    "setx PATH",
    "workspace-write",
    "danger-full-access",
    "shell=True",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)


def make_git_repo(tmp_path: Path, branch: str = "step-590-example") -> Path:
    if shutil.which("git") is None:
        pytest.skip("git executable not available")

    repo = tmp_path / "target_repo"
    repo.mkdir()
    init_result = run_git(repo, "init", "-b", "main")
    if init_result.returncode != 0:
        init_result = run_git(repo, "init")
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr

    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "user.name", "ASF Test")
    (repo / "README.md").write_text("# Temporary repo\n", encoding="utf-8")
    assert run_git(repo, "add", "README.md").returncode == 0
    commit_result = run_git(repo, "commit", "-m", "initial commit")
    assert commit_result.returncode == 0, commit_result.stdout + commit_result.stderr

    switch_result = run_git(repo, "switch", "-c", branch)
    if switch_result.returncode != 0:
        switch_result = run_git(repo, "checkout", "-b", branch)
    assert switch_result.returncode == 0, switch_result.stdout + switch_result.stderr
    return repo


def write_handoff(tmp_path: Path) -> Path:
    handoff = tmp_path / "codex_handoff.md"
    handoff.write_text("# Codex Handoff\n\nRead-only analysis request.\n", encoding="utf-8")
    return handoff


def write_approval(tmp_path: Path, decision: str) -> Path:
    approval = tmp_path / "human_approval_gate.md"
    approval.write_text(
        f"""# ASF Human Approval Gate

## Summary

- decisione: `{decision}`
""",
        encoding="utf-8",
    )
    return approval


def base_args(repo: Path, handoff: Path, output_dir: Path) -> list[str | Path]:
    return [
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "590",
        "--branch",
        "step-590-example",
        "--handoff-path",
        handoff,
        "--output-dir",
        output_dir,
    ]


def test_readonly_invocation_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "execute-readonly" in result.stdout
    assert "--confirm-readonly-execution" in result.stdout


def test_readonly_invocation_preview_generates_files_without_running_codex(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "GO")
    output_dir = tmp_path / "readonly"

    result = run_script(*base_args(repo, handoff, output_dir), "--approval-gate", approval)

    assert result.returncode == 0, result.stdout + result.stderr
    step_dir = output_dir / "Temp_Project" / "step_590"
    markdown = step_dir / "readonly_invocation_preview.md"
    preview = step_dir / "codex_readonly_command_preview.ps1"

    assert markdown.exists()
    assert preview.exists()

    markdown_content = read(markdown)
    preview_content = read(preview)
    for fragment in ["Temp_Project", "590", "step-590-example", "read-only", "Codex was not executed"]:
        assert fragment in markdown_content
    assert "# Get-Content -Raw" in preview_content
    assert "codex exec --sandbox read-only" in preview_content
    assert "Codex was not executed" in result.stdout


def test_execute_readonly_without_confirmation_fails_before_codex_lookup(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "GO")

    result = run_script(
        "--mode",
        "execute-readonly",
        *base_args(repo, handoff, tmp_path / "readonly"),
        "--approval-gate",
        approval,
    )

    assert result.returncode != 0
    assert "confirm-readonly-execution" in result.stderr


def test_execute_readonly_with_non_go_approval_fails_before_codex_lookup(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "WARNING")

    result = run_script(
        "--mode",
        "execute-readonly",
        *base_args(repo, handoff, tmp_path / "readonly"),
        "--approval-gate",
        approval,
        "--confirm-readonly-execution",
        "YES_I_APPROVE_READONLY_CODEX_EXECUTION",
    )

    assert result.returncode != 0
    assert "must be GO" in result.stderr


def test_execute_readonly_with_dirty_working_tree_fails_before_codex_lookup(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "GO")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = run_script(
        "--mode",
        "execute-readonly",
        *base_args(repo, handoff, tmp_path / "readonly"),
        "--approval-gate",
        approval,
        "--confirm-readonly-execution",
        "YES_I_APPROVE_READONLY_CODEX_EXECUTION",
    )

    assert result.returncode != 0
    assert "working tree must be CLEAN" in result.stderr


def test_readonly_invocation_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC)
    for fragment in ["preview", "execute-readonly", "YES_I_APPROVE_READONLY_CODEX_EXECUTION", "read-only"]:
        assert fragment in doc


def test_readonly_invocation_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content
