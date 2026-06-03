from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_RUNTIME_ERROR = 3

DECISION_ORDER = ("GO", "WARNING", "HOLD", "NO-GO")


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
class EvidenceFile:
    label: str
    provided: bool
    path: Path | None
    exists: bool
    content: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a read-only ASF human approval gate report for a target repository.",
    )
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--branch", required=True, help="Expected working branch.")
    parser.add_argument("--main-branch", default="main", help="Main branch name. Default: main.")
    parser.add_argument("--codex-report-intake", help="Optional path to codex_report_intake.md.")
    parser.add_argument("--verification-pack", help="Optional path to verification_pack.md.")
    parser.add_argument("--closure-pack", help="Optional path to closure_pack.md.")
    parser.add_argument("--output-dir", default="tmp/asf_approval_gate", help="Output base directory.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow a dirty target working tree and downgrade that condition to WARNING.",
    )
    parser.add_argument(
        "--require-tests",
        action="store_true",
        help="Require test evidence in provided reports. Default is false.",
    )
    return parser.parse_args(argv)


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "project"


def step_component(step: str) -> str:
    cleaned = safe_path_component(step)
    return f"step_{cleaned or 'invalid'}"


def output_step_dir(args: argparse.Namespace, root: Path) -> Path:
    base = resolve_path(args.output_dir, base=root)
    return base / safe_path_component(args.project_name) / step_component(args.step)


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def resolve_target_repo(path_value: str, root: Path) -> tuple[Path, list[str]]:
    path = resolve_path(path_value, base=root)
    errors: list[str] = []
    if not path.exists():
        errors.append(f"repo-path does not exist: {path}")
    elif not path.is_dir():
        errors.append(f"repo-path is not a directory: {path}")
    elif not (path / ".git").exists():
        errors.append(f"repo-path is not a Git repository with .git: {path}")
    return path, errors


def read_git_snapshot(repo: Path) -> tuple[GitSnapshot | None, list[str]]:
    commands = {
        "branch": ["git", "branch", "--show-current"],
        "status": ["git", "status", "--short"],
        "diff_stat": ["git", "--no-pager", "diff", "--stat"],
        "recent_commits": ["git", "--no-pager", "log", "--oneline", "--max-count=10"],
    }
    results: dict[str, str] = {}
    errors: list[str] = []

    for key, command in commands.items():
        result = run_command(command, cwd=repo)
        if result.returncode != 0:
            errors.append(f"unable to read Git {key}: {result.stderr.strip() or result.stdout.strip()}")
        results[key] = result.stdout.strip()

    if errors:
        return None, errors

    return (
        GitSnapshot(
            branch=results["branch"] or "(detached or unavailable)",
            status=results["status"],
            diff_stat=results["diff_stat"],
            recent_commits=results["recent_commits"],
        ),
        [],
    )


def read_optional_file(label: str, value: str | None, root: Path) -> EvidenceFile:
    if not value:
        return EvidenceFile(label=label, provided=False, path=None, exists=False, content="")

    path = resolve_path(value, base=root)
    if not path.is_file():
        return EvidenceFile(label=label, provided=True, path=path, exists=False, content="")

    return EvidenceFile(
        label=label,
        provided=True,
        path=path,
        exists=True,
        content=path.read_text(encoding="utf-8", errors="replace"),
    )


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def validate_step(step: str) -> tuple[bool, str]:
    cleaned = step.strip()
    if not cleaned.isdigit() or int(cleaned) <= 0:
        return False, "--step must be a positive numeric value."
    return True, ""


def branch_is_coherent(current: str, expected: str) -> bool:
    current_clean = current.strip()
    expected_clean = expected.strip()
    return current_clean == expected_clean


def branch_is_explainable(current: str, expected: str) -> bool:
    current_clean = current.strip().casefold()
    expected_clean = expected.strip().casefold()
    if not current_clean or not expected_clean:
        return False
    return current_clean.startswith(expected_clean) or expected_clean.startswith(current_clean)


def contains_fail_signal(content: str) -> bool:
    fail_patterns = [
        r"intake status:\s*`?FAIL`?",
        r"result:\s*FAIL",
        r"status:\s*FAIL",
        r"decisione:\s*`?NO-GO`?",
        r"decision:\s*`?NO-GO`?",
    ]
    lowered = content.casefold()
    return any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in fail_patterns)


def contains_scope_or_secret_violation(content: str) -> bool:
    lowered = content.casefold()
    direct_signals = [
        "scope vietato rilevato",
        "forbidden scope detected",
        "file sensibili modificati",
        "sensitive files modified",
        "secret modificato",
        "secret modified",
        ".env modificato",
        ".env modified",
        "credential modified",
        "commit diretto su main",
        "direct commit to main",
    ]
    if any(signal in lowered for signal in direct_signals):
        return True

    for line in lowered.splitlines():
        if any(skip in line for skip in ["nessun", "no secret", "not modified"]):
            continue
        if any(token in line for token in ["secret", ".env", "credential", "file sensibili"]):
            if any(action in line for action in ["modificat", "modified", "changed", "toccato"]):
                return True
    return False


def sensitive_path_in_git_text(text: str) -> bool:
    for raw_line in text.splitlines():
        line = raw_line.casefold()
        if ".env.example" in line:
            continue
        patterns = [
            ".env",
            "secrets/",
            "secret/",
            "credentials/",
            ".pem",
            ".key",
            ".p12",
            ".pfx",
            "id_rsa",
        ]
        if any(pattern in line.replace("\\", "/") for pattern in patterns):
            return True
    return False


def tests_documented(evidence_files: list[EvidenceFile]) -> bool:
    combined = "\n".join(evidence.content for evidence in evidence_files if evidence.exists)
    lowered = combined.casefold()
    return any(fragment in lowered for fragment in ["python -m pytest", "pytest", "verify.ps1", "test: pass", "tests: pass"])


def classify(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    repo_errors: list[str],
    snapshot: GitSnapshot | None,
    git_errors: list[str],
    evidence_files: list[EvidenceFile],
) -> tuple[str, list[str], list[str], list[str]]:
    no_go: list[str] = []
    hold: list[str] = []
    warnings: list[str] = []

    step_ok, step_error = validate_step(args.step)
    if not step_ok:
        no_go.append(step_error)

    expected_branch = args.branch.strip()
    main_branch = args.main_branch.strip() or "main"
    if not expected_branch:
        no_go.append("--branch must not be empty.")
    if re.search(r"\s", expected_branch):
        no_go.append("--branch must not contain spaces.")
    if expected_branch == main_branch:
        no_go.append("expected branch is the main branch; direct work on main is not approved.")

    if repo_errors:
        no_go.extend(repo_errors)

    if git_errors:
        no_go.extend(git_errors)

    if snapshot is not None:
        if not branch_is_coherent(snapshot.branch, expected_branch):
            if snapshot.branch == main_branch or snapshot.branch.startswith("("):
                hold.append("current branch is ambiguous or not the expected working branch.")
            elif branch_is_explainable(snapshot.branch, expected_branch):
                warnings.append("current branch differs from expected branch but appears explainable.")
            else:
                hold.append("current branch differs from expected branch and is not explainable.")

        if snapshot.status and not args.allow_dirty:
            no_go.append("target working tree is DIRTY and --allow-dirty was not provided.")
        elif snapshot.status and args.allow_dirty:
            warnings.append("target working tree is DIRTY, accepted because --allow-dirty is active.")

        if sensitive_path_in_git_text(snapshot.status + "\n" + snapshot.diff_stat):
            no_go.append("sensitive or secret-like file path appears in target Git status or diff stat.")

    for evidence in evidence_files:
        if evidence.provided and not evidence.exists:
            hold.append(f"{evidence.label} was requested but is missing: {evidence.path}")
        elif not evidence.provided and evidence.label in {"Codex report intake", "Verification pack"}:
            warnings.append(f"{evidence.label} was not provided.")
        elif not evidence.provided and evidence.label == "Closure pack":
            warnings.append("Closure pack was not provided; final closure evidence is not part of this gate.")
        elif evidence.exists:
            if contains_fail_signal(evidence.content):
                no_go.append(f"{evidence.label} contains FAIL or NO-GO signal.")
            if contains_scope_or_secret_violation(evidence.content):
                no_go.append(f"{evidence.label} mentions a forbidden scope, sensitive file, or direct-main request.")
            if "no checks reported" in evidence.content.casefold() or "pr checks non disponibili" in evidence.content.casefold():
                warnings.append(f"{evidence.label} mentions unavailable PR checks.")
            if "lf/crlf warning" in evidence.content.casefold():
                warnings.append(f"{evidence.label} mentions LF/CRLF warning.")

    if args.require_tests and not tests_documented(evidence_files):
        hold.append("--require-tests is active but test evidence was not documented in provided files.")

    if no_go:
        return "NO-GO", no_go, hold, warnings
    if hold:
        return "HOLD", no_go, hold, warnings
    if warnings:
        return "WARNING", no_go, hold, warnings
    return "GO", no_go, hold, warnings


def evidence_summary(evidence_files: list[EvidenceFile]) -> str:
    lines: list[str] = []
    for evidence in evidence_files:
        if not evidence.provided:
            lines.append(f"- {evidence.label}: not provided")
        elif evidence.exists:
            lines.append(f"- {evidence.label}: present at `{evidence.path}`")
        else:
            lines.append(f"- {evidence.label}: missing at `{evidence.path}`")
    return "\n".join(lines)


def next_actions(decision: str) -> list[str]:
    if decision == "GO":
        return [
            "Alberto reviews this gate report and decides whether to proceed.",
            "Continue only with human-approved manual actions.",
            "Keep Codex invocation disabled unless a future approved step enables it.",
        ]
    if decision == "WARNING":
        return [
            "Review each warning before proceeding.",
            "Document accepted warnings in the next human-gated pack.",
            "Do not treat WARNING as automatic approval.",
        ]
    if decision == "HOLD":
        return [
            "Resolve HOLD items before moving toward invocation preview or closure.",
            "Regenerate missing requested evidence if needed.",
            "Rerun this approval gate after correction.",
        ]
    return [
        "Stop the workflow for this step.",
        "Resolve NO-GO causes before any further action.",
        "Do not run Codex, commit, push, open PR, merge, or close the step.",
    ]


def build_report(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    snapshot: GitSnapshot | None,
    decision: str,
    no_go: list[str],
    hold: list[str],
    warnings: list[str],
    evidence_files: list[EvidenceFile],
) -> str:
    current_branch = snapshot.branch if snapshot else "(unavailable)"
    working_tree = snapshot.working_tree_state if snapshot else "(unavailable)"
    status = snapshot.status if snapshot else ""
    diff_stat = snapshot.diff_stat if snapshot else ""
    recent_commits = snapshot.recent_commits if snapshot else ""

    reasons = [*no_go, *hold, *warnings]
    if not reasons:
        reasons = ["No blocking or warning signals were detected by this read-only gate."]

    return f"""# ASF Human Approval Gate

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- step: `{args.step.strip()}`
- expected branch: `{args.branch.strip()}`
- main branch: `{args.main_branch.strip() or "main"}`
- current branch: `{current_branch}`
- working tree: `{working_tree}`
- decisione: `{decision}`

## Motivazione

{bullets(reasons)}

## Evidenze

### File evidence

{evidence_summary(evidence_files)}

### Git status target

```text
{markdown_block(status)}
```

### Git diff stat target

```text
{markdown_block(diff_stat)}
```

### Ultimi commit target

```text
{markdown_block(recent_commits)}
```

## Dettaglio decisione

### NO-GO

{bullets(no_go)}

### HOLD

{bullets(hold)}

### WARNING

{bullets(warnings)}

## Prossime azioni consigliate

{bullets(next_actions(decision))}

## Limiti

- Questo gate e' read-only.
- Non modifica il repository target.
- Non esegue test.
- Non fa commit, push, PR o merge.
- Non chiama GitHub.
- Non invoca Codex.
- La decisione finale resta di Alberto.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    target_repo, repo_errors = resolve_target_repo(args.repo_path, root)
    snapshot: GitSnapshot | None = None
    git_errors: list[str] = []
    if not repo_errors:
        snapshot, git_errors = read_git_snapshot(target_repo)

    evidence_files = [
        read_optional_file("Codex report intake", args.codex_report_intake, root),
        read_optional_file("Verification pack", args.verification_pack, root),
        read_optional_file("Closure pack", args.closure_pack, root),
    ]
    decision, no_go, hold, warnings = classify(
        args=args,
        target_repo=target_repo,
        repo_errors=repo_errors,
        snapshot=snapshot,
        git_errors=git_errors,
        evidence_files=evidence_files,
    )

    output_dir = output_step_dir(args, root)
    output_path = output_dir / "human_approval_gate.md"
    write_text(
        output_path,
        build_report(
            args=args,
            target_repo=target_repo,
            snapshot=snapshot,
            decision=decision,
            no_go=no_go,
            hold=hold,
            warnings=warnings,
            evidence_files=evidence_files,
        ),
    )

    print(f"Human approval gate generated: {output_path}")
    print(f"Decision: {decision}")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
