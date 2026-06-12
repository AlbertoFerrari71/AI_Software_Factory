from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asf_gpt_prompt_generator import (  # noqa: E402
    classify_provider_error,
    extract_response_text,
    provider_response_has_refusal,
    redact_sensitive_text,
    sanitize_data,
)


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
SECRET_REDACTION = "[REDACTED_SECRET]"

SUCCESS = "success"
EMPTY = "empty"
PARTIAL = "partial"
MALFORMED = "malformed"
PROVIDER_ERROR = "provider_error"
RATE_LIMITED = "rate_limited"
QUOTA_EXCEEDED = "quota_exceeded"
MISSING_CREDENTIALS = "missing_credentials"
UNKNOWN_SCHEMA = "unknown_schema"

SUPPORTED_STATUSES = {
    SUCCESS,
    EMPTY,
    PARTIAL,
    MALFORMED,
    PROVIDER_ERROR,
    RATE_LIMITED,
    QUOTA_EXCEEDED,
    MISSING_CREDENTIALS,
    UNKNOWN_SCHEMA,
}

PARTIAL_STATUS_MARKERS = {
    "incomplete",
    "partial",
    "requires_action",
    "queued",
    "in_progress",
}


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def render_json(packet: Mapping[str, Any]) -> str:
    return json.dumps(sanitize_data(dict(packet)), indent=2, sort_keys=True) + "\n"


def _input_kind(value: Any) -> str:
    if isinstance(value, str):
        return "json_string"
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return "list"
    if value is None:
        return "none"
    return "object"


def _parse_payload(value: Any) -> tuple[Any, str, str | None]:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None, "json_string", None
        try:
            return json.loads(text), "json_string", None
        except json.JSONDecodeError as exc:
            return None, "json_string", f"invalid JSON: {exc.msg}"
    return value, _input_kind(value), None


def _error_payload(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        error = value.get("error")
        if isinstance(error, Mapping):
            return dict(error)
        if isinstance(error, str):
            return {"message": error}
        status = compact_string(value.get("status")).casefold()
        if status in {"error", "failed"}:
            return {
                "message": value.get("message") or value.get("detail") or "provider error",
                "type": value.get("type") or status,
                "code": value.get("code"),
            }
    return None


def _error_text(error: Mapping[str, Any]) -> str:
    parts = [
        compact_string(error.get("type")),
        compact_string(error.get("code")),
        compact_string(error.get("message")),
        compact_string(error.get("param")),
    ]
    return " ".join(part for part in parts if part)


def _status_for_error_class(error_class: str) -> str:
    if error_class == "rate_limit":
        return RATE_LIMITED
    if error_class == "quota_exceeded":
        return QUOTA_EXCEEDED
    if error_class in {"missing_api_key", "authentication_error"}:
        return MISSING_CREDENTIALS
    if error_class == "bad_request":
        return MALFORMED
    return PROVIDER_ERROR


def _direct_text(value: Any) -> str:
    if not isinstance(value, Mapping):
        return ""
    for key in ("text", "message_text", "normalized_text"):
        text = compact_string(value.get(key))
        if text:
            return text
    content = value.get("content")
    if isinstance(content, str):
        return compact_string(content)
    message = value.get("message")
    if isinstance(message, Mapping):
        content = message.get("content")
        if isinstance(content, str):
            return compact_string(content)
    return ""


def _response_status_marker(value: Any) -> str:
    if not isinstance(value, Mapping):
        return ""
    return compact_string(value.get("status") or value.get("finish_reason")).casefold()


def _looks_empty(value: Any) -> bool:
    return value is None or value == {} or value == [] or value == ""


def normalize_response(value: Any) -> dict[str, Any]:
    payload, input_kind, parse_error = _parse_payload(value)
    base: dict[str, Any] = {
        "status": UNKNOWN_SCHEMA,
        "text": "",
        "input_kind": input_kind,
        "diagnostics": [],
        "provider_error_class": "",
    }

    if parse_error:
        base["status"] = MALFORMED
        base["diagnostics"] = [redact_sensitive_text(parse_error)]
        return base

    if _looks_empty(payload):
        base["status"] = EMPTY
        base["diagnostics"] = ["empty response payload"]
        return base

    error = _error_payload(payload)
    if error is not None:
        error_text = _error_text(error)
        error_class = classify_provider_error(error_text or "provider error")
        base["status"] = _status_for_error_class(error_class)
        base["provider_error_class"] = error_class
        base["diagnostics"] = [redact_sensitive_text(error_text or "provider error")]
        return base

    direct_text = _direct_text(payload)
    response_text = direct_text or extract_response_text(payload)
    status_marker = _response_status_marker(payload)
    if response_text:
        base["status"] = PARTIAL if status_marker in PARTIAL_STATUS_MARKERS else SUCCESS
        base["text"] = redact_sensitive_text(response_text)
        if direct_text:
            base["diagnostics"] = ["direct normalized text"]
        else:
            base["diagnostics"] = ["responses text extracted"]
        return base

    if provider_response_has_refusal(payload):
        base["status"] = PROVIDER_ERROR
        base["provider_error_class"] = "provider_refusal"
        base["diagnostics"] = ["provider refusal without usable text"]
        return base

    if status_marker in PARTIAL_STATUS_MARKERS:
        base["status"] = PARTIAL
        base["diagnostics"] = [f"partial status without text: {status_marker}"]
        return base

    if isinstance(payload, list) and not payload:
        base["status"] = EMPTY
        base["diagnostics"] = ["empty response list"]
        return base

    base["diagnostics"] = ["no supported text or provider error fields found"]
    return base


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize ASF/OpenAI Responses-style payloads.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-json", help="JSON payload string to normalize.")
    source.add_argument("--input-file", help="Path to a JSON payload file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = args.input_json
        if args.input_file:
            payload = Path(args.input_file).read_text(encoding="utf-8")
        packet = normalize_response(payload)
    except OSError as exc:
        packet = {
            "status": MALFORMED,
            "text": "",
            "input_kind": "file",
            "diagnostics": [redact_sensitive_text(str(exc))],
            "provider_error_class": "",
        }
        print(render_json(packet), end="")
        return EXIT_INPUT_ERROR

    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["status"])
    return EXIT_SUCCESS


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
