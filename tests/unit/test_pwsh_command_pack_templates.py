from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

README = "templates/pwsh_command_pack/README.md"
SKILL_DRAFT = "templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md"
SKILL_EXPORT = "templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md"
SCRIPT_TEMPLATE = "templates/pwsh_command_pack/safe_command_pack_script_template.ps1"
DOC_0805 = "docs/motor/0805_POWERSHELL_PUBLISH_SKILL_SYNC_WITH_PROVEN_RUNNER_FLOW.md"
QUICK_REFERENCE = "docs/36_WORKFLOW_QUICK_REFERENCE.md"
COOKBOOK = "docs/38_WORKFLOW_COMMAND_COOKBOOK.md"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def combined_template_text() -> str:
    return "\n".join(
        read(path)
        for path in [
            README,
            SKILL_DRAFT,
            SKILL_EXPORT,
            SCRIPT_TEMPLATE,
            DOC_0805,
            QUICK_REFERENCE,
            COOKBOOK,
        ]
    )


def test_asf_publish_flow_documents_config_json_and_runner() -> None:
    combined = combined_template_text()

    required_fragments = [
        "PrepareConfig",
        "scope discovery",
        "human review",
        "config JSON esplicito",
        "explicit config JSON",
        "scripts/asf_publish_step.ps1",
        "-Config",
        "Phase B",
        "-ApprovePublish",
        "gh pr list --head",
        "--json number",
        "--jq \".[0].number\"",
        "Phase C",
        "-PrNumber",
        "-ApproveMerge",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_asf_publish_flow_documents_prepare_config_and_recovery_scope_review() -> None:
    combined = combined_template_text()

    for fragment in [
        "scripts/asf_publish_step.ps1 -Phase PrepareConfig",
        "human review of `expected_files` and `changed_files`",
        "recovery report",
        "suggested config",
        "add files to scope only after human review",
        "do not approve publication",
        "do not force scope automatically",
        "LF/CRLF warnings are not out-of-scope files",
        "DOCX/accessory outputs are best-effort",
        "must not invalidate a publish already verified",
        "Bridge/LAST primary-path locks",
        "timestamped fallback",
        "single writer ownership",
        "NNNN-Wrapper_Log_*.txt",
    ]:
        assert fragment in combined


def test_asf_publish_config_lists_required_fields() -> None:
    combined = combined_template_text()

    for field_name in [
        "step",
        "name",
        "repo_path",
        "bridge_root",
        "branch",
        "commit_message",
        "pr_title",
        "pr_body",
        "next_step",
        "expected_files",
        "changed_files",
        "verification_profile",
        "risk_level",
        "verification_phase",
        "profile_selector_expected_profile",
        "intent",
        "provided_gates",
        "phase_a_checks",
        "phase_c_checks",
        "allow_no_github_checks_reported",
        "log_max_count",
    ]:
        assert field_name in combined


def test_asf_publish_flow_validates_pr_number_before_phase_c() -> None:
    script = read(SCRIPT_TEMPLATE)

    empty_check = script.index('if ([string]::IsNullOrWhiteSpace($PrNumber))')
    numeric_check = script.index('if ($PrNumber -notmatch "^\\d+$")')
    phase_c = script.index('"ASF publish Phase C"')

    assert empty_check < phase_c
    assert numeric_check < phase_c

    combined = combined_template_text()
    assert "PR number is empty" in combined or "PR number missing" in combined
    assert "PR number is not numeric" in combined


def test_asf_publish_flow_uses_content_clipboard_copy_not_path_parameter() -> None:
    script = read(SCRIPT_TEMPLATE)
    combined = combined_template_text()

    assert "Get-Content -Path $LastCompactPath -Raw | Set-Clipboard" in script
    assert "Get-Content -Path <file> -Raw | Set-Clipboard" in combined
    assert not re.search(r"Set-Clipboard\s+-Path\b", script, flags=re.IGNORECASE)
    assert not re.search(r"Set-Clipboard\s+-LiteralPath\b", script, flags=re.IGNORECASE)


def test_asf_publish_flow_documents_lf_crlf_and_docx_as_non_blocking() -> None:
    combined = combined_template_text()

    for fragment in [
        "LF/CRLF",
        "non-blocking",
        "git --no-pager diff --check",
        "tests",
        "workflow health check",
        "verify gate",
        "DOCX is best-effort",
        "DOCX/Word COM resta best-effort",
        "Markdown",
        "compact Markdown is mandatory",
        "COMPLETATO CON WARNING NON BLOCCANTE",
    ]:
        assert fragment in combined


def test_asf_publish_flow_discourages_fragile_scope_and_introspection_patterns() -> None:
    combined = combined_template_text()

    for fragment in [
        "fragile parsing of `git status --short`",
        "do not infer scope by parsing git status --short",
        "2>&1",
        "Get-Command -Path",
        "AST parsing",
        "mega-wrapper PowerShell",
        "Do not run Phase C without",
        "non-empty numeric PR number",
    ]:
        assert fragment in combined


def test_asf_publish_flow_does_not_declare_completed_before_final_gates() -> None:
    script = read(SCRIPT_TEMPLATE)

    final_status = script.index('Run -FileName "git" -ArgList @("--no-pager", "status", "--short")')
    completed = script.index('Write-Log "COMPLETATO after final ASF publish gates passed."')

    assert final_status < completed
    assert 'Write-Host "COMPLETATO"' not in script
    assert "printing `COMPLETATO` before final gates pass" in combined_template_text()


def test_asf_publish_flow_documents_single_writer_transcript_rule() -> None:
    script = read(SCRIPT_TEMPLATE)
    combined = combined_template_text()

    assert "Start-Transcript" in combined
    assert "Output_Completo" in combined
    assert "NNNN-Wrapper_Log_*.txt" in combined
    assert "single writer ownership" in combined
    assert "Start-Transcript" in script
