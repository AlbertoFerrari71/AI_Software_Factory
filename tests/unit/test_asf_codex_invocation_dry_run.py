from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_invocation_dry_run.py"
DOC = ROOT / "docs" / "51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_codex_invocation_dry_run_template.md"


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
    handoff.write_text("# Codex Handoff\n\nManual handoff content.\n", encoding="utf-8")
    return handoff


def write_approval(tmp_path: Path, decision: str) -> Path:
    approval = tmp_path / "human_approval_gate.md"
    approval.write_text(
        f"""# ASF Human Approval Gate

## Summary

- decisione: `{decision}`

## Nota

La decisione finale resta di Alberto.
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


def test_codex_invocation_dry_run_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--handoff-path" in result.stdout
    assert "workspace-write-preview" in result.stdout


def test_codex_invocation_dry_run_generates_pack(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "GO")
    output_dir = tmp_path / "dry_run"

    result = run_script(*base_args(repo, handoff, output_dir), "--approval-gate", approval)

    assert result.returncode == 0, result.stdout + result.stderr
    step_dir = output_dir / "Temp_Project" / "step_590"
    markdown = step_dir / "codex_invocation_dry_run.md"
    preview = step_dir / "codex_exec_preview.ps1"

    assert markdown.exists()
    assert preview.exists()

    markdown_content = read(markdown)
    preview_content = read(preview)
    required_fragments = [
        "ASF Codex Invocation Dry Run Pack",
        "Temp_Project",
        "590",
        "step-590-example",
        "read-only",
        "codex exec",
        "not executed",
        "DRY RUN ONLY",
    ]
    for fragment in required_fragments:
        assert fragment in markdown_content

    assert "DO NOT RUN WITHOUT ALBERTO APPROVAL" in preview_content
    assert "codex exec" in preview_content
    assert "Preview command, not executed" in preview_content
    assert "Codex was not invoked" in result.stdout


def test_codex_invocation_dry_run_with_no_go_approval_marks_do_not_run(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)
    approval = write_approval(tmp_path, "NO-GO")
    output_dir = tmp_path / "dry_run"

    result = run_script(*base_args(repo, handoff, output_dir), "--approval-gate", approval)

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "codex_invocation_dry_run.md")

    assert "NO-GO" in content
    assert "DO NOT RUN" in content
    assert "must not be run" in content


def test_codex_invocation_dry_run_rejects_danger_full_access(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    handoff = write_handoff(tmp_path)

    result = run_script(*base_args(repo, handoff, tmp_path / "dry_run"), "--sandbox", "danger-full-access")

    assert result.returncode != 0
    assert "invalid choice" in result.stderr


def test_codex_invocation_dry_run_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC)
    for fragment in ["dry-run", "codex_exec_preview.ps1", "read-only", "workspace-write-preview", "DO NOT RUN"]:
        assert fragment in doc


def test_codex_invocation_dry_run_script_avoids_operational_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content

    assert '["codex"' not in content
    assert "['codex'" not in content
    assert "shell=True" not in content

