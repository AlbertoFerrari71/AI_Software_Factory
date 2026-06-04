from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRIAL_DOC = ROOT / "docs" / "55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md"
RESULTS_DOC = ROOT / "docs" / "56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_first_manual_trial_docs_exist() -> None:
    assert TRIAL_DOC.exists()
    assert RESULTS_DOC.exists()


def test_first_manual_trial_doc_covers_required_topics() -> None:
    content = read(TRIAL_DOC)

    required_fragments = [
        "First Manual Trial",
        "read-only",
        "AI_Software_Factory",
        "Human Approval Gate",
        "preview",
        "execute-readonly",
        "result capture",
        "safety gate",
        "workspace-write",
        "Codex non deve modificare repo target",
        "commit, push, PR e merge non sono automatici",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_first_manual_trial_results_doc_covers_required_topics() -> None:
    content = read(RESULTS_DOC)

    required_fragments = [
        "Target",
        "Prepare runner",
        "Approval gate",
        "Preview",
        "Execute-readonly",
        "Result capture",
        "Safety gate",
        "Classificazione finale",
        "non e' fallimento",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_project_workflow_index_links_first_manual_trial() -> None:
    content = read(ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md")

    assert "docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md" in content
    assert "docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md" in content
    assert "ASF Codex Read-Only First Manual Trial" in content


def test_health_or_status_docs_reference_first_manual_trial_docs() -> None:
    health = read(ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md")
    status = read(ROOT / "docs" / "39_WORKFLOW_STATUS_DASHBOARD.md")
    combined = health + "\n" + status

    assert "docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md" in combined
    assert "docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md" in combined
