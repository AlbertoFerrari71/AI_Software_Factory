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

CLASSIFICATION_ORDER = (
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
)

REPORT_OK = "OK"
REPORT_MISSING = "MISSING"
REPORT_MALFORMED = "MALFORMED"


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedReport:
    path: Path
    state: str
    data: Any
    error: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize ASF Codex read-only invocation JSON evidence into deterministic diagnostics.",
    )
    parser.add_argument("--reports", nargs="+", required=True, help="JSON report paths to diagnose.")
    parser.add_argument(
        "--output-json",
        default="tmp/asf_codex_readonly_diagnostics/readonly_diagnostics.json",
        help="Stable JSON output path.",
    )
    parser.add_argument("--output-markdown", help="Optional Markdown summary output path.")
    return parser.parse_args(argv)


def resolve_path(value: str | Path, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, dict):
        output: list[str] = []
        for key, nested in value.items():
            output.append(str(key))
            output.extend(iter_strings(nested))
        return output
    if isinstance(value, list):
        output: list[str] = []
        for nested in value:
            output.extend(iter_strings(nested))
        return output
    return [str(value)]


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


def flatten_classifications(value: Any) -> set[str]:
    found: set[str] = set()
    for raw in find_values(value, {"classification", "classifications", "status", "decision", "decisione"}):
        if isinstance(raw, list):
            candidates = raw
        else:
            candidates = [raw]
        for candidate in candidates:
            if not isinstance(candidate, str):
                continue
            for token in re.findall(r"\b[A-Z][A-Z0-9_ -]{2,}\b", candidate.upper()):
                cleaned = token.replace(" ", "_").replace("-", "_").strip("_")
                if cleaned in CLASSIFICATION_ORDER or cleaned in {
                    "PASS",
                    "WARNING",
                    "FAIL",
                    "AVAILABLE",
                    "GO",
                    "GO_TO_WORKSPACE_WRITE_DESIGN",
                    "READONLY_EXECUTED_CLEAN",
                    "READONLY_EXECUTED_WARNING",
                    "CODEX_NOT_AVAILABLE",
                }:
                    found.add(cleaned)
    return found


def parse_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        cleaned = value.strip().strip("`")
        if cleaned in {"", "(not present)", "UNKNOWN"}:
            return None
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().casefold() in {"1", "true", "yes", "y", "supported", "available", "present"}
    return bool(value)


def text_is_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned not in {"", "(none)", "none", "NONE", "null", "NULL"}
    return bool(value)


def text_is_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() in {"", "(none)", "none", "NONE"}
    return False


def output_incomplete_signal(text: str) -> bool:
    lowered = text.casefold()
    fragments = [
        "output_incomplete",
        "output incomplete",
        "output incompleto",
        "could not complete",
        "incomplete-output",
        "sandbox error",
        "errore sandbox",
    ]
    return any(fragment in lowered for fragment in fragments)


def classify_loaded_report(report: LoadedReport) -> tuple[list[str], dict[str, Any]]:
    if report.state == REPORT_MISSING:
        return ["REPORT_MISSING"], {"error": report.error}
    if report.state == REPORT_MALFORMED:
        return ["REPORT_MALFORMED"], {"error": report.error}

    data = report.data
    strings = iter_strings(data)
    combined = "\n".join(strings)
    combined_upper = combined.upper()
    combined_lower = combined.casefold()
    classifications = set(flatten_classifications(data))
    evidence: dict[str, Any] = {}

    if "CODEX_NOT_AVAILABLE" in classifications or "CODEX_NOT_AVAILABLE" in combined_upper:
        classifications.add("CODEX_NOT_AVAILABLE")
    elif any(fragment in combined_upper for fragment in ["CODEX_AVAILABLE", "AVAILABLE"]):
        if "codex" in combined_lower:
            classifications.add("CODEX_AVAILABLE")

    executable_values = find_values(data, {"executable_present", "codex_executable_present", "present"})
    if any(truthy(value) for value in executable_values) and "codex" in combined_lower:
        classifications.add("CODEX_AVAILABLE")

    if normalized_key(str(data.get("report_type", ""))) == "asf_codex_cli_compatibility_probe" if isinstance(data, dict) else False:
        if "CODEX_AVAILABLE" in classifications:
            classifications.add("CLI_PROBE_AVAILABLE")

    exit_values = find_values(data, {"exit_code", "exitcode", "returncode", "return_code"})
    exit_codes = [code for code in (parse_int(value) for value in exit_values) if code is not None]
    if exit_codes:
        evidence["exit_codes"] = exit_codes
        if any(code != 0 for code in exit_codes):
            classifications.add("EXIT_CODE_NONZERO")
            classifications.add("EXECUTION_FAILED")
        if any(code == 0 for code in exit_codes):
            classifications.add("EXECUTION_COMPLETED")

    if any(
        fragment in combined_upper
        for fragment in ["EXECUTION_COMPLETED", "EXECUTE_READONLY_COMPLETED", "READONLY_EXECUTED_CLEAN"]
    ):
        classifications.add("EXECUTION_COMPLETED")
    if any(fragment in combined_upper for fragment in ["EXECUTION_FAILED", "FAILED_EXIT", "READONLY_EXECUTED_FAILED"]):
        classifications.add("EXECUTION_FAILED")

    stderr_values = find_values(data, {"stderr", "stderr_summary", "stderr_text"})
    if any(text_is_nonempty(value) for value in stderr_values):
        classifications.add("STDERR_NONEMPTY")
        evidence["stderr_nonempty"] = True

    stdout_values = find_values(data, {"stdout", "stdout_summary", "stdout_text"})
    if stdout_values and all(text_is_empty(value) for value in stdout_values):
        classifications.add("STDOUT_EMPTY")
        evidence["stdout_empty"] = True

    incomplete_values = find_values(data, {"output_incomplete", "incomplete_output"})
    complete_values = find_values(data, {"output_complete"})
    if any(truthy(value) for value in incomplete_values) or any(not truthy(value) for value in complete_values):
        classifications.add("OUTPUT_INCOMPLETE")
    if output_incomplete_signal(combined):
        classifications.add("OUTPUT_INCOMPLETE")

    working_tree_values = find_values(
        data,
        {
            "target_working_tree",
            "target_working_tree_after",
            "working_tree_after",
            "final_working_tree",
            "working_tree_finale_target",
            "target_final_working_tree",
        },
    )
    normalized_states = {str(value).strip().strip("`").upper() for value in working_tree_values}
    if "DIRTY" in normalized_states:
        classifications.add("TARGET_DIRTY_AFTER_READONLY")
    if "CLEAN" in normalized_states:
        classifications.add("TARGET_CLEAN_AFTER_READONLY")

    if "TARGET_DIRTY_AFTER_READONLY" in combined_upper or "WORKING TREE FINALE TARGET: `DIRTY`" in combined_upper:
        classifications.add("TARGET_DIRTY_AFTER_READONLY")
    if "TARGET_CLEAN_AFTER_READONLY" in combined_upper or "WORKING TREE FINALE TARGET: `CLEAN`" in combined_upper:
        classifications.add("TARGET_CLEAN_AFTER_READONLY")

    if not classifications:
        classifications.add("UNKNOWN_REVIEW_REQUIRED")

    ordered = [item for item in CLASSIFICATION_ORDER if item in classifications]
    if not ordered:
        ordered = ["UNKNOWN_REVIEW_REQUIRED"]
    return ordered, evidence


def load_report(path: Path) -> LoadedReport:
    if not path.is_file():
        return LoadedReport(path=path, state=REPORT_MISSING, data=None, error="report path does not exist")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return LoadedReport(path=path, state=REPORT_MALFORMED, data=None, error=str(exc))
    return LoadedReport(path=path, state=REPORT_OK, data=data, error="")


def ordered_unique(values: list[str]) -> list[str]:
    present = set(values)
    return [item for item in CLASSIFICATION_ORDER if item in present]


def build_diagnostics(report_paths: list[Path]) -> dict[str, Any]:
    reports = [load_report(path) for path in sorted(report_paths, key=lambda item: str(item).casefold())]
    report_entries: list[dict[str, Any]] = []
    all_classifications: list[str] = []

    for report in reports:
        classifications, evidence = classify_loaded_report(report)
        all_classifications.extend(classifications)
        report_entries.append(
            {
                "path": str(report.path),
                "state": report.state,
                "classifications": classifications,
                "evidence": evidence,
                "error": report.error,
            }
        )

    overall = ordered_unique(all_classifications)
    if not overall:
        overall = ["UNKNOWN_REVIEW_REQUIRED"]
    return {
        "schema_version": "1.0",
        "report_type": "asf_codex_readonly_diagnostics",
        "classification_order": list(CLASSIFICATION_ORDER),
        "classifications": overall,
        "summary": {
            "input_count": len(report_paths),
            "report_count": len(report_entries),
            "missing_count": sum(1 for entry in report_entries if entry["state"] == REPORT_MISSING),
            "malformed_count": sum(1 for entry in report_entries if entry["state"] == REPORT_MALFORMED),
        },
        "reports": report_entries,
    }


def markdown_summary(diagnostics: dict[str, Any]) -> str:
    lines = [
        "# ASF Codex Read-Only Diagnostics",
        "",
        "## Summary",
        "",
        f"- report-type: `{diagnostics['report_type']}`",
        f"- input-count: `{diagnostics['summary']['input_count']}`",
        f"- classifications: `{', '.join(diagnostics['classifications'])}`",
        "",
        "## Reports",
        "",
    ]
    for report in diagnostics["reports"]:
        lines.extend(
            [
                f"### {report['path']}",
                "",
                f"- state: `{report['state']}`",
                f"- classifications: `{', '.join(report['classifications'])}`",
                f"- error: `{report['error'] or '(none)'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Limits",
            "",
            "- This diagnostics report did not invoke Codex.",
            "- This diagnostics report did not modify any target repository.",
            "- Missing or malformed inputs are evidence, not hidden failures.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    report_paths = [resolve_path(value, base=root) for value in args.reports]
    output_json = resolve_path(args.output_json, base=root)
    diagnostics = build_diagnostics(report_paths)
    write_json(output_json, diagnostics)
    print(f"Read-only diagnostics JSON generated: {output_json}")
    print(f"Classifications: {', '.join(diagnostics['classifications'])}")

    if args.output_markdown:
        output_markdown = resolve_path(args.output_markdown, base=root)
        write_text(output_markdown, markdown_summary(diagnostics))
        print(f"Read-only diagnostics Markdown generated: {output_markdown}")
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
