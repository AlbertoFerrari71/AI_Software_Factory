# Soft Protection Guardrails

## 1. Purpose

This document defines local guardrails that reduce the risk of accidental work on `main` while real GitHub branch protection is not available on the current private repository and GitHub plan.

STEP 110 confirmed that the real required CI check is `Verification Gate`, but GitHub returned HTTP 403 for branch protection unless the repository is public or the account is upgraded.

Soft guardrails keep the local-first workflow safer without changing GitHub settings.

---

## 2. Hard protection vs soft protection

Hard protection is enforced by GitHub through branch protection or rulesets. It can block direct pushes, require pull requests, require status checks, block force pushes, and block branch deletion.

Soft protection is enforced by local rules, Git hooks, scripts, and operating discipline. It helps prevent mistakes on Alberto's machine, but it does not replace GitHub branch protection.

When GitHub Pro/Team or repository visibility makes hard protection available, real branch protection should be preferred.

---

## 3. Guardrails introduced

STEP 120 introduces:

- `.githooks/pre-commit`;
- `.githooks/pre-push`;
- `scripts/git/install_soft_guardrails.ps1`;
- `scripts/git/check_soft_guardrails.ps1`.

The hooks are opt-in. Codex creates and tests them, but does not install them automatically.

Future Codex Task Packets must repeat this constraint when soft guardrails are relevant: Codex does not install hooks, does not run `git config core.hooksPath`, and does not use `ASF_ALLOW_MAIN_BYPASS` during ordinary tasks.

---

## 4. Pre-commit guard

`.githooks/pre-commit` blocks commits made directly on `main`.

If `ASF_ALLOW_MAIN_BYPASS=1` is set, the hook allows the commit and prints a strong warning.

The bypass is only for recovery or emergency work. If the bypass matters to project history, document it in `docs/11_DECISIONS.md` or `CHANGELOG.md`.

---

## 5. Pre-push guard

`.githooks/pre-push` blocks direct pushes to `refs/heads/main`.

The normal workflow remains:

```text
branch -> PR -> CI "Verification Gate" -> review -> merge
```

If `ASF_ALLOW_MAIN_BYPASS=1` is set, the hook allows the push and prints a strong warning.

The bypass is only for recovery or emergency work.

---

## 6. Install guardrails

Run DryRun first:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\install_soft_guardrails.ps1 -DryRun
```

Install only after reviewing the output:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\install_soft_guardrails.ps1
```

Installation sets local Git configuration:

```text
core.hooksPath = .githooks
```

Codex must not run the install command without an explicit task and approval.

---

## 7. Check guardrails

Check local installation with:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

Exit codes:

- `0`: installed and coherent;
- `2`: hook files are present and installable, but `core.hooksPath` is not configured;
- `1`: real error, missing files, or invalid hook content.

The check script is read-only. It does not change Git configuration.

---

## 8. Emergency bypass

Use bypass only for recovery or emergency work.

The bypass must not appear in normal task execution. If a future task appears to require `ASF_ALLOW_MAIN_BYPASS`, Codex must stop and ask for an explicit emergency/recovery decision.

PowerShell example:

```powershell
$env:ASF_ALLOW_MAIN_BYPASS = "1"
git commit -m "emergency fix"
Remove-Item Env:\ASF_ALLOW_MAIN_BYPASS
```

For a push emergency, use the same variable only for the command that needs the bypass, then remove it immediately.

Every meaningful bypass should be documented.

---

## 9. Limitations

Soft guardrails have limits:

- they protect only local repositories where hooks are installed;
- they can be disabled by changing local Git configuration;
- they do not protect other computers;
- they do not block changes made from GitHub UI;
- they do not replace hard protection enforced by GitHub.

Soft protection is an interim operating control, not the final governance model.

---

## 10. Future hardening

Future steps can add:

- guided onboarding installation;
- optional guardrail checks in the Verification Gate;
- local preflight script;
- GitHub Pro/Team branch protection;
- GitHub rulesets.
