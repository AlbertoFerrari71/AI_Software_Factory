from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_gpt_prompt_generator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_gpt_prompt_generator", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_plan(path: Path, **updates: object) -> Path:
    payload: dict[str, object] = {
        "step_id": "0980",
        "title": "GPT Prompt Generator API Adapter",
        "objective": "Generate a deterministic Codex prompt in mock mode.",
        "risk_level": "L1",
        "phase": "unit-test",
        "allowed_paths": ["scripts", "tests/unit"],
        "forbidden_actions": [],
    }
    payload.update(updates)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_mock_mode_generates_deterministic_prompt(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"

    first_packet = module.generate_prompt(plan, output_path=first, mode="mock")
    second_packet = module.generate_prompt(plan, output_path=second, mode="mock")

    assert first_packet["status"] == "PROMPT_READY"
    assert first_packet["controlled_status"] == "MOCK_SUCCESS"
    assert second_packet["status"] == "PROMPT_READY"
    assert second_packet["controlled_status"] == "MOCK_SUCCESS"
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")
    assert "generator_mode: mock" in first.read_text(encoding="utf-8")


def test_live_mode_is_disabled_by_default(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    output = tmp_path / "prompt.md"

    packet = module.generate_prompt(plan, output_path=output, mode="live", environ={})

    assert packet["status"] == "LIVE_SKIPPED_NO_APPROVAL"
    assert packet["live_call_attempted"] is False
    assert packet["fallback_mode"] == "mock"
    assert output.is_file()


def test_live_mode_with_future_flag_still_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    output = tmp_path / "prompt.md"

    packet = module.generate_prompt(plan, output_path=output, mode="live", allow_live=True, environ={})

    assert packet["status"] == "LIVE_SKIPPED_NO_API_KEY"
    assert packet["live_call_attempted"] is False
    assert packet["fallback_mode"] == "mock"
    assert output.is_file()


def test_mock_mode_does_not_require_provider_secret(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")

    packet = module.generate_prompt(plan, output_path=tmp_path / "prompt.md", mode="mock")

    assert packet["status"] == "PROMPT_READY"
    assert packet["live_enabled"] is False


def test_output_json_contains_required_fields_and_valid_prompt_path(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    packet = module.generate_prompt(plan, output_path=tmp_path / "prompt.md", mode="mock")
    payload = json.loads(module.render_json(packet))

    for field in [
        "step_id",
        "mode",
        "selected_model",
        "provider",
        "live_enabled",
        "prompt_path",
        "risk_level",
        "requires_alberto",
        "status",
        "next_action",
    ]:
        assert field in payload

    assert Path(payload["prompt_path"]).is_file()
    assert payload["mode"] == "mock"
    assert payload["next_action"] == "CODEX_DRY_RUN_READY"


def test_markdown_plan_is_accepted(tmp_path: Path) -> None:
    module = load_module()
    plan = tmp_path / "0980-plan.md"
    plan.write_text("# 0980 GPT Prompt Generator\n\nCreate mock prompt.\n", encoding="utf-8")

    packet = module.generate_prompt(plan, output_path=tmp_path / "prompt.md", mode="mock")

    assert packet["step_id"] == "0980"
    assert packet["source_format"] == "markdown"


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


def test_cli_mock_json_works(tmp_path: Path) -> None:
    plan = write_plan(tmp_path / "plan.json")
    output = tmp_path / "generated.md"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--plan", str(plan), "--mode", "mock", "--output", str(output), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PROMPT_READY"
    assert payload["controlled_status"] == "MOCK_SUCCESS"
    assert output.is_file()
