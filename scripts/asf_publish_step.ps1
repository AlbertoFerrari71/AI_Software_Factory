param(
    [string]$Config,
    [ValidateSet("Plan", "A", "B", "C")]
    [string]$Phase = "Plan",
    [switch]$ApprovePublish,
    [switch]$ApproveMerge,
    [int]$PrNumber = 0,
    [string]$BridgeRoot,
    [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DefaultBridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
$script:LogLines = [System.Collections.Generic.List[string]]::new()
$script:WarningLines = [System.Collections.Generic.List[string]]::new()
$script:PrNumber = $null
$publishConfig = $null

function Resolve-InputPath {
    param([string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

function Write-Log {
    param([string]$Message)
    $line = ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message)
    $script:LogLines.Add($line)
    Write-Host $line
}

function Add-WarningLine {
    param([string]$Message)
    $script:WarningLines.Add($Message)
    Write-Warning $Message
}

function Test-HasProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    return ($Object.PSObject.Properties.Name -contains $Name)
}

function Assert-StringProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    if (-not (Test-HasProperty -Object $Object -Name $Name)) {
        throw "Missing config field: $Name"
    }
    $value = [string]$Object.$Name
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Config field must not be empty: $Name"
    }
    return $value
}

function Get-ConfigArray {
    param(
        [object]$Object,
        [string]$Name
    )
    if (-not (Test-HasProperty -Object $Object -Name $Name)) {
        throw "Missing config field: $Name"
    }
    return @($Object.$Name)
}

function Read-PublishConfig {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "-Config is required unless -SelfTest is used."
    }
    $resolved = Resolve-InputPath -Path $Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "Config file not found: $resolved"
    }
    $raw = Get-Content -Path $resolved -Raw
    $configObject = $raw | ConvertFrom-Json
    $configObject | Add-Member -NotePropertyName "_config_path" -NotePropertyValue $resolved -Force
    return $configObject
}

function Assert-ArgvCommand {
    param(
        [object]$Command,
        [string]$FieldName
    )
    if (-not (Test-HasProperty -Object $Command -Name "name")) {
        throw "$FieldName command is missing name."
    }
    if (-not (Test-HasProperty -Object $Command -Name "argv")) {
        throw "$FieldName command '$($Command.name)' is missing argv."
    }
    if ((Test-HasProperty -Object $Command -Name "shell") -and ([bool]$Command.shell)) {
        throw "$FieldName command '$($Command.name)' requests shell execution. Shell execution is disabled."
    }
    $argv = @($Command.argv)
    if (@($argv).Count -eq 0) {
        throw "$FieldName command '$($Command.name)' has empty argv."
    }
    foreach ($item in $argv) {
        if (-not ($item -is [string]) -or [string]::IsNullOrWhiteSpace($item)) {
            throw "$FieldName command '$($Command.name)' contains a non-string or empty argv item."
        }
    }
}

function Assert-PublishConfig {
    param([object]$PublishConfig)
    [void](Assert-StringProperty -Object $PublishConfig -Name "step")
    [void](Assert-StringProperty -Object $PublishConfig -Name "name")
    [void](Assert-StringProperty -Object $PublishConfig -Name "branch")
    [void](Assert-StringProperty -Object $PublishConfig -Name "commit_message")
    [void](Assert-StringProperty -Object $PublishConfig -Name "pr_title")
    [void](Assert-StringProperty -Object $PublishConfig -Name "pr_body")
    [void](Assert-StringProperty -Object $PublishConfig -Name "next_step")

    $expectedFiles = @(Get-ConfigArray -Object $PublishConfig -Name "expected_files")
    if (@($expectedFiles).Count -eq 0) {
        throw "expected_files must not be empty."
    }
    foreach ($file in $expectedFiles) {
        if (-not ($file -is [string]) -or [string]::IsNullOrWhiteSpace($file)) {
            throw "expected_files contains a non-string or empty value."
        }
    }

    foreach ($command in @(Get-ConfigArray -Object $PublishConfig -Name "phase_a_checks")) {
        Assert-ArgvCommand -Command $command -FieldName "phase_a_checks"
    }
    foreach ($command in @(Get-ConfigArray -Object $PublishConfig -Name "phase_c_checks")) {
        Assert-ArgvCommand -Command $command -FieldName "phase_c_checks"
    }

    if (-not (Test-HasProperty -Object $PublishConfig -Name "allow_no_github_checks_reported")) {
        throw "Missing config field: allow_no_github_checks_reported"
    }
    if (-not (Test-HasProperty -Object $PublishConfig -Name "log_max_count")) {
        throw "Missing config field: log_max_count"
    }
}

function Get-RepoPath {
    param([object]$PublishConfig)
    if ((Test-HasProperty -Object $PublishConfig -Name "repo_path") -and -not [string]::IsNullOrWhiteSpace([string]$PublishConfig.repo_path)) {
        return Resolve-InputPath -Path ([string]$PublishConfig.repo_path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
}

function Assert-Repo {
    param([string]$RepoPath)
    if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
        throw "Repository path does not exist: $RepoPath"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $RepoPath ".git"))) {
        throw "Repository path is not a Git repository: $RepoPath"
    }
}

function Normalize-GitPath {
    param([string]$PathText)
    $value = $PathText.Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
        try {
            $value = $value | ConvertFrom-Json
        } catch {
            $value = $value.Trim('"')
        }
    }
    $value = $value.Replace("\", "/")
    while ($value.StartsWith("./")) {
        $value = $value.Substring(2)
    }
    return $value
}

function Get-GitStatusPaths {
    param([string]$RepoPath)
    Push-Location $RepoPath
    try {
        $lines = & git @("status", "--porcelain=v1", "--untracked-files=all") 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to read git status: $($lines -join [Environment]::NewLine)"
        }
    } finally {
        Pop-Location
    }

    $paths = [System.Collections.Generic.List[string]]::new()
    foreach ($line in @($lines)) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) {
            continue
        }
        $rawPath = $line.Substring(3)
        if ($rawPath.Contains(" -> ")) {
            foreach ($part in ($rawPath -split " -> ", 2)) {
                $paths.Add((Normalize-GitPath -PathText $part))
            }
        } else {
            $paths.Add((Normalize-GitPath -PathText $rawPath))
        }
    }
    return @($paths | Select-Object -Unique)
}

function Test-PathExpected {
    param(
        [string]$PathText,
        [string[]]$ExpectedFiles
    )
    $path = Normalize-GitPath -PathText $PathText
    foreach ($expectedRaw in $ExpectedFiles) {
        $expected = Normalize-GitPath -PathText $expectedRaw
        if ($expected.EndsWith("/**")) {
            $prefix = $expected.Substring(0, $expected.Length - 3)
            if ($path.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                return $true
            }
        } elseif ($expected.Contains("*") -or $expected.Contains("?")) {
            $pattern = [System.Management.Automation.WildcardPattern]::new($expected, [System.Management.Automation.WildcardOptions]::IgnoreCase)
            if ($pattern.IsMatch($path)) {
                return $true
            }
        } elseif ([string]::Equals($path, $expected, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Assert-ExpectedScope {
    param(
        [string]$RepoPath,
        [string[]]$ExpectedFiles
    )
    $changedPaths = @(Get-GitStatusPaths -RepoPath $RepoPath)
    Write-Log ("Changed paths detected: {0}" -f $changedPaths.Count)
    $outside = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $changedPaths) {
        if (-not (Test-PathExpected -PathText $path -ExpectedFiles $ExpectedFiles)) {
            $outside.Add($path)
        }
    }
    if ($outside.Count -gt 0) {
        throw "Out-of-scope changes detected: $($outside -join ', ')"
    }
}

function Invoke-ArgvCommand {
    param(
        [string]$Name,
        [string[]]$Argv,
        [string]$WorkingDirectory,
        [switch]$AllowFailure
    )
    $safeArgv = @($Argv)
    if ($safeArgv.Count -eq 0) {
        throw "Command '$Name' has empty argv."
    }
    $exe = $safeArgv[0]
    $commandArgs = @()
    if ($safeArgv.Count -gt 1) {
        $commandArgs = @($safeArgv[1..($safeArgv.Count - 1)])
    }
    Write-Log ("RUN {0}: {1} {2}" -f $Name, $exe, ($commandArgs -join " "))
    Push-Location $WorkingDirectory
    $oldPref = $PSNativeCommandUseErrorActionPreference
    try {
        $PSNativeCommandUseErrorActionPreference = $false
        $output = & $exe @commandArgs 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $PSNativeCommandUseErrorActionPreference = $oldPref
        Pop-Location
    }
    foreach ($line in @($output)) {
        $script:LogLines.Add([string]$line)
    }
    Write-Log ("EXIT {0}: {1}" -f $Name, $exitCode)
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "Command failed: $Name (exit $exitCode)"
    }
    return [pscustomobject]@{
        Name = $Name
        ExitCode = $exitCode
        Output = @($output)
    }
}

function Invoke-Git {
    param(
        [string]$RepoPath,
        [string[]]$ArgList,
        [string]$Name = "Git"
    )
    $argv = @("git") + $ArgList
    return Invoke-ArgvCommand -Name $Name -Argv $argv -WorkingDirectory $RepoPath
}

function Invoke-Gh {
    param(
        [string]$RepoPath,
        [string[]]$ArgList,
        [string]$Name = "GitHub CLI"
    )
    $argv = @("gh") + $ArgList
    return Invoke-ArgvCommand -Name $Name -Argv $argv -WorkingDirectory $RepoPath
}

function Invoke-ConfiguredChecks {
    param(
        [object[]]$Checks,
        [string]$RepoPath
    )
    foreach ($check in $Checks) {
        $argv = @($check.argv)
        [void](Invoke-ArgvCommand -Name ([string]$check.name) -Argv $argv -WorkingDirectory $RepoPath)
    }
}

function Get-CurrentBranch {
    param([string]$RepoPath)
    $result = Invoke-Git -RepoPath $RepoPath -ArgList @("branch", "--show-current") -Name "Current branch"
    return (($result.Output) -join [Environment]::NewLine).Trim()
}

function Invoke-PhaseA {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    Write-Log "PHASE A - local verification"
    Assert-Repo -RepoPath $RepoPath
    $branch = Get-CurrentBranch -RepoPath $RepoPath
    Write-Log ("Current branch: {0}" -f $branch)
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("status", "--porcelain=v1", "--untracked-files=all") -Name "Git status porcelain")
    Assert-ExpectedScope -RepoPath $RepoPath -ExpectedFiles @($PublishConfig.expected_files)
    Invoke-ConfiguredChecks -Checks @($PublishConfig.phase_a_checks) -RepoPath $RepoPath
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--check") -Name "Diff check")
    Write-Log "PHASE A completed."
}

function Ensure-StepBranch {
    param(
        [string]$RepoPath,
        [string]$Branch
    )
    $current = Get-CurrentBranch -RepoPath $RepoPath
    if ($current -eq $Branch) {
        Write-Log ("Already on branch: {0}" -f $Branch)
        return
    }
    $verify = Invoke-ArgvCommand -Name "Check branch exists" -Argv @("git", "rev-parse", "--verify", $Branch) -WorkingDirectory $RepoPath -AllowFailure
    if ($verify.ExitCode -eq 0) {
        [void](Invoke-Git -RepoPath $RepoPath -ArgList @("switch", $Branch) -Name "Switch branch")
    } else {
        [void](Invoke-Git -RepoPath $RepoPath -ArgList @("switch", "-c", $Branch) -Name "Create branch")
    }
}

function Invoke-PhaseB {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    if (-not $ApprovePublish) {
        throw "Phase B requires -ApprovePublish."
    }
    Write-Log "PHASE B - branch publish"
    Invoke-PhaseA -PublishConfig $PublishConfig -RepoPath $RepoPath
    Ensure-StepBranch -RepoPath $RepoPath -Branch ([string]$PublishConfig.branch)
    Assert-ExpectedScope -RepoPath $RepoPath -ExpectedFiles @($PublishConfig.expected_files)
    [void](Invoke-Git -RepoPath $RepoPath -ArgList (@("add", "--") + @($PublishConfig.expected_files)) -Name "Stage expected files")
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--cached", "--check") -Name "Cached diff check")
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("commit", "-m", ([string]$PublishConfig.commit_message)) -Name "Create commit")
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("push", "-u", "origin", ([string]$PublishConfig.branch)) -Name "Push branch")

    $existing = Invoke-ArgvCommand -Name "Find existing PR" -Argv @("gh", "pr", "list", "--head", ([string]$PublishConfig.branch), "--json", "number", "--jq", ".[0].number") -WorkingDirectory $RepoPath -AllowFailure
    $existingNumber = (($existing.Output) -join "").Trim()
    if ($existing.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($existingNumber)) {
        $script:PrNumber = $existingNumber
        Write-Log ("Reusing PR #{0}" -f $script:PrNumber)
    } else {
        $created = Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "create", "--base", "main", "--head", ([string]$PublishConfig.branch), "--title", ([string]$PublishConfig.pr_title), "--body", ([string]$PublishConfig.pr_body)) -Name "Create PR"
        $createdText = ($created.Output -join [Environment]::NewLine)
        $numberMatch = [regex]::Match($createdText, "/pull/(\d+)")
        if ($numberMatch.Success) {
            $script:PrNumber = $numberMatch.Groups[1].Value
        }
        Write-Log ("Created PR reference: {0}" -f $createdText)
    }
    Write-Log "PHASE B completed. Merge was not performed."
}

function Get-PrNumber {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    if ($PrNumber -gt 0) {
        return [string]$PrNumber
    }
    if ((Test-HasProperty -Object $PublishConfig -Name "pr_number") -and ([int]$PublishConfig.pr_number -gt 0)) {
        return [string]$PublishConfig.pr_number
    }
    $existing = Invoke-ArgvCommand -Name "Find PR for branch" -Argv @("gh", "pr", "list", "--head", ([string]$PublishConfig.branch), "--json", "number", "--jq", ".[0].number") -WorkingDirectory $RepoPath -AllowFailure
    $value = (($existing.Output) -join "").Trim()
    if ($existing.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($value)) {
        return $value
    }
    throw "Phase C requires -PrNumber or a resolvable PR for the configured branch."
}

function Invoke-GhPrChecks {
    param(
        [object]$PublishConfig,
        [string]$RepoPath,
        [string]$Number
    )
    Push-Location $RepoPath
    $oldPref = $PSNativeCommandUseErrorActionPreference
    try {
        $PSNativeCommandUseErrorActionPreference = $false
        $output = & gh @("pr", "checks", $Number, "--watch") 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $PSNativeCommandUseErrorActionPreference = $oldPref
        Pop-Location
    }
    $text = ($output -join [Environment]::NewLine)
    $script:LogLines.Add($text)
    Write-Log ("gh pr checks exit: {0}" -f $exitCode)
    if ($exitCode -eq 0) {
        return
    }
    if ($exitCode -eq 1 -and $text.ToLowerInvariant().Contains("no checks reported")) {
        if ([bool]$PublishConfig.allow_no_github_checks_reported) {
            Add-WarningLine "gh pr checks returned no checks reported; accepted by config."
            return
        }
        throw "gh pr checks reported no checks and config does not allow this warning."
    }
    throw "gh pr checks failed with exit code $exitCode"
}

function Invoke-PhaseC {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    if (-not $ApproveMerge) {
        throw "Phase C requires -ApproveMerge."
    }
    Write-Log "PHASE C - merge and final verification"
    $number = Get-PrNumber -PublishConfig $PublishConfig -RepoPath $RepoPath
    $script:PrNumber = $number
    [void](Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "view", $number) -Name "View PR")
    Invoke-GhPrChecks -PublishConfig $PublishConfig -RepoPath $RepoPath -Number $number
    [void](Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "merge", $number, "--squash") -Name "Merge PR")
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("switch", "main") -Name "Switch main")
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("pull", "--ff-only", "origin", "main") -Name "Pull main")
    Invoke-ConfiguredChecks -Checks @($PublishConfig.phase_c_checks) -RepoPath $RepoPath
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--check") -Name "Final diff check")
    $status = @(Get-GitStatusPaths -RepoPath $RepoPath)
    if ($status.Count -gt 0) {
        throw "Working tree is not clean after merge: $($status -join ', ')"
    }
    [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "log", "--oneline", "--max-count=$([int]$PublishConfig.log_max_count)") -Name "Final log")
    Write-Log "PHASE C completed."
}

function Escape-Xml {
    param([string]$Text)
    return [System.Security.SecurityElement]::Escape($Text)
}

function Add-ZipTextEntry {
    param(
        [System.IO.Compression.ZipArchive]$Archive,
        [string]$Name,
        [string]$Content
    )
    $entry = $Archive.CreateEntry($Name)
    $stream = $entry.Open()
    $writer = [System.IO.StreamWriter]::new($stream, [System.Text.Encoding]::UTF8)
    $writer.Write($Content)
    $writer.Dispose()
    $stream.Dispose()
}

function Write-MinimalDocx {
    param(
        [string]$Path,
        [string]$Text
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $parent = [System.IO.Path]::GetDirectoryName($fullPath)
    [void][System.IO.Directory]::CreateDirectory($parent)

    $contentTypes = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    $rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    $paragraphs = [System.Collections.Generic.List[string]]::new()
    foreach ($line in ($Text -split "`r?`n")) {
        $paragraphs.Add(('<w:p><w:r><w:t xml:space="preserve">{0}</w:t></w:r></w:p>' -f (Escape-Xml -Text $line)))
    }
    $document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ($paragraphs -join "") + '<w:sectPr/></w:body></w:document>'

    $fileStream = [System.IO.FileStream]::new($fullPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite)
    try {
        $archive = [System.IO.Compression.ZipArchive]::new($fileStream, [System.IO.Compression.ZipArchiveMode]::Create)
        try {
            Add-ZipTextEntry -Archive $archive -Name "[Content_Types].xml" -Content $contentTypes
            Add-ZipTextEntry -Archive $archive -Name "_rels/.rels" -Content $rels
            Add-ZipTextEntry -Archive $archive -Name "word/document.xml" -Content $document
        } finally {
            $archive.Dispose()
        }
    } finally {
        $fileStream.Dispose()
    }
}

function Get-SafeName {
    param([string]$Value)
    $safe = ($Value -replace "[^A-Za-z0-9_.-]+", "_").Trim("._-")
    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "publish_step"
    }
    return $safe
}

function Quote-PwshArg {
    param([string]$Value)
    return "'" + $Value.Replace("'", "''") + "'"
}

function Get-ShortCommand {
    param(
        [object]$PublishConfig,
        [string]$EffectivePhase
    )
    if ($SelfTest) {
        $items = @("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Quote-PwshArg -Value $PSCommandPath), "-SelfTest")
        if (-not [string]::IsNullOrWhiteSpace($BridgeRoot)) {
            $items += @("-BridgeRoot", (Quote-PwshArg -Value $BridgeRoot))
        }
        return ($items -join " ")
    }
    $items = @("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\asf_publish_step.ps1", "-Config", (Quote-PwshArg -Value ([string]$PublishConfig._config_path)), "-Phase", $EffectivePhase)
    if ($EffectivePhase -eq "B") {
        $items += "-ApprovePublish"
    }
    if ($EffectivePhase -eq "C") {
        if ($PrNumber -gt 0) {
            $items += @("-PrNumber", [string]$PrNumber)
        }
        $items += "-ApproveMerge"
    }
    return ($items -join " ")
}

function Get-BridgeRoot {
    param([object]$PublishConfig)
    if (-not [string]::IsNullOrWhiteSpace($BridgeRoot)) {
        return $BridgeRoot
    }
    if ($null -ne $PublishConfig -and (Test-HasProperty -Object $PublishConfig -Name "bridge_root") -and -not [string]::IsNullOrWhiteSpace([string]$PublishConfig.bridge_root)) {
        return [string]$PublishConfig.bridge_root
    }
    return $DefaultBridgeRoot
}

function Copy-FileToClipboard {
    param([string]$File)
    if (Get-Command Set-Clipboard -ErrorAction SilentlyContinue) {
        try {
            Get-Content -Path $File -Raw | Set-Clipboard
        } catch {
            Add-WarningLine "Clipboard copy failed; output files were still written."
        }
    }
}

function Write-BridgeOutputs {
    param(
        [object]$PublishConfig,
        [string]$EffectivePhase,
        [string]$Status
    )
    $root = Get-BridgeRoot -PublishConfig $PublishConfig
    [void][System.IO.Directory]::CreateDirectory($root)
    $prefix = [string]$PublishConfig.step
    $name = Get-SafeName -Value ([string]$PublishConfig.name)
    $shortCommand = Get-ShortCommand -PublishConfig $PublishConfig -EffectivePhase $EffectivePhase
    $warnings = if ($script:WarningLines.Count -gt 0) { $script:WarningLines -join [Environment]::NewLine } else { "none" }
    $prText = if ($null -ne $script:PrNumber) { [string]$script:PrNumber } else { "not available" }

    $requestText = @(
        "ASF Publish Step Runner",
        "Step: $($PublishConfig.step)",
        "Name: $($PublishConfig.name)",
        "Phase: $EffectivePhase",
        "Status: $Status",
        "Next step: $($PublishConfig.next_step)"
    ) -join [Environment]::NewLine
    $commandText = $shortCommand + [Environment]::NewLine
    $fullText = @(
        "ASF Publish Step Runner - full output",
        "Status: $Status",
        "PR number: $prText",
        "Warnings:",
        $warnings,
        "",
        "Log:",
        ($script:LogLines -join [Environment]::NewLine)
    ) -join [Environment]::NewLine
    $compactText = @(
        "# ASF Publish Step Runner",
        "",
        ("- Step: ``{0}``" -f $PublishConfig.step),
        ("- Name: ``{0}``" -f $PublishConfig.name),
        ("- Phase: ``{0}``" -f $EffectivePhase),
        ("- Status: ``{0}``" -f $Status),
        ("- PR number: ``{0}``" -f $prText),
        ("- Next step: ``{0}``" -f $PublishConfig.next_step),
        "",
        "## Short command",
        "",
        "```powershell",
        $shortCommand,
        "```",
        "",
        "## Warnings",
        "",
        $warnings
    ) -join [Environment]::NewLine

    $numbered = @{
        Request = Join-Path $root ("{0}-Richiesta_Generazione_{1}.txt" -f $prefix, $name)
        Command = Join-Path $root ("{0}-Comando_Eseguito_{1}.ps1" -f $prefix, $name)
        Full = Join-Path $root ("{0}-Output_Completo_{1}.txt" -f $prefix, $name)
        Compact = Join-Path $root ("{0}-Output_Compatto_{1}.md" -f $prefix, $name)
        Docx = Join-Path $root ("{0}-Output_Compatto_{1}.docx" -f $prefix, $name)
    }
    Set-Content -Path $numbered.Request -Value $requestText -Encoding UTF8
    Set-Content -Path $numbered.Command -Value $commandText -Encoding UTF8
    Set-Content -Path $numbered.Full -Value $fullText -Encoding UTF8
    Set-Content -Path $numbered.Compact -Value $compactText -Encoding UTF8
    Write-MinimalDocx -Path $numbered.Docx -Text $compactText

    Copy-Item -Path $numbered.Request -Destination (Join-Path $root "LAST-Richiesta_Generazione.txt") -Force
    Copy-Item -Path $numbered.Command -Destination (Join-Path $root "LAST-Comando_Eseguito.ps1") -Force
    Copy-Item -Path $numbered.Full -Destination (Join-Path $root "LAST-Output_Completo.txt") -Force
    Copy-Item -Path $numbered.Compact -Destination (Join-Path $root "LAST-Output_Compatto.md") -Force
    Copy-Item -Path $numbered.Docx -Destination (Join-Path $root "LAST-Output_Compatto.docx") -Force
    Copy-FileToClipboard -File $numbered.Compact
    Write-Log ("Bridge output written to: {0}" -f $root)
}

function New-SelfTestConfig {
    return [pscustomobject]@{
        step = "0000"
        name = "SelfTest"
        branch = "self-test"
        commit_message = "self test"
        pr_title = "self test"
        pr_body = "self test"
        next_step = "none"
        expected_files = @("scripts/asf_publish_step.ps1")
        phase_a_checks = @([pscustomobject]@{ name = "Noop"; argv = @("pwsh", "-NoProfile", "-Command", "Write-Output self-test") })
        phase_c_checks = @([pscustomobject]@{ name = "Noop"; argv = @("pwsh", "-NoProfile", "-Command", "Write-Output self-test") })
        allow_no_github_checks_reported = $true
        log_max_count = 5
    }
}

try {
    if ($SelfTest) {
        $selfConfig = New-SelfTestConfig
        Assert-PublishConfig -PublishConfig $selfConfig
        Write-Log "SelfTest running."
        Write-BridgeOutputs -PublishConfig $selfConfig -EffectivePhase "SelfTest" -Status "PASS"
        exit 0
    }

    $publishConfig = Read-PublishConfig -Path $Config
    Assert-PublishConfig -PublishConfig $publishConfig
    $repoPath = Get-RepoPath -PublishConfig $publishConfig

    switch ($Phase) {
        "Plan" {
            Write-Log "PLAN - config validated. No GitHub or publish action executed."
        }
        "A" {
            Invoke-PhaseA -PublishConfig $publishConfig -RepoPath $repoPath
        }
        "B" {
            Invoke-PhaseB -PublishConfig $publishConfig -RepoPath $repoPath
        }
        "C" {
            Invoke-PhaseC -PublishConfig $publishConfig -RepoPath $repoPath
        }
        default {
            throw "Unsupported phase: $Phase"
        }
    }

    Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "PASS"
    exit 0
} catch {
    $message = $_.Exception.Message
    Write-Log ("ERROR: {0}" -f $message)
    if ($SelfTest) {
        $fallbackConfig = New-SelfTestConfig
        Write-BridgeOutputs -PublishConfig $fallbackConfig -EffectivePhase "SelfTest" -Status "FAIL"
    } elseif (-not [string]::IsNullOrWhiteSpace($Config)) {
        try {
            if ($null -eq $publishConfig) {
                $publishConfig = Read-PublishConfig -Path $Config
            }
            Write-BridgeOutputs -PublishConfig $publishConfig -EffectivePhase $Phase -Status "FAIL"
        } catch {
            Write-Warning "Unable to write Bridge outputs after failure: $($_.Exception.Message)"
        }
    }
    Write-Error $message
    exit 1
}
