# Branch Protection Implementation

## 1. Purpose

This document explains how to apply and verify protection for `main` according to the STEP 090 Branch Protection Policy.

The goal is to prepare local, reviewable scripts and an operator runbook. It does not apply GitHub protection by itself.

---

## 2. Implementation status

STEP 100 prepares:

- local PowerShell scripts;
- a dry-run-first apply flow;
- a read-only verification flow;
- tests that check the expected files and guardrails.

Codex does not apply real branch protection in this step.

Real application requires an explicit command from Alberto. Every script starts in a safe mode or read-only mode.

---

## 3. Minimum viable protection

Minimum viable protection for `main` is:

- pull request required before merge;
- required status check for CI;
- no force push;
- no branch deletion;
- admin enforcement configurable;
- no mandatory review yet.

This matches the Level 1 policy in `docs/22_BRANCH_PROTECTION_POLICY.md`.

---

## 4. Required CI check detection

The exact required CI check name must not be guessed.

It should be:

- detected from GitHub check runs or workflow runs; or
- passed explicitly with `-RequiredCheckName`.

If multiple candidate checks exist, Alberto must choose the correct one before applying branch protection.

---

## 5. Script overview

STEP 100 adds three scripts:

- `scripts/github/detect_required_checks.ps1` detects candidate check names without modifying GitHub;
- `scripts/github/apply_branch_protection.ps1` prepares or applies classic branch protection;
- `scripts/github/verify_branch_protection.ps1` reads current branch protection and reports gaps.

The implementation uses classic GitHub branch protection through `gh api`. GitHub rulesets remain documented as future hardening.

---

## 6. DryRun rule

`apply_branch_protection.ps1` does not modify GitHub unless `-Apply` is passed.

Without `-Apply`, the script prints:

- endpoint;
- target repository and branch;
- required check name;
- admin enforcement setting;
- JSON payload;
- exact follow-up command pattern.

With `-Apply`, the script uses `gh api` and requires an additional explicit confirmation.

---

## 7. Recommended operator sequence

1. Verify GitHub CLI authentication:

   ```powershell
   gh auth status
   ```

2. Detect candidate checks:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\github\detect_required_checks.ps1
   ```

3. Choose `RequiredCheckName`.

4. Run dry-run:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\github\apply_branch_protection.ps1 -RequiredCheckName "<check name>"
   ```

5. Review endpoint and payload.

6. Apply only after explicit approval:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\github\apply_branch_protection.ps1 -RequiredCheckName "<check name>" -Apply -ConfirmApply
   ```

7. Verify:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\github\verify_branch_protection.ps1 -RequiredCheckName "<check name>"
   ```

8. Open a test PR or verify behavior on the next real PR.

---

## 8. Failure handling

If `gh` is not installed:

- install GitHub CLI outside this step;
- do not bypass the scripts by copying tokens into commands.

If `gh` is not authenticated:

- run `gh auth status`;
- authenticate interactively using GitHub CLI;
- do not store or print tokens manually.

If the CI check is not found:

- inspect recent workflow runs;
- pass `-RequiredCheckName` explicitly only after verifying the correct check name.

If the API returns `403`:

- check whether GitHub reports that branch protection requires GitHub Pro/Team or public repository visibility;
- if the plan limitation is detected, treat `verify_branch_protection.ps1` exit code `2` as the documented fallback condition;
- use soft protection and do not run `apply_branch_protection.ps1 -Apply`;
- if the error is not a plan limitation, confirm repository permissions and admin rights before retrying.

If the API returns `422`:

- inspect the payload;
- verify required check name and branch name;
- rerun dry-run before applying again.

If protection is applied incorrectly:

- read the current configuration first;
- prefer GitHub UI or a reviewed corrective script;
- document the correction if it affects workflow or safety.

---

## 9. Recovery

Do not remove protections blindly.

Recovery sequence:

1. read current protection with `verify_branch_protection.ps1`;
2. identify the specific broken setting;
3. choose UI correction or reviewed script correction;
4. document emergency bypass or recovery in `docs/11_DECISIONS.md` or `CHANGELOG.md` when relevant.

---

## GitHub plan limitation detected

STEP 110-A detected the real CI required check name:

```text
Verification Gate
```

The read-only branch protection verification returned HTTP 403 with a GitHub message requiring an upgrade to GitHub Pro or making the repository public.

While the repository remains private and the current GitHub plan does not support protected branches, hard branch protection cannot be applied or verified for `main`.

In this state:

- do not run `apply_branch_protection.ps1 -Apply`;
- keep `apply_branch_protection.ps1` in DryRun only;
- use the soft protection policy documented in `docs/22_BRANCH_PROTECTION_POLICY.md`;
- continue using PR, CI, Verification Gate, Documentation Sync, and manual Alberto review as the operating gate.

`verify_branch_protection.ps1` exits with code `2` when it detects the known GitHub plan or repository visibility limitation.

After STEP 120, local soft guardrails are available in `.githooks/` and `scripts/git/`. They are opt-in and must be installed manually with `scripts/git/install_soft_guardrails.ps1` after review. The central runbook is `docs/24_SOFT_PROTECTION_GUARDRAILS.md`.

The required check remains:

```text
Verification Gate
```

---

## 10. Future hardening

Future hardening can add:

- GitHub rulesets;
- required review;
- conversation resolution;
- signed commits;
- linear history;
- merge queue;
- security scan required check.
