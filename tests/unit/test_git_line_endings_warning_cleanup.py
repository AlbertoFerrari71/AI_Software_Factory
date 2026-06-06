from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "72_ASF_GIT_LINE_ENDINGS_WARNING_CLEANUP.md"
ATTRIBUTES = ROOT / ".gitattributes"
TARGET = "templates/test_plans/test_plan_template.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_line_endings_policy_files_exist() -> None:
    assert ATTRIBUTES.exists()
    assert DOC.exists()


def test_gitattributes_defines_prudent_line_endings_policy() -> None:
    content = read(ATTRIBUTES)

    for fragment in [
        "* text=auto",
        "*.md text eol=lf",
        "*.py text eol=lf",
        "*.yml text eol=lf",
        "*.yaml text eol=lf",
        "*.json text eol=lf",
        "*.txt text eol=lf",
        f"{TARGET} text eol=lf",
        "*.bat text eol=crlf",
        "*.cmd text eol=crlf",
        "*.ps1 text eol=crlf",
    ]:
        assert fragment in content


def test_cleanup_document_explains_target_and_non_blocking_warning_rule() -> None:
    content = read(DOC)

    for fragment in [
        "STEP 548",
        TARGET,
        "core.autocrlf",
        "core.eol",
        ".gitattributes",
        "i/lf",
        "w/lf",
        "LF/CRLF warnings are controlled warnings",
        "git --no-pager diff --check",
        "python -m pytest",
        "python scripts/check_workflow_health.py",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\verify.ps1",
    ]:
        assert fragment in content


def test_cleanup_document_rejects_blind_mass_renormalization() -> None:
    content = read(DOC)

    assert "No broad normalization was executed" in content
    assert "git add --renormalize --dry-run ." in content
    assert "If it reports more than 10 files, stop" in content
    assert "Do not run this blindly" in content
    assert "git add --renormalize ." in content
