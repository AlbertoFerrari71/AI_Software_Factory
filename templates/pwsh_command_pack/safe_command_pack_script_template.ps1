#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$PackName = "step-XXXX-safe-command-pack-example"
$OutputRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunId = "{0}-{1}" -f $Stamp, $PackName
$OutDir = Join-Path $OutputRoot $RunId
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$FullOutputPath = Join-Path $OutDir ("{0}-Output_Completo_{1}.txt" -f $Stamp, $PackName)
$CompactOutputPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.md" -f $Stamp, $PackName)
$DocxOutputPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx" -f $Stamp, $PackName)
$DocxFailedPath = Join-Path $OutDir ("{0}-Output_Compatto_{1}.docx.failed.txt" -f $Stamp, $PackName)
$LastFullOutputPath = Join-Path $OutputRoot "LAST-Output_Completo.txt"
$LastCompactOutputPath = Join-Path $OutputRoot "LAST-Output_Compatto.md"
$LastDocxOutputPath = Join-Path $OutputRoot "LAST-Output_Compatto.docx"
$LastDocxFailedPath = Join-Path $OutputRoot "LAST-Output_Compatto.docx.failed.txt"

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Message
    )

    $Line = "[{0}] {1}" -f (Get-Date -Format o), $Message
    Add-Content -LiteralPath $FullOutputPath -Value $Line -Encoding utf8
    Write-Host $Message
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [Parameter()]
        [string[]] $Arguments = @(),

        [Parameter()]
        [int[]] $AllowedExitCodes = @(0),

        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    Write-Log ("START {0}: {1} {2}" -f $Label, $FileName, ($Arguments -join " "))

    $StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = $FileName
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    foreach ($Argument in $Arguments) {
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
        Stdout = $Stdout
        Stderr = $Stderr
    }
}

function Test-BranchExists {
    param(
        [Parameter(Mandatory = $true)]
        [string] $BranchName
    )

    $Result = Invoke-NativeCommand -FileName "git" -Arguments @("rev-parse", "--verify", $BranchName) -AllowedExitCodes @(0, 128) -Label "branch exists check"
    return ($Result.ExitCode -eq 0)
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
    Write-Log "Use branch + PR for publication to main. Never use direct push to main as the default."
    Write-Log "If local main is ahead of origin/main, create and push a publish branch, open PR, merge PR, realign main, then verify."

    [void] (Invoke-NativeCommand -FileName "git" -Arguments @("--no-pager", "status", "--short", "--branch") -AllowedExitCodes @(0) -Label "git status")

    # Add step-specific commands here. Use Invoke-NativeCommand for native tools.
    # Treat LF/CRLF warnings as controlled warnings only when diff-check, tests, health and verify pass.

    New-CompactReport -Status "COMPLETED_OR_READY_FOR_REVIEW" -WarningText "DOCX is best-effort and non-blocking."
    [void] (Write-DocxBestEffort -CompactPath $CompactOutputPath -DocxPath $DocxOutputPath -FailedPath $DocxFailedPath)
} catch {
    Write-Log ("ERROR: {0}" -f $_.Exception.Message)
    New-CompactReport -Status "FAILED" -WarningText $_.Exception.Message
    [void] (Write-DocxBestEffort -CompactPath $CompactOutputPath -DocxPath $DocxOutputPath -FailedPath $DocxFailedPath)
    throw
}

Copy-Item -LiteralPath $FullOutputPath -Destination $LastFullOutputPath -Force
Copy-Item -LiteralPath $CompactOutputPath -Destination $LastCompactOutputPath -Force
if (Test-Path -LiteralPath $DocxOutputPath) {
    Copy-Item -LiteralPath $DocxOutputPath -Destination $LastDocxOutputPath -Force
}
if (Test-Path -LiteralPath $DocxFailedPath) {
    Copy-Item -LiteralPath $DocxFailedPath -Destination $LastDocxFailedPath -Force
}
Set-Clipboard -Value (Get-Content -LiteralPath $CompactOutputPath -Raw)
