from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_branch_protection_implementation_files_exist() -> None:
    required_paths = [
        "docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md",
        "scripts/github/detect_required_checks.ps1",
        "scripts/github/apply_branch_protection.ps1",
        "scripts/github/verify_branch_protection.ps1",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert missing == []


def test_branch_protection_implementation_document_contains_core_concepts() -> None:
    content = read_text("docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md")
    required_fragments = [
        "Branch Protection Implementation",
        "DryRun",
        "RequiredCheckName",
        "apply_branch_protection.ps1",
        "verify_branch_protection.ps1",
        "STEP 110",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_apply_script_is_dry_run_by_default_and_contains_required_payload_terms() -> None:
    content = read_text("scripts/github/apply_branch_protection.ps1")
    required_fragments = [
        "RequiredCheckName",
        "[switch] $Apply",
        "gh api",
        "allow_force_pushes",
        "allow_deletions",
        "required_status_checks",
        "DryRun only",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "allow_force_pushes = $false" in content
    assert "allow_deletions = $false" in content


def test_verify_script_is_read_only() -> None:
    content = read_text("scripts/github/verify_branch_protection.ps1")
    upper_content = content.upper()

    assert "gh api" in content
    assert "branches/$Branch/protection" in content
    assert "--method PUT" not in content
    assert "--method PATCH" not in content
    assert "--method DELETE" not in content
    assert "REMOVE-ITEM" not in upper_content


def test_step_100_changelog_and_decision_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")

    assert "STEP 100 - Branch Protection Implementation" in changelog
    assert "DEC-030 - Branch protection scripts" in decisions
