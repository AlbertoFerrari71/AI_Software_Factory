from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_soft_protection_guardrail_files_exist() -> None:
    required_paths = [
        ".githooks/pre-commit",
        ".githooks/pre-push",
        "scripts/git/install_soft_guardrails.ps1",
        "scripts/git/check_soft_guardrails.ps1",
        "docs/24_SOFT_PROTECTION_GUARDRAILS.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert missing == []


def test_pre_commit_blocks_main_with_explicit_bypass() -> None:
    content = read_text(".githooks/pre-commit")

    required_fragments = [
        "main",
        "ASF_ALLOW_MAIN_BYPASS",
        "exit 1",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_pre_push_blocks_main_push_with_required_check_reference() -> None:
    content = read_text(".githooks/pre-push")

    required_fragments = [
        "refs/heads/main",
        "ASF_ALLOW_MAIN_BYPASS",
        "Verification Gate",
        "exit 1",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_install_script_is_explicit_and_dry_run_capable() -> None:
    content = read_text("scripts/git/install_soft_guardrails.ps1")

    required_fragments = [
        "core.hooksPath",
        ".githooks",
        "DryRun",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_check_script_reports_installation_state_without_modifying_git() -> None:
    content = read_text("scripts/git/check_soft_guardrails.ps1")

    required_fragments = [
        "core.hooksPath",
        "exit 2",
        "pre-commit",
        "pre-push",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "git config core.hooksPath" not in content


def test_soft_protection_document_contains_core_concepts() -> None:
    content = read_text("docs/24_SOFT_PROTECTION_GUARDRAILS.md")
    lower_content = content.lower()

    required_fragments = [
        "Soft Protection Guardrails",
        "ASF_ALLOW_MAIN_BYPASS",
        "Verification Gate",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "hard protection" in lower_content
    assert "soft protection" in lower_content


def test_step_120_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 120 - Soft Protection Guardrails" in changelog
    assert "DEC-032 - Soft protection guardrails" in decisions
    assert "STEP 130" in roadmap
    assert "Prompt Packet Hardening" in roadmap
