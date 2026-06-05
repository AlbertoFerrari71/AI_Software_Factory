# 64 - ASF PowerShell Command Pack Skill Hardening

## 1. Scope

STEP 490 hardens the existing personal skill:

```text
%USERPROFILE%\.agents\skills\as-common-pwsh-command-pack
```

The skill is not renamed and no second skill is introduced.

This repository document records the ASF-facing behavior, verification checks and safety boundaries for the updated skill. The skill files themselves live outside this repository.

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
description: "Generate safe logged PowerShell command packs for Alberto with robust .ps1 scripts, numbered and LAST outputs, compact Markdown/DOCX reports, clipboard copy, and Git/Codex/ASF guardrails."
```

Long rules, technical sources and the robust template are kept in `references/`. Progressive examples are kept in `examples/`.

---

## 3. Command Pack Contract

The skill now requires generated `.ps1` scripts for long or conditional command packs, launched with:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File <script.ps1>
```

The robust template includes:

- `#Requires -Version 7.0`;
- `Set-StrictMode -Version Latest`;
- `$ErrorActionPreference = 'Stop'`;
- `try/catch/finally`;
- explicit `$LASTEXITCODE` handling for native commands;
- UTF-8 without BOM writes;
- compact Markdown output;
- DOCX output;
- `Set-Clipboard` for `LAST-Output_Compatto.md`.

The ASF output root is:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\pwsh_command
```

Each command pack must generate numbered artifacts and matching `LAST-*` artifacts for request, executed script, full output, compact Markdown and compact DOCX.

---

## 4. Guardrails

The skill enforces these guardrails:

- split FASE A / FASE B / FASE C when commit, push, PR, merge, release, deploy or restart may appear;
- do not proceed to publication when tests, verify, health check or guardrails fail;
- use `git --no-pager` for long Git output;
- avoid `setx PATH`;
- avoid unrequested destructive commands;
- keep secrets out of generated files, logs, DOCX and clipboard output;
- treat `gh pr checks --watch` with no checks reported or exit code 1 as a controlled warning only when all other local gates pass;
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
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -LiteralPath \"$env:USERPROFILE\.agents\skills\as-common-pwsh-command-pack\references\pwsh-command-pack-template.ps1\")) | Out-Null; 'syntax ok'"
```

If available, run:

```powershell
Invoke-ScriptAnalyzer -Path "$env:USERPROFILE\.agents\skills\as-common-pwsh-command-pack\references\pwsh-command-pack-template.ps1" -Severity Warning,Error
```

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
