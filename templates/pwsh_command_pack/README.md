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
- `Set-Clipboard` best-effort for content only;
- file-to-clipboard copies use `Get-Content -Path <file> -Raw | Set-Clipboard`;
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

## Clipboard

Non usare `Set-Clipboard -Path`: il cmdlet non supporta il parametro `-Path`.
Per copiare negli appunti il contenuto di un file usare:

```powershell
Get-Content -Path <file> -Raw | Set-Clipboard
```

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

## Output Contract

Use a four-digit step number and a two-digit intra-step iteration:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

Do not generate `LAST-*` files. To find the latest artifact of one type for one
step, use `max(II)` for `(step, type)`.

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
