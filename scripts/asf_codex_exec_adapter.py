from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

DEFAULT_MODE = "dry-run"
SUPPORTED_MODES = {"dry-run"}


@dataclass(frozen=True)
class CodexExecRequest:
    step_id: str
    prompt_path: Path
    working_directory: Path
    mode: str = DEFAULT_MODE
    allowed_paths: tuple[Path, ...] = ()
    forbidden_actions: tuple[str, ...] = ()
    execute: bool = False
    allow_execute: bool = False
    envelope_output: Path | None = None
    report_output: Path | None = None


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return []
    if isinstance(value, list | tuple | set):
        items: list[str] = []
        for item in value:
            text = compact_string(item)
            if text:
                items.append(text)
        return items
    text = compact_string(value)
    return [text] if text else []


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_path(base: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def resolve_allowed_paths(base: Path, values: tuple[str, ...], prompt_path: Path) -> tuple[Path, ...]:
    if not values:
        return tuple(dict.fromkeys([base.resolve(), prompt_path.parent.resolve()]))
    resolved: list[Path] = []
    for value in values:
        resolved.append(resolve_path(base, value))
    return tuple(dict.fromkeys(resolved))


def path_allowed(path: Path, allowed_paths: tuple[Path, ...]) -> bool:
    return any(path == root or is_relative_to(path, root) for root in allowed_paths)


def dangerous_action_patterns() -> tuple[str, ...]:
    return (
        "git " + "reset",
        "git " + "clean",
        "git " + "rebase",
        "git " + "checkout --",
        "git " + "push",
        "git " + "merge",
        "gh pr " + "create",
        "gh pr " + "merge",
        "gh " + "release",
        "de" + "ploy",
        "secret",
        "credential",
    )


def detected_forbidden_actions(actions: tuple[str, ...]) -> list[str]:
    detected: list[str] = []
    patterns = dangerous_action_patterns()
    for action in actions:
        lowered = action.casefold()
        if any(pattern.casefold() in lowered for pattern in patterns):
            detected.append(action)
    return detected


def build_codex_command(prompt_path: Path, working_directory: Path) -> list[str]:
    return [
        "codex",
        "exec",
        "--cd",
        str(working_directory),
        "--json",
        "--prompt-file",
        str(prompt_path),
    ]


def validate_request(request: CodexExecRequest) -> tuple[list[str], tuple[Path, ...]]:
    errors: list[str] = []
    root = repo_root().resolve()
    prompt_path = request.prompt_path.resolve()
    working_directory = request.working_directory.resolve()
    allowed_paths = request.allowed_paths or tuple(dict.fromkeys([working_directory, prompt_path.parent.resolve()]))

    if request.mode not in SUPPORTED_MODES:
        errors.append(f"Unsupported mode: {request.mode}")
    if not prompt_path.is_file():
        errors.append(f"prompt_path does not exist: {prompt_path}")
    if not working_directory.is_dir():
        errors.append(f"working_directory does not exist: {working_directory}")
    elif not (working_directory == root or is_relative_to(working_directory, root)):
        errors.append(f"working_directory is outside repository: {working_directory}")
    if not path_allowed(prompt_path, allowed_paths):
        errors.append(f"prompt_path is outside allowed_paths: {prompt_path}")

    forbidden = detected_forbidden_actions(request.forbidden_actions)
    if forbidden:
        errors.append("Forbidden action detected: " + ", ".join(forbidden))

    if request.execute and not request.allow_execute:
        errors.append("execute=true requires explicit allow-execute approval.")
    if request.execute and request.allow_execute:
        errors.append("Real Codex execution remains disabled in step 0980-1010.")

    return errors, allowed_paths


def write_json(path: Path, packet: dict[str, Any]) -> Path:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return resolved


def write_report(path: Path, packet: dict[str, Any]) -> Path:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ASF Codex Exec Adapter Dry Run",
        "",
        f"- step_id: `{packet['step_id']}`",
        f"- status: `{packet['status']}`",
        f"- mode: `{packet['mode']}`",
        f"- execute_enabled: `{str(packet['execute_enabled']).lower()}`",
        f"- prompt_path: `{packet['prompt_path']}`",
        f"- working_directory: `{packet['working_directory']}`",
        "",
        "The command is prepared for review only and is not run by this adapter in this step.",
        "",
    ]
    resolved.write_text("\n".join(lines), encoding="utf-8")
    return resolved


def prepare_codex_exec(request: CodexExecRequest) -> dict[str, Any]:
    prompt_path = request.prompt_path.resolve()
    working_directory = request.working_directory.resolve()
    errors, allowed_paths = validate_request(request)
    status = "CODEX_BLOCKED" if errors else "CODEX_DRY_RUN_DONE"
    command = build_codex_command(prompt_path, working_directory) if not errors else []
    packet: dict[str, Any] = {
        "step_id": request.step_id,
        "mode": DEFAULT_MODE,
        "codex_command": command,
        "prompt_path": str(prompt_path),
        "working_directory": str(working_directory),
        "allowed_paths": [str(path) for path in allowed_paths],
        "forbidden_actions": list(request.forbidden_actions),
        "execute_enabled": False,
        "requires_alberto": False,
        "status": status,
        "next_action": "REVIEW_REQUESTED" if not errors else "STOP",
        "validation_errors": errors,
    }

    if request.envelope_output:
        packet["envelope_path"] = str(write_json(request.envelope_output, packet))
    if request.report_output:
        packet["dry_run_report_path"] = str(write_report(request.report_output, packet))
    return packet


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a dry-run Codex exec envelope without running Codex.")
    parser.add_argument("--prompt", required=True, help="Prompt Markdown path.")
    parser.add_argument("--working-directory", required=True, help="Repository working directory.")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=sorted(SUPPORTED_MODES), help="Adapter mode.")
    parser.add_argument("--step-id", default="0990", help="Step id for the output envelope.")
    parser.add_argument("--allowed-path", action="append", default=[], help="Allowed path. Can be repeated.")
    parser.add_argument("--forbidden-action", action="append", default=[], help="Detected forbidden action. Can be repeated.")
    parser.add_argument("--execute", action="store_true", help="Request real execution; blocked in this step.")
    parser.add_argument("--allow-execute", action="store_true", help="Reserved future approval flag; still blocked here.")
    parser.add_argument("--envelope-output", help="Optional JSON envelope output path.")
    parser.add_argument("--report-output", help="Optional Markdown dry-run report output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def request_from_args(args: argparse.Namespace) -> CodexExecRequest:
    working_directory = Path(args.working_directory).resolve()
    prompt_path = Path(args.prompt).resolve()
    allowed = resolve_allowed_paths(working_directory, tuple(compact_list(args.allowed_path)), prompt_path)
    return CodexExecRequest(
        step_id=compact_string(args.step_id) or "0990",
        prompt_path=prompt_path,
        working_directory=working_directory,
        mode=args.mode,
        allowed_paths=allowed,
        forbidden_actions=tuple(compact_list(args.forbidden_action)),
        execute=bool(args.execute),
        allow_execute=bool(args.allow_execute),
        envelope_output=Path(args.envelope_output) if args.envelope_output else None,
        report_output=Path(args.report_output) if args.report_output else None,
    )


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    packet = prepare_codex_exec(request_from_args(args))
    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["status"])
    return EXIT_SUCCESS if packet["status"] == "CODEX_DRY_RUN_DONE" else EXIT_INPUT_ERROR


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
