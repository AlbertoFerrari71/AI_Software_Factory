# Safe Bootstrap PowerShell Command Pack template.
# Replace PACK_NAME, STEP_NUMBER and SCRIPT_LINES before use.
# Keep this pasted wrapper short. Put complex logic in the generated .ps1.

& {
    $ErrorActionPreference = "Stop"
    $PSNativeCommandUseErrorActionPreference = $false

    $PackName = "step-XXXX-safe-bootstrap-example"
    $StepNumber = "NNNN"
    $Iteration = "01"
    $ArtifactPrefix = "{0}-{1}" -f $StepNumber, $Iteration
    $BridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $RunId = "{0}-{1}" -f $Stamp, $PackName
    $OutDir = Join-Path $BridgeRoot $RunId
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

    $RequestFile = Join-Path $OutDir ("{0}-Richiesta_Generazione_{1}.txt" -f $ArtifactPrefix, $PackName)
    $CommandFile = Join-Path $OutDir ("{0}-Comando_Eseguito_{1}.ps1" -f $ArtifactPrefix, $PackName)
    $FullOutputFile = Join-Path $OutDir ("{0}-Output_Completo_{1}.txt" -f $ArtifactPrefix, $PackName)
    $CompactOutputFile = Join-Path $OutDir ("{0}-Output_Compatto_{1}.md" -f $ArtifactPrefix, $PackName)

    $RequestLines = @(
        "Safe Bootstrap PowerShell Command Pack",
        "Pack: $PackName",
        "Step number: $StepNumber",
        "Iteration: $Iteration",
        "Generated: $(Get-Date -Format o)",
        "Rule: short bootstrap, generated script, parse check, then pwsh -File.",
        "Artifact rule: NNNN-II-Tipo_Nome.ext; no LAST artifacts."
    )
    Set-Content -LiteralPath $RequestFile -Value $RequestLines -Encoding utf8

    $ScriptLines = @(
        "#Requires -Version 7.0",
        "Set-StrictMode -Version Latest",
        "`$ErrorActionPreference = `"Stop`"",
        "`$PSNativeCommandUseErrorActionPreference = `$false",
        "Write-Output 'Replace SCRIPT_LINES with the full generated command pack script.'"
    )
    $ScriptText = $ScriptLines -join [Environment]::NewLine
    Set-Content -LiteralPath $CommandFile -Value $ScriptText -Encoding utf8

    $ParseOk = $false
    $ParseError = ""
    try {
        [scriptblock]::Create($ScriptText) | Out-Null
        $ParseOk = $true
    } catch {
        $ParseError = $_.Exception.Message
    }

    if (-not $ParseOk) {
        $BlockedLines = @(
            "Safe Bootstrap PowerShell Command Pack - BLOCKED",
            "Pack: $PackName",
            "Reason: generated script parse check failed",
            "Error: $ParseError",
            "No Git command was executed."
        )
        Set-Content -LiteralPath $FullOutputFile -Value $BlockedLines -Encoding utf8
        Set-Content -LiteralPath $CompactOutputFile -Value $BlockedLines -Encoding utf8
        try { Set-Clipboard -Value ($BlockedLines -join [Environment]::NewLine) } catch { }
        Write-Host "Parse check failed. Generated script was not executed."
        Write-Host ";"
        exit 1
    }

    if ([string]::IsNullOrWhiteSpace($CommandFile)) {
        Set-Content -LiteralPath $FullOutputFile -Value "Generated script path is empty. No command was executed." -Encoding utf8
        Set-Content -LiteralPath $CompactOutputFile -Value "Generated script path is empty. No command was executed." -Encoding utf8
        Write-Host "Generated script path is empty. No command was executed."
        Write-Host ";"
        exit 1
    }
    if (-not (Test-Path -LiteralPath $CommandFile)) {
        Set-Content -LiteralPath $FullOutputFile -Value "Generated script file is missing. No command was executed." -Encoding utf8
        Set-Content -LiteralPath $CompactOutputFile -Value "Generated script file is missing. No command was executed." -Encoding utf8
        Write-Host "Generated script file is missing. No command was executed."
        Write-Host ";"
        exit 1
    }

    Write-Host "Executing generated script after parse check."
    & pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile
    $ExitCode = $LASTEXITCODE
    if ($null -eq $ExitCode) {
        $ExitCode = 1
    }
    Write-Host ("Generated script exit code: {0}" -f $ExitCode)
    if ($ExitCode -ne 0) {
        Write-Host ";"
        exit $ExitCode
    }
    Write-Host "Generated script completed after exit code 0."
}
Write-Host ";"
