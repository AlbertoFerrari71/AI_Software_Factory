from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_TEXT_VERBOSITY = "medium"
DEFAULT_LIVE_SMOKE_INPUT = "Return exactly ASF_LIVE_SMOKE_OK."
DEFAULT_LIVE_MAX_OUTPUT_TOKENS = 32
DEFAULT_LIVE_TIMEOUT_SECONDS = 30.0

SUPPORTED_REASONING_EFFORTS = ("none", "low", "medium", "high", "xhigh")
SUPPORTED_TEXT_VERBOSITY = ("low", "medium", "high")
SUPPORTED_MODES = ("check-env", "dry-run", "mock", "live")

LIVE_MODE_NOT_IMPLEMENTED = "LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500"
LIVE_CALLS_NOT_IMPLEMENTED = "LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510"
LIVE_DISABLED_BY_DEFAULT = "LIVE_DISABLED_BY_DEFAULT"
CREDENTIAL_MISSING = "CREDENTIAL_MISSING"
LIVE_ENV_FLAG_MISSING = "LIVE_ENV_FLAG_MISSING"
LIVE_FLAG_MISSING = "LIVE_FLAG_MISSING"
LIVE_CONFIRMATION_MISSING = "LIVE_CONFIRMATION_MISSING"
LIVE_READY_FOR_SEPARATE_SMOKE_STEP = "LIVE_READY_FOR_SEPARATE_SMOKE_STEP"
LIVE_SMOKE_READY_FOR_CALL = "LIVE_SMOKE_READY_FOR_CALL"
LIVE_SMOKE_EXECUTED_AND_PASSED = "LIVE_SMOKE_EXECUTED_AND_PASSED"
LIVE_SMOKE_EXECUTED_BUT_FAILED = "LIVE_SMOKE_EXECUTED_BUT_FAILED"
LIVE_SMOKE_NOT_RUN_MISSING_GATE = "LIVE_SMOKE_NOT_RUN_MISSING_GATE"
LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED = "LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED"
LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT = "LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT"
LIVE_SMOKE_HTTP_ERROR = "LIVE_SMOKE_HTTP_ERROR"
LIVE_SMOKE_INVALID_JSON = "LIVE_SMOKE_INVALID_JSON"
LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE = "LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE"
LIVE_SMOKE_UNKNOWN_ERROR = "LIVE_SMOKE_UNKNOWN_ERROR"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
OPENAI_RESPONSES_ENDPOINT_PATH = "/v1/responses"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
ASF_OPENAI_LIVE_ENABLED_ENV = "ASF_OPENAI_LIVE_ENABLED"
ASF_OPENAI_LIVE_ENABLED_VALUE = "1"
LIVE_CONFIRMATION_VALUE = "I_UNDERSTAND_THIS_CALLS_OPENAI_API"
MOCK_OUTPUT_TEXT = "ASF OpenAI adapter mock response."
EXPECTED_LIVE_SMOKE_MARKER = "ASF_LIVE_SMOKE_OK"
LIVE_SMOKE_RESULT_SCHEMA_VERSION = "1.0"
LIVE_SMOKE_CLASSIFICATIONS = (
    "not_configured",
    "disabled",
    "credential_missing",
    "live_not_allowed",
    "success",
    "provider_error",
    "network_error",
    "rate_limited",
    "auth_error",
    "schema_error",
    "unknown_error",
)
LIVE_SMOKE_STATUSES = ("success", "failed", "skipped")

OPENAI_API_KEY_PATTERN = re.compile(r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}")
BEARER_TOKEN_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]{8,}")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(openai_api_key|api[_-]?key|authorization|token|secret)\b\s*([:=])\s*([\"']?)[^\s,\"'}]+"
)
REDACTION_MARKER = "[REDACTED_OPENAI_API_KEY]"
SECRET_REDACTION_MARKER = "[REDACTED_SECRET]"


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class HttpJsonResponse:
    status_code: int
    body_text: str


@dataclass(frozen=True)
class OpenAIAdapterConfig:
    mode: str = "dry-run"
    input_text: str = ""
    instructions: str | None = None
    model: str = DEFAULT_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    text_verbosity: str = DEFAULT_TEXT_VERBOSITY
    allow_live: bool = False
    live_confirm: str | None = None
    max_output_tokens: int | None = None
    gate_only: bool = False
    timeout_seconds: float = DEFAULT_LIVE_TIMEOUT_SECONDS


@dataclass(frozen=True)
class OpenAIAdapterResult:
    status: str
    network_performed: bool
    payload: dict[str, Any] | None = None
    environment: dict[str, bool] | None = None
    mock_output_text: str | None = None
    input_length: int | None = None
    input_sha256_16: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": self.status,
            "network_performed": self.network_performed,
        }
        if self.message is not None:
            result["message"] = self.message
        if self.payload is not None:
            result["payload"] = self.payload
        if self.environment is not None:
            result["environment"] = self.environment
        if self.mock_output_text is not None:
            result["mock_output_text"] = self.mock_output_text
        if self.input_length is not None:
            result["input_length"] = self.input_length
        if self.input_sha256_16 is not None:
            result["input_sha256_16"] = self.input_sha256_16
        return result


@dataclass(frozen=True)
class LiveResultClock:
    timestamp: str
    started_perf: float


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def redact_secret_assignment(match: re.Match[str]) -> str:
    key, separator, quote = match.groups()
    closing_quote = quote if quote else ""
    return f"{key}{separator}{quote}{SECRET_REDACTION_MARKER}{closing_quote}"


def redact_secret(value: str) -> str:
    redacted = OPENAI_API_KEY_PATTERN.sub(REDACTION_MARKER, value)
    redacted = BEARER_TOKEN_PATTERN.sub(f"Bearer {SECRET_REDACTION_MARKER}", redacted)
    return SECRET_ASSIGNMENT_PATTERN.sub(redact_secret_assignment, redacted)


def redact_data(value: Any) -> Any:
    if isinstance(value, str):
        return redact_secret(value)
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, tuple):
        return [redact_data(item) for item in value]
    if isinstance(value, dict):
        return {redact_secret(str(key)): redact_data(item) for key, item in value.items()}
    return value


def read_input_text(input_text: str | None = None, input_file: str | None = None) -> str:
    if input_text is not None and input_file:
        raise InputError("Use either --input or --input-file, not both.")
    if input_file:
        path = Path(input_file).expanduser()
        if not path.is_file():
            raise InputError(f"--input-file does not exist or is not a file: {path}")
        return path.read_text(encoding="utf-8-sig")
    return input_text or ""


def validate_adapter_config(config: OpenAIAdapterConfig) -> None:
    if config.mode not in SUPPORTED_MODES:
        raise InputError(f"Unsupported mode: {config.mode}")
    if not config.model.strip():
        raise InputError("--model must not be empty.")
    if re.search(r"\s", config.model):
        raise InputError("--model must not contain whitespace.")
    if config.reasoning_effort not in SUPPORTED_REASONING_EFFORTS:
        allowed = ", ".join(SUPPORTED_REASONING_EFFORTS)
        raise InputError(f"--reasoning-effort must be one of: {allowed}")
    if config.text_verbosity not in SUPPORTED_TEXT_VERBOSITY:
        allowed = ", ".join(SUPPORTED_TEXT_VERBOSITY)
        raise InputError(f"--text-verbosity must be one of: {allowed}")
    if config.max_output_tokens is not None and config.max_output_tokens < 1:
        raise InputError("--max-output-tokens must be greater than zero.")
    if config.max_output_tokens is not None and config.max_output_tokens > 4096:
        raise InputError("--max-output-tokens must be 4096 or less.")
    if config.timeout_seconds <= 0:
        raise InputError("--timeout-seconds must be greater than zero.")


def build_responses_payload(
    input_text: str,
    *,
    instructions: str | None = None,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    text_verbosity: str = DEFAULT_TEXT_VERBOSITY,
    store: bool | None = None,
    max_output_tokens: int | None = None,
) -> dict[str, Any]:
    config = OpenAIAdapterConfig(
        input_text=input_text,
        instructions=instructions,
        model=model,
        reasoning_effort=reasoning_effort,
        text_verbosity=text_verbosity,
        max_output_tokens=max_output_tokens,
    )
    validate_adapter_config(config)

    payload: dict[str, Any] = {
        "model": model,
        "input": input_text,
    }
    if instructions and instructions.strip():
        payload["instructions"] = instructions
    if store is not None:
        payload["store"] = store
    if max_output_tokens is not None:
        payload["max_output_tokens"] = max_output_tokens
    payload["reasoning"] = {"effort": reasoning_effort}
    payload["text"] = {"verbosity": text_verbosity}
    return payload


def environment_source(environ: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def check_environment(environ: Mapping[str, str] | None = None) -> dict[str, bool]:
    source = environment_source(environ)
    return {"openai_api_key_present": bool(source.get(OPENAI_API_KEY_ENV))}


def check_credential_gate(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = environment_source(environ)
    return {
        "credential_source": OPENAI_API_KEY_ENV,
        "openai_api_key_present": bool(source.get(OPENAI_API_KEY_ENV)),
        "secret_value_logged": False,
    }


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def start_live_result_clock() -> LiveResultClock:
    return LiveResultClock(timestamp=utc_timestamp(), started_perf=time.perf_counter())


def elapsed_ms(clock: LiveResultClock) -> int:
    return max(0, int(round((time.perf_counter() - clock.started_perf) * 1000)))


def stable_checksum(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def run_check_env(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    result = OpenAIAdapterResult(
        status="ENV_CHECK",
        network_performed=False,
        environment=check_environment(environ),
        message="Environment readiness checked without emitting credentials.",
    )
    return redact_data(result.to_dict())


def run_dry_run(config: OpenAIAdapterConfig, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    validate_adapter_config(config)
    payload = build_responses_payload(
        config.input_text,
        instructions=config.instructions,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        text_verbosity=config.text_verbosity,
    )
    result = OpenAIAdapterResult(
        status="DRY_RUN",
        network_performed=False,
        payload=payload,
        environment=check_environment(environ),
        message="No network or OpenAI API call was performed.",
    )
    return redact_data(result.to_dict())


def run_mock(config: OpenAIAdapterConfig) -> dict[str, Any]:
    validate_adapter_config(config)
    payload = build_responses_payload(
        config.input_text,
        instructions=config.instructions,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        text_verbosity=config.text_verbosity,
    )
    result = OpenAIAdapterResult(
        status="MOCK_RESPONSE",
        network_performed=False,
        payload=payload,
        mock_output_text=MOCK_OUTPUT_TEXT,
        input_length=len(config.input_text),
        input_sha256_16=stable_checksum(config.input_text),
        message="Deterministic mock response generated without network.",
    )
    return redact_data(result.to_dict())


def build_live_request_plan(config: OpenAIAdapterConfig) -> dict[str, Any]:
    payload_preview = build_responses_payload(
        config.input_text,
        instructions=config.instructions,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        text_verbosity=config.text_verbosity,
        store=False,
        max_output_tokens=live_max_output_tokens(config),
    )
    return {
        "api_surface": "responses",
        "endpoint": OPENAI_RESPONSES_ENDPOINT_PATH,
        "model": config.model,
        "store": False,
        "network_call_performed": False,
        "payload_preview": redact_data(payload_preview),
    }


def evaluate_live_boundary(config: OpenAIAdapterConfig, environ: Mapping[str, str] | None = None) -> str:
    source = environment_source(environ)
    if not source.get(OPENAI_API_KEY_ENV):
        return CREDENTIAL_MISSING
    if source.get(ASF_OPENAI_LIVE_ENABLED_ENV) != ASF_OPENAI_LIVE_ENABLED_VALUE:
        return LIVE_ENV_FLAG_MISSING
    if not config.allow_live:
        return LIVE_FLAG_MISSING
    if config.live_confirm != LIVE_CONFIRMATION_VALUE:
        return LIVE_CONFIRMATION_MISSING
    return LIVE_READY_FOR_SEPARATE_SMOKE_STEP


def live_max_output_tokens(config: OpenAIAdapterConfig) -> int:
    return config.max_output_tokens or DEFAULT_LIVE_MAX_OUTPUT_TOKENS


def is_tiny_non_sensitive_live_prompt(input_text: str) -> bool:
    text = input_text.strip()
    if text != DEFAULT_LIVE_SMOKE_INPUT:
        return False
    if len(text) > 80:
        return False
    if OPENAI_API_KEY_PATTERN.search(text) or BEARER_TOKEN_PATTERN.search(text):
        return False
    return True


def evaluate_live_smoke_gates(
    config: OpenAIAdapterConfig,
    environ: Mapping[str, str] | None = None,
) -> list[str]:
    source = environment_source(environ)
    missing_gates: list[str] = []
    if not source.get(OPENAI_API_KEY_ENV):
        missing_gates.append(OPENAI_API_KEY_ENV)
    if source.get(ASF_OPENAI_LIVE_ENABLED_ENV) != ASF_OPENAI_LIVE_ENABLED_VALUE:
        missing_gates.append(f"{ASF_OPENAI_LIVE_ENABLED_ENV}={ASF_OPENAI_LIVE_ENABLED_VALUE}")
    if not config.allow_live:
        missing_gates.append("--allow-live")
    if config.live_confirm != LIVE_CONFIRMATION_VALUE:
        missing_gates.append(f"--live-confirm {LIVE_CONFIRMATION_VALUE}")
    if not is_tiny_non_sensitive_live_prompt(config.input_text):
        missing_gates.append("tiny non-sensitive live smoke prompt")
    return missing_gates


def classify_missing_live_smoke_gate(missing_gates: list[str], source: Mapping[str, str]) -> str:
    if OPENAI_API_KEY_ENV in missing_gates:
        return "credential_missing"
    if f"{ASF_OPENAI_LIVE_ENABLED_ENV}={ASF_OPENAI_LIVE_ENABLED_VALUE}" in missing_gates:
        if ASF_OPENAI_LIVE_ENABLED_ENV not in source:
            return "not_configured"
        return "disabled"
    if "tiny non-sensitive live smoke prompt" in missing_gates:
        return "not_configured"
    if "--allow-live" in missing_gates or any(gate.startswith("--live-confirm ") for gate in missing_gates):
        return "live_not_allowed"
    if "runtime artifact path under tmp/" in missing_gates:
        return "live_not_allowed"
    return "not_configured"


def classify_http_status(status_code: int) -> str:
    if status_code in {401, 403}:
        return "auth_error"
    if status_code == 429:
        return "rate_limited"
    return "provider_error"


def classify_live_exception(exc: BaseException) -> str:
    if isinstance(exc, (OSError, TimeoutError, urllib.error.URLError)):
        return "network_error"
    return "unknown_error"


def build_live_payload(config: OpenAIAdapterConfig) -> dict[str, Any]:
    return build_responses_payload(
        config.input_text,
        instructions=config.instructions,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        text_verbosity=config.text_verbosity,
        store=False,
        max_output_tokens=live_max_output_tokens(config),
    )


def post_openai_responses(
    endpoint: str,
    payload: dict[str, Any],
    api_key: str,
    timeout_seconds: float,
) -> HttpJsonResponse:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return HttpJsonResponse(status_code=response.getcode(), body_text=response_body)
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        return HttpJsonResponse(status_code=exc.code, body_text=response_body)


HttpPostJson = Callable[[str, dict[str, Any], str, float], HttpJsonResponse]


def collect_response_text_fragments(value: Any) -> list[str]:
    fragments: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"output_text", "text"} and isinstance(item, str):
                fragments.append(item)
            else:
                fragments.extend(collect_response_text_fragments(item))
    elif isinstance(value, list):
        for item in value:
            fragments.extend(collect_response_text_fragments(item))
    return fragments


def extract_output_text(response_json: Any) -> str:
    return "\n".join(fragment for fragment in collect_response_text_fragments(response_json) if fragment)


def response_has_minimal_success_evidence(response_json: Any, output_text: str) -> bool:
    if isinstance(response_json, dict):
        if bool(response_json.get("id")):
            return True
        if response_json.get("object") == "response":
            return True
    return bool(output_text)


def base_live_result(
    config: OpenAIAdapterConfig,
    source: Mapping[str, str],
    *,
    runtime_artifact_path: str | None = None,
) -> dict[str, Any]:
    credential_gate = check_credential_gate(source)
    return {
        "status": "LIVE_SMOKE",
        "mode": "live",
        "decision": LIVE_SMOKE_NOT_RUN_MISSING_GATE,
        "credential_source": credential_gate["credential_source"],
        "openai_api_key_present": credential_gate["openai_api_key_present"],
        "secret_value_logged": credential_gate["secret_value_logged"],
        "network_performed": False,
        "network_call_attempted": False,
        "network_call_performed": False,
        "network_call_count": 0,
        "store": False,
        "model": config.model,
        "runtime_artifact_path": runtime_artifact_path,
        "output_text_present": False,
        "expected_marker_found": False,
        "response_id_present": False,
        "minimal_success_evidence_present": False,
        "gate_only": config.gate_only,
        "gate_inputs": {
            "asf_openai_live_enabled": source.get(ASF_OPENAI_LIVE_ENABLED_ENV) == ASF_OPENAI_LIVE_ENABLED_VALUE,
            "allow_live_flag": config.allow_live,
            "live_confirmation_present": bool(config.live_confirm),
            "live_confirmation_matches": config.live_confirm == LIVE_CONFIRMATION_VALUE,
            "tiny_non_sensitive_prompt": is_tiny_non_sensitive_live_prompt(config.input_text),
        },
        "live_request_plan": build_live_request_plan(config),
    }


def live_safe_details(result: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "decision",
        "error_category",
        "missing_gates",
        "http_status",
        "network_call_attempted",
        "network_call_performed",
        "network_call_count",
        "store",
        "gate_only",
        "runtime_artifact_path",
        "output_text_present",
        "expected_marker_found",
        "response_id_present",
        "minimal_success_evidence_present",
    ]
    return redact_data({key: result[key] for key in keys if key in result})


def live_next_step(status: str, classification: str) -> str:
    if status == "success":
        return "Review the redacted artifact and require a separate human-approved step before any further live call."
    if classification == "credential_missing":
        return "Set a credential only in the local shell when a future approved live step explicitly requires it."
    if classification in {"not_configured", "disabled", "live_not_allowed"}:
        return "Keep the live smoke blocked until all gates are intentionally configured and separately authorized."
    return "Review the classified failure, keep fail-closed behavior, and retry only in a separately authorized step."


def finalize_live_result(
    result: dict[str, Any],
    *,
    status: str,
    classification: str,
    message: str,
    clock: LiveResultClock,
) -> dict[str, Any]:
    if status not in LIVE_SMOKE_STATUSES:
        raise InputError(f"Unsupported live result status: {status}")
    if classification not in LIVE_SMOKE_CLASSIFICATIONS:
        raise InputError(f"Unsupported live result classification: {classification}")

    result["legacy_status"] = "LIVE_SMOKE"
    result["status"] = status
    result["classification"] = classification
    result["message"] = redact_secret(message)
    result["safe_details"] = live_safe_details(result)
    result["provider"] = "openai"
    result["live_enabled"] = bool(result.get("gate_inputs", {}).get("asf_openai_live_enabled"))
    result["credential_present"] = bool(result.get("openai_api_key_present"))
    result["duration_ms"] = elapsed_ms(clock)
    result["timestamp"] = clock.timestamp
    result["schema_version"] = LIVE_SMOKE_RESULT_SCHEMA_VERSION
    result["operator_next_step"] = live_next_step(status, classification)
    return redact_data(result)


def run_live(
    config: OpenAIAdapterConfig,
    environ: Mapping[str, str] | None = None,
    *,
    http_post_json: HttpPostJson | None = None,
    runtime_artifact_path: str | None = None,
) -> dict[str, Any]:
    clock = start_live_result_clock()
    validate_adapter_config(config)
    source = environment_source(environ)
    result = base_live_result(config, source, runtime_artifact_path=runtime_artifact_path)
    missing_gates = evaluate_live_smoke_gates(config, source)
    if not missing_gates and not config.gate_only and runtime_artifact_path is None:
        missing_gates.append("runtime artifact path under tmp/")
    result["missing_gates"] = missing_gates
    result["live_boundary_decision"] = evaluate_live_boundary(config, source)

    if missing_gates:
        result["decision"] = LIVE_SMOKE_NOT_RUN_MISSING_GATE
        result["error_category"] = LIVE_SMOKE_NOT_RUN_MISSING_GATE
        classification = classify_missing_live_smoke_gate(missing_gates, source)
        return finalize_live_result(
            result,
            status="skipped",
            classification=classification,
            message="Live smoke was not run because one or more mandatory gates are missing.",
            clock=clock,
        )

    if config.gate_only:
        result["decision"] = LIVE_SMOKE_READY_FOR_CALL
        return finalize_live_result(
            result,
            status="skipped",
            classification="disabled",
            message="All live smoke gates are present; gate-only preflight performed no network call.",
            clock=clock,
        )

    api_key = source.get(OPENAI_API_KEY_ENV)
    if not api_key:
        result["decision"] = LIVE_SMOKE_NOT_RUN_MISSING_GATE
        result["error_category"] = LIVE_SMOKE_NOT_RUN_MISSING_GATE
        result["missing_gates"] = [OPENAI_API_KEY_ENV]
        return finalize_live_result(
            result,
            status="skipped",
            classification="credential_missing",
            message="Live smoke was not run because the credential gate is missing.",
            clock=clock,
        )

    payload = build_live_payload(config)
    result["network_call_attempted"] = True
    result["network_call_count"] = 1
    post_json = post_openai_responses if http_post_json is None else http_post_json
    try:
        http_response = post_json(OPENAI_RESPONSES_ENDPOINT, payload, api_key, config.timeout_seconds)
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        result["decision"] = LIVE_SMOKE_EXECUTED_BUT_FAILED
        result["error_category"] = LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED
        return finalize_live_result(
            result,
            status="failed",
            classification=classify_live_exception(exc),
            message=f"Live smoke network call failed before a usable provider response: {redact_secret(str(exc))}",
            clock=clock,
        )
    except Exception as exc:
        result["decision"] = LIVE_SMOKE_EXECUTED_BUT_FAILED
        result["error_category"] = LIVE_SMOKE_UNKNOWN_ERROR
        return finalize_live_result(
            result,
            status="failed",
            classification=classify_live_exception(exc),
            message=f"Live smoke failed with an unexpected local error: {redact_secret(str(exc))}",
            clock=clock,
        )

    result["network_performed"] = True
    result["network_call_performed"] = True
    result["http_status"] = http_response.status_code

    if http_response.status_code < 200 or http_response.status_code >= 300:
        result["decision"] = LIVE_SMOKE_EXECUTED_BUT_FAILED
        result["error_category"] = LIVE_SMOKE_HTTP_ERROR
        return finalize_live_result(
            result,
            status="failed",
            classification=classify_http_status(http_response.status_code),
            message="OpenAI Responses API returned a non-success HTTP status.",
            clock=clock,
        )

    try:
        response_json = json.loads(http_response.body_text)
    except json.JSONDecodeError as exc:
        result["decision"] = LIVE_SMOKE_EXECUTED_BUT_FAILED
        result["error_category"] = LIVE_SMOKE_INVALID_JSON
        return finalize_live_result(
            result,
            status="failed",
            classification="schema_error",
            message=f"OpenAI Responses API returned JSON that could not be parsed safely: {redact_secret(str(exc))}",
            clock=clock,
        )

    output_text = extract_output_text(response_json)
    response_id_present = isinstance(response_json, dict) and bool(response_json.get("id"))
    minimal_success_evidence = response_has_minimal_success_evidence(response_json, output_text)
    marker_found = EXPECTED_LIVE_SMOKE_MARKER in output_text
    result["output_text_present"] = bool(output_text)
    result["expected_marker_found"] = marker_found
    result["response_id_present"] = response_id_present
    result["minimal_success_evidence_present"] = minimal_success_evidence
    result["output_text"] = redact_secret(output_text)

    if marker_found and minimal_success_evidence and payload.get("store") is False and result["network_call_count"] == 1:
        result["decision"] = LIVE_SMOKE_EXECUTED_AND_PASSED
        return finalize_live_result(
            result,
            status="success",
            classification="success",
            message="Live smoke executed exactly once and returned the expected marker.",
            clock=clock,
        )

    result["decision"] = LIVE_SMOKE_EXECUTED_BUT_FAILED
    if output_text and not marker_found:
        result["error_category"] = LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT
    else:
        result["error_category"] = LIVE_SMOKE_MISSING_SUCCESS_EVIDENCE
    return finalize_live_result(
        result,
        status="failed",
        classification="schema_error",
        message="Live smoke response did not satisfy the expected marker and success evidence contract.",
        clock=clock,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic OpenAI Responses-style adapter evidence without live API calls.",
    )
    parser.add_argument("--mode", required=True, choices=SUPPORTED_MODES, help="Adapter mode to run.")
    parser.add_argument("--input", dest="input_text", help="Inline input text for dry-run or mock mode.")
    parser.add_argument("--input-file", help="UTF-8 text file to use as input.")
    parser.add_argument("--instructions", help="Optional Responses-style instructions field.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model id. Default: {DEFAULT_MODEL}.")
    parser.add_argument(
        "--reasoning-effort",
        default=DEFAULT_REASONING_EFFORT,
        choices=SUPPORTED_REASONING_EFFORTS,
        help=f"Reasoning effort. Default: {DEFAULT_REASONING_EFFORT}.",
    )
    parser.add_argument(
        "--text-verbosity",
        default=DEFAULT_TEXT_VERBOSITY,
        choices=SUPPORTED_TEXT_VERBOSITY,
        help=f"Text verbosity. Default: {DEFAULT_TEXT_VERBOSITY}.",
    )
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="Acknowledge the live boundary gate. STEP 510 still performs no live API call.",
    )
    parser.add_argument(
        "--live-confirm",
        help=f"Required confirmation string for future live readiness: {LIVE_CONFIRMATION_VALUE}.",
    )
    parser.add_argument(
        "--gate-only",
        action="store_true",
        help="Evaluate live smoke gates without performing a network call.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        help=f"Maximum output tokens for a live Responses API smoke call. Default: {DEFAULT_LIVE_MAX_OUTPUT_TOKENS}.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_LIVE_TIMEOUT_SECONDS,
        help=f"HTTP timeout for the live smoke call. Default: {DEFAULT_LIVE_TIMEOUT_SECONDS}.",
    )
    parser.add_argument("--output-json", help="Optional path for deterministic JSON evidence.")
    parser.add_argument("--output-markdown", help="Optional path for an operator Markdown summary.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> OpenAIAdapterConfig:
    return OpenAIAdapterConfig(
        mode=args.mode,
        input_text=read_input_text(args.input_text, args.input_file),
        instructions=args.instructions,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        text_verbosity=args.text_verbosity,
        allow_live=args.allow_live,
        live_confirm=args.live_confirm,
        max_output_tokens=args.max_output_tokens,
        gate_only=args.gate_only,
        timeout_seconds=args.timeout_seconds,
    )


def resolve_output_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = repo_root() / path
    return path


def relative_display_path(path: Path) -> str:
    root = repo_root().resolve()
    resolved = path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(resolved)


def is_under_repo_tmp(path: Path) -> bool:
    tmp_root = (repo_root() / "tmp").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(tmp_root)
    except ValueError:
        return False
    return True


def live_runtime_artifact_path(path_value: str | None) -> str | None:
    if not path_value:
        return None
    path = resolve_output_path(path_value)
    if not is_under_repo_tmp(path):
        raise InputError("--output-json for live mode must stay under tmp/.")
    return relative_display_path(path)


def operator_markdown_output_path(path_value: str | None, *, mode: str) -> Path | None:
    if not path_value:
        return None
    path = resolve_output_path(path_value)
    if mode == "live" and not is_under_repo_tmp(path):
        raise InputError("--output-markdown for live mode must stay under tmp/.")
    return path


def write_json(path_value: str, data: dict[str, Any]) -> Path:
    path = resolve_output_path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(redact_data(data), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def build_operator_markdown(data: dict[str, Any]) -> str:
    safe_data = redact_data(data)
    if safe_data.get("mode") != "live":
        return "\n".join(
            [
                "# ASF OpenAI API Adapter Result",
                "",
                f"- Status: {safe_data.get('status')}",
                f"- Network performed: {safe_data.get('network_performed')}",
                f"- Message: {safe_data.get('message', '')}",
                "",
            ]
        )

    safe_details_json = json.dumps(safe_data.get("safe_details", {}), indent=2, sort_keys=True)
    return "\n".join(
        [
            "# ASF OpenAI Live Smoke Result",
            "",
            f"- Status: {safe_data.get('status')}",
            f"- Classification: {safe_data.get('classification')}",
            f"- Provider: {safe_data.get('provider')}",
            f"- Model: {safe_data.get('model')}",
            f"- Live enabled: {safe_data.get('live_enabled')}",
            f"- Credential present: {safe_data.get('credential_present')}",
            f"- Network attempted: {safe_data.get('network_call_attempted')}",
            f"- Network performed: {safe_data.get('network_call_performed')}",
            f"- Decision: {safe_data.get('decision')}",
            f"- Message: {safe_data.get('message', '')}",
            f"- Next step: {safe_data.get('operator_next_step')}",
            "",
            "## Safe Details",
            "",
            "```json",
            safe_details_json,
            "```",
            "",
        ]
    )


def write_markdown(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_operator_markdown(data), encoding="utf-8", newline="\n")
    return path


def emit_result(data: dict[str, Any], output_json: str | None, output_markdown: str | None, *, mode: str) -> None:
    safe_data = redact_data(data)
    if output_json:
        output_path = write_json(output_json, safe_data)
        print(f"OpenAI adapter evidence written: {redact_secret(str(output_path))}")
    else:
        print(json.dumps(safe_data, indent=2, sort_keys=True))

    markdown_path = operator_markdown_output_path(output_markdown, mode=mode)
    if markdown_path:
        written_path = write_markdown(markdown_path, safe_data)
        print(f"OpenAI adapter operator summary written: {redact_secret(str(written_path))}")


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    config = build_config(args)
    operator_markdown_output_path(args.output_markdown, mode=config.mode)

    if config.mode == "check-env":
        data = run_check_env()
    elif config.mode == "dry-run":
        data = run_dry_run(config)
    elif config.mode == "mock":
        data = run_mock(config)
    elif config.mode == "live":
        data = run_live(config, runtime_artifact_path=live_runtime_artifact_path(args.output_json))
    else:
        raise InputError(f"Unsupported mode: {config.mode}")

    emit_result(data, args.output_json, args.output_markdown, mode=config.mode)
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except InputError as exc:
        print(f"ERROR: {redact_secret(str(exc))}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {redact_secret(str(exc))}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
