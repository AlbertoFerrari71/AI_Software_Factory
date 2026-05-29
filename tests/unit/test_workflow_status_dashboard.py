from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "show_workflow_status.py"
DOC = ROOT / "docs" / "39_WORKFLOW_STATUS_DASHBOARD.md"
INDEX = ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md"
COOKBOOK = ROOT / "docs" / "38_WORKFLOW_COMMAND_COOKBOOK.md"
HEALTH = ROOT / "scripts" / "check_workflow_health.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_status_dashboard_files_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()


def test_workflow_status_dashboard_script_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    required_output = [
        "Workflow Status Dashboard",
        "AI Software Factory",
        "Branch",
        "Working tree",
        "Next suggested local checks",
        "check_workflow_health.py",
        "verify.ps1",
    ]
    for fragment in required_output:
        assert fragment in result.stdout


def test_workflow_status_dashboard_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    forbidden_patterns = [
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
    for pattern in forbidden_patterns:
        assert pattern not in content


def test_workflow_status_dashboard_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "read-only",
        "local-first",
        "Workflow Health Check",
        "Verification Gate",
        "Workflow Quick Reference",
        "Workflow Command Cookbook",
        "Step Closure Report",
        "GitHub API",
        "CI",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_workflow_status_dashboard_is_linked_from_index_and_cookbook() -> None:
    assert "docs/39_WORKFLOW_STATUS_DASHBOARD.md" in read(INDEX)
    assert "docs/39_WORKFLOW_STATUS_DASHBOARD.md" in read(COOKBOOK)


def test_workflow_health_check_includes_dashboard_files() -> None:
    content = read(HEALTH)

    assert "docs/39_WORKFLOW_STATUS_DASHBOARD.md" in content
    assert "scripts/show_workflow_status.py" in content


def test_step_270_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 270 - Workflow Status Dashboard" in changelog
    assert "DEC-047 - Workflow Status Dashboard" in decisions
    assert "STEP 280" in roadmap
    assert "Release Readiness" in roadmap
