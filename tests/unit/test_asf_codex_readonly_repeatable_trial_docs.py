from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK_DOC = ROOT / "docs" / "59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md"
RESULTS_DOC = ROOT / "docs" / "60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(content: str, fragment: str) -> None:
    assert fragment.casefold() in content.casefold()


def test_repeatable_trial_docs_exist() -> None:
    assert PACK_DOC.exists()
    assert RESULTS_DOC.exists()


def test_repeatable_trial_pack_doc_covers_required_topics() -> None:
    content = read(PACK_DOC)

    required_fragments = [
        "Repeatable Trial Pack",
        "read-only",
        "prepare-only",
        "run-readonly-if-safe",
        "approval gate GO",
        "target CLEAN",
        "Codex non disponibile",
        "output incompleto",
        "stderr",
        "workspace-write non autorizzato",
        "trial comparison",
    ]
    for fragment in required_fragments:
        assert_contains(content, fragment)


def test_repeatable_trial_results_doc_covers_required_topics() -> None:
    content = read(RESULTS_DOC)

    required_fragments = [
        "STEP 450",
        "trial eseguiti",
        "execute-readonly",
        "CODEX_NOT_AVAILABLE",
        "target CLEAN",
        "safety gate",
        "output incompleto",
        "stderr",
        "workspace-write non autorizzato",
        "conclusione",
        "460",
    ]
    for fragment in required_fragments:
        assert_contains(content, fragment)


def test_health_check_includes_repeatable_trial_pack_files() -> None:
    health = read(ROOT / "scripts" / "check_workflow_health.py")

    required_fragments = [
        "docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md",
        "docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md",
        "scripts/asf_codex_readonly_repeatable_trial.py",
        "scripts/asf_codex_readonly_trial_compare.py",
        "templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md",
        "templates/codex_tasks/asf_codex_readonly_trial_compare_template.md",
    ]
    for fragment in required_fragments:
        assert fragment in health


def test_index_and_status_docs_reference_repeatable_trial_pack() -> None:
    combined = "\n".join(
        read(ROOT / relative_path)
        for relative_path in [
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/35_WORKFLOW_HEALTH_CHECK.md",
            "docs/39_WORKFLOW_STATUS_DASHBOARD.md",
        ]
    )

    assert "docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md" in combined
    assert "docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md" in combined
    assert "ASF Codex Read-Only Repeatable Trial Pack" in combined

