# 71 - ASF PowerShell Command Pack Skill Export Install

## 1. Scope

STEP 546 turns the STEP 545 draft into an installable repository-local export for the common skill:

```text
as-common-pwsh-command-pack
```

The installable ASF copy is:

```text
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
```

The installer is:

```text
scripts/install_pwsh_command_pack_skill.py
```

Codex non installa direttamente la skill in cartelle esterne alla repository ASF. This step prepares the export, installer, docs and tests only.

Out-of-repository targets remain manual follow-up operations after intake.

---

## 2. What the skill does

`as-common-pwsh-command-pack` generates safe logged PowerShell command packs for Alberto when a task requires Bridge/audit artifacts, controlled verification, or controlled publication.

The standard remains:

- short safe bootstrap;
- generated `.ps1` script;
- parse-check with `[scriptblock]::Create(...)`;
- complex logic only in the generated `.ps1`;
- native command parameter name `ArgList`, not `$Args`;
- `git status --porcelain=v1 --untracked-files=all`;
- PR-first publishing;
- numbered and `LAST` outputs;
- DOCX best-effort/non-blocking;
- no direct push to `main` by default.

---

## 3. Export layout

Canonical installable folder:

```text
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/
```

Canonical installable file:

```text
templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md
```

Naming rules:

- folder is exactly `as-common-pwsh-command-pack`;
- file is exactly `SKILL.md`;
- folder name is lowercase kebab-case;
- no underscores, spaces or accents in the folder name.

The older draft remains available as the source history:

```text
templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md
```

Future updates should edit the repository source and refresh the export copy in the same reviewed ASF step.

---

## 4. Installer dry-run

Dry-run is the default. It validates source, target and content, then prints the planned action without writing files.

Dry-run toward the user skill folder:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills
```

Dry-run toward an explicit skills root:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-dir "C:\path\to\skills-root"
```

If the explicit path is already named `as-common-pwsh-command-pack`, the installer treats it as the skill folder. Otherwise it appends `as-common-pwsh-command-pack`.

Dry-run must not create directories, write files, update backups or touch external repositories.

---

## 5. Installer apply

Apply requires an explicit `--apply` flag:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills --apply
```

Explicit target apply:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-dir "C:\path\to\skills-root" --apply
```

If the destination `SKILL.md` exists and differs, the installer blocks unless the operator also provides:

```powershell
--confirm-overwrite
```

Confirmed overwrite example:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills --apply --confirm-overwrite
```

On confirmed overwrite, the existing destination file is copied to a timestamped backup next to `SKILL.md` before the new file is written.

The installer never deletes folders.

---

## 6. Guardrails

The installer blocks or reports clearly when:

- the export source does not exist;
- the target path is missing or ambiguous;
- a target path contains wildcard, null or `..` traversal segments;
- the destination folder is not named `as-common-pwsh-command-pack`;
- an existing destination `SKILL.md` declares a different skill name;
- the installable file does not declare `name: as-common-pwsh-command-pack`;
- the installable file misses mandatory standard concepts;
- the destination exists and differs but `--confirm-overwrite` is missing in apply mode.

Dry-run mode never writes.

Apply mode writes only when `--apply` is present.

---

## 7. User skill installation

Manual operator path after intake:

```text
%USERPROFILE%\.agents\skills\as-common-pwsh-command-pack\SKILL.md
```

Recommended sequence:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills
python scripts/install_pwsh_command_pack_skill.py --target-user-skills --apply
```

If an older skill exists and differs:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills --apply --confirm-overwrite
```

Then start a new Codex session and verify that the skill list includes `as-common-pwsh-command-pack`.

---

## 8. Optional Codex_Skills flow

This ASF step does not modify `Codex_Skills`.

Future manual flow:

1. export skill from ASF;
2. dry-run install toward `%USERPROFILE%\.agents\skills`;
3. optionally copy the same `SKILL.md` into the separate `Codex_Skills` repository;
4. run the validator or tests inside `Codex_Skills`;
5. commit and push in `Codex_Skills` as a separate repository lifecycle.

Do not combine ASF step publication with cross-repo skill publication.

---

## 9. Verify installation

After a manual install, verify:

- target file exists;
- folder name is `as-common-pwsh-command-pack`;
- `SKILL.md` frontmatter declares `name: as-common-pwsh-command-pack`;
- content mentions Safe Bootstrap, generated `.ps1`, parse-check, `ArgList`, porcelain Git status, PR-first publishing, numbered and `LAST`, DOCX best-effort and no direct push to `main`;
- no real secrets or credentials were inserted.

Optional dry-run comparison after install:

```powershell
python scripts/install_pwsh_command_pack_skill.py --target-user-skills
```

Expected action is `noop` when destination already matches the ASF export.

---

## 10. Rollback

If a confirmed overwrite created a backup, rollback is manual:

1. inspect the timestamped `SKILL.md.bak.*` file;
2. copy it back to `SKILL.md` using a manual operator command;
3. restart the Codex session;
4. run dry-run again to understand whether ASF export and installed copy still differ.

The installer does not perform automatic rollback and does not delete backups.

---

## 11. Verification

Focused test:

```powershell
python -m pytest tests/unit/test_pwsh_command_pack_skill_export_install.py
```

Full checks:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
```

---

## 12. Out of Scope

This step does not:

- install the skill into `%USERPROFILE%\.agents\skills`;
- modify `C:\Users\alberto.ferrari\.agents\skills`;
- modify `Codex_Skills`;
- commit;
- push;
- open PRs;
- merge;
- deploy;
- touch stash entries.

---

## 13. Next Step

```text
550) OpenAI API Adapter First Authorized Live Run
```
