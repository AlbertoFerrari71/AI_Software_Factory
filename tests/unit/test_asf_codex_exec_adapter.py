from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_exec_adapter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_codex_exec_adapter", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def prompt(tmp_path: Path) -> Path:
    path = tmp_path / "prompt.md"
    path.write_text("# Prompt\n\nDry-run only.\n", encoding="utf-8")
    return path


def make_request(tmp_path: Path, **updates: object):
    module = load_module()
    request = {
        "step_id": "0990",
        "prompt_path": prompt(tmp_path),
        "working_directory": ROOT,
        "allowed_paths": (ROOT, tmp_path),
        "envelope_output": tmp_path / "envelope.json",
        "report_output": tmp_path / "report.md",
    }
    request.update(updates)
    return module.CodexExecRequest(**request)


def test_dry_run_generates_codex_exec_command_without_running(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path))

    assert packet["status"] == "CODEX_DRY_RUN_DONE"
    assert packet["execute_enabled"] is False
    assert packet["codex_command"][:2] == ["codex", "exec"]
    assert "--cd" in packet["codex_command"]
    assert Path(packet["envelope_path"]).is_file()
    assert Path(packet["dry_run_report_path"]).is_file()


def test_execute_mode_without_approval_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path, execute=True, allow_execute=False))

    assert packet["status"] == "CODEX_BLOCKED"
    assert any("allow-execute" in error for error in packet["validation_errors"])


def test_execute_mode_with_future_approval_still_does_not_run(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path, execute=True, allow_execute=True))

    assert packet["status"] == "CODEX_BLOCKED"
    assert packet["execute_enabled"] is False
    assert any("disabled" in error for error in packet["validation_errors"])


def test_missing_prompt_fails(tmp_path: Path) -> None:
    module = load_module()
    missing = tmp_path / "missing.md"
    packet = module.prepare_codex_exec(
        make_request(tmp_path, prompt_path=missing, allowed_paths=(ROOT, tmp_path))
    )

    assert packet["status"] == "CODEX_BLOCKED"
    assert any("prompt_path does not exist" in error for error in packet["validation_errors"])


def test_working_directory_outside_repo_fails(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path, working_directory=tmp_path))

    assert packet["status"] == "CODEX_BLOCKED"
    assert any("outside repository" in error for error in packet["validation_errors"])


def test_prompt_path_outside_allowed_paths_fails(tmp_path: Path) -> None:
    module = load_module()
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_prompt = prompt(outside)
    packet = module.prepare_codex_exec(
        make_request(tmp_path, prompt_path=outside_prompt, allowed_paths=(ROOT,))
    )

    assert packet["status"] == "CODEX_BLOCKED"
    assert any("outside allowed_paths" in error for error in packet["validation_errors"])


def test_forbidden_action_fails(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path, forbidden_actions=("git " + "push origin main",)))

    assert packet["status"] == "CODEX_BLOCKED"
    assert any("Forbidden action" in error for error in packet["validation_errors"])


def test_output_envelope_is_valid(tmp_path: Path) -> None:
    module = load_module()
    packet = module.prepare_codex_exec(make_request(tmp_path))
    envelope = json.loads(Path(packet["envelope_path"]).read_text(encoding="utf-8"))

    for field in [
        "step_id",
        "mode",
        "codex_command",
        "prompt_path",
        "working_directory",
        "execute_enabled",
        "requires_alberto",
        "status",
        "next_action",
    ]:
        assert field in envelope


def test_source_does_not_contain_direct_os_appunti_patterns() -> None:
    content = SCRIPT.read_text(encoding="utf-8")
    forbidden = [
        "Set-" + "Cl" + "ipboard",
        "cl" + "ip.exe",
        "cl" + "ip",
        "pyper" + "cl" + "ip",
        "win32" + "cl" + "ipboard",
        "Cl" + "ipboard",
        "Windows.Forms." + "Cl" + "ipboard",
        "System." + "Windows.Forms",
        "Cl" + "ipboard.Set" + "Text",
        "Set" + "Text(",
        "copy-compact-to-" + "cl" + "ipboard",
    ]
    for pattern in forbidden:
        assert pattern not in content


def test_cli_dry_run_json_works(tmp_path: Path) -> None:
    prompt_path = prompt(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--prompt",
            str(prompt_path),
            "--working-directory",
            str(ROOT),
            "--mode",
            "dry-run",
            "--allowed-path",
            str(ROOT),
            "--allowed-path",
            str(tmp_path),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "CODEX_DRY_RUN_DONE"
