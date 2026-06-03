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


@dataclass(frozen=True)
class SectionCheck:
    name: str
    present: bool


EXPECTED_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("STEP ESEGUITO", ("STEP ESEGUITO", "Step eseguito")),
    ("STATO", ("STATO", "Stato step")),
    ("BRANCH CORRENTE", ("BRANCH CORRENTE", "Branch corrente")),
    ("FILE CREATI", ("FILE CREATI", "File creati")),
    ("FILE MODIFICATI", ("FILE MODIFICATI", "File modificati")),
    ("COMANDI ESEGUITI", ("COMANDI ESEGUITI", "Comandi eseguiti")),
    ("VERIFICHE NON ESEGUITE", ("VERIFICHE NON ESEGUITE", "Verifiche non eseguite")),
    ("RISCHI / NOTE", ("RISCHI / NOTE", "Rischi / note", "Rischi")),
    ("CONFERME VINCOLI", ("CONFERME VINCOLI", "Vincoli rispettati")),
    ("PROSSIMO STEP", ("PROSSIMO STEP", "Prossimo step")),
    ("RIEPILOGO FINALE", ("RIEPILOGO FINALE", "Riepilogo finale")),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a saved Codex final report and produce a local intake report without changing the target repo.",
    )
    parser.add_argument("--report-path", required=True, help="Path to the saved Codex Markdown report.")
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--step", required=True, help="Step number.")
    parser.add_argument("--output-dir", default="tmp/asf_codex_intake", help="Output base directory.")
    parser.add_argument("--main-branch", default="main", help="Target repository main branch. Default: main.")
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


def resolve_report(path_value: str, root: Path) -> Path:
    path = resolve_path(path_value, base=root)
    if not path.is_file():
        raise InputError(f"--report-path does not exist or is not a file: {path}")
    return path


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


def contains_any(text: str, candidates: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(candidate.casefold() in lowered for candidate in candidates)


def inspect_sections(report_text: str) -> list[SectionCheck]:
    return [SectionCheck(name=name, present=contains_any(report_text, aliases)) for name, aliases in EXPECTED_SECTIONS]


def classify_intake(section_checks: list[SectionCheck]) -> str:
    step_present = next(check.present for check in section_checks if check.name == "STEP ESEGUITO")
    if not step_present:
        return "FAIL"
    if all(check.present for check in section_checks):
        return "PASS"
    return "WARNING"


def markdown_block(value: str) -> str:
    return value if value.strip() else "(none)"


def output_step_dir(args: argparse.Namespace, root: Path, step: str) -> Path:
    base = resolve_path(args.output_dir, base=root)
    return base / safe_path_component(args.project_name) / f"step_{step}"


def build_intake_report(
    *,
    args: argparse.Namespace,
    report_path: Path,
    repo_path: Path,
    step: str,
    section_checks: list[SectionCheck],
    intake_status: str,
    snapshot: GitSnapshot,
) -> str:
    found = [check.name for check in section_checks if check.present]
    missing = [check.name for check in section_checks if not check.present]
    warnings: list[str] = []
    if missing:
        warnings.append("Some expected Codex report sections are missing.")
    if snapshot.status:
        warnings.append("Target working tree is DIRTY and needs human review.")
    if intake_status == "FAIL":
        warnings.append("STEP ESEGUITO section was not found; do not treat this report as ready.")

    found_text = "\n".join(f"- {item}" for item in found) or "- none"
    missing_text = "\n".join(f"- {item}" for item in missing) or "- none"
    warnings_text = "\n".join(f"- {item}" for item in warnings) or "- none"

    return f"""# ASF Codex Report Intake

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{repo_path}`
- main-branch: `{args.main_branch.strip() or "main"}`
- step: `{step}`
- report-path: `{report_path}`
- intake status: `{intake_status}`

## Sections found

{found_text}

## Sections missing

{missing_text}

## Target Git status

- branch corrente target: `{snapshot.branch or "(none)"}`
- working tree: `{snapshot.working_tree_state}`

Working tree detail:

```text
{markdown_block(snapshot.status)}
```

Diff stat:

```text
{markdown_block(snapshot.diff_stat)}
```

Ultimi commit:

```text
{markdown_block(snapshot.recent_commits)}
```

## Warnings

{warnings_text}

## Prossime verifiche consigliate

- Review manuale del report Codex.
- Verifica diff e scope.
- Verifica vincoli e forbidden actions.
- Eseguire test e Verification Gate manualmente.
- Usare closure pack solo come guida human-gated.

## Nota

Questo intake e' un controllo locale read-only. Non equivale ad approval, non sostituisce review Alberto/ChatGPT e non chiude lo step.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    step = validate_step(args.step)
    report_path = resolve_report(args.report_path, root)
    target_repo = resolve_target_repo(args.repo_path, root)
    report_text = report_path.read_text(encoding="utf-8")
    section_checks = inspect_sections(report_text)
    intake_status = classify_intake(section_checks)
    snapshot = read_git_snapshot(target_repo)
    out_dir = output_step_dir(args, root, step)
    output_path = out_dir / "codex_report_intake.md"

    write_text(
        output_path,
        build_intake_report(
            args=args,
            report_path=report_path,
            repo_path=target_repo,
            step=step,
            section_checks=section_checks,
            intake_status=intake_status,
            snapshot=snapshot,
        ),
    )

    print(f"Codex report intake generated: {output_path}")
    print(f"Intake status: {intake_status}")
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
