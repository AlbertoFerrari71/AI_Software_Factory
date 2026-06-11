from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_gpt_prompt_generator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_gpt_prompt_generator_live", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_plan(path: Path, **updates: object) -> Path:
    payload: dict[str, object] = {
        "step_id": "1020",
        "title": "1020 smoke generate Codex prompt",
        "objective": "Generate a safe docs-only Codex prompt for human review.",
        "risk_level": "L1",
        "phase": "live-controlled-test",
        "allowed_paths": ["docs/motor", "docs/templates"],
        "forbidden_actions": ["commit", "push", "PR", "merge", "deploy"],
    }
    payload.update(updates)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def read_texts(*paths: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


class FakeResponses:
    def __init__(self, behavior: Any) -> None:
        self.behavior = behavior
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self.behavior, BaseException):
            raise self.behavior
        return self.behavior


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def test_live_mode_without_approval_writes_safe_result_and_does_not_call_provider(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    output = tmp_path / "prompt.md"
    result_json = tmp_path / "result.json"
    sanitized = tmp_path / "result.md"
    fake_responses = FakeResponses(SimpleNamespace(output_text="should not be used"))

    packet = module.generate_prompt(
        plan,
        output_path=output,
        mode="live",
        approve_live=False,
        result_json_path=result_json,
        sanitized_result_path=sanitized,
        environ={module.OPENAI_API_KEY_ENV: "present-but-not-used"},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    assert packet["status"] == "LIVE_SKIPPED_NO_APPROVAL"
    assert packet["live_call_attempted"] is False
    assert packet["live_call_count"] == 0
    assert fake_responses.calls == []
    assert output.is_file()
    assert result_json.is_file()
    assert sanitized.is_file()


def test_live_mode_without_provider_secret_does_not_attempt_call(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")

    packet = module.generate_prompt(
        plan,
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={},
        client_factory=lambda _secret: pytest.fail("provider should not be called"),
    )

    assert packet["status"] == "LIVE_SKIPPED_NO_API_KEY"
    assert packet["live_call_attempted"] is False
    assert packet["api_key_present"] is False


def test_provider_secret_value_is_not_written_to_json_or_markdown(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    result_json = tmp_path / "result.json"
    sanitized = tmp_path / "result.md"
    secret_value = "sk-" + "proj-secretvalue123456"
    fake_responses = FakeResponses(RuntimeError(f"authentication failed for {secret_value}"))

    packet = module.generate_prompt(
        plan,
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=result_json,
        sanitized_result_path=sanitized,
        environ={module.OPENAI_API_KEY_ENV: secret_value},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    combined = read_texts(result_json, sanitized)
    assert packet["status"] == "LIVE_BLOCKED_BY_PROVIDER"
    assert packet["error_class"] == "authentication_error"
    assert secret_value not in combined
    assert module.SECRET_REDACTION in combined


def test_quota_or_rate_limit_is_classified_without_retry(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    fake_responses = FakeResponses(RuntimeError("insufficient_quota: project limit reached"))

    packet = module.generate_prompt(
        plan,
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
        client_factory=lambda _secret: FakeClient(fake_responses),
    )

    assert packet["status"] == "LIVE_BLOCKED_BY_QUOTA_OR_RATE_LIMIT"
    assert packet["error_class"] == "quota_exceeded"
    assert packet["live_call_count"] == 1
    assert len(fake_responses.calls) == 1


def test_missing_openai_package_is_config_block(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")

    def missing_package() -> Any:
        raise ImportError("No module named 'openai'")

    monkeypatch.setattr(module, "load_openai_client_class", missing_package)

    packet = module.generate_prompt(
        plan,
        output_path=tmp_path / "prompt.md",
        mode="live",
        approve_live=True,
        result_json_path=tmp_path / "result.json",
        sanitized_result_path=tmp_path / "result.md",
        environ={module.OPENAI_API_KEY_ENV: "present"},
    )

    assert packet["status"] == "LIVE_BLOCKED_BY_CONFIG"
    assert packet["error_class"] == "missing_openai_package"
    assert packet["live_call_attempted"] is False
    assert packet["fallback_mode"] == "mock"


def test_live_success_with_fake_client_writes_prompt_and_result(tmp_path: Path) -> None:
    module = load_module()
    plan = write_plan(tmp_path / "plan.json")
    output = tmp_path / "prompt.md"
    result_json = tmp_path / "result.json"
    sanitized = tmp_path / "result.md"
    fake_responses = FakeResponses(SimpleNamespace(output_text="# Codex Prompt\n\nSafe docs-only prompt."))

    packet = module.generate_prompt(
        plan,
        output_path=output,
        mode="live",
        approve_live=True,
        result_json_path=result_json,
        sanitized_result_path=sanitized,
        environ={module.OPENAI_API_KEY_ENV: "present"},
        client_factory=lambda _secret: FakeClient(fake_responses),
        max_output_tokens=321,
        selected_model="gpt-test-model",
    )

    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert packet["status"] == "LIVE_SUCCESS"
    assert payload["status"] == "LIVE_SUCCESS"
    assert packet["live_call_attempted"] is True
    assert packet["live_call_count"] == 1
    assert len(fake_responses.calls) == 1
    assert fake_responses.calls[0]["max_output_tokens"] == 321
    assert fake_responses.calls[0]["model"] == "gpt-test-model"
    assert "Safe docs-only prompt" in output.read_text(encoding="utf-8")
    assert sanitized.is_file()


def test_source_does_not_contain_direct_os_appunti_patterns() -> None:
    sources = [
        SCRIPT.read_text(encoding="utf-8"),
        Path(__file__).read_text(encoding="utf-8"),
    ]
    forbidden = [
        "Set-" + "Cl" + "ipboard",
        "cl" + "ip.exe",
        "cl" + "ip",
        "pyper" + "cl" + "ip",
        "win32" + "cl" + "ipboard",
        "Cl" + "ipboard",
        "Windows.Forms." + "Cl" + "ipboard",
        "System." + "Windows.Forms",
        "Cl" + "ipboard.Set" + "Text",
        "Set" + "Text(",
        "copy-compact-to-" + "cl" + "ipboard",
    ]
    for content in sources:
        for pattern in forbidden:
            assert pattern not in content


def test_adapter_does_not_execute_real_codex() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "codex exec" not in source.lower()


def test_quality_first_decision_is_documented() -> None:
    decisions = (ROOT / "docs" / "11_DECISIONS.md").read_text(encoding="utf-8")
    assert "Quality-first operating principle" in decisions
    assert "fail-closed behavior" in decisions
