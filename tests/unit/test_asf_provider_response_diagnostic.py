from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_provider_response_diagnostic.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_provider_response_diagnostic", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponses:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def rendered(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def test_sanitizer_redacts_sensitive_keys_and_text_fields() -> None:
    module = load_module()
    secret = "sk-test-secret123456"
    payload = {
        "type": "response",
        "status": "completed",
        "api_key": secret,
        "output_text": "secret provider text",
        "message": "do not store this",
        "content": [{"type": "output_text", "text": "candidate text"}],
    }

    shape = module.sanitize_provider_response_shape(payload)
    text = rendered(shape)

    assert secret not in text
    assert "secret provider text" not in text
    assert "candidate text" not in text
    assert shape["values"]["api_key"]["redacted"] is True
    assert shape["values"]["api_key"]["sensitive_key"] is True
    assert shape["values"]["output_text"]["length"] == len("secret provider text")
    assert shape["values"]["output_text"]["redacted"] is True
    assert shape["values"]["type"]["value"] == "response"
    assert shape["values"]["status"]["value"] == "completed"


def test_sanitizer_handles_lists_and_sdk_like_objects() -> None:
    module = load_module()

    class SdkResponse:
        def model_dump(self, **_: object) -> dict[str, object]:
            return {
                "object": "response",
                "output": [
                    {"content": [{"type": "output_text", "text": "first"}]},
                    {"content": [{"type": "output_text", "text": "second"}]},
                    {"content": [{"type": "output_text", "text": "third"}]},
                    {"content": [{"type": "output_text", "text": "fourth"}]},
                    {"content": [{"type": "output_text", "text": "fifth"}]},
                    {"content": [{"type": "output_text", "text": "sixth"}]},
                ],
            }

    shape = module.sanitize_provider_response_shape(SdkResponse())
    text = rendered(shape)

    assert "first" not in text
    assert "sixth" not in text
    assert shape["type"] == "object"
    assert shape["shape"]["values"]["output"]["type"] == "list"
    assert shape["shape"]["values"]["output"]["omitted_count"] == 1


def test_candidate_detector_finds_known_text_paths_without_raw_text() -> None:
    module = load_module()
    payload = {
        "output_text": "ASF_1035_OK",
        "output": [{"content": [{"type": "output_text", "text": "nested"}]}],
        "choices": [{"message": {"content": "choice content"}}],
    }

    candidates = module.detect_candidate_text_paths(payload, expected_sentinel=module.EXPECTED_SENTINEL)
    text = rendered(candidates)

    paths = {item["path"] for item in candidates}
    assert "output_text" in paths
    assert "output[0].content[0].text" in paths
    assert "choices[0].message.content" in paths
    assert "nested" not in text
    assert "choice content" not in text
    output_text = next(item for item in candidates if item["path"] == "output_text")
    assert output_text["contains_expected_sentinel"] is True
    assert output_text["usable_text_candidate"] is True


def test_candidate_detector_marks_empty_and_non_text_candidates() -> None:
    module = load_module()
    payload = {
        "output_text": "",
        "output": [{"content": [{"text": {"value": "not directly supported"}}]}],
    }

    candidates = module.detect_candidate_text_paths(payload, expected_sentinel=module.EXPECTED_SENTINEL)
    output_text = next(item for item in candidates if item["path"] == "output_text")
    nested = next(item for item in candidates if item["path"] == "output[0].content[0].text")

    assert output_text["empty"] is True
    assert output_text["usable_text_candidate"] is False
    assert nested["type"] == "dict"
    assert nested["usable_text_candidate"] is False


def test_build_shape_packet_contains_only_sanitized_parser_result() -> None:
    module = load_module()
    payload = {"output": [{"content": [{"type": "output_text", "text": "ASF_1035_OK"}]}]}

    packet = module.build_shape_packet(
        payload,
        source="local_fixture",
        expected_sentinel=module.EXPECTED_SENTINEL,
    )
    text = rendered(packet)

    assert module.EXPECTED_SENTINEL not in text
    assert packet["raw_payload_saved"] is False
    assert packet["raw_text_saved"] is False
    assert packet["parser_result"]["contains_expected_sentinel"] is True
    assert packet["summary"]["candidate_text_paths_count"] >= 1


def test_live_diagnostic_requires_approval_and_does_not_call_provider(tmp_path: Path) -> None:
    module = load_module()
    fake_responses = FakeResponses(SimpleNamespace(output_text=module.EXPECTED_SENTINEL))

    packet = module.run_live_diagnostic(
        approve_live=False,
        shape_output=tmp_path / "shape.json",
        diagnostic_output=tmp_path / "diagnostic.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    assert packet["status"] == "not_attempted"
    assert packet["live_call_count"] == 0
    assert fake_responses.calls == []
    assert (tmp_path / "shape.json").is_file()
    assert (tmp_path / "diagnostic.md").is_file()


def test_live_diagnostic_success_is_one_call_and_does_not_write_raw_response(tmp_path: Path) -> None:
    module = load_module()
    fake_responses = FakeResponses(
        {
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": module.EXPECTED_SENTINEL}]}
            ]
        }
    )

    packet = module.run_live_diagnostic(
        approve_live=True,
        shape_output=tmp_path / "shape.json",
        diagnostic_output=tmp_path / "diagnostic.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )
    combined = (tmp_path / "shape.json").read_text(encoding="utf-8") + (
        tmp_path / "diagnostic.md"
    ).read_text(encoding="utf-8")

    assert packet["status"] == "success"
    assert packet["live_call_count"] == 1
    assert len(fake_responses.calls) == 1
    assert fake_responses.calls[0]["store"] is False
    assert packet["automatic_retries_disabled"] is True
    assert packet["raw_response_saved"] is False
    assert packet["raw_text_saved"] is False
    assert module.EXPECTED_SENTINEL not in combined


def test_live_diagnostic_classifies_quota_without_raw_secret(tmp_path: Path) -> None:
    module = load_module()
    secret = "sk-test-secret123456"
    fake_responses = FakeResponses(RuntimeError(f"insufficient_quota for {secret}"))

    packet = module.run_live_diagnostic(
        approve_live=True,
        shape_output=tmp_path / "shape.json",
        diagnostic_output=tmp_path / "diagnostic.md",
        environ={module.OPENAI_API_KEY_ENV: secret},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )
    combined = (tmp_path / "shape.json").read_text(encoding="utf-8") + (
        tmp_path / "diagnostic.md"
    ).read_text(encoding="utf-8") + rendered(packet)

    assert packet["status"] == "quota_exceeded"
    assert packet["live_call_count"] == 1
    assert secret not in combined
