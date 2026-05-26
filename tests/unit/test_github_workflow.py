from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_github_workflow_document_contains_required_sections() -> None:
    content = read_text("docs/15_GITHUB_WORKFLOW.md")
    required_sections = [
        "Issue policy",
        "Branch naming policy",
        "Commit policy",
        "Pull Request policy",
        "Branch protection checklist",
        "Merge policy",
        "Release e tag policy",
    ]
    for section in required_sections:
        assert section in content


def test_github_templates_are_present() -> None:
    required_paths = [
        ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/research.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/workflows/ci.yml",
    ]
    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_pull_request_template_contains_safety_and_rollback() -> None:
    content = read_text(".github/pull_request_template.md")
    assert "Safety level" in content
    assert "Test eseguiti" in content
    assert "Rischi residui" in content
    assert "Rollback" in content


def test_issue_templates_contain_risk_level() -> None:
    for path in [
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/research.yml",
    ]:
        content = read_text(path)
        assert "Livello massimo di rischio" in content


def test_step_050_checklist_exists() -> None:
    assert (ROOT / "docs/checklists/050_GITHUB_WORKFLOW_CHECKLIST.md").exists()
