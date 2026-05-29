from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "37_STEP_CLOSURE_REPORT.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "step_closure_report_template.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_closure_report_files_exist() -> None:
    assert DOC.exists()
    assert TEMPLATE.exists()


def test_step_closure_report_doc_contains_required_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "Step Closure Report",
        "report Codex non equivale a merge su main",
        "Completato localmente",
        "Pushato",
        "PR creata",
        "Mergiato su main",
        "Chiuso e verificato su main",
        "Workflow Health Check",
        "Verification Gate",
        "git status --short",
        "gh pr checks --watch",
        "no checks reported",
        "CRLF/LF",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_closure_report_template_contains_required_fields() -> None:
    content = read(TEMPLATE)

    required_fragments = [
        "Step",
        "Stato",
        "Branch",
        "Commit step",
        "PR",
        "Merge commit",
        "Main aggiornato",
        "Test",
        "Workflow Health Check",
        "Verification Gate",
        "Working tree",
        "Prossimo step",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_closure_report_links_workflow_references() -> None:
    content = read(DOC)

    assert "docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md" in content
    assert "docs/36_WORKFLOW_QUICK_REFERENCE.md" in content


def test_step_closure_report_clarifies_codex_boundaries() -> None:
    content = read(DOC)

    assert "Codex non deve fare commit" in content
    assert "push" in content
    assert "PR" in content
    assert "merge" in content


def test_step_closure_report_records_unavailable_pr_checks_as_attention() -> None:
    content = read(DOC).casefold()

    assert "attenzione da verificare" in content
    assert "registrare nel report finale" in content


def test_step_250_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 250 - Step Closure Report" in changelog
    assert "DEC-045 - Step Closure Report" in decisions
    assert "STEP 260" in roadmap
    assert "Workflow Command Cookbook" in roadmap
