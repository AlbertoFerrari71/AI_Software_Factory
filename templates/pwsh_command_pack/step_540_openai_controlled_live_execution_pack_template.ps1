# STEP 540 OpenAI controlled live execution pack safe bootstrap template.
# Keep this pasted wrapper short. Put execution logic in the generated .ps1.
# Default is dry-run and no OpenAI network call.
# For a future authorized live run only, set the credential in the parent shell:
# $env:OPENAI_API_KEY = "<set in environment, never printed>"

$PackName = "step-540-openai-controlled-live-execution-pack"
$StepNumber = "0540"
$Iteration = "01"
$ArtifactSlug = "openai_controlled_live_execution_pack"
$ArtifactPrefix = "{0}-{1}" -f $StepNumber, $Iteration
$ExecutionMode = "dry-run"
$ConfirmLiveOpenAI = $false
$RepoRoot = "C:\Users\alberto.ferrari\source\repos\AI_Software_Factory"
$BridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunId = "{0}-{1}" -f $Stamp, $PackName
$OutDir = Join-Path $BridgeRoot $RunId
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$RequestPath = Join-Path $OutDir ("{0}-Richiesta_Generazione_{1}.txt" -f $ArtifactPrefix, $ArtifactSlug)
$ScriptPath = Join-Path $OutDir ("{0}-Comando_Eseguito_{1}.ps1" -f $ArtifactPrefix, $ArtifactSlug)
$FullPath = Join-Path $OutDir ("{0}-Output_Completo_{1}.txt" -f $ArtifactPrefix, $ArtifactSlug)
$CompactPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.md" -f $ArtifactPrefix, $ArtifactSlug)
$DocxPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx" -f $ArtifactPrefix, $ArtifactSlug)
$DocxFailedPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx.failed.txt" -f $ArtifactPrefix, $ArtifactSlug)

$RequestLines = @(
    "Safe Bootstrap PowerShell Command Pack",
    "Pack: $PackName",
    "Generated: $(Get-Date -Format o)",
    "Execution mode: $ExecutionMode",
    "Artifact rule: NNNN-II-Tipo_Nome.ext; no LAST artifacts.",
    "Compact artifact example: 0540-01-Output_Compatto_openai_controlled_live_execution_pack.md",
    "Default posture: dry-run, no OpenAI network call.",
    "Live requires ASF_OPENAI_LIVE_ENABLED=1 and --confirm-live-openai.",
    "API key presence is not authorization.",
    "Do not paste, print, save, hash, truncate, or serialize API keys.",
    "No Git publication is performed by this pack.",
    "If publication is later required, use branch + PR; direct push to main is not the default."
)
Set-Content -LiteralPath $RequestPath -Value $RequestLines -Encoding utf8

$ScriptLines = @(
    "#Requires -Version 7.0",
    "Set-StrictMode -Version Latest",
    "`$ErrorActionPreference = 'Stop'",
    "`$PSNativeCommandUseErrorActionPreference = `$false",
    "`$RepoRoot = `"$RepoRoot`"",
    "`$ExecutionMode = `"$ExecutionMode`"",
    "Set-Location -LiteralPath `$RepoRoot",
    "Write-Output 'STEP 540 OpenAI controlled live execution pack'",
    "Write-Output 'Default safe posture: dry-run unless changed before generation.'",
    "Write-Output 'Credential value is never printed. Presence is reported only as a boolean.'",
    "if (`$null -ne `$env:OPENAI_API_KEY -and `$env:OPENAI_API_KEY -ne '') { Write-Output 'credential_present: true' } else { Write-Output 'credential_present: false' }",
    "if (`$env:ASF_OPENAI_LIVE_ENABLED -eq '1') { Write-Output 'live_enabled: true' } else { Write-Output 'live_enabled: false' }",
    "git --no-pager status --short",
    "`$CommandArgs = @(",
    "    'scripts/asf_openai_controlled_live_execution_pack.py',",
    "    '--execution-mode',",
    "    `$ExecutionMode,",
    "    '--output-dir',",
    "    'tmp/asf_openai_controlled_live_execution_pack'",
    ")"
)
if ($ConfirmLiveOpenAI) {
    $ScriptLines += "`$CommandArgs += '--confirm-live-openai'"
}
$ScriptLines += @(
    "python @CommandArgs",
    "if (`$LASTEXITCODE -ne 0) { throw ('controlled live execution pack failed with exit code {0}' -f `$LASTEXITCODE) }",
    "Write-Output 'Controlled live execution pack completed.'"
)
$ScriptText = $ScriptLines -join [Environment]::NewLine
Set-Content -LiteralPath $ScriptPath -Value $ScriptText -Encoding utf8

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
        "STEP 540 OpenAI controlled live execution pack - BLOCKED",
        "Pack: $PackName",
        "Reason: generated script parse check failed",
        "Error: $ParseError",
        "No OpenAI call was executed."
    )
    Set-Content -LiteralPath $FullPath -Value $BlockedLines -Encoding utf8
    Set-Content -LiteralPath $CompactPath -Value $BlockedLines -Encoding utf8
    Set-Content -LiteralPath $DocxFailedPath -Value "DOCX skipped because parse check failed." -Encoding utf8
    Set-Clipboard -Value ($BlockedLines -join [Environment]::NewLine)
    Write-Host "Parse check failed. Generated script was not executed."
    Write-Host ";"
    exit 1
}

& pwsh -NoProfile -ExecutionPolicy Bypass -File $ScriptPath *> $FullPath
$ExitCode = $LASTEXITCODE
if ($null -eq $ExitCode) {
    $ExitCode = 1
}

$Tail = @()
if (Test-Path -LiteralPath $FullPath) {
    $Tail = Get-Content -LiteralPath $FullPath -Tail 80
}
if ($Tail.Count -eq 0) {
    $Tail = @("Full output missing or empty.")
}
$Fence = -join @([char]96, [char]96, [char]96)
$CompactLines = @(
    "# STEP 540 OpenAI controlled live execution pack",
    "",
    "- Pack: $PackName",
    "- Execution mode: $ExecutionMode",
    "- Exit code: $ExitCode",
    "- Full output: $FullPath",
    "- JSON/Markdown runtime artifacts: tmp/asf_openai_controlled_live_execution_pack/",
    "- DOCX: best-effort/non-blocking",
    "",
    "## Tail",
    $Fence
)
$CompactLines += $Tail
$CompactLines += $Fence
Set-Content -LiteralPath $CompactPath -Value $CompactLines -Encoding utf8
Set-Content -LiteralPath $DocxFailedPath -Value "DOCX generation was not required for this dry-run template; non-blocking." -Encoding utf8

Set-Clipboard -Value (Get-Content -LiteralPath $CompactPath -Raw)

Write-Host ("Generated script exit code: {0}" -f $ExitCode)
if ($ExitCode -ne 0) {
    Write-Host ";"
    exit $ExitCode
}
Write-Host ";"
