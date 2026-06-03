from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "asf_next_step.py"
DOC = ROOT / "docs" / "46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_runner_verification_pack_template.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_runner(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *(str(arg) for arg in args)],
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


def write_profiles_config(tmp_path: Path, repo: Path) -> Path:
    config = {
        "profiles": {
            "Temp_Project": {
                "project_name": "Temp_Project",
                "repo_path": str(repo),
                "main_branch": "main",
                "test_command": "python -m pytest",
                "health_command": "python scripts/check_workflow_health.py",
                "notes": ["Human gate required."],
            }
        }
    }
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_hardened_verification_pack_contains_full_cycle_checks(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    profiles = write_profiles_config(tmp_path, repo)
    output_dir = tmp_path / "out"

    result = run_runner(
        "--mode",
        "prepare",
        "--profile",
        "Temp_Project",
        "--profiles-config",
        profiles,
        "--step",
        "600",
        "--title",
        "Verification Pack Hardening Test",
        "--branch",
        "step-600-verification-pack-hardening-test",
        "--objective",
        "Generate a hardened verification pack.",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    pack = read(output_dir / "Temp_Project" / "step_600" / "verification_pack.md")

    required_fragments = [
        "Temp_Project",
        str(repo),
        "Branch corrente target",
        "Working tree",
        "Ultimi commit",
        "Pre-Codex checks",
        "prerequisito dello step precedente",
        "Leggere `codex_handoff.md`",
        "Human gate",
        "Post-Codex local checks",
        "git status --short",
        "git --no-pager diff --stat",
        "git --no-pager diff --check",
        "python -m pytest",
        "python scripts/check_workflow_health.py",
        "file temporanei",
        "Scope checks",
        "secret",
        ".env",
        "CI",
        "Codex report checks",
        "VERIFICHE NON ESEGUITE",
        "CONFERME VINCOLI",
        "Approvazione commit",
        "Approvazione push",
        "Approvazione PR",
        "Approvazione merge",
        "gh pr checks --watch",
        "no checks reported",
        "LF/CRLF",
        "Quick Reference",
        "Workflow Command Cookbook",
        "Step Closure Report",
    ]
    for fragment in required_fragments:
        assert fragment in pack


def test_verification_pack_hardening_doc_and_template_cover_required_topics() -> None:
    doc = read(DOC)
    template = read(TEMPLATE)
    combined = doc + "\n" + template

    required_fragments = [
        "Pre-Codex checks",
        "Post-Codex",
        "Report checks",
        "PR checks",
        "LF/CRLF",
        "Human gates",
        "gh pr checks --watch",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_health_check_includes_automation_readiness_pack_files() -> None:
    content = read(ROOT / "scripts" / "check_workflow_health.py")

    required_fragments = [
        "docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md",
        "docs/47_ASF_CODEX_REPORT_INTAKE.md",
        "docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md",
        "scripts/asf_codex_report_intake.py",
        "scripts/asf_generate_closure_pack.py",
        "templates/codex_tasks/asf_codex_report_intake_template.md",
        "templates/codex_tasks/asf_human_gated_closure_pack_template.md",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_340_360_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "MEGA-STEP 340-360 - ASF Runner Automation Readiness Pack" in changelog
    assert "DEC-052 - ASF Runner Automation Readiness Pack" in decisions
    assert "STEP 370" in roadmap
    assert "ASF Runner Human Approval Gate" in roadmap
