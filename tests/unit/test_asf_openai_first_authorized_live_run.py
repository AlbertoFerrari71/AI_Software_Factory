from __future__ import annotations

import json
from pathlib import Path

from scripts import asf_openai_api_adapter as adapter
from scripts import asf_openai_first_authorized_live_run as first_live


ROOT = Path(__file__).resolve().parents[2]
FAKE_KEY = "test-openai-key-step560-secret-value"


def encode(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def config(name: str, **overrides: object) -> first_live.FirstAuthorizedLiveRunConfig:
    values: dict[str, object] = {
        "report_path": f"tmp/test_step_560/{name}/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md",
        "evidence_path": f"tmp/test_step_560/{name}/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json",
    }
    values.update(overrides)
    return first_live.FirstAuthorizedLiveRunConfig(**values)


def live_env(**overrides: str) -> dict[str, str]:
    values = {
        "OPENAI_API_KEY": FAKE_KEY,
        "ASF_OPENAI_LIVE_RUN": "1",
    }
    values.update(overrides)
    return values


def success_response(output_text: str = adapter.EXPECTED_LIVE_SMOKE_MARKER) -> adapter.HttpJsonResponse:
    return adapter.HttpJsonResponse(
        status_code=200,
        body_text=json.dumps(
            {
                "id": "resp_step_560_success",
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


def provider_error_response(
    *,
    status_code: int,
    error_type: str,
    error_code: str,
    message: str,
) -> adapter.HttpJsonResponse:
    return adapter.HttpJsonResponse(
        status_code=status_code,
        body_text=json.dumps(
            {
                "error": {
                    "type": error_type,
                    "code": error_code,
                    "message": message,
                }
            }
        ),
    )


def assert_no_secret(value: object) -> None:
    encoded = encode(value)
    assert FAKE_KEY not in encoded
    assert "test-openai-key-step560" not in encoded
    assert ("Bearer" + " ") not in encoded


def test_live_requested_without_api_key_is_blocked_and_writes_report_only() -> None:
    calls: list[object] = []
    summary = first_live.run_and_write(
        config("missing_key", live=True),
        environ={"ASF_OPENAI_LIVE_RUN": "1"},
        http_post_json=lambda endpoint, payload, api_key, timeout: calls.append(payload) or success_response(),
    )

    report_path = ROOT / str(summary["report_written"])

    assert calls == []
    assert summary["status"] == "BLOCKED"
    assert summary["request_count"] == 0
    assert summary["evidence_written"] is None
    assert "OPENAI_API_KEY" in summary["missing_gates"]
    assert report_path.is_file()
    assert_no_secret(summary)
    assert_no_secret(report_path.read_text(encoding="utf-8"))


def test_api_key_without_live_authorization_is_blocked_before_network() -> None:
    calls: list[object] = []
    summary = first_live.run_and_write(
        config("missing_live_flag"),
        environ={"OPENAI_API_KEY": FAKE_KEY},
        http_post_json=lambda endpoint, payload, api_key, timeout: calls.append(payload) or success_response(),
    )

    assert calls == []
    assert summary["status"] == "BLOCKED"
    assert summary["live_authorized"] is False
    assert summary["authorization_source"] == "missing"
    assert summary["request_count"] == 0
    assert "--allow-live" in summary["missing_gates"]
    assert_no_secret(summary)


def test_authorized_success_uses_adapter_once_and_writes_sanitized_evidence() -> None:
    calls: list[dict[str, object]] = []

    def fake_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        calls.append({"endpoint": endpoint, "payload": payload, "api_key": api_key, "timeout": timeout})
        return success_response()

    summary = first_live.run_and_write(
        config("success", live=True),
        environ=live_env(ASF_OPENAI_MODEL="test-model-step-560"),
        http_post_json=fake_post,
    )
    evidence_path = ROOT / str(summary["evidence_written"])
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert len(calls) == 1
    assert calls[0]["api_key"] == FAKE_KEY
    assert calls[0]["payload"]["model"] == "test-model-step-560"
    assert calls[0]["payload"]["input"] == adapter.DEFAULT_LIVE_SMOKE_INPUT
    assert calls[0]["payload"]["max_output_tokens"] == first_live.DEFAULT_MAX_OUTPUT_TOKENS
    assert calls[0]["payload"]["store"] is False
    assert summary["status"] == "COMPLETATO"
    assert summary["request_count"] == 1
    assert summary["output_check"]["expected_marker_found"] is True
    assert summary["usage_available"] is True
    assert summary["response_id_hash_16"]
    assert evidence["request_count"] == 1
    assert evidence["usage"] == {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5}
    assert_no_secret(summary)
    assert_no_secret(evidence)


def test_rate_limit_is_blocked_without_success_evidence() -> None:
    summary = first_live.run_and_write(
        config("rate_limit", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=429,
            error_type="rate_limit_exceeded",
            error_code="rate_limit",
            message="rate limit secret=ratelimit-step560",
        ),
    )

    assert summary["status"] == "BLOCKED_BY_RATE_LIMIT_OR_QUOTA"
    assert summary["adapter_classification"] == "rate_limited"
    assert summary["failure_reason"] == "provider_http_error"
    assert summary["provider_error_class"] == "rate_limited"
    assert summary["provider_http_status"] == 429
    assert summary["provider_error_type"] == "rate_limit_exceeded"
    assert summary["provider_error_code"] == "rate_limit"
    assert summary["provider_message"] == "rate limit secret=[REDACTED_SECRET]"
    assert summary["retryable"] == "true"
    assert summary["output_check"]["diagnosis"] == "provider_http_error"
    assert summary["output_check"]["provider_error_class"] == "rate_limited"
    assert summary["response_diagnostics"]["http_status"] == 429
    assert summary["request_count"] == 1
    assert summary["evidence_written"] is None
    assert_no_secret(summary)


def test_quota_exceeded_report_is_blocked_by_rate_limit_or_quota_without_evidence() -> None:
    summary = first_live.run_and_write(
        config("quota_exceeded", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=429,
            error_type="insufficient_quota",
            error_code="insufficient_quota",
            message="You exceeded your current quota.",
        ),
    )

    assert summary["status"] == "BLOCKED_BY_RATE_LIMIT_OR_QUOTA"
    assert summary["provider_error_class"] == "quota_exceeded"
    assert summary["provider_error_code"] == "insufficient_quota"
    assert summary["retryable"] == "false"
    assert summary["evidence_written"] is None
    assert not (ROOT / "tmp/test_step_560/quota_exceeded/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json").exists()


def test_model_access_denied_report_is_blocked_by_provider_http_error_without_evidence() -> None:
    summary = first_live.run_and_write(
        config("model_access_denied", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: provider_error_response(
            status_code=403,
            error_type="model_access_denied",
            error_code="model_not_available",
            message="Project does not have access to this model.",
        ),
    )

    assert summary["status"] == "BLOCKED_BY_PROVIDER_HTTP_ERROR"
    assert summary["provider_error_class"] == "model_access_denied"
    assert summary["provider_http_status"] == 403
    assert summary["evidence_written"] is None


def test_network_error_is_blocked_without_leaking_secret() -> None:
    def fail_post(endpoint: str, payload: dict[str, object], api_key: str, timeout: float) -> adapter.HttpJsonResponse:
        raise TimeoutError("timeout secret=network-step560")

    summary = first_live.run_and_write(
        config("network_error", live=True),
        environ=live_env(),
        http_post_json=fail_post,
    )

    assert summary["status"] == "BLOCKED"
    assert summary["adapter_classification"] == "network_error"
    assert summary["request_count"] == 1
    assert summary["network_call_performed"] is False
    assert_no_secret(summary)


def test_unexpected_model_output_is_failed_after_one_adapter_call() -> None:
    summary = first_live.run_and_write(
        config("unexpected_output", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response("different output"),
    )
    report_text = (ROOT / str(summary["report_written"])).read_text(encoding="utf-8")

    assert summary["status"] == "FALLITO"
    assert summary["adapter_classification"] == "schema_error"
    assert summary["failure_reason"] == "marker_missing"
    assert summary["request_count"] == 1
    assert summary["output_check"]["expected_marker_found"] is False
    assert summary["output_check"]["output_text_present"] is True
    assert summary["output_check"]["diagnosis"] == "marker_missing"
    assert "## Response Diagnostics" in report_text
    assert "marker_missing" in report_text
    assert summary["evidence_written"] is None
    assert_no_secret(summary)


def test_completed_response_without_text_reports_output_text_absent() -> None:
    summary = first_live.run_and_write(
        config("completed_without_text", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=200,
            body_text=json.dumps(
                {
                    "id": "resp_completed_without_text",
                    "object": "response",
                    "status": "completed",
                    "output": [],
                }
            ),
        ),
    )
    report_text = (ROOT / str(summary["report_written"])).read_text(encoding="utf-8")

    assert summary["status"] == "FALLITO"
    assert summary["failure_reason"] == "output_text_absent"
    assert summary["output_check"]["diagnosis"] == "output_text_absent"
    assert summary["response_diagnostics"]["response_status"] == "completed"
    assert summary["response_diagnostics"]["output_item_count"] == 0
    assert "output_text_absent" in report_text
    assert_no_secret(summary)


def test_report_diagnostics_do_not_include_secret_like_error_body() -> None:
    secret_value = "s" + "k-" + "proj-wrappererrorsecret123456"
    summary = first_live.run_and_write(
        config("sanitized_error_report", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: adapter.HttpJsonResponse(
            status_code=429,
            body_text=json.dumps(
                {
                    "error": {
                        "type": "rate_limit_exceeded",
                        "code": "rate_limit",
                        "message": secret_value,
                    }
                }
            ),
        ),
    )
    report_text = (ROOT / str(summary["report_written"])).read_text(encoding="utf-8")

    assert summary["status"] == "BLOCKED_BY_RATE_LIMIT_OR_QUOTA"
    assert summary["failure_reason"] == "provider_http_error"
    assert summary["provider_error_class"] == "rate_limited"
    assert "rate_limit_exceeded" in report_text
    assert secret_value not in report_text
    assert FAKE_KEY not in report_text
    assert "message" not in summary["response_diagnostics"]


def test_console_summary_and_report_do_not_include_api_key(capsys: object) -> None:
    summary = first_live.run_and_write(
        config("console", live=True),
        environ=live_env(),
        http_post_json=lambda endpoint, payload, api_key, timeout: success_response(),
    )

    first_live.emit_console_summary(summary)
    captured = capsys.readouterr()
    report_text = (ROOT / str(summary["report_written"])).read_text(encoding="utf-8")

    assert FAKE_KEY not in captured.out
    assert FAKE_KEY not in report_text
    assert ("Bearer" + " ") not in captured.out
    assert ("Bearer" + " ") not in report_text
