param(
    [string] $Owner = "AlbertoFerrari71",
    [string] $Repo = "AI_Software_Factory",
    [string] $Branch = "main",
    [string] $RequiredCheckName
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
        throw "GitHub CLI 'gh' was not found. Install gh before verifying branch protection."
    }

    & gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI is not authenticated. Run 'gh auth status' before verifying branch protection."
    }
}

Write-Host "Verify Branch Protection"
Write-Host "Repository: $Owner/$Repo"
Write-Host "Branch: $Branch"

Require-Gh

$endpoint = "repos/$Owner/$Repo/branches/$Branch/protection"
Write-Step "Read current protection"
$raw = & gh api $endpoint 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    $message = ($raw | Out-String)
    if ($message -match "404" -or $message -match "Not Found") {
        Write-Host "Branch protection is not configured for $Branch."
        exit 0
    }

    throw "Could not read branch protection. gh api exit code: $exitCode. $message"
}

$json = ($raw | Out-String)
$protection = $json | ConvertFrom-Json

Write-Step "Required status checks"
$configuredChecks = @()
if ($null -ne $protection.required_status_checks) {
    if ($null -ne $protection.required_status_checks.checks) {
        $configuredChecks = @($protection.required_status_checks.checks | ForEach-Object { $_.context })
    }
    elseif ($null -ne $protection.required_status_checks.contexts) {
        $configuredChecks = @($protection.required_status_checks.contexts)
    }
}

if ($configuredChecks.Count -eq 0) {
    Write-Host "No required status checks configured."
}
else {
    foreach ($check in $configuredChecks) {
        Write-Host "- $check"
    }
}

if (-not [string]::IsNullOrWhiteSpace($RequiredCheckName)) {
    if ($configuredChecks -contains $RequiredCheckName) {
        Write-Host "Required check present: $RequiredCheckName"
    }
    else {
        Write-Warning "Required check not found: $RequiredCheckName"
    }
}

Write-Step "Protection summary"
$enforceAdmins = $false
if ($null -ne $protection.enforce_admins -and $null -ne $protection.enforce_admins.enabled) {
    $enforceAdmins = [bool]$protection.enforce_admins.enabled
}
Write-Host "Enforce admins: $enforceAdmins"

$prProtection = ($null -ne $protection.required_pull_request_reviews)
Write-Host "Pull request protection: $prProtection"

$forcePushAllowed = $false
if ($null -ne $protection.allow_force_pushes -and $null -ne $protection.allow_force_pushes.enabled) {
    $forcePushAllowed = [bool]$protection.allow_force_pushes.enabled
}
Write-Host "Allow force pushes: $forcePushAllowed"

$deletionAllowed = $false
if ($null -ne $protection.allow_deletions -and $null -ne $protection.allow_deletions.enabled) {
    $deletionAllowed = [bool]$protection.allow_deletions.enabled
}
Write-Host "Allow deletions: $deletionAllowed"

Write-Step "Minimum viable protection warnings"
if (-not $prProtection) {
    Write-Warning "Pull request protection is not configured."
}
if ($configuredChecks.Count -eq 0) {
    Write-Warning "No required CI/status check is configured."
}
if ($forcePushAllowed) {
    Write-Warning "Force pushes are allowed; minimum viable protection expects them blocked."
}
if ($deletionAllowed) {
    Write-Warning "Branch deletion is allowed; minimum viable protection expects it blocked."
}

Write-Host ""
Write-Host "Branch protection verification completed."
