from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRIAL_DOC = ROOT / "docs" / "57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md"
RESULTS_DOC = ROOT / "docs" / "58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(content: str, fragment: str) -> None:
    assert fragment.casefold() in content.casefold()


def test_clean_target_trial_docs_exist() -> None:
    assert TRIAL_DOC.exists()
    assert RESULTS_DOC.exists()


def test_clean_target_trial_doc_covers_required_topics() -> None:
    content = read(TRIAL_DOC)

    required_fragments = [
        "Clean Target Trial",
        "read-only",
        "repo temporanea",
        "tmp/",
        "Human Approval Gate",
        "approval gate GO",
        "execute-readonly",
        "codex",
        "working tree `CLEAN`",
        "workspace-write non autorizzato",
        "danger-full-access non autorizzato",
        "nessun commit/push/PR/merge automatico",
        "target esterni non modificati",
    ]
    for fragment in required_fragments:
        assert_contains(content, fragment)


def test_clean_target_trial_results_doc_covers_required_topics() -> None:
    content = read(RESULTS_DOC)

    required_fragments = [
        "Target temporaneo",
        "Approval gate",
        "Preview",
        "Execute-readonly",
        "Result capture",
        "Safety gate",
        "Working tree",
        "Classificazione finale",
        "prossimo step",
    ]
    for fragment in required_fragments:
        assert_contains(content, fragment)

    assert (
        "non e' fallimento se ambiente non disponibile" in content
        or "eseguito read-only" in content
    )


def test_project_workflow_index_links_clean_target_trial() -> None:
    content = read(ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md")

    assert "docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md" in content
    assert "docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md" in content
    assert "ASF Codex Read-Only Clean Target Trial" in content


def test_health_or_status_docs_reference_clean_target_trial_docs() -> None:
    health = read(ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md")
    status = read(ROOT / "docs" / "39_WORKFLOW_STATUS_DASHBOARD.md")
    combined = health + "\n" + status

    assert "docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md" in combined
    assert "docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md" in combined
