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

DECISION_GO = "GO_TO_WORKSPACE_WRITE_DESIGN"
DECISION_WARNING = "WARNING_REVIEW_REQUIRED"
DECISION_HOLD = "HOLD"
DECISION_NO_GO = "NO_GO"


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
class ResultCapture:
    path: Path
    exists: bool
    content: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a Codex read-only invocation capture before any future broader execution design.",
    )
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--result-capture", required=True, help="Path to codex_result_capture.md.")
    parser.add_argument("--output-dir", default="tmp/asf_codex_readonly_safety_gate", help="Output base directory.")
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


def read_result_capture(path_value: str, root: Path) -> ResultCapture:
    path = resolve_path(path_value, base=root)
    if not path.is_file():
        return ResultCapture(path=path, exists=False, content="")
    return ResultCapture(path=path, exists=True, content=path.read_text(encoding="utf-8", errors="replace"))


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


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- none"


def contains_any(text: str, fragments: list[str]) -> bool:
    lowered = text.casefold()
    return any(fragment.casefold() in lowered for fragment in fragments)


def extract_capture_classification(text: str) -> str | None:
    patterns = [
        r"(?im)^\s*-\s*classification\s*:\s*`?([A-Z][A-Z_-]*)`?\s*$",
        r"(?im)^\s*classification\s*:\s*`?([A-Z][A-Z_-]*)`?\s*$",
        r"(?im)^\s*-\s*classificazione\s*:\s*`?([A-Z][A-Z_-]*)`?\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).upper()
    return None


def section_body(text: str, heading: str) -> str:
    pattern = rf"(?ims)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def section_has_nonempty_bullets(text: str, heading: str) -> bool:
    body = section_body(text, heading)
    for line in body.splitlines():
        cleaned = line.strip()
        if not cleaned.startswith("-"):
            continue
        value = cleaned.lstrip("-").strip()
        if value and value.casefold() not in {"none", "(none)", "nessuno", "nessuna"}:
            return True
    return False


def forbidden_action_signals() -> list[str]:
    return [
        "commit automatic",
        "push automatic",
        "merge automatic",
        "pr automatic",
        "pull request automatic",
        "gh pr " + "create",
        "gh pr " + "merge",
        "git " + "push",
        "git " + "commit",
        "git " + "merge",
        "git " + "reset --hard",
        "git " + "clean",
        "force push",
        "workspace" + "-write without gate",
        "workspace" + "-write senza gate",
        "danger" + "-full-access",
        "secret",
        ".env",
        "bypass",
        "scope violation",
        "fuori scope",
        "file vietati",
    ]


def has_pass_capture(text: str) -> bool:
    return extract_capture_classification(text) == "PASS"


def has_warning_capture(text: str) -> bool:
    if extract_capture_classification(text) == "WARNING":
        return True
    if section_has_nonempty_bullets(text, "Outputs missing"):
        return True
    return contains_any(
        text,
        [
            "output incompleto",
            "stderr non vuoto",
            "stderr not empty",
            "review required",
            "chiarimenti",
            "ambiguous",
            "ambiguo",
        ],
    )


def has_fail_capture(text: str) -> bool:
    if extract_capture_classification(text) == "FAIL":
        return True
    return contains_any(
        text,
        [
            "exit code: `1`",
            "exit code nonzero",
            "exit code non zero",
            "working tree: `DIRTY`",
            "target working tree: `DIRTY`",
        ],
    )


def has_modification_signal(text: str) -> bool:
    lowered = text.casefold()
    for line in lowered.splitlines():
        if any(
            skip in line
            for skip in [
                "(none)",
                "none",
                "nessun",
                "nessuna modifica",
                "no file",
                "no files",
                "without file modification",
                "without file modifications",
                "did not modify",
                "does not modify",
                "not modified",
                "not modify",
                "non modifica",
                "non modificato",
            ]
        ):
            continue
        if any(fragment in line for fragment in ["file modified", "files modified", "file modificati", "working tree: `dirty`"]):
            return True
    return False


def classify(capture: ResultCapture, snapshot: GitSnapshot) -> tuple[str, list[str], list[str], list[str]]:
    no_go: list[str] = []
    hold: list[str] = []
    warnings: list[str] = []

    if snapshot.working_tree_state == "DIRTY":
        no_go.append("target working tree is DIRTY after read-only invocation evidence.")

    if not capture.exists:
        hold.append(f"result capture is missing: {capture.path}")
        return DECISION_HOLD, no_go, hold, warnings

    text = capture.content
    if has_fail_capture(text):
        no_go.append("result capture contains FAIL, nonzero exit code or dirty working tree evidence.")
    if has_modification_signal(text):
        no_go.append("result capture indicates file modifications after read-only execution.")
    if contains_any(text, forbidden_action_signals()):
        no_go.append("result capture mentions forbidden action, bypass, secret-like path or out-of-scope execution.")

    if no_go:
        return DECISION_NO_GO, no_go, hold, warnings

    if not has_pass_capture(text):
        if has_warning_capture(text):
            warnings.append("result capture contains warning or incomplete-output evidence.")
        else:
            hold.append("result capture does not provide enough structured PASS evidence.")

    if has_warning_capture(text):
        warnings.append("manual review is required for warning or ambiguous evidence.")

    if hold:
        return DECISION_HOLD, no_go, hold, warnings
    if warnings:
        return DECISION_WARNING, no_go, hold, warnings
    return DECISION_GO, no_go, hold, warnings


def next_actions(decision: str) -> list[str]:
    if decision == DECISION_GO:
        return [
            "Document the read-only trial evidence.",
            "Design a future broader execution step separately, with explicit human approval.",
            "Do not treat this gate as direct authorization for broader execution.",
        ]
    if decision == DECISION_WARNING:
        return [
            "Review warning evidence with Alberto before any future design step.",
            "Clarify incomplete or ambiguous outputs.",
            "Regenerate capture if needed.",
        ]
    if decision == DECISION_HOLD:
        return [
            "Produce or repair the missing result capture evidence.",
            "Rerun result capture before evaluating future broader execution design.",
            "Do not proceed while evidence is insufficient.",
        ]
    return [
        "Stop the progression toward broader execution design.",
        "Resolve fail evidence before any future step.",
        "Do not run broader Codex execution from this result.",
    ]


def build_report(
    *,
    args: argparse.Namespace,
    target_repo: Path,
    capture: ResultCapture,
    snapshot: GitSnapshot,
    decision: str,
    no_go: list[str],
    hold: list[str],
    warnings: list[str],
) -> str:
    evidence: list[str] = []
    evidence.append(f"result capture exists: {capture.exists}")
    evidence.append(f"target branch: {snapshot.branch}")
    evidence.append(f"target working tree: {snapshot.working_tree_state}")
    if capture.exists:
        if has_pass_capture(capture.content):
            evidence.append("result capture PASS evidence detected")
        if has_warning_capture(capture.content):
            evidence.append("result capture WARNING evidence detected")
        if has_fail_capture(capture.content):
            evidence.append("result capture FAIL evidence detected")

    risks = [*no_go, *hold, *warnings]
    if not risks:
        risks = ["No blocking or warning signals were detected by this safety gate."]

    return f"""# ASF Codex Read-Only Safety Gate

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- step: `{args.step.strip()}`
- result-capture: `{capture.path}`
- decisione: `{decision}`
- target branch: `{snapshot.branch}`
- target working tree: `{snapshot.working_tree_state}`

## Evidenze

{bullets(evidence)}

## Rischi

{bullets(risks)}

## Target Git status

```text
{markdown_block(snapshot.status)}
```

## Target recent commits

```text
{markdown_block(snapshot.recent_commits)}
```

## Dettaglio decisione

### NO_GO

{bullets(no_go)}

### HOLD

{bullets(hold)}

### WARNING_REVIEW_REQUIRED

{bullets(warnings)}

## Prossime azioni

{bullets(next_actions(decision))}

## Nota di sicurezza

Questo gate non autorizza direttamente una futura esecuzione piu' ampia. Autorizza al massimo la progettazione di uno step successivo separato, con gate umano, branch dedicato, scope esplicito e test.

## Prossimo step consigliato

430) ASF Codex Read-Only Invocation First Manual Trial, oppure uno step di correzione evidenze se la decisione non e' `{DECISION_GO}`.

## Limiti

- Questo safety gate e' read-only.
- Non invoca Codex.
- Non modifica il repository target.
- Non esegue commit, push, PR, merge o operazioni GitHub.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    validate_step(args.step)
    target_repo = resolve_target_repo(args.repo_path, root)
    capture = read_result_capture(args.result_capture, root)
    snapshot = read_git_snapshot(target_repo)
    decision, no_go, hold, warnings = classify(capture, snapshot)

    output_path = output_step_dir(args, root) / "readonly_safety_gate.md"
    write_text(
        output_path,
        build_report(
            args=args,
            target_repo=target_repo,
            capture=capture,
            snapshot=snapshot,
            decision=decision,
            no_go=no_go,
            hold=hold,
            warnings=warnings,
        ),
    )

    print(f"Read-only safety gate generated: {output_path}")
    print(f"Decision: {decision}")
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
