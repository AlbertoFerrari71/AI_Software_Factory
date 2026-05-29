from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "38_WORKFLOW_COMMAND_COOKBOOK.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_command_cookbook_exists() -> None:
    assert DOC.exists()


def test_workflow_command_cookbook_contains_required_commands_and_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "Workflow Command Cookbook",
        "AI Software Factory",
        "Set-Location",
        "generate_task_packet.py",
        "validate_task_packet.py",
        "--strict",
        "check_workflow_health.py",
        "verify.ps1",
        "git status --short",
        "git --no-pager diff --check",
        "python -m pytest",
        "gh pr create",
        "gh pr checks --watch",
        "gh pr merge",
        "git fetch --all --prune",
        "reset --hard",
        "CRLF/LF",
        "report Codex non equivale a merge su main",
        "branch remoto assente",
        "working tree sporca su main",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_workflow_command_cookbook_clarifies_codex_boundaries() -> None:
    content = read(DOC)

    assert "Codex non deve fare commit" in content
    assert "Codex non deve fare push" in content
    assert "Codex non deve aprire PR" in content
    assert "Codex non deve fare merge" in content


def test_workflow_command_cookbook_has_required_recipes() -> None:
    content = read(DOC).casefold()

    assert "pr checks non disponibili" in content
    assert "branch locale presente ma branch remoto assente" in content
    assert "health check fallito" in content


def test_workflow_command_cookbook_links_references() -> None:
    content = read(DOC)

    required_links = [
        "docs/36_WORKFLOW_QUICK_REFERENCE.md",
        "docs/37_STEP_CLOSURE_REPORT.md",
        "templates/codex_tasks/step_closure_report_template.md",
    ]
    for link in required_links:
        assert link in content


def test_workflow_command_cookbook_marks_git_operations_as_supervised() -> None:
    content = read(DOC).casefold()

    assert "alberto" in content
    assert "non sono automazione non presidiata" in content
    assert "non devono essere messi in uno script automatico" in content


def test_step_260_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 260 - Workflow Command Cookbook" in changelog
    assert "DEC-046 - Workflow Command Cookbook" in decisions
    assert "STEP 270" in roadmap
    assert "Workflow Status Dashboard" in roadmap
