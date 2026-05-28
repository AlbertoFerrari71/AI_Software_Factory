from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_prompt_packet_hardening_document_exists_and_contains_core_concepts() -> None:
    path = ROOT / "docs" / "25_PROMPT_PACKET_HARDENING.md"
    assert path.exists()

    content = read_text("docs/25_PROMPT_PACKET_HARDENING.md")
    required_fragments = [
        "Prompt Packet Hardening",
        "Forbidden actions",
        "Allowed scope",
        "Forbidden scope",
        "Verification Gate",
        "Documentation Sync",
        "Soft Protection",
        "Final Codex report",
        "STEP 140",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_core_workflow_documents_reference_prompt_packet_hardening() -> None:
    codex_workflow = read_text("docs/08_CODEX_WORKFLOW.md")
    workflow = read_text("docs/04_WORKFLOW.md")

    assert "docs/25_PROMPT_PACKET_HARDENING.md" in codex_workflow
    assert "Prompt Packet Hardening" in workflow


def test_codex_templates_include_hardened_scope_and_report_terms() -> None:
    template_paths = [
        ROOT / "templates" / "codex_tasks" / "codex_task_packet_template.md",
        *sorted((ROOT / "templates" / "prompts").glob("codex_*.md")),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in template_paths)
    lower_combined = combined.lower()

    required_fragments = [
        "Forbidden actions",
        "Verification Gate",
        "Documentation Sync",
        "Step eseguito",
        "Tempo impiegato",
    ]
    for fragment in required_fragments:
        assert fragment in combined

    assert "allowed scope" in lower_combined
    assert "forbidden scope" in lower_combined


def test_step_130_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 130 - Prompt Packet Hardening" in changelog
    assert "DEC-033 - Prompt Packet Hardening" in decisions
    assert "STEP 140" in roadmap
    assert "Prompt Packet Validation Lite" in roadmap
