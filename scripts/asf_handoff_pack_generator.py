from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asf_bridge_report_discovery import DEFAULT_BRIDGE_ROOT, discover_reports


EXIT_SUCCESS = 0
EXIT_ERROR = 1
DEFAULT_STATUS = "PARTIAL_PASS"
DEFAULT_NEXT_STEP = "1040) Publish GPT Live Continuity Mega-Step"
SECRET_REDACTION = "[REDACTED_SECRET]"
OPENAI_SECRET_PATTERN = re.compile(r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}")
BEARER_SECRET_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(openai[_-]?api[_-]?key|api[_-]?key|authorization|bearer|secret)\b\s*([:=])\s*([\"']?)[^\s,\"'}]+"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def redact_sensitive_text(value: Any) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    redacted = OPENAI_SECRET_PATTERN.sub(SECRET_REDACTION, text)
    redacted = BEARER_SECRET_PATTERN.sub("Bearer " + SECRET_REDACTION, redacted)

    def replace_assignment(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}{SECRET_REDACTION}"

    return SECRET_ASSIGNMENT_PATTERN.sub(replace_assignment, redacted)


def sanitize_data(value: Any) -> Any:
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, list):
        return [sanitize_data(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_data(item) for item in value]
    if isinstance(value, dict):
        return {redact_sensitive_text(key): sanitize_data(item) for key, item in value.items()}
    return value


def now_utc() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(argv: list[str], *, cwd: Path, timeout_seconds: int = 8) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        return {
            "command": argv,
            "status": "UNAVAILABLE",
            "exit_code": None,
            "stdout": "",
            "stderr": redact_sensitive_text(str(exc)),
        }
    except subprocess.TimeoutExpired:
        return {
            "command": argv,
            "status": "TIMEOUT",
            "exit_code": None,
            "stdout": "",
            "stderr": "command timed out",
        }

    return {
        "command": argv,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "exit_code": completed.returncode,
        "stdout": redact_sensitive_text(completed.stdout.strip()),
        "stderr": redact_sensitive_text(completed.stderr.strip()),
    }


def collect_git_state(root: Path) -> dict[str, Any]:
    branch = run_command(["git", "--no-pager", "branch", "--show-current"], cwd=root)
    head = run_command(["git", "--no-pager", "rev-parse", "--short", "HEAD"], cwd=root)
    status = run_command(["git", "--no-pager", "status", "--short"], cwd=root)
    log = run_command(["git", "--no-pager", "log", "--oneline", "--max-count=5"], cwd=root)
    status_text = str(status.get("stdout") or "")
    if status["status"] != "PASS":
        working_tree = "unknown"
    elif status_text.strip():
        working_tree = "dirty"
    else:
        working_tree = "clean"
    return {
        "root": str(root.resolve()),
        "branch": str(branch.get("stdout") or ""),
        "head": str(head.get("stdout") or ""),
        "working_tree": working_tree,
        "status_short": status_text,
        "recent_log": str(log.get("stdout") or "").splitlines(),
        "commands": [branch, head, status, log],
    }


def collect_gh_state(root: Path, *, include_gh: bool) -> dict[str, Any]:
    if not include_gh:
        return {"status": "SKIPPED", "reason": "gh collection not requested", "recent_prs": []}
    result = run_command(
        [
            "gh",
            "pr",
            "list",
            "--limit",
            "3",
            "--json",
            "number,title,state,isDraft,headRefName,baseRefName,updatedAt",
        ],
        cwd=root,
        timeout_seconds=8,
    )
    if result["status"] != "PASS":
        return {"status": "UNAVAILABLE", "command": result, "recent_prs": []}
    try:
        recent_prs = json.loads(str(result["stdout"] or "[]"))
    except json.JSONDecodeError as exc:
        return {"status": "ERROR", "command": result, "error_message": str(exc), "recent_prs": []}
    return {"status": "FOUND", "command": result, "recent_prs": sanitize_data(recent_prs)}


def load_small_json(path: Path, *, max_bytes: int = 200_000) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        if path.stat().st_size > max_bytes:
            return {"status": "SKIPPED", "reason": "file too large", "path": str(path)}
        return sanitize_data(json.loads(path.read_text(encoding="utf-8")))
    except Exception as exc:
        return {"status": "ERROR", "path": str(path), "error_message": redact_sensitive_text(str(exc))}


def collect_bridge_state(bridge_root: Path, *, step: str) -> dict[str, Any]:
    if not bridge_root.exists():
        return {
            "root": str(bridge_root),
            "status": "BRIDGE_MISSING",
            "reports": [],
            "state": {},
            "live_run": {},
        }
    discovery = discover_reports(bridge_root, expected_step=step, kind="any")
    live_run_path = bridge_root / "codex_command" / f"{step}-B-Live-Result.json"
    state_path = bridge_root / "state.json"
    return {
        "root": str(bridge_root),
        "status": discovery.get("status", "ERROR"),
        "reports": discovery.get("matches", []),
        "selected": discovery.get("selected"),
        "state": load_small_json(state_path),
        "live_run": load_small_json(live_run_path),
    }


def parse_check(value: str) -> dict[str, str]:
    if "=" in value:
        name, status = value.split("=", 1)
    else:
        name, status = value, "RECORDED"
    return {"name": name.strip(), "status": status.strip()}


def default_output_dir(*, bridge_root: Path, root: Path, step: str) -> Path:
    if bridge_root.exists():
        return bridge_root / "handoff"
    return root / "tmp" / "asf_handoff" / step


def render_markdown(packet: Mapping[str, Any]) -> str:
    repo = packet["repo"]
    bridge = packet["bridge"]
    checks = packet.get("checks", [])
    reports = bridge.get("reports", [])
    changed_files = repo.get("status_short") or "clean"
    lines = [
        f"# {packet['step']}) {packet['title']} - Handoff",
        "",
        f"- Titolo chat consigliato: ASF {packet['step']} Continuity Handoff",
        "- Contesto progetto: AI Software Factory, local-first, safety-first, human-gated.",
        f"- Repository: {repo.get('root')}",
        f"- Bridge: {bridge.get('root')}",
        "",
        "## Stato Git",
        "",
        f"- branch: {repo.get('branch') or 'unknown'}",
        f"- head: {repo.get('head') or 'unknown'}",
        f"- working_tree: {repo.get('working_tree')}",
        "",
        "## Step completati",
        "",
        "- 0940, 0945-0970, 0980-1010 e 1020 risultano prerequisiti consolidati nel contesto 1030.",
        "",
        "## Stato step corrente",
        "",
        f"- step: {packet['step']}",
        f"- status: {packet['status']}",
        f"- generated_at_utc: {packet['generated_at_utc']}",
        "",
        "## File modificati o creati",
        "",
        "```text",
        changed_files,
        "```",
        "",
        "## Verifiche eseguite",
        "",
    ]
    if checks:
        lines.extend(f"- {check.get('name')}: {check.get('status')}" for check in checks)
    else:
        lines.append("- Nessuna verifica dichiarata nel comando handoff.")
    lines.extend(
        [
            "",
            "## Bridge reports",
            "",
            f"- discovery_status: {bridge.get('status')}",
        ]
    )
    if reports:
        lines.extend(f"- {item.get('relative_path')}: {item.get('reason')}" for item in reports[:10])
    else:
        lines.append("- Nessun report Bridge rilevato.")
    lines.extend(
        [
            "",
            "## Problemi aperti",
            "",
            *[f"- {item}" for item in packet.get("open_issues", [])],
            "",
            "## Rischi residui",
            "",
            *[f"- {item}" for item in packet.get("risks", [])],
            "",
            "## Prossimo step consigliato",
            "",
            f"{packet['next_step']}",
            "",
            "## Prompt di ripartenza breve",
            "",
            "Vedi il file Start_Next_Chat_Prompt generato nello stesso pacchetto.",
            "",
        ]
    )
    return redact_sensitive_text("\n".join(lines))


def render_next_chat_prompt(packet: Mapping[str, Any]) -> str:
    repo = packet["repo"]
    return redact_sensitive_text(
        "\n".join(
            [
                f"# Ripartenza ASF - Step {packet['step']}",
                "",
                "Sei ChatGPT nel progetto AI Software Factory.",
                f"Continua dal pacchetto handoff dello step {packet['step']}: {packet['title']}.",
                "",
                "Contesto minimo:",
                f"- Repository: {repo.get('root')}",
                f"- Branch corrente atteso: {repo.get('branch') or 'main'}",
                f"- HEAD rilevato: {repo.get('head') or 'unknown'}",
                f"- Stato step precedente: {packet['status']}",
                f"- Prossimo step consigliato: {packet['next_step']}",
                "",
                "Regole:",
                "- Non inventare report o stati.",
                "- Se Alberto scrive Codex fatto o Pwsh fatto, cerca prima il report/output nel Bridge se accessibile.",
                "- Chiedi incolla manuale solo se il Bridge non e' accessibile o il file e' incoerente.",
                "- Non fare commit, push, PR, merge o deploy senza step separato esplicito.",
                "",
            ]
        )
    )


def render_json(packet: Mapping[str, Any]) -> str:
    return json.dumps(sanitize_data(dict(packet)), indent=2, sort_keys=True) + "\n"


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path.resolve()


def generate_handoff_pack(
    *,
    bridge_root: Path,
    root: Path,
    step: str,
    title: str,
    status: str = DEFAULT_STATUS,
    output_dir: Path | None = None,
    next_step: str = DEFAULT_NEXT_STEP,
    checks: list[dict[str, str]] | None = None,
    include_gh: bool = True,
) -> dict[str, Any]:
    out_dir = output_dir or default_output_dir(bridge_root=bridge_root, root=root, step=step)
    git_state = collect_git_state(root)
    bridge_state = collect_bridge_state(bridge_root, step=step)
    gh_state = collect_gh_state(root, include_gh=include_gh)

    packet: dict[str, Any] = {
        "step": step,
        "title": title,
        "status": status,
        "generated_at_utc": now_utc(),
        "repo": git_state,
        "bridge": bridge_state,
        "github": gh_state,
        "checks": checks or [],
        "live_run": bridge_state.get("live_run", {}),
        "next_step": next_step,
        "risks": [
            "Il pacchetto e' una fotografia locale: verificare Git e Bridge prima di pubblicare.",
            "gh e Bridge sono fail-soft: assenza o auth non bloccano la generazione handoff.",
        ],
        "open_issues": [],
        "outputs": {},
    }

    markdown_path = out_dir / f"{step}-Handoff.md"
    json_path = out_dir / f"{step}-Handoff.json"
    prompt_path = out_dir / f"{step}-Start_Next_Chat_Prompt.md"
    packet["outputs"] = {
        "markdown": str(markdown_path.resolve()),
        "json": str(json_path.resolve()),
        "start_next_chat_prompt": str(prompt_path.resolve()),
    }

    write_text(markdown_path, render_markdown(packet))
    write_text(prompt_path, render_next_chat_prompt(packet))
    write_text(json_path, render_json(packet))
    return sanitize_data(packet)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ASF handoff Markdown, JSON and next-chat prompt.")
    parser.add_argument("--bridge-root", default=str(DEFAULT_BRIDGE_ROOT), help="ASF Bridge root path.")
    parser.add_argument("--repo-root", default=str(repo_root()), help="Repository root path.")
    parser.add_argument("--step", required=True, help="Step id, for example 1030.")
    parser.add_argument("--title", required=True, help="Step title.")
    parser.add_argument("--status", default=DEFAULT_STATUS, help="Current step status.")
    parser.add_argument("--next-step", default=DEFAULT_NEXT_STEP, help="Recommended next step.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to Bridge handoff or repo tmp fallback.")
    parser.add_argument("--check", action="append", default=[], help="Recorded check as NAME=STATUS.")
    parser.add_argument("--skip-gh", action="store_true", help="Do not attempt gh read-only collection.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        packet = generate_handoff_pack(
            bridge_root=Path(args.bridge_root),
            root=Path(args.repo_root),
            step=args.step,
            title=args.title,
            status=args.status,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            next_step=args.next_step,
            checks=[parse_check(item) for item in args.check],
            include_gh=not args.skip_gh,
        )
    except Exception as exc:
        error_packet = {"status": "ERROR", "error_message": redact_sensitive_text(str(exc))}
        print(render_json(error_packet), end="")
        return EXIT_ERROR

    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["outputs"]["markdown"])
    return EXIT_SUCCESS


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
