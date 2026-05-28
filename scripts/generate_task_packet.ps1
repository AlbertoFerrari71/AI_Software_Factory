param(
    [Parameter(Mandatory = $true)]
    [string]$Step,

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [Parameter(Mandatory = $true)]
    [string]$Branch,

    [Parameter(Mandatory = $true)]
    [string]$Objective,

    [string]$Output,

    [switch]$Print,

    [switch]$Force,

    [switch]$StrictReady
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$PythonGenerator = Join-Path $RepoRoot "scripts\generate_task_packet.py"

$CliArgs = @(
    $PythonGenerator,
    "--step", $Step,
    "--title", $Title,
    "--branch", $Branch,
    "--objective", $Objective
)

if ($Output) {
    $CliArgs += @("--output", $Output)
}

if ($Print) {
    $CliArgs += "--print"
}

if ($Force) {
    $CliArgs += "--force"
}

if ($StrictReady) {
    $CliArgs += "--strict-ready"
}

Write-Host "Running Prompt Packet Generator..."
& python @CliArgs
exit $LASTEXITCODE
