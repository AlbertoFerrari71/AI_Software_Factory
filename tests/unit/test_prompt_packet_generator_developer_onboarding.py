from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_developer_onboarding_doc_exists() -> None:
    assert DOC.exists()


def test_developer_onboarding_contains_required_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "AI Software Factory",
        "Codex Alchemy Method",
        "local-first",
        "generate_task_packet.py",
        "generate_task_packet.ps1",
        "validate_task_packet.py",
        "smoke_prompt_packet_release.ps1",
        "Lite Mode",
        "Strict Mode",
        "Verification Gate",
        "Release Smoke Workflow",
        "Lifecycle Checklist",
        "Codex",
        "Alberto",
        "commit",
        "push",
        "PR",
        "merge",
        "main",
        "git status --short",
        "gh pr checks --watch",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_developer_onboarding_clarifies_codex_boundaries() -> None:
    content = read(DOC)

    assert "Codex non fa commit" in content
    assert "Codex non fa push" in content
    assert "Codex non apre PR" in content
    assert "Codex non fa merge" in content


def test_developer_onboarding_report_is_not_main_merge() -> None:
    content = read(DOC)

    assert "report Codex non equivale a merge su `main`" in content


def test_developer_onboarding_has_errors_and_troubleshooting() -> None:
    content = read(DOC).casefold()

    assert "errori comuni" in content
    assert "troubleshooting" in content
    assert "branch locale" in content
    assert "main non aggiornato" in content


def test_developer_onboarding_links_lifecycle_checklist() -> None:
    content = read(DOC)

    assert "docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md" in content


def test_step_210_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 210 - Prompt Packet Generator Developer Onboarding" in changelog
    assert "DEC-041 - Prompt Packet Generator Developer Onboarding" in decisions
    assert "STEP 220" in roadmap
    assert "Project Workflow Index" in roadmap
