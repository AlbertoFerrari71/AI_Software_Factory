from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_next_step.py"
DOC = ROOT / "docs" / "42_ASF_NEXT_STEP_RUNNER.md"
HANDOFF_TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_next_step_runner_handoff_template.md"


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


def run_runner(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def base_args(repo_path: Path, output_dir: Path) -> list[str | Path]:
    return [
        "--mode",
        "prepare",
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo_path,
        "--main-branch",
        "main",
        "--step",
        "580",
        "--title",
        "Temporary Prepare Mode Test",
        "--branch",
        "step-580-temporary-prepare-mode-test",
        "--objective",
        "Prepare a temporary runner test packet.",
        "--output-dir",
        output_dir,
        "--strict-ready",
    ]


def test_asf_next_step_runner_files_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert HANDOFF_TEMPLATE.exists()


def test_asf_next_step_runner_help_returns_success() -> None:
    result = run_runner("--help")

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "prepare" in result.stdout


def test_asf_next_step_runner_fails_with_unsupported_mode(tmp_path: Path) -> None:
    args = base_args(ROOT, tmp_path / "out")
    args[1] = "run"

    result = run_runner(*args)

    assert result.returncode != 0
    assert "supports only 'prepare'" in result.stderr


def test_asf_next_step_runner_fails_with_non_numeric_step(tmp_path: Path) -> None:
    args = base_args(ROOT, tmp_path / "out")
    args[9] = "abc"

    result = run_runner(*args)

    assert result.returncode != 0
    assert "--step must be numeric" in result.stderr


def test_asf_next_step_runner_fails_with_step_not_multiple_of_10(tmp_path: Path) -> None:
    args = base_args(ROOT, tmp_path / "out")
    args[9] = "581"

    result = run_runner(*args)

    assert result.returncode != 0
    assert "--step must be a multiple of 10" in result.stderr


def test_asf_next_step_runner_fails_with_branch_containing_spaces(tmp_path: Path) -> None:
    args = base_args(ROOT, tmp_path / "out")
    args[13] = "branch with spaces"

    result = run_runner(*args)

    assert result.returncode != 0
    assert "--branch must not contain spaces" in result.stderr


def test_asf_next_step_runner_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content


def git_available() -> bool:
    return shutil.which("git") is not None


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def test_prepare_mode_creates_outputs_with_temporary_git_repo(tmp_path: Path) -> None:
    if not git_available():
        pytest.skip("git executable not available")

    target_repo = tmp_path / "target_repo"
    target_repo.mkdir()

    init_result = run_git(target_repo, "init", "-b", "main")
    if init_result.returncode != 0:
        init_result = run_git(target_repo, "init")
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr

    run_git(target_repo, "config", "user.email", "test@example.invalid")
    run_git(target_repo, "config", "user.name", "ASF Test")
    (target_repo / "README.md").write_text("# Temporary repo\n", encoding="utf-8")
    assert run_git(target_repo, "add", "README.md").returncode == 0
    commit_result = run_git(target_repo, "commit", "-m", "initial commit")
    assert commit_result.returncode == 0, commit_result.stdout + commit_result.stderr

    output_dir = tmp_path / "runner_output"
    result = run_runner(*base_args(target_repo, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr

    step_dir = output_dir / "Temp_Project" / "step_580"
    task_packet = step_dir / "task_packet.md"
    handoff = step_dir / "codex_handoff.md"
    report = step_dir / "runner_report.md"
    verification_pack = step_dir / "verification_pack.md"

    assert task_packet.exists()
    assert handoff.exists()
    assert report.exists()
    assert verification_pack.exists()

    report_content = read(report)
    task_content = read(task_packet)

    assert "CLEAN" in report_content or "DIRTY" in report_content
    assert "Lite: PASS" in report_content
    assert "Strict: PASS" in report_content
    assert "verification_pack.md" in report_content

    required_task_fragments = [
        "580",
        "step-580-temporary-prepare-mode-test",
        "Prepare a temporary runner test packet.",
        "FORBIDDEN ACTIONS",
        "Nessun commit/push/PR/merge",
        "Non fare commit",
        "Non fare push",
        "Non aprire PR",
        "Non fare merge",
        "Step Closure Report",
    ]
    for fragment in required_task_fragments:
        assert fragment in task_content


def test_asf_next_step_runner_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "FASE 1",
        "FASE 2",
        "Codex",
        "Git",
        "Step Closure Report",
        "Lite",
        "Strict",
        "Human gate",
        "prepare mode",
        "automazione completa non autorizzata",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_300_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 300 - ASF Next Step Runner" in changelog
    assert "DEC-050 - ASF Next Step Runner" in decisions
    assert "STEP 310" in roadmap
    assert "ASF Next Step Runner Project Profiles" in roadmap
