from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

REQUIRED_FIELDS = (
    "task_id",
    "working_directory",
    "allowed_paths",
    "forbidden_patterns",
    "timeout_seconds",
    "stdout_path",
    "stderr_path",
    "full_output_path",
    "compact_output_path",
)

READ_ONLY_PREFIXES = (
    ("git", "--no-pager", "status"),
    ("git", "--no-pager", "diff", "--check"),
    ("python", "scripts/check_workflow_health.py"),
    ("python", "-m", "pytest"),
    ("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\\verify.ps1"),
    ("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1"),
)


@dataclass(frozen=True)
class RunnerValidation:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    command: tuple[str, ...]
    working_directory: Path | None
    output_paths: dict[str, Path]
    timeout_seconds: int
    idle_timeout_seconds: int


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
        return [text for item in value if (text := compact_string(item))]
    text = compact_string(value)
    return [text] if text else []


def compact_int(value: Any, *, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Unable to read envelope: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Envelope is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Envelope JSON must be an object.")
    return payload


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_existing_dir(value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = repo_root() / path
    try:
        resolved = path.resolve()
    except OSError:
        return None
    return resolved if resolved.is_dir() else None


def resolve_path(base: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def allowed_roots(base: Path, values: list[str]) -> list[Path]:
    roots: list[Path] = []
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = base / path
        try:
            roots.append(path.resolve())
        except OSError:
            continue
    return list(dict.fromkeys(roots))


def path_allowed(path: Path, roots: list[Path]) -> bool:
    return any(path == root or is_relative_to(path, root) for root in roots)


def default_forbidden_patterns() -> list[str]:
    os_appunti_patterns = [
        "Set-" + "Cl" + "ipboard",
        "cl" + "ip.exe",
        "pyper" + "cl" + "ip",
        "win32" + "cl" + "ipboard",
        "Windows.Forms." + "Cl" + "ipboard",
        "System." + "Windows.Forms",
        "Cl" + "ipboard.Set" + "Text",
        "Set" + "Text(",
        "copy-compact-to-" + "cl" + "ipboard",
    ]
    command_patterns = [
        "git " + "reset",
        "git " + "clean",
        "git " + "rebase",
        "git " + "checkout --",
        "git " + "push",
        "git " + "merge",
        "gh pr " + "create",
        "gh pr " + "merge",
        "deploy",
    ]
    return command_patterns + os_appunti_patterns


def missing_fields(raw: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in raw:
            missing.append(field)
            continue
        value = raw[field]
        if field in {"allowed_paths", "forbidden_patterns"}:
            if not compact_list(value):
                missing.append(field)
        elif compact_string(value) == "":
            missing.append(field)
    if not compact_list(raw.get("arguments")) and not compact_string(raw.get("script_path")):
        missing.append("arguments or script_path")
    return missing


def command_from_envelope(raw: dict[str, Any]) -> tuple[str, ...]:
    args = tuple(compact_list(raw.get("arguments")))
    if args:
        return args
    script_path = compact_string(raw.get("script_path"))
    if script_path:
        return ("pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path)
    return ()


def is_whitelisted_read_only(command: tuple[str, ...]) -> bool:
    normalized = tuple(part.replace("/", "\\") if part.endswith(".ps1") else part for part in command)
    for prefix in READ_ONLY_PREFIXES:
        if len(normalized) >= len(prefix) and normalized[: len(prefix)] == prefix:
            return True
    return False


def validate_envelope(raw: dict[str, Any]) -> RunnerValidation:
    errors: list[str] = []
    warnings: list[str] = []
    output_paths: dict[str, Path] = {}

    missing = missing_fields(raw)
    if missing:
        errors.append("Missing required fields: " + ", ".join(missing))
        return RunnerValidation(False, tuple(errors), tuple(warnings), (), None, {}, 0, 0)

    working_directory = resolve_existing_dir(compact_string(raw.get("working_directory")))
    if working_directory is None:
        errors.append("working_directory must exist and be a directory.")
        return RunnerValidation(False, tuple(errors), tuple(warnings), (), None, {}, 0, 0)

    roots = allowed_roots(working_directory, compact_list(raw.get("allowed_paths")))
    if not roots:
        errors.append("allowed_paths did not resolve to any usable root.")
    elif not path_allowed(working_directory, roots):
        errors.append("working_directory is outside allowed_paths.")

    command = command_from_envelope(raw)
    command_text = " ".join(command)
    patterns = compact_list(raw.get("forbidden_patterns")) + default_forbidden_patterns()
    for pattern in patterns:
        if pattern and pattern.casefold() in command_text.casefold():
            errors.append(f"Forbidden pattern detected in command: {pattern}")

    script_path = compact_string(raw.get("script_path"))
    if script_path:
        resolved_script = resolve_path(working_directory, script_path)
        if not path_allowed(resolved_script, roots):
            errors.append(f"script_path is outside allowed_paths: {script_path}")

    for field in ("stdout_path", "stderr_path", "full_output_path", "compact_output_path"):
        resolved = resolve_path(working_directory, compact_string(raw.get(field)))
        output_paths[field] = resolved
        if not path_allowed(resolved, roots):
            errors.append(f"{field} is outside allowed_paths: {raw.get(field)}")

    timeout_seconds = compact_int(raw.get("timeout_seconds"))
    idle_timeout_seconds = compact_int(raw.get("idle_timeout_seconds"))
    if timeout_seconds <= 0:
        errors.append("timeout_seconds must be positive.")
    if idle_timeout_seconds < 0:
        errors.append("idle_timeout_seconds must not be negative.")
    if idle_timeout_seconds and timeout_seconds and idle_timeout_seconds > timeout_seconds:
        errors.append("idle_timeout_seconds must not exceed timeout_seconds.")
    if idle_timeout_seconds:
        warnings.append("idle_timeout_seconds is recorded by this foundation runner; execution enforces absolute timeout.")

    return RunnerValidation(
        not errors,
        tuple(errors),
        tuple(warnings),
        command,
        working_directory,
        output_paths,
        timeout_seconds,
        idle_timeout_seconds,
    )


def load_recovery_classifier() -> Any:
    path = Path(__file__).with_name("asf_powershell_recovery_classifier.py")
    spec = importlib.util.spec_from_file_location("asf_powershell_recovery_classifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load recovery classifier: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def classify_output(*, stdout: str, stderr: str, command: tuple[str, ...], exit_code: int | None) -> dict[str, Any]:
    classifier = load_recovery_classifier()
    return classifier.classify_recovery(
        classifier.RecoveryInput(
            stdout=stdout,
            stderr=stderr,
            command_text=" ".join(command),
            exit_code=exit_code,
        )
    )


def write_outputs(paths: dict[str, Path], *, stdout: str, stderr: str, packet: dict[str, Any]) -> None:
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["stdout_path"].write_text(stdout, encoding="utf-8")
    paths["stderr_path"].write_text(stderr, encoding="utf-8")
    full = "\n".join(
        [
            "ASF PowerShell Task Runner full output",
            "",
            "STDOUT:",
            stdout,
            "",
            "STDERR:",
            stderr,
            "",
            "RESULT:",
            json.dumps(packet, indent=2, sort_keys=True),
            "",
        ]
    )
    compact = "\n".join(
        [
            "# ASF PowerShell Task Runner",
            "",
            f"- status: `{packet['status']}`",
            f"- exit_code: `{packet['exit_code']}`",
            f"- classification: `{packet['classification']}`",
            "",
        ]
    )
    paths["full_output_path"].write_text(full, encoding="utf-8")
    paths["compact_output_path"].write_text(compact, encoding="utf-8")


def dry_run_packet(raw: dict[str, Any], validation: RunnerValidation) -> dict[str, Any]:
    return {
        "task_id": compact_string(raw.get("task_id")),
        "status": "DRY_RUN_READY" if validation.ok else "BLOCKED",
        "dry_run": True,
        "command": list(validation.command),
        "working_directory": str(validation.working_directory) if validation.working_directory else None,
        "timeout_seconds": validation.timeout_seconds,
        "idle_timeout_seconds": validation.idle_timeout_seconds,
        "output_paths": {key: str(path) for key, path in validation.output_paths.items()},
        "exit_code": None,
        "classification": "DRY_RUN_VALIDATED" if validation.ok else "VALIDATION_FAILED",
        "validation_errors": list(validation.errors),
        "warnings": list(validation.warnings),
    }


def execute_packet(raw: dict[str, Any], validation: RunnerValidation) -> dict[str, Any]:
    if not validation.ok:
        return dry_run_packet(raw, validation) | {"dry_run": False}
    if not is_whitelisted_read_only(validation.command):
        return {
            "task_id": compact_string(raw.get("task_id")),
            "status": "BLOCKED",
            "dry_run": False,
            "command": list(validation.command),
            "working_directory": str(validation.working_directory),
            "timeout_seconds": validation.timeout_seconds,
            "idle_timeout_seconds": validation.idle_timeout_seconds,
            "output_paths": {key: str(path) for key, path in validation.output_paths.items()},
            "exit_code": None,
            "classification": "COMMAND_NOT_WHITELISTED",
            "validation_errors": ["Execution is limited to whitelisted read-only commands."],
            "warnings": list(validation.warnings),
        }

    try:
        completed = subprocess.run(
            list(validation.command),
            cwd=validation.working_directory,
            text=True,
            capture_output=True,
            timeout=validation.timeout_seconds,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
        classification = classify_output(stdout=stdout, stderr=stderr, command=validation.command, exit_code=exit_code)
        status = "PASS" if exit_code == 0 else "FAILED"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        exit_code = None
        classifier = load_recovery_classifier()
        classification = classifier.classify_recovery(
            classifier.RecoveryInput(
                stdout=stdout,
                stderr=stderr,
                command_text=" ".join(validation.command),
                timed_out=True,
            )
        )
        status = "TIMEOUT"

    packet = {
        "task_id": compact_string(raw.get("task_id")),
        "status": status,
        "dry_run": False,
        "command": list(validation.command),
        "working_directory": str(validation.working_directory),
        "timeout_seconds": validation.timeout_seconds,
        "idle_timeout_seconds": validation.idle_timeout_seconds,
        "output_paths": {key: str(path) for key, path in validation.output_paths.items()},
        "exit_code": exit_code,
        "classification": classification["classification"],
        "recovery": classification,
        "validation_errors": [],
        "warnings": list(validation.warnings),
    }
    write_outputs(validation.output_paths, stdout=stdout, stderr=stderr, packet=packet)
    return packet


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and optionally run a constrained PowerShell task envelope.")
    parser.add_argument("--envelope", required=True, help="Task envelope JSON path.")
    parser.add_argument("--execute", action="store_true", help="Execute only whitelisted read-only commands.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        raw = load_json_object(Path(args.envelope))
    except ValueError as exc:
        packet = {
            "task_id": "",
            "status": "BLOCKED",
            "dry_run": not args.execute,
            "command": [],
            "validation_errors": [str(exc)],
            "warnings": [],
            "exit_code": None,
            "classification": "VALIDATION_FAILED",
        }
        print(render_json(packet), end="")
        return EXIT_INPUT_ERROR

    validation = validate_envelope(raw)
    packet = execute_packet(raw, validation) if args.execute else dry_run_packet(raw, validation)
    print(render_json(packet), end="")
    return EXIT_SUCCESS if packet["status"] in {"DRY_RUN_READY", "PASS"} else EXIT_INPUT_ERROR


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
