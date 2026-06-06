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
        "docs/65_ASF_OPENAI_API_ADAPTER.md",
        "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md",
        "config/asf_project_profiles.json",
        "scripts/asf_openai_api_adapter.py",
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
            ("ASF OpenAI API Adapter", ["ASF OpenAI API Adapter"]),
            (
                "ASF OpenAI API Adapter Live Boundary Credential Gate",
                ["ASF OpenAI API Adapter Live Boundary Credential Gate"],
            ),
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
                "ASF OpenAI API Adapter document",
                ["docs/65_ASF_OPENAI_API_ADAPTER.md"],
            ),
            (
                "ASF OpenAI API Adapter Live Boundary Credential Gate document",
                ["docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md"],
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
