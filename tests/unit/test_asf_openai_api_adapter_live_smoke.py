from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import asf_openai_api_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
FAKE_KEY = "sk-proj-testlivesmoke123456"


def live_config(**overrides: object) -> adapter.OpenAIAdapterConfig:
    values: dict[str, object] = {
        "mode": "live",
        "input_text": adapter.DEFAULT_LIVE_SMOKE_INPUT,
        "allow_live": True,
        "live_confirm": adapter.LIVE_CONFIRMATION_VALUE,
        "max_output_tokens": 32,
        "reasoning_effort": "none",
        "text_verbosity": "low",
    }
    values.update(overrides)
    return adapter.OpenAIAdapterConfig(**values)


def live_env(**overrides: str) -> dict[str, str]:
    values = {
        "OPENAI_API_KEY": FAKE_KEY,
        "ASF_OPENAI_LIVE_ENABLED": "1",
    }
    values.update(overrides)
    return values


def artifact_path(name: str = "result.json") -> str:
    return f"tmp/{name}"


def encode(report: dict[str, object]) -> str:
    return json.dumps(report, sort_keys=True)


def success_response(output_text: str = "ASF_LIVE_SMOKE_OK") -> adapter.HttpJsonResponse:
    return adapter.HttpJsonResponse(
        status_code=200,
        body_text=json.dumps(
            {
                "id": "resp_test_123",
                "object": "response",
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": output_text,
                            }
                        ]
                    }
                ],
            }
        ),
    )


def test_all_gates_missing_reports_missing_gates_and_no_network() -> None:
    calls: list[dict[str, object]] = []

    def fake_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        calls.append({"endpoint": endpoint, "payload": payload, "api_key": api_key, "timeout": timeout})
        return success_response()

    report = adapter.run_live(
        adapter.OpenAIAdapterConfig(mode="live", input_text=adapter.DEFAULT_LIVE_SMOKE_INPUT),
        environ={},
        http_post_json=fake_post,
    )

    assert calls == []
    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert report["network_call_attempted"] is False
    assert report["network_call_performed"] is False
    assert report["network_call_count"] == 0
    assert "OPENAI_API_KEY" in report["missing_gates"]
    assert "ASF_OPENAI_LIVE_ENABLED=1" in report["missing_gates"]
    assert "--allow-live" in report["missing_gates"]
    assert f"--live-confirm {adapter.LIVE_CONFIRMATION_VALUE}" in report["missing_gates"]


def test_api_key_present_but_live_flag_missing_reports_no_network() -> None:
    report = adapter.run_live(
        live_config(),
        environ={"OPENAI_API_KEY": FAKE_KEY},
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert report["network_call_attempted"] is False
    assert "ASF_OPENAI_LIVE_ENABLED=1" in report["missing_gates"]
    assert FAKE_KEY not in encode(report)


def test_env_live_flag_present_but_confirmation_missing_reports_no_network() -> None:
    report = adapter.run_live(
        live_config(live_confirm=None),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert report["network_call_attempted"] is False
    assert f"--live-confirm {adapter.LIVE_CONFIRMATION_VALUE}" in report["missing_gates"]


def test_all_gates_present_with_mocked_http_success_performs_one_call_and_finds_marker() -> None:
    calls: list[dict[str, object]] = []

    def fake_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        calls.append({"endpoint": endpoint, "payload": payload, "api_key": api_key, "timeout": timeout})
        return success_response()

    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=fake_post,
        runtime_artifact_path=artifact_path(),
    )

    assert len(calls) == 1
    assert calls[0]["endpoint"] == adapter.OPENAI_RESPONSES_ENDPOINT
    assert calls[0]["api_key"] == FAKE_KEY
    assert calls[0]["payload"]["store"] is False
    assert calls[0]["payload"]["max_output_tokens"] == 32
    assert calls[0]["payload"]["input"] == adapter.DEFAULT_LIVE_SMOKE_INPUT
    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_AND_PASSED
    assert report["network_call_attempted"] is True
    assert report["network_call_performed"] is True
    assert report["network_call_count"] == 1
    assert report["store"] is False
    assert report["runtime_artifact_path"] == artifact_path()
    assert report["output_text_present"] is True
    assert report["expected_marker_found"] is True
    assert FAKE_KEY not in encode(report)


def test_all_gates_present_with_unexpected_output_classifies_model_output() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response("different text"),
        runtime_artifact_path=artifact_path("unexpected.json"),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT
    assert report["network_call_count"] == 1
    assert report["output_text_present"] is True
    assert report["expected_marker_found"] is False


def test_mocked_http_failure_is_classified_without_leaking_secret() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=401,
            body_text="invalid key sk-proj-thismustnotleak123456",
        ),
        runtime_artifact_path=artifact_path("http_failure.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_HTTP_ERROR
    assert report["http_status"] == 401
    assert "sk-proj-thismustnotleak123456" not in encoded
    assert FAKE_KEY not in encoded


def test_response_output_is_redacted_before_visible_json() -> None:
    output_secret = "ASF_LIVE_SMOKE_OK sk-proj-outputsecret123456"
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(output_secret),
        runtime_artifact_path=artifact_path("redaction.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_AND_PASSED
    assert "sk-proj-outputsecret123456" not in encoded
    assert adapter.REDACTION_MARKER in encoded


def test_live_runtime_artifact_path_must_stay_under_tmp() -> None:
    assert adapter.live_runtime_artifact_path("tmp/asf_openai_live_smoke_result.json") == (
        "tmp/asf_openai_live_smoke_result.json"
    )

    with pytest.raises(adapter.InputError):
        adapter.live_runtime_artifact_path("docs/not_allowed.json")

    with pytest.raises(adapter.InputError):
        adapter.live_runtime_artifact_path(str(ROOT / "not_tmp.json"))


def test_all_gates_present_without_runtime_artifact_path_blocks_before_network() -> None:
    calls: list[object] = []

    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: calls.append(payload) or success_response(),
    )

    assert calls == []
    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert "runtime artifact path under tmp/" in report["missing_gates"]
    assert report["network_call_attempted"] is False
