from __future__ import annotations

import json
import socket
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


def assert_safe_live_schema(report: dict[str, object], *, classification: str, status: str) -> None:
    assert report["status"] == status
    assert report["classification"] == classification
    assert report["provider"] == "openai"
    assert report["model"] == "gpt-5.5"
    assert isinstance(report["live_enabled"], bool)
    assert isinstance(report["credential_present"], bool)
    assert isinstance(report["duration_ms"], int)
    assert isinstance(report["timestamp"], str)
    assert isinstance(report["safe_details"], dict)
    assert report["schema_version"] == adapter.LIVE_SMOKE_RESULT_SCHEMA_VERSION
    assert FAKE_KEY not in encode(report)


def assert_no_secret_derivative_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).casefold()
            assert "fingerprint" not in lowered
            assert "api_key_length" not in lowered
            assert "key_length" not in lowered
            assert "credential_length" not in lowered
            assert "api_key_sha" not in lowered
            assert "credential_sha" not in lowered
            assert_no_secret_derivative_fields(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_secret_derivative_fields(item)


def success_response(output_text: str = adapter.EXPECTED_LIVE_SMOKE_MARKER) -> adapter.HttpJsonResponse:
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
                "usage": {
                    "input_tokens": 3,
                    "output_tokens": 2,
                    "total_tokens": 5,
                },
            }
        ),
    )


class SdkLikeObject:
    def __init__(self, **values: object) -> None:
        self.__dict__.update(values)


def json_response(body: dict[str, object], *, status_code: int = 200) -> adapter.HttpJsonResponse:
    return adapter.HttpJsonResponse(status_code=status_code, body_text=json.dumps(body))


def provider_error_response(
    *,
    status_code: int,
    error_type: str,
    error_code: str,
    message: str,
) -> adapter.HttpJsonResponse:
    return json_response(
        {
            "error": {
                "type": error_type,
                "code": error_code,
                "message": message,
            }
        },
        status_code=status_code,
    )


def test_extract_output_text_from_sdk_object_output_text_property() -> None:
    response = SdkLikeObject(output_text=adapter.EXPECTED_LIVE_SMOKE_MARKER)

    assert adapter.extract_output_text(response) == adapter.EXPECTED_LIVE_SMOKE_MARKER


def test_extract_output_text_from_dict_output_text_property() -> None:
    response = {"output_text": adapter.EXPECTED_LIVE_SMOKE_MARKER}

    assert adapter.extract_output_text(response) == adapter.EXPECTED_LIVE_SMOKE_MARKER


def test_extract_output_text_from_sdk_like_output_content_text() -> None:
    response = SdkLikeObject(
        output=[
            SdkLikeObject(
                content=[
                    SdkLikeObject(
                        type="output_text",
                        text=adapter.EXPECTED_LIVE_SMOKE_MARKER,
                    )
                ]
            )
        ]
    )

    assert adapter.extract_output_text(response) == adapter.EXPECTED_LIVE_SMOKE_MARKER


def test_all_gates_present_with_top_level_output_text_finds_marker() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: json_response(
            {
                "id": "resp_output_text_property",
                "object": "response",
                "status": "completed",
                "output_text": adapter.EXPECTED_LIVE_SMOKE_MARKER,
            }
        ),
        runtime_artifact_path=artifact_path("output_text_property.json"),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_AND_PASSED
    assert report["output_text_present"] is True
    assert report["expected_marker_found"] is True
    assert report["response_diagnostics"]["has_output_text_property"] is True


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
    assert_safe_live_schema(report, classification="credential_missing", status="skipped")
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
    assert_safe_live_schema(report, classification="not_configured", status="skipped")
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
    assert_safe_live_schema(report, classification="live_not_allowed", status="skipped")
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
    assert_safe_live_schema(report, classification="success", status="success")
    assert report["network_call_attempted"] is True
    assert report["network_call_performed"] is True
    assert report["network_call_count"] == 1
    assert report["store"] is False
    assert report["runtime_artifact_path"] == artifact_path()
    assert report["output_text_present"] is True
    assert report["expected_marker_found"] is True
    assert report["usage"] == {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5}
    assert report["response_id_hash_16"]
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
    assert report["failure_reason"] == "marker_missing"
    assert_safe_live_schema(report, classification="schema_error", status="failed")
    assert report["network_call_count"] == 1
    assert report["output_text_present"] is True
    assert report["expected_marker_found"] is False
    assert report["response_diagnostics"]["output_text_present"] is True


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
    assert_safe_live_schema(report, classification="auth_error", status="failed")
    assert report["http_status"] == 401
    assert "sk-proj-thismustnotleak123456" not in encoded
    assert FAKE_KEY not in encoded


def test_response_output_is_redacted_before_visible_json() -> None:
    output_secret_value = "s" + "k-" + "proj-outputsecret123456"
    output_secret = f"{adapter.EXPECTED_LIVE_SMOKE_MARKER} {output_secret_value}"
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(output_secret),
        runtime_artifact_path=artifact_path("redaction.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_AND_PASSED
    assert_safe_live_schema(report, classification="success", status="success")
    assert output_secret_value not in encoded
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
    assert_safe_live_schema(report, classification="live_not_allowed", status="skipped")
    assert "runtime artifact path under tmp/" in report["missing_gates"]
    assert report["network_call_attempted"] is False


def test_live_env_flag_different_from_one_is_classified_disabled() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(ASF_OPENAI_LIVE_ENABLED="0"),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert_safe_live_schema(report, classification="disabled", status="skipped")
    assert "ASF_OPENAI_LIVE_ENABLED=1" in report["missing_gates"]
    assert report["network_call_attempted"] is False


def test_incomplete_live_prompt_is_classified_not_configured() -> None:
    report = adapter.run_live(
        live_config(input_text="ping"),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
        runtime_artifact_path=artifact_path("bad_prompt.json"),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_NOT_RUN_MISSING_GATE
    assert_safe_live_schema(report, classification="not_configured", status="skipped")
    assert "tiny non-sensitive live smoke prompt" in report["missing_gates"]
    assert report["network_call_attempted"] is False


def test_mocked_rate_limit_is_classified_without_leaking_secret() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=429,
            error_type="rate_limit_exceeded",
            error_code="rate_limit",
            message="rate limit " + ("s" + "k-" + "proj-ratelimitsecret123456"),
        ),
        runtime_artifact_path=artifact_path("rate_limit.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_HTTP_ERROR
    assert report["failure_reason"] == "provider_http_error"
    assert report["provider_error_class"] == "rate_limited"
    assert report["provider_http_status"] == 429
    assert report["provider_error_type"] == "rate_limit_exceeded"
    assert report["provider_error_code"] == "rate_limit"
    assert report["retryable"] == "true"
    assert_safe_live_schema(report, classification="rate_limited", status="failed")
    assert "proj-ratelimitsecret123456" not in encoded


def test_mocked_quota_exceeded_is_distinct_from_rate_limit() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=429,
            error_type="insufficient_quota",
            error_code="insufficient_quota",
            message="You exceeded your current quota.",
        ),
        runtime_artifact_path=artifact_path("quota_exceeded.json"),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["failure_reason"] == "provider_http_error"
    assert report["provider_error_class"] == "quota_exceeded"
    assert report["provider_http_status"] == 429
    assert report["retryable"] == "false"
    assert "quota" in report["suggested_next_action"].casefold()


def test_mocked_authentication_error_is_provider_side_block() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=401,
            error_type="invalid_request_error",
            error_code="invalid_api_key",
            message="Invalid API key.",
        ),
        runtime_artifact_path=artifact_path("auth_error.json"),
    )

    assert report["provider_error_class"] == "authentication_error"
    assert report["provider_http_status"] == 401
    assert report["retryable"] == "false"
    assert_safe_live_schema(report, classification="auth_error", status="failed")


def test_mocked_model_access_denied_is_provider_side_block() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=403,
            error_type="model_access_denied",
            error_code="model_not_available",
            message="Project does not have access to this model.",
        ),
        runtime_artifact_path=artifact_path("model_access_denied.json"),
    )

    assert report["provider_error_class"] == "model_access_denied"
    assert report["provider_http_status"] == 403
    assert report["retryable"] == "false"
    assert_safe_live_schema(report, classification="auth_error", status="failed")


def test_mocked_provider_5xx_is_retryable_unknown_provider_error() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=503,
            error_type="server_error",
            error_code="service_unavailable",
            message="Provider service unavailable.",
        ),
        runtime_artifact_path=artifact_path("provider_5xx.json"),
    )

    assert report["provider_error_class"] == "unknown_provider_error"
    assert report["provider_http_status"] == 503
    assert report["retryable"] == "true"
    assert_safe_live_schema(report, classification="provider_error", status="failed")


def test_provider_error_object_without_http_error_status_is_provider_error() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=200,
            error_type="provider_error",
            error_code="unknown",
            message="Provider returned an error object without output.",
        ),
        runtime_artifact_path=artifact_path("provider_error_object.json"),
    )

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["failure_reason"] == "provider_http_error"
    assert report["provider_error_class"] == "unknown_provider_error"
    assert report["provider_http_status"] == 200
    assert_safe_live_schema(report, classification="provider_error", status="failed")


def test_provider_error_diagnostics_without_http_status_are_sanitized() -> None:
    secret_value = "s" + "k-" + "proj-diagnosticsecret123456"
    diagnostics = adapter.response_diagnostics(
        {
            "error": {
                "type": "provider_error",
                "code": "unknown",
                "message": f"diagnostic {secret_value}",
            }
        },
        "",
    )
    encoded = encode(diagnostics)

    assert diagnostics["provider_error_class"] == "unknown_provider_error"
    assert diagnostics["provider_http_status"] is None
    assert diagnostics["retryable"] == "unknown"
    assert secret_value not in encoded
    assert adapter.REDACTION_MARKER in encoded


def test_mocked_provider_error_is_classified_without_leaking_secret() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=500,
            body_text="provider failure sk-proj-providersecret123456",
        ),
        runtime_artifact_path=artifact_path("provider_error.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_HTTP_ERROR
    assert_safe_live_schema(report, classification="provider_error", status="failed")
    assert "sk-proj-providersecret123456" not in encoded


def test_mocked_network_error_is_classified_without_leaking_secret() -> None:
    def fail_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        raise TimeoutError("timeout sk-proj-networksecret123456")

    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=fail_post,
        runtime_artifact_path=artifact_path("network_error.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED
    assert_safe_live_schema(report, classification="network_error", status="failed")
    assert "sk-proj-networksecret123456" not in encoded


def test_mocked_socket_error_is_classified_as_network_error() -> None:
    def fail_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        raise socket.timeout("socket timeout")

    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=fail_post,
        runtime_artifact_path=artifact_path("socket_error.json"),
    )

    assert_safe_live_schema(report, classification="network_error", status="failed")


def test_invalid_json_response_is_classified_schema_error() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=200,
            body_text="{not json sk-proj-jsonsecret123456",
        ),
        runtime_artifact_path=artifact_path("invalid_json.json"),
    )
    encoded = encode(report)

    assert report["error_category"] == adapter.LIVE_SMOKE_INVALID_JSON
    assert_safe_live_schema(report, classification="schema_error", status="failed")
    assert "sk-proj-jsonsecret123456" not in encoded


def test_missing_success_evidence_is_classified_schema_error() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=200,
            body_text=json.dumps({"id": "resp_empty", "object": "response", "status": "completed", "output": []}),
        ),
        runtime_artifact_path=artifact_path("missing_evidence.json"),
    )

    assert report["error_category"] == adapter.LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE
    assert report["failure_reason"] == "output_text_absent"
    assert_safe_live_schema(report, classification="schema_error", status="failed")
    assert report["response_diagnostics"]["response_status"] == "completed"
    assert report["response_diagnostics"]["output_item_count"] == 0
    assert report["response_diagnostics"]["content_part_count"] == 0
    assert report["response_diagnostics"]["output_text_present"] is False


def test_incomplete_details_are_reported_as_sanitized_diagnostics() -> None:
    secret_value = "s" + "k-" + "proj-incompletesecret123456"
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=200,
            body_text=json.dumps(
                {
                    "id": "resp_incomplete",
                    "object": "response",
                    "status": "incomplete",
                    "incomplete_details": {
                        "reason": "max_output_tokens",
                        "note": secret_value,
                    },
                    "output": [],
                }
            ),
        ),
        runtime_artifact_path=artifact_path("incomplete_details.json"),
    )
    encoded = encode(report)

    assert report["error_category"] == adapter.LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE
    assert report["failure_reason"] == "output_text_absent"
    assert report["response_diagnostics"]["response_status"] == "incomplete"
    assert report["response_diagnostics"]["incomplete_details"]["reason"] == "max_output_tokens"
    assert secret_value not in encoded
    assert adapter.REDACTION_MARKER in encoded


def test_http_error_diagnostics_are_sanitized_without_raw_body() -> None:
    secret_value = "s" + "k-" + "proj-errorsecret123456"
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=429,
            body_text=json.dumps(
                {
                    "error": {
                        "type": "rate_limit_exceeded",
                        "code": "rate_limit",
                        "message": f"do not leak {secret_value}",
                    }
                }
            ),
        ),
        runtime_artifact_path=artifact_path("http_error_diagnostics.json"),
    )
    encoded = encode(report)

    assert report["error_category"] == adapter.LIVE_SMOKE_HTTP_ERROR
    assert report["failure_reason"] == "provider_http_error"
    assert report["response_diagnostics"]["http_status"] == 429
    assert report["response_diagnostics"]["has_error"] is True
    assert report["response_diagnostics"]["error_type"] == "rate_limit_exceeded"
    assert report["response_diagnostics"]["error_code"] == "rate_limit"
    assert "message" not in report["response_diagnostics"]
    assert secret_value not in encoded


def test_unknown_local_error_is_classified_fail_closed_without_leaking_secret() -> None:
    def fail_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        raise RuntimeError("unexpected sk-proj-unknownsecret123456")

    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=fail_post,
        runtime_artifact_path=artifact_path("unknown_error.json"),
    )
    encoded = encode(report)

    assert report["decision"] == adapter.LIVE_SMOKE_EXECUTED_BUT_FAILED
    assert report["error_category"] == adapter.LIVE_SMOKE_UNKNOWN_ERROR
    assert_safe_live_schema(report, classification="unknown_error", status="failed")
    assert "sk-proj-unknownsecret123456" not in encoded


def test_no_report_contains_api_key_or_derivative_fields() -> None:
    reports = [
        adapter.run_live(live_config(), environ={}),
        adapter.run_live(live_config(), environ={"OPENAI_API_KEY": FAKE_KEY}),
        adapter.run_live(live_config(), environ=live_env(ASF_OPENAI_LIVE_ENABLED="0")),
        adapter.run_live(
            live_config(),
            environ=live_env(),
            http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
            runtime_artifact_path=artifact_path("safe_report.json"),
        ),
    ]

    for report in reports:
        encoded = encode(report)
        assert FAKE_KEY not in encoded
        assert "sk-proj-testlivesmoke" not in encoded
        assert_no_secret_derivative_fields(report)


def test_operator_markdown_artifact_is_safe_and_under_tmp() -> None:
    report = adapter.run_live(
        live_config(),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
        runtime_artifact_path=artifact_path("markdown_result.json"),
    )
    markdown = adapter.build_operator_markdown(report)

    assert "Classification: success" in markdown
    assert "Credential present: True" in markdown
    assert FAKE_KEY not in markdown
    assert "sk-proj-testlivesmoke" not in markdown

    assert adapter.operator_markdown_output_path("tmp/asf_openai_live_smoke_summary.md", mode="live") is not None
    with pytest.raises(adapter.InputError):
        adapter.operator_markdown_output_path("docs/not_allowed.md", mode="live")
