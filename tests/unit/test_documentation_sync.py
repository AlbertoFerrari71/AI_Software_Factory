from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_documentation_sync_document_exists() -> None:
    assert (ROOT / "docs" / "21_DOCUMENTATION_SYNC.md").exists()


def test_documentation_sync_document_contains_core_concepts() -> None:
    content = read_text("docs/21_DOCUMENTATION_SYNC.md")
    uppercase_content = content.upper()

    required_fragments = [
        "Documentation Sync",
        "Verification Gate",
        "Codex final report",
    ]
    for fragment in required_fragments:
        assert fragment in content

    for keyword in ["CHANGELOG", "ROADMAP", "DECISIONS"]:
        assert keyword in uppercase_content


def test_verification_gate_references_documentation_sync() -> None:
    content = read_text("docs/20_VERIFICATION_GATE.md")
    assert "Documentation Sync" in content
    assert "docs/21_DOCUMENTATION_SYNC.md" in content


def test_workflow_documents_reference_documentation_sync() -> None:
    workflow = read_text("docs/04_WORKFLOW.md")
    codex = read_text("docs/08_CODEX_WORKFLOW.md")

    assert "Documentation Sync" in workflow
    assert "docs/21_DOCUMENTATION_SYNC.md" in workflow
    assert "docs/21_DOCUMENTATION_SYNC.md" in codex


def test_step_080_changelog_and_decision_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")

    assert "STEP 080 - Documentation Sync" in changelog
    assert "DEC-028 - Documentation Sync" in decisions


def test_pull_request_template_mentions_documentation_sync_check() -> None:
    content = read_text(".github/pull_request_template.md")
    assert "CHANGELOG.md" in content
    assert "docs/10_ROADMAP.md" in content
    assert "docs/11_DECISIONS.md" in content
