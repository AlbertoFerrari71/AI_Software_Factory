from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_generate_closure_pack.py"
DOC = ROOT / "docs" / "48_ASF_HUMAN_GATED_CLOSURE_PACK.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_human_gated_closure_pack_template.md"


FORBIDDEN_PATTERNS = [
    "git commit",
    "git push",
    "gh pr create",
    "gh pr merge",
    "gh release",
    "git merge",
    "git reset --hard",
    "git clean",
    "codex run",
    "codex exec",
    "gh api",
    "api.github.com",
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


def test_human_gated_closure_pack_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--commit-message" in result.stdout
    assert "--pr-title" in result.stdout


def test_human_gated_closure_pack_generates_markdown(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    output_dir = tmp_path / "closure"

    result = run_script(
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "580",
        "--branch",
        "step-580-example",
        "--commit-message",
        "580 example closure",
        "--pr-title",
        "580) Example Closure",
        "--pr-body",
        "Manual closure body.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    pack = output_dir / "Temp_Project" / "step_580" / "closure_pack.md"
    assert pack.exists()

    content = read(pack)
    required_fragments = [
        "ASF Human-Gated Closure Pack",
        "Temp_Project",
        "580",
        "step-580-example",
        "580 example closure",
        "580) Example Closure",
        "gh pr checks --watch",
        "PSNativeCommandUseErrorActionPreference",
        "warning LF/CRLF",
        "Step Closure Report",
        "manuale",
        "human-gated",
        "non eseguiti dallo script",
    ]
    lowered = content.casefold()
    for fragment in required_fragments:
        assert fragment.casefold() in lowered


def test_human_gated_closure_pack_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC).casefold()
    for fragment in ["human-gated", "PR checks", "LF/CRLF", "limiti", "non esegue"]:
        assert fragment.casefold() in doc


def test_human_gated_closure_pack_script_avoids_operational_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content
