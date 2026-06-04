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
MODES = ("preview", "execute-readonly")


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    status: str
    recent_commits: str

    @property
    def working_tree_state(self) -> str:
        return "CLEAN" if not self.status else "DIRTY"


@dataclass(frozen=True)
class ApprovalGate:
    path: Path | None
    status: str
    content: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare or execute a human-approved Codex invocation in read-only sandbox.",
    )
    parser.add_argument("--mode", default="preview", choices=MODES, help="Default: preview.")
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--branch", required=True, help="Expected target branch.")
    parser.add_argument("--handoff-path", required=True, help="Path to codex_handoff.md.")
    parser.add_argument("--approval-gate", help="Path to human_approval_gate.md.")
    parser.add_argument(
        "--output-dir",
        default="tmp/asf_codex_readonly_invocation",
        help="Output base directory.",
    )
    parser.add_argument("--codex-command", default="codex", help="Codex command name or path. Default: codex.")
    parser.add_argument("--confirm-readonly-execution", help="Required only for execute-readonly mode.")
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
        recent_commits=results["recent_commits"],
    )


def parse_approval_status(content: str) -> str:
    lowered = content.casefold()
    if re.search(r"\bno-go\b|\bno go\b", lowered, flags=re.IGNORECASE):
        return "NO-GO"
    if re.search(r"\bhold\b", lowered, flags=re.IGNORECASE):
        return "HOLD"
    if re.search(r"\bwarning\b", lowered, flags=re.IGNORECASE):
        return "WARNING"
    if re.search(r"\bgo\b", lowered, flags=re.IGNORECASE):
        return "GO"
    return "UNKNOWN"


def read_approval_gate(path_value: str | None, root: Path, *, required: bool) -> ApprovalGate:
    if not path_value:
        if required:
            raise InputError("--approval-gate is required in execute-readonly mode.")
        return ApprovalGate(path=None, status="NOT PROVIDED", content="")

    path = resolve_path(path_value, base=root)
    if not path.is_file():
        if required:
            raise InputError(f"--approval-gate does not exist or is not a file: {path}")
        return ApprovalGate(path=path, status="MISSING", content="")

    content = path.read_text(encoding="utf-8", errors="replace")
    return ApprovalGate(path=path, status=parse_approval_status(content), content=content)


def powershell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def build_preview_command(*, codex_command: str, handoff_path: Path) -> str:
    handoff = powershell_single_quote(str(handoff_path))
    cleaned_command = codex_command.strip() or "codex"
    if cleaned_command == "codex":
        return f"Get-Content -Raw {handoff} | codex exec --sandbox read-only -"
    return f"Get-Content -Raw {handoff} | & {powershell_single_quote(cleaned_command)} exec --sandbox read-only -"


def build_exec_command(*, codex_command: str) -> list[str]:
    return [codex_command, "exec", "--sandbox", "read-only", "-"]


def command_for_report(command: list[str]) -> str:
    return " ".join(command)


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def build_preview_markdown(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    handoff_path: Path,
    approval: ApprovalGate,
    snapshot: GitSnapshot,
    preview_command: str,
) -> str:
    approval_path = str(approval.path) if approval.path else "(not provided)"
    return f"""# ASF Codex Read-Only Invocation Preview

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- step: `{args.step.strip()}`
- branch: `{args.branch.strip()}`
- handoff-path: `{handoff_path}`
- approval gate: `{approval_path}`
- approval status: `{approval.status}`
- target current branch: `{snapshot.branch}`
- target working tree: `{snapshot.working_tree_state}`
- status: `PREVIEW ONLY`

## Target Git status

```text
{markdown_block(snapshot.status)}
```

## Target recent commits

```text
{markdown_block(snapshot.recent_commits)}
```

## Command preview

This command was generated as text only. Codex was not executed.

```powershell
{preview_command}
```

## Stop conditions

- Missing target repository or missing `.git`.
- Missing handoff file.
- Missing approval gate in execute-readonly mode.
- Human Approval Gate is not `GO`.
- Target working tree is not `CLEAN`.
- Confirmation token is missing or invalid.
- Local Codex command is unavailable in execute-readonly mode.
- Any request to perform commit, push, PR, merge, GitHub changes, CI changes, dependency changes, hook changes or secret changes.

## Execute-readonly instructions

Execution is disabled by default. To run a future read-only invocation, use `--mode execute-readonly` and provide:

```text
--confirm-readonly-execution {CONFIRM_TOKEN}
```

The execution path uses only the read-only Codex sandbox and saves stdout, stderr, exit code and result report under this output directory.

## Not executed

- Codex was not executed.
- The PowerShell preview was not executed.
- No repository target was modified by this preview script.
- No commit, push, PR, merge or GitHub operation was performed.
"""


def build_preview_ps1(*, preview_command: str) -> str:
    return f"""# ASF Codex Read-Only Command Preview
# PREVIEW ONLY.
# DO NOT RUN WITHOUT ALBERTO APPROVAL.
# Generated for review; not executed by ASF.
# Codex was not executed when this file was generated.
#
# Future read-only command preview:
# {preview_command}
"""


def build_result_markdown(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    handoff_path: Path,
    approval: ApprovalGate,
    command: list[str],
    stdout_path: Path,
    stderr_path: Path,
    exit_code_path: Path,
    exit_code: int,
    before: GitSnapshot,
    after: GitSnapshot,
) -> str:
    classification = "PASS" if exit_code == 0 and after.working_tree_state == "CLEAN" else "FAIL"
    approval_path = str(approval.path) if approval.path else "(not provided)"
    return f"""# ASF Codex Read-Only Invocation Result

## Summary

- project-name: `{args.project_name.strip()}`
- repository target: `{target_repo}`
- step: `{args.step.strip()}`
- branch target: `{args.branch.strip()}`
- handoff-path: `{handoff_path}`
- approval gate: `{approval_path}`
- approval status: `{approval.status}`
- command executed: `{command_for_report(command)}`
- exit code: `{exit_code}`
- stdout path: `{stdout_path}`
- stderr path: `{stderr_path}`
- exit code path: `{exit_code_path}`
- classification: `{classification}`

## Working tree before

- branch: `{before.branch}`
- working tree: `{before.working_tree_state}`

```text
{markdown_block(before.status)}
```

## Working tree after

- branch: `{after.branch}`
- working tree: `{after.working_tree_state}`

```text
{markdown_block(after.status)}
```

## Recent commits after

```text
{markdown_block(after.recent_commits)}
```

## Safety note

This read-only invocation should not modify the repository target. If the working tree after execution is `DIRTY`, this result is classified as `FAIL`.

## Not performed

- No commit, push, PR or merge was performed.
- No GitHub operation was performed.
- No target branch was created by this script.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_preview(args: argparse.Namespace, root: Path, target_repo: Path, handoff_path: Path) -> int:
    snapshot = read_git_snapshot(target_repo)
    approval = read_approval_gate(args.approval_gate, root, required=False)
    preview_command = build_preview_command(codex_command=args.codex_command, handoff_path=handoff_path)

    out_dir = output_step_dir(args, root)
    markdown_path = out_dir / "readonly_invocation_preview.md"
    preview_path = out_dir / "codex_readonly_command_preview.ps1"

    write_text(
        markdown_path,
        build_preview_markdown(
            args=args,
            target_repo=target_repo,
            handoff_path=handoff_path,
            approval=approval,
            snapshot=snapshot,
            preview_command=preview_command,
        ),
    )
    write_text(preview_path, build_preview_ps1(preview_command=preview_command))

    print(f"Read-only invocation preview generated: {markdown_path}")
    print(f"Codex read-only command preview generated: {preview_path}")
    print("Codex was not executed.")
    return EXIT_SUCCESS


def require_execute_gate(args: argparse.Namespace, root: Path, target_repo: Path) -> ApprovalGate:
    if args.confirm_readonly_execution != CONFIRM_TOKEN:
        raise InputError(f"--confirm-readonly-execution must be {CONFIRM_TOKEN!r} in execute-readonly mode.")

    approval = read_approval_gate(args.approval_gate, root, required=True)
    if approval.status != "GO":
        raise InputError(f"approval gate must be GO for execute-readonly mode; found {approval.status}.")

    snapshot = read_git_snapshot(target_repo)
    if snapshot.working_tree_state != "CLEAN":
        raise InputError("target working tree must be CLEAN for execute-readonly mode.")

    return approval


def run_execute_readonly(args: argparse.Namespace, root: Path, target_repo: Path, handoff_path: Path) -> int:
    approval = require_execute_gate(args, root, target_repo)
    codex_command = args.codex_command.strip() or "codex"
    resolved_codex = shutil.which(codex_command)
    if resolved_codex is None:
        raise InputError(f"Codex command not found: {codex_command}")

    command = build_exec_command(codex_command=resolved_codex)
    before = read_git_snapshot(target_repo)
    handoff_text = handoff_path.read_text(encoding="utf-8", errors="replace")
    result = subprocess.run(
        command,
        cwd=target_repo,
        input=handoff_text,
        text=True,
        capture_output=True,
        check=False,
    )
    after = read_git_snapshot(target_repo)

    out_dir = output_step_dir(args, root)
    stdout_path = out_dir / "stdout.txt"
    stderr_path = out_dir / "stderr.txt"
    exit_code_path = out_dir / "exit_code.txt"
    result_path = out_dir / "codex_readonly_invocation_result.md"

    write_text(stdout_path, result.stdout)
    write_text(stderr_path, result.stderr)
    write_text(exit_code_path, f"{result.returncode}\n")
    write_text(
        result_path,
        build_result_markdown(
            args=args,
            target_repo=target_repo,
            handoff_path=handoff_path,
            approval=approval,
            command=command,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            exit_code_path=exit_code_path,
            exit_code=result.returncode,
            before=before,
            after=after,
        ),
    )

    print(f"Codex read-only invocation result generated: {result_path}")
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0 and after.working_tree_state == "CLEAN":
        return EXIT_SUCCESS
    return EXIT_RUNTIME_ERROR


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    validate_step(args.step)
    validate_branch(args.branch)
    target_repo = resolve_target_repo(args.repo_path, root)
    handoff_path = resolve_handoff(args.handoff_path, root)

    if args.mode == "preview":
        return run_preview(args, root, target_repo, handoff_path)
    return run_execute_readonly(args, root, target_repo, handoff_path)


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
