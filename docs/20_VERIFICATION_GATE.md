# Verification Gate

## 1. Purpose

The Verification Gate defines what "verified" means before a change enters `main`.

It is a small, repeatable gate between Codex local work, human review, pull request, CI, and merge. It does not replace review and does not approve risky actions automatically.

The gate checks that:

- tests pass;
- whitespace and patch formatting are clean;
- Git status is understood;
- key templates and policies are still present;
- the pull request documents verification;
- GitHub Actions confirms the same baseline checks.

Branch protection or rulesets can later make part of this gate mandatory on GitHub. STEP 090 documents the Branch Protection Policy in `docs/22_BRANCH_PROTECTION_POLICY.md`; STEP 100 may apply it.

STEP 110 confirms that the real CI check name is `Verification Gate`. If GitHub cannot enforce branch protection because the private repository or plan returns HTTP 403, this gate becomes the primary soft protection discipline until hard protection is available.

---

## 2. Local verification

Local verification is run before commit and before push.

Standard command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

The script runs:

```powershell
python --version
python -m pytest --version
python -m pytest
git diff --check
git status --short
```

The script does not commit, push, create branches, install packages, or modify files.

If `pwsh` is not available, run the commands manually:

```powershell
python -m pytest
git diff --check
git status --short
```

---

## 3. Git verification

Before commit Alberto checks:

- the branch is the intended branch for the step;
- `git status --short` contains only expected files;
- `git diff` is readable and scoped;
- `git diff --check` passes;
- no `.env`, secret, generated cache, dependency lock, or unrelated file is present.

`git status --short` may show modified or new files before commit. That is acceptable only when every path is expected by the task packet.

---

## 4. Policy and template verification

The automatic tests protect the lightweight contracts already present in the repository:

- `tests/unit/test_safety_policy.py` checks Safety Model policy invariants;
- `tests/unit/test_prompt_templates.py` checks prompt and task packet structure;
- `tests/unit/test_github_workflow.py` checks GitHub workflow templates;
- `tests/unit/test_codex_workflow.py` checks Codex workflow guardrails;
- `tests/unit/test_verification_gate.py` checks this Verification Gate.

These tests are intentionally simple. They verify presence, sections, and robust keywords instead of exact long text.

Manual verification remains required for meaning:

- the change matches the step objective;
- the scope is not broader than requested;
- the task respected allowed scope, forbidden scope, and forbidden actions;
- the final Codex report is complete enough for review;
- documentation and changelog are updated when behavior or workflow changes;
- rollback is clear.

Prompt Packet Hardening defines the expected task packet and final report structure in `docs/25_PROMPT_PACKET_HARDENING.md`.

Prompt Packet Validation Lite can be used as a pre-step support check for task packets:

```powershell
python scripts/validate_task_packet.py templates/codex_tasks/codex_task_packet_template.md
```

The reference document is `docs/26_PROMPT_PACKET_VALIDATION_LITE.md`. In STEP 140 this check is not yet a required CI check and is not part of `scripts/verify.ps1`; future steps can decide whether to integrate it into the gate.

STEP 150 adds golden samples in `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`. They help verify the behavior of the Lite validator, but they are not a separate required gate check yet.

STEP 160 adds optional Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict <task-packet.md>
```

Strict Mode can be used as a manual pre-check for important task packets. It is not yet required in CI and is not part of `scripts/verify.ps1`.

### Documentation Sync

The Verification Gate also includes Documentation Sync.

Before merge, Alberto and Codex must evaluate whether `CHANGELOG.md`, `docs/10_ROADMAP.md`, and `docs/11_DECISIONS.md` need updates. Not every document must be edited on every step, but the central documents must not contradict the actual project state.

The detailed rule lives in `docs/21_DOCUMENTATION_SYNC.md`. Any documentation sync pytest checks must pass with the rest of the gate.

---

## 5. Pull request verification

Before opening a PR, Alberto checks local verification output and the final diff.

The PR must declare:

- step or issue;
- safety level;
- files changed;
- tests run;
- checks not run, if any;
- risks;
- rollback;
- Verification Gate checklist.

GitHub Actions must pass before merge unless Alberto records an explicit exception.

Branch protection is the GitHub mechanism that can enforce required PRs and required status checks. The policy is documented in `docs/22_BRANCH_PROTECTION_POLICY.md`; no real protection is applied by STEP 090.

Before branch protection is applied, the local Verification Gate must pass. After application, the result should be checked with `scripts/github/verify_branch_protection.ps1`. The implementation runbook is `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`.

If `verify_branch_protection.ps1` exits with code `2`, GitHub branch protection is not available for the current repository or plan. In that case, no hard protection can be verified and the project must rely on PR, CI, manual Alberto review, and the soft protection policy.

STEP 120 adds an optional local soft guardrail check:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1
```

This check is local and read-only. It can return exit code `2` when hook files are present but `core.hooksPath` is not configured. That is a useful local warning, not a CI failure requirement, because Git hook installation is machine-local.

---

## 6. Merge verification

Merge is allowed only after:

- local verification passed on the branch;
- PR diff was reviewed;
- GitHub Actions passed;
- documentation and changelog are aligned;
- rollback is clear;
- Alberto approves the merge.

After merge, Alberto pulls `main` locally and runs the final baseline:

```powershell
git checkout main
git pull origin main
python -m pytest
git status --short
```

---

## 7. Failure handling

If a check fails:

1. stop;
2. keep the failing output visible;
3. identify the smallest likely cause;
4. apply the minimum fix in scope;
5. rerun the failed check and then the full gate;
6. do not commit, push, open PR, or merge until the gate is clean.

Do not bypass failed tests, hide failures, or remove tests to make the gate pass.

If the fix requires CI/CD, dependencies, auth, database schema, security policy, destructive actions, or secrets, reclassify the task using the Safety Model before continuing.

---

## 8. Standard output

Codex and human handoffs should report verification in this form:

```text
Verification Gate
- python -m pytest: passed / failed / not run
- git diff --check: passed / failed / not run
- git status --short: reviewed / not reviewed
- scripts/verify.ps1: passed / failed / not run
- GitHub Actions: passed / failed / pending / not applicable
- Manual checklist: complete / incomplete
- Residual risks: ...
```

If a check is not run, the reason must be explicit.

---

## 9. Manual checklist

- [ ] Branch dedicated to the step.
- [ ] Diff limited to expected files.
- [ ] No CI/CD change unless explicitly in scope.
- [ ] No dependency change unless explicitly in scope.
- [ ] No `src/**` change unless explicitly required.
- [ ] No `.env`, credential, or secret touched.
- [ ] `python -m pytest` passed.
- [ ] `git diff --check` passed.
- [ ] `git status --short` reviewed.
- [ ] Soft Protection Guardrails checked or explicitly marked not installed.
- [ ] Documentation Sync reviewed using `docs/21_DOCUMENTATION_SYNC.md`.
- [ ] Documentation and changelog updated if needed.
- [ ] Rollback path is clear.

---

## 10. Future hardening

Future steps can strengthen the gate with:

- branch protection or rulesets requiring PR review and status checks;
- linting;
- type checking;
- markdown checks;
- secret scanning;
- security scans;
- stricter path-policy checks.

Branch protection is recommended, but STEP 100 only prepares scripts and a runbook unless Alberto explicitly applies them. Future pull requests should respect the protection after it is enabled.

Until hard protection is available, future pull requests should treat the `Verification Gate` CI check as required by process even if GitHub cannot technically require it.
