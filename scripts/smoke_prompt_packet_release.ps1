param(
    [string]$Output = "tmp\smoke_prompt_packet_release.md",
    [string]$Step = "190",
    [string]$Title = "Prompt Packet Generator Release Smoke Workflow",
    [string]$Branch = "step-190-prompt-packet-generator-release-smoke-workflow",
    [string]$Objective = "Verify the prompt packet generator release smoke workflow locally."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host ""
    Write-Host "==> $Message"
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,

        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage Exit code: $LASTEXITCODE"
    }
}

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
    $RepoRootPath = [System.IO.Path]::GetFullPath($RepoRoot.Path)
    $TmpRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRootPath "tmp"))

    if ([System.IO.Path]::IsPathRooted($Output)) {
        $OutputPath = [System.IO.Path]::GetFullPath($Output)
    }
    else {
        $OutputPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRootPath $Output))
    }

    $TrimChars = [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $TmpRootWithSeparator = $TmpRoot.TrimEnd($TrimChars) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $OutputPath.StartsWith($TmpRootWithSeparator, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Smoke output must be inside the repository tmp directory: $TmpRoot"
    }

    $GeneratorWrapper = Join-Path $RepoRootPath "scripts\generate_task_packet.ps1"
    $Validator = Join-Path $RepoRootPath "scripts\validate_task_packet.py"

    Write-Host "Prompt Packet Generator Release Smoke Workflow"
    Write-Host "Output: $OutputPath"

    Write-Step "Generate smoke task packet"
    Invoke-Native -FailureMessage "Task packet generation failed." -Command {
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $GeneratorWrapper `
            -Step $Step `
            -Title $Title `
            -Branch $Branch `
            -Objective $Objective `
            -Output $OutputPath `
            -Force `
            -StrictReady
    }

    Write-Step "Validate smoke task packet with Lite Mode"
    Invoke-Native -FailureMessage "Lite validation failed." -Command {
        & python $Validator $OutputPath
    }

    Write-Step "Validate smoke task packet with Strict Mode"
    Invoke-Native -FailureMessage "Strict validation failed." -Command {
        & python $Validator --strict $OutputPath
    }

    Write-Host ""
    Write-Host "Prompt Packet Generator Release Smoke Workflow PASSED"
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
