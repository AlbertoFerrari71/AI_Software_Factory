from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_verification_gate_document_and_script_exist() -> None:
    required_paths = [
        "docs/20_VERIFICATION_GATE.md",
        "scripts/verify.ps1",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert missing == []


def test_verification_gate_document_contains_required_topics() -> None:
    content = read_text("docs/20_VERIFICATION_GATE.md")
    required_topics = [
        "Local verification",
        "Git verification",
        "Policy and template verification",
        "Pull request verification",
        "Merge verification",
        "Failure handling",
        "Standard output",
        "Manual checklist",
        "Future hardening",
        "branch protection",
    ]
    for topic in required_topics:
        assert topic in content


def test_verify_script_runs_expected_local_checks() -> None:
    content = read_text("scripts/verify.ps1")
    required_fragments = [
        "Set-StrictMode -Version Latest",
        '$ErrorActionPreference = "Stop"',
        "python --version",
        "python -m pytest --version",
        "python -m pytest",
        "git diff --check",
        "git status --short",
        "Verification Gate PASSED",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_pull_request_template_contains_verification_gate_section() -> None:
    content = read_text(".github/pull_request_template.md")
    required_fragments = [
        "## Verification Gate",
        "Ho eseguito i test locali",
        "git diff --check",
        "git status --short",
        "La CI GitHub e' passata",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_ci_contains_verification_gate_commands() -> None:
    content = read_text(".github/workflows/ci.yml")
    required_fragments = [
        "pull_request:",
        "push:",
        "contents: read",
        "ubuntu-latest",
        "actions/checkout@v4",
        "actions/setup-python@v5",
        'python-version: "3.13"',
        'python -m pip install -e ".[dev]"',
        "python -m pytest",
        "git diff --check",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_core_documents_reference_verification_gate() -> None:
    required_documents = [
        "docs/04_WORKFLOW.md",
        "docs/08_CODEX_WORKFLOW.md",
        "docs/15_GITHUB_WORKFLOW.md",
    ]
    for path in required_documents:
        content = read_text(path)
        assert "Verification Gate" in content
        assert "docs/20_VERIFICATION_GATE.md" in content
