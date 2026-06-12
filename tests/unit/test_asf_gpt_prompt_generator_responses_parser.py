from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_gpt_prompt_generator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_gpt_prompt_generator_responses", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_plan(path: Path, **updates: object) -> Path:
    payload: dict[str, object] = {
        "step_id": "1030",
        "title": "GPT Live Continuity",
        "objective": "Generate a safe docs-only Codex prompt.",
        "risk_level": "L1",
        "phase": "unit-test",
        "allowed_paths": ["docs/motor", "scripts", "tests/unit"],
        "forbidden_actions": ["commit", "push", "PR", "merge", "deploy"],
    }
    payload.update(updates)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


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


def test_extracts_direct_dict_output_text() -> None:
    module = load_module()

    assert module.extract_response_text({"output_text": "Prompt text"}) == "Prompt text"


def test_extracts_direct_sdk_object_output_text() -> None:
    module = load_module()

    assert module.extract_response_text(SimpleNamespace(output_text="Object prompt")) == "Object prompt"


def test_extracts_output_content_text() -> None:
    module = load_module()
    response = {"output": [{"content": [{"text": "Nested prompt"}]}]}

    assert module.extract_response_text(response) == "Nested prompt"


def test_extracts_top_level_content_text() -> None:
    module = load_module()
    response = {"content": [{"type": "output_text", "text": "Top-level prompt"}]}

    assert module.extract_response_text(response) == "Top-level prompt"


def test_skips_reasoning_and_tool_items_before_message() -> None:
    module = load_module()
    response = {
        "output": [
            {"type": "reasoning", "content": [{"text": "internal reasoning"}]},
            {"type": "function_call", "content": [{"type": "output_text", "text": "tool text"}]},
            {"type": "message", "content": [{"type": "output_text", "text": "Final prompt"}]},
        ]
    }

    assert module.extract_response_text(response) == "Final prompt"


def test_concatenates_multiple_output_text_segments() -> None:
    module = load_module()
    response = {
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "First"}]},
            {"type": "message", "content": [{"type": "output_text", "text": "Second"}]},
        ]
    }

    assert module.extract_response_text(response) == "First\nSecond"


def test_normalizes_sdk_like_model_dump() -> None:
    module = load_module()

    class SdkResponse:
        def model_dump(self, **_: object) -> dict[str, object]:
            return {"output": [{"content": [{"type": "output_text", "text": "From model_dump"}]}]}

    assert module.extract_response_text(SdkResponse()) == "From model_dump"


def test_object_without_text_fails_closed_to_empty_text() -> None:
    module = load_module()

    assert module.extract_response_text({"output": [{"type": "reasoning", "summary": "no prompt"}]}) == ""


def test_refusal_is_not_prompt_text(tmp_path: Path) -> None:
    module = load_module()
    response = {"output": [{"type": "message", "content": [{"type": "refusal", "refusal": "No."}]}]}
    fake_responses = FakeResponses(response)

    assert module.extract_response_text(response) == ""
    assert module.provider_response_has_refusal(response) is True

    packet = module.generate_prompt(
        write_plan(tmp_path / "plan.json"),
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    assert packet["status"] == "LIVE_BLOCKED_BY_PROVIDER"
    assert packet["error_class"] == "provider_refusal"
    assert packet["live_call_count"] == 1


def test_secret_sentinel_is_redacted_from_prompt_and_results(tmp_path: Path) -> None:
    module = load_module()
    secret = "sk-" + "proj-secretvalue123456"
    response = {"output": [{"type": "message", "content": [{"type": "output_text", "text": f"# Prompt {secret}"}]}]}
    fake_responses = FakeResponses(response)

    module.generate_prompt(
        write_plan(tmp_path / "plan.json"),
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: secret},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [tmp_path / "prompt.md", tmp_path / "result.json", tmp_path / "result.md"]
    )
    assert secret not in combined
    assert module.SECRET_REDACTION in combined


def test_default_openai_client_disables_sdk_retries(monkeypatch, tmp_path: Path) -> None:
    module = load_module()
    fake_responses = FakeResponses(SimpleNamespace(output_text="# Prompt\n\nSafe."))

    class FakeOpenAI:
        init_kwargs: list[dict[str, Any]] = []

        def __init__(self, **kwargs: Any) -> None:
            self.__class__.init_kwargs.append(kwargs)
            self.responses = fake_responses

    monkeypatch.setattr(module, "load_openai_client_class", lambda: FakeOpenAI)

    packet = module.generate_prompt(
        write_plan(tmp_path / "plan.json"),
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
    )

    assert packet["status"] == "LIVE_SUCCESS"
    assert FakeOpenAI.init_kwargs[0]["max_retries"] == 0
    assert packet["automatic_retries_disabled"] is True


def test_default_openai_client_blocks_when_retry_disable_is_not_supported(monkeypatch, tmp_path: Path) -> None:
    module = load_module()

    class OldOpenAI:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

    monkeypatch.setattr(module, "load_openai_client_class", lambda: OldOpenAI)

    packet = module.generate_prompt(
        write_plan(tmp_path / "plan.json"),
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
    )

    assert packet["status"] == "LIVE_BLOCKED_BY_CONFIG"
    assert packet["live_call_attempted"] is False
    assert packet["automatic_retries_disabled"] is False
