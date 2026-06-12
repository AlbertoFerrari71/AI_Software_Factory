from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from asf_latest_report_resolver import resolve_latest_report
from asf_publish_readiness_gate import DEFAULT_BRIDGE, evaluate_readiness


def list_lines(values: list[Any]) -> list[str]:
    if not values:
        return ["- None declared."]
    return [f"- {value}" for value in values]


def build_packet(*, bridge: Path, expected_step: str | None) -> str:
    resolved = resolve_latest_report(bridge, expected_step=expected_step)
    readiness = evaluate_readiness(bridge=bridge, expected_step=expected_step)
    report = resolved.get("report") if isinstance(resolved.get("report"), dict) else {}
    files_created = report.get("files_created", []) if isinstance(report, dict) else []
    files_modified = report.get("files_modified", []) if isinstance(report, dict) else []
    risks = report.get("risks", []) if isinstance(report, dict) else []
    decisions = report.get("decisions_required", []) if isinstance(report, dict) else []
    checks = report.get("checks", []) if isinstance(report, dict) else []

    lines = [
        "# GPT Reviewer Packet",
        "",
        "Packet type: independent review evidence.",
        "Decision requested: PASS / FIX / STOP / ASK_ALBERTO.",
        "",
        "## Context",
        "",
        f"- Project: AI_Software_Factory",
        f"- Expected step: {expected_step or 'latest'}",
        f"- Resolution status: {resolved['resolution_status']}",
        f"- Report status: {resolved['status']}",
        f"- Publish readiness: {readiness['semaphore']}",
        f"- Report JSON: {resolved.get('selected_report') or 'not found'}",
        f"- Report Markdown: {resolved.get('selected_markdown') or 'not found'}",
        "",
        "## Files Created",
        "",
        *list_lines(files_created),
        "",
        "## Files Modified",
        "",
        *list_lines(files_modified),
        "",
        "## Checks",
        "",
    ]
    if checks:
        for check in checks:
            if isinstance(check, dict):
                lines.append(
                    f"- {check.get('name', 'unnamed')}: {check.get('status', 'UNKNOWN')} "
                    f"(`{check.get('command', '')}`)"
                )
            else:
                lines.append(f"- {check}")
    else:
        lines.append("- No machine-readable checks declared.")
    lines.extend(
        [
            "",
            "## Risks",
            "",
            *list_lines(risks),
            "",
            "## Decisions Required",
            "",
            *list_lines(decisions),
            "",
            "## Review Question",
            "",
            "Return exactly one verdict: PASS, FIX, STOP, or ASK_ALBERTO. Explain only evidence-backed reasons.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a GPT reviewer packet from the latest Codex report.")
    parser.add_argument("--bridge", default=DEFAULT_BRIDGE)
    parser.add_argument("--expected-step")
    parser.add_argument("--output", help="Optional Markdown output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON wrapper instead of raw Markdown.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    markdown = build_packet(bridge=Path(args.bridge), expected_step=args.expected_step)
    if args.output:
        Path(args.output).write_text(markdown + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps({"markdown": markdown, "output": args.output}, indent=2, sort_keys=True))
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
