Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Require-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git was not found. Install Git before checking soft guardrails."
    }
}

function Get-RepoRoot {
    $root = (& git rev-parse --show-toplevel 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "This script must be run inside a Git repository."
    }
    return $root
}

function Test-ContentFragment {
    param(
        [Parameter(Mandatory = $true)][string] $Path,
        [Parameter(Mandatory = $true)][string] $Fragment
    )
    $content = Get-Content -LiteralPath $Path -Raw
    return $content.Contains($Fragment)
}

Require-Git
$repoRoot = Get-RepoRoot
$expectedHooksPath = ".githooks"
$preCommit = Join-Path $repoRoot ".githooks/pre-commit"
$prePush = Join-Path $repoRoot ".githooks/pre-push"

Write-Host "Check Soft Protection Guardrails"
Write-Host "Repository: $repoRoot"

Write-Step "Git hook configuration"
$configuredHooksPath = (& git config --get core.hooksPath 2>$null | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($configuredHooksPath)) {
    Write-Host "core.hooksPath: not set"
}
else {
    Write-Host "core.hooksPath: $configuredHooksPath"
}

$installed = ($configuredHooksPath -eq $expectedHooksPath)
if ($installed) {
    Write-Host "Installed: yes"
}
else {
    Write-Warning "Installed: no. Expected core.hooksPath to be .githooks."
}

Write-Step "Hook files"
$missing = @()
foreach ($path in @($preCommit, $prePush)) {
    if (Test-Path -LiteralPath $path) {
        Write-Host "Present: $path"
    }
    else {
        Write-Warning "Missing: $path"
        $missing += $path
    }
}

if ($missing.Count -gt 0) {
    Write-Error "Soft guardrail hook files are missing."
    exit 1
}

Write-Step "Hook content"
$contentIssues = @()
$checks = @(
    @{ Path = $preCommit; Fragment = "ASF_ALLOW_MAIN_BYPASS"; Label = "pre-commit bypass variable" },
    @{ Path = $preCommit; Fragment = "main"; Label = "pre-commit main guard" },
    @{ Path = $prePush; Fragment = "ASF_ALLOW_MAIN_BYPASS"; Label = "pre-push bypass variable" },
    @{ Path = $prePush; Fragment = "refs/heads/main"; Label = "pre-push main ref guard" }
)

foreach ($check in $checks) {
    if (Test-ContentFragment -Path $check.Path -Fragment $check.Fragment) {
        Write-Host "OK: $($check.Label)"
    }
    else {
        Write-Warning "Missing content: $($check.Label)"
        $contentIssues += $check.Label
    }
}

if ($contentIssues.Count -gt 0) {
    Write-Error "Soft guardrail hooks are present but content checks failed."
    exit 1
}

Write-Step "Result"
if (-not $installed) {
    Write-Warning "Soft protection guardrails are present but not installed."
    Write-Host "Run install script only after manual review:"
    Write-Host 'pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\install_soft_guardrails.ps1 -DryRun'
    Write-Host "Exit code 2 means: hook files are present and installable, but core.hooksPath is not configured."
    exit 2
}

Write-Host "Soft protection guardrails installed and coherent."
exit 0
