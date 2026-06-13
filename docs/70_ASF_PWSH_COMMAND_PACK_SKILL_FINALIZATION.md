# 70 - ASF PowerShell Command Pack Skill Finalization

## 1. Scope

STEP 545 finalizes the PowerShell Command Pack standard as a reusable ASF skill/operating instruction.

It does not modify external skill folders such as:

```text
%USERPROFILE%\.agents\skills
```

The repository-local export draft is:

```text
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
```

STEP 546 adds the installable export form:

```text
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
```

Installation and update flow are documented in:

```text
docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md
```

The canonical templates are:

```text
templates/pwsh_command_pack/README.md
templates/pwsh_command_pack/safe_bootstrap_template.ps1
templates/pwsh_command_pack/safe_command_pack_script_template.ps1
```

STEP 536 introduced the Safe Bootstrap hardening. STEP 540 validated the standard with a real safe-bootstrap plus branch/PR publication flow. STEP 545 makes the standard reusable and test-protected.

---

## 2. Canonical Standard

Safe Bootstrap PowerShell Command Pack:

1. Generate a short PowerShell bootstrap.
2. The bootstrap writes a complete `.ps1` file in `pwsh_command`.
3. The bootstrap validates parsing with `[scriptblock]::Create($ScriptText) | Out-Null`.
4. Only if the parse-check passes, execute `pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile`.
5. All complex logic lives in the generated `.ps1`.
6. The pasted terminal block stays short and robust.
7. The outer wrapper does not contain complex Git logic.
8. The outer wrapper does not contain nested here-strings.
9. The outer wrapper does not use fragile `try/finally`.
10. The pasted terminal block ends with `# terminatore copia-incolla` followed by one real blank final line.

The bootstrap is a writer/launcher. The generated `.ps1` is the operational script.

---

## 3. Required Bootstrap Pattern

The bootstrap must include:

- `& { ... }`;
- `$ErrorActionPreference = "Stop"`;
- `$PSNativeCommandUseErrorActionPreference = $false`;
- Bridge directory creation;
- request artifact generation with `NNNN-II-Richiesta_Generazione_<name>.txt`;
- command `.ps1` artifact generation with `NNNN-II-Comando_Eseguito_<name>.ps1`;
- no `LAST-*` artifact generation;
- parse-check:

```powershell
[scriptblock]::Create($ScriptText) | Out-Null
```

- execution:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File $CommandFile
```

- explicit `$LASTEXITCODE` handling;
- clear final message;
- executable final line.

The bootstrap must stay short. Do not put test suites, publication logic, DOCX XML or long helper functions in the pasted block.

---

## 4. Required Generated Script Pattern

The generated `.ps1` should contain, when pertinent:

- `#Requires -Version 7.0`;
- `Set-StrictMode -Version Latest`;
- `$ErrorActionPreference = "Stop"`;
- `$PSNativeCommandUseErrorActionPreference = $false`;
- robust logging;
- full output artifact;
- compact Markdown artifact;
- DOCX best-effort/non-blocking artifact;
- progressive `NNNN-II-Tipo_Nome.ext` artifacts only;
- file-only handoff for compact reports;
- native command wrapper with explicit allowed exit codes;
- `git --no-pager` for long Git output;
- robust Git parser;
- scope guard before staging;
- test command;
- workflow health check;
- verify gate;
- PR-first publication when publication is explicitly requested.

Native command wrappers must use `ArgList`, not `Args`:

```powershell
function Invoke-NativeCommand {
    param(
        [string] $FileName,
        [string[]] $ArgList = @()
    )
}
```

Do not use `$Args` as a parameter name. `$args` is a PowerShell automatic variable and can create ambiguity, fragile diagnostics and accidental behavior.

### Appunti Rule

Non scrivere automaticamente negli appunti; mantenere il compatto su file.

---

## 5. Robust Git Parser

Use this status command before scope-sensitive staging:

```powershell
git status --porcelain=v1 --untracked-files=all
```

Reason:

- untracked directories are expanded to individual files;
- scope guards can validate exact new files;
- `git add -- @AllowedPaths` is safer;
- parser behavior is stable and machine-readable.

Avoid observed bugs:

- `AGENTS.md` parsed as `GENTS.md` because the first character was lost;
- untracked `templates/pwsh_command_pack/` treated as an out-of-scope directory instead of checking files inside it;
- fragile `Substring(3)` against non-porcelain output;
- path slicing without verifying the expected porcelain format.

The canonical script template includes a parser that reads porcelain v1 lines and supports rename-style paths.

---

## 6. Forbidden Patterns

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
- recording key length;
- serializing secrets in output, artifacts, logs, DOCX, Markdown, JSON or appunti.

---

## 7. PR-First Publication

Publication toward `main` is PR-first by default:

1. commit on the step branch;
2. push the step branch;
3. `gh pr create`;
4. `gh pr merge`;
5. `git checkout main`;
6. `git pull --ff-only origin main`;
7. run final verification.

No default command pack may use `git push origin main`.

Special case:

```text
main...origin/main [ahead N]
```

If local `main` is ahead, do not push `main` directly. Create a publish branch from local `main`, push that branch, open a PR, merge it, realign local `main`, then verify.

---

## 8. Output Contract

Use a four-digit step number, for example:

```text
0540
0545
0550
```

Required progressive artifacts:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

`LAST-*` files are deprecated. The newest artifact is found by `max(II)` for `(step, type)`. The Bridge is operational, not authoritative; Git and versioned files preserve audit history.

---

## 9. DOCX Best-Effort

DOCX must never block commit or publication when TXT and Markdown were produced correctly.

Rules:

- generate full TXT first;
- generate compact Markdown second;
- generate DOCX only after TXT/MD exist;
- wrap DOCX generation in `try/catch`;
- write a non-blocking warning on failure;
- create `.docx.failed.txt` or a placeholder when useful.

---

## 10. LF/CRLF Handling

Git LF/CRLF warnings on Windows are non-blocking if all of these pass:

- `git --no-pager diff --check`;
- tests;
- workflow health check;
- verify gate.

Do not mark an otherwise verified command pack as failed only because Git warns that LF will be replaced by CRLF.

---

## 11. Quality Checklist

Before handing off a new command pack template or generated pack:

- bootstrap is short;
- bootstrap uses `& { ... }`;
- generated `.ps1` parses with `[scriptblock]::Create(...)`;
- generated script is launched with `pwsh -NoProfile -ExecutionPolicy Bypass -File`;
- native wrapper uses `ArgList`;
- no function parameter is named `$Args`;
- Git parser uses `git status --porcelain=v1 --untracked-files=all`;
- no direct `git push origin main` default exists;
- publication flow is PR-first;
- progressive `NNNN-II-Tipo_Nome.ext` artifacts are documented;
- `LAST-*` artifacts are not generated or read as input;
- DOCX is best-effort/non-blocking;
- LF/CRLF warning rule is documented;
- no secret values or secret derivatives are written.

---

## 12. Verification

Focused tests:

```powershell
python -m pytest tests/unit/test_pwsh_command_pack_safe_bootstrap_hardening.py tests/unit/test_pwsh_command_pack_skill_finalization.py
```

Parse-check templates:

```powershell
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw 'templates/pwsh_command_pack/safe_bootstrap_template.ps1')) | Out-Null"
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw 'templates/pwsh_command_pack/safe_command_pack_script_template.ps1')) | Out-Null"
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw 'templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1')) | Out-Null"
```

Full checks:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
```

---

## 13. Out of Scope

This step does not:

- edit external skill folders;
- install PowerShell modules;
- change PATH or PowerShell profiles;
- execute publication;
- commit;
- push;
- open PRs;
- merge;
- deploy.

---

## 14. Next Step

```text
560) OpenAI API Adapter First Authorized Live Run
```
