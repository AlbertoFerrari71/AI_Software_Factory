from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_project_workflow_index_exists() -> None:
    assert DOC.exists()


def test_project_workflow_index_contains_required_concepts() -> None:
    content = read(DOC)

    required_fragments = [
        "AI Software Factory",
        "Project Workflow Index",
        "Prompt Packet Generator",
        "Lite Mode",
        "Strict Mode",
        "Verification Gate",
        "Documentation Sync",
        "Soft Protection Guardrails",
        "Release Smoke Workflow",
        "Lifecycle Checklist",
        "Developer Onboarding",
        "Codex",
        "Alberto",
        "PR",
        "merge",
        "main",
        "git status --short",
        "git diff --check",
        "gh pr checks --watch",
        "fetch --all --prune",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_project_workflow_index_links_core_documents() -> None:
    content = read(DOC)

    required_links = [
        "docs/19_PROMPT_PACKET_GENERATOR.md",
        "docs/20_VERIFICATION_GATE.md",
        "docs/21_DOCUMENTATION_SYNC.md",
        "docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md",
        "docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md",
        "docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md",
    ]
    for link in required_links:
        assert link in content


def test_project_workflow_index_cites_main_scripts() -> None:
    content = read(DOC)

    scripts = [
        "scripts/generate_task_packet.py",
        "scripts/generate_task_packet.ps1",
        "scripts/validate_task_packet.py",
        "scripts/smoke_prompt_packet_release.ps1",
        "scripts/verify.ps1",
        "scripts/git/check_soft_guardrails.ps1",
    ]
    for script in scripts:
        assert script in content


def test_project_workflow_index_has_troubleshooting_and_antipatterns() -> None:
    content = read(DOC).casefold()

    assert "troubleshooting" in content
    assert "anti-pattern" in content
    assert "branch locale" in content
    assert "pr non creata" in content


def test_project_workflow_index_clarifies_codex_boundaries() -> None:
    content = read(DOC)

    assert "Codex non deve fare commit" in content
    assert "push" in content
    assert "PR" in content
    assert "merge" in content


def test_project_workflow_index_report_is_not_main_merge() -> None:
    content = read(DOC)

    assert "Il report Codex non equivale a merge su `main`" in content


def test_step_220_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 220 - Project Workflow Index" in changelog
    assert "DEC-042 - Project Workflow Index" in decisions
    assert "STEP 230" in roadmap
    assert "Workflow Health Check" in roadmap
