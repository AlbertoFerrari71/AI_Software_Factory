# Safe Bootstrap PowerShell Command Pack template.
# Replace PACK_NAME, STEP_NUMBER and SCRIPT_LINES before use.
# Keep this pasted wrapper short. Put complex logic in the generated .ps1.

& {
    $ErrorActionPreference = "Stop"
    $PSNativeCommandUseErrorActionPreference = $false

    $PackName = "step-XXXX-safe-bootstrap-example"
    $StepNumber = "NNNN"
    $BridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $RunId = "{0}-{1}" -f $Stamp, $PackName
    $OutDir = Join-Path $BridgeRoot $RunId
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

    $RequestFile = Join-Path $OutDir ("{0}-Richiesta_Generazione_{1}.txt" -f $StepNumber, $PackName)
    $CommandFile = Join-Path $OutDir ("{0}-Comando_Eseguito_{1}.ps1" -f $StepNumber, $PackName)
    $FullOutputFile = Join-Path $OutDir ("{0}-Output_Completo_{1}.txt" -f $StepNumber, $PackName)
    $CompactOutputFile = Join-Path $OutDir ("{0}-Output_Compatto_{1}.md" -f $StepNumber, $PackName)
    $LastRequestFile = Join-Path $BridgeRoot "LAST-Richiesta_Generazione.txt"
    $LastCommandFile = Join-Path $BridgeRoot "LAST-Comando_Eseguito.ps1"
    $LastFullOutputFile = Join-Path $BridgeRoot "LAST-Output_Completo.txt"
    $LastCompactOutputFile = Join-Path $BridgeRoot "LAST-Output_Compatto.md"

    $RequestLines = @(
        "Safe Bootstrap PowerShell Command Pack",
        "Pack: $PackName",
        "Step number: $StepNumber",
        "Generated: $(Get-Date -Format o)",
        "Rule: short bootstrap, generated script, parse check, then pwsh -File."
    )
    Set-Content -LiteralPath $RequestFile -Value $RequestLines -Encoding utf8
    Copy-Item -LiteralPath $RequestFile -Destination $LastRequestFile -Force

    $ScriptLines = @(
        "#Requires -Version 7.0",
        "Set-StrictMode -Version Latest",
        "`$ErrorActionPreference = `"Stop`"",
        "`$PSNativeCommandUseErrorActionPreference = `$false",
        "Write-Output 'Replace SCRIPT_LINES with the full generated command pack script.'"
    )
    $ScriptText = $ScriptLines -join [Environment]::NewLine
    Set-Content -LiteralPath $CommandFile -Value $ScriptText -Encoding utf8
    Copy-Item -LiteralPath $CommandFile -Destination $LastCommandFile -Force

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
        Copy-Item -LiteralPath $FullOutputFile -Destination $LastFullOutputFile -Force
        Copy-Item -LiteralPath $CompactOutputFile -Destination $LastCompactOutputFile -Force
        try { Set-Clipboard -Value ($BlockedLines -join [Environment]::NewLine) } catch { }
        Write-Host "Parse check failed. Generated script was not executed."
        Write-Host ";"
        exit 1
    }

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
}
Write-Host ";"
