from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import asf_openai_api_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_openai_api_adapter.py"


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_default_config_uses_gpt_55() -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping")

    assert config.model == "gpt-5.5"
    assert config.reasoning_effort == "medium"
    assert config.text_verbosity == "medium"


@pytest.mark.parametrize("effort", adapter.SUPPORTED_REASONING_EFFORTS)
def test_valid_reasoning_efforts_are_accepted(effort: str) -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping", reasoning_effort=effort)

    adapter.validate_adapter_config(config)


def test_invalid_reasoning_effort_is_rejected() -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping", reasoning_effort="extreme")

    with pytest.raises(adapter.InputError):
        adapter.validate_adapter_config(config)


@pytest.mark.parametrize("verbosity", adapter.SUPPORTED_TEXT_VERBOSITY)
def test_valid_text_verbosity_values_are_accepted(verbosity: str) -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping", text_verbosity=verbosity)

    adapter.validate_adapter_config(config)


def test_payload_builder_produces_stable_responses_style_dict() -> None:
    payload = adapter.build_responses_payload(
        "ping",
        instructions="Reply tersely.",
        reasoning_effort="medium",
        text_verbosity="low",
    )

    assert payload == {
        "model": "gpt-5.5",
        "input": "ping",
        "instructions": "Reply tersely.",
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "low"},
    }


def test_dry_run_json_reports_no_network_and_redacts_key_like_input() -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping sk-proj-secretvalue123456")

    report = adapter.run_dry_run(config, environ={"OPENAI_API_KEY": "sk-proj-envsecret123456"})
    encoded = json.dumps(report, sort_keys=True)

    assert report["status"] == "DRY_RUN"
    assert report["network_performed"] is False
    assert report["environment"] == {"openai_api_key_present": True}
    assert "sk-proj-secretvalue123456" not in encoded
    assert "sk-proj-envsecret123456" not in encoded
    assert adapter.REDACTION_MARKER in encoded


def test_mock_mode_is_deterministic() -> None:
    config = adapter.OpenAIAdapterConfig(input_text="ping")

    first = adapter.run_mock(config)
    second = adapter.run_mock(config)

    assert first == second
    assert first["status"] == "MOCK_RESPONSE"
    assert first["network_performed"] is False
    assert first["mock_output_text"] == "ASF OpenAI adapter mock response."
    assert first["input_length"] == 4
    assert first["input_sha256_16"] == adapter.stable_checksum("ping")


def test_check_env_never_emits_api_key_value() -> None:
    secret = "sk-proj-thismustnotappear123456"

    report = adapter.run_check_env(environ={"OPENAI_API_KEY": secret})
    encoded = json.dumps(report, sort_keys=True)

    assert report["status"] == "ENV_CHECK"
    assert report["network_performed"] is False
    assert report["environment"] == {"openai_api_key_present": True}
    assert secret not in encoded


def test_live_mode_emits_gate_report_without_network() -> None:
    result = run_script("--mode", "live", "--input", adapter.DEFAULT_LIVE_SMOKE_INPUT)

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["status"] == "skipped"
    assert data["legacy_status"] == "LIVE_SMOKE"
    assert data["classification"] == "credential_missing"
    assert data["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert data["error_category"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert data["network_performed"] is False
    assert data["network_call_attempted"] is False
    assert data["network_call_performed"] is False
    assert data["network_call_count"] == 0
    assert data["store"] is False
    assert data["runtime_artifact_path"] is None


def test_cli_writes_dry_run_json_without_requiring_key(tmp_path: Path) -> None:
    output = tmp_path / "dry_run.json"

    result = run_script("--mode", "dry-run", "--input", "ping", "--output-json", output)

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["status"] == "DRY_RUN"
    assert data["network_performed"] is False
    assert data["payload"]["input"] == "ping"
    assert data["payload"]["model"] == "gpt-5.5"


def test_cli_help_has_no_api_key_argument() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--output-json" in result.stdout
    assert "--output-markdown" in result.stdout
    assert "api-key" not in result.stdout.casefold()
