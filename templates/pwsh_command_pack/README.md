# PowerShell Command Pack Templates

This folder contains the ASF canonical Safe Bootstrap PowerShell Command Pack templates.

Use these files when Alberto asks for a PowerShell command pack for ChatGPT Bridge output, audit trail, controlled verification, or controlled publication.

Do not use a PowerShell wrapper as the default format for Codex prompts. STEP 535 keeps the default as a clean Codex prompt. PowerShell command packs are for Bridge/audit/publication flows only.

## Files

```text
safe_bootstrap_template.ps1
safe_command_pack_script_template.ps1
step_540_openai_controlled_live_execution_pack_template.ps1
as-common-pwsh-command-pack-SKILL.md
export/as-common-pwsh-command-pack/SKILL.md
../../scripts/install_pwsh_command_pack_skill.py
```

`as-common-pwsh-command-pack-SKILL.md` is a repository-local draft for future export to the shared `as-common-pwsh-command-pack` skill. Do not edit `%USERPROFILE%\.agents\skills` from this repository step.

`export/as-common-pwsh-command-pack/SKILL.md` is the installable form prepared by STEP 546. Use `scripts/install_pwsh_command_pack_skill.py` for dry-run/apply installation after manual intake; Codex does not install it directly into external skill folders during ASF implementation steps.

## Canonical Flow

Safe Bootstrap PowerShell Command Pack:

1. Generate a short pasted bootstrap.
2. The bootstrap writes a complete `.ps1` file under `pwsh_command`.
3. The bootstrap validates parsing with `[scriptblock]::Create($ScriptText) | Out-Null`.
4. Only if parse-check passes, execute `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`.
5. Complex logic lives only in the generated `.ps1`.
6. The pasted bootstrap stays short and robust.
7. The pasted bootstrap does not contain complex Git logic.
8. The pasted bootstrap does not contain nested here-strings.
9. The pasted bootstrap does not use fragile outer `try/finally`.
10. The final line must be executable, for example `Write-Host ";"`.
11. The pack generates only progressive `NNNN-II-Tipo_Nome.ext` artifacts.
12. The pack does not generate or read `LAST-*` artifacts.

## Required Patterns

Bootstrap:

- wrapper `& { ... }`;
- `$ErrorActionPreference = "Stop"`;
- `$PSNativeCommandUseErrorActionPreference = $false`;
- Bridge output directory creation;
- numbered request file;
- numbered command `.ps1` file;
- no `LAST-*` files;
- parse-check with `[scriptblock]::Create($ScriptText) | Out-Null`;
- execution with `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`;
- explicit `$LASTEXITCODE` read;
- clear final message;
- executable final line.

Generated `.ps1`:

- robust logging;
- full output;
- compact Markdown;
- DOCX best-effort/non-blocking;
- progressive `NNNN-II-Tipo_Nome.ext` files only;
- file-only handoff with no automatic appunti write;
- native command wrapper with exit-code control;
- `git --no-pager` for long Git output;
- robust Git parser with `git status --porcelain=v1 --untracked-files=all`;
- scope guard before `git add -- @AllowedPaths`;
- tests, health check and verify gate before publication;
- PR-first publication by default.

## Forbidden Patterns

Forbidden in the pasted bootstrap:

- complex Git logic;
- test suites;
- long functions;
- DOCX XML;
- nested here-strings;
- fragile `try/finally`;
- separable outer `else` blocks;
- direct publication to `main`;
- `git push origin main` as a default;
- function parameters named `$Args`.

Forbidden for secrets:

- printing keys;
- saving keys;
- hashing keys;
- truncating keys;
- printing prefixes or suffixes;
- recording secret length;
- serializing secrets into output or artifacts.

## Git Parser

Use:

```powershell
git status --porcelain=v1 --untracked-files=all
```

This shows individual untracked files, avoids treating an untracked directory such as `templates/pwsh_command_pack/` as a single out-of-scope item, and prevents path slicing bugs such as losing the first character of `AGENTS.md`.

Avoid fragile parsing based on non-porcelain output. Do not rely on blind `Substring(3)` without first requiring porcelain v1 format.

## ArgList

Do not use `$Args` as a function parameter name in wrappers. `$args` is a PowerShell automatic variable. Use `$ArgList` for native command arguments.

## Native Command Guardrails

All native commands such as `git`, `gh`, `python` and `pwsh` must go through a wrapper equivalent to `Invoke-NativeCommand`.

Required behavior:

- set `$PSNativeCommandUseErrorActionPreference = $false` and classify native command results from explicit exit codes;
- reject empty `FileName`, empty `Label`, null `ArgList`, empty `ArgList` entries and empty `AllowedExitCodes` before execution;
- use `System.Diagnostics.ProcessStartInfo.ArgumentList` instead of shell-concatenated command strings;
- log stdout and stderr separately; non-empty stderr is evidence to classify, not an automatic failure by itself;
- treat success as `ExitCode` being explicitly listed in `AllowedExitCodes`;
- print completion language only after every native command and verification gate has passed.

Use this status only after all native guardrails and gates passed:

```text
COMPLETED_AFTER_ALL_NATIVE_GUARDRAILS
```

Do not print `COMPLETATO` or an equivalent final success marker before the final native command exit code has been checked.

## Appunti

I command pack non scrivono automaticamente negli appunti. Il compatto resta
recuperabile dai file Bridge e dagli artifact progressivi.

## Publication

Publishing to `main` is PR-first by default:

1. commit on the step branch;
2. push the step branch;
3. `gh pr create`;
4. `gh pr merge`;
5. `git checkout main`;
6. `git pull --ff-only origin main`;
7. final verification.

No default command pack should use `git push origin main`.

If local status shows `main...origin/main [ahead N]`, create a publish branch from local `main`, push that branch, open a PR, merge it, realign `main`, then verify.

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

Use this flow when Alberto has explicitly authorized publication of an ASF step
after local review/intake. Do not use it for clean Codex prompts, read-only
verification-only work, external target repositories, or generic scripts that do
not publish through `scripts/asf_publish_step.ps1`.

The config JSON must be explicit. Include at least:

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

`expected_files` and `changed_files` are operator-owned scope declarations.
`PrepareConfig` and scope discovery can propose them, but do not approve publication.
If the runner reports out-of-scope changes, stop, read the recovery
report or suggested config, and add files to scope only after human review. Do
not recover scope by parsing Git output when the expected scope is already
known. Do not infer scope by parsing git status --short.

Phase B is publication to branch/PR after local gates. Phase C is PR merge and
final verification after a valid PR number is available. Do not run Phase C
without a non-empty numeric PR number.

Bridge output policy for the ASF publish runner:

- mandatory gates remain fail-closed: failed Git, PR, tests, verify gate or diff-check means `BLOCCATO`;
- compact Markdown is mandatory and must be written to the primary path or a timestamped fallback;
- DOCX/Word COM is best-effort and a DOCX failure is a non-blocking warning;
- `LAST-*` compatibility files are updated with retry/fallback by the runner only;
- single writer ownership: external wrappers must not write or transcript to the same runner `Output_Completo` file.
- the final report should include or point to a post-publish evidence pack with PR, merge commit, checks, Bridge outputs, LAST files, accepted warnings and next step.

For short ASF publish packs, a simple `Run` helper is enough: reject empty
command names and arguments, execute the native command, read `$LASTEXITCODE`
immediately, and `throw` on non-zero exit code. Avoid adaptive wrappers that try
to infer runner behavior.

### ASF Publish Anti-Patterns

Avoid these patterns for ASF publication commands:

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

## Output Contract

Use a four-digit step number and a two-digit intra-step iteration:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

Do not generate `LAST-*` files in generic command packs. To find the latest
artifact of one type for one step, use `max(II)` for `(step, type)`.
Exception: the ASF publish runner may maintain `LAST-*` compatibility files for
operator handoff, with retry/fallback and explicit warning when a primary LAST
path is locked.

DOCX is best-effort. TXT and Markdown are primary. If DOCX fails, write a non-blocking warning and optionally create `.docx.failed.txt`.

The Bridge is operational storage, not the authoritative source. Git and
versioned files are authoritative.

## LF/CRLF

Git LF/CRLF warnings on Windows are non-blocking when all of these pass:

- `git --no-pager diff --check`;
- tests;
- workflow health check;
- verify gate.

## Validation Source

STEP 536 introduced the hardening standard. STEP 540 validated it in a real branch/PR publication flow using safe bootstrap.

STEP 545 finalized the repository-local skill draft. STEP 546 added the installable export folder and dry-run/apply installer. STEP 0550 deprecated `LAST-*` artifacts.
