---
name: "as-common-pwsh-command-pack"
description: "Generate safe logged PowerShell command packs for Alberto with short safe bootstraps, generated .ps1 scripts, numbered and LAST outputs, compact Markdown/DOCX reports, clipboard copy, robust Git parsing, PR-first publication, and Git/Codex/ASF guardrails."
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

## Bootstrap Requirements

The bootstrap must include:

- wrapper `& { ... }`;
- `$ErrorActionPreference = "Stop"`;
- `$PSNativeCommandUseErrorActionPreference = $false`;
- Bridge directory creation;
- request file generation;
- command `.ps1` generation;
- `LAST-Richiesta_Generazione.txt`;
- `LAST-Comando_Eseguito.ps1`;
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
- `LAST` files always updated;
- `Set-Clipboard` best-effort;
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
- do not serialize secrets into output, artifacts, logs, DOCX, Markdown, JSON, or clipboard.

## Output Contract

Use four-digit step numbers:

```text
0540
0545
0550
```

Generate numbered and `LAST` artifacts:

```text
NNNN-Richiesta_Generazione_<name>.txt
NNNN-Comando_Eseguito_<name>.ps1
NNNN-Output_Completo_<name>.txt
NNNN-Output_Compatto_<name>.md
NNNN-Output_Compatto_<name>.docx
LAST-Richiesta_Generazione.txt
LAST-Comando_Eseguito.ps1
LAST-Output_Completo.txt
LAST-Output_Compatto.md
LAST-Output_Compatto.docx
```

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

## LF/CRLF

LF/CRLF warnings on Windows are non-blocking only when all of these pass:

- `git --no-pager diff --check`;
- tests;
- workflow health check;
- verify gate.

## Provenance

STEP 536 introduced the Safe Bootstrap hardening. STEP 540 validated it in a real ASF publication flow with safe bootstrap plus branch/PR. STEP 545 finalizes this reusable draft for future export.
