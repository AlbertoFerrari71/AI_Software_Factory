from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

SANDBOX_VALUES = ("read-only", "workspace-write-preview")


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    status: str
    diff_stat: str
    recent_commits: str

    @property
    def working_tree_state(self) -> str:
        return "CLEAN" if not self.status else "DIRTY"


@dataclass(frozen=True)
class ApprovalGate:
    path: Path | None
    status: str
    content: str
    do_not_run: bool
    reason: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a dry-run Codex invocation preview pack without running Codex.",
    )
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--branch", required=True, help="Expected working branch.")
    parser.add_argument("--handoff-path", required=True, help="Path to codex_handoff.md.")
    parser.add_argument("--approval-gate", help="Optional path to human_approval_gate.md.")
    parser.add_argument(
        "--sandbox",
        default="read-only",
        choices=SANDBOX_VALUES,
        help="Proposed sandbox: read-only or workspace-write-preview. Default: read-only.",
    )
    parser.add_argument("--output-dir", default="tmp/asf_codex_invocation", help="Output base directory.")
    return parser.parse_args(argv)


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "project"


def output_step_dir(args: argparse.Namespace, root: Path) -> Path:
    base = resolve_path(args.output_dir, base=root)
    return base / safe_path_component(args.project_name) / f"step_{safe_path_component(args.step)}"


def validate_step(step: str) -> str:
    cleaned = step.strip()
    if not cleaned.isdigit() or int(cleaned) <= 0:
        raise InputError("--step must be a positive numeric value.")
    return cleaned


def validate_branch(branch: str) -> str:
    cleaned = branch.strip()
    if not cleaned:
        raise InputError("--branch must not be empty.")
    if re.search(r"\s", cleaned):
        raise InputError("--branch must not contain spaces.")
    return cleaned


def resolve_target_repo(path_value: str, root: Path) -> Path:
    path = resolve_path(path_value, base=root)
    if not path.exists():
        raise InputError(f"--repo-path does not exist: {path}")
    if not path.is_dir():
        raise InputError(f"--repo-path is not a directory: {path}")
    if not (path / ".git").exists():
        raise InputError(f"--repo-path is not a Git repository with .git: {path}")
    return path


def resolve_handoff(path_value: str, root: Path) -> Path:
    path = resolve_path(path_value, base=root)
    if not path.is_file():
        raise InputError(f"--handoff-path does not exist or is not a file: {path}")
    return path


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def read_git_snapshot(repo: Path) -> GitSnapshot:
    commands = {
        "branch": ["git", "branch", "--show-current"],
        "status": ["git", "status", "--short"],
        "diff_stat": ["git", "--no-pager", "diff", "--stat"],
        "recent_commits": ["git", "--no-pager", "log", "--oneline", "--max-count=10"],
    }
    results: dict[str, str] = {}
    for key, command in commands.items():
        result = run_command(command, cwd=repo)
        if result.returncode != 0:
            raise InputError(f"unable to read Git {key}: {result.stderr.strip() or result.stdout.strip()}")
        results[key] = result.stdout.strip()
    return GitSnapshot(
        branch=results["branch"] or "(detached or unavailable)",
        status=results["status"],
        diff_stat=results["diff_stat"],
        recent_commits=results["recent_commits"],
    )


def parse_approval_status(content: str) -> str:
    lowered = content.casefold()
    if "no-go" in lowered:
        return "NO-GO"
    if re.search(r"\bhold\b", lowered, flags=re.IGNORECASE):
        return "HOLD"
    if re.search(r"\bwarning\b", lowered, flags=re.IGNORECASE):
        return "WARNING"
    if re.search(r"\bgo\b", lowered, flags=re.IGNORECASE):
        return "GO"
    return "UNKNOWN"


def read_approval_gate(path_value: str | None, root: Path) -> ApprovalGate:
    if not path_value:
        return ApprovalGate(
            path=None,
            status="NOT PROVIDED",
            content="",
            do_not_run=True,
            reason="No human approval gate was provided.",
        )

    path = resolve_path(path_value, base=root)
    if not path.is_file():
        return ApprovalGate(
            path=path,
            status="MISSING",
            content="",
            do_not_run=True,
            reason="Human approval gate path was provided but the file is missing.",
        )

    content = path.read_text(encoding="utf-8", errors="replace")
    status = parse_approval_status(content)
    do_not_run = status in {"HOLD", "NO-GO", "MISSING", "UNKNOWN"}
    reason = "Approval gate allows preview review only."
    if status in {"HOLD", "NO-GO"}:
        reason = f"Approval gate status is {status}."
    elif status == "UNKNOWN":
        reason = "Approval gate status could not be parsed."
    return ApprovalGate(path=path, status=status, content=content, do_not_run=do_not_run, reason=reason)


def powershell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def codex_sandbox_value(sandbox: str) -> str:
    if sandbox == "workspace-write-preview":
        return "workspace-write"
    return "read-only"


def build_preview_command(handoff_path: Path, sandbox: str) -> str:
    handoff = powershell_single_quote(str(handoff_path))
    return f"Get-Content -Raw {handoff} | codex exec --sandbox {codex_sandbox_value(sandbox)} -"


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def do_not_run_banner(approval: ApprovalGate) -> str:
    if approval.do_not_run:
        return "DO NOT RUN - manual review required before any future Codex invocation."
    return "DRY RUN ONLY - do not run without Alberto approval."


def build_markdown(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    handoff_path: Path,
    approval: ApprovalGate,
    snapshot: GitSnapshot,
    preview_command: str,
) -> str:
    approval_path = str(approval.path) if approval.path else "(not provided)"
    banner = do_not_run_banner(approval)

    return f"""# ASF Codex Invocation Dry Run Pack

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- step: `{args.step.strip()}`
- branch: `{args.branch.strip()}`
- sandbox proposed: `{args.sandbox}`
- approval status: `{approval.status}`
- approval gate: `{approval_path}`
- handoff-path: `{handoff_path}`
- status: `{banner}`

## Git snapshot target

- current branch: `{snapshot.branch}`
- working tree: `{snapshot.working_tree_state}`

Diff stat:

```text
{markdown_block(snapshot.diff_stat)}
```

Recent commits:

```text
{markdown_block(snapshot.recent_commits)}
```

## Command preview

This command is a text preview only. It was not executed by ASF Runner.

```powershell
{preview_command}
```

If the local Codex CLI version does not accept stdin with `-`, this preview must be verified manually in a future read-only prototype step.

## Approval state interpretation

- Approval status: `{approval.status}`
- Run status: `{banner}`
- Reason: {approval.reason}

HOLD or NO-GO in the approval gate means the preview pack can be reviewed, but the command must not be run.

## Risks

- Codex invocation would share the handoff content with the local Codex process.
- `workspace-write-preview` maps to future `workspace-write` execution and is not approved by this step.
- A wrong branch, dirty target repo, missing handoff, broad scope or sensitive file mention must stop execution.
- This step does not verify whether the local Codex CLI accepts the preview syntax.

## Stop conditions

- Human approval gate is HOLD or NO-GO.
- Human approval gate is missing or cannot be parsed.
- Target repo is dirty and not explicitly accepted in a future gate.
- Branch is not coherent with the step.
- Task packet is not Strict PASS.
- Scope is too broad.
- Sensitive files, secrets or `.env` files are involved.
- Codex command syntax has not been manually verified.

## Manual instructions

- Review `codex_invocation_dry_run.md`.
- Review `codex_exec_preview.ps1`.
- Do not run the preview without Alberto approval.
- Keep this pack under `tmp/` and ignored by Git.
- Do not use this pack to commit, push, open PR, merge or modify GitHub.

## Not executed

- ASF Runner did not invoke Codex.
- ASF Runner did not execute the PowerShell preview.
- ASF Runner did not modify the target repository.
- ASF Runner did not create branch, commit, push, PR or merge.
"""


def build_preview_ps1(
    *,
    args: argparse.Namespace,
    handoff_path: Path,
    approval: ApprovalGate,
    preview_command: str,
) -> str:
    banner = do_not_run_banner(approval)
    return f"""# ASF Codex Invocation Dry Run Preview
# DRY RUN ONLY.
# MANUAL REVIEW REQUIRED.
# DO NOT RUN WITHOUT ALBERTO APPROVAL.
# Not executed by ASF Runner.
# This file prints the future preview command and intentionally does not invoke Codex.

$ErrorActionPreference = "Stop"

$ProjectName = {powershell_single_quote(args.project_name.strip())}
$Step = {powershell_single_quote(args.step.strip())}
$Branch = {powershell_single_quote(args.branch.strip())}
$SandboxPreview = {powershell_single_quote(args.sandbox)}
$ApprovalStatus = {powershell_single_quote(approval.status)}
$HandoffPath = {powershell_single_quote(str(handoff_path))}
$RunStatus = {powershell_single_quote(banner)}

$PreviewCommand = @'
{preview_command}
'@

Write-Host "ASF Codex Invocation Dry Run Preview"
Write-Host "Project: $ProjectName"
Write-Host "Step: $Step"
Write-Host "Branch: $Branch"
Write-Host "Sandbox preview: $SandboxPreview"
Write-Host "Approval status: $ApprovalStatus"
Write-Host "Run status: $RunStatus"
Write-Host ""
Write-Host "Preview command, not executed:"
Write-Host $PreviewCommand
Write-Host ""
Write-Host "This preview did not invoke Codex and must not be used without Alberto approval."
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    validate_step(args.step)
    validate_branch(args.branch)
    target_repo = resolve_target_repo(args.repo_path, root)
    handoff_path = resolve_handoff(args.handoff_path, root)
    snapshot = read_git_snapshot(target_repo)
    approval = read_approval_gate(args.approval_gate, root)
    preview_command = build_preview_command(handoff_path, args.sandbox)

    out_dir = output_step_dir(args, root)
    markdown_path = out_dir / "codex_invocation_dry_run.md"
    preview_path = out_dir / "codex_exec_preview.ps1"

    write_text(
        markdown_path,
        build_markdown(
            args=args,
            target_repo=target_repo,
            handoff_path=handoff_path,
            approval=approval,
            snapshot=snapshot,
            preview_command=preview_command,
        ),
    )
    write_text(
        preview_path,
        build_preview_ps1(args=args, handoff_path=handoff_path, approval=approval, preview_command=preview_command),
    )

    print(f"Codex invocation dry-run pack generated: {markdown_path}")
    print(f"Codex exec preview generated: {preview_path}")
    print("Codex was not invoked.")
    return EXIT_SUCCESS


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
