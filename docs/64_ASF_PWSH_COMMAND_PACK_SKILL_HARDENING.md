# 64 - ASF PowerShell Command Pack Skill Hardening

## 1. Scope

STEP 490 hardens the existing personal skill:

```text
%USERPROFILE%\.agents\skills\as-common-pwsh-command-pack
```

The skill is not renamed and no second skill is introduced.

This repository document records the ASF-facing behavior, verification checks and safety boundaries for the updated skill. The skill files themselves live outside this repository.

STEP 545 finalizes the repository-local canonical package and exportable skill draft in:

```text
docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md
templates/pwsh_command_pack/README.md
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
```

STEP 536 introduced the Safe Bootstrap structure. STEP 540 validated it in a real safe-bootstrap plus branch/PR publication flow.

---

## 2. Updated Skill Files

The expected skill layout is:

```text
as-common-pwsh-command-pack/
  SKILL.md
  references/
    pwsh-command-pack-standard.md
    pwsh-command-pack-template.ps1
  examples/
    demo-prompts.md
```

`SKILL.md` stays compact and uses YAML frontmatter with:

```yaml
name: "as-common-pwsh-command-pack"
description: "Generate safe logged PowerShell command packs for Alberto with robust .ps1 scripts, progressive NNNN-II artifacts, compact Markdown/DOCX reports, clipboard copy, and Git/Codex/ASF guardrails."
```

Long rules, technical sources and the robust template are kept in `references/`. Progressive examples are kept in `examples/`.

---

## 3. Command Pack Contract

STEP 536 upgrades the command pack contract to a Safe Bootstrap PowerShell Command Pack.

Default:

1. ChatGPT generates a short PowerShell bootstrap.
2. The bootstrap writes a complete `.ps1` script under `pwsh_command`.
3. The bootstrap validates parsing with `[scriptblock]::Create($ScriptText) | Out-Null`.
4. Only if parsing passes, the bootstrap executes the generated file with:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File <script.ps1>
```

5. Complex logic lives in the generated `.ps1`, not in the pasted bootstrap.
6. The outer bootstrap must not contain complex Git logic.
7. The outer bootstrap must not contain nested here-strings.
8. The outer bootstrap must not contain a fragile outer `try/finally`.
9. The outer bootstrap must end with a line that is actually executable, such as `Write-Host ";"`.

The pasted bootstrap may only:

- define base variables;
- create the Bridge output directory;
- create request text and generated script text;
- write the generated `.ps1`;
- validate parsing with `[scriptblock]::Create(...)`;
- write only progressive `NNNN-II-Tipo_Nome.ext` artifacts;
- execute the generated `.ps1`;
- print the exit code;
- terminate with `Write-Host ";"`.

The pasted bootstrap must not contain:

- merge logic;
- test suites;
- DOCX XML;
- long functions;
- extended Git blocks;
- nested here-strings;
- outer `else` branches;
- fragile outer `finally` blocks.

The generated `.ps1` script is the only place for:

- logging functions;
- native command invocation wrappers;
- Git validation;
- tests, health check and verify gate;
- PR creation and PR merge commands when explicitly requested;
- full and compact output generation;
- non-blocking DOCX generation.

The generated `.ps1` is launched with:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File <script.ps1>
```

The robust template includes:

- `#Requires -Version 7.0`;
- `Set-StrictMode -Version Latest`;
- `$ErrorActionPreference = 'Stop'`;
- guarded `try/catch` without fragile outer `finally`;
- a native command wrapper that captures stdout, stderr and exit code;
- explicit allowed exit codes when a non-zero exit can be a controlled warning;
- UTF-8 without BOM writes;
- compact Markdown output built from arrays of lines or a string builder;
- DOCX output as a non-blocking best-effort step;
- `Set-Clipboard` for the compact Markdown artifact.

The ASF output root is:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command
```

Each command pack must generate only progressive artifacts for request, executed script, full output, compact Markdown and compact DOCX:

```text
NNNN-II-Richiesta_Generazione_<name>.txt
NNNN-II-Comando_Eseguito_<name>.ps1
NNNN-II-Output_Completo_<name>.txt
NNNN-II-Output_Compatto_<name>.md
NNNN-II-Output_Compatto_<name>.docx
```

Do not generate `LAST-*` artifacts. Do not read `LAST-*` artifacts as input. To find the latest artifact of one type for one step, use `max(II)` for `(step, type)`. The Bridge is operational, not authoritative.

If DOCX generation fails, the command pack must not fail only for that reason when the TXT and Markdown artifacts were produced correctly. It must write a clear warning in the compact Markdown and may create:

```text
NNNN-II-Output_Compatto_<name>.docx.failed.txt
```

The ASF-facing templates for STEP 536 are:

```text
templates/pwsh_command_pack/safe_bootstrap_template.ps1
templates/pwsh_command_pack/safe_command_pack_script_template.ps1
templates/pwsh_command_pack/README.md
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
```

After STEP 545, the canonical template requirements also include `ArgList` for native wrapper parameters and `git status --porcelain=v1 --untracked-files=all` for scope-sensitive Git parsing.

---

## 3.1 Forbidden Nested Here-Strings

Generated command packs must not nest PowerShell here-strings.

Forbidden pattern:

```text
outer command text here-string contains inner XML or Markdown here-string
```

Use one of these safer alternatives instead:

- array of lines plus `-join [Environment]::NewLine`;
- separate template files;
- `System.Text.StringBuilder`;
- explicit escaping;
- `[char]96` for Markdown backticks when needed.

This rule exists because nested here-strings can close the outer command text early and cause inner script code to run directly in the terminal.

---

## 3.2 Parse Check and Fail-Closed Bootstrap

Before executing the generated `.ps1`, the bootstrap must run:

```powershell
[scriptblock]::Create($ScriptText) | Out-Null
```

If parsing fails:

- do not execute the generated script;
- do not run Git commands;
- generate full and compact blocked-output artifacts;
- copy the compact blocked output to the clipboard;
- print a clear parse failure message and exit non-zero.

This prevents partial execution, missing functions such as `Invoke-Native` or `Test-BranchExists`, stray `else` blocks and isolated brace parser errors from becoming publication actions.

---

## 3.3 Robust Output and DOCX Rules

The full output artifact must be produced first.

The compact Markdown artifact must then be built from an array of lines or a string builder. It must not depend on fragile inline Markdown fences in a long pasted block. Use `[char]96` for backticks when needed.

The compact Markdown must never be empty. If normal generation fails, create a minimal fallback with:

- command pack name;
- status;
- branch;
- final exit code;
- path to full output;
- warning explaining the fallback.

DOCX generation happens after TXT and Markdown. It is best-effort and non-blocking:

- wrap it in `try/catch`;
- record a warning on failure;
- create `.docx.failed.txt` when useful;
- do not fail publication only because DOCX failed if TXT/MD are valid.

---

## 3.4 PR-First Publishing

Publication toward `main` must be PR-first by default:

1. work on a step branch or publish branch;
2. push that branch;
3. create a PR with `gh pr create`;
4. wait for checks and review;
5. merge with `gh pr merge`;
6. realign local `main` with `origin/main`;
7. run final verification.

The default command pack must never use `git push origin main`.

Direct push to `main` is allowed only as an explicit, exceptional, manual bypass requested by Alberto. The bypass must be visible in the command pack title/body and must not be hidden inside a default publication flow.

If local status shows:

```text
main...origin/main [ahead N]
```

because local `main` contains verified merges not present on `origin/main`, the command pack must:

1. not push `main` directly;
2. create a publish branch from local `main`;
3. push the publish branch;
4. open a PR toward `main`;
5. merge the PR;
6. realign local `main` to `origin/main`;
7. verify with tests, health check, verify gate and `git --no-pager diff --check`.

---

## 3.5 Warning Classification

Use `git --no-pager` for long Git output.

LF/CRLF warnings on Windows are controlled warnings, not automatic failures, when all these pass:

- `git --no-pager diff --check`;
- tests;
- workflow health check;
- verify gate.

Real failures still stop the script.

## 3.6 Clean-first Boundary for Codex Prompts

STEP 535 clarifies the ChatGPT -> Codex boundary:

```text
Clean Codex prompt first by default.
PowerShell only when archiving, auditing, or publishing.
```

The default handoff to Codex is a clean, self-contained prompt that can be copied directly into Codex, without a PowerShell wrapper.

Use the Codex command pack PowerShell only when Alberto explicitly asks to save the prompt in the Bridge Dropbox / ChatGPT Bridge with progressive `NNNN-II-Tipo_Nome.ext` artifacts or a formal audit trail.

Use the pwsh/publication command pack after the Codex report, intake gate, local verification and human review, for controlled commit, push, PR/merge and final verification. Publication remains blocked when tests, health check, Verification Gate or guardrails fail.

Do not mix a Codex prompt, Bridge save script, Git commands, publication and final checks in the same block unless Alberto explicitly asks for that combined artifact.

---

## 4. Guardrails

The skill enforces these guardrails:

- split FASE A / FASE B / FASE C when commit, push, PR, merge, release, deploy or restart may appear;
- do not proceed to publication when tests, verify, health check or guardrails fail;
- use branch + PR as the default path to publish changes to `main`;
- forbid direct push to `main` unless Alberto requests an explicit emergency bypass;
- use `git --no-pager` for long Git output;
- avoid `setx PATH`;
- avoid nested here-strings in generated command packs;
- avoid fragile outer `try/finally` and outer `else` branches in the pasted bootstrap;
- avoid unrequested destructive commands;
- keep secrets out of generated files, logs, DOCX and clipboard output;
- treat `gh pr checks --watch` with no checks reported or exit code 1 as a controlled warning only when all other local gates pass;
- treat LF/CRLF warnings as non-blocking when `git --no-pager diff --check`, tests, health check and verify gate pass;
- recommend `.gitattributes` line-ending policy for mixed Windows/Git work.

The skill does not authorize commit, push, PR, merge, release or deploy. It only produces command packs and reports unless a later explicitly approved task asks for a separate human-gated publication phase.

---

## 5. Source Principles

The skill reference document integrates source principles from:

- Microsoft command-line and `CreateProcessW` limits;
- PowerShell encoding, transcript, error handling, automatic variables, preference variables, redirection, splatting and `Set-StrictMode` documentation;
- PSScriptAnalyzer overview and rule model;
- Git attributes and `git diff --check`;
- GitHub CLI `gh pr checks` and exit-code documentation;
- OpenAI Codex skill examples using `SKILL.md` frontmatter plus optional `references/`, `scripts/`, `examples/` or assets.

The sources are summarized in the skill reference file, not copied verbatim into `SKILL.md`, to keep the skill compact.

---

## 6. Verification

The required local checks for this step are:

```powershell
git --no-pager status --short
git --no-pager diff --check
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -LiteralPath 'templates/pwsh_command_pack/safe_bootstrap_template.ps1')) | Out-Null; 'safe bootstrap syntax ok'"
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -LiteralPath 'templates/pwsh_command_pack/safe_command_pack_script_template.ps1')) | Out-Null; 'safe command pack script syntax ok'"
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -LiteralPath 'templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1')) | Out-Null; 'step 540 template syntax ok'"
```

Do not modify external skill folders during repository verification. The export draft for future skill updates is `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md`.

If present, also run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

---

## 7. Out of Scope

This step does not:

- create a new skill name;
- modify Codex runtime configuration;
- install PowerShell modules;
- change PATH or PowerShell profiles;
- run publication phases;
- commit, push, open PRs, merge, release or deploy;
- modify external target repositories.
