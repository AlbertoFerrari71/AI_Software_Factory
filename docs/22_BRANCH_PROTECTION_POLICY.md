# Branch Protection Policy

## 1. Purpose

The Branch Protection Policy defines how `main` should be protected from accidental or unsafe changes.

The policy is designed to prevent:

- accidental direct pushes;
- merges without green CI;
- force push;
- deletion of the branch;
- pull requests outside the project workflow;
- unverified changes entering `main`.

`main` is the stable integration branch. It should receive changes through reviewed, verified pull requests, not direct edits.

---

## 2. Scope

This policy applies to:

- the `main` branch;
- pull requests targeting `main`;
- checks required before merge;
- the relationship between branch protection, Verification Gate, Documentation Sync, GitHub Workflow, and Codex Workflow.

STEP 090 documents the policy only. It does not apply branch protection, rulesets, or any real GitHub repository configuration.

STEP 100 introduces local scripts and the implementation runbook in `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`. Real application remains manual and controlled.

---

## 3. Protection mechanisms

GitHub offers two practical mechanisms for protecting `main`.

### Branch protection rules

Branch protection rules are the classic branch-specific protection mechanism.

They are simple and familiar. They can require pull requests, status checks, review, and restrictions on force pushes or branch deletion for a branch pattern such as `main`.

### Rulesets

Rulesets are a newer and more flexible mechanism.

They can express multiple overlapping rules, support clearer enforcement states, and make repository rules easier to inspect as the project grows.

### Recommendation

For AI Software Factory:

- document both mechanisms;
- prefer rulesets as the future evolution;
- keep classic branch protection as the simplest understandable fallback;
- do not configure either mechanism in STEP 090.

---

## 4. Minimum viable protection for main

Level 1 - Minimum viable protection is recommended for STEP 100.

Required settings:

- require pull request before merging;
- require status checks to pass before merging;
- require the CI check to pass;
- block force pushes;
- block branch deletion;
- keep admin bypass possible only for recovery or emergency;
- do not require review yet if Alberto works alone.

This is the minimum protection level that makes `main` harder to damage without making solo work unnecessarily slow.

---

## 5. Future protection levels

### Level 2 - Review protection

- Level 1;
- require at least 1 approving review;
- require conversation resolution before merge.

### Level 3 - History and identity hardening

- Level 2;
- require linear history;
- optionally require signed commits;
- stricter admin bypass rules.

### Level 4 - Advanced governance

- merge queue;
- deployment gates;
- security or code scanning required checks;
- stricter rulesets for protected paths.

These levels are future hardening options, not STEP 090 configuration.

---

## 6. Required checks naming rule

Required status checks depend on stable GitHub Actions check names.

If the workflow name, job name, or required check name changes, GitHub branch protection or rulesets may stop matching the intended check and require manual update.

Do not rename CI jobs casually after protection is enabled.

STEP 090 does not modify CI.

---

## 7. Merge policy

Merge to `main` should happen only after:

- dedicated branch;
- local Verification Gate completed;
- Documentation Sync evaluated;
- pull request created;
- CI green;
- no files outside scope;
- no secret or sensitive file;
- warnings reviewed;
- merge executed through a pull request.

Direct merge or local history manipulation is not part of the standard workflow.

---

## 8. Direct push policy

Direct pushes to `main` should be avoided.

Normal changes must reach `main` only through pull requests.

Exceptions are allowed only for documented recovery or emergency cases. Admin bypass must not become routine.

---

## 9. Force push and deletion policy

Force push to `main` is forbidden.

Deletion of `main` is forbidden.

These protections are always recommended, including at Level 1.

---

## 10. Emergency bypass

Emergency bypass may be considered only for:

- repository recovery;
- fixing broken repository configuration;
- CI blocked in a way that cannot be recovered through a pull request;
- operational incident response.

Every bypass must be documented in `docs/11_DECISIONS.md` or `CHANGELOG.md` when relevant.

---

## 11. Implementation guidance for STEP 100

STEP 100 prepares implementation of this policy by:

- choosing between ruleset and classic branch protection;
- verifying GitHub permissions;
- identifying the exact CI check name;
- preparing scripts under `scripts/github/`;
- keeping apply behavior in DryRun unless `-Apply` is explicitly passed;
- documenting how to verify that `main` is actually protected.

STEP 100 still does not apply protection automatically. The concrete operator sequence is in `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md`.

---

## 12. Checklist

Policy checklist:

- [ ] `main` protected by required pull request.
- [ ] CI required before merge.
- [ ] Force push blocked.
- [ ] Branch deletion blocked.
- [ ] Admin bypass limited to emergencies.
- [ ] Required checks use stable names.
- [ ] Policy documented.
- [ ] Application verified.

In STEP 090 this checklist is policy, not real GitHub configuration.
