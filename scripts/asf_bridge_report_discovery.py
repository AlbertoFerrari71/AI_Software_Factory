from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_ERROR = 1

DEFAULT_BRIDGE_ROOT = Path(
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory"
)
SUPPORTED_KINDS = {"codex", "pwsh", "any"}
SECRET_REDACTION = "[REDACTED_SECRET]"
OPENAI_SECRET_PATTERN = re.compile(r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}")
BEARER_SECRET_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(openai[_-]?api[_-]?key|api[_-]?key|authorization|bearer|secret)\b\s*([:=])\s*([\"']?)[^\s,\"'}]+"
)


def redact_sensitive_text(value: Any) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    redacted = OPENAI_SECRET_PATTERN.sub(SECRET_REDACTION, text)
    redacted = BEARER_SECRET_PATTERN.sub("Bearer " + SECRET_REDACTION, redacted)

    def replace_assignment(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}{SECRET_REDACTION}"

    return SECRET_ASSIGNMENT_PATTERN.sub(replace_assignment, redacted)


def utc_timestamp(path: Path) -> str:
    return (
        datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def candidate_patterns(kind: str) -> list[tuple[str, str, str]]:
    patterns: list[tuple[str, str, str]] = []
    if kind in {"codex", "any"}:
        patterns.append(("codex", "codex_command", "*-Report_Codex.json"))
        patterns.append(("codex", "codex_command", "*-Report_Codex.md"))
        patterns.append(("codex", "codex_command", "*-Live-Result*.json"))
        patterns.append(("codex", "codex_command", "*-Live-Result-Sanitized.md"))
    if kind in {"pwsh", "any"}:
        patterns.append(("pwsh", "pwsh_command", "*-Output_Compatto*.md"))
        patterns.append(("pwsh", "pwsh_command", "*-Output_Completo*.txt"))
    if kind == "any":
        patterns.append(("state", ".", "state.json"))
        patterns.append(("handoff", "handoff", "*"))
    return patterns


def file_score(path: Path, *, file_kind: str, expected_step: str | None) -> tuple[int, str]:
    name = path.name
    score = 0
    reasons: list[str] = []

    if file_kind == "codex" and name.endswith("-Report_Codex.json"):
        score += 45
        reasons.append("structured_report_suffix")
    elif file_kind == "codex" and name.endswith("-Report_Codex.md"):
        score += 40
        reasons.append("report_suffix")
    elif file_kind == "codex" and "Live-Result" in name:
        score += 32
        reasons.append("live_result_artifact")
    elif file_kind == "pwsh" and "Output_Compatto" in name:
        score += 35
        reasons.append("pwsh_compact_suffix")
    elif file_kind == "pwsh" and "Output_Completo" in name:
        score += 30
        reasons.append("pwsh_complete_suffix")
    elif file_kind == "state":
        score += 20
        reasons.append("state_json")
    elif file_kind == "handoff":
        score += 15
        reasons.append("handoff_artifact")

    if expected_step:
        if name.startswith(expected_step):
            score += 100
            reasons.append("expected_step_prefix")
        elif expected_step in name:
            score += 80
            reasons.append("expected_step_name_match")

    if not reasons:
        reasons.append("pattern_match")
    return score, "_and_".join(reasons)


def searched_patterns(bridge_root: Path, *, kind: str) -> list[str]:
    return [
        str((bridge_root if folder_name == "." else bridge_root / folder_name) / pattern)
        for _, folder_name, pattern in candidate_patterns(kind)
    ]


def make_match(path: Path, *, root: Path, file_kind: str, expected_step: str | None) -> dict[str, Any]:
    score, reason = file_score(path, file_kind=file_kind, expected_step=expected_step)
    try:
        size_bytes = path.stat().st_size
        modified_utc = utc_timestamp(path)
    except OSError:
        size_bytes = 0
        modified_utc = ""
    return {
        "path": str(path.resolve()),
        "relative_path": str(path.resolve().relative_to(root.resolve())),
        "name": path.name,
        "kind": file_kind,
        "modified_utc": modified_utc,
        "size_bytes": size_bytes,
        "score": score,
        "reason": reason,
    }


def is_recent_enough(path: Path, *, max_age_hours: float | None, now: datetime | None = None) -> bool:
    if max_age_hours is None:
        return True
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    except OSError:
        return False
    current = now or datetime.now(tz=UTC)
    return modified >= current - timedelta(hours=max_age_hours)


def collect_matches(
    bridge_root: Path,
    *,
    expected_step: str | None = None,
    kind: str = "any",
    max_age_hours: float | None = None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for file_kind, folder_name, pattern in candidate_patterns(kind):
        folder = bridge_root if folder_name == "." else bridge_root / folder_name
        if not folder.is_dir():
            continue
        for path in folder.glob(pattern):
            if not path.is_file() or not is_recent_enough(path, max_age_hours=max_age_hours):
                continue
            if expected_step and file_kind != "state" and expected_step not in path.name:
                continue
            matches.append(make_match(path, root=bridge_root, file_kind=file_kind, expected_step=expected_step))
    def sort_key(item: dict[str, Any]) -> tuple[int, float, str]:
        modified = str(item.get("modified_utc") or "")
        try:
            modified_epoch = datetime.fromisoformat(modified.replace("Z", "+00:00")).timestamp()
        except ValueError:
            modified_epoch = 0.0
        return (-int(item["score"]), -modified_epoch, str(item["relative_path"]))

    return sorted(matches, key=sort_key)


def select_match(matches: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    if not matches:
        return "NOT_FOUND", None
    best = matches[0]
    tied = [
        match
        for match in matches
        if match["score"] == best["score"] and match.get("modified_utc") == best.get("modified_utc")
    ]
    status = "AMBIGUOUS" if len(tied) > 1 else "FOUND"
    selected = dict(best)
    selected["selection_reason"] = (
        "best_score_tie_selected_deterministically" if status == "AMBIGUOUS" else "best_score"
    )
    return status, selected


def _extract_markdown_status(text: str) -> str:
    status_pattern = re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:stato|status)\s*[:|]\s*([A-Z_]+)\b")
    match = status_pattern.search(text)
    if match:
        return match.group(1)
    for status in ("PASS", "FAIL", "BLOCKED", "PARTIAL", "PARTIAL_PASS", "PROVIDER_BLOCKED", "LIVE_FAILED_SAFE"):
        if re.search(rf"\b{re.escape(status)}\b", text):
            return status
    return "UNKNOWN"


def _compact_lines(text: str, *, limit: int = 12) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("-") or "PASS" in line or "FAIL" in line or "BLOCKED" in line:
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def summarize_report(path: Path | str | None) -> dict[str, Any]:
    if not path:
        return {
            "status": "NOT_FOUND",
            "report_status": "UNKNOWN",
            "summary": "",
            "manual_paste_instruction": "Incolla il report Codex/PowerShell pertinente se il Bridge non e' accessibile.",
        }
    report_path = Path(path)
    if not report_path.is_file():
        return {
            "status": "NOT_FOUND",
            "report_status": "UNKNOWN",
            "summary": "",
            "manual_paste_instruction": f"Incolla il contenuto del file atteso: {report_path.name}",
        }
    try:
        text = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "status": "ERROR",
            "report_status": "UNKNOWN",
            "summary": "",
            "error_message": redact_sensitive_text(str(exc)),
            "manual_paste_instruction": f"Incolla manualmente il contenuto di {report_path.name}.",
        }

    if report_path.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return {
                "status": "MALFORMED",
                "report_status": "UNKNOWN",
                "summary": redact_sensitive_text(f"JSON non valido: {exc.msg}"),
                "manual_paste_instruction": f"Incolla manualmente il contenuto di {report_path.name}.",
            }
        if not isinstance(payload, dict):
            return {
                "status": "UNKNOWN_SCHEMA",
                "report_status": "UNKNOWN",
                "summary": "Report JSON non oggetto.",
                "manual_paste_instruction": f"Incolla manualmente il contenuto di {report_path.name}.",
            }
        report_status = str(payload.get("status") or "UNKNOWN")
        tests = payload.get("tests") if isinstance(payload.get("tests"), list) else []
        files = payload.get("files_changed") if isinstance(payload.get("files_changed"), list) else []
        created = payload.get("files_created") if isinstance(payload.get("files_created"), list) else []
        summary = (
            f"step={payload.get('step', '')}; status={report_status}; "
            f"tests={len(tests)}; files_changed={len(files)}; files_created={len(created)}"
        )
        return {
            "status": "SUMMARY_READY",
            "report_status": report_status,
            "summary": summary,
            "next_step": redact_sensitive_text(payload.get("next_step_recommended") or payload.get("next_step") or ""),
            "manual_paste_instruction": f"Se il Bridge non e' accessibile, incolla {report_path.name}.",
        }

    report_status = _extract_markdown_status(text)
    compact = "\n".join(_compact_lines(text))
    return {
        "status": "SUMMARY_READY",
        "report_status": report_status,
        "summary": redact_sensitive_text(compact),
        "manual_paste_instruction": f"Se il Bridge non e' accessibile, incolla {report_path.name}.",
    }


def discover_reports(
    bridge_root: Path | str = DEFAULT_BRIDGE_ROOT,
    *,
    expected_step: str | None = None,
    kind: str = "any",
    max_age_hours: float | None = None,
) -> dict[str, Any]:
    root = Path(bridge_root)
    kind = kind if kind in SUPPORTED_KINDS else "any"
    packet: dict[str, Any] = {
        "status": "ERROR",
        "bridge_root": str(root),
        "expected_step": expected_step or "",
        "kind": kind,
        "searched": searched_patterns(root, kind=kind),
        "matches": [],
        "selected": None,
        "summary": {
            "status": "NOT_FOUND",
            "report_status": "UNKNOWN",
            "summary": "",
            "manual_paste_instruction": "Incolla il report/output pertinente se il Bridge non e' accessibile.",
        },
    }

    if not root.exists():
        packet["status"] = "BRIDGE_MISSING"
        return packet
    if not root.is_dir():
        packet["status"] = "ERROR"
        packet["error_message"] = "bridge_root is not a directory"
        return packet

    try:
        matches = collect_matches(
            root,
            expected_step=expected_step,
            kind=kind,
            max_age_hours=max_age_hours,
        )
    except Exception as exc:
        packet["status"] = "ERROR"
        packet["error_message"] = str(exc)
        return packet

    status, selected = select_match(matches)
    packet["status"] = status
    packet["matches"] = matches
    packet["selected"] = selected
    packet["summary"] = summarize_report(selected.get("path") if selected else None)
    return packet


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover recent ASF Bridge reports and outputs.")
    parser.add_argument("--bridge-root", default=str(DEFAULT_BRIDGE_ROOT), help="ASF Bridge root path.")
    parser.add_argument("--expected-step", help="Expected step id, for example 1030.")
    parser.add_argument("--kind", choices=sorted(SUPPORTED_KINDS), default="any", help="Report kind to search.")
    parser.add_argument("--max-age-hours", type=float, help="Optional recency filter in hours.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    packet = discover_reports(
        args.bridge_root,
        expected_step=args.expected_step,
        kind=args.kind,
        max_age_hours=args.max_age_hours,
    )
    if args.json:
        print(render_json(packet), end="")
    else:
        selected = packet.get("selected") or {}
        print(selected.get("path") or packet["status"])
    return EXIT_ERROR if packet["status"] == "ERROR" else EXIT_SUCCESS


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
