Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Message
    )

    Write-Host ""
    Write-Host "==> $Message"
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Label,

        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    Write-Step $Label
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Verification step failed: $Label"
    }
}

try {
    Write-Host "Verification Gate"

    Invoke-CheckedCommand "Python version" { python --version }
    Invoke-CheckedCommand "pytest version" { python -m pytest --version }
    Invoke-CheckedCommand "Run pytest" { python -m pytest }
    Invoke-CheckedCommand "Check diff whitespace" { git diff --check }
    Invoke-CheckedCommand "Show git status" { git status --short }

    Write-Host ""
    Write-Host "Verification Gate PASSED"
}
catch {
    Write-Host ""
    Write-Error "Verification Gate FAILED. $($_.Exception.Message)"
    exit 1
}
