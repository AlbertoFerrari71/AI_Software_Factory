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
        "scripts/generate_task_packet.py",
        "scripts/generate_task_packet.ps1",
        "scripts/smoke_prompt_packet_release.ps1",
        "scripts/validate_task_packet.py",
        "scripts/verify.ps1",
        "scripts/git/check_soft_guardrails.ps1",
        "templates/codex_tasks/codex_task_packet_template.md",
        "templates/codex_tasks/prompt_packet_lifecycle_checklist.md",
        "templates/codex_tasks/step_closure_report_template.md",
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
            ("generate task packet script", ["scripts/generate_task_packet.py"]),
            ("task packet validator script", ["scripts/validate_task_packet.py"]),
            ("verification gate script", ["scripts/verify.ps1"]),
            ("soft guardrails check script", ["scripts/git/check_soft_guardrails.ps1"]),
            ("Workflow Health Check document", ["docs/35_WORKFLOW_HEALTH_CHECK.md"]),
            ("Workflow Health Check script", ["scripts/check_workflow_health.py"]),
            ("Workflow Quick Reference document", ["docs/36_WORKFLOW_QUICK_REFERENCE.md"]),
            ("Step Closure Report document", ["docs/37_STEP_CLOSURE_REPORT.md"]),
            ("Step Closure Report template", ["templates/codex_tasks/step_closure_report_template.md"]),
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
        "scripts/check_workflow_health.py",
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
