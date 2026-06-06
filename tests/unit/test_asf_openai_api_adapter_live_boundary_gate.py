from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts import asf_openai_api_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_openai_api_adapter.py"
FAKE_KEY = "sk-proj-testliveboundary123456"


def run_script(*args: str | Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    clean_env = os.environ.copy()
    clean_env.pop("OPENAI_API_KEY", None)
    clean_env.pop("ASF_OPENAI_LIVE_ENABLED", None)
    if env:
        clean_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=clean_env,
    )


def base_config(**overrides: object) -> adapter.OpenAIAdapterConfig:
    values: dict[str, object] = {"mode": "live", "input_text": adapter.DEFAULT_LIVE_SMOKE_INPUT}
    values.update(overrides)
    return adapter.OpenAIAdapterConfig(**values)


def encode(report: dict[str, object]) -> str:
    return json.dumps(report, sort_keys=True)


def test_absent_credential_blocks_live_boundary_without_network() -> None:
    report = adapter.run_live(base_config(), environ={})

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert report["error_category"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert "OPENAI_API_KEY" in report["missing_gates"]
    assert report["openai_api_key_present"] is False
    assert report["network_performed"] is False
    assert report["network_call_attempted"] is False
    assert report["network_call_performed"] is False
    assert report["network_call_count"] == 0


def test_credential_presence_is_detected_without_value_leakage() -> None:
    report = adapter.run_live(base_config(), environ={"OPENAI_API_KEY": FAKE_KEY})
    encoded = encode(report)

    assert report["openai_api_key_present"] is True
    assert report["credential_source"] == "OPENAI_API_KEY"
    assert report["secret_value_logged"] is False
    assert FAKE_KEY not in encoded


def test_missing_live_env_flag_blocks_after_credential_gate() -> None:
    report = adapter.run_live(base_config(), environ={"OPENAI_API_KEY": FAKE_KEY})

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert "ASF_OPENAI_LIVE_ENABLED=1" in report["missing_gates"]
    assert report["gate_inputs"]["asf_openai_live_enabled"] is False


def test_missing_allow_live_flag_blocks_after_env_gate() -> None:
    report = adapter.run_live(
        base_config(),
        environ={"OPENAI_API_KEY": FAKE_KEY, "ASF_OPENAI_LIVE_ENABLED": "1"},
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert "--allow-live" in report["missing_gates"]
    assert report["gate_inputs"]["asf_openai_live_enabled"] is True
    assert report["gate_inputs"]["allow_live_flag"] is False


def test_missing_confirmation_blocks_after_allow_live_flag() -> None:
    report = adapter.run_live(
        base_config(allow_live=True),
        environ={"OPENAI_API_KEY": FAKE_KEY, "ASF_OPENAI_LIVE_ENABLED": "1"},
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert f"--live-confirm {adapter.LIVE_CONFIRMATION_VALUE}" in report["missing_gates"]
    assert report["gate_inputs"]["allow_live_flag"] is True
    assert report["gate_inputs"]["live_confirmation_matches"] is False


def test_all_gates_present_gate_only_reports_ready_without_call() -> None:
    report = adapter.run_live(
        base_config(allow_live=True, live_confirm=adapter.LIVE_CONFIRMATION_VALUE, gate_only=True),
        environ={"OPENAI_API_KEY": FAKE_KEY, "ASF_OPENAI_LIVE_ENABLED": "1"},
    )

    assert report["decision"] == adapter.LIVE_SMOKE_READY_FOR_CALL
    assert report["missing_gates"] == []
    assert report["network_performed"] is False
    assert report["network_call_attempted"] is False
    assert report["network_call_performed"] is False
    assert report["network_call_count"] == 0
    assert report["live_request_plan"]["api_surface"] == "responses"
    assert report["live_request_plan"]["endpoint"] == "/v1/responses"
    assert report["live_request_plan"]["model"] == "gpt-5.5"
    assert report["live_request_plan"]["store"] is False
    assert report["live_request_plan"]["network_call_performed"] is False


def test_redaction_removes_key_like_and_secret_like_values_from_visible_output() -> None:
    secret_input = "payload sk-proj-visibleinput123456 Authorization: Bearer secretbearertoken123456"
    report = adapter.run_live(
        base_config(
            input_text=secret_input,
            instructions="api_key=supersecretvalue123456",
            allow_live=True,
            live_confirm=adapter.LIVE_CONFIRMATION_VALUE,
        ),
        environ={"OPENAI_API_KEY": FAKE_KEY, "ASF_OPENAI_LIVE_ENABLED": "1"},
    )
    encoded = encode(report)

    assert "sk-proj-visibleinput123456" not in encoded
    assert "secretbearertoken123456" not in encoded
    assert "supersecretvalue123456" not in encoded
    assert FAKE_KEY not in encoded
    assert adapter.REDACTION_MARKER in encoded
    assert adapter.SECRET_REDACTION_MARKER in encoded
    assert "tiny non-sensitive live smoke prompt" in report["missing_gates"]


def test_cli_live_gate_report_never_requires_real_api_key_or_network() -> None:
    result = run_script(
        "--mode",
        "live",
        "--input",
        adapter.DEFAULT_LIVE_SMOKE_INPUT,
        "--allow-live",
        "--live-confirm",
        adapter.LIVE_CONFIRMATION_VALUE,
        "--gate-only",
        env={"OPENAI_API_KEY": FAKE_KEY, "ASF_OPENAI_LIVE_ENABLED": "1"},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["decision"] == adapter.LIVE_SMOKE_READY_FOR_CALL
    assert data["network_performed"] is False
    assert data["network_call_attempted"] is False
    assert data["network_call_performed"] is False
    assert data["network_call_count"] == 0
    assert FAKE_KEY not in result.stdout
    assert FAKE_KEY not in result.stderr


def test_adapter_uses_no_openai_sdk_or_requests_dependency_for_live_gate() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    for forbidden in ["requests", "openai import", "import openai"]:
        assert forbidden not in content
