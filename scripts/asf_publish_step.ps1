param(
    [string]$Config,
    [ValidateSet("Plan", "PrepareConfig", "A", "B", "C")]
    [string]$Phase = "Plan",
    [switch]$ApprovePublish,
    [switch]$ApproveMerge,
    [int]$PrNumber = 0,
    [string]$BridgeRoot,
    [string]$StepNumber,
    [string]$StepName,
    [string]$BranchName,
    [string]$CommitMessage,
    [string]$PrTitle,
    [string]$PrBody,
    [string]$NextStep,
    [string]$RiskLevel = "L1",
    [string]$VerificationProfile = "publish",
    [string]$VerificationPhase = "local",
    [string]$ProfileSelectorExpectedProfile,
    [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DefaultBridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command"
$script:LogLines = [System.Collections.Generic.List[string]]::new()
$script:WarningLines = [System.Collections.Generic.List[string]]::new()
$script:RequestedPrNumber = $PrNumber
$script:PrNumber = $null
$script:ProfileValidation = [pscustomobject]@{
    Enabled = $false
    Status = "not configured"
    DeclaredProfile = "not configured"
    RecommendedProfile = "not configured"
    SelectorFailClosed = "not available"
    AllowReduction = $false
    PhaseCReduction = "disabled"
    Reasons = @()
    Warnings = @()
}
$script:StateHookConfig = [pscustomobject]@{
    Enabled = $false
    Step = ""
    StateFile = ""
    WriteBridge = $false
    BridgeRoot = ""
    FailOnHookError = $false
    ExpectedBeforePhaseB = ""
    ExpectedBeforePhaseC = ""
    CloseOnPhaseCSuccess = $false
    EmitMainVerified = $true
}
$script:StateHookWarnings = [System.Collections.Generic.List[string]]::new()
$script:StateHookErrors = [System.Collections.Generic.List[string]]::new()
$script:StateHookSummary = [pscustomobject]@{
    Enabled = $false
    StateFile = "not configured"
    BridgeRoot = "not configured"
    LastEvent = "none"
    FinalState = "not available"
    CloseStepEmitted = $false
}
$script:VerificationProfileRank = @{
    "docs-only" = 10
    "code-unit" = 20
    "publish" = 30
    "motor-core" = 40
    "final-main" = 50
    "high-risk" = 60
}
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

function Get-OptionalStringProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    if ($null -eq $Object -or -not (Test-HasProperty -Object $Object -Name $Name)) {
        return ""
    }
    $value = [string]$Object.$Name
    if ([string]::IsNullOrWhiteSpace($value)) {
        return ""
    }
    return $value.Trim()
}

function Get-OptionalBoolProperty {
    param(
        [object]$Object,
        [string]$Name,
        [bool]$Default = $false
    )
    if ($null -eq $Object -or -not (Test-HasProperty -Object $Object -Name $Name)) {
        return $Default
    }
    $value = $Object.$Name
    if ($value -is [bool]) {
        return $value
    }
    $text = ([string]$value).Trim()
    if ([string]::Equals($text, "true", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    if ([string]::Equals($text, "false", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $false
    }
    throw "Config field must be boolean: $Name"
}

function Resolve-RepoRelativePath {
    param(
        [string]$PathText,
        [string]$RepoPath
    )
    if ([string]::IsNullOrWhiteSpace($PathText)) {
        return ""
    }
    if ([System.IO.Path]::IsPathRooted($PathText)) {
        return [System.IO.Path]::GetFullPath($PathText)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoPath $PathText))
}

function Get-StateStepPathName {
    param([string]$Step)
    $safe = ($Step -replace "[^A-Za-z0-9]+", "_").Trim("_")
    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "step"
    }
    return $safe
}

function Add-StateHookWarning {
    param([string]$Message)
    $script:StateHookWarnings.Add($Message)
    Add-WarningLine ("State hook: {0}" -f $Message)
}

function Add-StateHookError {
    param([string]$Message)
    $script:StateHookErrors.Add($Message)
}

function ConvertTo-StringList {
    param([object]$Value)
    $items = [System.Collections.Generic.List[string]]::new()
    if ($null -eq $Value) {
        return @()
    }
    if ($Value -is [string]) {
        if (-not [string]::IsNullOrWhiteSpace($Value)) {
            $items.Add($Value.Trim())
        }
        return @($items)
    }
    foreach ($item in @($Value)) {
        if ($null -eq $item) {
            continue
        }
        $text = ([string]$item).Trim()
        if (-not [string]::IsNullOrWhiteSpace($text)) {
            $items.Add($text)
        }
    }
    return @($items | Select-Object -Unique)
}

function Get-OptionalStringArrayProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    if ($null -eq $Object -or -not (Test-HasProperty -Object $Object -Name $Name)) {
        return @()
    }
    return @(ConvertTo-StringList -Value $Object.$Name)
}

function Assert-NonEmptyString {
    param(
        [object]$Value,
        [string]$Name
    )
    if ($null -eq $Value) {
        throw "$Name must not be null."
    }
    $text = ([string]$Value).Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "$Name must not be empty."
    }
    return $text
}

function Assert-NonEmptyArray {
    param(
        [object[]]$Value,
        [string]$Name
    )
    if ($null -eq $Value -or @($Value).Count -eq 0) {
        throw "$Name must not be empty."
    }
    return @($Value)
}

function Assert-ExpectedFiles {
    param([object[]]$ExpectedFiles)
    if ($null -eq $ExpectedFiles -or @($ExpectedFiles).Count -eq 0) {
        throw "expected_files must not be empty."
    }
    $items = @(Assert-NonEmptyArray -Value @($ExpectedFiles) -Name "expected_files")
    foreach ($file in $items) {
        if (-not ($file -is [string])) {
            throw "expected_files contains a non-string or empty value."
        }
        [void](Assert-NonEmptyString -Value $file -Name "expected_files item")
    }
    return @($items)
}

function Assert-StringProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    if (-not (Test-HasProperty -Object $Object -Name $Name)) {
        throw "Missing config field: $Name"
    }
    return Assert-NonEmptyString -Value $Object.$Name -Name "Config field $Name"
}

function Test-ProfileIntegrationRequested {
    param([object]$PublishConfig)
    foreach ($name in @(
        "verification_profile",
        "profile_selector_expected_profile",
        "risk_level",
        "changed_files",
        "verification_phase",
        "allow_profile_check_reduction",
        "profile_selector_input"
    )) {
        if (Test-HasProperty -Object $PublishConfig -Name $name) {
            return $true
        }
    }
    return $false
}

function Get-ProfileSelectorInputObject {
    param([object]$PublishConfig)
    if (-not (Test-HasProperty -Object $PublishConfig -Name "profile_selector_input")) {
        return $null
    }
    $value = $PublishConfig.profile_selector_input
    if ($null -eq $value -or $value -is [string]) {
        return $null
    }
    return $value
}

function Get-ProfileSelectorInputFile {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    if (-not (Test-HasProperty -Object $PublishConfig -Name "profile_selector_input")) {
        return ""
    }
    $value = $PublishConfig.profile_selector_input
    if ($null -eq $value -or -not ($value -is [string]) -or [string]::IsNullOrWhiteSpace($value)) {
        return ""
    }
    $pathText = [string]$value
    if ([System.IO.Path]::IsPathRooted($pathText)) {
        return [System.IO.Path]::GetFullPath($pathText)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoPath $pathText))
}

function Get-DeclaredVerificationProfile {
    param([object]$PublishConfig)
    $declared = Get-OptionalStringProperty -Object $PublishConfig -Name "verification_profile"
    $expected = Get-OptionalStringProperty -Object $PublishConfig -Name "profile_selector_expected_profile"
    if (-not [string]::IsNullOrWhiteSpace($declared) -and -not [string]::IsNullOrWhiteSpace($expected)) {
        if (-not [string]::Equals($declared, $expected, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "verification_profile and profile_selector_expected_profile disagree."
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($declared)) {
        return $declared.Trim().ToLowerInvariant()
    }
    if (-not [string]::IsNullOrWhiteSpace($expected)) {
        return $expected.Trim().ToLowerInvariant()
    }
    return ""
}

function Get-ProfileRank {
    param([string]$Profile)
    $profileName = $Profile.Trim().ToLowerInvariant()
    if (-not $script:VerificationProfileRank.ContainsKey($profileName)) {
        throw "Unknown verification profile: $Profile"
    }
    return [int]$script:VerificationProfileRank[$profileName]
}

function Assert-DeclaredProfileAdequate {
    param(
        [string]$DeclaredProfile,
        [string]$RecommendedProfile
    )
    $declaredRank = Get-ProfileRank -Profile $DeclaredProfile
    $recommendedRank = Get-ProfileRank -Profile $RecommendedProfile
    if ($declaredRank -lt $recommendedRank) {
        throw "Verification profile '$DeclaredProfile' is lighter than selector recommendation '$RecommendedProfile'."
    }
    if ($RecommendedProfile -eq "publish" -and $DeclaredProfile -notin @("publish", "motor-core", "final-main", "high-risk")) {
        throw "Publish intent requires verification_profile publish, motor-core, final-main, or high-risk."
    }
}

function Test-PhaseCChecksRobust {
    param([object]$PublishConfig)
    foreach ($command in @($PublishConfig.phase_c_checks)) {
        $text = ((@($command.argv) | ForEach-Object { [string]$_ }) -join " ").ToLowerInvariant()
        if ($text.Contains("verify.ps1") -or $text.Contains("check_workflow_health.py") -or $text.Contains("pytest")) {
            return $true
        }
    }
    return $false
}

function Get-ProfileSelectorArgs {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    $selectorPath = Join-Path $RepoPath "scripts/asf_verification_profile_selector.py"
    if (-not (Test-Path -LiteralPath $selectorPath -PathType Leaf)) {
        throw "Verification profile selector not found: $selectorPath"
    }

    $inputObject = Get-ProfileSelectorInputObject -PublishConfig $PublishConfig
    $inputFile = Get-ProfileSelectorInputFile -PublishConfig $PublishConfig -RepoPath $RepoPath
    if (-not [string]::IsNullOrWhiteSpace($inputFile) -and -not (Test-Path -LiteralPath $inputFile -PathType Leaf)) {
        throw "profile_selector_input file not found: $inputFile"
    }

    $argv = @("python", $selectorPath, "--json")
    if (-not [string]::IsNullOrWhiteSpace($inputFile)) {
        $argv += @("--input-file", $inputFile)
    }

    $riskLevel = Get-OptionalStringProperty -Object $PublishConfig -Name "risk_level"
    if ([string]::IsNullOrWhiteSpace($riskLevel)) {
        $riskLevel = Get-OptionalStringProperty -Object $inputObject -Name "risk_level"
    }
    if (-not [string]::IsNullOrWhiteSpace($riskLevel)) {
        $argv += @("--risk-level", $riskLevel)
    }

    $changedFiles = @(Get-OptionalStringArrayProperty -Object $PublishConfig -Name "changed_files")
    if ($changedFiles.Count -eq 0) {
        $changedFiles = @(Get-OptionalStringArrayProperty -Object $inputObject -Name "changed_files")
    }
    if ($changedFiles.Count -eq 0) {
        $changedFiles = @($PublishConfig.expected_files)
    }
    if ($changedFiles.Count -gt 0) {
        $argv += "--changed-files"
        $argv += $changedFiles
    }

    $stepType = Get-OptionalStringProperty -Object $PublishConfig -Name "step_type"
    if ([string]::IsNullOrWhiteSpace($stepType)) {
        $stepType = Get-OptionalStringProperty -Object $inputObject -Name "step_type"
    }
    if (-not [string]::IsNullOrWhiteSpace($stepType)) {
        $argv += @("--step-type", $stepType)
    }

    $verificationPhase = Get-OptionalStringProperty -Object $PublishConfig -Name "verification_phase"
    if ([string]::IsNullOrWhiteSpace($verificationPhase)) {
        $verificationPhase = Get-OptionalStringProperty -Object $inputObject -Name "verification_phase"
    }
    if ([string]::IsNullOrWhiteSpace($verificationPhase)) {
        $verificationPhase = Get-OptionalStringProperty -Object $inputObject -Name "phase"
    }
    if (-not [string]::IsNullOrWhiteSpace($verificationPhase)) {
        $argv += @("--phase", $verificationPhase)
    }

    $intentItems = @(Get-OptionalStringArrayProperty -Object $PublishConfig -Name "intent")
    $intentItems += @(Get-OptionalStringArrayProperty -Object $inputObject -Name "intent")
    $intentItems += @(Get-OptionalStringArrayProperty -Object $inputObject -Name "intents")
    foreach ($intent in @($intentItems | Select-Object -Unique)) {
        $argv += @("--intent", $intent)
    }

    $checkItems = @(Get-OptionalStringArrayProperty -Object $PublishConfig -Name "checks_already_run")
    $checkItems += @(Get-OptionalStringArrayProperty -Object $inputObject -Name "checks_already_run")
    foreach ($check in @($checkItems | Select-Object -Unique)) {
        $argv += @("--check-executed", $check)
    }

    $gateItems = @(Get-OptionalStringArrayProperty -Object $PublishConfig -Name "provided_gates")
    $gateItems += @(Get-OptionalStringArrayProperty -Object $inputObject -Name "provided_gates")
    if ($ApprovePublish) {
        $gateItems += @("approve_publish", "explicit_publish_approval")
    }
    foreach ($gate in @($gateItems | Select-Object -Unique)) {
        $argv += @("--provided-gate", $gate)
    }

    return @($argv)
}

function Invoke-VerificationProfileValidation {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    if (-not (Test-ProfileIntegrationRequested -PublishConfig $PublishConfig)) {
        $script:ProfileValidation = [pscustomobject]@{
            Enabled = $false
            Status = "not configured"
            DeclaredProfile = "not configured"
            RecommendedProfile = "not configured"
            SelectorFailClosed = "not available"
            AllowReduction = $false
            PhaseCReduction = "disabled"
            Reasons = @()
            Warnings = @()
        }
        return
    }

    $declaredProfile = Get-DeclaredVerificationProfile -PublishConfig $PublishConfig
    if ([string]::IsNullOrWhiteSpace($declaredProfile)) {
        throw "Profile integration fields are present, but verification_profile is missing."
    }
    [void](Get-ProfileRank -Profile $declaredProfile)

    $allowReduction = Get-OptionalBoolProperty -Object $PublishConfig -Name "allow_profile_check_reduction" -Default $false
    $script:ProfileValidation = [pscustomobject]@{
        Enabled = $true
        Status = "validating"
        DeclaredProfile = $declaredProfile
        RecommendedProfile = "not available"
        SelectorFailClosed = "not available"
        AllowReduction = $allowReduction
        PhaseCReduction = "disabled"
        Reasons = @()
        Warnings = @()
    }

    $riskLevel = Get-OptionalStringProperty -Object $PublishConfig -Name "risk_level"
    if ([string]::Equals($riskLevel, "L4", [System.StringComparison]::OrdinalIgnoreCase) -and $declaredProfile -ne "high-risk") {
        throw "Risk level L4 requires verification_profile high-risk."
    }

    $argv = @(Get-ProfileSelectorArgs -PublishConfig $PublishConfig -RepoPath $RepoPath)
    $selectorResult = Invoke-ArgvCommand -Name "Verification profile selector" -Argv $argv -WorkingDirectory $RepoPath
    $selectorText = ($selectorResult.Output -join [Environment]::NewLine)
    try {
        $selectorPacket = $selectorText | ConvertFrom-Json
    } catch {
        throw "Verification profile selector returned invalid JSON."
    }

    $recommendedProfile = ([string]$selectorPacket.profile).Trim().ToLowerInvariant()
    [void](Get-ProfileRank -Profile $recommendedProfile)
    $failClosed = [bool]$selectorPacket.fail_closed

    $script:ProfileValidation.RecommendedProfile = $recommendedProfile
    $script:ProfileValidation.SelectorFailClosed = [string]$failClosed
    $script:ProfileValidation.Reasons = @($selectorPacket.reasons)
    $script:ProfileValidation.Warnings = @($selectorPacket.warnings)

    if ($failClosed) {
        $script:ProfileValidation.Status = "blocked"
        throw "Verification profile selector failed closed for recommended profile '$recommendedProfile'."
    }

    Assert-DeclaredProfileAdequate -DeclaredProfile $declaredProfile -RecommendedProfile $recommendedProfile

    if ($allowReduction) {
        if ($recommendedProfile -notin @("docs-only", "code-unit")) {
            $script:ProfileValidation.Status = "blocked"
            throw "allow_profile_check_reduction is allowed only for docs-only or code-unit recommendations."
        }
        if (-not (Test-PhaseCChecksRobust -PublishConfig $PublishConfig)) {
            $script:ProfileValidation.Status = "blocked"
            throw "allow_profile_check_reduction requires robust phase_c_checks."
        }
    }

    $script:ProfileValidation.Status = "pass"
    Write-Log ("Verification profile validation: declared={0}; recommended={1}; reduction={2}; phase_c_reduction=disabled" -f $declaredProfile, $recommendedProfile, $allowReduction)
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

    [void](Assert-ExpectedFiles -ExpectedFiles @(Get-ConfigArray -Object $PublishConfig -Name "expected_files"))

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
    if ([string]::IsNullOrWhiteSpace($PathText)) {
        return ""
    }
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

function Invoke-NativeStdoutChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter()]
        [string[]]$Arguments = @(),

        [Parameter()]
        [string]$Label = "",

        [Parameter()]
        [string]$WorkingDirectory = (Get-Location).Path
    )
    $commandName = Assert-NonEmptyString -Value $Command -Name "Stdout-only native command"
    $displayLabel = $Label
    if ([string]::IsNullOrWhiteSpace($displayLabel)) {
        $displayLabel = $commandName
    }
    $workDir = Assert-NonEmptyString -Value $WorkingDirectory -Name "Stdout-only native command working directory"
    if (-not (Test-Path -LiteralPath $workDir -PathType Container)) {
        throw "Stdout-only native command working directory does not exist: $workDir"
    }
    if ($null -eq $Arguments) {
        throw "Stdout-only native command arguments are null for label: $displayLabel"
    }
    foreach ($argument in @($Arguments)) {
        if ($null -eq $argument) {
            throw "Stdout-only native command argument is null for label: $displayLabel"
        }
    }

    $resolvedCommand = $commandName
    $commandInfo = Get-Command $commandName -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $commandInfo -and -not [string]::IsNullOrWhiteSpace([string]$commandInfo.Source)) {
        $resolvedCommand = [string]$commandInfo.Source
    }

    Write-Log ("RUN {0}: {1} {2}" -f $displayLabel, $commandName, ($Arguments -join " "))
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $resolvedCommand
    $startInfo.WorkingDirectory = $workDir
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($argument in @($Arguments)) {
        [void]$startInfo.ArgumentList.Add([string]$argument)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    try {
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        $exitCode = $process.ExitCode
    } finally {
        $process.Dispose()
    }

    Write-Log ("EXIT {0}: {1}" -f $displayLabel, $exitCode)
    if (-not [string]::IsNullOrWhiteSpace($stderr)) {
        foreach ($line in ($stderr -split "`r?`n")) {
            if (-not [string]::IsNullOrWhiteSpace($line)) {
                Add-WarningLine ("{0} stderr ignored for path discovery: {1}" -f $displayLabel, $line.Trim())
            }
        }
    }
    if ($exitCode -ne 0) {
        throw "Stdout-only native command failed. Label=$displayLabel Command=$commandName ExitCode=$exitCode"
    }
    return @(($stdout -split "`r?`n") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Test-RepositoryChangedFileCandidate {
    param([string]$PathText)
    $path = Normalize-GitPath -PathText $PathText
    if ([string]::IsNullOrWhiteSpace($path)) {
        return $false
    }
    $lower = $path.ToLowerInvariant()
    foreach ($prefix in @("warning:", "fatal:", "error:", "hint:")) {
        if ($lower.StartsWith($prefix)) {
            return $false
        }
    }
    if ([System.IO.Path]::IsPathRooted($path)) {
        return $false
    }
    if ($path -eq ".." -or $path.StartsWith("../") -or $path.Contains("/../")) {
        return $false
    }
    return $true
}

function Get-RepositoryChangedFiles {
    param([string]$RepoPath)
    Assert-Repo -RepoPath $RepoPath
    $commands = @(
        [pscustomobject]@{
            Label = "Git unstaged changed files"
            Args = @("--no-pager", "diff", "--name-only", "--")
        },
        [pscustomobject]@{
            Label = "Git staged changed files"
            Args = @("--no-pager", "diff", "--cached", "--name-only", "--")
        },
        [pscustomobject]@{
            Label = "Git untracked files"
            Args = @("ls-files", "--others", "--exclude-standard", "--")
        }
    )

    $paths = [System.Collections.Generic.List[string]]::new()
    foreach ($command in $commands) {
        $lines = @(Invoke-NativeStdoutChecked -Command "git" -Arguments @($command.Args) -Label ([string]$command.Label) -WorkingDirectory $RepoPath)
        foreach ($line in $lines) {
            if (Test-RepositoryChangedFileCandidate -PathText $line) {
                $paths.Add((Normalize-GitPath -PathText $line))
            }
        }
    }
    return @($paths | Sort-Object -Unique)
}

function Get-GitStatusPaths {
    param([string]$RepoPath)
    $result = Invoke-NativeChecked -Command "git" -Arguments @("status", "--porcelain=v1", "--untracked-files=all") -AllowedExitCodes @(0) -Label "Git status paths" -WorkingDirectory $RepoPath
    $lines = @($result.Output)

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

function Copy-PublishConfigWithScope {
    param(
        [object]$PublishConfig,
        [string[]]$ChangedFiles
    )
    $copy = [ordered]@{}
    foreach ($property in $PublishConfig.PSObject.Properties) {
        $copy[$property.Name] = $property.Value
    }
    $copy["expected_files"] = @($ChangedFiles)
    $copy["changed_files"] = @($ChangedFiles)
    return [pscustomobject]$copy
}

function Write-OutOfScopeRecoveryReport {
    param(
        [object]$PublishConfig,
        [string]$RepoPath,
        [string[]]$ExpectedFiles,
        [string[]]$ChangedFiles,
        [string[]]$OutOfScopeFiles
    )
    if ($null -eq $PublishConfig) {
        return $null
    }

    $root = Get-BridgeRoot -PublishConfig $PublishConfig
    [void][System.IO.Directory]::CreateDirectory($root)
    $prefix = [string]$PublishConfig.step
    $name = Get-SafeName -Value ([string]$PublishConfig.name)
    $reportPath = Join-Path $root ("{0}-Recovery_Out_Of_Scope_{1}.md" -f $prefix, $name)
    $suggestedConfigPath = Join-Path $root ("{0}-Recovery_Out_Of_Scope_Suggested_Config_{1}.json" -f $prefix, $name)

    $suggested = Copy-PublishConfigWithScope -PublishConfig $PublishConfig -ChangedFiles @($ChangedFiles)
    $suggested | ConvertTo-Json -Depth 20 | Set-Content -Path $suggestedConfigPath -Encoding UTF8

    $expectedText = if (@($ExpectedFiles).Count -gt 0) { (@($ExpectedFiles) -join [Environment]::NewLine) } else { "none" }
    $changedText = if (@($ChangedFiles).Count -gt 0) { (@($ChangedFiles) -join [Environment]::NewLine) } else { "none" }
    $outsideText = if (@($OutOfScopeFiles).Count -gt 0) { (@($OutOfScopeFiles) -join [Environment]::NewLine) } else { "none" }
    $report = @(
        "# ASF publish out-of-scope recovery",
        "",
        ("- Step: ``{0}``" -f $PublishConfig.step),
        ("- Name: ``{0}``" -f $PublishConfig.name),
        ("- Repo path: ``{0}``" -f $RepoPath),
        "- Status: ``BLOCCATO``",
        "",
        "The runner remains fail-closed. Review the suggested config. If the files are expected, rerun Phase B with the updated config.",
        "",
        "## Out-of-scope files",
        "",
        "```text",
        $outsideText,
        "```",
        "",
        "## Config expected_files",
        "",
        "```text",
        $expectedText,
        "```",
        "",
        "## Repository changed files discovered from stdout-only Git commands",
        "",
        "```text",
        $changedText,
        "```",
        "",
        "## Ignored warning/non-file lines",
        "",
        'Path discovery reads only stdout from `git --no-pager diff --name-only`, `git --no-pager diff --cached --name-only`, and `git ls-files --others --exclude-standard`. Git stderr warnings such as LF/CRLF are not treated as paths.',
        "",
        "## Suggested config",
        "",
        ("Suggested JSON: ``{0}``" -f $suggestedConfigPath),
        "",
        "No commit, push, PR, merge or deploy was executed by this recovery report."
    ) -join [Environment]::NewLine
    Set-Content -Path $reportPath -Value $report -Encoding UTF8

    Write-Log ("Out-of-scope recovery report written: {0}" -f $reportPath)
    Write-Log ("Out-of-scope suggested config written: {0}" -f $suggestedConfigPath)
    return [pscustomobject]@{
        Report = $reportPath
        SuggestedConfig = $suggestedConfigPath
    }
}

function Assert-ExpectedScope {
    param(
        [string]$RepoPath,
        [string[]]$ExpectedFiles,
        [object]$PublishConfig = $null
    )
    $expected = @(Assert-ExpectedFiles -ExpectedFiles $ExpectedFiles)
    $changedPaths = @(Get-RepositoryChangedFiles -RepoPath $RepoPath)
    Write-Log ("Changed paths detected: {0}" -f $changedPaths.Count)
    $outside = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $changedPaths) {
        if (-not (Test-PathExpected -PathText $path -ExpectedFiles $expected)) {
            $outside.Add($path)
        }
    }
    if ($outside.Count -gt 0) {
        $recovery = Write-OutOfScopeRecoveryReport -PublishConfig $PublishConfig -RepoPath $RepoPath -ExpectedFiles @($expected) -ChangedFiles @($changedPaths) -OutOfScopeFiles @($outside)
        Write-Log "Out-of-scope changes detected. Publication is blocked until scope is reviewed."
        Write-Log ("Expected files: {0}" -f (@($expected) -join ", "))
        Write-Log ("Repository changed files: {0}" -f (@($changedPaths) -join ", "))
        Write-Log ("Out-of-scope files: {0}" -f (@($outside) -join ", "))
        if ($null -ne $recovery) {
            Write-Log ("Review the suggested config. If the files are expected, rerun Phase B with the updated config: {0}" -f $recovery.SuggestedConfig)
        }
        throw "Out-of-scope changes detected: $($outside -join ', ')"
    }
}

function Assert-NoOutOfScopeFiles {
    param(
        [string]$RepoPath,
        [string[]]$ExpectedFiles,
        [object]$PublishConfig = $null
    )
    Assert-ExpectedScope -RepoPath $RepoPath -ExpectedFiles $ExpectedFiles -PublishConfig $PublishConfig
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter()]
        [string[]]$Arguments = @(),

        [Parameter()]
        [int[]]$AllowedExitCodes = @(0),

        [Parameter()]
        [string]$Label = "",

        [Parameter()]
        [string]$WorkingDirectory = (Get-Location).Path,

        [Parameter()]
        [switch]$AllowAnyExitCode
    )
    $commandName = Assert-NonEmptyString -Value $Command -Name "Native command"
    $displayLabel = $Label
    if ([string]::IsNullOrWhiteSpace($displayLabel)) {
        $displayLabel = $commandName
    } else {
        $displayLabel = Assert-NonEmptyString -Value $displayLabel -Name "Native command label"
    }
    if ($null -eq $Arguments) {
        throw "Native command arguments are null for label: $displayLabel"
    }
    for ($index = 0; $index -lt @($Arguments).Count; $index++) {
        if ($null -eq $Arguments[$index]) {
            throw "Native command argument $index is null for label: $displayLabel"
        }
        if ([string]::IsNullOrWhiteSpace([string]$Arguments[$index])) {
            throw "Native command argument $index is empty for label: $displayLabel"
        }
    }
    if (-not $AllowAnyExitCode) {
        [void](Assert-NonEmptyArray -Value @($AllowedExitCodes) -Name "AllowedExitCodes")
    }
    $workDir = Assert-NonEmptyString -Value $WorkingDirectory -Name "Native command working directory"
    if (-not (Test-Path -LiteralPath $workDir -PathType Container)) {
        throw "Native command working directory does not exist: $workDir"
    }

    Write-Log ("RUN {0}: {1} {2}" -f $displayLabel, $commandName, ($Arguments -join " "))
    Push-Location $workDir
    $oldPref = $PSNativeCommandUseErrorActionPreference
    try {
        $PSNativeCommandUseErrorActionPreference = $false
        $output = & $commandName @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $PSNativeCommandUseErrorActionPreference = $oldPref
        Pop-Location
    }
    if ($null -eq $exitCode) {
        throw "Native command did not produce LASTEXITCODE. Label=$displayLabel Command=$commandName"
    }
    foreach ($line in @($output)) {
        $script:LogLines.Add([string]$line)
    }
    Write-Log ("EXIT {0}: {1}" -f $displayLabel, $exitCode)
    if (-not $AllowAnyExitCode -and $AllowedExitCodes -notcontains $exitCode) {
        throw "Native command failed. Label=$displayLabel Command=$commandName ExitCode=$exitCode"
    }
    return [pscustomobject]@{
        Name = $displayLabel
        Command = $commandName
        Arguments = @($Arguments)
        ExitCode = $exitCode
        AllowedExitCodes = @($AllowedExitCodes)
        Output = @($output)
    }
}

function Invoke-ArgvCommand {
    param(
        [string]$Name,
        [string[]]$Argv,
        [string]$WorkingDirectory,
        [switch]$AllowFailure
    )
    $safeArgv = @(Assert-NonEmptyArray -Value @($Argv) -Name "Command '$Name' argv")
    $exe = $safeArgv[0]
    [void](Assert-NonEmptyString -Value $exe -Name "Command '$Name' executable")
    $commandArgs = @()
    if ($safeArgv.Count -gt 1) {
        $commandArgs = @($safeArgv[1..($safeArgv.Count - 1)])
    }

    if ($AllowFailure) {
        # Tolerant native probes are allowed only when the caller immediately
        # inspects ExitCode and decides the next guarded action.
        return Invoke-NativeChecked -Command $exe -Arguments $commandArgs -Label $Name -WorkingDirectory $WorkingDirectory -AllowAnyExitCode
    }

    return Invoke-NativeChecked -Command $exe -Arguments $commandArgs -AllowedExitCodes @(0) -Label $Name -WorkingDirectory $WorkingDirectory
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

function Initialize-StateHookConfig {
    param(
        [object]$PublishConfig,
        [string]$RepoPath
    )
    $enabled = Get-OptionalBoolProperty -Object $PublishConfig -Name "state_machine_enabled" -Default $false
    $script:StateHookConfig.Enabled = $enabled
    $script:StateHookSummary.Enabled = $enabled
    if (-not $enabled) {
        return
    }

    $stateStep = Get-OptionalStringProperty -Object $PublishConfig -Name "state_step"
    if ([string]::IsNullOrWhiteSpace($stateStep)) {
        $stateStep = [string]$PublishConfig.step
    }
    if ([string]::IsNullOrWhiteSpace($stateStep)) {
        throw "state_step could not be resolved from config."
    }

    $writeBridge = Get-OptionalBoolProperty -Object $PublishConfig -Name "state_write_bridge" -Default $false
    $bridgeRoot = Get-OptionalStringProperty -Object $PublishConfig -Name "state_bridge_root"
    if ($writeBridge -and [string]::IsNullOrWhiteSpace($bridgeRoot)) {
        throw "state_bridge_root is required when state_write_bridge is true."
    }
    $resolvedBridgeRoot = ""
    if (-not [string]::IsNullOrWhiteSpace($bridgeRoot)) {
        $resolvedBridgeRoot = Resolve-RepoRelativePath -PathText $bridgeRoot -RepoPath $RepoPath
    }

    $stateFile = Get-OptionalStringProperty -Object $PublishConfig -Name "state_file"
    if (-not [string]::IsNullOrWhiteSpace($stateFile)) {
        $stateFile = Resolve-RepoRelativePath -PathText $stateFile -RepoPath $RepoPath
    } elseif ($writeBridge) {
        $stateFile = Join-Path $resolvedBridgeRoot "LAST-State.json"
    } else {
        $stateFile = Join-Path (Join-Path $RepoPath "tmp\state_machine") ("{0}_state.json" -f (Get-StateStepPathName -Step $stateStep))
    }

    $script:StateHookConfig = [pscustomobject]@{
        Enabled = $true
        Step = $stateStep
        StateFile = $stateFile
        WriteBridge = $writeBridge
        BridgeRoot = $resolvedBridgeRoot
        FailOnHookError = (Get-OptionalBoolProperty -Object $PublishConfig -Name "state_fail_on_hook_error" -Default $true)
        ExpectedBeforePhaseB = (Get-OptionalStringProperty -Object $PublishConfig -Name "state_expected_before_phase_b")
        ExpectedBeforePhaseC = (Get-OptionalStringProperty -Object $PublishConfig -Name "state_expected_before_phase_c")
        CloseOnPhaseCSuccess = (Get-OptionalBoolProperty -Object $PublishConfig -Name "state_close_on_phase_c_success" -Default $false)
        EmitMainVerified = (Get-OptionalBoolProperty -Object $PublishConfig -Name "state_emit_main_verified" -Default $true)
    }
    if ([string]::IsNullOrWhiteSpace($script:StateHookConfig.ExpectedBeforePhaseB)) {
        $script:StateHookConfig.ExpectedBeforePhaseB = "READY_TO_PUBLISH"
    }
    if ([string]::IsNullOrWhiteSpace($script:StateHookConfig.ExpectedBeforePhaseC)) {
        $script:StateHookConfig.ExpectedBeforePhaseC = "PR_CREATED"
    }
    $script:StateHookSummary.StateFile = $stateFile
    $script:StateHookSummary.BridgeRoot = if ($writeBridge) { $resolvedBridgeRoot } else { "not enabled" }
}

function Get-StateFileCurrentState {
    param([string]$StateFile)
    if ([string]::IsNullOrWhiteSpace($StateFile) -or -not (Test-Path -LiteralPath $StateFile -PathType Leaf)) {
        return ""
    }
    try {
        $payload = Get-Content -Path $StateFile -Raw | ConvertFrom-Json
    } catch {
        throw "Unable to read state_file before hook: ${StateFile}: $($_.Exception.Message)"
    }
    if (-not (Test-HasProperty -Object $payload -Name "current_state") -or [string]::IsNullOrWhiteSpace([string]$payload.current_state)) {
        throw "state_file is missing current_state before hook: $StateFile"
    }
    return ([string]$payload.current_state).Trim().ToUpperInvariant()
}

function Assert-StateHookExpectedState {
    param(
        [string]$PhaseName,
        [string]$ExpectedState
    )
    if (-not $script:StateHookConfig.Enabled -or [string]::IsNullOrWhiteSpace($ExpectedState)) {
        return
    }
    $actual = Get-StateFileCurrentState -StateFile $script:StateHookConfig.StateFile
    if ([string]::IsNullOrWhiteSpace($actual)) {
        throw "State hook expected $ExpectedState before $PhaseName but state file does not exist: $($script:StateHookConfig.StateFile)"
    }
    if (-not [string]::Equals($actual, $ExpectedState.Trim().ToUpperInvariant(), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "State hook expected $ExpectedState before $PhaseName but found $actual."
    }
}

function Invoke-StateMachineEvent {
    param(
        [string]$Event,
        [string]$RepoPath
    )
    if (-not $script:StateHookConfig.Enabled) {
        return [pscustomobject]@{ Invoked = $false; Succeeded = $true; Event = $Event; NextState = "" }
    }

    $stateScript = Join-Path $PSScriptRoot "asf_step_state_machine.py"
    if (-not (Test-Path -LiteralPath $stateScript -PathType Leaf)) {
        throw "State machine script not found: $stateScript"
    }

    $argv = @(
        "python",
        $stateScript,
        "--step",
        $script:StateHookConfig.Step,
        "--event",
        $Event,
        "--state-file",
        $script:StateHookConfig.StateFile,
        "--config-step",
        ([string]$publishConfig.step),
        "--step-title",
        ([string]$publishConfig.name),
        "--next-step",
        ([string]$publishConfig.next_step),
        "--json"
    )
    if ($script:StateHookConfig.WriteBridge) {
        $argv += "--write-bridge"
        $argv += "--bridge-root"
        $argv += $script:StateHookConfig.BridgeRoot
    }

    $result = Invoke-ArgvCommand -Name ("State machine event {0}" -f $Event) -Argv $argv -WorkingDirectory $RepoPath -AllowFailure
    $text = (($result.Output) -join [Environment]::NewLine).Trim()
    $packet = $null
    if (-not [string]::IsNullOrWhiteSpace($text)) {
        try {
            $packet = $text | ConvertFrom-Json
        } catch {
            Add-StateHookError "State machine event $Event returned non-JSON output."
        }
    } else {
        Add-StateHookError "State machine event $Event returned empty output."
    }

    $nextState = ""
    if ($null -ne $packet) {
        $script:StateHookSummary.LastEvent = [string]$packet.event
        $nextState = [string]$packet.next_state
        if (-not [string]::IsNullOrWhiteSpace($nextState)) {
            $script:StateHookSummary.FinalState = $nextState
        }
        foreach ($warning in @($packet.warnings)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$warning)) {
                $script:StateHookWarnings.Add([string]$warning)
            }
        }
    } else {
        $script:StateHookSummary.LastEvent = $Event
    }

    $failed = $result.ExitCode -ne 0
    if ($null -ne $packet -and [bool]$packet.fail_closed) {
        $failed = $true
    }
    if ($failed) {
        $reasonText = if ($null -ne $packet -and @($packet.reasons).Count -gt 0) { (@($packet.reasons) -join "; ") } else { "exit $($result.ExitCode)" }
        $message = "State machine event $Event failed: $reasonText"
        Add-StateHookError $message
        if ($script:StateHookConfig.FailOnHookError) {
            throw $message
        }
        Add-StateHookWarning $message
        return [pscustomobject]@{ Invoked = $true; Succeeded = $false; Event = $Event; NextState = $nextState }
    }

    Write-Log ("State machine event emitted: {0} -> {1}" -f $Event, $nextState)
    return [pscustomobject]@{ Invoked = $true; Succeeded = $true; Event = $Event; NextState = $nextState }
}

function Try-StateMachineFailureEvent {
    param(
        [string]$Event,
        [string]$RepoPath,
        [string]$OriginalError
    )
    if (-not $script:StateHookConfig.Enabled) {
        return
    }
    try {
        [void](Invoke-StateMachineEvent -Event $Event -RepoPath $RepoPath)
    } catch {
        $hookMessage = "Failure hook $Event failed after operational error '$OriginalError': $($_.Exception.Message)"
        Add-StateHookError $hookMessage
        throw "$OriginalError State recovery hook also failed: $($_.Exception.Message)"
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
    Assert-NoOutOfScopeFiles -RepoPath $RepoPath -ExpectedFiles @($PublishConfig.expected_files) -PublishConfig $PublishConfig
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
    Assert-StateHookExpectedState -PhaseName "Phase B" -ExpectedState $script:StateHookConfig.ExpectedBeforePhaseB
    [void](Invoke-StateMachineEvent -Event "phase_b_started" -RepoPath $RepoPath)
    try {
        & {
            Invoke-PhaseA -PublishConfig $PublishConfig -RepoPath $RepoPath
            Ensure-StepBranch -RepoPath $RepoPath -Branch ([string]$PublishConfig.branch)
            Assert-NoOutOfScopeFiles -RepoPath $RepoPath -ExpectedFiles @($PublishConfig.expected_files) -PublishConfig $PublishConfig
            [void](Invoke-Git -RepoPath $RepoPath -ArgList (@("add", "--") + @($PublishConfig.expected_files)) -Name "Stage expected files")
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--cached", "--check") -Name "Cached diff check")
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("commit", "-m", ([string]$PublishConfig.commit_message)) -Name "Create commit")
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("push", "-u", "origin", ([string]$PublishConfig.branch)) -Name "Push branch")

            $existing = Invoke-ArgvCommand -Name "Find existing PR" -Argv @("gh", "pr", "list", "--head", ([string]$PublishConfig.branch), "--json", "number", "--jq", ".[0].number") -WorkingDirectory $RepoPath -AllowFailure
            $existingNumber = (($existing.Output) -join "").Trim()
            if ($existing.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($existingNumber)) {
                $script:PrNumber = Assert-PrNumberText -Value $existingNumber -Name "Recovered PR number"
                Write-Log ("Reusing PR #{0}" -f $script:PrNumber)
            } else {
                $created = Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "create", "--base", "main", "--head", ([string]$PublishConfig.branch), "--title", ([string]$PublishConfig.pr_title), "--body", ([string]$PublishConfig.pr_body)) -Name "Create PR"
                $createdText = ($created.Output -join [Environment]::NewLine)
                $numberMatch = [regex]::Match($createdText, "/pull/(\d+)")
                if ($numberMatch.Success) {
                    $script:PrNumber = Assert-PrNumberText -Value $numberMatch.Groups[1].Value -Name "Created PR number"
                }
                Write-Log ("Created PR reference: {0}" -f $createdText)
            }
            if ([string]::IsNullOrWhiteSpace([string]$script:PrNumber)) {
                throw "Phase B did not resolve a non-empty numeric PR number after PR list/create."
            }
        }
    } catch {
        $phaseError = $_.Exception.Message
        Try-StateMachineFailureEvent -Event "phase_b_failed" -RepoPath $RepoPath -OriginalError $phaseError
        throw $phaseError
    }
    try {
        [void](Invoke-StateMachineEvent -Event "phase_b_passed" -RepoPath $RepoPath)
        [void](Invoke-StateMachineEvent -Event "pr_created" -RepoPath $RepoPath)
    } catch {
        Add-StateHookWarning "Phase B operational actions finished, but success hook failed; manual state recovery/check is required."
        throw
    }
    Write-Log "PHASE B completed. Merge was not performed."
}

function Assert-PrNumberText {
    param(
        [object]$Value,
        [string]$Name = "PrNumber"
    )
    $text = Assert-NonEmptyString -Value $Value -Name $Name
    if ($text -notmatch "^\d+$") {
        throw "$Name must be numeric."
    }
    return $text
}

function Get-PrNumber {
    param(
        [object]$PublishConfig
    )
    if ($script:RequestedPrNumber -gt 0) {
        return Assert-PrNumberText -Value ([string]$script:RequestedPrNumber) -Name "PrNumber"
    }
    if ((Test-HasProperty -Object $PublishConfig -Name "pr_number") -and ([int]$PublishConfig.pr_number -gt 0)) {
        return Assert-PrNumberText -Value ([string]$PublishConfig.pr_number) -Name "Config field pr_number"
    }
    throw "Phase C requires a non-empty -PrNumber or config pr_number before any PR command is executed."
}

function Invoke-GhPrChecks {
    param(
        [object]$PublishConfig,
        [string]$RepoPath,
        [string]$Number
    )
    $checkedNumber = Assert-NonEmptyString -Value $Number -Name "PrNumber"
    # GitHub can return exit 1 with "no checks reported"; that single case is
    # classified below as a warning when the config explicitly allows it.
    $result = Invoke-NativeChecked -Command "gh" -Arguments @("pr", "checks", $checkedNumber, "--watch") -AllowedExitCodes @(0, 1) -Label "GH PR checks watch" -WorkingDirectory $RepoPath
    $exitCode = $result.ExitCode
    $text = ($result.Output -join [Environment]::NewLine)
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
    $number = Get-PrNumber -PublishConfig $PublishConfig
    Write-Log "PHASE C - merge and final verification"
    Assert-StateHookExpectedState -PhaseName "Phase C" -ExpectedState $script:StateHookConfig.ExpectedBeforePhaseC
    [void](Invoke-StateMachineEvent -Event "phase_c_started" -RepoPath $RepoPath)
    try {
        $script:PrNumber = $number
        & {
            [void](Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "view", $number) -Name "View PR")
            Invoke-GhPrChecks -PublishConfig $PublishConfig -RepoPath $RepoPath -Number $number
            [void](Invoke-Gh -RepoPath $RepoPath -ArgList @("pr", "merge", $number, "--squash") -Name "Merge PR")
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("switch", "main") -Name "Switch main")
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("pull", "--ff-only", "origin", "main") -Name "Pull main")
            Invoke-ConfiguredChecks -Checks @($PublishConfig.phase_c_checks) -RepoPath $RepoPath
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "diff", "--check") -Name "Final diff check")
            $status = @(Get-RepositoryChangedFiles -RepoPath $RepoPath)
            if ($status.Count -gt 0) {
                throw "Working tree is not clean after merge: $($status -join ', ')"
            }
            [void](Invoke-Git -RepoPath $RepoPath -ArgList @("--no-pager", "log", "--oneline", "--max-count=$([int]$PublishConfig.log_max_count)") -Name "Final log")
        }
    } catch {
        $phaseError = $_.Exception.Message
        Try-StateMachineFailureEvent -Event "phase_c_failed" -RepoPath $RepoPath -OriginalError $phaseError
        throw $phaseError
    }
    try {
        [void](Invoke-StateMachineEvent -Event "phase_c_passed" -RepoPath $RepoPath)
        if ($script:StateHookConfig.EmitMainVerified) {
            [void](Invoke-StateMachineEvent -Event "main_verified" -RepoPath $RepoPath)
        }
        if ($script:StateHookConfig.CloseOnPhaseCSuccess) {
            [void](Invoke-StateMachineEvent -Event "close_step" -RepoPath $RepoPath)
            $script:StateHookSummary.CloseStepEmitted = $true
        }
    } catch {
        Add-StateHookWarning "Phase C operational actions finished, but success hook failed; manual state recovery/check is required."
        throw
    }
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
        if ($script:RequestedPrNumber -gt 0) {
            $items += @("-PrNumber", [string]$script:RequestedPrNumber)
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

function New-DefaultPublishChecks {
    return @(
        [pscustomobject]@{
            name = "Full pytest"
            argv = @("python", "-m", "pytest")
        },
        [pscustomobject]@{
            name = "Workflow Health Check"
            argv = @("python", "scripts/check_workflow_health.py")
        },
        [pscustomobject]@{
            name = "Verification Gate"
            argv = @("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1")
        }
    )
}

function New-DraftPublishConfig {
    param(
        [string]$RepoPath,
        [string[]]$ChangedFiles
    )
    $step = Assert-NonEmptyString -Value $StepNumber -Name "StepNumber"
    $name = Assert-NonEmptyString -Value $StepName -Name "StepName"
    $branch = Assert-NonEmptyString -Value $BranchName -Name "BranchName"
    $commit = Assert-NonEmptyString -Value $CommitMessage -Name "CommitMessage"
    $title = Assert-NonEmptyString -Value $PrTitle -Name "PrTitle"
    $next = Assert-NonEmptyString -Value $NextStep -Name "NextStep"
    $profile = Assert-NonEmptyString -Value $VerificationProfile -Name "VerificationProfile"
    $risk = Assert-NonEmptyString -Value $RiskLevel -Name "RiskLevel"
    $phase = Assert-NonEmptyString -Value $VerificationPhase -Name "VerificationPhase"
    $expectedProfile = $ProfileSelectorExpectedProfile
    if ([string]::IsNullOrWhiteSpace($expectedProfile)) {
        $expectedProfile = $profile
    }
    $body = $PrBody
    if ([string]::IsNullOrWhiteSpace($body)) {
        $body = "Implements STEP $step $name. Generated by PrepareConfig as a human-reviewed draft scope; no publish action was executed."
    }
    $bridge = $BridgeRoot
    if ([string]::IsNullOrWhiteSpace($bridge)) {
        $bridge = $DefaultBridgeRoot
    }

    return [pscustomobject][ordered]@{
        step = $step
        name = $name
        repo_path = "."
        bridge_root = $bridge
        branch = $branch
        commit_message = $commit
        pr_title = $title
        pr_body = $body
        next_step = $next
        expected_files = @($ChangedFiles)
        changed_files = @($ChangedFiles)
        verification_profile = $profile
        risk_level = $risk
        verification_phase = $phase
        profile_selector_expected_profile = $expectedProfile
        intent = @("publish_step", "human_gated")
        provided_gates = @()
        phase_a_checks = @(New-DefaultPublishChecks)
        phase_c_checks = @(New-DefaultPublishChecks)
        allow_no_github_checks_reported = $true
        log_max_count = 12
    }
}

function Write-PrepareConfigOutputs {
    param(
        [object]$DraftConfig,
        [string]$RepoPath,
        [string[]]$ChangedFiles
    )
    $root = Get-BridgeRoot -PublishConfig $DraftConfig
    [void][System.IO.Directory]::CreateDirectory($root)
    $name = Get-SafeName -Value ([string]$DraftConfig.name)
    $prefix = [string]$DraftConfig.step
    $configPath = Join-Path $root ("{0}-Publish_Config_Draft_{1}.json" -f $prefix, $name)
    $reviewPath = Join-Path $root ("{0}-PrepareConfig_Review_{1}.md" -f $prefix, $name)
    $lastConfigPath = Join-Path $root "LAST-Publish_Config_Draft.json"
    $lastReviewPath = Join-Path $root "LAST-PrepareConfig_Review.md"

    $DraftConfig | ConvertTo-Json -Depth 20 | Set-Content -Path $configPath -Encoding UTF8
    Copy-Item -Path $configPath -Destination $lastConfigPath -Force

    $changedText = if (@($ChangedFiles).Count -gt 0) { (@($ChangedFiles) -join [Environment]::NewLine) } else { "none" }
    $review = @(
        "# ASF publish PrepareConfig review",
        "",
        ("- Step: ``{0}``" -f $DraftConfig.step),
        ("- Name: ``{0}``" -f $DraftConfig.name),
        ("- Repo path: ``{0}``" -f $RepoPath),
        "- Status: ``DRAFT_REVIEW_REQUIRED``",
        "",
        "PrepareConfig discovered changed files using stdout-only Git commands:",
        "",
        '- `git --no-pager diff --name-only --`',
        '- `git --no-pager diff --cached --name-only --`',
        '- `git ls-files --others --exclude-standard --`',
        "",
        'The generated JSON is a draft. Review `expected_files` and `changed_files` before Phase B. Do not publish automatically from this output.',
        "",
        "## Changed files",
        "",
        "```text",
        $changedText,
        "```",
        "",
        "## Draft config",
        "",
        ("Config JSON: ``{0}``" -f $configPath),
        "",
        "## Recovery policy",
        "",
        "If Phase B later reports out-of-scope changes, review the recovery report and suggested config. Add files to scope only after human review.",
        "",
        "No commit, push, PR, merge, deploy or tag was executed."
    ) -join [Environment]::NewLine
    Set-Content -Path $reviewPath -Value $review -Encoding UTF8
    Copy-Item -Path $reviewPath -Destination $lastReviewPath -Force

    Write-Log ("PrepareConfig draft config written: {0}" -f $configPath)
    Write-Log ("PrepareConfig review report written: {0}" -f $reviewPath)
    Copy-FileToClipboard -File $reviewPath
}

function Invoke-PrepareConfig {
    $repoPath = [System.IO.Path]::GetFullPath((Get-Location).Path)
    Assert-Repo -RepoPath $repoPath
    $changedFiles = @(Get-RepositoryChangedFiles -RepoPath $repoPath)
    if ($changedFiles.Count -eq 0) {
        throw "PrepareConfig found no changed files. Refusing to generate an empty publish scope."
    }
    $draft = New-DraftPublishConfig -RepoPath $repoPath -ChangedFiles @($changedFiles)
    Assert-PublishConfig -PublishConfig $draft
    Write-PrepareConfigOutputs -DraftConfig $draft -RepoPath $repoPath -ChangedFiles @($changedFiles)
    Write-Log "PrepareConfig completed. Review the draft config before Phase B."
}

function Get-ProfileValidationSummaryLines {
    if (-not $script:ProfileValidation.Enabled) {
        return @("Verification profile validation: not configured")
    }
    $reasons = if (@($script:ProfileValidation.Reasons).Count -gt 0) { (@($script:ProfileValidation.Reasons) -join "; ") } else { "none" }
    $warnings = if (@($script:ProfileValidation.Warnings).Count -gt 0) { (@($script:ProfileValidation.Warnings) -join "; ") } else { "none" }
    return @(
        ("Verification profile validation: {0}" -f $script:ProfileValidation.Status),
        ("Declared verification profile: {0}" -f $script:ProfileValidation.DeclaredProfile),
        ("Recommended verification profile: {0}" -f $script:ProfileValidation.RecommendedProfile),
        ("Selector fail_closed: {0}" -f $script:ProfileValidation.SelectorFailClosed),
        ("Profile check reduction allowed: {0}" -f $script:ProfileValidation.AllowReduction),
        ("Phase C reduction: {0}" -f $script:ProfileValidation.PhaseCReduction),
        ("Profile reasons: {0}" -f $reasons),
        ("Profile warnings: {0}" -f $warnings)
    )
}

function Get-StateHookSummaryLines {
    $hookWarnings = if ($script:StateHookWarnings.Count -gt 0) { (@($script:StateHookWarnings) | Select-Object -Unique) -join "; " } else { "none" }
    $hookErrors = if ($script:StateHookErrors.Count -gt 0) { (@($script:StateHookErrors) | Select-Object -Unique) -join "; " } else { "none" }
    return @(
        ("State machine enabled: {0}" -f $script:StateHookSummary.Enabled),
        ("State file: {0}" -f $script:StateHookSummary.StateFile),
        ("State bridge root: {0}" -f $script:StateHookSummary.BridgeRoot),
        ("Last state event emitted: {0}" -f $script:StateHookSummary.LastEvent),
        ("Final state: {0}" -f $script:StateHookSummary.FinalState),
        ("Close step emitted: {0}" -f $script:StateHookSummary.CloseStepEmitted),
        ("Hook warnings: {0}" -f $hookWarnings),
        ("Hook errors: {0}" -f $hookErrors)
    )
}

function Get-BridgeStatusLabel {
    param([string]$Status)
    if ([string]::Equals($Status, "PASS", [System.StringComparison]::OrdinalIgnoreCase)) {
        if ($script:WarningLines.Count -gt 0) {
            return "COMPLETATO CON WARNING NON BLOCCANTE"
        }
        return "COMPLETATO"
    }
    if ([string]::Equals($Status, "FAIL", [System.StringComparison]::OrdinalIgnoreCase)) {
        return "BLOCCATO"
    }
    return $Status
}

function Add-UniqueWarningLine {
    param([string]$Message)
    if (-not $script:WarningLines.Contains($Message)) {
        Add-WarningLine $Message
    }
}

function New-BridgeFileOperationResult {
    param(
        [string]$Label,
        [string]$Path,
        [bool]$Success,
        [int]$Attempts,
        [string]$ErrorMessage = "",
        [bool]$FallbackUsed = $false,
        [string]$FallbackPath = "",
        [string]$EffectivePath = ""
    )

    if ([string]::IsNullOrWhiteSpace($EffectivePath)) {
        $EffectivePath = if ($FallbackUsed) { $FallbackPath } else { $Path }
    }

    return [pscustomobject]@{
        Label = $Label
        Path = $Path
        Success = $Success
        Attempts = $Attempts
        ErrorMessage = $ErrorMessage
        FallbackUsed = $FallbackUsed
        FallbackPath = $FallbackPath
        EffectivePath = $EffectivePath
    }
}

function Invoke-BridgeFileOperationWithRetry {
    param(
        [string]$Label,
        [scriptblock]$Operation,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500
    )

    if ($MaxAttempts -lt 1) {
        throw "MaxAttempts must be at least 1."
    }
    if ($DelayMilliseconds -lt 0) {
        throw "DelayMilliseconds cannot be negative."
    }

    $lastError = ""
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            & $Operation
            return [pscustomobject]@{
                Success = $true
                Attempts = $attempt
                ErrorMessage = ""
            }
        } catch {
            $lastError = $_.Exception.Message
            if ($attempt -lt $MaxAttempts) {
                Write-Log ("Bridge file retry {0}/{1} for {2}: {3}" -f $attempt, $MaxAttempts, $Label, $lastError)
                Start-Sleep -Milliseconds $DelayMilliseconds
            }
        }
    }

    return [pscustomobject]@{
        Success = $false
        Attempts = $MaxAttempts
        ErrorMessage = $lastError
    }
}

function Set-ContentWithRetry {
    param(
        [string]$Path,
        [string]$Value,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500
    )

    return Invoke-BridgeFileOperationWithRetry -Label ("write {0}" -f $Path) -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds -Operation {
        Set-Content -LiteralPath $Path -Value $Value -Encoding UTF8 -ErrorAction Stop
    }
}

function Copy-ItemWithRetry {
    param(
        [string]$Path,
        [string]$Destination,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500
    )

    return Invoke-BridgeFileOperationWithRetry -Label ("copy {0} to {1}" -f $Path, $Destination) -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds -Operation {
        if (Test-Path -LiteralPath $Destination -PathType Container) {
            throw ("Destination is a directory, not a file: {0}" -f $Destination)
        }
        Copy-Item -LiteralPath $Path -Destination $Destination -Force -ErrorAction Stop
    }
}

function Move-ItemWithRetry {
    param(
        [string]$Path,
        [string]$Destination,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500
    )

    return Invoke-BridgeFileOperationWithRetry -Label ("move {0} to {1}" -f $Path, $Destination) -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds -Operation {
        if (Test-Path -LiteralPath $Destination -PathType Container) {
            throw ("Destination is a directory, not a file: {0}" -f $Destination)
        }
        Move-Item -LiteralPath $Path -Destination $Destination -Force -ErrorAction Stop
    }
}

function New-FallbackBridgePath {
    param(
        [string]$Path,
        [datetime]$Stamp = (Get-Date)
    )

    $directory = Split-Path -Parent $Path
    $leaf = Split-Path -Leaf $Path
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($leaf)
    $extension = [System.IO.Path]::GetExtension($leaf)
    $stampText = $Stamp.ToString("yyyyMMdd_HHmmss")
    return (Join-Path $directory ("{0}_fallback_{1}{2}" -f $baseName, $stampText, $extension))
}

function Write-BridgeFileWithRetry {
    param(
        [string]$Label,
        [string]$Path,
        [string]$Value,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500,
        [datetime]$FallbackStamp = (Get-Date)
    )

    $directory = Split-Path -Parent $Path
    [void][System.IO.Directory]::CreateDirectory($directory)
    $leaf = Split-Path -Leaf $Path
    $tempPath = Join-Path $directory (".{0}.{1}.tmp" -f $leaf, ([guid]::NewGuid().ToString("N")))

    $tempResult = Set-ContentWithRetry -Path $tempPath -Value $Value -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds
    if (-not $tempResult.Success) {
        return New-BridgeFileOperationResult -Label $Label -Path $Path -Success $false -Attempts $tempResult.Attempts -ErrorMessage $tempResult.ErrorMessage -EffectivePath ""
    }

    $moveResult = Move-ItemWithRetry -Path $tempPath -Destination $Path -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds
    if ($moveResult.Success) {
        return New-BridgeFileOperationResult -Label $Label -Path $Path -Success $true -Attempts $moveResult.Attempts
    }

    $fallbackPath = New-FallbackBridgePath -Path $Path -Stamp $FallbackStamp
    $fallbackResult = Move-ItemWithRetry -Path $tempPath -Destination $fallbackPath -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds
    if ($fallbackResult.Success) {
        return New-BridgeFileOperationResult -Label $Label -Path $Path -Success $true -Attempts $moveResult.Attempts -ErrorMessage $moveResult.ErrorMessage -FallbackUsed $true -FallbackPath $fallbackPath
    }

    return New-BridgeFileOperationResult -Label $Label -Path $Path -Success $false -Attempts $moveResult.Attempts -ErrorMessage ("primary: {0}; fallback: {1}" -f $moveResult.ErrorMessage, $fallbackResult.ErrorMessage) -FallbackPath $fallbackPath -EffectivePath ""
}

function Update-LastFileWithRetry {
    param(
        [string]$Label,
        [string]$Source,
        [string]$LastPath,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500,
        [datetime]$FallbackStamp = (Get-Date)
    )

    if ([string]::IsNullOrWhiteSpace($Source) -or -not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        return New-BridgeFileOperationResult -Label $Label -Path $LastPath -Success $false -Attempts 0 -ErrorMessage ("Source file is missing: {0}" -f $Source) -EffectivePath ""
    }

    $copyResult = Copy-ItemWithRetry -Path $Source -Destination $LastPath -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds
    if ($copyResult.Success) {
        return New-BridgeFileOperationResult -Label $Label -Path $LastPath -Success $true -Attempts $copyResult.Attempts
    }

    $fallbackPath = New-FallbackBridgePath -Path $LastPath -Stamp $FallbackStamp
    $fallbackResult = Copy-ItemWithRetry -Path $Source -Destination $fallbackPath -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds
    if ($fallbackResult.Success) {
        return New-BridgeFileOperationResult -Label $Label -Path $LastPath -Success $true -Attempts $copyResult.Attempts -ErrorMessage $copyResult.ErrorMessage -FallbackUsed $true -FallbackPath $fallbackPath
    }

    return New-BridgeFileOperationResult -Label $Label -Path $LastPath -Success $false -Attempts $copyResult.Attempts -ErrorMessage ("primary: {0}; fallback: {1}" -f $copyResult.ErrorMessage, $fallbackResult.ErrorMessage) -FallbackPath $fallbackPath -EffectivePath ""
}

function Format-BridgeOperationSummaryLines {
    param(
        [object[]]$Results,
        [string]$EmptyMessage
    )

    if ($null -eq $Results -or @($Results).Count -eq 0) {
        return @($EmptyMessage)
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($result in @($Results)) {
        if ($result.Success -and $result.FallbackUsed) {
            $lines.Add(("- WARNING: {0}: primary blocked after retry; fallback written. Primary: {1}; fallback: {2}" -f $result.Label, $result.Path, $result.FallbackPath))
        } elseif ($result.Success) {
            $lines.Add(("- OK: {0}: {1}" -f $result.Label, $result.EffectivePath))
        } else {
            $lines.Add(("- FAILED: {0}: {1}; error: {2}" -f $result.Label, $result.Path, $result.ErrorMessage))
        }
    }
    return @($lines)
}

function Add-BridgeOperationWarnings {
    param(
        [object[]]$Results,
        [string]$Context
    )

    foreach ($result in @($Results)) {
        if ($result.Success -and $result.FallbackUsed) {
            Add-UniqueWarningLine ("{0}: primary path blocked after retry; fallback used for {1}. Primary: {2}; fallback: {3}" -f $Context, $result.Label, $result.Path, $result.FallbackPath)
        } elseif (-not $result.Success) {
            Add-UniqueWarningLine ("{0}: failed after retry for {1}. Path: {2}. Error: {3}" -f $Context, $result.Label, $result.Path, $result.ErrorMessage)
        }
    }
}

function Update-BridgeLastOutputs {
    param(
        [string]$Root,
        [hashtable]$SourcePaths,
        [bool]$DocxWritten,
        [int]$MaxAttempts = 5,
        [int]$DelayMilliseconds = 500,
        [datetime]$FallbackStamp = (Get-Date)
    )

    $mappings = @(
        [pscustomobject]@{ Label = "LAST-Richiesta_Generazione.txt"; Source = $SourcePaths["Request"]; LastPath = (Join-Path $Root "LAST-Richiesta_Generazione.txt") },
        [pscustomobject]@{ Label = "LAST-Comando_Eseguito.ps1"; Source = $SourcePaths["Command"]; LastPath = (Join-Path $Root "LAST-Comando_Eseguito.ps1") },
        [pscustomobject]@{ Label = "LAST-Output_Completo.txt"; Source = $SourcePaths["Full"]; LastPath = (Join-Path $Root "LAST-Output_Completo.txt") },
        [pscustomobject]@{ Label = "LAST-Output_Compatto.md"; Source = $SourcePaths["Compact"]; LastPath = (Join-Path $Root "LAST-Output_Compatto.md") }
    )
    if ($DocxWritten -and $SourcePaths.ContainsKey("Docx")) {
        $mappings += [pscustomobject]@{ Label = "LAST-Output_Compatto.docx"; Source = $SourcePaths["Docx"]; LastPath = (Join-Path $Root "LAST-Output_Compatto.docx") }
    } elseif ($SourcePaths.ContainsKey("DocxFailed")) {
        $mappings += [pscustomobject]@{ Label = "LAST-Output_Compatto.docx.failed.txt"; Source = $SourcePaths["DocxFailed"]; LastPath = (Join-Path $Root "LAST-Output_Compatto.docx.failed.txt") }
    }

    $results = [System.Collections.Generic.List[object]]::new()
    foreach ($mapping in $mappings) {
        $result = Update-LastFileWithRetry -Label $mapping.Label -Source $mapping.Source -LastPath $mapping.LastPath -MaxAttempts $MaxAttempts -DelayMilliseconds $DelayMilliseconds -FallbackStamp $FallbackStamp
        $results.Add($result)
    }
    return @($results)
}

function Validate-BridgeLastOutputs {
    param(
        [object[]]$LastResults
    )

    $issues = [System.Collections.Generic.List[string]]::new()
    foreach ($result in @($LastResults)) {
        if (-not $result.Success) {
            $issues.Add(("LAST validation failed for {0}: {1}" -f $result.Label, $result.ErrorMessage))
        } elseif ($result.FallbackUsed) {
            $issues.Add(("LAST validation warning for {0}: primary LAST not updated; fallback written to {1}" -f $result.Label, $result.FallbackPath))
        } elseif (-not (Test-Path -LiteralPath $result.EffectivePath -PathType Leaf)) {
            $issues.Add(("LAST validation failed for {0}: missing {1}" -f $result.Label, $result.EffectivePath))
        }
    }

    if ($issues.Count -eq 0) {
        return @("LAST validation PASS: primary LAST files updated.")
    }
    return @($issues)
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
    $prText = if ($null -ne $script:PrNumber) { [string]$script:PrNumber } else { "not available" }
    $profileSummary = Get-ProfileValidationSummaryLines
    $stateHookSummary = Get-StateHookSummaryLines
    $commandText = $shortCommand + [Environment]::NewLine

    $numbered = @{
        Request = Join-Path $root ("{0}-Richiesta_Generazione_{1}.txt" -f $prefix, $name)
        Command = Join-Path $root ("{0}-Comando_Eseguito_{1}.ps1" -f $prefix, $name)
        Full = Join-Path $root ("{0}-Output_Completo_{1}.txt" -f $prefix, $name)
        Compact = Join-Path $root ("{0}-Output_Compatto_{1}.md" -f $prefix, $name)
        Docx = Join-Path $root ("{0}-Output_Compatto_{1}.docx" -f $prefix, $name)
        DocxFailed = Join-Path $root ("{0}-Output_Compatto_{1}.docx.failed.txt" -f $prefix, $name)
    }

    $fallbackStamp = Get-Date
    $bridgeWriteResults = [System.Collections.Generic.List[object]]::new()
    $lastUpdateResults = @()
    $lastValidationLines = @("LAST validation pending.")
    $sourcePaths = @{}

    $buildPayload = {
        $fence = -join @([char]96, [char]96, [char]96)
        $warnings = if ($script:WarningLines.Count -gt 0) { $script:WarningLines -join [Environment]::NewLine } else { "none" }
        $displayStatus = Get-BridgeStatusLabel -Status $Status
        $bridgeSummaryLines = Format-BridgeOperationSummaryLines -Results ($bridgeWriteResults.ToArray()) -EmptyMessage "Bridge retry/fallback summary: pending."
        $lastSummaryLines = Format-BridgeOperationSummaryLines -Results @($lastUpdateResults) -EmptyMessage "LAST update summary: pending."
        $lastValidationText = if (@($lastValidationLines).Count -gt 0) { @($lastValidationLines) -join [Environment]::NewLine } else { "LAST validation pending." }
        $requestText = @(
            "ASF Publish Step Runner",
            "Step: $($PublishConfig.step)",
            "Name: $($PublishConfig.name)",
            "Phase: $EffectivePhase",
            "Status: $displayStatus",
            "Machine status: $Status",
            "Next step: $($PublishConfig.next_step)",
            "",
            "Verification profile:",
            ($profileSummary -join [Environment]::NewLine),
            "",
            "State machine hooks:",
            ($stateHookSummary -join [Environment]::NewLine),
            "",
            "Bridge retry/fallback:",
            ($bridgeSummaryLines -join [Environment]::NewLine),
            "",
            "LAST validation:",
            $lastValidationText
        ) -join [Environment]::NewLine
        $fullText = @(
            "ASF Publish Step Runner - full output",
            "Status: $displayStatus",
            "Machine status: $Status",
            "PR number: $prText",
            "Warnings:",
            $warnings,
            "",
            "Verification profile:",
            ($profileSummary -join [Environment]::NewLine),
            "",
            "State machine hooks:",
            ($stateHookSummary -join [Environment]::NewLine),
            "",
            "Bridge retry/fallback:",
            ($bridgeSummaryLines -join [Environment]::NewLine),
            "",
            "LAST update:",
            ($lastSummaryLines -join [Environment]::NewLine),
            "",
            "LAST validation:",
            $lastValidationText,
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
            ("- Status: ``{0}``" -f $displayStatus),
            ("- Machine status: ``{0}``" -f $Status),
            ("- PR number: ``{0}``" -f $prText),
            ("- Next step: ``{0}``" -f $PublishConfig.next_step),
            "",
            "## Verification profile",
            "",
            ($profileSummary -join [Environment]::NewLine),
            "",
            "## State machine hooks",
            "",
            ($stateHookSummary -join [Environment]::NewLine),
            "",
            "## Output accessory policy",
            "",
            "TXT and Markdown are primary outputs. Compact Markdown is mandatory and must be written to the primary path or a timestamped fallback. DOCX is best-effort; a DOCX failure after required gates is a non-blocking warning.",
            "",
            "Gate failed = BLOCCATO. Git, PR, tests, verify gate or diff-check failed = BLOCCATO. Bridge output primary path blocked after gates passed = retry, timestamped fallback, then COMPLETATO CON WARNING NON BLOCCANTE.",
            "",
            "## Retry/fallback Bridge",
            "",
            ($bridgeSummaryLines -join [Environment]::NewLine),
            "",
            "## LAST validation",
            "",
            ($lastSummaryLines -join [Environment]::NewLine),
            "",
            $lastValidationText,
            "",
            "## Short command",
            "",
            ($fence + "powershell"),
            $shortCommand,
            $fence,
            "",
            "## Warnings",
            "",
            $warnings
        ) -join [Environment]::NewLine
        return [pscustomobject]@{
            Request = $requestText
            Full = $fullText
            Compact = $compactText
        }
    }

    $payload = & $buildPayload
    $textOutputs = @(
        [pscustomobject]@{ Kind = "Request"; Label = "numbered request"; Path = $numbered.Request; Value = $payload.Request; Required = $false },
        [pscustomobject]@{ Kind = "Command"; Label = "numbered command"; Path = $numbered.Command; Value = $commandText; Required = $false },
        [pscustomobject]@{ Kind = "Full"; Label = "numbered full output"; Path = $numbered.Full; Value = $payload.Full; Required = $false },
        [pscustomobject]@{ Kind = "Compact"; Label = "numbered compact Markdown"; Path = $numbered.Compact; Value = $payload.Compact; Required = $true }
    )

    foreach ($item in $textOutputs) {
        $result = Write-BridgeFileWithRetry -Label $item.Label -Path $item.Path -Value $item.Value -FallbackStamp $fallbackStamp
        $bridgeWriteResults.Add($result)
        if ($result.Success) {
            $sourcePaths[$item.Kind] = $result.EffectivePath
        } elseif ($item.Required) {
            Add-BridgeOperationWarnings -Results @($result) -Context "Bridge output"
            throw ("Mandatory compact Markdown Bridge output failed after retry and fallback: {0}" -f $result.ErrorMessage)
        }
    }
    Add-BridgeOperationWarnings -Results ($bridgeWriteResults.ToArray()) -Context "Bridge output"

    $docxWritten = $false
    try {
        Write-MinimalDocx -Path $numbered.Docx -Text $payload.Compact
        $docxWritten = $true
        $sourcePaths["Docx"] = $numbered.Docx
    } catch {
        $docxMessage = "DOCX accessory output failed without blocking primary TXT/Markdown outputs: $($_.Exception.Message)"
        Add-WarningLine $docxMessage
        $docxFailedResult = Write-BridgeFileWithRetry -Label "DOCX failure marker" -Path $numbered.DocxFailed -Value $docxMessage -FallbackStamp $fallbackStamp
        $bridgeWriteResults.Add($docxFailedResult)
        if ($docxFailedResult.Success) {
            $sourcePaths["DocxFailed"] = $docxFailedResult.EffectivePath
        }
        Add-BridgeOperationWarnings -Results @($docxFailedResult) -Context "Bridge output"
    }

    $lastUpdateResults = @(Update-BridgeLastOutputs -Root $root -SourcePaths $sourcePaths -DocxWritten $docxWritten -FallbackStamp $fallbackStamp)
    Add-BridgeOperationWarnings -Results @($lastUpdateResults) -Context "LAST update"
    $lastValidationLines = @(Validate-BridgeLastOutputs -LastResults $lastUpdateResults)
    foreach ($line in $lastValidationLines) {
        if ($line -notlike "LAST validation PASS*") {
            Add-UniqueWarningLine $line
        }
    }

    $payload = & $buildPayload
    $finalTextOutputs = @(
        [pscustomobject]@{ Kind = "Request"; Label = "final numbered request"; Path = $numbered.Request; Value = $payload.Request; Required = $false },
        [pscustomobject]@{ Kind = "Full"; Label = "final numbered full output"; Path = $numbered.Full; Value = $payload.Full; Required = $false },
        [pscustomobject]@{ Kind = "Compact"; Label = "final numbered compact Markdown"; Path = $numbered.Compact; Value = $payload.Compact; Required = $true }
    )
    $finalWriteResults = [System.Collections.Generic.List[object]]::new()
    foreach ($item in $finalTextOutputs) {
        $result = Write-BridgeFileWithRetry -Label $item.Label -Path $item.Path -Value $item.Value -FallbackStamp $fallbackStamp
        $finalWriteResults.Add($result)
        $bridgeWriteResults.Add($result)
        if ($result.Success) {
            $sourcePaths[$item.Kind] = $result.EffectivePath
        } elseif ($item.Required) {
            Add-BridgeOperationWarnings -Results @($result) -Context "Bridge output"
            throw ("Mandatory compact Markdown Bridge output failed after final retry and fallback: {0}" -f $result.ErrorMessage)
        }
    }
    Add-BridgeOperationWarnings -Results ($finalWriteResults.ToArray()) -Context "Bridge output"

    $lastUpdateResults = @(Update-BridgeLastOutputs -Root $root -SourcePaths $sourcePaths -DocxWritten $docxWritten -FallbackStamp $fallbackStamp)
    Add-BridgeOperationWarnings -Results @($lastUpdateResults) -Context "LAST update"
    $lastValidationLines = @(Validate-BridgeLastOutputs -LastResults $lastUpdateResults)
    foreach ($line in $lastValidationLines) {
        if ($line -notlike "LAST validation PASS*") {
            Add-UniqueWarningLine $line
        }
    }

    $lastCompactPath = $sourcePaths["Compact"]
    foreach ($result in @($lastUpdateResults)) {
        if ($result.Label -eq "LAST-Output_Compatto.md" -and $result.Success) {
            $lastCompactPath = $result.EffectivePath
        }
    }
    Copy-FileToClipboard -File $lastCompactPath
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

    if ($Phase -eq "PrepareConfig") {
        Invoke-PrepareConfig
        exit 0
    }

    $publishConfig = Read-PublishConfig -Path $Config
    Assert-PublishConfig -PublishConfig $publishConfig
    $repoPath = Get-RepoPath -PublishConfig $publishConfig
    Initialize-StateHookConfig -PublishConfig $publishConfig -RepoPath $repoPath
    Invoke-VerificationProfileValidation -PublishConfig $publishConfig -RepoPath $repoPath

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
