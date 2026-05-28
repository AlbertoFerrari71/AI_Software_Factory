param(
    [switch] $DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Require-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git was not found. Install Git before installing soft guardrails."
    }
}

function Get-RepoRoot {
    $root = (& git rev-parse --show-toplevel 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "This script must be run inside a Git repository."
    }
    return $root
}

Require-Git
$repoRoot = Get-RepoRoot
$hooksPath = ".githooks"
$preCommit = Join-Path $repoRoot ".githooks/pre-commit"
$prePush = Join-Path $repoRoot ".githooks/pre-push"

Write-Host "Install Soft Protection Guardrails"
Write-Host "Repository: $repoRoot"

if (-not (Test-Path -LiteralPath $preCommit)) {
    throw "Missing hook: .githooks/pre-commit"
}
if (-not (Test-Path -LiteralPath $prePush)) {
    throw "Missing hook: .githooks/pre-push"
}

Write-Step "Current Git hook configuration"
$currentHooksPath = (& git config --get core.hooksPath 2>$null | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($currentHooksPath)) {
    Write-Host "core.hooksPath: not set"
}
else {
    Write-Host "core.hooksPath: $currentHooksPath"
}

Write-Step "Requested configuration"
Write-Host "core.hooksPath -> $hooksPath"

if ($DryRun) {
    Write-Host ""
    Write-Host "DryRun only. No Git configuration was changed."
    Write-Host "To install after review:"
    Write-Host 'pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\install_soft_guardrails.ps1'
    exit 0
}

Write-Step "Install local hooks path"
& git config core.hooksPath $hooksPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set git config core.hooksPath."
}

Write-Step "Installed configuration"
& git config --get core.hooksPath
if ($LASTEXITCODE -ne 0) {
    throw "Could not read installed core.hooksPath."
}

Write-Host ""
Write-Host "Soft protection guardrails installed locally."
Write-Host "Verify with:"
Write-Host 'pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1'
