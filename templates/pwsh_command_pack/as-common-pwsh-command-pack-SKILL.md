---
name: "as-common-pwsh-command-pack"
description: "Generate safe logged PowerShell command packs for Alberto with short safe bootstraps, generated .ps1 scripts, progressive NNNN-II artifacts, compact Markdown/DOCX reports, file-only handoff, robust Git parsing, PR-first publication, and Git/Codex/ASF guardrails."
---

# as-common-pwsh-command-pack

Use this skill when Alberto asks for PowerShell command packs, robust Windows command sequences, ASF/Git/Codex verification command packs, Bridge/audit artifacts, or logged scripts that produce reusable output files.

Do not use this skill as the default wrapper for Codex prompts. The default Codex handoff is a clean, self-contained prompt. Use PowerShell only when Alberto asks for Bridge output, audit trail, controlled verification, or controlled publication.

## Canonical Standard

Safe Bootstrap PowerShell Command Pack:

1. Generate a short PowerShell bootstrap.
2. The bootstrap writes a complete `.ps1` file in `pwsh_command`.
3. The bootstrap validates parsing with `[scriptblock]::Create($ScriptText) | Out-Null`.
4. Only if parse-check passes, execute `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`.
5. All complex logic lives in the generated `.ps1`.
6. The pasted terminal block stays short and robust.
7. The outer wrapper does not contain complex Git logic.
8. The outer wrapper does not contain nested here-strings.
9. The outer wrapper does not use fragile `try/finally`.
10. The final line is actually executable, for example `Write-Host ";"`.
11. The pack generates only progressive `NNNN-II-Tipo_Nome.ext` artifacts.
12. The pack does not generate or read `LAST-*` artifacts.

## Bootstrap Requirements

The bootstrap must include:

- wrapper `& { ... }`;
- `$ErrorActionPreference = "Stop"`;
- `$PSNativeCommandUseErrorActionPreference = $false`;
- Bridge directory creation;
- request file generation;
- command `.ps1` generation;
- no `LAST-*` artifacts;
- parse-check with `[scriptblock]::Create($ScriptText) | Out-Null`;
- execution with `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`;
- explicit `$LASTEXITCODE` handling;
- clear final message;
- executable final line.

## Generated Script Requirements

The `.ps1` script should contain, when pertinent:

- robust logging;
- full output artifact;
- compact Markdown artifact;
- DOCX best-effort/non-blocking artifact;
- progressive `NNNN-II-Tipo_Nome.ext` artifacts only;
- file-only handoff with no automatic appunti write;
- native command wrapper with allowed exit codes;
- `git --no-pager` for long Git output;
- robust Git status parser;
- scope guard before staging;
- tests;
- workflow health check;
- verify gate;
- PR-first publication.

Use `ArgList` as the native-command argument parameter name:

```powershell
function Invoke-NativeCommand {
    param(
        [string] $FileName,
        [string[]] $ArgList = @()
    )
}
```

Do not use `$Args` as a parameter name. `$args` is a PowerShell automatic variable and can cause ambiguity and fragile diagnostics.

## Native Command Guardrails

All native commands such as `git`, `gh`, `python` and `pwsh` must go through a wrapper equivalent to `Invoke-NativeCommand`.

The wrapper must fail closed before execution when `FileName`, `Label`, `ArgList`, any `ArgList` entry, or `AllowedExitCodes` is empty or null.

Use `System.Diagnostics.ProcessStartInfo.ArgumentList` for argument passing. Do not concatenate shell command strings.

Classify results from explicit exit codes:

- success means `ExitCode` is listed in `AllowedExitCodes`;
- stderr is logged as evidence and classified with context;
- non-empty stderr is not automatically a failure;
- completion language such as `COMPLETATO` is allowed only after every native command and verification gate has passed.

The canonical success status for guarded command packs is:

```text
COMPLETED_AFTER_ALL_NATIVE_GUARDRAILS
```

## Appunti Rule

Non scrivere automaticamente negli appunti. Il compatto deve restare
recuperabile dai file Bridge e dagli artifact progressivi.

## Robust Git Parser

Use:

```powershell
git status --porcelain=v1 --untracked-files=all
```

Reason:

- untracked directories are expanded to individual files;
- scope guards can validate exact new files;
- `git add -- @AllowedPaths` becomes safer;
- path slicing bugs are avoided.

Avoid known bugs:

- losing the first character of `AGENTS.md` and reading it as `GENTS.md`;
- treating untracked `templates/pwsh_command_pack/` as an out-of-scope directory instead of checking files inside it;
- using fragile `Substring(3)` without first requiring porcelain v1 format.

## Forbidden Patterns

Do not put these in the pasted bootstrap:

- complex Git logic;
- test suites;
- long functions;
- DOCX XML;
- nested here-strings;
- fragile `try/finally`;
- separable outer `else` blocks;
- direct publication to `main`;
- `git push origin main` as the default;
- function parameters named `$Args`.

Do not expose secrets:

- do not print keys;
- do not save keys;
- do not hash keys;
- do not truncate keys;
- do not print prefixes or suffixes;
- do not record key length;
- do not serialize secrets into output, artifacts, logs, DOCX, Markdown, JSON, or appunti.

## Output Contract

Use four-digit step numbers and two-digit intra-step iterations:

```text
0540-01
0545-01
0550-01
0550-02
```

Generate progressive artifacts only:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

Do not generate `LAST-*` files in generic command packs. Do not read `LAST-*`
files as input. To find the latest artifact of one type for one step, use
`max(II)` for `(step, type)`.
Exception: the ASF publish runner may maintain `LAST-*` compatibility files for
operator handoff, with retry/fallback and explicit warning when a primary LAST
path is locked.
The Bridge is operational storage; Git and versioned files are authoritative.

DOCX is best-effort. Produce full TXT and compact Markdown first. If DOCX fails, write a non-blocking warning and a `.docx.failed.txt` or placeholder where useful.

## Publication

Publishing to `main` is PR-first by default:

1. commit on the step branch;
2. push the step branch;
3. run `gh pr create`;
4. run `gh pr merge`;
5. run `git checkout main`;
6. run `git pull --ff-only origin main`;
7. run final verification.

Do not default to `git push origin main`.

If local `main` is ahead of `origin/main`:

```text
main...origin/main [ahead N]
```

Do not push `main` directly. Create a publish branch from local `main`, push that branch, open a PR, merge the PR, realign local `main`, then verify.

## ASF Publish Runner Flow

For ASF step publication command packs, default to the proven runner flow from
STEP 0790, STEP 0800, STEP 0810, and STEP 0820:

1. run `scripts/asf_publish_step.ps1 -Phase PrepareConfig` for scope discovery, or use an equivalent reviewed config draft;
2. perform human review of `expected_files` and `changed_files`;
3. call `scripts/asf_publish_step.ps1` with the reviewed config JSON and `-Config`;
4. run Phase B with `-ApprovePublish`;
5. recover the PR number with `gh pr list --head $BranchName --json number --jq ".[0].number"`;
6. stop if `$PrNumber` is empty;
7. stop if `$PrNumber` is not numeric;
8. run Phase C with `-PrNumber $PrNumber -ApproveMerge`;
9. run final checks;
10. keep the runner Bridge output numbered and `LAST-*` compatibility files;
11. read or share `LAST-Output_Compatto.md` from the Bridge file when needed.
12. let `scripts/asf_publish_step.ps1` own its standard Bridge outputs;
13. do not open `Start-Transcript` on the runner `Output_Completo` path; use `NNNN-Wrapper_Log_*.txt` for any external wrapper log;
14. treat Bridge/LAST primary-path locks as retry, timestamped fallback, then `COMPLETATO CON WARNING NON BLOCCANTE` only after required gates passed.
15. after a successful human-gated publish, include or point to a post-publish evidence pack with PR, merge commit, checks, Bridge outputs, LAST files, accepted warnings and next step; do not turn the pack into commit/push/merge automation.

Use this flow only when Alberto has explicitly authorized publication of an ASF
step after local review/intake. Do not use it for clean Codex prompts,
verification-only work, external target repositories, or generic scripts that do
not publish through `scripts/asf_publish_step.ps1`.

The config JSON must include at least:

```text
step
name
repo_path
bridge_root
branch
commit_message
pr_title
pr_body
next_step
expected_files
changed_files
verification_profile
risk_level
verification_phase
profile_selector_expected_profile
intent
provided_gates
phase_a_checks
phase_c_checks
allow_no_github_checks_reported
log_max_count
```

`expected_files` and `changed_files` are explicit scope declarations.
`PrepareConfig` and scope discovery can propose them, but do not approve publication.
If the runner reports out-of-scope changes, stop, read the recovery
report or suggested config, and add files to scope only after human review. Do
not recover scope by parsing Git output when the expected scope is already
known. Do not infer scope by parsing git status --short.

Phase B publishes branch/PR after local gates. Phase C merges and runs final
verification after a valid PR number is available. Do not run Phase C without a
non-empty numeric PR number.

Bridge output policy for the ASF publish runner:

- mandatory gates remain fail-closed: failed Git, PR, tests, verify gate or diff-check means `BLOCCATO`;
- compact Markdown is mandatory and must be written to the primary path or a timestamped fallback;
- DOCX/Word COM is best-effort and a DOCX failure is a non-blocking warning;
- `LAST-*` compatibility files are updated with retry/fallback by the runner only;
- single writer ownership: external wrappers must not write or transcript to the same runner `Output_Completo` file.
- the final report should include or point to a post-publish evidence pack with PR, merge commit, checks, Bridge outputs, LAST files, accepted warnings and next step.

For short ASF publish packs, use a simple `Run` helper: reject empty command
names and arguments, execute the native command, read `$LASTEXITCODE`
immediately, and `throw` on non-zero exit code.

Avoid these ASF publish anti-patterns:

- mega-wrapper PowerShell that tries to infer everything;
- fragile parsing of `git status --short` to determine publish scope;
- using Git `2>&1` output as a file list, because LF/CRLF warnings can pollute it;
- treating LF/CRLF warnings as out-of-scope files when tests, workflow health,
  verify gate, and `git --no-pager diff --check` pass;
- `Get-Command -Path` introspection on `.ps1` scripts;
- AST parsing to infer runner parameters, except for exceptional diagnostics;
- casual scope expansion;
- printing `COMPLETATO` before final gates pass;
- using `Start-Transcript` on the same `Output_Completo` file owned by the runner;
- automatic appunti writes;
- blocking publication only because Word COM or DOCX generation failed;
- making a verified publish look failed only because a DOCX/accessory output
  failed after the final gates;
- treating a Bridge/LAST primary-path lock as a failed gate after gates already passed.

## LF/CRLF

LF/CRLF warnings on Windows are non-blocking only when all of these pass:

- `git --no-pager diff --check`;
- tests;
- workflow health check;
- verify gate.

## Provenance

STEP 536 introduced the Safe Bootstrap hardening. STEP 540 validated it in a real ASF publication flow with safe bootstrap plus branch/PR. STEP 545 finalized this reusable draft for future export. STEP 0550 deprecated `LAST-*` artifacts.
