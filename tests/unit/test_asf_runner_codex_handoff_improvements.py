from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_next_step.py"
DOC = ROOT / "docs" / "44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_next_step_runner_handoff_template.md"


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


def write_profiles_config(path: Path, repo: Path) -> None:
    data = {
        "profiles": {
            "Temp_Project": {
                "project_name": "Temp_Project",
                "repo_path": str(repo),
                "main_branch": "main",
                "test_command": "python -m pytest",
                "notes": ["Profile safety note for handoff."],
                "recommended_inspection": ["README.md", "docs/SAFETY.md"],
            }
        }
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_codex_handoff_improvement_files_exist() -> None:
    assert DOC.exists()
    assert TEMPLATE.exists()


def test_generated_handoff_contains_improved_structure_and_profile_notes(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    config = tmp_path / "profiles.json"
    output_dir = tmp_path / "out"
    write_profiles_config(config, repo)

    result = run_runner(
        "--mode",
        "prepare",
        "--profile",
        "Temp_Project",
        "--profiles-config",
        config,
        "--step",
        "590",
        "--title",
        "Handoff Improvements Test",
        "--branch",
        "step-590-handoff-improvements-test",
        "--objective",
        "Prepare an improved Codex handoff.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    handoff = read(output_dir / "Temp_Project" / "step_590" / "codex_handoff.md")

    required_fragments = [
        "Handoff Improvements Test",
        "Contesto progetto target",
        "Branch di lavoro previsto",
        "Stato Git letto dal runner",
        "Prerequisito",
        "FASE 1",
        "FASE 2",
        "Codex",
        "forbidden actions",
        "Step Closure Report",
        "Profile safety note for handoff.",
        "Questo handoff e' stato generato dal runner",
    ]
    for fragment in required_fragments:
        assert fragment.casefold() in handoff.casefold()


def test_handoff_template_contains_required_sections() -> None:
    content = read(TEMPLATE)

    required_fragments = [
        "FASE 1",
        "FASE 2",
        "Domande chiuse",
        "Forbidden actions",
        "Step Closure Report",
        "revisionato da Alberto/ChatGPT",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_codex_handoff_improvements_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "FASE 1",
        "FASE 2",
        "Human gate",
        "Codex",
        "Alberto/ChatGPT",
        "manuale",
    ]
    for fragment in required_fragments:
        assert fragment in content

