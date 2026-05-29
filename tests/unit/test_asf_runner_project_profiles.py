from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_next_step.py"
CONFIG = ROOT / "config" / "asf_project_profiles.json"
DOC = ROOT / "docs" / "43_ASF_RUNNER_PROJECT_PROFILES.md"


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


def make_git_repo(tmp_path: Path) -> Path:
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
    return repo


def write_profiles_config(path: Path, repo: Path) -> None:
    data = {
        "profiles": {
            "Temp_Project": {
                "project_name": "Temp_Project",
                "repo_path": str(repo),
                "main_branch": "main",
                "test_command": "python -m pytest",
                "notes": ["Safety note from profile."],
                "default_forbidden_notes": ["No target repo writes from runner."],
                "recommended_inspection": ["README.md", "docs/ROADMAP.md"],
            }
        }
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_profiles_config_and_doc_exist() -> None:
    assert CONFIG.exists()
    assert DOC.exists()


def test_prepare_mode_uses_profile_from_temp_config(tmp_path: Path) -> None:
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
        "Profile Prepare Test",
        "--branch",
        "step-590-profile-prepare-test",
        "--objective",
        "Prepare a profile-based runner output.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    step_dir = output_dir / "Temp_Project" / "step_590"
    assert (step_dir / "task_packet.md").exists()
    assert (step_dir / "codex_handoff.md").exists()
    assert (step_dir / "runner_report.md").exists()
    assert (step_dir / "verification_pack.md").exists()

    report = read(step_dir / "runner_report.md")
    task_packet = read(step_dir / "task_packet.md")
    assert "profile: `Temp_Project`" in report
    assert "Safety note from profile." in task_packet
    assert "docs/ROADMAP.md" in task_packet
    assert "Lite: PASS" in report
    assert "Strict: PASS" in report


def test_prepare_mode_profile_can_be_overridden(tmp_path: Path) -> None:
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
        "--project-name",
        "Override_Project",
        "--repo-path",
        repo,
        "--step",
        "600",
        "--title",
        "Profile Override Test",
        "--branch",
        "step-600-profile-override-test",
        "--objective",
        "Prepare an override-based runner output.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (output_dir / "Override_Project" / "step_600" / "task_packet.md").exists()


def test_missing_profile_fails_with_clear_error(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    config = tmp_path / "profiles.json"
    write_profiles_config(config, repo)

    result = run_runner(
        "--mode",
        "prepare",
        "--profile",
        "Missing_Profile",
        "--profiles-config",
        config,
        "--step",
        "590",
        "--title",
        "Missing Profile Test",
        "--branch",
        "step-590-missing-profile-test",
        "--objective",
        "Fail on missing profile.",
    )

    assert result.returncode != 0
    assert "profile not found: Missing_Profile" in result.stderr


def test_malformed_profile_config_fails_with_clear_error(tmp_path: Path) -> None:
    config = tmp_path / "profiles.json"
    config.write_text("{not valid json", encoding="utf-8")

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
        "Malformed Profile Test",
        "--branch",
        "step-590-malformed-profile-test",
        "--objective",
        "Fail on malformed profile config.",
    )

    assert result.returncode != 0
    assert "profile config is not valid JSON" in result.stderr


def test_project_profiles_document_contains_required_context() -> None:
    content = read(DOC)
    lower_content = content.casefold()

    required_fragments = [
        "config/asf_project_profiles.json",
        "AI_Software_Factory",
        "Family_Photo_Organizer",
        "override",
        "sicurezza",
        "GitHub API",
    ]
    for fragment in required_fragments:
        assert fragment.casefold() in lower_content


def test_health_check_includes_runner_upgrade_central_files() -> None:
    content = read(ROOT / "scripts" / "check_workflow_health.py")

    required_fragments = [
        "docs/43_ASF_RUNNER_PROJECT_PROFILES.md",
        "docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md",
        "docs/45_ASF_RUNNER_VERIFICATION_PACK.md",
        "config/asf_project_profiles.json",
        "templates/codex_tasks/asf_runner_verification_pack_template.md",
    ]
    for fragment in required_fragments:
        assert fragment in content
