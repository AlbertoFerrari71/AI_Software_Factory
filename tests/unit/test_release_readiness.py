from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "40_RELEASE_READINESS.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "release_readiness_checklist.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_release_readiness_files_exist() -> None:
    assert DOC.exists()
    assert TEMPLATE.exists()


def test_release_readiness_document_contains_required_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "Release Readiness",
        "Beta operativa local-first",
        "Pilot ready",
        "Stable internal release",
        "Public/SaaS ready",
        "GO",
        "WARNING",
        "NO-GO",
        "Project Intake",
        "progetto e' gia' a meta' sviluppo",
        "progetto già a metà sviluppo",
        "branch dedicato",
        "working tree pulita",
        "test",
        "Verification Gate",
        "Workflow Health Check",
        "Workflow Status Dashboard",
        "Step Closure Report",
        "Workflow Command Cookbook",
        "branch protection reale non disponibile",
        "PR checks non disponibili",
        "LF/CRLF",
        "refactor massivo",
        "dati sensibili",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_release_readiness_document_links_core_documents() -> None:
    content = read(DOC)

    required_links = [
        "docs/34_PROJECT_WORKFLOW_INDEX.md",
        "docs/35_WORKFLOW_HEALTH_CHECK.md",
        "docs/36_WORKFLOW_QUICK_REFERENCE.md",
        "docs/37_STEP_CLOSURE_REPORT.md",
        "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
        "docs/39_WORKFLOW_STATUS_DASHBOARD.md",
    ]
    for link in required_links:
        assert link in content


def test_release_readiness_template_is_checkable_and_compilable() -> None:
    content = read(TEMPLATE)

    assert "- [ ]" in content
    required_fragments = [
        "Nome progetto candidato",
        "Repository",
        "Branch principale",
        "Stato Git",
        "Test disponibili",
        "Rischi noti",
        "Dati sensibili",
        "Primo step pilota proposto",
        "Decisione finale",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_release_readiness_avoids_absolute_public_release_claims() -> None:
    content = read(DOC)

    assert "Non e' classificata come **Public/SaaS ready**" in content
    assert "pronto come prodotto pubblico" in content


def test_release_readiness_is_linked_from_workflow_docs() -> None:
    linked_docs = [
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md",
        ROOT / "docs" / "36_WORKFLOW_QUICK_REFERENCE.md",
        ROOT / "docs" / "38_WORKFLOW_COMMAND_COOKBOOK.md",
        ROOT / "docs" / "39_WORKFLOW_STATUS_DASHBOARD.md",
    ]

    for path in linked_docs:
        assert "docs/40_RELEASE_READINESS.md" in read(path)


def test_workflow_health_check_includes_release_readiness_files() -> None:
    content = read(ROOT / "scripts" / "check_workflow_health.py")

    assert "docs/40_RELEASE_READINESS.md" in content
    assert "templates/codex_tasks/release_readiness_checklist.md" in content


def test_step_280_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 280 - Release Readiness" in changelog
    assert "DEC-048 - Release Readiness" in decisions
    assert "STEP 290" in roadmap
    assert "Existing Project Pilot Onboarding" in roadmap
