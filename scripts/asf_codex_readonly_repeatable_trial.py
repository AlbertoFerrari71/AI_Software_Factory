from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

CONFIRM_TOKEN = "YES_I_APPROVE_READONLY_CODEX_EXECUTION"
MODES = ("prepare-only", "run-readonly-if-safe")
WORKSPACE_WRITE = "workspace" + "-write"
DANGER_FULL_ACCESS = "danger" + "-full-access"


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class TrialPaths:
    base: Path
    target_repo: Path
    inputs: Path
    approval: Path
    invocation: Path
    capture: Path
    safety: Path
    reports: Path


@dataclass(frozen=True)
class CommandRun:
    label: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "PASS" if self.returncode == 0 else f"FAILED_EXIT_{self.returncode}"


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    status: str
    recent_commits: str

    @property
    def working_tree_state(self) -> str:
        return "CLEAN" if not self.status else "DIRTY"


@dataclass(frozen=True)
class TrialReport:
    trial_name: str
    step: str
    mode: str
    target_repo: Path
    approval_status: str
    invocation_status: str
    capture_status: str
    safety_gate_status: str
    codex_availability: str
    exit_code: str
    stdout_path: str
    stderr_path: str
    final_working_tree: str
    classification: str
    command_runs: list[CommandRun]
    next_actions: list[str]
    notes: list[str]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare or run a repeatable ASF Codex read-only invocation trial on a synthetic tmp repository.",
    )
    parser.add_argument("--mode", choices=MODES, default="prepare-only", help="Default: prepare-only.")
    parser.add_argument("--trial-name", required=True, help="Safe trial name: letters, numbers, dash, underscore.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument(
        "--output-dir",
        default="tmp/asf_codex_readonly_repeatable_trials",
        help="Output base directory.",
    )
    parser.add_argument("--confirm-readonly-execution", help="Required only for run-readonly-if-safe.")
    parser.add_argument("--codex-command", default="codex", help="Codex command name or path. Default: codex.")
    return parser.parse_args(argv)


def validate_trial_name(value: str) -> str:
    cleaned = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", cleaned):
        raise InputError("--trial-name may contain only letters, numbers, dash and underscore.")
    return cleaned


def validate_step(value: str) -> str:
    cleaned = value.strip()
    if not cleaned.isdigit() or int(cleaned) <= 0:
        raise InputError("--step must be a positive numeric value.")
    return cleaned


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "trial"


def trial_paths(args: argparse.Namespace, root: Path) -> TrialPaths:
    base = resolve_path(args.output_dir, base=root) / safe_path_component(args.trial_name)
    return TrialPaths(
        base=base,
        target_repo=base / "target_repo",
        inputs=base / "inputs",
        approval=base / "approval",
        invocation=base / "invocation",
        capture=base / "capture",
        safety=base / "safety",
        reports=base / "reports",
    )


def trial_project_name(trial_name: str) -> str:
    return f"ASF_ReadOnly_Trial_{safe_path_component(trial_name)}"


def trial_branch(step: str, trial_name: str) -> str:
    return f"step-{step}-{safe_path_component(trial_name)}"


def step_dir(base: Path, project_name: str, step: str) -> Path:
    return base / safe_path_component(project_name) / f"step_{safe_path_component(step)}"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def run_command(command: list[str], *, cwd: Path, label: str) -> CommandRun:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return CommandRun(label=label, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)


def run_git(repo: Path, args: list[str], *, label: str) -> CommandRun:
    return run_command(["git", *args], cwd=repo, label=label)


def require_git() -> None:
    if shutil.which("git") is None:
        raise InputError("git executable is required to create the synthetic target repository.")


def ensure_directories(paths: TrialPaths) -> None:
    for path in [
        paths.target_repo,
        paths.inputs,
        paths.approval,
        paths.invocation,
        paths.capture,
        paths.safety,
        paths.reports,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def synthetic_readme(step: str, trial_name: str) -> str:
    return f"""# ASF Synthetic Read-Only Trial Target

This repository is synthetic and lives under ignored `tmp/` output.

- Step: {step}
- Trial: {trial_name}
- Purpose: stable read-only Codex invocation diagnostics.

No external repository, real data or production configuration is represented here.
"""


def synthetic_notes() -> str:
    return """# Notes

The expected task is analysis only.

The trial target exists to verify preview, explicit approval, read-only execution evidence, capture and safety gate behavior.
"""


def synthetic_demo() -> str:
    return """demo record
status: synthetic
scope: read-only analysis target
"""


def write_synthetic_target_files(paths: TrialPaths, *, step: str, trial_name: str) -> None:
    write_text(paths.target_repo / "README.md", synthetic_readme(step, trial_name))
    write_text(paths.target_repo / "docs" / "NOTES.md", synthetic_notes())
    write_text(paths.target_repo / "src" / "demo.txt", synthetic_demo())


def branch_exists(repo: Path, branch: str) -> bool:
    result = run_git(repo, ["rev-parse", "--verify", branch], label="git branch exists")
    return result.returncode == 0


def has_head(repo: Path) -> bool:
    result = run_git(repo, ["rev-parse", "--verify", "HEAD"], label="git has head")
    return result.returncode == 0


def read_git_snapshot(repo: Path) -> GitSnapshot:
    branch = run_git(repo, ["branch", "--show-current"], label="git branch")
    status = run_git(repo, ["status", "--short"], label="git status")
    recent = run_git(repo, ["--no-pager", "log", "--oneline", "--max-count=10"], label="git log")
    if branch.returncode != 0:
        raise InputError(branch.stderr.strip() or branch.stdout.strip() or "unable to read target branch")
    if status.returncode != 0:
        raise InputError(status.stderr.strip() or status.stdout.strip() or "unable to read target status")
    recent_text = recent.stdout.strip() if recent.returncode == 0 else "(no commits)"
    return GitSnapshot(
        branch=branch.stdout.strip() or "(detached or unavailable)",
        status=status.stdout.strip(),
        recent_commits=recent_text,
    )


def ensure_branch(repo: Path, branch: str) -> CommandRun:
    snapshot = read_git_snapshot(repo)
    if snapshot.branch == branch:
        return CommandRun("target branch already selected", 0, snapshot.branch, "")
    if snapshot.working_tree_state != "CLEAN":
        return CommandRun("target branch switch skipped", 2, "", "target working tree is not clean")
    if branch_exists(repo, branch):
        return run_git(repo, ["switch", branch], label="target branch switch")
    result = run_git(repo, ["switch", "-c", branch], label="target branch create")
    if result.returncode != 0:
        return run_git(repo, ["checkout", "-b", branch], label="target branch create fallback")
    return result


def initialize_target_repo(paths: TrialPaths, *, step: str, trial_name: str, branch: str) -> list[CommandRun]:
    require_git()
    paths.target_repo.mkdir(parents=True, exist_ok=True)
    command_runs: list[CommandRun] = []

    if not (paths.target_repo / ".git").exists():
        init = run_git(paths.target_repo, ["init", "-b", branch], label="target git init")
        if init.returncode != 0:
            init = run_git(paths.target_repo, ["init"], label="target git init fallback")
        command_runs.append(init)
        if init.returncode != 0:
            raise InputError(init.stderr.strip() or init.stdout.strip() or "unable to initialize target repo")

    command_runs.append(run_git(paths.target_repo, ["config", "user.email", "asf-readonly-trial@example.invalid"], label="target git config email"))
    command_runs.append(run_git(paths.target_repo, ["config", "user.name", "ASF Read-Only Trial"], label="target git config name"))
    write_synthetic_target_files(paths, step=step, trial_name=trial_name)

    if not has_head(paths.target_repo):
        command_runs.append(run_git(paths.target_repo, ["add", "README.md", "docs/NOTES.md", "src/demo.txt"], label="target baseline add"))
        commit = run_git(paths.target_repo, ["commit", "-m", "synthetic read-only trial baseline"], label="target baseline commit")
        command_runs.append(commit)
        if commit.returncode != 0:
            raise InputError(commit.stderr.strip() or commit.stdout.strip() or "unable to create target baseline")

    branch_run = ensure_branch(paths.target_repo, branch)
    command_runs.append(branch_run)
    if branch_run.returncode != 0:
        raise InputError(branch_run.stderr.strip() or branch_run.stdout.strip() or "unable to select target branch")

    return command_runs


def build_handoff(*, step: str, trial_name: str) -> str:
    return f"""# ASF Codex Read-Only Repeatable Trial Handoff

## Scope

Analyze this synthetic repository and return a short report.

## Trial metadata

- step: {step}
- trial-name: {trial_name}

## Hard constraints

- Do not modify files.
- Do not create files.
- Do not create branches.
- Do not run any Git publication action.
- Do not open pull requests.
- Do not call GitHub.
- Do not use {WORKSPACE_WRITE}.
- Do not use {DANGER_FULL_ACCESS}.
- Use read-only analysis only.

## Requested output

Return:

- repository purpose in two or three lines;
- files inspected;
- any read-only observations;
- confirmation that no target file modification was requested.
"""


def write_inputs(paths: TrialPaths, *, step: str, trial_name: str) -> Path:
    handoff = paths.inputs / "handoff.md"
    write_text(handoff, build_handoff(step=step, trial_name=trial_name))
    write_text(
        paths.inputs / "codex_report_intake.md",
        """# Synthetic Codex Report Intake

## Summary

- intake status: `PASS`
- scope: synthetic repeatable read-only trial
- evidence: prepared for approval gate
""",
    )
    write_text(
        paths.inputs / "verification_pack.md",
        """# Synthetic Verification Pack

## Summary

- result: PASS
- target: synthetic temporary repository
- mode: read-only diagnostic trial

## Checks

- target repository exists
- target working tree expected CLEAN
- no remote operation requested
""",
    )
    write_text(
        paths.inputs / "closure_pack.md",
        """# Synthetic Closure Pack

## Summary

- status: PASS
- publication: manual review only
- remote operations: none
""",
    )
    return handoff


def parse_labeled_value(text: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"(?im)^\s*-\s*{re.escape(label)}\s*:\s*`?([^`\n]+)`?\s*$"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        pattern = rf"(?im)^\s*{re.escape(label)}\s*:\s*`?([^`\n]+)`?\s*$"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "UNKNOWN"


def parse_approval_status(path: Path) -> str:
    return parse_labeled_value(read_text(path), ["decisione", "decision"]).upper()


def parse_capture_status(path: Path) -> str:
    return parse_labeled_value(read_text(path), ["classification", "classificazione"]).upper()


def parse_safety_status(path: Path) -> str:
    return parse_labeled_value(read_text(path), ["decisione", "decision"]).upper()


def read_exit_code(path: Path) -> str:
    text = read_text(path).strip()
    return text if text else "(not present)"


def command_status(run: CommandRun, ok_status: str, fail_status: str) -> str:
    return ok_status if run.returncode == 0 else f"{fail_status}_{run.returncode}"


def run_approval_gate(
    *,
    root: Path,
    paths: TrialPaths,
    project_name: str,
    step: str,
    branch: str,
) -> tuple[CommandRun, Path, str]:
    report_path = step_dir(paths.approval, project_name, step) / "human_approval_gate.md"
    command = [
        sys.executable,
        str(root / "scripts" / "asf_human_approval_gate.py"),
        "--project-name",
        project_name,
        "--repo-path",
        str(paths.target_repo),
        "--step",
        step,
        "--branch",
        branch,
        "--codex-report-intake",
        str(paths.inputs / "codex_report_intake.md"),
        "--verification-pack",
        str(paths.inputs / "verification_pack.md"),
        "--closure-pack",
        str(paths.inputs / "closure_pack.md"),
        "--output-dir",
        str(paths.approval),
    ]
    run = run_command(command, cwd=root, label="human approval gate")
    status = parse_approval_status(report_path) if report_path.is_file() else "ERROR"
    return run, report_path, status


def run_preview(
    *,
    root: Path,
    paths: TrialPaths,
    project_name: str,
    step: str,
    branch: str,
    handoff: Path,
    approval_report: Path,
    codex_command: str,
) -> tuple[CommandRun, Path, str]:
    command = [
        sys.executable,
        str(root / "scripts" / "asf_codex_readonly_invoke.py"),
        "--mode",
        "preview",
        "--project-name",
        project_name,
        "--repo-path",
        str(paths.target_repo),
        "--step",
        step,
        "--branch",
        branch,
        "--handoff-path",
        str(handoff),
        "--approval-gate",
        str(approval_report),
        "--output-dir",
        str(paths.invocation),
        "--codex-command",
        codex_command,
    ]
    run = run_command(command, cwd=root, label="readonly invocation preview")
    status = command_status(run, "PREVIEW_CREATED", "PREVIEW_FAILED")
    return run, step_dir(paths.invocation, project_name, step), status


def write_codex_not_available_outputs(invocation_dir: Path, codex_command: str) -> None:
    write_text(invocation_dir / "stdout.txt", "")
    write_text(invocation_dir / "stderr.txt", f"Codex command is not available: {codex_command}\n")
    write_text(invocation_dir / "exit_code.txt", "\n")
    write_text(
        invocation_dir / "codex_readonly_invocation_result.md",
        f"""# ASF Codex Read-Only Invocation Result

## Summary

- classification: `CODEX_NOT_AVAILABLE`
- command: `{codex_command}`
- sandbox: `read-only`

Codex was not executed because the command was not available in the local environment.
The synthetic target repository was not modified.
""",
    )


def run_execute_readonly(
    *,
    root: Path,
    paths: TrialPaths,
    project_name: str,
    step: str,
    branch: str,
    handoff: Path,
    approval_report: Path,
    codex_command: str,
) -> CommandRun:
    command = [
        sys.executable,
        str(root / "scripts" / "asf_codex_readonly_invoke.py"),
        "--mode",
        "execute-readonly",
        "--project-name",
        project_name,
        "--repo-path",
        str(paths.target_repo),
        "--step",
        step,
        "--branch",
        branch,
        "--handoff-path",
        str(handoff),
        "--approval-gate",
        str(approval_report),
        "--output-dir",
        str(paths.invocation),
        "--confirm-readonly-execution",
        CONFIRM_TOKEN,
        "--codex-command",
        codex_command,
    ]
    return run_command(command, cwd=root, label="readonly execution")


def run_capture(
    *,
    root: Path,
    paths: TrialPaths,
    project_name: str,
    step: str,
    invocation_dir: Path,
) -> tuple[CommandRun, Path, str]:
    report_path = step_dir(paths.capture, project_name, step) / "codex_result_capture.md"
    command = [
        sys.executable,
        str(root / "scripts" / "asf_codex_result_capture.py"),
        "--project-name",
        project_name,
        "--repo-path",
        str(paths.target_repo),
        "--step",
        step,
        "--invocation-dir",
        str(invocation_dir),
        "--output-dir",
        str(paths.capture),
    ]
    run = run_command(command, cwd=root, label="result capture")
    status = parse_capture_status(report_path) if report_path.is_file() else command_status(run, "CAPTURE_CREATED", "CAPTURE_FAILED")
    return run, report_path, status


def run_safety_gate(
    *,
    root: Path,
    paths: TrialPaths,
    project_name: str,
    step: str,
    capture_report: Path,
) -> tuple[CommandRun, Path, str]:
    report_path = step_dir(paths.safety, project_name, step) / "readonly_safety_gate.md"
    command = [
        sys.executable,
        str(root / "scripts" / "asf_codex_readonly_safety_gate.py"),
        "--project-name",
        project_name,
        "--repo-path",
        str(paths.target_repo),
        "--step",
        step,
        "--result-capture",
        str(capture_report),
        "--output-dir",
        str(paths.safety),
    ]
    run = run_command(command, cwd=root, label="readonly safety gate")
    status = parse_safety_status(report_path) if report_path.is_file() else command_status(run, "SAFETY_CREATED", "SAFETY_FAILED")
    return run, report_path, status


def codex_available(codex_command: str) -> bool:
    cleaned = codex_command.strip() or "codex"
    return shutil.which(cleaned) is not None


def stderr_is_nonempty(stderr_path: Path) -> bool:
    return bool(read_text(stderr_path).strip())


def output_looks_incomplete(stdout_path: Path, stderr_path: Path) -> bool:
    combined = f"{read_text(stdout_path)}\n{read_text(stderr_path)}".casefold()
    fragments = [
        "could not complete",
        "output incompleto",
        "incomplete",
        "spawn setup refresh",
        "not available",
        "errore sandbox",
        "sandbox error",
    ]
    return any(fragment in combined for fragment in fragments)


def next_actions_for(classification: str) -> list[str]:
    if classification == "PREPARED_ONLY":
        return [
            "Review the generated handoff, approval gate and preview.",
            f"Run again with --mode run-readonly-if-safe and --confirm-readonly-execution {CONFIRM_TOKEN} only when ready.",
        ]
    if classification == "READONLY_EXECUTED_CLEAN":
        return [
            "Review stdout, stderr, result capture and safety gate.",
            "Use the comparison script if multiple trials are available.",
            f"Do not treat the clean read-only result as authorization for {WORKSPACE_WRITE}.",
        ]
    if classification == "READONLY_EXECUTED_WARNING":
        return [
            "Review stderr and incomplete-output evidence.",
            "Compare this trial with another run before any broader design decision.",
            f"Keep {WORKSPACE_WRITE} unauthorized.",
        ]
    if classification == "CODEX_NOT_AVAILABLE":
        return [
            "Verify the local Codex CLI command outside this script.",
            "Repeat the same trial name or a new trial when Codex is available.",
            "Use the generated report as an environment diagnostic, not as a failed target modification.",
        ]
    if classification == "BLOCKED_BY_APPROVAL":
        return [
            "Review Human Approval Gate output.",
            "Do not execute Codex until the gate is GO.",
        ]
    if classification == "BLOCKED_BY_DIRTY_TARGET":
        return [
            "Inspect the synthetic target repository status.",
            "Do not execute Codex while the target is DIRTY.",
        ]
    return [
        "Inspect command outputs and generated reports.",
        "Stop before any broader execution design.",
    ]


def build_report(report: TrialReport) -> str:
    commands = "\n".join(
        f"- {run.label}: `{run.status}`" for run in report.command_runs
    ) or "- none"
    notes = "\n".join(f"- {note}" for note in report.notes) or "- none"
    next_actions = "\n".join(f"- {action}" for action in report.next_actions) or "- none"
    return f"""# ASF Codex Read-Only Repeatable Trial Report

## Summary

- trial-name: `{report.trial_name}`
- step: `{report.step}`
- mode: `{report.mode}`
- target repo path: `{report.target_repo}`
- approval status: `{report.approval_status}`
- invocation status: `{report.invocation_status}`
- capture status: `{report.capture_status}`
- safety gate status: `{report.safety_gate_status}`
- Codex availability: `{report.codex_availability}`
- exit code: `{report.exit_code}`
- stdout path: `{report.stdout_path}`
- stderr path: `{report.stderr_path}`
- working tree finale target: `{report.final_working_tree}`
- classification: `{report.classification}`

## Command outcomes

{commands}

## Notes

{notes}

## Safety boundaries

- sandbox requested: `read-only`
- {WORKSPACE_WRITE} authorization: `not authorized`
- {DANGER_FULL_ACCESS} authorization: `not authorized`
- external target repositories modified: `no`
- GitHub operations performed: `no`
- automatic publication actions performed: `no`

## Next actions

{next_actions}
"""


def write_report(paths: TrialPaths, report: TrialReport) -> Path:
    report_path = paths.reports / "repeatable_trial_report.md"
    write_text(report_path, build_report(report))
    return report_path


def prepare_common(args: argparse.Namespace, root: Path) -> tuple[TrialPaths, str, str, Path, list[CommandRun]]:
    trial_name = validate_trial_name(args.trial_name)
    step = validate_step(args.step)
    paths = trial_paths(args, root)
    branch = trial_branch(step, trial_name)
    ensure_directories(paths)
    command_runs = initialize_target_repo(paths, step=step, trial_name=trial_name, branch=branch)
    handoff = write_inputs(paths, step=step, trial_name=trial_name)
    return paths, trial_project_name(trial_name), branch, handoff, command_runs


def run_prepare_only(args: argparse.Namespace, root: Path) -> int:
    paths, project_name, branch, handoff, command_runs = prepare_common(args, root)
    step = validate_step(args.step)
    approval_run, approval_report, approval_status = run_approval_gate(
        root=root,
        paths=paths,
        project_name=project_name,
        step=step,
        branch=branch,
    )
    preview_run, _, invocation_status = run_preview(
        root=root,
        paths=paths,
        project_name=project_name,
        step=step,
        branch=branch,
        handoff=handoff,
        approval_report=approval_report,
        codex_command=args.codex_command,
    )
    command_runs.extend([approval_run, preview_run])
    final_snapshot = read_git_snapshot(paths.target_repo)
    report = TrialReport(
        trial_name=args.trial_name,
        step=step,
        mode=args.mode,
        target_repo=paths.target_repo,
        approval_status=approval_status,
        invocation_status=invocation_status,
        capture_status="NOT_RUN",
        safety_gate_status="NOT_RUN",
        codex_availability="NOT_CHECKED",
        exit_code="(not present)",
        stdout_path="(not present)",
        stderr_path="(not present)",
        final_working_tree=final_snapshot.working_tree_state,
        classification="PREPARED_ONLY",
        command_runs=command_runs,
        next_actions=next_actions_for("PREPARED_ONLY"),
        notes=["Codex was not executed in prepare-only mode."],
    )
    report_path = write_report(paths, report)
    print(f"Repeatable trial prepared: {report_path}")
    print("Classification: PREPARED_ONLY")
    return EXIT_SUCCESS


def run_readonly_if_safe(args: argparse.Namespace, root: Path) -> int:
    if args.confirm_readonly_execution != CONFIRM_TOKEN:
        raise InputError(f"--confirm-readonly-execution must be {CONFIRM_TOKEN!r} in run-readonly-if-safe mode.")

    paths, project_name, branch, handoff, command_runs = prepare_common(args, root)
    step = validate_step(args.step)
    approval_run, approval_report, approval_status = run_approval_gate(
        root=root,
        paths=paths,
        project_name=project_name,
        step=step,
        branch=branch,
    )
    preview_run, invocation_dir, preview_status = run_preview(
        root=root,
        paths=paths,
        project_name=project_name,
        step=step,
        branch=branch,
        handoff=handoff,
        approval_report=approval_report,
        codex_command=args.codex_command,
    )
    command_runs.extend([approval_run, preview_run])

    classification = "FAILED"
    invocation_status = preview_status
    capture_status = "NOT_RUN"
    safety_status = "NOT_RUN"
    availability = "NOT_CHECKED"
    exit_code = "(not present)"
    stdout_path = str(invocation_dir / "stdout.txt") if (invocation_dir / "stdout.txt").is_file() else "(not present)"
    stderr_path = str(invocation_dir / "stderr.txt") if (invocation_dir / "stderr.txt").is_file() else "(not present)"
    notes: list[str] = []

    if approval_status != "GO":
        classification = "BLOCKED_BY_APPROVAL"
        notes.append(f"Approval gate blocked execution with status {approval_status}.")
    else:
        before_execution = read_git_snapshot(paths.target_repo)
        if before_execution.working_tree_state != "CLEAN":
            classification = "BLOCKED_BY_DIRTY_TARGET"
            notes.append("Target working tree was not CLEAN before execution.")
        elif not codex_available(args.codex_command):
            availability = "CODEX_NOT_AVAILABLE"
            write_codex_not_available_outputs(invocation_dir, args.codex_command)
            stdout_path = str(invocation_dir / "stdout.txt")
            stderr_path = str(invocation_dir / "stderr.txt")
            invocation_status = "CODEX_NOT_AVAILABLE"
            classification = "CODEX_NOT_AVAILABLE"
            capture_run, capture_report, capture_status = run_capture(
                root=root,
                paths=paths,
                project_name=project_name,
                step=step,
                invocation_dir=invocation_dir,
            )
            safety_run, _, safety_status = run_safety_gate(
                root=root,
                paths=paths,
                project_name=project_name,
                step=step,
                capture_report=capture_report,
            )
            command_runs.extend([capture_run, safety_run])
            notes.append("Codex command was not available; no Codex execution was attempted.")
        else:
            availability = "AVAILABLE"
            execute_run = run_execute_readonly(
                root=root,
                paths=paths,
                project_name=project_name,
                step=step,
                branch=branch,
                handoff=handoff,
                approval_report=approval_report,
                codex_command=args.codex_command,
            )
            command_runs.append(execute_run)
            invocation_status = command_status(execute_run, "EXECUTE_READONLY_COMPLETED", "EXECUTE_READONLY_FAILED")
            stdout_file = invocation_dir / "stdout.txt"
            stderr_file = invocation_dir / "stderr.txt"
            exit_file = invocation_dir / "exit_code.txt"
            stdout_path = str(stdout_file) if stdout_file.is_file() else "(not present)"
            stderr_path = str(stderr_file) if stderr_file.is_file() else "(not present)"
            exit_code = read_exit_code(exit_file)
            capture_run, capture_report, capture_status = run_capture(
                root=root,
                paths=paths,
                project_name=project_name,
                step=step,
                invocation_dir=invocation_dir,
            )
            safety_run, _, safety_status = run_safety_gate(
                root=root,
                paths=paths,
                project_name=project_name,
                step=step,
                capture_report=capture_report,
            )
            command_runs.extend([capture_run, safety_run])
            final_state = read_git_snapshot(paths.target_repo).working_tree_state
            if final_state != "CLEAN":
                classification = "FAILED"
                notes.append("Target working tree became DIRTY after read-only execution.")
            elif exit_code != "0":
                classification = "FAILED"
                notes.append("Codex execution did not produce exit code 0.")
            elif safety_status == "WARNING_REVIEW_REQUIRED" or stderr_is_nonempty(stderr_file) or output_looks_incomplete(stdout_file, stderr_file):
                classification = "READONLY_EXECUTED_WARNING"
                notes.append("Execution finished with clean target but warning evidence requires review.")
            else:
                classification = "READONLY_EXECUTED_CLEAN"
                notes.append("Execution finished with exit code 0 and clean target.")

    final_snapshot = read_git_snapshot(paths.target_repo)
    if availability == "NOT_CHECKED" and classification not in {"BLOCKED_BY_APPROVAL", "BLOCKED_BY_DIRTY_TARGET"}:
        availability = "UNKNOWN"
    report = TrialReport(
        trial_name=args.trial_name,
        step=step,
        mode=args.mode,
        target_repo=paths.target_repo,
        approval_status=approval_status,
        invocation_status=invocation_status,
        capture_status=capture_status,
        safety_gate_status=safety_status,
        codex_availability=availability,
        exit_code=exit_code,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        final_working_tree=final_snapshot.working_tree_state,
        classification=classification,
        command_runs=command_runs,
        next_actions=next_actions_for(classification),
        notes=notes,
    )
    report_path = write_report(paths, report)
    print(f"Repeatable trial report generated: {report_path}")
    print(f"Classification: {classification}")
    return EXIT_SUCCESS if classification != "FAILED" else EXIT_RUNTIME_ERROR


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    validate_trial_name(args.trial_name)
    validate_step(args.step)
    if args.mode == "prepare-only":
        return run_prepare_only(args, root)
    return run_readonly_if_safe(args, root)


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
