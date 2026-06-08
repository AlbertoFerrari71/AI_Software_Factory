from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


@dataclass(frozen=True)
class HealthIssue:
    area: str
    path: str
    requirement: str
    suggestion: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def contains(text: str, fragment: str) -> bool:
    return fragment.casefold() in text.casefold()


def contains_any(text: str, fragments: list[str]) -> bool:
    return any(contains(text, fragment) for fragment in fragments)


def check_files(root: Path) -> list[HealthIssue]:
    required_paths = [
        "README.md",
        "CHANGELOG.md",
        "docs/19_PROMPT_PACKET_GENERATOR.md",
        "docs/20_VERIFICATION_GATE.md",
        "docs/21_DOCUMENTATION_SYNC.md",
        "docs/24_SOFT_PROTECTION_GUARDRAILS.md",
        "docs/26_PROMPT_PACKET_VALIDATION_LITE.md",
        "docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md",
        "docs/31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md",
        "docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md",
        "docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md",
        "docs/34_PROJECT_WORKFLOW_INDEX.md",
        "docs/35_WORKFLOW_HEALTH_CHECK.md",
        "docs/36_WORKFLOW_QUICK_REFERENCE.md",
        "docs/37_STEP_CLOSURE_REPORT.md",
        "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
        "docs/39_WORKFLOW_STATUS_DASHBOARD.md",
        "docs/40_RELEASE_READINESS.md",
        "docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md",
        "docs/42_ASF_NEXT_STEP_RUNNER.md",
        "docs/43_ASF_RUNNER_PROJECT_PROFILES.md",
        "docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md",
        "docs/45_ASF_RUNNER_VERIFICATION_PACK.md",
        "docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md",
        "docs/47_ASF_CODEX_REPORT_INTAKE.md",
        "docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md",
        "docs/49_ASF_HUMAN_APPROVAL_GATE.md",
        "docs/50_ASF_CODEX_INVOCATION_DESIGN.md",
        "docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md",
        "docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md",
        "docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md",
        "docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md",
        "docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md",
        "docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md",
        "docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md",
        "docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md",
        "docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md",
        "docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md",
        "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
        "docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md",
        "docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md",
        "docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md",
        "docs/65_ASF_OPENAI_API_ADAPTER.md",
        "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md",
        "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md",
        "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md",
        "docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md",
        "docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md",
        "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md",
        "docs/motor/0580_DRY_RUN_LOOP_RUNNER.md",
        "docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md",
        "docs/motor/0600_RISK_CLASSIFIER_GATE_POLICY.md",
        "docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md",
        "docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md",
        "docs/motor/0620_VERIFICATION_BALANCE_NOTES.md",
        "docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md",
        "docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md",
        "docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md",
        "docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md",
        "docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md",
        "docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md",
        "docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md",
        "docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md",
        "docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md",
        "docs/motor/0720_MVP_USAGE_RUNBOOK.md",
        "docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md",
        "docs/motor/0740_MVP_REAL_STEP_PILOT.md",
        "docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md",
        "docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md",
        "docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md",
        "docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md",
        "docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md",
        "docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md",
        "config/asf_project_profiles.json",
        "scripts/asf_openai_api_adapter.py",
        "scripts/asf_openai_controlled_live_execution_pack.py",
        "scripts/asf_openai_first_authorized_live_run.py",
        "scripts/asf_dry_run_loop_runner.py",
        "scripts/asf_publish_step.ps1",
        "scripts/asf_publish_config_generator.py",
        "scripts/asf_risk_classifier.py",
        "scripts/asf_gate_decision_report.py",
        "scripts/asf_verification_profile_selector.py",
        "scripts/asf_step_state_machine.py",
        "scripts/asf_e2e_mvp_smoke.py",
        "scripts/asf_motor_run_manifest.py",
        "scripts/install_pwsh_command_pack_skill.py",
        "scripts/migrate_artifact_names_4digit.py",
        "scripts/asf_codex_invocation_dry_run.py",
        "scripts/asf_codex_readonly_invoke.py",
        "scripts/asf_codex_readonly_repeatable_trial.py",
        "scripts/asf_codex_result_capture.py",
        "scripts/asf_codex_readonly_safety_gate.py",
        "scripts/asf_codex_readonly_trial_compare.py",
        "scripts/asf_codex_report_intake.py",
        "scripts/asf_generate_closure_pack.py",
        "scripts/asf_human_approval_gate.py",
        "scripts/asf_next_step.py",
        "scripts/generate_task_packet.py",
        "scripts/generate_task_packet.ps1",
        "scripts/smoke_prompt_packet_release.ps1",
        "scripts/show_workflow_status.py",
        "scripts/validate_task_packet.py",
        "scripts/verify.ps1",
        "scripts/git/check_soft_guardrails.ps1",
        "templates/codex_tasks/codex_task_packet_template.md",
        "templates/codex_tasks/prompt_packet_lifecycle_checklist.md",
        "templates/codex_tasks/step_closure_report_template.md",
        "templates/codex_tasks/release_readiness_checklist.md",
        "templates/codex_tasks/existing_project_intake_template.md",
        "templates/codex_tasks/first_pilot_step_packet_template.md",
        "templates/codex_tasks/asf_next_step_runner_handoff_template.md",
        "templates/codex_tasks/asf_runner_verification_pack_template.md",
        "templates/codex_tasks/asf_codex_report_intake_template.md",
        "templates/codex_tasks/asf_human_gated_closure_pack_template.md",
        "templates/codex_tasks/asf_human_approval_gate_template.md",
        "templates/codex_tasks/asf_codex_invocation_dry_run_template.md",
        "templates/codex_tasks/asf_codex_readonly_invocation_template.md",
        "templates/codex_tasks/asf_codex_invocation_result_capture_template.md",
        "templates/codex_tasks/asf_codex_readonly_safety_gate_template.md",
        "templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md",
        "templates/codex_tasks/asf_codex_readonly_trial_compare_template.md",
        "templates/codex_tasks/asf_openai_api_adapter_template.md",
        "templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md",
        "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
        "templates/pwsh_command_pack/README.md",
        "templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md",
        "templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md",
        "templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1",
        "examples/dry_run_loop/step_0580_simulated_request.json",
        "examples/dry_run_loop/step_0580_execution_plan.json",
        "examples/dry_run_loop/step_0610_docs_only_request.json",
        "examples/dry_run_loop/step_0610_code_change_request.json",
        "examples/dry_run_loop/step_0610_publish_intent_request.json",
        "examples/dry_run_loop/step_0610_l4_blocked_request.json",
        "examples/publish_step/0590_publish_config.example.json",
        "examples/publish_step/0640_publish_config_motor_core.example.json",
        "examples/publish_step/0640_publish_config_docs_only.example.json",
        "examples/publish_step/0640_publish_config_profile_mismatch_fail_closed.example.json",
        "examples/publish_step/0750_publish_config_state_hooks.example.json",
        "examples/publish_step/0750_publish_config_state_hooks_close_step.example.json",
        "examples/publish_step/0750_publish_config_state_hooks_mismatch_fail_closed.example.json",
        "examples/risk_classifier/sample_l0_docs_only.json",
        "examples/risk_classifier/sample_l2_code_change.json",
        "examples/risk_classifier/sample_l3_publish.json",
        "examples/risk_classifier/sample_l4_deploy_or_destructive.json",
        "examples/gate_decision/sample_l1_local_docs.json",
        "examples/gate_decision/sample_l2_code_change_checked.json",
        "examples/gate_decision/sample_l3_publish_needs_approval.json",
        "examples/gate_decision/sample_l3_publish_approved.json",
        "examples/gate_decision/sample_l4_blocked.json",
        "examples/gate_decision/sample_invalid_fail_closed.json",
        "examples/verification_profiles/sample_docs_only.json",
        "examples/verification_profiles/sample_code_unit.json",
        "examples/verification_profiles/sample_motor_core.json",
        "examples/verification_profiles/sample_publish.json",
        "examples/verification_profiles/sample_final_main.json",
        "examples/verification_profiles/sample_high_risk.json",
        "examples/verification_profiles/sample_ambiguous_fail_closed.json",
        "examples/publish_config_generator/sample_docs_only_input.json",
        "examples/publish_config_generator/sample_code_unit_input.json",
        "examples/publish_config_generator/sample_motor_core_input.json",
        "examples/publish_config_generator/sample_publish_runner_input.json",
        "examples/publish_config_generator/sample_bridge_output_input.json",
        "examples/publish_config_generator/sample_state_machine_integration_input.json",
        "examples/publish_config_generator/sample_high_risk_fail_closed_input.json",
        "examples/publish_config_generator/sample_missing_required_fields_fail_closed_input.json",
        "examples/state_machine/sample_normal_flow_events.json",
        "examples/state_machine/sample_phase_c_failed_recovery.json",
        "examples/state_machine/sample_combined_recovery_step.json",
        "examples/state_machine/sample_invalid_transition_fail_closed.json",
        "examples/state_machine/sample_local_verified_state.json",
        "examples/state_machine/sample_closed_with_runner_hooks_state.json",
        "examples/motor_run_manifest/sample_manifest_input_ready.json",
        "examples/motor_run_manifest/sample_manifest_input_fail_closed.json",
        "examples/motor_run_manifest/sample_manifest_input_missing_artifacts.json",
        "examples/motor_run_manifest/sample_manifest_input_runner_hooks_closed.json",
        "examples/motor_run_manifest/sample_manifest_input_runner_hooks_missing_event.json",
        "examples/motor_run_manifest/sample_manifest_input_runner_hooks_step_mismatch.json",
        "tests/unit/test_asf_verification_profile_selector.py",
        "tests/unit/test_asf_publish_step_runner.py",
        "tests/unit/test_asf_publish_config_generator.py",
        "tests/unit/test_asf_step_state_machine.py",
        "tests/unit/test_asf_e2e_mvp_smoke.py",
        "tests/unit/test_asf_motor_run_manifest.py",
    ]

    issues: list[HealthIssue] = []
    for relative_path in required_paths:
        if not (root / relative_path).is_file():
            issues.append(
                HealthIssue(
                    area="files",
                    path=relative_path,
                    requirement="required file exists",
                    suggestion="Restore or create the expected workflow file.",
                )
            )
    return issues


def check_required_fragments(
    *,
    root: Path,
    area: str,
    relative_path: str,
    requirements: list[tuple[str, list[str]]],
) -> list[HealthIssue]:
    issues: list[HealthIssue] = []
    try:
        text = read_text(root, relative_path)
    except FileNotFoundError:
        return [
            HealthIssue(
                area=area,
                path=relative_path,
                requirement="file readable",
                suggestion="Restore the file before checking its content.",
            )
        ]

    for label, fragments in requirements:
        if not contains_any(text, fragments):
            issues.append(
                HealthIssue(
                    area=area,
                    path=relative_path,
                    requirement=label,
                    suggestion="Add or restore the missing workflow reference.",
                )
            )
    return issues


def check_project_workflow_index(root: Path) -> list[HealthIssue]:
    return check_required_fragments(
        root=root,
        area="project workflow index",
        relative_path="docs/34_PROJECT_WORKFLOW_INDEX.md",
        requirements=[
            ("Prompt Packet Generator", ["Prompt Packet Generator"]),
            ("Lite Mode", ["Lite Mode"]),
            ("Strict Mode", ["Strict Mode"]),
            ("Verification Gate", ["Verification Gate"]),
            ("Documentation Sync", ["Documentation Sync"]),
            ("Soft Protection Guardrails", ["Soft Protection Guardrails"]),
            ("Release Smoke Workflow", ["Release Smoke Workflow"]),
            ("Lifecycle Checklist", ["Lifecycle Checklist"]),
            ("Developer Onboarding", ["Developer Onboarding"]),
            ("Workflow Quick Reference", ["Workflow Quick Reference"]),
            ("Step Closure Report", ["Step Closure Report"]),
            ("Workflow Command Cookbook", ["Workflow Command Cookbook"]),
            ("Workflow Status Dashboard", ["Workflow Status Dashboard"]),
            ("Release Readiness", ["Release Readiness"]),
            ("Existing Project Pilot Onboarding", ["Existing Project Pilot Onboarding"]),
            ("ASF Next Step Runner", ["ASF Next Step Runner"]),
            ("ASF Runner Project Profiles", ["ASF Runner Project Profiles"]),
            ("ASF Runner Codex Handoff Improvements", ["ASF Runner Codex Handoff Improvements"]),
            ("ASF Runner Verification Pack", ["ASF Runner Verification Pack"]),
            ("ASF Runner Verification Pack Hardening", ["ASF Runner Verification Pack Hardening"]),
            ("ASF Codex Report Intake", ["ASF Codex Report Intake"]),
            ("ASF Human-Gated Closure Pack", ["ASF Human-Gated Closure Pack"]),
            ("ASF Human Approval Gate", ["ASF Human Approval Gate"]),
            ("ASF Codex Invocation Design", ["ASF Codex Invocation Design"]),
            ("ASF Codex Invocation Dry Run Pack", ["ASF Codex Invocation Dry Run Pack"]),
            ("ASF Codex Read-Only Invocation Prototype", ["ASF Codex Read-Only Invocation Prototype"]),
            ("ASF Codex Invocation Result Capture", ["ASF Codex Invocation Result Capture"]),
            ("ASF Codex Read-Only Safety Gate", ["ASF Codex Read-Only Safety Gate"]),
            ("ASF Codex Read-Only First Manual Trial", ["ASF Codex Read-Only First Manual Trial"]),
            ("ASF Codex Read-Only Clean Target Trial", ["ASF Codex Read-Only Clean Target Trial"]),
            ("ASF Codex Read-Only Repeatable Trial Pack", ["ASF Codex Read-Only Repeatable Trial Pack"]),
            ("ASF Codex Read-Only Trial Compare", ["ASF Codex Read-Only Trial Compare"]),
            ("ASF PowerShell Command Pack Skill Hardening", ["ASF PowerShell Command Pack Skill Hardening"]),
            ("ASF PowerShell Command Pack Skill Finalization", ["ASF PowerShell Command Pack Skill Finalization"]),
            ("ASF PowerShell Command Pack Skill Export Install", ["ASF PowerShell Command Pack Skill Export Install"]),
            (
                "LAST Deprecation and 4-Digit Artifact Naming Standard",
                ["LAST Deprecation and 4-Digit Artifact Naming Standard"],
            ),
            ("ASF OpenAI API Adapter", ["ASF OpenAI API Adapter"]),
            (
                "ASF OpenAI API Adapter Live Boundary Credential Gate",
                ["ASF OpenAI API Adapter Live Boundary Credential Gate"],
            ),
            (
                "ASF OpenAI API Adapter First Controlled Live Smoke Test",
                ["ASF OpenAI API Adapter First Controlled Live Smoke Test"],
            ),
            (
                "ASF OpenAI API Adapter Live Smoke Result Hardening",
                ["ASF OpenAI API Adapter Live Smoke Result Hardening"],
            ),
            (
                "ASF OpenAI API Adapter Controlled Live Execution Pack",
                ["ASF OpenAI API Adapter Controlled Live Execution Pack"],
            ),
            (
                "OpenAI API Adapter First Authorized Live Run",
                ["OpenAI API Adapter First Authorized Live Run"],
            ),
            (
                "OpenAI Provider HTTP Error and Rate Limit Diagnostic",
                ["OpenAI Provider HTTP Error and Rate Limit Diagnostic"],
            ),
            ("ASF Dry-run Loop Runner", ["ASF Dry-run Loop Runner"]),
            ("ASF Stable PowerShell Publish Runner", ["ASF Stable PowerShell Publish Runner"]),
            ("ASF Risk Classifier Gate Policy", ["ASF Risk Classifier + Gate Policy"]),
            ("ASF Risk Classifier Dry-run Integration", ["ASF Risk Classifier Dry-run Integration"]),
            ("ASF Gate Decision Report", ["ASF Gate Decision Report"]),
            ("ASF Verification Balance Notes", ["Verification Balance Notes"]),
            ("generate task packet script", ["scripts/generate_task_packet.py"]),
            ("task packet validator script", ["scripts/validate_task_packet.py"]),
            ("ASF Next Step Runner script", ["scripts/asf_next_step.py"]),
            ("ASF Codex Report Intake script", ["scripts/asf_codex_report_intake.py"]),
            ("ASF Human-Gated Closure Pack script", ["scripts/asf_generate_closure_pack.py"]),
            ("ASF Human Approval Gate script", ["scripts/asf_human_approval_gate.py"]),
            ("ASF Codex Invocation Dry Run script", ["scripts/asf_codex_invocation_dry_run.py"]),
            ("ASF Codex Read-Only Invocation script", ["scripts/asf_codex_readonly_invoke.py"]),
            ("ASF Codex Read-Only Repeatable Trial script", ["scripts/asf_codex_readonly_repeatable_trial.py"]),
            ("ASF Codex Result Capture script", ["scripts/asf_codex_result_capture.py"]),
            ("ASF Codex Read-Only Safety Gate script", ["scripts/asf_codex_readonly_safety_gate.py"]),
            ("ASF Codex Read-Only Trial Compare script", ["scripts/asf_codex_readonly_trial_compare.py"]),
            ("ASF OpenAI API Adapter script", ["scripts/asf_openai_api_adapter.py"]),
            (
                "ASF OpenAI API Adapter Controlled Live Execution Pack script",
                ["scripts/asf_openai_controlled_live_execution_pack.py"],
            ),
            (
                "OpenAI API Adapter First Authorized Live Run script",
                ["scripts/asf_openai_first_authorized_live_run.py"],
            ),
            (
                "ASF Dry-run Loop Runner script",
                ["scripts/asf_dry_run_loop_runner.py"],
            ),
            (
                "ASF Stable PowerShell Publish Runner script",
                ["scripts/asf_publish_step.ps1"],
            ),
            (
                "ASF Risk Classifier script",
                ["scripts/asf_risk_classifier.py"],
            ),
            (
                "ASF Gate Decision Report script",
                ["scripts/asf_gate_decision_report.py"],
            ),
            (
                "ASF Verification Profile Selector script",
                ["scripts/asf_verification_profile_selector.py"],
            ),
            (
                "ASF Risk Classifier Dry-run Integration document",
                ["docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md"],
            ),
            (
                "ASF Gate Decision Report document",
                ["docs/motor/0620_GATE_DECISION_REPORT_HUMAN_APPROVAL_PACKET.md"],
            ),
            (
                "ASF Verification Balance Notes document",
                ["docs/motor/0620_VERIFICATION_BALANCE_NOTES.md"],
            ),
            (
                "ASF Verification Profile Selector document",
                ["docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md"],
            ),
            (
                "ASF Verification Profile Publish Runner Integration document",
                ["docs/motor/0640_VERIFICATION_PROFILE_INTEGRATION_PUBLISH_RUNNER.md"],
            ),
            (
                "ASF Publish Config Generator document",
                ["docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md"],
            ),
            (
                "ASF Publish Config Generator Bridge Output Integration document",
                ["docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md"],
            ),
            (
                "ASF Step Execution State Machine document",
                ["docs/motor/0670_STEP_EXECUTION_STATE_MACHINE.md"],
            ),
            (
                "ASF State Machine Bridge Integration document",
                ["docs/motor/0680_STATE_MACHINE_BRIDGE_INTEGRATION.md"],
            ),
            (
                "ASF State Machine Publish Config Generator Integration document",
                ["docs/motor/0690_STATE_MACHINE_INTEGRATION_WITH_PUBLISH_CONFIG_GENERATOR.md"],
            ),
            (
                "ASF End-to-End MVP Smoke Scenario document",
                ["docs/motor/0700_END_TO_END_MVP_SMOKE_SCENARIO.md"],
            ),
            (
                "ASF Motor Run Manifest document",
                ["docs/motor/0710_MOTOR_RUN_MANIFEST_AND_EVIDENCE_PACK.md"],
            ),
            (
                "ASF MVP Usage Runbook document",
                ["docs/motor/0720_MVP_USAGE_RUNBOOK.md"],
            ),
            (
                "ASF End-to-End MVP Closure Pack document",
                ["docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md"],
            ),
            (
                "ASF MVP Real Step Pilot document",
                ["docs/motor/0740_MVP_REAL_STEP_PILOT.md"],
            ),
            (
                "ASF State Machine Publish Runner Event Hooks document",
                ["docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md"],
            ),
            (
                "ASF MVP Real Step Pilot 2 with State Hooks document",
                ["docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md"],
            ),
            (
                "ASF Runner Hook Evidence Manifest Integration document",
                ["docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md"],
            ),
            (
                "ASF MVP Real Step Pilot 3 with Manifest Hooks document",
                ["docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md"],
            ),
            (
                "ASF Post-MVP Roadmap and Hardening Plan document",
                ["docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md"],
            ),
            (
                "ASF PowerShell Native Command Guardrail Hardening document",
                ["docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md"],
            ),
            (
                "ASF PowerShell Native Command Guardrail Hardening pointers",
                [
                    "Invoke-NativeChecked",
                    "Assert-NoOutOfScopeFiles",
                    "PrNumber",
                    "AllowedExitCodes",
                    "0810) Publish Runner Recovery UX and No-False-Completed Guard",
                ],
            ),
            (
                "ASF State Machine Bridge Integration pointers",
                ["LAST-State.json", "LAST-Output_Compatto.md", "state_machine"],
            ),
            (
                "ASF State Machine Publish Config Generator Integration pointers",
                ["LAST-Publish_Config.json", "LAST-State.json", "--update-state"],
            ),
            (
                "ASF End-to-End MVP Smoke Scenario pointers",
                ["tmp/e2e_mvp_smoke", "negative_fail_closed.json", "READY_TO_PUBLISH"],
            ),
            (
                "ASF Motor Run Manifest pointers",
                ["motor_run_manifest.json", "motor_run_summary.md", "LAST-Run_Manifest.json"],
            ),
            (
                "ASF MVP Usage Runbook pointers",
                [
                    "codex_command",
                    "publish_config",
                    "state_machine",
                    "motor_run",
                    "Phase B",
                    "Phase C",
                    "-ApprovePublish",
                    "-ApproveMerge",
                    "READY_TO_PUBLISH",
                ],
            ),
            (
                "ASF End-to-End MVP Closure Pack pointers",
                [
                    "MVP STATUS: GO WITH WARNINGS",
                    "GO/WARNING/NO-GO",
                    "0740) MVP Real Step Pilot",
                ],
            ),
            (
                "ASF MVP Real Step Pilot pointers",
                [
                    "PILOT STATUS: GO WITH WARNINGS",
                    "tmp/0740_mvp_real_step_pilot",
                    "0750) State Machine Publish Runner Event Hooks",
                ],
            ),
            (
                "ASF State Machine Publish Runner Event Hooks pointers",
                [
                    "state_machine_enabled",
                    "phase_b_started",
                    "phase_c_started",
                    "main_verified",
                    "examples/publish_step/0750_publish_config_state_hooks.example.json",
                    "-ApprovePublish",
                    "-ApproveMerge",
                ],
            ),
            (
                "ASF MVP Real Step Pilot 2 with State Hooks pointers",
                [
                    "PILOT STATUS: GO WITH WARNINGS",
                    "tmp/0760_mvp_real_step_pilot_2_state_hooks",
                    "READY_TO_PUBLISH",
                    "Phase Plan",
                    "LAST-State.json",
                    "0770) Runner Hook Evidence Manifest Integration",
                ],
            ),
            (
                "ASF Runner Hook Evidence Manifest Integration pointers",
                [
                    "runner_hooks",
                    "--include-runner-hooks",
                    "--expected-events",
                    "sample_manifest_input_runner_hooks_closed.json",
                    "sample_closed_with_runner_hooks_state.json",
                    "0780) MVP Real Step Pilot 3 with Manifest Hooks",
                ],
            ),
            (
                "ASF MVP Real Step Pilot 3 with Manifest Hooks pointers",
                [
                    "PILOT STATUS: GO WITH WARNINGS",
                    "tmp/0780_mvp_real_step_pilot_3_manifest_hooks",
                    "READY_TO_PUBLISH",
                    "Phase Plan",
                    "--include-runner-hooks",
                    "--expected-final-state",
                    "0790) Post-MVP Roadmap and Hardening Plan",
                ],
            ),
            (
                "ASF Post-MVP Roadmap and Hardening Plan pointers",
                [
                    "POST-MVP DECISION: HARDENING FIRST",
                    "PowerShell Native Command Guardrail Hardening",
                    "Bridge Output Consistency and LAST Validation",
                    "0800) PowerShell Native Command Guardrail Hardening",
                ],
            ),
            (
                "ASF Publish Config Generator script",
                ["scripts/asf_publish_config_generator.py"],
            ),
            (
                "ASF Step Execution State Machine script",
                ["scripts/asf_step_state_machine.py"],
            ),
            (
                "ASF End-to-End MVP Smoke Scenario script",
                ["scripts/asf_e2e_mvp_smoke.py"],
            ),
            (
                "ASF Motor Run Manifest script",
                ["scripts/asf_motor_run_manifest.py"],
            ),
            (
                "ASF Publish Config Generator examples",
                ["examples/publish_config_generator/"],
            ),
            (
                "ASF State Machine Publish Runner Event Hooks examples",
                [
                    "examples/publish_step/0750_publish_config_state_hooks.example.json",
                    "examples/publish_step/0750_publish_config_state_hooks_close_step.example.json",
                    "examples/publish_step/0750_publish_config_state_hooks_mismatch_fail_closed.example.json",
                ],
            ),
            (
                "ASF Publish Config Generator State Machine integration example",
                ["sample_state_machine_integration_input.json"],
            ),
            (
                "ASF Step Execution State Machine examples",
                ["examples/state_machine/"],
            ),
            (
                "ASF Motor Run Manifest examples",
                ["examples/motor_run_manifest/"],
            ),
            (
                "ASF Motor Run Manifest runner hook examples",
                [
                    "sample_manifest_input_runner_hooks_closed.json",
                    "sample_manifest_input_runner_hooks_missing_event.json",
                    "sample_manifest_input_runner_hooks_step_mismatch.json",
                ],
            ),
            (
                "ASF State Machine local verified example",
                ["sample_local_verified_state.json"],
            ),
            (
                "ASF State Machine closed runner hooks example",
                ["sample_closed_with_runner_hooks_state.json"],
            ),
            (
                "artifact naming migration script",
                ["scripts/migrate_artifact_names_4digit.py"],
            ),
            ("verification gate script", ["scripts/verify.ps1"]),
            ("soft guardrails check script", ["scripts/git/check_soft_guardrails.ps1"]),
            ("Workflow Health Check document", ["docs/35_WORKFLOW_HEALTH_CHECK.md"]),
            ("Workflow Health Check script", ["scripts/check_workflow_health.py"]),
            ("Workflow Quick Reference document", ["docs/36_WORKFLOW_QUICK_REFERENCE.md"]),
            ("Step Closure Report document", ["docs/37_STEP_CLOSURE_REPORT.md"]),
            ("Step Closure Report template", ["templates/codex_tasks/step_closure_report_template.md"]),
            ("Workflow Command Cookbook document", ["docs/38_WORKFLOW_COMMAND_COOKBOOK.md"]),
            ("Workflow Status Dashboard document", ["docs/39_WORKFLOW_STATUS_DASHBOARD.md"]),
            ("Workflow Status Dashboard script", ["scripts/show_workflow_status.py"]),
            ("Release Readiness document", ["docs/40_RELEASE_READINESS.md"]),
            ("Release Readiness template", ["templates/codex_tasks/release_readiness_checklist.md"]),
            ("Existing Project Pilot Onboarding document", ["docs/41_EXISTING_PROJECT_PILOT_ONBOARDING.md"]),
            ("Existing Project Intake template", ["templates/codex_tasks/existing_project_intake_template.md"]),
            ("First Pilot Step Packet template", ["templates/codex_tasks/first_pilot_step_packet_template.md"]),
            ("ASF Next Step Runner document", ["docs/42_ASF_NEXT_STEP_RUNNER.md"]),
            ("ASF Runner Project Profiles document", ["docs/43_ASF_RUNNER_PROJECT_PROFILES.md"]),
            (
                "ASF Runner Codex Handoff Improvements document",
                ["docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md"],
            ),
            ("ASF Runner Verification Pack document", ["docs/45_ASF_RUNNER_VERIFICATION_PACK.md"]),
            (
                "ASF Runner Verification Pack Hardening document",
                ["docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md"],
            ),
            ("ASF Codex Report Intake document", ["docs/47_ASF_CODEX_REPORT_INTAKE.md"]),
            ("ASF Human-Gated Closure Pack document", ["docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md"]),
            ("ASF Human Approval Gate document", ["docs/49_ASF_HUMAN_APPROVAL_GATE.md"]),
            ("ASF Codex Invocation Design document", ["docs/50_ASF_CODEX_INVOCATION_DESIGN.md"]),
            ("ASF Codex Invocation Dry Run Pack document", ["docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md"]),
            (
                "ASF Codex Read-Only Invocation Prototype document",
                ["docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md"],
            ),
            ("ASF Codex Invocation Result Capture document", ["docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md"]),
            ("ASF Codex Read-Only Safety Gate document", ["docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md"]),
            (
                "ASF Codex Read-Only First Manual Trial document",
                ["docs/55_ASF_CODEX_READONLY_FIRST_MANUAL_TRIAL.md"],
            ),
            (
                "ASF Codex Read-Only First Trial Results document",
                ["docs/56_ASF_CODEX_READONLY_FIRST_TRIAL_RESULTS.md"],
            ),
            (
                "ASF Codex Read-Only Clean Target Trial document",
                ["docs/57_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL.md"],
            ),
            (
                "ASF Codex Read-Only Clean Target Trial Results document",
                ["docs/58_ASF_CODEX_READONLY_CLEAN_TARGET_TRIAL_RESULTS.md"],
            ),
            (
                "ASF Codex Read-Only Repeatable Trial Pack document",
                ["docs/59_ASF_CODEX_READONLY_REPEATABLE_TRIAL_PACK.md"],
            ),
            (
                "ASF Codex Read-Only Repeatable Trial Results document",
                ["docs/60_ASF_CODEX_READONLY_REPEATABLE_TRIAL_RESULTS.md"],
            ),
            (
                "ASF PowerShell Command Pack Skill Hardening document",
                ["docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md"],
            ),
            (
                "ASF PowerShell Command Pack Skill Finalization document",
                ["docs/70_ASF_PWSH_COMMAND_PACK_SKILL_FINALIZATION.md"],
            ),
            (
                "ASF PowerShell Command Pack Skill Export Install document",
                ["docs/71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md"],
            ),
            (
                "LAST Deprecation and 4-Digit Artifact Naming Standard document",
                ["docs/73_LAST_DEPRECATION_4_DIGIT_ARTIFACT_NAMING_STANDARD.md"],
            ),
            (
                "ASF OpenAI API Adapter document",
                ["docs/65_ASF_OPENAI_API_ADAPTER.md"],
            ),
            (
                "ASF OpenAI API Adapter Live Boundary Credential Gate document",
                ["docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md"],
            ),
            (
                "ASF OpenAI API Adapter First Controlled Live Smoke Test document",
                ["docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md"],
            ),
            (
                "ASF OpenAI API Adapter Live Smoke Result Hardening document",
                ["docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md"],
            ),
            (
                "ASF OpenAI API Adapter Controlled Live Execution Pack document",
                ["docs/69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md"],
            ),
            (
                "OpenAI API Adapter First Authorized Live Run report",
                ["docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md"],
            ),
            (
                "OpenAI Provider HTTP Error and Rate Limit Diagnostic document",
                ["docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md"],
            ),
            (
                "ASF Dry-run Loop Runner document",
                ["docs/motor/0580_DRY_RUN_LOOP_RUNNER.md"],
            ),
            (
                "ASF Stable PowerShell Publish Runner document",
                ["docs/motor/0590_STABLE_POWERSHELL_PUBLISH_RUNNER.md"],
            ),
            ("ASF project profiles config", ["config/asf_project_profiles.json"]),
            (
                "ASF Next Step Runner handoff template",
                ["templates/codex_tasks/asf_next_step_runner_handoff_template.md"],
            ),
            (
                "ASF Runner Verification Pack template",
                ["templates/codex_tasks/asf_runner_verification_pack_template.md"],
            ),
            (
                "ASF Codex Report Intake template",
                ["templates/codex_tasks/asf_codex_report_intake_template.md"],
            ),
            (
                "ASF Human-Gated Closure Pack template",
                ["templates/codex_tasks/asf_human_gated_closure_pack_template.md"],
            ),
            (
                "ASF Human Approval Gate template",
                ["templates/codex_tasks/asf_human_approval_gate_template.md"],
            ),
            (
                "ASF Codex Invocation Dry Run template",
                ["templates/codex_tasks/asf_codex_invocation_dry_run_template.md"],
            ),
            (
                "ASF Codex Read-Only Invocation template",
                ["templates/codex_tasks/asf_codex_readonly_invocation_template.md"],
            ),
            (
                "ASF Codex Invocation Result Capture template",
                ["templates/codex_tasks/asf_codex_invocation_result_capture_template.md"],
            ),
            (
                "ASF Codex Read-Only Safety Gate template",
                ["templates/codex_tasks/asf_codex_readonly_safety_gate_template.md"],
            ),
            (
                "ASF Codex Read-Only Repeatable Trial template",
                ["templates/codex_tasks/asf_codex_readonly_repeatable_trial_template.md"],
            ),
            (
                "ASF Codex Read-Only Trial Compare template",
                ["templates/codex_tasks/asf_codex_readonly_trial_compare_template.md"],
            ),
            (
                "ASF OpenAI API Adapter template",
                ["templates/codex_tasks/asf_openai_api_adapter_template.md"],
            ),
            (
                "ASF OpenAI API Adapter Live Boundary Credential Gate template",
                ["templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md"],
            ),
            (
                "ASF OpenAI API Adapter First Controlled Live Smoke Test template",
                ["templates/codex_tasks/asf_openai_api_live_smoke_test_template.md"],
            ),
            (
                "STEP 540 OpenAI controlled live execution pack PowerShell template",
                ["templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1"],
            ),
            (
                "PowerShell command pack template README",
                ["templates/pwsh_command_pack/README.md"],
            ),
            (
                "PowerShell command pack skill draft",
                ["templates/pwsh_command_pack/as-common-pwsh-command-pack-SKILL.md"],
            ),
            (
                "PowerShell command pack installable skill export",
                ["templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md"],
            ),
            (
                "PowerShell command pack skill installer",
                ["scripts/install_pwsh_command_pack_skill.py"],
            ),
            (
                "ASF Dry-run Loop Runner examples",
                ["examples/dry_run_loop/step_0580_simulated_request.json"],
            ),
            (
                "ASF Risk Classifier Dry-run Integration examples",
                ["examples/dry_run_loop/step_0610_code_change_request.json"],
            ),
            (
                "ASF Stable PowerShell Publish Runner config",
                ["examples/publish_step/0590_publish_config.example.json"],
            ),
            (
                "ASF Risk Classifier examples",
                ["examples/risk_classifier/"],
            ),
            (
                "ASF Gate Decision Report examples",
                ["examples/gate_decision/"],
            ),
            (
                "ASF Verification Profile Selector examples",
                ["examples/verification_profiles/"],
            ),
            (
                "ASF Publish Config Generator examples",
                ["examples/publish_config_generator/"],
            ),
        ],
    )


def check_developer_onboarding(root: Path) -> list[HealthIssue]:
    return check_required_fragments(
        root=root,
        area="developer onboarding",
        relative_path="docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md",
        requirements=[
            ("Quickstart", ["Quickstart"]),
            ("Codex", ["Codex"]),
            ("Alberto", ["Alberto"]),
            ("Lite Mode", ["Lite Mode"]),
            ("Strict Mode", ["Strict Mode"]),
            ("Verification Gate", ["Verification Gate"]),
            ("Release Smoke Workflow", ["Release Smoke Workflow"]),
            ("Lifecycle Checklist", ["Lifecycle Checklist"]),
            ("git status command", ["git status --short"]),
            ("PR checks command", ["gh pr checks --watch"]),
            (
                "Codex report is not main merge",
                ["report Codex non equivale a merge su `main`", "report Codex non equivale a merge su main"],
            ),
        ],
    )


def check_lifecycle_checklist(root: Path) -> list[HealthIssue]:
    return check_required_fragments(
        root=root,
        area="lifecycle checklist",
        relative_path="docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md",
        requirements=[
            ("git status command", ["git status --short"]),
            ("git diff check command", ["git diff --check"]),
            ("pytest command", ["python -m pytest"]),
            ("commit step", ["commit"]),
            ("push step", ["push"]),
            ("PR step", ["PR"]),
            ("merge step", ["merge"]),
            ("main branch", ["main"]),
            ("Codex does not commit", ["Codex non fa commit"]),
            ("Codex does not push", ["Codex non fa push"]),
            ("Codex does not open PR", ["Codex non apre PR"]),
            ("Codex does not merge", ["Codex non fa merge"]),
            (
                "Codex report is not main merge",
                ["report Codex non equivale a merge su `main`", "report Codex non equivale a merge su main"],
            ),
        ],
    )


def forbidden_script_patterns() -> list[str]:
    return [
        "git " + "commit",
        "git " + "push",
        "gh pr " + "create",
        "gh pr " + "merge",
        "gh " + "release",
        "git " + "merge",
        "git " + "reset --hard",
        "git " + "clean",
        "Set-" + "ExecutionPolicy",
        "setx " + "PATH",
    ]


def check_script_safety(root: Path) -> list[HealthIssue]:
    scripts = [
        "scripts/generate_task_packet.py",
        "scripts/generate_task_packet.ps1",
        "scripts/smoke_prompt_packet_release.ps1",
        "scripts/show_workflow_status.py",
        "scripts/check_workflow_health.py",
        "scripts/asf_next_step.py",
        "scripts/asf_codex_report_intake.py",
        "scripts/asf_generate_closure_pack.py",
        "scripts/asf_human_approval_gate.py",
        "scripts/asf_codex_invocation_dry_run.py",
        "scripts/asf_codex_readonly_invoke.py",
        "scripts/asf_codex_readonly_repeatable_trial.py",
        "scripts/asf_codex_result_capture.py",
        "scripts/asf_codex_readonly_safety_gate.py",
        "scripts/asf_codex_readonly_trial_compare.py",
        "scripts/asf_openai_api_adapter.py",
        "scripts/asf_openai_controlled_live_execution_pack.py",
        "scripts/asf_dry_run_loop_runner.py",
        "scripts/asf_publish_step.ps1",
        "scripts/asf_publish_config_generator.py",
        "scripts/asf_risk_classifier.py",
        "scripts/asf_gate_decision_report.py",
        "scripts/asf_verification_profile_selector.py",
        "scripts/asf_step_state_machine.py",
        "scripts/asf_e2e_mvp_smoke.py",
        "scripts/asf_motor_run_manifest.py",
        "scripts/migrate_artifact_names_4digit.py",
    ]
    patterns = forbidden_script_patterns()
    issues: list[HealthIssue] = []

    for relative_path in scripts:
        path = root / relative_path
        if not path.is_file():
            issues.append(
                HealthIssue(
                    area="script safety scan",
                    path=relative_path,
                    requirement="script exists",
                    suggestion="Restore or create the script before scanning it.",
                )
            )
            continue

        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern.casefold() in text.casefold():
                issues.append(
                    HealthIssue(
                        area="script safety scan",
                        path=relative_path,
                        requirement=f"forbidden pattern absent: {pattern}",
                        suggestion="Remove the dangerous command from operational scripts.",
                    )
                )
    return issues


def print_area(name: str, issues: list[HealthIssue]) -> None:
    status = "PASS" if not issues else "FAIL"
    print(f"* {name}: {status}")


def print_issues(issues: list[HealthIssue]) -> None:
    if not issues:
        return

    print()
    print("Failures:")
    for issue in issues:
        print(f"- area: {issue.area}")
        print(f"  file: {issue.path}")
        print(f"  missing: {issue.requirement}")
        print(f"  suggestion: {issue.suggestion}")


def main() -> int:
    root = repo_root()
    checks = [
        ("files", check_files(root)),
        ("project workflow index", check_project_workflow_index(root)),
        ("developer onboarding", check_developer_onboarding(root)),
        ("lifecycle checklist", check_lifecycle_checklist(root)),
        ("script safety scan", check_script_safety(root)),
    ]

    print("Workflow Health Check")
    print()

    all_issues: list[HealthIssue] = []
    for name, issues in checks:
        print_area(name, issues)
        all_issues.extend(issues)

    print_issues(all_issues)
    print()

    if all_issues:
        print("Workflow Health Check FAILED")
        return EXIT_FAILURE

    print("Workflow Health Check PASSED")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
