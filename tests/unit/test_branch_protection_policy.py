from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_branch_protection_policy_document_exists() -> None:
    assert (ROOT / "docs" / "22_BRANCH_PROTECTION_POLICY.md").exists()


def test_branch_protection_policy_document_contains_core_concepts() -> None:
    content = read_text("docs/22_BRANCH_PROTECTION_POLICY.md")
    lower_content = content.lower()

    required_fragments = [
        "Branch Protection Policy",
        "main",
        "pull request",
        "force push",
        "deletion",
        "rulesets",
        "STEP 100",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "status checks" in lower_content or "ci" in lower_content


def test_github_workflow_references_branch_protection_policy() -> None:
    content = read_text("docs/15_GITHUB_WORKFLOW.md")
    assert "Branch Protection Policy" in content
    assert "docs/22_BRANCH_PROTECTION_POLICY.md" in content


def test_verification_gate_references_branch_protection_policy() -> None:
    content = read_text("docs/20_VERIFICATION_GATE.md")
    assert "Branch Protection Policy" in content
    assert "docs/22_BRANCH_PROTECTION_POLICY.md" in content


def test_step_090_changelog_and_decision_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")

    assert "STEP 090 - Branch Protection Policy" in changelog
    assert "DEC-029 - Branch Protection Policy" in decisions
