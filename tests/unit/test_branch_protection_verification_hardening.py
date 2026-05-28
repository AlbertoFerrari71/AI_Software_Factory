from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_branch_protection_implementation_documents_plan_limitation() -> None:
    content = read_text("docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md")
    lower_content = content.lower()

    required_fragments = [
        "Verification Gate",
        "HTTP 403",
        "GitHub Pro",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "soft protection" in lower_content


def test_branch_protection_policy_distinguishes_hard_and_soft_protection() -> None:
    content = read_text("docs/22_BRANCH_PROTECTION_POLICY.md").lower()

    assert "hard protection" in content
    assert "soft protection" in content


def test_verify_script_handles_plan_limited_http_403() -> None:
    content = read_text("scripts/github/verify_branch_protection.ps1")

    required_fragments = [
        "HTTP 403",
        "GitHub Pro",
        "soft protection",
        "exit 2",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_apply_script_warns_about_plan_limited_branch_protection() -> None:
    content = read_text("scripts/github/apply_branch_protection.ps1")

    required_fragments = [
        "HTTP 403",
        "verify_branch_protection.ps1",
        "soft protection",
        "plan",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_110_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 110 - Branch Protection Verification and Hardening" in changelog
    assert "DEC-031 - Branch protection plan limit" in decisions
    assert "STEP 120" in roadmap
    assert "Soft Protection Guardrails" in roadmap
