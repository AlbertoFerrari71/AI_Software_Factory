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
- update `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md` when prompt packet golden samples are added or changed;
- update `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md` when Strict Mode behavior changes;
- update `docs/29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md` when the prompt packet generator CLI changes;
- update `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md` when local generator packaging, wrappers, or generated samples change;
- update `docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md` when local generator smoke workflow behavior changes;
- update `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md` when the prompt packet lifecycle, handoff checklist, or step completion sequence changes;
- update `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md` when generator onboarding, operator Quickstart, roles, or troubleshooting guidance changes;
- update `docs/34_PROJECT_WORKFLOW_INDEX.md` when workflow navigation, document map, script map, or operational entry points change;
- update `docs/35_WORKFLOW_HEALTH_CHECK.md` when the local workflow health check behavior, coverage, or interpretation changes;
- update `docs/36_WORKFLOW_QUICK_REFERENCE.md` when daily workflow commands, supervised handoff commands, or final `main` verification commands change;
- update `docs/37_STEP_CLOSURE_REPORT.md` when step closure states, final report fields, PR check interpretation, or post-merge evidence requirements change;
- update `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` when recurring workflow command recipes, troubleshooting cases, or command interpretation rules change;
- update `docs/39_WORKFLOW_STATUS_DASHBOARD.md` when local workflow status fields, displayed documents/scripts, or suggested local checks change;
- update `docs/40_RELEASE_READINESS.md` when pilot readiness levels, go/warning/no-go criteria, pilot scope rules, or readiness templates change;
- update `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md` when existing-project intake, pilot risk mapping, first pilot step rules, or pilot templates change;
- update `docs/42_ASF_NEXT_STEP_RUNNER.md` when runner prepare mode, generated outputs, validation behavior, or handoff rules change;
- update `docs/43_ASF_RUNNER_PROJECT_PROFILES.md` when project profiles, config format, override behavior, or profile safety rules change;
- update `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md` when generated handoff structure, FASE 1 / FASE 2 content, or Human gate wording changes;
- update `docs/45_ASF_RUNNER_VERIFICATION_PACK.md` when verification pack output, recommended checks, or manual gate references change;
- update `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md` when hardened verification stages, report checks, PR checks, or LF/CRLF handling change;
- update `docs/47_ASF_CODEX_REPORT_INTAKE.md` when Codex report intake inputs, outputs, section checks, or PASS/WARNING/FAIL behavior change;
- update `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md` when closure pack generation, manual command guidance, PR checks handling, or human gate rules change;
- update `docs/49_ASF_HUMAN_APPROVAL_GATE.md` when approval gate inputs, outputs, decision logic, evidence rules or Alberto responsibility change;
- update `docs/50_ASF_CODEX_INVOCATION_DESIGN.md` when Codex invocation levels, sandbox rules, input/output contract or stop conditions change;
- update `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md` when dry-run pack generation, preview PowerShell behavior, sandbox options or approval interpretation change;
- update `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md` when read-only invocation preview or execute-readonly behavior changes;
- update `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md` when stdout/stderr/exit code capture or PASS/WARNING/FAIL behavior changes;
- update `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md` when read-only safety gate criteria or decisions change;
- update `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` when the manual trial procedure, target choice, stop conditions or execute-readonly prerequisites change;
- update `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md` when first-trial evidence, classification, verification status or next recommended trial changes;
- update `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md` when clean target setup, execute-readonly conditions or tmp target rules change;
- update `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md` when clean target trial evidence, stdout/stderr/exit code, safety gate decision or next step changes;
- update `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md` when repeatable trial modes, classifications, tmp layout, approval rules or compare flow change;
- update `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md` when STEP 450 trial evidence, Codex availability, target cleanliness or next step changes;
- update `docs/61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md` when diagnostics classifications, JSON contract or Markdown summary behavior changes;
- update `docs/62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md` when CLI metadata probe behavior or support evidence changes;
- update `docs/63_ASF_CODEX_READONLY_DECISION_GATE.md` when allowed decisions or conservative decision rules change;
- update `config/asf_project_profiles.json` only when profile defaults need to change and no secrets are introduced;
- update `templates/codex_tasks/asf_runner_verification_pack_template.md` when the Verification Pack structure changes;
- update `templates/codex_tasks/asf_codex_report_intake_template.md` when intake report structure changes;
- update `templates/codex_tasks/asf_human_gated_closure_pack_template.md` when closure pack structure changes;
- update `templates/codex_tasks/asf_human_approval_gate_template.md` when approval gate report structure changes;
- update `templates/codex_tasks/asf_codex_invocation_dry_run_template.md` when dry-run invocation pack structure changes;
- update `templates/codex_tasks/asf_codex_readonly_invocation_template.md` when read-only invocation template structure changes;
- update `templates/codex_tasks/asf_codex_invocation_result_capture_template.md` when result capture template structure changes;
- update `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md` when read-only safety gate template structure changes;
- update `templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md` when repeatable trial report structure changes;
- update `templates/codex_tasks/asf_codex_readonly_trial_compare_template.md` when trial comparison structure changes;
- update `templates/codex_tasks/asf_codex_readonly_diagnostics_template.md` when diagnostics command or review fields change;
- update `templates/codex_tasks/asf_codex_cli_compatibility_probe_template.md` when CLI probe command or support evidence changes;
- update `templates/codex_tasks/asf_codex_readonly_decision_gate_template.md` when decision gate inputs, outputs or allowed decisions change;
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
