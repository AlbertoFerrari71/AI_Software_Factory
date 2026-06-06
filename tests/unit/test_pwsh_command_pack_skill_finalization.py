from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = "docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md"
README = "templates/pwsh_command_pack/README.md"
SKILL_DRAFT = "templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md"
BOOTSTRAP_TEMPLATE = "templates/pwsh_command_pack/safe_bootstrap_template.ps1"
SCRIPT_TEMPLATE = "templates/pwsh_command_pack/safe_command_pack_script_template.ps1"
STEP_540_TEMPLATE = "templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def parse_check(relative_path: str) -> subprocess.CompletedProcess[str]:
    command = (
        "[scriptblock]::Create((Get-Content -Raw "
        f"'{relative_path}')) | Out-Null"
    )
    return subprocess.run(
        ["pwsh", "-NoProfile", "-Command", command],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_step_545_files_exist() -> None:
    for relative_path in [
        DOC,
        README,
        SKILL_DRAFT,
        BOOTSTRAP_TEMPLATE,
        SCRIPT_TEMPLATE,
    ]:
        assert (ROOT / relative_path).exists(), relative_path


def test_skill_finalization_documents_canonical_standard() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            DOC,
            README,
            SKILL_DRAFT,
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
        ]
    )

    for fragment in [
        "Safe Bootstrap PowerShell Command Pack",
        "& { ... }",
        '$ErrorActionPreference = "Stop"',
        "$PSNativeCommandUseErrorActionPreference = $false",
        "[scriptblock]::Create($ScriptText) | Out-Null",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile",
        "ArgList",
        "$Args",
        "git status --porcelain=v1 --untracked-files=all",
        "AGENTS.md",
        "GENTS.md",
        "templates/pwsh_command_pack/",
        "git add -- @AllowedPaths",
        "PR-first",
        "main...origin/main [ahead N]",
        "NNNN-Richiesta_Generazione_<name>.txt",
        "LAST-Output_Compatto.docx",
        "DOCX is best-effort",
        "LF/CRLF",
        "STEP 536 introduced",
        "STEP 540 validated",
    ]:
        assert fragment in combined


def test_templates_use_arglist_and_porcelain_git_status() -> None:
    bootstrap = read(BOOTSTRAP_TEMPLATE)
    script = read(SCRIPT_TEMPLATE)

    assert "& {" in bootstrap
    assert bootstrap.rstrip().endswith('Write-Host ";"')
    assert "pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile" in bootstrap
    assert "ArgList" in script
    assert "git status --porcelain=v1 --untracked-files=all" in script
    assert '--porcelain=v1", "--untracked-files=all' in script
    assert "Test-GitScope" in script
    assert "Set-Clipboard" in script


def test_templates_avoid_forbidden_patterns() -> None:
    combined = "\n".join([read(BOOTSTRAP_TEMPLATE), read(SCRIPT_TEMPLATE), read(STEP_540_TEMPLATE)])
    lowered = combined.casefold()

    for forbidden in [
        "@'",
        '@"',
        " finally",
        " git push origin main",
    ]:
        assert forbidden not in lowered

    assert not re.search(r"param\s*\([^)]*\$Args\b", combined, flags=re.IGNORECASE | re.DOTALL)
    assert "[string[]] $Args" not in combined


def test_skill_finalization_tracking_documents_are_updated() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "AGENTS.md",
            "README.md",
            "CHANGELOG.md",
            "docs/08_CODEX_WORKFLOW.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
            "docs/21_DOCUMENTATION_SYNC.md",
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/35_WORKFLOW_HEALTH_CHECK.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "scripts/check_workflow_health.py",
        ]
    )

    for fragment in [
        "STEP 545 - PowerShell Command Pack Skill Finalization",
        "DEC-066 - PowerShell command pack skill finalization",
        DOC,
        README,
        SKILL_DRAFT,
        "ArgList",
        "git status --porcelain=v1 --untracked-files=all",
        "550) OpenAI API Adapter First Authorized Live Run",
    ]:
        assert fragment in combined


def test_pwsh_templates_parse() -> None:
    for relative_path in [
        BOOTSTRAP_TEMPLATE,
        SCRIPT_TEMPLATE,
        STEP_540_TEMPLATE,
    ]:
        result = parse_check(relative_path)
        assert result.returncode == 0, result.stdout + result.stderr
