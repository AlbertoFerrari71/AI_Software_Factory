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

REPORT_RE = re.compile(
    r"^(?P<step>\d{4}(?:-\d{4})?)-(?P<kind>Report_Codex|Codex_Report)\.(?P<ext>json|md)$",
    re.IGNORECASE,
)
STATUS_RE = re.compile(r"(?:^|\n)\s*(?:B\.\s*)?Stato\s*:?\s*(PASS|PARTIAL|FAIL|STOP)", re.IGNORECASE)

REQUIRED_JSON_FIELDS = {
    "schema_version",
    "status",
    "branch",
    "checks",
    "forbidden_actions_confirmed",
    "human_gate_required",
    "summary",
}


@dataclass(frozen=True)
class ReportFile:
    path: Path
    step: str
    ext: str
    modified_ns: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "step": self.step,
            "ext": self.ext,
            "modified_ns": self.modified_ns,
        }


def normalize_step(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if "/" in cleaned:
        cleaned = cleaned.rsplit("/", 1)[-1]
    match = re.search(r"\d{4}(?:-\d{4})?", cleaned)
    return match.group(0) if match else cleaned


def step_contains(candidate: str, expected: str | None) -> bool:
    if expected is None:
        return True
    candidate_norm = normalize_step(candidate)
    expected_norm = normalize_step(expected)
    if not candidate_norm or not expected_norm:
        return False
    if candidate_norm == expected_norm:
        return True
    if "-" in candidate_norm and "-" not in expected_norm:
        start, end = (int(part) for part in candidate_norm.split("-", 1))
        return start <= int(expected_norm) <= end
    return False


def extract_status_from_markdown(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = STATUS_RE.search(text)
    return match.group(1).upper() if match else None


def discover_report_files(bridge: Path, expected_step: str | None = None) -> list[ReportFile]:
    if not bridge.exists() or not bridge.is_dir():
        return []
    reports: list[ReportFile] = []
    for path in bridge.iterdir():
        if not path.is_file() or path.name.upper().startswith("LAST-"):
            continue
        match = REPORT_RE.match(path.name)
        if not match:
            continue
        step = match.group("step")
        if not step_contains(step, expected_step):
            continue
        reports.append(
            ReportFile(
                path=path,
                step=step,
                ext=match.group("ext").lower(),
                modified_ns=path.stat().st_mtime_ns,
            )
        )
    return sorted(reports, key=lambda item: (item.modified_ns, item.path.name), reverse=True)


def load_report_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid JSON report: {exc}"]
    if not isinstance(payload, dict):
        return None, ["JSON report root must be an object"]
    missing = sorted(REQUIRED_JSON_FIELDS.difference(payload))
    if missing:
        warnings.append("JSON report missing required fields: " + ", ".join(missing))
    return payload, warnings


def find_markdown_pair(json_report: ReportFile, reports: list[ReportFile]) -> Path | None:
    same_step = [item for item in reports if item.ext == "md" and item.step == json_report.step]
    if not same_step:
        return None
    return same_step[0].path


def report_status(payload: dict[str, Any], fallback: str | None = None) -> str | None:
    status = payload.get("status") or payload.get("state") or fallback
    return str(status).strip().upper() if status else None


def build_missing_result(bridge: Path, expected_step: str | None) -> dict[str, Any]:
    status = "MISSING_BRIDGE" if not bridge.exists() else "MISSING_REPORT"
    return {
        "resolution_status": "MISSING",
        "status": status,
        "expected_step": normalize_step(expected_step),
        "bridge": str(bridge),
        "selected_report": None,
        "selected_markdown": None,
        "latest_step": None,
        "warnings": [f"Bridge folder not found: {bridge}" if not bridge.exists() else "No matching Codex report found"],
        "candidates": [],
        "report": None,
    }


def resolve_latest_report(
    bridge: Path,
    *,
    expected_step: str | None = None,
    latest: bool = False,
) -> dict[str, Any]:
    reports = discover_report_files(bridge, expected_step if not latest else None)
    if not reports:
        return build_missing_result(bridge, None if latest else expected_step)

    json_reports = [item for item in reports if item.ext == "json"]
    markdown_reports = [item for item in reports if item.ext == "md"]
    candidates = [item.as_dict() for item in reports]

    if expected_step and len({item.path.stem for item in json_reports}) > 1:
        return {
            "resolution_status": "AMBIGUOUS",
            "status": "AMBIGUOUS_REPORT",
            "expected_step": normalize_step(expected_step),
            "bridge": str(bridge),
            "selected_report": None,
            "selected_markdown": None,
            "latest_step": None,
            "warnings": ["Multiple JSON Codex reports match the expected step; review manually."],
            "candidates": candidates,
            "report": None,
        }

    warnings: list[str] = []
    if json_reports:
        selected = json_reports[0]
        payload, json_warnings = load_report_json(selected.path)
        warnings.extend(json_warnings)
        markdown_pair = find_markdown_pair(selected, reports)
        if payload is None or json_warnings:
            return {
                "resolution_status": "INCOHERENT",
                "status": "INCOHERENT_REPORT",
                "expected_step": normalize_step(expected_step),
                "bridge": str(bridge),
                "selected_report": str(selected.path),
                "selected_markdown": str(markdown_pair) if markdown_pair else None,
                "latest_step": selected.step,
                "warnings": warnings,
                "candidates": candidates,
                "report": payload,
            }
        return {
            "resolution_status": "FOUND",
            "status": report_status(payload),
            "expected_step": normalize_step(expected_step),
            "bridge": str(bridge),
            "selected_report": str(selected.path),
            "selected_markdown": str(markdown_pair) if markdown_pair else None,
            "latest_step": normalize_step(str(payload.get("step_range") or payload.get("step") or selected.step)),
            "warnings": warnings,
            "candidates": candidates,
            "report": payload,
        }

    selected_md = markdown_reports[0]
    markdown_status = extract_status_from_markdown(selected_md.path)
    return {
        "resolution_status": "DEGRADED",
        "status": markdown_status or "MARKDOWN_ONLY_UNKNOWN_STATUS",
        "expected_step": normalize_step(expected_step),
        "bridge": str(bridge),
        "selected_report": None,
        "selected_markdown": str(selected_md.path),
        "latest_step": selected_md.step,
        "warnings": ["Only Markdown report found; JSON sidecar is missing."],
        "candidates": candidates,
        "report": None,
    }


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"resolution_status: {result['resolution_status']}",
        f"status: {result['status']}",
        f"bridge: {result['bridge']}",
        f"expected_step: {result.get('expected_step') or ''}",
        f"latest_step: {result.get('latest_step') or ''}",
        f"selected_report: {result.get('selected_report') or ''}",
        f"selected_markdown: {result.get('selected_markdown') or ''}",
        "warnings:",
    ]
    lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve the latest ASF Codex report from a Bridge folder.")
    parser.add_argument("--bridge", default=".", help="Bridge folder to inspect.")
    parser.add_argument("--expected-step", help="Expected step number or range, for example 1050 or 1050-1130.")
    parser.add_argument("--latest", action="store_true", help="Ignore expected step and return the newest report.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.expected_step and args.latest:
        print("ERROR: use either --expected-step or --latest, not both.", file=sys.stderr)
        return EXIT_INPUT_ERROR
    result = resolve_latest_report(Path(args.bridge), expected_step=args.expected_step, latest=args.latest)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result), end="")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
