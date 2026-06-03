from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_human_approval_gate.py"
DOC = ROOT / "docs" / "49_ASF_HUMAN_APPROVAL_GATE.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_human_approval_gate_template.md"


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
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def git_available() -> bool:
    return shutil.which("git") is not None


def make_git_repo(tmp_path: Path, branch: str = "step-590-example") -> Path:
    if not git_available():
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


def base_args(repo: Path, output_dir: Path) -> list[str | Path]:
    return [
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "590",
        "--branch",
        "step-590-example",
        "--output-dir",
        output_dir,
    ]


def test_human_approval_gate_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--project-name" in result.stdout
    assert "--allow-dirty" in result.stdout
    assert "--require-tests" in result.stdout


def test_human_approval_gate_generates_report_for_clean_git_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "approval"

    result = run_script(*base_args(repo, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    gate = output_dir / "Temp_Project" / "step_590" / "human_approval_gate.md"
    assert gate.exists()

    content = read(gate)
    required_fragments = [
        "ASF Human Approval Gate",
        "Temp_Project",
        "590",
        "step-590-example",
        "current branch",
        "working tree",
        "decisione",
        "CLEAN",
        "La decisione finale resta di Alberto",
    ]
    for fragment in required_fragments:
        assert fragment in content
    assert "`GO`" in content or "`WARNING`" in content


def test_human_approval_gate_dirty_without_allow_dirty_is_no_go(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "approval"
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = run_script(*base_args(repo, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    gate = output_dir / "Temp_Project" / "step_590" / "human_approval_gate.md"
    content = read(gate)

    assert "`NO-GO`" in content
    assert "DIRTY" in content
    assert "allow-dirty" in content
    assert "?? dirty.txt" in run_git(repo, "status", "--short").stdout


def test_human_approval_gate_dirty_with_allow_dirty_is_warning(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "approval"
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = run_script(*base_args(repo, output_dir), "--allow-dirty")

    assert result.returncode == 0, result.stdout + result.stderr
    gate = output_dir / "Temp_Project" / "step_590" / "human_approval_gate.md"
    content = read(gate)

    assert "`WARNING`" in content
    assert "accepted because --allow-dirty is active" in content
    assert "?? dirty.txt" in run_git(repo, "status", "--short").stdout


def test_human_approval_gate_requested_missing_files_create_hold(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "approval"

    result = run_script(
        *base_args(repo, output_dir),
        "--codex-report-intake",
        tmp_path / "missing_intake.md",
        "--verification-pack",
        tmp_path / "missing_verification.md",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "human_approval_gate.md")

    assert "`HOLD`" in content
    assert "was requested but is missing" in content


def test_human_approval_gate_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC)
    for fragment in ["GO", "WARNING", "HOLD", "NO-GO", "Codex Report Intake", "Closure Pack", "Alberto"]:
        assert fragment in doc


def test_human_approval_gate_script_avoids_operational_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content

