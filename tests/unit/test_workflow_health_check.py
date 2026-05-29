from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_workflow_health.py"
DOC = ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md"
INDEX = ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_health_check_files_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()


def test_workflow_health_check_script_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Workflow Health Check PASSED" in result.stdout


def test_workflow_health_check_script_avoids_forbidden_patterns() -> None:
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


def test_workflow_health_check_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "Verification Gate",
        "Documentation Sync",
        "Release Smoke Workflow",
        "Project Workflow Index",
        "read-only",
        "local-first",
        "CI",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_project_workflow_index_mentions_health_check() -> None:
    content = read(INDEX)

    assert "docs/35_WORKFLOW_HEALTH_CHECK.md" in content
    assert "scripts/check_workflow_health.py" in content
