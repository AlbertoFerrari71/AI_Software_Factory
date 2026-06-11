<#
.SYNOPSIS
Creates or previews the shared Alberto/Luca Bridge folder structure.

.DESCRIPTION
[F] Safe-by-default: WhatIfMode defaults to true, so the script previews actions.
[F] The script never deletes files or folders.
[S] Use -WhatIfMode:$false only after manual review of the preview.
[O] Prefer running this first with default parameters and saving the output as evidence.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $false)]
    [string]$RootPath = 'D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge_Shared',

    [Parameter(Mandatory = $false)]
    [string[]]$Projects = @(
        'AI_Software_Factory',
        'AI_Release_Radar',
        'ASF_Blueprint_Studio',
        'Codex_Skills'
    ),

    [Parameter(Mandatory = $false)]
    [string[]]$Users = @('alberto', 'luca'),

    [Parameter(Mandatory = $false)]
    [bool]$WhatIfMode = $true
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Write-BridgeLine {
    param(
        [Parameter(Mandatory = $true)][string]$Level,
        [Parameter(Mandatory = $true)][string]$Message
    )
    Write-Output ("{0}: {1}" -f $Level, $Message)
}

function Add-DirectoryPlan {
    param(
        [Parameter(Mandatory = $true)][System.Collections.Generic.List[string]]$Plan,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Plan.Add($Path) | Out-Null
}

try {
    if ([string]::IsNullOrWhiteSpace($RootPath)) {
        throw 'RootPath is empty.'
    }

    $resolvedRootParent = Split-Path -Parent $RootPath
    if ([string]::IsNullOrWhiteSpace($resolvedRootParent)) {
        throw 'RootPath must include a parent directory.'
    }

    $plan = New-Object 'System.Collections.Generic.List[string]'
    Add-DirectoryPlan -Plan $plan -Path $RootPath
    foreach ($shared in @('_shared_docs', '_handoff', '_templates')) {
        Add-DirectoryPlan -Plan $plan -Path (Join-Path $RootPath $shared)
    }

    foreach ($project in $Projects) {
        if ([string]::IsNullOrWhiteSpace($project)) { continue }
        $projectRoot = Join-Path $RootPath $project
        Add-DirectoryPlan -Plan $plan -Path $projectRoot
        foreach ($user in $Users) {
            if ([string]::IsNullOrWhiteSpace($user)) { continue }
            $userRoot = Join-Path $projectRoot $user
            Add-DirectoryPlan -Plan $plan -Path $userRoot
            Add-DirectoryPlan -Plan $plan -Path (Join-Path $userRoot 'codex_command')
            Add-DirectoryPlan -Plan $plan -Path (Join-Path $userRoot 'pwsh_command')
        }
        Add-DirectoryPlan -Plan $plan -Path (Join-Path $projectRoot 'shared_reports')
    }

    Write-BridgeLine -Level 'INFO' -Message '[F] Shared Bridge structure plan generated.'
    Write-BridgeLine -Level 'INFO' -Message ('[F] RootPath={0}' -f $RootPath)
    Write-BridgeLine -Level 'INFO' -Message ('[F] WhatIfMode={0}' -f $WhatIfMode)

    foreach ($directory in $plan) {
        if (Test-Path -LiteralPath $directory) {
            Write-BridgeLine -Level 'PASS' -Message ("[F] Exists: {0}" -f $directory)
            continue
        }

        if ($WhatIfMode) {
            Write-BridgeLine -Level 'DRYRUN' -Message ("[S] Would create: {0}" -f $directory)
            continue
        }

        if ($PSCmdlet.ShouldProcess($directory, 'Create directory')) {
            New-Item -ItemType Directory -Path $directory -Force | Out-Null
            Write-BridgeLine -Level 'PASS' -Message ("[F] Created: {0}" -f $directory)
        }
    }

    if ($WhatIfMode) {
        Write-BridgeLine -Level 'WARN' -Message '[S] Dry-run only. Re-run with -WhatIfMode:$false to create folders after approval.'
    } else {
        Write-BridgeLine -Level 'PASS' -Message '[F] Apply completed without delete operations.'
    }

    exit 0
} catch {
    Write-BridgeLine -Level 'FAIL' -Message ("[F] {0}" -f $_.Exception.Message)
    exit 1
}