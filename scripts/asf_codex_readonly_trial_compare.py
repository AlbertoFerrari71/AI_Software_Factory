from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedTrial:
    path: Path
    trial_name: str
    classification: str
    approval_status: str
    invocation_status: str
    capture_status: str
    safety_gate_status: str
    codex_availability: str
    exit_code: str
    stderr_or_incomplete: bool


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two or more ASF Codex read-only repeatable trial reports.",
    )
    parser.add_argument("--reports", nargs="+", required=True, help="Repeatable trial report Markdown paths.")
    parser.add_argument(
        "--output-dir",
        default="tmp/asf_codex_readonly_repeatable_trials/comparison",
        help="Output directory.",
    )
    return parser.parse_args(argv)


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_value(text: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"(?im)^\s*-\s*{re.escape(label)}\s*:\s*`?([^`\n]+)`?\s*$"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "UNKNOWN"


def has_stderr_or_incomplete_evidence(text: str) -> bool:
    lowered = text.casefold()
    fragments = [
        "stderr",
        "output incompleto",
        "incomplete-output",
        "incomplete output",
        "could not complete",
        "warning_review_required",
        "not available",
    ]
    return any(fragment in lowered for fragment in fragments)


def parse_report(path: Path) -> ParsedTrial:
    text = read_text(path)
    return ParsedTrial(
        path=path,
        trial_name=extract_value(text, ["trial-name"]),
        classification=extract_value(text, ["classification"]).upper(),
        approval_status=extract_value(text, ["approval status"]).upper(),
        invocation_status=extract_value(text, ["invocation status"]).upper(),
        capture_status=extract_value(text, ["capture status"]).upper(),
        safety_gate_status=extract_value(text, ["safety gate status"]).upper(),
        codex_availability=extract_value(text, ["Codex availability"]).upper(),
        exit_code=extract_value(text, ["exit code"]),
        stderr_or_incomplete=has_stderr_or_incomplete_evidence(text),
    )


def validate_reports(report_values: list[str], root: Path) -> list[Path]:
    paths = [resolve_path(value, base=root) for value in report_values]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise InputError(f"report path does not exist:\n{formatted}")
    return paths


def bullet(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- none"


def table(trials: list[ParsedTrial]) -> str:
    rows = [
        "| Report | Trial | Classification | Approval | Invocation | Capture | Safety gate | Codex | Exit code |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for trial in trials:
        rows.append(
            f"| `{trial.path}` | `{trial.trial_name}` | `{trial.classification}` | `{trial.approval_status}` | "
            f"`{trial.invocation_status}` | `{trial.capture_status}` | `{trial.safety_gate_status}` | "
            f"`{trial.codex_availability}` | `{trial.exit_code}` |"
        )
    return "\n".join(rows)


def differences(trials: list[ParsedTrial]) -> list[str]:
    fields = {
        "classification": [trial.classification for trial in trials],
        "approval status": [trial.approval_status for trial in trials],
        "invocation status": [trial.invocation_status for trial in trials],
        "capture status": [trial.capture_status for trial in trials],
        "safety gate status": [trial.safety_gate_status for trial in trials],
        "Codex availability": [trial.codex_availability for trial in trials],
        "exit code": [trial.exit_code for trial in trials],
    }
    output: list[str] = []
    for label, values in fields.items():
        unique = sorted(set(values))
        if len(unique) > 1:
            output.append(f"{label}: {', '.join(unique)}")
    return output


def classification_groups(trials: list[ParsedTrial]) -> dict[str, list[str]]:
    groups = {
        "succeeded": [],
        "warning": [],
        "blocked": [],
        "codex_not_available": [],
        "failed": [],
    }
    for trial in trials:
        entry = f"{trial.trial_name} ({trial.classification})"
        if trial.classification == "READONLY_EXECUTED_CLEAN":
            groups["succeeded"].append(entry)
        elif trial.classification in {"READONLY_EXECUTED_WARNING"} or "WARNING" in trial.safety_gate_status:
            groups["warning"].append(entry)
        elif trial.classification.startswith("BLOCKED"):
            groups["blocked"].append(entry)
        elif trial.classification == "CODEX_NOT_AVAILABLE":
            groups["codex_not_available"].append(entry)
        elif trial.classification == "FAILED":
            groups["failed"].append(entry)
    return groups


def recommendation(trials: list[ParsedTrial]) -> str:
    classifications = {trial.classification for trial in trials}
    if "FAILED" in classifications:
        return "Stop and inspect failed trial evidence before repeating or broadening the experiment."
    if "CODEX_NOT_AVAILABLE" in classifications:
        return "Verify local Codex availability, then repeat the same prepared trial for a comparable run."
    if "READONLY_EXECUTED_WARNING" in classifications:
        return "Keep the work at read-only diagnostics and harden stderr/output completeness handling."
    if classifications == {"READONLY_EXECUTED_CLEAN"}:
        return "The read-only trials are mechanically clean; still keep broader execution as a separate future design step."
    if any(value.startswith("BLOCKED") for value in classifications):
        return "Resolve blocking approval or target cleanliness conditions before attempting read-only execution."
    return "Collect another repeatable trial before making a broader workflow decision."


def build_report(trials: list[ParsedTrial]) -> str:
    groups = classification_groups(trials)
    recurring = Counter("stderr/output incomplete" for trial in trials if trial.stderr_or_incomplete)
    recurring_lines = [f"{label}: {count}" for label, count in recurring.items()]
    return f"""# ASF Codex Read-Only Trial Comparison Report

## Reports compared

{table(trials)}

## Differences

{bullet(differences(trials))}

## Trial groups

### Trial riusciti

{bullet(groups["succeeded"])}

### Trial warning

{bullet(groups["warning"])}

### Trial bloccati

{bullet(groups["blocked"])}

### Codex non disponibile

{bullet(groups["codex_not_available"])}

### Trial falliti

{bullet(groups["failed"])}

## Recurrence

{bullet(recurring_lines)}

## Raccomandazione

{recommendation(trials)}

## Limits

- This comparison did not execute Codex.
- This comparison did not modify any target repository.
- This comparison did not run Git or GitHub commands.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    report_paths = validate_reports(args.reports, root)
    output_dir = resolve_path(args.output_dir, base=root)
    trials = [parse_report(path) for path in report_paths]
    output_path = output_dir / "trial_comparison_report.md"
    write_text(output_path, build_report(trials))
    print(f"Trial comparison report generated: {output_path}")
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
