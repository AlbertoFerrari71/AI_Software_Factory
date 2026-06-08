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
- `docs/36_WORKFLOW_QUICK_REFERENCE.md` is present and linked from the Project Workflow Index;
- `docs/37_STEP_CLOSURE_REPORT.md` and `templates/codex_tasks/step_closure_report_template.md` are present and linked from the Project Workflow Index;
- `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` is present and linked from the Project Workflow Index;
- `docs/39_WORKFLOW_STATUS_DASHBOARD.md` and `scripts/show_workflow_status.py` are present and linked from the Project Workflow Index;
- `docs/40_RELEASE_READINESS.md` and `templates/codex_tasks/release_readiness_checklist.md` are present and linked from the Project Workflow Index;
- `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`, `templates/codex_tasks/existing_project_intake_template.md` and `templates/codex_tasks/first_pilot_step_packet_template.md` are present and linked from the Project Workflow Index;
- `docs/42_ASF_NEXT_STEP_RUNNER.md`, `scripts/asf_next_step.py` and `templates/codex_tasks/asf_next_step_runner_handoff_template.md` are present and linked from the Project Workflow Index;
- `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`, `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`, `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`, `config/asf_project_profiles.json` and `templates/codex_tasks/asf_runner_verification_pack_template.md` are present and linked from the Project Workflow Index;
- `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`, `docs/47_ASF_CODEX_REPORT_INTAKE.md`, `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`, `scripts/asf_codex_report_intake.py`, `scripts/asf_generate_closure_pack.py`, `templates/codex_tasks/asf_codex_report_intake_template.md` and `templates/codex_tasks/asf_human_gated_closure_pack_template.md` are present and linked from the Project Workflow Index;
- `docs/49_ASF_HUMAN_APPROVAL_GATE.md`, `docs/50_ASF_CODEX_INVOCATION_DESIGN.md`, `docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md`, `scripts/asf_human_approval_gate.py`, `scripts/asf_codex_invocation_dry_run.py`, `templates/codex_tasks/asf_human_approval_gate_template.md` and `templates/codex_tasks/asf_codex_invocation_dry_run_template.md` are present and linked from the Project Workflow Index;
- `docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md`, `docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md`, `docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md`, `scripts/asf_codex_readonly_invoke.py`, `scripts/asf_codex_result_capture.py`, `scripts/asf_codex_readonly_safety_gate.py`, `templates/codex_tasks/asf_codex_readonly_invocation_template.md`, `templates/codex_tasks/asf_codex_invocation_result_capture_template.md` and `templates/codex_tasks/asf_codex_readonly_safety_gate_template.md` are present and linked from the Project Workflow Index;
- `docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md` and `docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md` are present and linked from the Project Workflow Index;
- `docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md` and `docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md` are present and linked from the Project Workflow Index;
- `docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md`, `docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md`, `scripts/asf_codex_readonly_repeatable_trial.py`, `scripts/asf_codex_readonly_trial_compare.py`, `templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md` and `templates/codex_tasks/asf_codex_readonly_trial_compare_template.md` are present and linked from the Project Workflow Index;
- `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md` is present and linked from the Project Workflow Index;
- `docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md`, `templates/pwsh_command_pack/README.md` and `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md` are present and linked from the Project Workflow Index;
- `docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md`, `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md` and `scripts/install_pwsh_command_pack_skill.py` are present and linked from the Project Workflow Index;
- `docs/65_ASF_OPENAI_API_ADAPTER.md`, `scripts/asf_openai_api_adapter.py` and `templates/codex_tasks/asf_openai_api_adapter_template.md` are present and linked from the Project Workflow Index;
- `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md` and `templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md` are present and linked from the Project Workflow Index;
- `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`, `scripts/asf_openai_controlled_live_execution_pack.py` and `templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1` are present and linked from the Project Workflow Index;
- `docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md`, `scripts/asf_verification_profile_selector.py`, `tests/unit/test_asf_verification_profile_selector.py` and `examples/verification_profiles/` are present and linked from the Project Workflow Index;
- `docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md`, `tests/unit/test_asf_publish_step_runner.py` and `examples/publish_step/0640_publish_config_*.example.json` are present and linked from the Project Workflow Index;
- `docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md`, `scripts/asf_publish_config_generator.py`, `tests/unit/test_asf_publish_config_generator.py` and `examples/publish_config_generator/` are present and linked from the Project Workflow Index;
- `docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md` and `examples/publish_config_generator/sample_bridge_output_input.json` are present and linked from the Project Workflow Index;
- `docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md`, `scripts/asf_step_state_machine.py`, `tests/unit/test_asf_step_state_machine.py` and `examples/state_machine/` are present and linked from the Project Workflow Index;
- `docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md`, `LAST-State.json`, `LAST-Event.json` and `LAST-Output_Compatto.md` are referenced from the Project Workflow Index without requiring Dropbox real paths;
- `docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md`, `sample_state_machine_integration_input.json`, `sample_local_verified_state.json`, `LAST-Publish_Config.json`, `LAST-State.json` and `--update-state` are referenced from the Project Workflow Index without requiring Dropbox real paths;
- `docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md`, `scripts/asf_e2e_mvp_smoke.py`, `tests/unit/test_asf_e2e_mvp_smoke.py`, `tmp/e2e_mvp_smoke`, `negative_fail_closed.json` and `READY_TO_PUBLISH` are referenced without executing the smoke or requiring Dropbox real paths;
- `docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md`, `scripts/asf_motor_run_manifest.py`, `tests/unit/test_asf_motor_run_manifest.py`, `examples/motor_run_manifest/`, `motor_run_manifest.json`, `motor_run_summary.md` and `LAST-Run_Manifest.json` are referenced without executing publication phases or requiring Dropbox real paths;
- `docs/motor/0720_MVP_USAGE_RUNBOOK.md`, `codex_command`, `publish_config`, `state_machine`, `motor_run`, `Phase B`, `Phase C`, `-ApprovePublish`, `-ApproveMerge` and `READY_TO_PUBLISH` are referenced without executing publication phases or requiring Dropbox real paths;
- `docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md`, `MVP STATUS: GO WITH WARNINGS`, `GO/WARNING/NO-GO`, `0740) MVP Real Step Pilot` and the Project Workflow Index closure pointer are referenced without changing publication behavior;
- `docs/motor/0740_MVP_REAL_STEP_PILOT.md`, `PILOT STATUS: GO WITH WARNINGS`, `tmp/0740_mvp_real_step_pilot`, `State Machine Publish Runner Event Hooks` and the Project Workflow Index pilot pointer are referenced without executing smoke, manifest generation, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md`, `state_machine_enabled`, `phase_b_started`, `phase_c_started`, `main_verified`, `examples/publish_step/0750_publish_config_state_hooks.example.json`, the 0750 example configs and the Project Workflow Index hook pointer are referenced without executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md`, `tmp/0760_mvp_real_step_pilot_2_state_hooks`, `READY_TO_PUBLISH`, `Phase Plan`, `LAST-State.json` and the Project Workflow Index pilot pointer are referenced without executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md`, `runner_hooks`, `--include-runner-hooks`, `--expected-events`, `sample_manifest_input_runner_hooks_closed.json`, `sample_closed_with_runner_hooks_state.json` and `0780) MVP Real Step Pilot 3 with Manifest Hooks` are referenced without executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md`, `tmp/0780_mvp_real_step_pilot_3_manifest_hooks`, `READY_TO_PUBLISH`, `Phase Plan`, `--include-runner-hooks`, `--expected-final-state` and `0790) Post-MVP Roadmap and Hardening Plan` are referenced without executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md`, `POST-MVP DECISION: HARDENING FIRST`, `PowerShell Native Command Guardrail Hardening`, `Bridge Output Consistency and LAST Validation` and `0800) PowerShell Native Command Guardrail Hardening` are referenced without adding automation, executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
- `docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md`, `Invoke-NativeChecked`, `Assert-NoOutOfScopeFiles`, `PrNumber`, `AllowedExitCodes` and `0810) Publish Runner Recovery UX and No-False-Completed Guard` are referenced without executing hooks, Phase B/C, publish, merge or requiring Dropbox real paths;
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
- Workflow Quick Reference;
- Step Closure Report;
- Workflow Command Cookbook;
- Workflow Status Dashboard;
- Release Readiness;
- Existing Project Pilot Onboarding;
- ASF Next Step Runner;
- ASF Runner Project Profiles;
- ASF Runner Codex Handoff Improvements;
- ASF Runner Verification Pack;
- ASF Runner Verification Pack Hardening;
- ASF Codex Report Intake;
- ASF Human-Gated Closure Pack;
- ASF Human Approval Gate;
- ASF Codex Invocation Design;
- ASF Codex Invocation Dry Run Pack;
- ASF Codex Read-Only Invocation Prototype;
- ASF Codex Invocation Result Capture;
- ASF Codex Read-Only Safety Gate;
- ASF Codex Read-Only First Manual Trial;
- ASF Codex Read-Only Clean Target Trial;
- ASF Codex Read-Only Repeatable Trial Pack;
- ASF Codex Read-Only Trial Compare;
- ASF PowerShell Command Pack Skill Hardening;
- ASF PowerShell Command Pack Skill Finalization;
- ASF PowerShell Command Pack Skill Export Install;
- ASF OpenAI API Adapter;
- ASF OpenAI API Adapter Live Boundary Credential Gate;
- ASF OpenAI API Adapter First Controlled Live Smoke Test;
- ASF OpenAI API Adapter Live Smoke Result Hardening;
- ASF OpenAI API Adapter Controlled Live Execution Pack;
- OpenAI Provider HTTP Error and Rate Limit Diagnostic;
- ASF Verification Profile Selector;
- ASF Verification Profile Integration with Publish Runner;
- ASF Publish Config Generator;
- ASF Publish Config Generator Bridge Output Integration;
- ASF Step Execution State Machine;
- ASF State Machine Bridge Integration;
- ASF End-to-End MVP Smoke Scenario;
- ASF Motor Run Manifest;
- ASF MVP Usage Runbook;
- ASF End-to-End MVP Closure Pack;
- ASF MVP Real Step Pilot;
- ASF State Machine Publish Runner Event Hooks;
- ASF MVP Real Step Pilot 2 with State Hooks;
- ASF Runner Hook Evidence Manifest Integration;
- ASF MVP Real Step Pilot 3 with Manifest Hooks;
- ASF Post-MVP Roadmap and Hardening Plan;
- ASF PowerShell Native Command Guardrail Hardening;
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

After STEP 240, the health check also treats `docs/36_WORKFLOW_QUICK_REFERENCE.md` as a core workflow document because it is the compact command entry point for daily use.

After STEP 250, it also treats `docs/37_STEP_CLOSURE_REPORT.md` and `templates/codex_tasks/step_closure_report_template.md` as core closure references because they distinguish local Codex completion from a step closed and verified on `main`.

After STEP 260, it also treats `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` as a core workflow document because it captures recurring command scenarios and troubleshooting without creating new automation.

After STEP 270, it also treats `docs/39_WORKFLOW_STATUS_DASHBOARD.md` and `scripts/show_workflow_status.py` as core workflow status references because they provide a local read-only snapshot of branch, working tree, recent commits and workflow files.

After STEP 280, it also treats `docs/40_RELEASE_READINESS.md` and `templates/codex_tasks/release_readiness_checklist.md` as core readiness references because they define go/warning/no-go criteria for a local-first pilot.

After STEP 290, it also treats `docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md`, `templates/codex_tasks/existing_project_intake_template.md` and `templates/codex_tasks/first_pilot_step_packet_template.md` as core pilot onboarding references because they define intake, risk mapping and the first reversible pilot task packet for an existing project.

After STEP 300, it also treats `docs/42_ASF_NEXT_STEP_RUNNER.md`, `scripts/asf_next_step.py` and `templates/codex_tasks/asf_next_step_runner_handoff_template.md` as core runner references because they prepare task packet, Codex handoff and runner report without invoking Codex or modifying the target repository.

After STEP 340-360, it also treats the Automation Readiness Pack documents, scripts and templates as core runner references because they add hardened verification, Codex report intake and human-gated closure pack generation without executing commit, push, PR or merge.

After STEP 370-390, it also treats the Automation Bridge Pack documents, scripts and templates as core runner references because they add a Human Approval Gate, Codex invocation design and dry-run preview pack without executing Codex or modifying repository targets.

After STEP 400-420, it also treats the Codex Read-Only Invocation Prototype Pack documents, scripts and templates as core runner references because they add preview-by-default read-only execution support, result capture and a safety gate without enabling broader execution or automatic Git/GitHub actions.

After STEP 450, it also treats the Codex Read-Only Repeatable Trial Pack documents, scripts and templates as core workflow references because they make read-only trials repeatable, comparable and robust when Codex is not available, without enabling workspace-write or target repository modifications.

After STEP 490, it also treats `docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md` as a core workflow reference because Alberto's PowerShell command pack skill is used to generate robust, logged and human-gated local command packs for ASF operations.

After STEP 545, it also treats `docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md`, `templates/pwsh_command_pack/README.md` and `templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md` as core workflow references because the PowerShell command pack standard is now a repository-local canonical package and exportable skill draft.

After STEP 546, it also treats `docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md`, `templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md` and `scripts/install_pwsh_command_pack_skill.py` as core workflow references because the shared skill now has a controlled installable export and dry-run/apply installer.

After STEP 0550, it also treats `docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md` and `scripts/migrate_artifact_names_4digit.py` as core workflow references because ASF artifact naming now deprecates `LAST-*`, uses `NNNN-II-Tipo_Nome.ext`, and resolves the latest artifact with `max(II)` for `(step, type)`.

After STEP 500, it also treats `docs/65_ASF_OPENAI_API_ADAPTER.md`, `scripts/asf_openai_api_adapter.py` and `templates/codex_tasks/asf_openai_api_adapter_template.md` as core workflow references because the OpenAI API Adapter produces local dry-run/mock evidence without SDK dependencies, live calls or API key leakage.

After STEP 510, it also treats `docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md` and `templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md` as core workflow references because the OpenAI API Adapter live boundary produces deterministic no-network gate reports before any future controlled live smoke test.

After STEP 520, it also treats `docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md` and `templates/codex_tasks/asf_openai_api_live_smoke_test_template.md` as core workflow references because the OpenAI API Adapter can perform one controlled live smoke call only after explicit local gates, with `store: false`, sanitized evidence under `tmp/` and no default test dependency on network or real credentials.

After STEP 530, it also treats `docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md` as a core workflow reference because the OpenAI API Adapter live smoke result now has a stable schema, fail-closed classifications, safe JSON/Markdown artifacts and mocked test coverage before any future live execution.

After STEP 540, it also treats `docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md`, `scripts/asf_openai_controlled_live_execution_pack.py` and `templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1` as core workflow references because future OpenAI live execution must use a separate dry-run-default, double-consent, artifact-safe pack.

After STEP 0560, it also treats `scripts/asf_openai_first_authorized_live_run.py`, `docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md` and `docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md` as core workflow references because the first authorized live run must pass through the repository adapter, stay one-call, classify provider-side HTTP/rate/quota blocks, and record sanitized BLOCKED or success results without secrets.

After STEP 0670, it also treats `docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md`, `scripts/asf_step_state_machine.py`, `tests/unit/test_asf_step_state_machine.py` and `examples/state_machine/` as core workflow references because step execution state, recovery and fail-closed transition checks are now part of the MVP Motore operating map.

After STEP 0680, it also treats `docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md` and the Project Workflow Index pointers to `LAST-State.json`, `LAST-Event.json`, `LAST-Output_Compatto.md` and `state_machine` as core workflow references. The check only verifies repository docs and script references; it does not require or access the real Dropbox Bridge.

After STEP 0690, it also treats `docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md`, `examples/publish_config_generator/sample_state_machine_integration_input.json`, `examples/state_machine/sample_local_verified_state.json` and the Project Workflow Index pointers to `LAST-Publish_Config.json`, `LAST-State.json` and `--update-state` as core workflow references. The check remains read-only and does not execute Phase B, Phase C, publish, merge or Bridge writes.

After STEP 0700, it also treats `docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md`, `scripts/asf_e2e_mvp_smoke.py`, `tests/unit/test_asf_e2e_mvp_smoke.py` and the Project Workflow Index pointers to `tmp/e2e_mvp_smoke`, `negative_fail_closed.json` and `READY_TO_PUBLISH` as core workflow references. The check remains read-only: it does not run the e2e smoke, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or Bridge writes.

After STEP 0710, it also treats `docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md`, `scripts/asf_motor_run_manifest.py`, `tests/unit/test_asf_motor_run_manifest.py`, `examples/motor_run_manifest/` and the Project Workflow Index pointers to `motor_run_manifest.json`, `motor_run_summary.md` and `LAST-Run_Manifest.json` as core workflow references. The check remains read-only: it does not generate manifests, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or Bridge writes.

After STEP 0720, it also treats `docs/motor/0720_MVP_USAGE_RUNBOOK.md` and the Project Workflow Index pointers to `codex_command`, `publish_config`, `state_machine`, `motor_run`, `Phase B`, `Phase C`, `-ApprovePublish`, `-ApproveMerge` and `READY_TO_PUBLISH` as core workflow references. The check remains read-only: it does not execute smoke, manifest generation, Bridge writes, Phase B, Phase C, publish, merge or deploy.

After STEP 0730, it also treats `docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md` and the Project Workflow Index pointers to `MVP STATUS: GO WITH WARNINGS`, `GO/WARNING/NO-GO` and `0740) MVP Real Step Pilot` as core workflow references. The check remains read-only: it does not change MVP status automatically, execute smoke, generate manifests, write Bridge output, run Phase B/C, publish, merge or deploy.

After STEP 0740, it also treats `docs/motor/0740_MVP_REAL_STEP_PILOT.md` and the Project Workflow Index pointers to `PILOT STATUS: GO WITH WARNINGS`, `tmp/0740_mvp_real_step_pilot` and `0750) State Machine Publish Runner Event Hooks` as core workflow references. The check remains read-only: it does not run smoke, generate manifests, write Bridge output, run Phase B/C, publish, merge or deploy.

After STEP 0750, it also treats `docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md`, `examples/publish_step/0750_publish_config_state_hooks.example.json`, the other 0750 publish config examples and the Project Workflow Index pointers to `state_machine_enabled`, `phase_b_started`, `phase_c_started`, `main_verified`, `-ApprovePublish` and `-ApproveMerge` as core workflow references. The check remains read-only: it does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.

After STEP 0760, it also treats `docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md` and the Project Workflow Index pointers to `tmp/0760_mvp_real_step_pilot_2_state_hooks`, `READY_TO_PUBLISH`, `Phase Plan`, `LAST-State.json` and `0770) Runner Hook Evidence Manifest Integration` as core workflow references. The check remains read-only: it does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.

After STEP 0770, it also treats `docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md` and the Project Workflow Index pointers to `runner_hooks`, `--include-runner-hooks`, `--expected-events`, `sample_manifest_input_runner_hooks_closed.json`, `sample_closed_with_runner_hooks_state.json` and `0780) MVP Real Step Pilot 3 with Manifest Hooks` as core workflow references. The check remains read-only: it does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.

After STEP 0780, it also treats `docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md` and the Project Workflow Index pointers to `tmp/0780_mvp_real_step_pilot_3_manifest_hooks`, `READY_TO_PUBLISH`, `Phase Plan`, `--include-runner-hooks`, `--expected-final-state` and `0790) Post-MVP Roadmap and Hardening Plan` as core workflow references. The check remains read-only: it does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.

After STEP 0790, it also treats `docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md` and the Project Workflow Index pointers to `POST-MVP DECISION: HARDENING FIRST`, `PowerShell Native Command Guardrail Hardening`, `Bridge Output Consistency and LAST Validation` and `0800) PowerShell Native Command Guardrail Hardening` as core workflow references. The check remains read-only: it does not add automation, does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.

After STEP 0800, it also treats `docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md` and the Project Workflow Index pointers to `Invoke-NativeChecked`, `Assert-NoOutOfScopeFiles`, `PrNumber`, `AllowedExitCodes` and `0810) Publish Runner Recovery UX and No-False-Completed Guard` as core workflow references. The check remains read-only: it does not run state hooks, does not call GitHub, does not require Dropbox, and does not execute Phase B, Phase C, publish, merge or deploy.
