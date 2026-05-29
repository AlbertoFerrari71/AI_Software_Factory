from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "41_EXISTING_PROJECT_PILOT_ONBOARDING.md"
INTAKE_TEMPLATE = ROOT / "templates" / "codex_tasks" / "existing_project_intake_template.md"
FIRST_PACKET_TEMPLATE = ROOT / "templates" / "codex_tasks" / "first_pilot_step_packet_template.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_existing_project_pilot_onboarding_files_exist() -> None:
    assert DOC.exists()
    assert INTAKE_TEMPLATE.exists()
    assert FIRST_PACKET_TEMPLATE.exists()


def test_existing_project_pilot_onboarding_document_contains_required_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "Existing Project Pilot Onboarding",
        "Project Intake",
        "progetto già a metà sviluppo",
        "GO",
        "WARNING",
        "NO-GO",
        "branch dedicato",
        "working tree",
        "dati sensibili",
        "secret",
        "refactor massivo",
        "primo step pilota",
        "First Existing Project Pilot",
        "Release Readiness",
        "Workflow Command Cookbook",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_existing_project_intake_template_contains_required_fields() -> None:
    content = read(INTAKE_TEMPLATE)

    required_fragments = [
        "Nome progetto",
        "Repository",
        "Cartella locale",
        "Branch principale",
        "Branch pilota proposto",
        "Stato Git",
        "Test disponibili",
        "Dati sensibili",
        "GO/WARNING/NO-GO",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_first_pilot_step_packet_template_contains_required_fields() -> None:
    content = read(FIRST_PACKET_TEMPLATE)

    required_fragments = [
        "branch pilota",
        "obiettivo piccolo e reversibile",
        "scope incluso",
        "scope escluso",
        "forbidden actions",
        "dati sensibili da non toccare",
        "nessun commit/push/PR/merge",
        "Step Closure Report",
    ]
    for fragment in required_fragments:
        assert fragment.casefold() in content.casefold()


def test_existing_project_pilot_onboarding_does_not_modify_external_repositories() -> None:
    content = read(DOC).casefold()

    assert "non permette" in content
    assert "modificare repository esterne" in content


def test_first_pilot_is_not_architectural_refactor() -> None:
    content = read(DOC).casefold()

    assert "il primo pilot non deve essere un refactor architetturale" in content
    assert "refactor architetturale" in content


def test_existing_project_pilot_onboarding_is_linked_from_core_workflow_docs() -> None:
    linked_docs = [
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md",
        ROOT / "docs" / "38_WORKFLOW_COMMAND_COOKBOOK.md",
        ROOT / "docs" / "40_RELEASE_READINESS.md",
    ]

    for path in linked_docs:
        assert "docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md" in read(path)


def test_workflow_health_check_includes_existing_project_pilot_files() -> None:
    content = read(ROOT / "scripts" / "check_workflow_health.py")

    assert "docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md" in content
    assert "templates/codex_tasks/existing_project_intake_template.md" in content
    assert "templates/codex_tasks/first_pilot_step_packet_template.md" in content


def test_step_290_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 290 - Existing Project Pilot Onboarding" in changelog
    assert "DEC-049 - Existing Project Pilot Onboarding" in decisions
    assert "STEP 300" in roadmap
    assert "First Existing Project Pilot" in roadmap
