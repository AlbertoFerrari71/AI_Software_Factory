#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$PackName = "step-XXXX-safe-command-pack-example"
$StepNumber = "NNNN"
$Iteration = "01"
$ArtifactPrefix = "{0}-{1}" -f $StepNumber, $Iteration
$OutputRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunId = "{0}-{1}" -f $Stamp, $PackName
$OutDir = Join-Path $OutputRoot $RunId
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$FullOutputPath = Join-Path $OutDir ("{0}-Output_Completo_{1}.txt" -f $ArtifactPrefix, $PackName)
$CompactOutputPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.md" -f $ArtifactPrefix, $PackName)
$DocxOutputPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx" -f $ArtifactPrefix, $PackName)
$DocxFailedPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx.failed.txt" -f $ArtifactPrefix, $PackName)
$AllowedPaths = @(
    "README.md",
    "CHANGELOG.md",
    "docs/",
    "templates/pwsh_command_pack/",
    "tests/unit/"
)

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Message
    )

    $Line = "[{0}] {1}" -f (Get-Date -Format o), $Message
    Add-Content -LiteralPath $FullOutputPath -Value $Line -Encoding utf8
    Write-Host $Message
}

function Test-NativeCommandInput {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [Parameter()]
        [string[]] $ArgList = @(),

        [Parameter()]
        [int[]] $AllowedExitCodes = @(0),

        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    if ([string]::IsNullOrWhiteSpace($FileName)) {
        throw ("Native command file name is empty for label: {0}" -f $Label)
    }
    if ([string]::IsNullOrWhiteSpace($Label)) {
        throw "Native command label is empty."
    }
    if ($null -eq $ArgList) {
        throw ("Native command ArgList is null for label: {0}" -f $Label)
    }
    if ($null -eq $AllowedExitCodes -or $AllowedExitCodes.Count -eq 0) {
        throw ("Native command allowed exit codes are empty for label: {0}" -f $Label)
    }

    for ($Index = 0; $Index -lt $ArgList.Count; $Index++) {
        $Argument = $ArgList[$Index]
        if ($null -eq $Argument) {
            throw ("Native command argument {0} is null for label: {1}" -f $Index, $Label)
        }
        if ([string]::IsNullOrWhiteSpace($Argument)) {
            throw ("Native command argument {0} is empty for label: {1}" -f $Index, $Label)
        }
    }
}

function Format-NativeCommandForLog {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [Parameter()]
        [string[]] $ArgList = @()
    )

    $RenderedArgs = @()
    foreach ($Argument in $ArgList) {
        if ($Argument -match "\s") {
            $RenderedArgs += ('"{0}"' -f ($Argument -replace '"', '\"'))
        }
        if ($Argument -notmatch "\s") {
            $RenderedArgs += $Argument
        }
    }

    return ("{0} {1}" -f $FileName, ($RenderedArgs -join " ")).Trim()
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [Parameter()]
        [string[]] $ArgList = @(),

        [Parameter()]
        [int[]] $AllowedExitCodes = @(0),

        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    Test-NativeCommandInput -FileName $FileName -ArgList $ArgList -AllowedExitCodes $AllowedExitCodes -Label $Label
    $RenderedCommand = Format-NativeCommandForLog -FileName $FileName -ArgList $ArgList
    Write-Log ("START {0}: {1}" -f $Label, $RenderedCommand)

    $StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = $FileName
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    foreach ($Argument in $ArgList) {
        [void] $StartInfo.ArgumentList.Add($Argument)
    }

    $Process = [System.Diagnostics.Process]::new()
    $Process.StartInfo = $StartInfo
    [void] $Process.Start()
    $Stdout = $Process.StandardOutput.ReadToEnd()
    $Stderr = $Process.StandardError.ReadToEnd()
    $Process.WaitForExit()

    if (-not [string]::IsNullOrWhiteSpace($Stdout)) {
        Add-Content -LiteralPath $FullOutputPath -Value $Stdout -Encoding utf8
    }
    if (-not [string]::IsNullOrWhiteSpace($Stderr)) {
        Add-Content -LiteralPath $FullOutputPath -Value ("STDERR: {0}" -f $Stderr) -Encoding utf8
    }

    Write-Log ("END {0}: exit {1}" -f $Label, $Process.ExitCode)

    if ($AllowedExitCodes -notcontains $Process.ExitCode) {
        throw ("{0} failed with exit code {1}" -f $Label, $Process.ExitCode)
    }

    [pscustomobject]@{
        Label = $Label
        ExitCode = $Process.ExitCode
        AllowedExitCodes = $AllowedExitCodes
        Stdout = $Stdout
        Stderr = $Stderr
    }
}

function Run {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [Parameter()]
        [string[]] $ArgList = @(),

        [Parameter(Mandatory = $true)]
        [string] $Label,

        [Parameter()]
        [switch] $CaptureOutput
    )

    Test-NativeCommandInput -FileName $FileName -ArgList $ArgList -AllowedExitCodes @(0) -Label $Label
    $RenderedCommand = Format-NativeCommandForLog -FileName $FileName -ArgList $ArgList
    Write-Log ("START {0}: {1}" -f $Label, $RenderedCommand)

    if ($CaptureOutput) {
        $Output = & $FileName @ArgList
    } else {
        & $FileName @ArgList
        $Output = @()
    }

    $ExitCode = $LASTEXITCODE
    if ($null -eq $ExitCode) {
        throw ("{0} did not produce a native LASTEXITCODE." -f $Label)
    }

    Write-Log ("END {0}: exit {1}" -f $Label, $ExitCode)
    if ($ExitCode -ne 0) {
        throw ("{0} failed with exit code {1}" -f $Label, $ExitCode)
    }

    if ($CaptureOutput) {
        return (($Output | Out-String).Trim())
    }
}

function Invoke-AsfPublishConfigRunnerFlow {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ConfigPath,

        [Parameter(Mandatory = $true)]
        [string] $BranchName,

        [Parameter()]
        [string] $RunnerPath = "scripts/asf_publish_step.ps1",

        [Parameter()]
        [string] $LastCompactPath = ""
    )

    if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
        throw "ASF publish config path is empty."
    }
    if ([string]::IsNullOrWhiteSpace($BranchName)) {
        throw "ASF publish branch name is empty."
    }
    if ([string]::IsNullOrWhiteSpace($RunnerPath)) {
        throw "ASF publish runner path is empty."
    }

    if (-not (Test-Path -Path $ConfigPath)) {
        throw ("ASF publish config does not exist: {0}" -f $ConfigPath)
    }
    if (-not (Test-Path -Path $RunnerPath)) {
        throw ("ASF publish runner does not exist: {0}" -f $RunnerPath)
    }

    Write-Log "ASF publish flow: PrepareConfig/scope discovery -> human scope review -> explicit config JSON + scripts/asf_publish_step.ps1 + Phase B -> PR recovery -> Phase C."
    Write-Log "Recommended preflight: run scripts/asf_publish_step.ps1 -Phase PrepareConfig, review expected_files and changed_files, then use the reviewed config."
    Write-Log "If the runner reports out-of-scope changes, stop and review the recovery report or suggested config; do not force scope automatically."
    Write-Log "ASF publish config must declare expected_files and changed_files explicitly; do not infer scope by parsing git status --short."
    Write-Log "LF/CRLF warnings are not out-of-scope files when tests, workflow health check, verify gate, and git --no-pager diff --check pass."
    Write-Log "DOCX/accessory outputs are best-effort and must not invalidate a publish already verified by final gates."
    Write-Log "Bridge/LAST primary-path locks use retry, then timestamped fallback, then COMPLETATO CON WARNING NON BLOCCANTE after required gates pass."
    Write-Log "After a successful human-gated publish, include or point to a post-publish evidence pack with PR, merge commit, checks, Bridge outputs, LAST files, accepted warnings and next step; do not turn the pack into commit/push/merge automation."
    Write-Log "The ASF publish runner owns its standard Bridge outputs; external wrappers must not Start-Transcript to the runner Output_Completo file."
    Write-Log "If an external transcript is needed, use a distinct NNNN-Wrapper_Log_*.txt file."
    Write-Log "Do not use Get-Command -Path or AST parsing to infer publish runner parameters."

    Run -FileName "pwsh" -ArgList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $RunnerPath,
        "-Config",
        $ConfigPath,
        "-Phase",
        "B",
        "-ApprovePublish"
    ) -Label "ASF publish Phase B"

    $PrNumber = Run -FileName "gh" -ArgList @(
        "pr",
        "list",
        "--head",
        $BranchName,
        "--json",
        "number",
        "--jq",
        ".[0].number"
    ) -Label "Recover ASF publish PR number" -CaptureOutput

    if ([string]::IsNullOrWhiteSpace($PrNumber)) {
        throw "ASF publish PR number is empty after gh pr list --head."
    }
    if ($PrNumber -notmatch "^\d+$") {
        throw ("ASF publish PR number is not numeric: {0}" -f $PrNumber)
    }

    Run -FileName "pwsh" -ArgList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $RunnerPath,
        "-Config",
        $ConfigPath,
        "-Phase",
        "C",
        "-PrNumber",
        $PrNumber,
        "-ApproveMerge"
    ) -Label "ASF publish Phase C"

    Run -FileName "python" -ArgList @("-m", "pytest") -Label "final pytest"
    Run -FileName "python" -ArgList @("scripts/check_workflow_health.py") -Label "final workflow health"
    Run -FileName "pwsh" -ArgList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1") -Label "final verify gate"
    Run -FileName "git" -ArgList @("--no-pager", "diff", "--check") -Label "final diff check"
    Run -FileName "git" -ArgList @("--no-pager", "status", "--short") -Label "final git status"

    Write-Log "COMPLETATO after final ASF publish gates passed."
}

function Test-BranchExists {
    param(
        [Parameter(Mandatory = $true)]
        [string] $BranchName
    )

    $Result = Invoke-NativeCommand -FileName "git" -ArgList @("rev-parse", "--verify", $BranchName) -AllowedExitCodes @(0, 128) -Label "branch exists check"
    return ($Result.ExitCode -eq 0)
}

function Get-GitPorcelainStatus {
    $Result = Invoke-NativeCommand -FileName "git" -ArgList @("status", "--porcelain=v1", "--untracked-files=all") -AllowedExitCodes @(0) -Label "git porcelain status"
    $Entries = @()
    foreach ($Line in ($Result.Stdout -split "\r?\n")) {
        if ([string]::IsNullOrWhiteSpace($Line)) {
            continue
        }
        if ($Line -notmatch "^(?<Status>.{2}) (?<Path>.+)$") {
            throw ("Unexpected git porcelain status line: {0}" -f $Line)
        }
        $PathValue = $Matches["Path"]
        if ($PathValue.Contains(" -> ")) {
            $PathValue = ($PathValue -split " -> ", 2)[1]
        }
        $Entries += [pscustomobject]@{
            Status = $Matches["Status"]
            Path = $PathValue.Trim('"')
        }
    }
    return $Entries
}

function Test-GitScope {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $AllowedPathList
    )

    $Entries = Get-GitPorcelainStatus
    foreach ($Entry in $Entries) {
        $NormalizedPath = ($Entry.Path -replace "\\", "/")
        $InScope = $false
        foreach ($AllowedPath in $AllowedPathList) {
            $NormalizedAllowedPath = ($AllowedPath -replace "\\", "/")
            if ($NormalizedPath -eq $NormalizedAllowedPath -or $NormalizedPath.StartsWith($NormalizedAllowedPath)) {
                $InScope = $true
                break
            }
        }
        if (-not $InScope) {
            throw ("Git scope guard blocked out-of-scope path: {0}" -f $Entry.Path)
        }
    }
    return $Entries
}

function New-CompactReport {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Status,

        [Parameter(Mandatory = $true)]
        [string] $WarningText
    )

    $Fence = -join @([char]96, [char]96, [char]96)
    $Tail = @()
    if (Test-Path -LiteralPath $FullOutputPath) {
        $Tail = Get-Content -LiteralPath $FullOutputPath -Tail 80
    }
    if ($Tail.Count -eq 0) {
        $Tail = @("Full output missing or empty.")
    }

    $Lines = @(
        "# Safe Bootstrap PowerShell Command Pack",
        "",
        "- Pack: $PackName",
        "- Status: $Status",
        "- Generated: $(Get-Date -Format o)",
        "- Full output: $FullOutputPath",
        "- Warning: $WarningText",
        "",
        "## Tail",
        $Fence
    )
    $Lines += $Tail
    $Lines += $Fence

    Set-Content -LiteralPath $CompactOutputPath -Value $Lines -Encoding utf8
    $CompactInfo = Get-Item -LiteralPath $CompactOutputPath
    if ($CompactInfo.Length -eq 0) {
        $Fallback = @(
            "# Safe Bootstrap PowerShell Command Pack",
            "",
            "- Pack: $PackName",
            "- Status: FALLBACK",
            "- Full output: $FullOutputPath",
            "- Warning: compact report fallback was required."
        )
        Set-Content -LiteralPath $CompactOutputPath -Value $Fallback -Encoding utf8
    }
}

function Write-DocxBestEffort {
    param(
        [Parameter(Mandatory = $true)]
        [string] $CompactPath,

        [Parameter(Mandatory = $true)]
        [string] $DocxPath,

        [Parameter(Mandatory = $true)]
        [string] $FailedPath
    )

    if (-not (Test-Path -LiteralPath $CompactPath)) {
        Set-Content -LiteralPath $FailedPath -Value "DOCX skipped: compact Markdown missing." -Encoding utf8
        return $false
    }

    try {
        $TempDir = Join-Path $OutDir ("docx_tmp_{0}" -f ([guid]::NewGuid().ToString("N")))
        $RelsDir = Join-Path $TempDir "_rels"
        $WordDir = Join-Path $TempDir "word"
        New-Item -ItemType Directory -Path $RelsDir -Force | Out-Null
        New-Item -ItemType Directory -Path $WordDir -Force | Out-Null

        $CompactText = Get-Content -LiteralPath $CompactPath -Raw
        $EscapedText = [System.Security.SecurityElement]::Escape($CompactText)
        $ContentTypes = @(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '<Default Extension="xml" ContentType="application/xml"/>',
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
            '</Types>'
        )
        $Rels = @(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>',
            '</Relationships>'
        )
        $DocumentXml = @(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">',
            '<w:body>',
            '<w:p><w:r><w:t xml:space="preserve">',
            $EscapedText,
            '</w:t></w:r></w:p>',
            '</w:body>',
            '</w:document>'
        )

        Set-Content -LiteralPath (Join-Path $TempDir "[Content_Types].xml") -Value $ContentTypes -Encoding utf8
        Set-Content -LiteralPath (Join-Path $RelsDir ".rels") -Value $Rels -Encoding utf8
        Set-Content -LiteralPath (Join-Path $WordDir "document.xml") -Value $DocumentXml -Encoding utf8
        Compress-Archive -Path (Join-Path $TempDir "*") -DestinationPath $DocxPath -Force
        return $true
    } catch {
        $Message = "DOCX generation failed without blocking publication: {0}" -f $_.Exception.Message
        Set-Content -LiteralPath $FailedPath -Value $Message -Encoding utf8
        Write-Log $Message
        return $false
    }
}

try {
    Set-Content -LiteralPath $FullOutputPath -Value @("Safe command pack started: $(Get-Date -Format o)") -Encoding utf8
    Write-Log "Use progressive artifacts only: NNNN-II-Tipo_Nome.ext. Do not generate or read LAST-* artifacts."
    Write-Log "Use branch + PR for publication to main. Never use direct push to main as the default."
    Write-Log "If local main is ahead of origin/main, create and push a publish branch, open PR, merge PR, realign main, then verify."
    Write-Log "Use git status --porcelain=v1 --untracked-files=all before scope-sensitive git add operations."
    Write-Log "Use ArgList as the native-command argument parameter name; do not use the PowerShell automatic variable name."
    Write-Log "Native command guardrail: reject empty FileName, empty Label, null ArgList, empty ArgList entries and empty AllowedExitCodes before execution."
    Write-Log "Native command guardrail: success means exit code is explicitly listed in AllowedExitCodes; stderr is logged and classified with context."
    Write-Log "Do not write COMPLETATO until every native command and verification gate has passed with exit code 0 or an explicit allowed exit code."
    Write-Log "Do not use Start-Transcript on an Output_Completo path owned by scripts/asf_publish_step.ps1; use NNNN-Wrapper_Log_*.txt for wrapper logs."

    [void] (Invoke-NativeCommand -FileName "git" -ArgList @("--no-pager", "status", "--short", "--branch") -AllowedExitCodes @(0) -Label "git status")
    [void] (Test-GitScope -AllowedPathList $AllowedPaths)

    # Add step-specific commands here. Use Invoke-NativeCommand for native tools.
    # Use Invoke-NativeCommand -FileName "python" -ArgList @("-m", "pytest") for tests.
    # Use Invoke-NativeCommand -FileName "python" -ArgList @("scripts/check_workflow_health.py") for health check.
    # Use Invoke-NativeCommand -FileName "pwsh" -ArgList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1") for verify gate.
    # Use git --no-pager for long output and publish to main by branch + PR only when explicitly requested.
    # Treat LF/CRLF warnings as controlled warnings only when diff-check, tests, health and verify pass.

    New-CompactReport -Status "COMPLETED_AFTER_ALL_NATIVE_GUARDRAILS" -WarningText "DOCX is best-effort and non-blocking."
    [void] (Write-DocxBestEffort -CompactPath $CompactOutputPath -DocxPath $DocxOutputPath -FailedPath $DocxFailedPath)
} catch {
    Write-Log ("ERROR: {0}" -f $_.Exception.Message)
    New-CompactReport -Status "FAILED" -WarningText $_.Exception.Message
    [void] (Write-DocxBestEffort -CompactPath $CompactOutputPath -DocxPath $DocxOutputPath -FailedPath $DocxFailedPath)
    throw
}
