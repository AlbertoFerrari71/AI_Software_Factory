from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "36_WORKFLOW_QUICK_REFERENCE.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_quick_reference_exists() -> None:
    assert DOC.exists()


def test_workflow_quick_reference_contains_required_commands_and_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "Workflow Quick Reference",
        "AI Software Factory",
        "generate_task_packet.py",
        "validate_task_packet.py",
        "--strict",
        "smoke_prompt_packet_release.ps1",
        "check_workflow_health.py",
        "verify.ps1",
        "check_soft_guardrails.ps1",
        "git status --short",
        "git --no-pager diff --check",
        "python -m pytest",
        "gh pr checks --watch",
        "gh pr merge",
        "main",
        "Codex",
        "Alberto",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_workflow_quick_reference_codex_boundaries_are_explicit() -> None:
    content = read(DOC)

    assert "Codex non fa commit" in content
    assert "Codex non fa push" in content
    assert "Codex non apre PR" in content
    assert "Codex non fa merge" in content


def test_workflow_quick_reference_report_is_not_main_merge() -> None:
    content = read(DOC)

    assert "report Codex non equivale a merge" in content


def test_workflow_quick_reference_links_deeper_documents() -> None:
    content = read(DOC)

    required_links = [
        "docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md",
        "docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md",
        "docs/34_PROJECT_WORKFLOW_INDEX.md",
        "docs/35_WORKFLOW_HEALTH_CHECK.md",
    ]
    for link in required_links:
        assert link in content


def test_workflow_quick_reference_has_fast_errors_section() -> None:
    content = read(DOC)

    assert "Errori rapidi da evitare" in content


def test_workflow_quick_reference_marks_git_operations_as_supervised() -> None:
    content = read(DOC).casefold()

    assert "presidiati" in content
    assert "alberto" in content
    assert "non automazione" in content
    assert "non uno script automatico" in content


def test_step_240_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 240 - Workflow Quick Reference" in changelog
    assert "DEC-044 - Workflow Quick Reference" in decisions
    assert "STEP 250" in roadmap
    assert "Step Closure Report" in roadmap
