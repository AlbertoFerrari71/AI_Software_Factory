# Documentation Sync

## 1. Purpose

Documentation Sync keeps code, tests, workflows, roadmap, changelog, and decision log aligned after every step.

The goal is practical consistency, not bureaucracy. A step is not really complete if tests pass but the documents still describe an older project state.

---

## 2. Core rule

Every completed step must leave the repository in a state where:

- tests pass;
- the working tree is understood and scoped;
- documentation reflects what was actually done;
- `CHANGELOG.md`, `docs/10_ROADMAP.md`, and `docs/11_DECISIONS.md` do not contradict the current project state.

If a document does not need changes, leave it unchanged and state that choice in the final report when relevant.

Task packets must explicitly declare which central documents and step-specific documents need evaluation. At minimum, every implementation step must say whether `CHANGELOG.md`, `docs/10_ROADMAP.md`, and `docs/11_DECISIONS.md` were updated or were not necessary.

---

## 3. Document update classes

### Always check

Review these files at every step:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- `docs/11_DECISIONS.md`;
- `docs/20_VERIFICATION_GATE.md` if the verification process changes;
- `docs/04_WORKFLOW.md` if the operating workflow changes.

Always check does not mean always edit. It means Codex and Alberto must decide whether the file is still coherent.

### Update when relevant

Update these only when the step actually touches their topic:

- `README.md`;
- `AGENTS.md`;
- `docs/08_CODEX_WORKFLOW.md`;
- `docs/15_GITHUB_WORKFLOW.md`;
- `docs/05_SECURITY_MODEL.md`;
- `policies/**`;
- `templates/**`.

Examples:

- update `docs/08_CODEX_WORKFLOW.md` when Codex responsibilities change;
- update `docs/15_GITHUB_WORKFLOW.md` when PR, merge, CI, or branch rules change;
- update `docs/22_BRANCH_PROTECTION_POLICY.md` when branch protection or ruleset policy changes;
- update `docs/23_BRANCH_PROTECTION_IMPLEMENTATION.md` when GitHub governance scripts or operator sequence change;
- update `docs/24_SOFT_PROTECTION_GUARDRAILS.md` when local Git hooks or soft guardrail scripts change;
- update `docs/25_PROMPT_PACKET_HARDENING.md` and `docs/26_PROMPT_PACKET_VALIDATION_LITE.md` when prompt packet rules, templates or validators change;
- update `docs/05_SECURITY_MODEL.md` or `policies/**` only when the Safety Model changes and the risk level is approved.

### Do not touch unless needed

Do not modify these for zeal or cosmetic consistency:

- `src/**`;
- existing policies;
- CI workflow;
- templates not involved in the step;
- historical documents that are already correct.

Unnecessary documentation churn makes review harder and increases the chance of contradictions.

---

## 4. Changelog rule

`CHANGELOG.md` records the user-facing and method-facing outcome of each step.

Rules:

- add one entry per completed step;
- describe what changed;
- keep detail at useful release-note level;
- include important exclusions when they matter;
- do not use the changelog as a debug diary.

Good changelog entries explain the result. They do not list every failed attempt or every intermediate edit.

---

## 5. Decision log rule

`docs/11_DECISIONS.md` records stable decisions, not every task action.

Add a decision only for:

- methodology choices;
- architecture choices;
- operating rules;
- safety rules;
- process rules that future steps should respect.

Do not add a decision for every file changed, every test added, or every wording improvement.

Decision entries must distinguish:

- context;
- decision;
- motivation;
- consequences.

---

## 6. Roadmap rule

`docs/10_ROADMAP.md` must describe the real step state.

Rules:

- mark a step completed only when the deliverables exist and verification passed;
- keep the next recommended step visible;
- do not mark future work as already done;
- record future hardening as future work, not as completed work.

For STEP 080, future hardening includes:

- lint/format gate;
- security scan gate;
- prompt packet hardening;
- branch protection policy.

---

## 7. Verification Gate integration

Documentation Sync is part of the Verification Gate.

The gate includes:

- automatic pytest checks for the existence and basic structure of the Documentation Sync rules;
- PR checklist confirmation that roadmap, changelog, and decision log were evaluated;
- manual review by Alberto before merge.

The central reference for this rule is `docs/21_DOCUMENTATION_SYNC.md`. The Verification Gate stays in `docs/20_VERIFICATION_GATE.md` and links here instead of duplicating the details.

---

## 8. Codex final report

Every Codex final report for an implementation step must include:

- step executed;
- status;
- files created;
- files modified;
- checks run;
- checks not run;
- risks or notes;
- next recommended step;
- final summary with step, time, status, and next step.

For Documentation Sync, Codex must also state whether `CHANGELOG.md`, `docs/10_ROADMAP.md`, and `docs/11_DECISIONS.md` were updated or checked and left unchanged.

---

## 9. Anti-duplication rule

Do not copy the same content into many documents.

Use central documents and references:

- `README.md` stays orienting and high level;
- workflow details belong in specific workflow documents;
- verification details belong in `docs/20_VERIFICATION_GATE.md`;
- documentation sync details belong in this document;
- changelog records outcomes, not full procedures.

When two documents need to mention the same rule, one should own the detail and the other should link to it.

---

## 10. Failure handling

If documentation is not aligned:

1. do not call the step complete;
2. list the documents that still need updates;
3. explain whether the mismatch is blocking or minor;
4. apply the smallest documentation fix in scope;
5. rerun the relevant tests;
6. do not proceed to merge if the mismatch is substantial.

If the documentation fix would require touching safety policy, CI, dependencies, secrets, or unrelated templates, reclassify the work before continuing.

---

## 11. Future hardening

Possible future improvements:

- dedicated docs check script;
- automatic roadmap/changelog consistency checks;
- branch protection;
- lint documentale;
- internal link checks;
- stronger prompt packet hardening.
