<#
.SYNOPSIS
Safely previews or applies a Codex skills sync from a repository source to a local target.

.DESCRIPTION
[F] DryRun defaults to true: no files are copied by default.
[F] Backup defaults to true before apply.
[F] The script never deletes unmanaged target files.
[F] The script does not execute installed skills.
[S] SourcePath should point to the official Codex_Skills source or a reviewed repo skill folder.
[O] Run dry-run first, review the report, then apply only after approval.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [Parameter(Mandatory = $false)]
    [bool]$DryRun = $true,

    [Parameter(Mandatory = $false)]
    [bool]$Backup = $true,

    [Parameter(Mandatory = $false)]
    [string]$ReportPath
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$report = New-Object 'System.Collections.Generic.List[string]'
function Add-ReportLine {
    param([Parameter(Mandatory = $true)][string]$Line)
    $report.Add($Line) | Out-Null
    Write-Output $Line
}

function Get-RelativePathSafe {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$ChildPath
    )
    $baseFull = [System.IO.Path]::GetFullPath($BasePath).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $childFull = [System.IO.Path]::GetFullPath($ChildPath)
    if (-not $childFull.StartsWith($baseFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Child path is outside base path: $ChildPath"
    }
    return $childFull.Substring($baseFull.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
}

function Test-ForbiddenSkillFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $name = [System.IO.Path]::GetFileName($Path)
    if ($name -match '^\.env(\.|$)?') { return $true }
    if ($name -match '(?i)(secret|token|password|private_key)') { return $true }
    return $false
}

try {
    Add-ReportLine '# Codex Skills Sync Report'
    Add-ReportLine ('[F] DryRun={0}' -f $DryRun)
    Add-ReportLine ('[F] Backup={0}' -f $Backup)

    $source = Resolve-Path -LiteralPath $SourcePath -ErrorAction Stop
    $sourcePathFull = $source.Path
    $targetPathFull = [System.IO.Path]::GetFullPath($TargetPath)
    Add-ReportLine ('[F] SourcePath={0}' -f $sourcePathFull)
    Add-ReportLine ('[F] TargetPath={0}' -f $targetPathFull)

    $files = Get-ChildItem -LiteralPath $sourcePathFull -Recurse -File -Force |
        Where-Object { $_.FullName -notmatch '\\.git(\\|$)' }

    if ($null -eq $files -or @($files).Count -eq 0) {
        Add-ReportLine '[WARN] [S] No files found in source.'
    }

    if (-not $DryRun) {
        if ($Backup) {
            $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
            $backupPath = ('{0}.backup-{1}' -f $targetPathFull.TrimEnd('\'), $timestamp)
            if (Test-Path -LiteralPath $targetPathFull) {
                Copy-Item -LiteralPath $targetPathFull -Destination $backupPath -Recurse -Force
                Add-ReportLine ('[PASS] [F] Backup created before apply: {0}' -f $backupPath)
            } else {
                Add-ReportLine '[WARN] [S] Target does not exist before apply; backup skipped.'
            }
        } else {
            Add-ReportLine '[WARN] [S] Backup disabled by parameter.'
        }
    }

    $blocked = 0
    $planned = 0
    foreach ($file in $files) {
        $relative = Get-RelativePathSafe -BasePath $sourcePathFull -ChildPath $file.FullName
        $destination = Join-Path $targetPathFull $relative
        if (Test-ForbiddenSkillFile -Path $file.FullName) {
            $blocked += 1
            Add-ReportLine ('[WARN] [S] Blocked suspicious file: {0}' -f $relative)
            continue
        }
        $planned += 1
        if ($DryRun) {
            Add-ReportLine ('[DRYRUN] [S] Would copy: {0}' -f $relative)
        } else {
            $destinationDirectory = Split-Path -Parent $destination
            if (-not (Test-Path -LiteralPath $destinationDirectory)) {
                New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
            }
            Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
            Add-ReportLine ('[PASS] [F] Copied: {0}' -f $relative)
        }
    }

    Add-ReportLine ('[F] PlannedOrCopiedFiles={0}' -f $planned)
    Add-ReportLine ('[S] BlockedSuspiciousFiles={0}' -f $blocked)
    Add-ReportLine '[F] Unmanaged target files were not deleted.'

    if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {
        $reportFull = [System.IO.Path]::GetFullPath($ReportPath)
        $reportDir = Split-Path -Parent $reportFull
        if (-not (Test-Path -LiteralPath $reportDir)) {
            New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        }
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($reportFull, ($report -join [Environment]::NewLine), $utf8NoBom)
        Write-Output ('PASS: [F] Report written: {0}' -f $reportFull)
    }

    if ($DryRun) {
        Add-ReportLine '[WARN] [S] Dry-run only. No files copied.'
    }

    exit 0
} catch {
    Add-ReportLine ('[FAIL] [F] {0}' -f $_.Exception.Message)
    if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {
        try {
            $reportFull = [System.IO.Path]::GetFullPath($ReportPath)
            $reportDir = Split-Path -Parent $reportFull
            if (-not (Test-Path -LiteralPath $reportDir)) {
                New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
            }
            $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($reportFull, ($report -join [Environment]::NewLine), $utf8NoBom)
        } catch {
            Write-Output ('WARN: [S] Could not write failure report: {0}' -f $_.Exception.Message)
        }
    }
    exit 1
}