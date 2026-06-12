from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_responses_parser.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_responses_parser", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_normalizes_direct_text_dict() -> None:
    module = load_module()

    packet = module.normalize_response({"status": "success", "text": "Ready"})

    assert packet["status"] == "success"
    assert packet["text"] == "Ready"


def test_normalizes_output_text_json_string() -> None:
    module = load_module()

    packet = module.normalize_response(json.dumps({"output_text": "Prompt"}))

    assert packet["status"] == "success"
    assert packet["text"] == "Prompt"
    assert packet["input_kind"] == "json_string"


def test_concatenates_nested_response_content_blocks() -> None:
    module = load_module()
    payload = {
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "First"}]},
            {"type": "message", "content": [{"type": "output_text", "text": "Second"}]},
        ]
    }

    packet = module.normalize_response(payload)

    assert packet["status"] == "success"
    assert packet["text"] == "First\nSecond"


def test_normalizes_top_level_content_blocks() -> None:
    module = load_module()

    packet = module.normalize_response({"content": [{"type": "output_text", "text": "Top-level"}]})

    assert packet["status"] == "success"
    assert packet["text"] == "Top-level"


def test_empty_and_partial_payloads_are_classified() -> None:
    module = load_module()

    assert module.normalize_response({})["status"] == "empty"
    partial = module.normalize_response({"status": "incomplete", "output": []})
    assert partial["status"] == "partial"
    assert partial["text"] == ""


def test_malformed_json_is_sanitized() -> None:
    module = load_module()

    packet = module.normalize_response("{not-json")

    assert packet["status"] == "malformed"
    assert "invalid JSON" in packet["diagnostics"][0]


def test_provider_error_classes_are_mapped() -> None:
    module = load_module()

    cases = [
        ({"error": {"message": "rate limit exceeded", "type": "rate_limit"}}, "rate_limited"),
        ({"error": {"message": "insufficient_quota", "code": "insufficient_quota"}}, "quota_exceeded"),
        ({"error": {"message": "invalid_api_key"}}, "missing_credentials"),
        ({"error": {"message": "Bad request malformed payload", "type": "bad_request"}}, "malformed"),
        ({"error": {"message": "permission denied", "type": "permission_error"}}, "provider_error"),
    ]

    for payload, expected_status in cases:
        assert module.normalize_response(payload)["status"] == expected_status


def test_unknown_schema_does_not_invent_success() -> None:
    module = load_module()

    packet = module.normalize_response({"unexpected": [{"value": 1}]})

    assert packet["status"] == "unknown_schema"
    assert packet["text"] == ""


def test_secrets_are_redacted_from_text_and_diagnostics() -> None:
    module = load_module()
    secret = "sk-" + "proj-secretvalue123456"

    text_packet = module.normalize_response({"output_text": f"Prompt {secret}"})
    error_packet = module.normalize_response({"error": {"message": f"api_key={secret}"}})

    combined = json.dumps([text_packet, error_packet], sort_keys=True)
    assert secret not in combined
    assert module.SECRET_REDACTION in combined
