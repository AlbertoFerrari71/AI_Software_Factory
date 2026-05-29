from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


CENTRAL_DOCUMENTS = [
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
]

MAIN_SCRIPTS = [
    "scripts/asf_next_step.py",
    "scripts/check_workflow_health.py",
    "scripts/show_workflow_status.py",
    "scripts/generate_task_packet.py",
    "scripts/validate_task_packet.py",
    "scripts/verify.ps1",
    "scripts/git/check_soft_guardrails.ps1",
]

CENTRAL_CONFIGS = [
    "config/asf_project_profiles.json",
]

NEXT_CHECKS = [
    "python scripts/check_workflow_health.py",
    "python -m pytest",
    r"pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1",
    r"pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\git\check_soft_guardrails.ps1",
]


def repo_root() -> Path:
    return Path.cwd()


def is_repo_root(root: Path) -> bool:
    required = [
        root / "README.md",
        root / "CHANGELOG.md",
        root / "docs",
        root / "scripts",
    ]
    return all(path.exists() for path in required)


def run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def path_status(root: Path, relative_paths: list[str]) -> tuple[list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for relative_path in relative_paths:
        if (root / relative_path).is_file():
            present.append(relative_path)
        else:
            missing.append(relative_path)
    return present, missing


def print_path_section(title: str, present: list[str], missing: list[str]) -> None:
    print(title)
    for relative_path in present:
        print(f"- OK {relative_path}")
    for relative_path in missing:
        print(f"- MISSING {relative_path}")
    print()


def main() -> int:
    root = repo_root()

    print("Workflow Status Dashboard")
    print("Repository: AI Software Factory")
    print(f"Root: {root}")
    print()

    if not is_repo_root(root):
        print("ERROR: run this command from the repository root.")
        return EXIT_FAILURE

    branch_code, branch, branch_error = run_git(root, ["branch", "--show-current"])
    status_code, status_text, status_error = run_git(root, ["status", "--short"])
    log_code, log_text, log_error = run_git(root, ["--no-pager", "log", "--oneline", "--max-count=5"])

    if branch_code != 0 or status_code != 0 or log_code != 0:
        print("ERROR: unable to read local Git status.")
        for error in [branch_error, status_error, log_error]:
            if error:
                print(f"- {error}")
        return EXIT_FAILURE

    working_tree = "CLEAN" if not status_text else "DIRTY"

    print(f"Branch: {branch or '(detached or unavailable)'}")
    print(f"Working tree: {working_tree}")
    if status_text:
        print("Working tree details:")
        for line in status_text.splitlines():
            print(f"- {line}")
    print()

    print("Recent commits:")
    if log_text:
        for line in log_text.splitlines():
            print(f"- {line}")
    else:
        print("- none")
    print()

    docs_present, docs_missing = path_status(root, CENTRAL_DOCUMENTS)
    configs_present, configs_missing = path_status(root, CENTRAL_CONFIGS)
    scripts_present, scripts_missing = path_status(root, MAIN_SCRIPTS)

    print_path_section("Central documents:", docs_present, docs_missing)
    print_path_section("Central configs:", configs_present, configs_missing)
    print_path_section("Main scripts:", scripts_present, scripts_missing)

    print("Next suggested local checks:")
    for command in NEXT_CHECKS:
        print(f"- {command}")
    print()

    print("Note: this dashboard does not replace Verification Gate, Workflow Health Check, or PR checks.")

    if docs_missing or configs_missing or scripts_missing:
        return EXIT_FAILURE
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
