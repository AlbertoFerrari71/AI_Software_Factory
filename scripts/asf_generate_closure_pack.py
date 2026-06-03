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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a human-gated closure pack without executing the generated commands.",
    )
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--branch", required=True, help="Expected working branch.")
    parser.add_argument("--commit-message", required=True, help="Suggested commit message for manual use.")
    parser.add_argument("--pr-title", required=True, help="Suggested PR title for manual use.")
    parser.add_argument("--pr-body", default="", help="Suggested PR body for manual use.")
    parser.add_argument("--main-branch", default="main", help="Main branch name. Default: main.")
    parser.add_argument("--output-dir", default="tmp/asf_closure_pack", help="Output base directory.")
    return parser.parse_args(argv)


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "project"


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
        raise InputError(f"--repo-path is not a Git repository: {path}")
    return path


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
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
        branch=results["branch"],
        status=results["status"],
        diff_stat=results["diff_stat"],
        recent_commits=results["recent_commits"],
    )


def markdown_block(value: str) -> str:
    return value if value.strip() else "(none)"


def output_step_dir(args: argparse.Namespace, root: Path, step: str) -> Path:
    base = resolve_path(args.output_dir, base=root)
    return base / safe_path_component(args.project_name) / f"step_{step}"


def load_template(root: Path) -> str:
    path = root / "templates" / "codex_tasks" / "asf_human_gated_closure_pack_template.md"
    if not path.is_file():
        raise InputError(f"closure pack template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def build_replacements(args: argparse.Namespace, target_repo: Path, step: str, snapshot: GitSnapshot) -> dict[str, str]:
    pr_body = args.pr_body.strip() or "Manual human-gated closure for the ASF step."
    return {
        "PROJECT_NAME": args.project_name.strip(),
        "REPO_PATH": str(target_repo),
        "STEP": step,
        "BRANCH": args.branch.strip(),
        "MAIN_BRANCH": args.main_branch.strip() or "main",
        "COMMIT_MESSAGE": args.commit_message.strip(),
        "PR_TITLE": args.pr_title.strip(),
        "PR_BODY": pr_body,
        "CURRENT_BRANCH": snapshot.branch or "(none)",
        "WORKING_TREE": snapshot.working_tree_state,
        "WORKING_TREE_DETAIL": markdown_block(snapshot.status),
        "DIFF_STAT": markdown_block(snapshot.diff_stat),
        "RECENT_COMMITS": markdown_block(snapshot.recent_commits),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    step = validate_step(args.step)
    target_repo = resolve_target_repo(args.repo_path, root)
    snapshot = read_git_snapshot(target_repo)
    template = load_template(root)
    output_dir = output_step_dir(args, root, step)
    output_path = output_dir / "closure_pack.md"
    content = render_template(template, build_replacements(args, target_repo, step, snapshot))
    write_text(output_path, content)

    print(f"Closure pack generated: {output_path}")
    print("Generated commands are manual and were not executed.")
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
