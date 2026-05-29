from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "prompt_packet_lifecycle_checklist.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_lifecycle_checklist_files_exist() -> None:
    assert DOC.exists()
    assert TEMPLATE.exists()


def test_lifecycle_document_contains_operational_keywords() -> None:
    content = read(DOC)

    required_fragments = [
        "Lite",
        "Strict",
        "Verification Gate",
        "Codex",
        "commit",
        "push",
        "PR",
        "merge",
        "main",
        "git status --short",
        "git diff --check",
        "python -m pytest",
        "check_soft_guardrails.ps1",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_lifecycle_template_has_markdown_checkboxes() -> None:
    content = read(TEMPLATE)

    assert "- [ ]" in content
    assert content.count("- [ ]") >= 20


def test_lifecycle_template_distinguishes_codex_and_alberto_operations() -> None:
    content = read(TEMPLATE)

    assert "Codex non fa commit" in content
    assert "Codex non fa push" in content
    assert "Queste azioni sono di Alberto, non di Codex" in content
    assert "Alberto ha eseguito `git commit" in content
    assert "Alberto ha eseguito `git push" in content


def test_lifecycle_document_has_troubleshooting_and_antipatterns() -> None:
    content = read(DOC).casefold()

    assert "troubleshooting" in content
    assert "anti-pattern" in content
    assert "reset --hard" in content
    assert "senza diagnosi" in content


def test_lifecycle_document_does_not_equate_codex_report_with_main_merge() -> None:
    content = read(DOC)

    assert "Il report Codex non equivale a merge su `main`" in content
    assert "step successivo" in content


def test_step_200_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 200 - Prompt Packet Lifecycle Checklist" in changelog
    assert "DEC-040 - Prompt Packet Lifecycle Checklist" in decisions
    assert "STEP 210" in roadmap
    assert "Prompt Packet Generator Developer Onboarding" in roadmap
