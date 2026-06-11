<#
.SYNOPSIS
Read-only readiness check for the shared collaboration backbone.

.DESCRIPTION
[F] This script does not authenticate, write files, call GitHub APIs, or request tokens.
[F] It checks local tools, Git state and expected collaboration folders.
[S] WARN means manual attention, not automatic failure.
[O] Use before Luca's first micro-step and before pilot 0290.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepositoryPath = (Get-Location).Path
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$script:FailCount = 0
$script:WarnCount = 0

function Write-Check {
    param(
        [Parameter(Mandatory = $true)][ValidateSet('PASS', 'WARN', 'FAIL', 'INFO')][string]$Status,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($Status -eq 'FAIL') { $script:FailCount += 1 }
    if ($Status -eq 'WARN') { $script:WarnCount += 1 }
    Write-Output ("{0}: {1}" -f $Status, $Message)
}

function Invoke-ReadOnlyNative {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
        return [PSCustomObject]@{
            ExitCode = $exitCode
            Output = @($output)
        }
    } finally {
        $ErrorActionPreference = $oldPreference
    }
}

try {
    $resolvedRepo = Resolve-Path -LiteralPath $RepositoryPath -ErrorAction Stop
    Set-Location -LiteralPath $resolvedRepo.Path
    Write-Check -Status 'INFO' -Message ("[F] RepositoryPath={0}" -f $resolvedRepo.Path)

    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $gitCommand) {
        Write-Check -Status 'FAIL' -Message '[F] git not available on PATH.'
    } else {
        Write-Check -Status 'PASS' -Message ("[F] git available: {0}" -f $gitCommand.Source)
        $top = Invoke-ReadOnlyNative -FilePath $gitCommand.Source -Arguments @('rev-parse', '--show-toplevel')
        if ($top.ExitCode -eq 0) {
            Write-Check -Status 'PASS' -Message ("[F] git top-level: {0}" -f (($top.Output -join ' ').Trim()))
        } else {
            Write-Check -Status 'FAIL' -Message '[F] Current directory is not a Git repository.'
        }

        $branch = Invoke-ReadOnlyNative -FilePath $gitCommand.Source -Arguments @('branch', '--show-current')
        if ($branch.ExitCode -eq 0) {
            $branchText = (($branch.Output -join ' ').Trim())
            if ([string]::IsNullOrWhiteSpace($branchText)) { $branchText = '(detached or unknown)' }
            Write-Check -Status 'PASS' -Message ("[F] Current branch: {0}" -f $branchText)
        } else {
            Write-Check -Status 'WARN' -Message '[S] Could not read current branch.'
        }

        $remote = Invoke-ReadOnlyNative -FilePath $gitCommand.Source -Arguments @('remote', 'get-url', 'origin')
        if ($remote.ExitCode -eq 0) {
            Write-Check -Status 'PASS' -Message ("[F] origin: {0}" -f (($remote.Output -join ' ').Trim()))
        } else {
            Write-Check -Status 'WARN' -Message '[S] origin remote not configured or not readable.'
        }
    }

    $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $ghCommand) {
        Write-Check -Status 'WARN' -Message '[S] gh not available on PATH. No authentication attempted.'
    } else {
        Write-Check -Status 'PASS' -Message ("[F] gh available: {0}. No authentication attempted." -f $ghCommand.Source)
    }

    foreach ($path in @('AGENTS.md', 'docs/collaboration', 'templates/collaboration', 'scripts/collaboration')) {
        if (Test-Path -LiteralPath $path) {
            Write-Check -Status 'PASS' -Message ("[F] Present: {0}" -f $path)
        } else {
            Write-Check -Status 'WARN' -Message ("[S] Missing: {0}" -f $path)
        }
    }

    if ($script:FailCount -gt 0) {
        Write-Check -Status 'INFO' -Message ("[F] Summary: FAIL={0} WARN={1}" -f $script:FailCount, $script:WarnCount)
        exit 1
    }

    if ($script:WarnCount -gt 0) {
        Write-Check -Status 'INFO' -Message ("[S] Summary: PASS_WITH_WARNINGS WARN={0}" -f $script:WarnCount)
        exit 0
    }

    Write-Check -Status 'INFO' -Message '[F] Summary: PASS'
    exit 0
} catch {
    Write-Check -Status 'FAIL' -Message ("[F] {0}" -f $_.Exception.Message)
    exit 1
}