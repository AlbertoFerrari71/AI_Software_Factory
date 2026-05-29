from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_next_step.py"
DOC = ROOT / "docs" / "45_ASF_RUNNER_VERIFICATION_PACK.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_runner_verification_pack_template.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_runner(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def make_git_repo(tmp_path: Path) -> Path:
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
    return repo


def test_verification_pack_files_exist() -> None:
    assert DOC.exists()
    assert TEMPLATE.exists()


def test_generated_verification_pack_contains_required_sections(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "out"

    result = run_runner(
        "--mode",
        "prepare",
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--main-branch",
        "main",
        "--step",
        "590",
        "--title",
        "Verification Pack Test",
        "--branch",
        "step-590-verification-pack-test",
        "--objective",
        "Prepare a verification pack.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    pack = read(output_dir / "Temp_Project" / "step_590" / "verification_pack.md")

    required_fragments = [
        "ASF Runner Verification Pack",
        "Pre-Codex checks",
        "Post-Codex local checks",
        "git status --short",
        "git --no-pager diff --check",
        "python -m pytest",
        "Human gates",
        "Quick Reference",
        "Command Cookbook",
        "Step Closure Report",
        "docs/36_WORKFLOW_QUICK_REFERENCE.md",
        "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
        "docs/37_STEP_CLOSURE_REPORT.md",
    ]
    for fragment in required_fragments:
        assert fragment in pack


def test_verification_pack_template_contains_required_sections() -> None:
    content = read(TEMPLATE)

    required_fragments = [
        "ASF Runner Verification Pack Template",
        "Pre-Codex checks",
        "Post-Codex local checks",
        "Human gates",
        "docs/36_WORKFLOW_QUICK_REFERENCE.md",
        "docs/37_STEP_CLOSURE_REPORT.md",
        "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_verification_pack_document_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "Verification Pack",
        "commit",
        "push",
        "PR",
        "merge",
        "Quick Reference",
        "Command Cookbook",
        "Step Closure Report",
        "python -m pytest",
    ]
    for fragment in required_fragments:
        assert fragment in content

