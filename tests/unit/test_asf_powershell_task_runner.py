from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_powershell_task_runner.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_powershell_task_runner", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def envelope(tmp_path: Path, **updates: object) -> dict[str, object]:
    data: dict[str, object] = {
        "task_id": "task-readonly",
        "working_directory": str(tmp_path),
        "command_kind": "native_read_only",
        "script_path": "",
        "arguments": ["git", "--no-pager", "status", "--short"],
        "allowed_paths": [str(tmp_path)],
        "forbidden_patterns": ["destructive_reset"],
        "timeout_seconds": 60,
        "idle_timeout_seconds": 10,
        "stdout_path": "out/stdout.txt",
        "stderr_path": "out/stderr.txt",
        "full_output_path": "out/full.log",
        "compact_output_path": "out/compact.md",
    }
    data.update(updates)
    return data


def validate(data: dict[str, object]):
    module = load_module()
    return module.validate_envelope(data)


def test_valid_read_only_envelope_dry_run(tmp_path: Path) -> None:
    module = load_module()
    data = envelope(tmp_path)
    validation = module.validate_envelope(data)
    packet = module.dry_run_packet(data, validation)

    assert validation.ok is True
    assert packet["status"] == "DRY_RUN_READY"
    assert packet["dry_run"] is True
    assert packet["timeout_seconds"] == 60
    assert packet["idle_timeout_seconds"] == 10
    assert packet["output_paths"]["stdout_path"].endswith("out\\stdout.txt") or packet["output_paths"][
        "stdout_path"
    ].endswith("out/stdout.txt")


def test_missing_required_field_fails_closed(tmp_path: Path) -> None:
    data = envelope(tmp_path)
    data.pop("allowed_paths")
    validation = validate(data)

    assert validation.ok is False
    assert any("Missing required fields" in error for error in validation.errors)


def test_forbidden_pattern_fails_closed(tmp_path: Path) -> None:
    data = envelope(
        tmp_path,
        arguments=["git", "reset", "--hard"],
    )
    validation = validate(data)

    assert validation.ok is False
    assert any("Forbidden pattern" in error for error in validation.errors)


def test_path_outside_scope_fails_closed(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}_outside"
    outside.mkdir()
    data = envelope(tmp_path, stdout_path=str(outside / "stdout.txt"))
    validation = validate(data)

    assert validation.ok is False
    assert any("stdout_path is outside allowed_paths" in error for error in validation.errors)


def test_timeout_and_output_paths_are_validated(tmp_path: Path) -> None:
    data = envelope(tmp_path, timeout_seconds=5, idle_timeout_seconds=6)
    validation = validate(data)

    assert validation.ok is False
    assert any("idle_timeout_seconds must not exceed timeout_seconds" in error for error in validation.errors)


def test_execute_blocks_non_whitelisted_command(tmp_path: Path) -> None:
    module = load_module()
    data = envelope(tmp_path, arguments=["pwsh", "-NoProfile", "-Command", "Write-Output hi"])
    validation = module.validate_envelope(data)
    packet = module.execute_packet(data, validation)

    assert packet["status"] == "BLOCKED"
    assert packet["classification"] == "COMMAND_NOT_WHITELISTED"


def test_source_does_not_contain_direct_os_appunti_patterns() -> None:
    content = SCRIPT.read_text(encoding="utf-8")
    forbidden = [
        "Set-" + "Cl" + "ipboard",
        "cl" + "ip.exe",
        "pyper" + "cl" + "ip",
        "win32" + "cl" + "ipboard",
        "Windows.Forms." + "Cl" + "ipboard",
        "System." + "Windows.Forms",
        "Cl" + "ipboard.Set" + "Text",
        "copy-compact-to-" + "cl" + "ipboard",
    ]
    for pattern in forbidden:
        assert pattern not in content


def test_cli_dry_run_json_is_valid(tmp_path: Path) -> None:
    envelope_path = tmp_path / "envelope.json"
    envelope_path.write_text(json.dumps(envelope(tmp_path), indent=2), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--envelope", str(envelope_path), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "DRY_RUN_READY"
