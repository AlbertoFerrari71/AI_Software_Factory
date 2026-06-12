from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from asf_latest_report_resolver import resolve_latest_report
from asf_publish_readiness_gate import DEFAULT_BRIDGE, evaluate_readiness
from asf_step_registry import NEXT_STEP_AFTER_RC, find_record


def run_git(args: list[str], root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "exit_code": None}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "exit_code": result.returncode,
    }


def collect_status(*, bridge: Path, expected_step: str | None, root: Path) -> dict[str, Any]:
    selected_step = expected_step or "latest"
    record = find_record(selected_step)
    branch = run_git(["--no-pager", "branch", "--show-current"], root)
    status = run_git(["--no-pager", "status", "--short"], root)
    commit = run_git(["--no-pager", "log", "--oneline", "--max-count=1"], root)
    resolver = resolve_latest_report(bridge, expected_step=None if selected_step == "latest" else selected_step, latest=selected_step == "latest")
    readiness = evaluate_readiness(bridge=bridge, expected_step=None if selected_step == "latest" else selected_step, root=root)

    warnings = list(resolver.get("warnings", [])) + list(readiness.get("warnings", []))
    if not bridge.exists():
        warnings.append("Bridge folder is not reachable.")
    if status["stdout"]:
        warnings.append("Working tree has local changes; review scope before any publication.")
    recommended = "Review Codex report and generate GPT reviewer packet."
    if readiness["semaphore"] == "RED":
        recommended = "Stop publication path and fix missing or failing evidence."
    elif readiness["semaphore"] == "GREEN":
        recommended = "Ready for Alberto review; publish remains human-gated through asf_publish_step.ps1."

    return {
        "project": "AI_Software_Factory",
        "branch": branch["stdout"],
        "working_tree_status": status["stdout"] or "clean",
        "latest_commit": commit["stdout"],
        "bridge_reachable": bridge.exists() and bridge.is_dir(),
        "bridge": str(bridge),
        "latest_report": resolver.get("selected_report") or resolver.get("selected_markdown"),
        "latest_step": resolver.get("latest_step"),
        "expected_next_step": record.next_step if record.status != "unknown" else NEXT_STEP_AFTER_RC,
        "warnings": warnings,
        "recommended_action": recommended,
        "publish_readiness": readiness,
        "report_resolution": resolver,
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"project: {payload['project']}",
        f"branch: {payload['branch']}",
        f"working_tree_status: {payload['working_tree_status']}",
        f"latest_commit: {payload['latest_commit']}",
        f"bridge_reachable: {str(payload['bridge_reachable']).lower()}",
        f"latest_report: {payload.get('latest_report') or ''}",
        f"latest_step: {payload.get('latest_step') or ''}",
        f"expected_next_step: {payload['expected_next_step']}",
        f"publish_readiness: {payload['publish_readiness']['semaphore']}",
        f"recommended_action: {payload['recommended_action']}",
        "warnings:",
    ]
    lines.extend(f"- {warning}" for warning in payload["warnings"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show ASF supervised operator status.")
    parser.add_argument("--bridge", default=DEFAULT_BRIDGE, help="Bridge codex_command folder.")
    parser.add_argument("--step", help="Step to inspect, or latest.")
    parser.add_argument("--expected-step", help="Expected step or range.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    expected = args.expected_step or args.step or "latest"
    payload = collect_status(bridge=Path(args.bridge), expected_step=expected, root=Path.cwd())
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
