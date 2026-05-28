param(
    [string] $Owner = "AlbertoFerrari71",
    [string] $Repo = "AI_Software_Factory",
    [string] $Branch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Require-Gh {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI 'gh' was not found. Install gh and authenticate before detecting checks."
    }

    & gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI is not authenticated. Run 'gh auth status' and authenticate before detecting checks."
    }
}

function Get-BranchSha {
    $sha = (& git rev-parse "origin/$Branch" 2>$null).Trim()
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($sha)) {
        return $sha
    }

    $sha = (& git rev-parse $Branch 2>$null).Trim()
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($sha)) {
        return $sha
    }

    throw "Could not resolve origin/$Branch or local $Branch."
}

Write-Host "Detect required status check candidates"
Write-Host "Repository: $Owner/$Repo"
Write-Host "Branch: $Branch"

Require-Gh

Write-Step "Resolve branch commit"
$sha = Get-BranchSha
Write-Host "Commit: $sha"

Write-Step "Read check runs"
$endpoint = "repos/$Owner/$Repo/commits/$sha/check-runs"
$checkNames = @()

try {
    $checkNames = & gh api $endpoint --jq ".check_runs[].name"
    if ($LASTEXITCODE -ne 0) {
        $checkNames = @()
    }
}
catch {
    $checkNames = @()
}

$checkNames = @($checkNames | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)

if ($checkNames.Count -eq 0) {
    Write-Host ""
    Write-Host "No check run candidates were detected for $sha."
    Write-Host "Run a pull request or inspect GitHub Actions, then pass -RequiredCheckName explicitly."
    Write-Host "Example:"
    Write-Host '.\scripts\github\apply_branch_protection.ps1 -RequiredCheckName "Verification Gate"'
    exit 0
}

Write-Host ""
Write-Host "Detected candidate check names:"
foreach ($name in $checkNames) {
    Write-Host "- $name"
}

Write-Host ""
Write-Host "Then use:"
Write-Host '.\scripts\github\apply_branch_protection.ps1 -RequiredCheckName "<check name>"'
