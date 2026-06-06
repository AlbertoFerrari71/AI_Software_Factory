from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_TEMPLATE = "templates/pwsh_command_pack/safe_bootstrap_template.ps1"
SCRIPT_TEMPLATE = "templates/pwsh_command_pack/safe_command_pack_script_template.ps1"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_step_536_primary_standard_is_documented() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "AGENTS.md",
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
            "docs/08_CODEX_WORKFLOW.md",
        ]
    )

    for fragment in [
        "Safe Bootstrap PowerShell Command Pack",
        "bootstrap corto",
        "[scriptblock]::Create",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File",
        "nested here-strings",
        "here-string annidate",
        "fragile outer `try/finally`",
        "outer `else`",
        "Write-Host \";\"",
    ]:
        assert fragment in combined


def test_step_536_pr_first_and_main_ahead_rules_are_documented() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "docs/11_DECISIONS.md",
        ]
    )

    for fragment in [
        "PR-first",
        "branch + PR",
        "gh pr create",
        "gh pr merge",
        "git push origin main",
        "main...origin/main [ahead N]",
        "publish branch",
        "riallineare `main`",
    ]:
        assert fragment in combined


def test_step_536_output_artifacts_and_docx_fallback_are_documented() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
        ]
    )

    for fragment in [
        "NNNN-Richiesta_Generazione_<name>.txt",
        "NNNN-Comando_Eseguito_<name>.ps1",
        "NNNN-Output_Completo_<name>.txt",
        "NNNN-Output_Compatto_<name>.md",
        "NNNN-Output_Compatto_<name>.docx",
        "LAST-Richiesta_Generazione.txt",
        "LAST-Comando_Eseguito.ps1",
        "LAST-Output_Completo.txt",
        "LAST-Output_Compatto.md",
        "LAST-Output_Compatto.docx",
        ".docx.failed.txt",
        "best-effort",
        "non-blocking",
        "git --no-pager",
        "LF/CRLF",
    ]:
        assert fragment in combined


def test_step_536_templates_exist_and_keep_bootstrap_short() -> None:
    bootstrap = ROOT / BOOTSTRAP_TEMPLATE
    script = ROOT / SCRIPT_TEMPLATE

    assert bootstrap.exists()
    assert script.exists()

    bootstrap_text = read(BOOTSTRAP_TEMPLATE)
    assert "[scriptblock]::Create($ScriptText)" in bootstrap_text
    assert "pwsh -NoProfile -ExecutionPolicy Bypass -File $ScriptPath" in bootstrap_text
    assert "Write-Host \";\"" in bootstrap_text
    assert len(bootstrap_text.splitlines()) < 100


def test_step_536_templates_avoid_fragile_patterns() -> None:
    combined = "\n".join(
        [
            read(BOOTSTRAP_TEMPLATE),
            read(SCRIPT_TEMPLATE),
        ]
    )
    lowered = combined.casefold()

    forbidden_fragments = [
        "@'",
        '@"',
        " finally",
        "\nelse",
        " git push origin main",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in lowered


def test_step_536_tracking_documents_are_updated() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "README.md",
            "CHANGELOG.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
        ]
    )

    for fragment in [
        "STEP 536 - PowerShell Command Pack Safe Bootstrap Hardening",
        "PowerShell Command Pack Safe Bootstrap Hardening",
        "DEC-064 - PowerShell command pack safe bootstrap",
        "540) OpenAI API Adapter Controlled Live Execution Pack",
    ]:
        assert fragment in combined
