param(
    [string] $Owner = "AlbertoFerrari71",
    [string] $Repo = "AI_Software_Factory",
    [string] $Branch = "main",

    [Parameter(Mandatory = $true)]
    [string] $RequiredCheckName,

    [switch] $Apply,
    [switch] $EnforceAdmins,
    [switch] $ConfirmApply
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
        throw "GitHub CLI 'gh' was not found. Install gh before applying branch protection."
    }

    & gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI is not authenticated. Run 'gh auth status' before applying branch protection."
    }
}

$endpoint = "repos/$Owner/$Repo/branches/$Branch/protection"

$payload = [ordered]@{
    required_status_checks = [ordered]@{
        strict = $true
        checks = @(
            [ordered]@{
                context = $RequiredCheckName
            }
        )
    }
    enforce_admins = [bool]$EnforceAdmins
    required_pull_request_reviews = [ordered]@{
        dismiss_stale_reviews = $false
        require_code_owner_reviews = $false
        required_approving_review_count = 0
        require_last_push_approval = $false
    }
    restrictions = $null
    required_linear_history = $false
    allow_force_pushes = $false
    allow_deletions = $false
    block_creations = $false
    required_conversation_resolution = $false
    lock_branch = $false
    allow_fork_syncing = $false
}

$payloadJson = $payload | ConvertTo-Json -Depth 10

Write-Host "Branch Protection Apply"
Write-Host "Repository: $Owner/$Repo"
Write-Host "Branch: $Branch"
Write-Host "Endpoint: PUT $endpoint"
Write-Host "RequiredCheckName: $RequiredCheckName"
Write-Host "EnforceAdmins: $([bool]$EnforceAdmins)"
Write-Host ""
Write-Warning "GitHub branch protection may be unavailable for private repositories on the current plan."
Write-Host "If GitHub returns HTTP 403 with an upgrade message, do not apply hard protection."
Write-Host "Run .\scripts\github\verify_branch_protection.ps1 first and use soft protection if the plan blocks protected branches."

Write-Step "Payload"
Write-Host $payloadJson

if (-not $Apply) {
    Write-Host ""
    Write-Host "DryRun only. No GitHub changes were made."
    Write-Host "To apply after review:"
    Write-Host '.\scripts\github\apply_branch_protection.ps1 -RequiredCheckName "<check name>" -Apply -ConfirmApply'
    exit 0
}

Write-Warning "This command is about to modify GitHub branch protection."
Write-Host "Confirm that the repository plan supports branch protection and that verify_branch_protection.ps1 did not report exit code 2."

if (-not $ConfirmApply) {
    $answer = Read-Host "Type APPLY to modify GitHub branch protection for $Owner/$Repo $Branch"
    if ($answer -ne "APPLY") {
        throw "Apply cancelled. Confirmation text did not match APPLY."
    }
}

Require-Gh

$tempFile = [System.IO.Path]::GetTempFileName()
try {
    Set-Content -LiteralPath $tempFile -Value $payloadJson -Encoding UTF8

    Write-Step "Apply branch protection"
    & gh api $endpoint --method PUT --input $tempFile
    if ($LASTEXITCODE -ne 0) {
        throw "gh api failed while applying branch protection."
    }

    Write-Host ""
    Write-Host "Branch protection apply request completed."
}
finally {
    if (Test-Path -LiteralPath $tempFile) {
        Remove-Item -LiteralPath $tempFile -Force
    }
}
