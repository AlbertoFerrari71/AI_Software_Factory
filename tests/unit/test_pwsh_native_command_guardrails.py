from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = "docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md"
README = "templates/pwsh_command_pack/README.md"
SKILL_DRAFT = "templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md"
SKILL_EXPORT = "templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md"
BOOTSTRAP_TEMPLATE = "templates/pwsh_command_pack/safe_bootstrap_template.ps1"
SCRIPT_TEMPLATE = "templates/pwsh_command_pack/safe_command_pack_script_template.ps1"


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


def test_step_0800_files_exist() -> None:
    for relative_path in [
        DOC,
        README,
        SKILL_DRAFT,
        SKILL_EXPORT,
        BOOTSTRAP_TEMPLATE,
        SCRIPT_TEMPLATE,
    ]:
        assert (ROOT / relative_path).is_file(), relative_path


def test_native_command_wrapper_rejects_ambiguous_input_before_execution() -> None:
    script = read(SCRIPT_TEMPLATE)

    required_fragments = [
        "function Test-NativeCommandInput",
        "Native command file name is empty",
        "Native command label is empty",
        "Native command ArgList is null",
        "Native command argument {0} is empty",
        "Native command allowed exit codes are empty",
        "Test-NativeCommandInput -FileName $FileName -ArgList $ArgList",
        "[System.Diagnostics.ProcessStartInfo]::new()",
        "$StartInfo.ArgumentList.Add($Argument)",
        "$AllowedExitCodes -notcontains $Process.ExitCode",
        "AllowedExitCodes = $AllowedExitCodes",
        "COMPLETED_AFTER_ALL_NATIVE_GUARDRAILS",
    ]
    for fragment in required_fragments:
        assert fragment in script


def test_bootstrap_reads_native_exit_code_before_success_message() -> None:
    bootstrap = read(BOOTSTRAP_TEMPLATE)

    assert "$PSNativeCommandUseErrorActionPreference = $false" in bootstrap
    assert "pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile" in bootstrap
    assert "$ExitCode = $LASTEXITCODE" in bootstrap
    assert "if ($null -eq $ExitCode)" in bootstrap
    assert "exit $ExitCode" in bootstrap

    failure_check = bootstrap.index("if ($ExitCode -ne 0)")
    success_message = bootstrap.index("Generated script completed after exit code 0.")
    assert failure_check < success_message


def test_docs_and_skill_export_describe_native_guardrail_standard() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            DOC,
            README,
            SKILL_DRAFT,
            SKILL_EXPORT,
        ]
    )

    required_fragments = [
        "PowerShell Native Command Guardrail Hardening",
        "$PSNativeCommandUseErrorActionPreference = $false",
        "System.Diagnostics.ProcessStartInfo.ArgumentList",
        "AllowedExitCodes",
        "non-empty stderr is not automatically a failure",
        "COMPLETATO",
        "COMPLETED_AFTER_ALL_NATIVE_GUARDRAILS",
        "0810) Publish Runner Recovery UX and No-False-Completed Guard",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_pwsh_templates_parse_after_native_guardrail_hardening() -> None:
    for relative_path in [
        BOOTSTRAP_TEMPLATE,
        SCRIPT_TEMPLATE,
    ]:
        result = parse_check(relative_path)
        assert result.returncode == 0, result.stdout + result.stderr
