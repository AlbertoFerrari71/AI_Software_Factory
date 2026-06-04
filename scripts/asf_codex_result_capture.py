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

EXPECTED_OUTPUTS = (
    "stdout.txt",
    "stderr.txt",
    "exit_code.txt",
    "codex_readonly_invocation_result.md",
)
PREVIEW_OUTPUTS = (
    "readonly_invocation_preview.md",
    "codex_readonly_command_preview.ps1",
)


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
class InvocationFiles:
    invocation_dir: Path
    present: tuple[str, ...]
    missing: tuple[str, ...]
    preview_present: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str
    result_markdown: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize a saved ASF Codex read-only invocation result without invoking Codex.",
    )
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--invocation-dir", required=True, help="Directory produced by asf_codex_readonly_invoke.py.")
    parser.add_argument("--output-dir", default="tmp/asf_codex_result_capture", help="Output base directory.")
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


def resolve_target_repo(path_value: str, root: Path) -> Path:
    path = resolve_path(path_value, base=root)
    if not path.exists():
        raise InputError(f"--repo-path does not exist: {path}")
    if not path.is_dir():
        raise InputError(f"--repo-path is not a directory: {path}")
    if not (path / ".git").exists():
        raise InputError(f"--repo-path is not a Git repository with .git: {path}")
    return path


def resolve_invocation_dir(path_value: str, root: Path) -> Path:
    path = resolve_path(path_value, base=root)
    if not path.exists():
        raise InputError(f"--invocation-dir does not exist: {path}")
    if not path.is_dir():
        raise InputError(f"--invocation-dir is not a directory: {path}")
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


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""


def parse_exit_code(text: str) -> int | None:
    cleaned = text.lstrip("\ufeff").strip()
    if not cleaned:
        return None
    try:
        return int(cleaned.splitlines()[0].strip())
    except ValueError:
        return None


def read_invocation_files(invocation_dir: Path) -> InvocationFiles:
    present = tuple(name for name in EXPECTED_OUTPUTS if (invocation_dir / name).is_file())
    missing = tuple(name for name in EXPECTED_OUTPUTS if name not in present)
    preview_present = tuple(name for name in PREVIEW_OUTPUTS if (invocation_dir / name).is_file())

    stdout = read_file(invocation_dir / "stdout.txt")
    stderr = read_file(invocation_dir / "stderr.txt")
    result_markdown = read_file(invocation_dir / "codex_readonly_invocation_result.md")
    exit_code = parse_exit_code(read_file(invocation_dir / "exit_code.txt"))

    return InvocationFiles(
        invocation_dir=invocation_dir,
        present=present,
        missing=missing,
        preview_present=preview_present,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        result_markdown=result_markdown,
    )


def summarize_text(value: str, *, max_lines: int = 12, max_chars: int = 1200) -> str:
    if not value.strip():
        return "(none)"
    lines = value.strip().splitlines()[:max_lines]
    summary = "\n".join(lines)
    if len(summary) > max_chars:
        summary = summary[:max_chars].rstrip() + "\n..."
    return summary


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def bullets(values: tuple[str, ...] | list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- none"


def classify(files: InvocationFiles, snapshot: GitSnapshot) -> str:
    if snapshot.working_tree_state == "DIRTY":
        return "FAIL"
    if files.exit_code is not None and files.exit_code != 0:
        return "FAIL"
    if files.exit_code == 0 and not files.missing:
        return "PASS"
    return "WARNING"


def next_actions(classification: str, files: InvocationFiles) -> list[str]:
    if classification == "PASS":
        return [
            "Review stdout, stderr and the invocation result report.",
            "Run the read-only safety gate before any future design for broader execution.",
            "Keep all generated outputs under ignored tmp paths.",
        ]
    if classification == "WARNING":
        actions = [
            "Review missing outputs before treating this as an execution result.",
            "If this was only preview, do not infer that Codex ran.",
            "Regenerate or rerun only with an explicit human-approved read-only gate.",
        ]
        if files.preview_present:
            actions.append("Preview artifacts are present; this may be a preview-only pack.")
        return actions
    return [
        "Stop and inspect the failed read-only invocation result.",
        "Do not proceed toward broader execution design.",
        "Resolve nonzero exit code or dirty working tree evidence first.",
    ]


def build_capture_report(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    files: InvocationFiles,
    snapshot: GitSnapshot,
    classification: str,
) -> str:
    exit_code = "(missing)" if files.exit_code is None else str(files.exit_code)
    return f"""# ASF Codex Invocation Result Capture

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- step: `{args.step.strip()}`
- invocation-dir: `{files.invocation_dir}`
- classification: `{classification}`
- exit code: `{exit_code}`
- target branch: `{snapshot.branch}`
- target working tree: `{snapshot.working_tree_state}`

## Outputs present

{bullets(files.present)}

## Outputs missing

{bullets(files.missing)}

## Preview outputs present

{bullets(files.preview_present)}

## stdout summary

```text
{summarize_text(files.stdout)}
```

## stderr summary

```text
{summarize_text(files.stderr)}
```

## Target Git status

```text
{markdown_block(snapshot.status)}
```

## Target recent commits

```text
{markdown_block(snapshot.recent_commits)}
```

## Classification criteria

- `PASS`: exit code is `0`, required outputs are present, and target working tree is `CLEAN`.
- `WARNING`: outputs are incomplete or only preview artifacts are present, with no fail signal detected.
- `FAIL`: exit code is nonzero or target working tree is `DIRTY` after read-only execution.

## Next actions

{bullets(next_actions(classification, files))}

## Limits

- This capture did not invoke Codex.
- This capture did not modify the target repository.
- This capture did not perform commit, push, PR, merge or GitHub operations.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    validate_step(args.step)
    target_repo = resolve_target_repo(args.repo_path, root)
    invocation_dir = resolve_invocation_dir(args.invocation_dir, root)
    files = read_invocation_files(invocation_dir)
    snapshot = read_git_snapshot(target_repo)
    classification = classify(files, snapshot)

    output_path = output_step_dir(args, root) / "codex_result_capture.md"
    write_text(
        output_path,
        build_capture_report(
            args=args,
            target_repo=target_repo,
            files=files,
            snapshot=snapshot,
            classification=classification,
        ),
    )

    print(f"Codex result capture generated: {output_path}")
    print(f"Classification: {classification}")
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
