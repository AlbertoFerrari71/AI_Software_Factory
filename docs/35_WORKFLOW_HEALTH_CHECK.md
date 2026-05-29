# Workflow Health Check

## 1. Purpose

The Workflow Health Check is a local read-only check for the operational workflow of AI Software Factory.

It verifies that the core documents, scripts, templates and cross-references built around the Prompt Packet workflow are still present and navigable.

---

## 2. Why local and read-only

The check is local-first because the workflow is operated from the repository before commit, push, PR or merge.

It is read-only because its purpose is diagnosis. It does not modify files, Git configuration, hooks, GitHub, CI, PATH, PowerShell profiles, packages or remote state.

---

## 3. What it checks

The script `scripts/check_workflow_health.py` checks:

- required documents, scripts and templates are present;
- `docs/34_PROJECT_WORKFLOW_INDEX.md` links the core workflow areas;
- `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` still contains Quickstart, roles and validation references;
- `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` still contains the critical handoff sequence;
- operational scripts do not contain dangerous Git/GitHub command patterns.

The covered areas include:

- Prompt Packet Generator;
- Lite Mode;
- Strict Mode;
- Verification Gate;
- Documentation Sync;
- Soft Protection Guardrails;
- Release Smoke Workflow;
- Lifecycle Checklist;
- Developer Onboarding;
- Project Workflow Index.

---

## 4. What it does not check

The Workflow Health Check does not:

- run all semantic reviews;
- prove every Markdown link is valid;
- replace `python -m pytest`;
- replace the Verification Gate;
- replace Documentation Sync;
- replace the Release Smoke Workflow;
- inspect GitHub remote settings;
- install hooks;
- create commits, pushes, PRs, merges or releases.

---

## 5. Difference from Verification Gate

The Verification Gate checks repository readiness: tests, `git diff --check`, `git status --short` and the broader local gate in `scripts/verify.ps1`.

The Workflow Health Check is narrower. It checks that workflow documents, scripts and references still form a coherent operating map.

Use both when workflow documentation or scripts change.

---

## 6. Difference from Documentation Sync

Documentation Sync is the rule for keeping changelog, roadmap, decision log and relevant documents aligned with the actual step.

The Workflow Health Check does not decide whether a step has been documented correctly. It verifies that key workflow documents and references still exist and contain critical concepts.

---

## 7. Difference from Release Smoke Workflow

The Release Smoke Workflow checks that the Prompt Packet Generator can create a task packet and that the generated packet passes Lite Mode and Strict Mode.

The Workflow Health Check checks the surrounding operating system: index, onboarding, lifecycle checklist, Verification Gate references, Documentation Sync references and script safety.

---

## 8. Usage

Run from the repository root:

```powershell
python scripts/check_workflow_health.py
```

Expected positive output:

```text
Workflow Health Check

* files: PASS
* project workflow index: PASS
* developer onboarding: PASS
* lifecycle checklist: PASS
* script safety scan: PASS

Workflow Health Check PASSED
```

---

## 9. Positive result

A positive result means the core workflow map is present and contains the expected references.

It does not mean the current diff is ready to merge. Continue with:

```powershell
python -m pytest
git diff --check
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

---

## 10. Negative result

A negative result prints:

- failing area;
- file involved;
- missing requirement;
- short suggestion.

Fix the smallest relevant issue, then rerun the Workflow Health Check and the normal Verification Gate.

---

## 11. Current limits

Current limits:

- keyword-based checks;
- no full Markdown link validation;
- no JSON report;
- no CI integration;
- no remote GitHub inspection;
- no automatic repair.

These limits keep the check easy to review and safe to run.

---

## 12. Why it is not in CI yet

STEP 230 keeps the health check manual. This avoids expanding CI before the check has been used locally and reviewed across a few workflow changes.

A future step can decide whether to include it in CI or `scripts/verify.ps1`.

---

## 13. Relationship with Project Workflow Index

`docs/34_PROJECT_WORKFLOW_INDEX.md` is the central navigation document.

The Workflow Health Check protects that index by checking that it still references the main workflow areas and scripts. If the index changes substantially, update this health check only when the operational entry points change.
