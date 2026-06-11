from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_supervised_loop_smoke.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_supervised_loop_smoke", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_positive_scenario_reaches_completed(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_smoke(tmp_path)

    assert result["status"] == "COMPLETED"
    assert result["final_state"] == "COMPLETED"
    assert result["scenarios"]["positive"]["decision"] == "PASS"
    assert "CODEX_DONE" in result["states"]


def test_smoke_covers_ask_fix_and_stop_scenarios(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_smoke(tmp_path)

    assert result["scenarios"]["ask_alberto"]["decision"] == "ASK_ALBERTO"
    assert result["scenarios"]["fix"]["decision"] == "FIX"
    assert result["scenarios"]["stop"]["decision"] == "STOP"


def test_state_json_and_event_log_are_written_under_tmp_root(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_smoke(tmp_path)
    state_path = Path(result["state_path"])
    event_log = Path(result["event_log_path"])

    assert state_path.is_file()
    assert event_log.is_file()
    assert json.loads(state_path.read_text(encoding="utf-8"))["state"] == "COMPLETED"
    lines = [line for line in event_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 10
    assert result["writes_within_smoke_root"] is True


def test_smoke_uses_required_components_in_mock_or_dry_run(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_smoke(tmp_path)
    components = result["components"]

    assert components["gpt_prompt_generator"]["mode"] == "mock"
    assert components["gpt_prompt_generator"]["live_enabled"] is False
    assert components["codex_exec_adapter"]["status"] == "CODEX_DRY_RUN_DONE"
    assert components["powershell_task_runner"]["status"] == "DRY_RUN_READY"
    assert components["recovery_classifier"]["classification"] == "POWERSHELL_PARSE_ERROR"
    assert components["verification_selector"]["selected_profile"] in {"FULL", "ESCALATED"}


def test_cli_json_works(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "COMPLETED"
