from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

DECISION_GO = "GO_TO_WORKSPACE_WRITE_DESIGN"
DECISION_MORE_TRIALS = "GO_TO_MORE_READONLY_TRIALS"
DECISION_WARNING = "WARNING_REVIEW_REQUIRED"
DECISION_HOLD = "HOLD"
DECISION_NO_GO = "NO_GO"

ALLOWED_DECISIONS = (
    DECISION_GO,
    DECISION_MORE_TRIALS,
    DECISION_WARNING,
    DECISION_HOLD,
    DECISION_NO_GO,
)

WORKSPACE_WRITE = "workspace" + "-write"
DANGER_FULL_ACCESS = "danger" + "-full-access"


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedJson:
    path: Path
    exists: bool
    malformed: bool
    data: Any
    error: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce a conservative decision from ASF Codex read-only diagnostics evidence.",
    )
    parser.add_argument("--diagnostics", nargs="+", required=True, help="Diagnostics JSON files.")
    parser.add_argument("--cli-probe", required=True, help="CLI compatibility probe JSON file.")
    parser.add_argument("--trial-comparison", help="Optional repeatable trial comparison JSON file.")
    parser.add_argument(
        "--output-json",
        default="tmp/asf_codex_readonly_decision_gate/readonly_decision_gate.json",
        help="Stable JSON output path.",
    )
    parser.add_argument("--output-markdown", help="Optional Markdown summary output path.")
    return parser.parse_args(argv)


def resolve_path(value: str | Path, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def load_json(path: Path) -> LoadedJson:
    if not path.is_file():
        return LoadedJson(path=path, exists=False, malformed=False, data=None, error="JSON file does not exist")
    try:
        return LoadedJson(path=path, exists=True, malformed=False, data=json.loads(path.read_text(encoding="utf-8-sig")), error="")
    except json.JSONDecodeError as exc:
        return LoadedJson(path=path, exists=True, malformed=True, data=None, error=str(exc))


def iter_values(value: Any) -> list[Any]:
    output = [value]
    if isinstance(value, dict):
        for key, nested in value.items():
            output.append(str(key))
            output.extend(iter_values(nested))
    elif isinstance(value, list):
        for nested in value:
            output.extend(iter_values(nested))
    return output


def iter_strings(value: Any) -> list[str]:
    return [str(item) for item in iter_values(value) if isinstance(item, (str, int, float))]


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def find_values(value: Any, key_names: set[str]) -> list[Any]:
    matches: list[Any] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if normalized_key(str(key)) in key_names:
                matches.append(nested)
            matches.extend(find_values(nested, key_names))
    elif isinstance(value, list):
        for nested in value:
            matches.extend(find_values(nested, key_names))
    return matches


def collect_classifications(value: Any) -> set[str]:
    output: set[str] = set()
    for raw in find_values(value, {"classification", "classifications", "decision", "decisione", "status"}):
        candidates = raw if isinstance(raw, list) else [raw]
        for candidate in candidates:
            if isinstance(candidate, str):
                for token in re.findall(r"\b[A-Z][A-Z0-9_ -]{2,}\b", candidate.upper()):
                    output.add(token.replace(" ", "_").replace("-", "_").strip("_"))
    for text in iter_strings(value):
        upper = text.upper()
        for token in [
            "CODEX_NOT_AVAILABLE",
            "CODEX_AVAILABLE",
            "CLI_PROBE_AVAILABLE",
            "EXECUTION_COMPLETED",
            "EXECUTION_FAILED",
            "STDERR_NONEMPTY",
            "STDOUT_EMPTY",
            "OUTPUT_INCOMPLETE",
            "EXIT_CODE_NONZERO",
            "TARGET_CLEAN_AFTER_READONLY",
            "TARGET_DIRTY_AFTER_READONLY",
            "REPORT_MALFORMED",
            "REPORT_MISSING",
            "UNKNOWN_REVIEW_REQUIRED",
            "READONLY_EXECUTED_CLEAN",
            "READONLY_EXECUTED_WARNING",
            "FAILED",
        ]:
            if token in upper:
                output.add(token)
    return output


def supported(probe: dict[str, Any], key: str) -> bool:
    support = probe.get("support", {}) if isinstance(probe, dict) else {}
    entry = support.get(key, {})
    if isinstance(entry, dict):
        return bool(entry.get("supported"))
    return bool(entry)


def cli_is_clear(probe: LoadedJson) -> bool:
    if not probe.exists or probe.malformed or not isinstance(probe.data, dict):
        return False
    classifications = collect_classifications(probe.data)
    if "CODEX_AVAILABLE" not in classifications or "CLI_PROBE_AVAILABLE" not in classifications:
        return False
    required_support = ["exec", "sandbox", "read_only"]
    return all(supported(probe.data, key) for key in required_support)


def forbidden_sandbox_mode(value: Any) -> bool:
    risky_keys = {
        "sandbox",
        "sandbox_mode",
        "requested_sandbox",
        "command",
        "command_executed",
        "command_preview",
    }
    for raw in find_values(value, risky_keys):
        if isinstance(raw, list):
            candidates = raw
        else:
            candidates = [raw]
        for candidate in candidates:
            if not isinstance(candidate, str):
                continue
            lowered = candidate.casefold()
            if WORKSPACE_WRITE in lowered or DANGER_FULL_ACCESS in lowered:
                return True
    return False


def comparison_is_clean(comparison: LoadedJson | None) -> bool:
    if comparison is None or not comparison.exists or comparison.malformed:
        return False
    classifications = collect_classifications(comparison.data)
    if "READONLY_EXECUTED_CLEAN" in classifications or DECISION_GO in classifications:
        return True
    if isinstance(comparison.data, dict):
        clean = find_values(comparison.data, {"repeated_readonly_trials_clean", "all_trials_clean"})
        if any(bool(value) for value in clean):
            return True
    return False


def comparison_has_warning_or_failure(comparison: LoadedJson | None) -> bool:
    if comparison is None or not comparison.exists or comparison.malformed:
        return False
    classifications = collect_classifications(comparison.data)
    return bool(
        classifications
        & {
            "READONLY_EXECUTED_WARNING",
            "WARNING_REVIEW_REQUIRED",
            "FAILED",
            "NO_GO",
            "TARGET_DIRTY_AFTER_READONLY",
        }
    )


def build_decision(
    *,
    diagnostics: list[LoadedJson],
    cli_probe: LoadedJson,
    comparison: LoadedJson | None,
) -> dict[str, Any]:
    no_go: list[str] = []
    hold: list[str] = []
    warnings: list[str] = []
    more_trials: list[str] = []

    loaded_items = [*diagnostics, cli_probe]
    if comparison is not None:
        loaded_items.append(comparison)

    for item in loaded_items:
        if not item.exists:
            hold.append(f"missing JSON input: {item.path}")
        if item.malformed:
            hold.append(f"malformed JSON input: {item.path}: {item.error}")

    diagnostic_classifications: set[str] = set()
    for item in diagnostics:
        diagnostic_classifications.update(collect_classifications(item.data))
        if forbidden_sandbox_mode(item.data):
            no_go.append(f"forbidden sandbox mode evidence found in {item.path}")

    if forbidden_sandbox_mode(cli_probe.data):
        no_go.append(f"forbidden sandbox mode evidence found in {cli_probe.path}")
    if comparison is not None and forbidden_sandbox_mode(comparison.data):
        no_go.append(f"forbidden sandbox mode evidence found in {comparison.path}")

    if "TARGET_DIRTY_AFTER_READONLY" in diagnostic_classifications:
        no_go.append("diagnostics show target DIRTY after read-only run.")
    if "REPORT_MISSING" in diagnostic_classifications or "REPORT_MALFORMED" in diagnostic_classifications:
        hold.append("diagnostics contain missing or malformed source reports.")

    warning_tokens = {"STDERR_NONEMPTY", "OUTPUT_INCOMPLETE", "EXIT_CODE_NONZERO"}
    if diagnostic_classifications & warning_tokens:
        if "TARGET_DIRTY_AFTER_READONLY" not in diagnostic_classifications:
            warnings.append("diagnostics contain stderr, incomplete output or nonzero exit evidence while target is not dirty.")

    cli_classifications = collect_classifications(cli_probe.data)
    if "CODEX_NOT_AVAILABLE" in cli_classifications or "CODEX_NOT_AVAILABLE" in diagnostic_classifications:
        more_trials.append("Codex CLI is not available; classify as environment diagnostic and repeat later.")
    if not cli_is_clear(cli_probe):
        more_trials.append("CLI compatibility is not clear enough for a future design step.")

    if "EXECUTION_COMPLETED" not in diagnostic_classifications:
        more_trials.append("diagnostics do not contain completed read-only execution evidence.")
    if "TARGET_CLEAN_AFTER_READONLY" not in diagnostic_classifications:
        more_trials.append("diagnostics do not prove target CLEAN after read-only execution.")

    if comparison is None:
        more_trials.append("repeatable trial comparison evidence is missing.")
    elif not comparison_is_clean(comparison):
        more_trials.append("repeatable trial comparison does not prove clean repeated read-only trials.")
    if comparison_has_warning_or_failure(comparison):
        warnings.append("repeatable trial comparison contains warning or failure evidence.")

    if no_go:
        decision = DECISION_NO_GO
    elif hold:
        decision = DECISION_HOLD
    elif warnings:
        decision = DECISION_WARNING
    elif more_trials:
        decision = DECISION_MORE_TRIALS
    else:
        decision = DECISION_GO

    return {
        "schema_version": "1.0",
        "report_type": "asf_codex_readonly_decision_gate",
        "allowed_decisions": list(ALLOWED_DECISIONS),
        "decision": decision,
        "inputs": {
            "diagnostics": [str(item.path) for item in diagnostics],
            "cli_probe": str(cli_probe.path),
            "trial_comparison": "" if comparison is None else str(comparison.path),
        },
        "classification_summary": {
            "diagnostics": sorted(diagnostic_classifications),
            "cli_probe": sorted(cli_classifications),
            "trial_comparison": [] if comparison is None else sorted(collect_classifications(comparison.data)),
        },
        "reasons": {
            DECISION_NO_GO: no_go,
            DECISION_HOLD: hold,
            DECISION_WARNING: warnings,
            DECISION_MORE_TRIALS: more_trials,
        },
        "safety_note": (
            f"{DECISION_GO} does not authorize broader execution. "
            "It only allows preparing a separate future design step with human approval."
        ),
    }


def markdown_summary(report: dict[str, Any]) -> str:
    def bullets(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- none"

    return f"""# ASF Codex Read-Only Decision Gate

## Summary

- decision: `{report['decision']}`
- allowed decisions: `{', '.join(report['allowed_decisions'])}`

## NO_GO

{bullets(report['reasons'][DECISION_NO_GO])}

## HOLD

{bullets(report['reasons'][DECISION_HOLD])}

## WARNING_REVIEW_REQUIRED

{bullets(report['reasons'][DECISION_WARNING])}

## GO_TO_MORE_READONLY_TRIALS

{bullets(report['reasons'][DECISION_MORE_TRIALS])}

## Safety Note

{report['safety_note']}

## Limits

- This decision gate did not invoke Codex.
- This decision gate did not modify any target repository.
- This decision gate did not execute commit, push, pull request, merge, tag or deploy.
"""


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    diagnostics = [load_json(resolve_path(value, base=root)) for value in args.diagnostics]
    cli_probe = load_json(resolve_path(args.cli_probe, base=root))
    comparison = load_json(resolve_path(args.trial_comparison, base=root)) if args.trial_comparison else None
    report = build_decision(diagnostics=diagnostics, cli_probe=cli_probe, comparison=comparison)

    output_json = resolve_path(args.output_json, base=root)
    write_json(output_json, report)
    print(f"Read-only decision gate JSON generated: {output_json}")
    print(f"Decision: {report['decision']}")

    if args.output_markdown:
        output_markdown = resolve_path(args.output_markdown, base=root)
        write_text(output_markdown, markdown_summary(report))
        print(f"Read-only decision gate Markdown generated: {output_markdown}")
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
