from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Callable, Mapping


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

DEFAULT_MODE = "mock"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_PROVIDER = "openai"
DEFAULT_MAX_OUTPUT_TOKENS = 1200
MAX_LIVE_OUTPUT_TOKENS_CAP = 4000
QUALITY_FIRST_OPERATING_PRINCIPLE = "Quality-first operating principle"
STEP_1020_SMOKE_STEP_ID = "1020-smoke-generate-codex-prompt"
STEP_1020_NEXT_STEP = "1020-A) Review and Publish Live Controlled Adapter"
OPENAI_API_KEY_ENV = "OPENAI_" + "API_KEY"
BRIDGE_CODEX_COMMAND_FRAGMENT = (
    "ChatGPT_Bridge",
    "AI_Software_Factory",
    "codex_command",
)
SUPPORTED_MODES = {"mock", "live"}
LIVE_STATUSES = {
    "LIVE_SUCCESS",
    "LIVE_SKIPPED_NO_APPROVAL",
    "LIVE_SKIPPED_NO_API_KEY",
    "LIVE_BLOCKED_BY_CONFIG",
    "LIVE_BLOCKED_BY_PROVIDER",
    "LIVE_BLOCKED_BY_QUOTA_OR_RATE_LIMIT",
    "LIVE_FAILED_SAFE",
}
PROVIDER_ERROR_CLASSES = {
    "missing_api_key",
    "missing_openai_package",
    "invalid_model",
    "authentication_error",
    "permission_error",
    "rate_limit",
    "quota_exceeded",
    "timeout",
    "network_error",
    "bad_request",
    "unknown_provider_error",
    "invalid_live_config",
    "provider_refusal",
}
SECRET_REDACTION = "[REDACTED_SECRET]"
OPENAI_SECRET_PATTERN = re.compile(r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}")
BEARER_SECRET_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(openai[_-]?api[_-]?key|api[_-]?key|authorization|bearer|secret)\b\s*([:=])\s*([\"']?)[^\s,\"'}]+"
)


LiveClientFactory = Callable[[str], Any]


class LiveRetryConfigurationError(RuntimeError):
    """Raised when the provider client cannot guarantee one-call/no-retry behavior."""


class ProviderRefusalError(ValueError):
    """Raised when the provider returned a refusal instead of prompt text."""


@dataclass(frozen=True)
class StepPlan:
    path: Path
    step_id: str
    title: str
    objective: str
    risk_level: str
    phase: str
    allowed_paths: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    source_format: str
    raw: dict[str, Any]


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return []
    if isinstance(value, list | tuple | set):
        items: list[str] = []
        for item in value:
            text = compact_string(item)
            if text:
                items.append(text)
        return items
    text = compact_string(value)
    return [text] if text else []


def redact_sensitive_text(value: Any) -> str:
    text = compact_string(value)
    if not text:
        return ""
    redacted = OPENAI_SECRET_PATTERN.sub(SECRET_REDACTION, text)
    redacted = BEARER_SECRET_PATTERN.sub("Bearer " + SECRET_REDACTION, redacted)

    def replace_assignment(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}{SECRET_REDACTION}"

    return SECRET_ASSIGNMENT_PATTERN.sub(replace_assignment, redacted)


def sanitize_data(value: Any) -> Any:
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, list):
        return [sanitize_data(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_data(item) for item in value]
    if isinstance(value, dict):
        return {redact_sensitive_text(key): sanitize_data(item) for key, item in value.items()}
    return value


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_relative_to_path(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_bridge_codex_command_path(path: Path) -> bool:
    parts = tuple(path.resolve().parts)
    for index in range(0, len(parts) - len(BRIDGE_CODEX_COMMAND_FRAGMENT) + 1):
        if parts[index : index + len(BRIDGE_CODEX_COMMAND_FRAGMENT)] == BRIDGE_CODEX_COMMAND_FRAGMENT:
            return True
    return False


def is_allowed_output_path(path: Path) -> bool:
    resolved = path.resolve()
    tmp_root = Path(gettempdir()).resolve()
    return (
        is_relative_to_path(resolved, repo_root())
        or is_relative_to_path(resolved, tmp_root)
        or is_bridge_codex_command_path(resolved)
    )


def infer_step_id(text: str, fallback: str) -> str:
    match = re.search(r"\b(\d{4}(?:-\d{4})?)\b", text)
    return match.group(1) if match else fallback


def first_markdown_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def load_plan(path: Path) -> StepPlan:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read plan: {path}: {exc}") from exc

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        heading = first_markdown_heading(text)
        step_id = infer_step_id(text, path.stem)
        raw = {
            "step_id": step_id,
            "title": heading or path.stem,
            "objective": heading or "Generate a deterministic Codex prompt from the supplied Markdown plan.",
            "risk_level": "L1",
            "phase": "mock-planning",
            "allowed_paths": [],
            "forbidden_actions": [],
            "source_excerpt": "\n".join(text.splitlines()[:20]),
        }
        return StepPlan(
            path=path.resolve(),
            step_id=step_id,
            title=compact_string(raw["title"]),
            objective=compact_string(raw["objective"]),
            risk_level=compact_string(raw["risk_level"]) or "L1",
            phase=compact_string(raw["phase"]) or "mock-planning",
            allowed_paths=(),
            forbidden_actions=(),
            source_format="markdown",
            raw=raw,
        )

    if not isinstance(parsed, dict):
        raise ValueError("Plan JSON must be an object.")

    step_id = compact_string(parsed.get("step_id") or parsed.get("id") or parsed.get("step"))
    title = compact_string(parsed.get("title") or parsed.get("name") or parsed.get("step_name"))
    objective = compact_string(parsed.get("objective") or parsed.get("goal") or parsed.get("summary"))
    risk_level = compact_string(parsed.get("risk_level") or parsed.get("risk") or "L1")
    phase = compact_string(parsed.get("phase") or parsed.get("current_phase") or "mock-planning")
    if not step_id:
        step_id = infer_step_id(json.dumps(parsed, sort_keys=True), path.stem)
    if not title:
        title = step_id
    if not objective:
        objective = title

    return StepPlan(
        path=path.resolve(),
        step_id=step_id,
        title=title,
        objective=objective,
        risk_level=risk_level,
        phase=phase,
        allowed_paths=tuple(compact_list(parsed.get("allowed_paths"))),
        forbidden_actions=tuple(compact_list(parsed.get("forbidden_actions"))),
        source_format="json",
        raw=parsed,
    )


def mock_generate_prompt(plan: StepPlan, *, generator_mode: str = "mock") -> str:
    plan_json = json.dumps(plan.raw, indent=2, sort_keys=True)
    allowed = "\n".join(f"- {item}" for item in plan.allowed_paths) or "- none declared"
    forbidden = "\n".join(f"- {item}" for item in plan.forbidden_actions) or "- none declared"
    return "\n".join(
        [
            f"# Codex Prompt - {plan.step_id}",
            "",
            "## Objective",
            plan.objective,
            "",
            "## Operating Mode",
            f"- generator_mode: {generator_mode}",
            "- live_provider_calls: disabled",
            "- credential_reading: disabled",
            "- network_access: disabled",
            "",
            "## Step Context",
            f"- step_id: {plan.step_id}",
            f"- title: {plan.title}",
            f"- risk_level: {plan.risk_level}",
            f"- phase: {plan.phase}",
            f"- source_format: {plan.source_format}",
            "",
            "## Allowed Paths",
            allowed,
            "",
            "## Forbidden Actions",
            forbidden,
            "",
            "## Required Agent Behavior",
            "- Work locally and keep changes scoped to the declared plan.",
            "- Do not publish, merge, tag, release, or run uncontrolled external actions.",
            "- Use deterministic checks and report every warning explicitly.",
            "",
            "## Normalized Plan JSON",
            "```json",
            plan_json,
            "```",
            "",
        ]
    )


def render_mock_prompt(plan: StepPlan) -> str:
    return mock_generate_prompt(plan, generator_mode="mock")


def write_text(path: Path, content: str) -> Path:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return resolved


def default_output_path(plan: StepPlan) -> Path:
    return repo_root() / "tmp" / "asf_gpt_prompt_generator" / f"{plan.step_id}-generated-prompt.md"


def default_result_json_path(plan: StepPlan) -> Path:
    return repo_root() / "tmp" / "asf_gpt_prompt_generator" / f"{plan.step_id}-controlled-result.json"


def default_sanitized_result_path(plan: StepPlan) -> Path:
    return repo_root() / "tmp" / "asf_gpt_prompt_generator" / f"{plan.step_id}-controlled-result.md"


def result_markdown_path_from_json(path: Path) -> Path:
    if path.suffix:
        return path.with_name(f"{path.stem}-Sanitized.md")
    return path / "controlled-result-Sanitized.md"


def load_openai_client_class() -> Any:
    module = importlib.import_module("openai")
    try:
        return module.OpenAI
    except AttributeError as exc:
        raise ImportError("openai package does not expose OpenAI client") from exc


def build_default_live_client(api_key: str) -> Any:
    openai_client_class = load_openai_client_class()
    try:
        return openai_client_class(api_key=api_key, max_retries=0)
    except TypeError as exc:
        raise LiveRetryConfigurationError(
            "OpenAI client does not support max_retries=0; live call not attempted."
        ) from exc


def build_live_request_text(plan: StepPlan) -> str:
    safe_plan = json.dumps(sanitize_data(plan.raw), indent=2, sort_keys=True)
    return "\n".join(
        [
            "Generate one safe Codex prompt for a controlled ASF docs-only step.",
            "",
            "Hard constraints:",
            "- Do not include commit, push, pull request, merge, deploy, reset, clean, rebase, or destructive checkout actions.",
            "- Do not include OS appunti usage.",
            "- Do not include live API calls or Codex runs.",
            "- Keep output suitable for human review before any execution.",
            "- Include a concise final report section.",
            "",
            "Step plan JSON:",
            safe_plan,
        ]
    )


def _call_response_serializer(value: Any, name: str) -> Any:
    serializer = getattr(value, name, None)
    if not callable(serializer):
        return None
    try:
        if name == "model_dump":
            try:
                return serializer(mode="json")
            except TypeError:
                return serializer()
        return serializer()
    except Exception:
        return None


def _normalize_provider_response(value: Any, *, _depth: int = 0, _seen: set[int] | None = None) -> Any:
    if _depth > 8:
        return None
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if _seen is None:
        _seen = set()
    object_id = id(value)
    if object_id in _seen:
        return None
    _seen.add(object_id)

    if isinstance(value, MappingABC):
        return {
            str(key): _normalize_provider_response(item, _depth=_depth + 1, _seen=_seen)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [_normalize_provider_response(item, _depth=_depth + 1, _seen=_seen) for item in value]

    for serializer_name in ("model_dump", "to_dict", "dict"):
        serialized = _call_response_serializer(value, serializer_name)
        if serialized is not None and serialized is not value:
            return _normalize_provider_response(serialized, _depth=_depth + 1, _seen=_seen)

    attrs: dict[str, Any] = {}
    for attr_name in (
        "id",
        "object",
        "status",
        "output_text",
        "output",
        "content",
        "text",
        "type",
        "role",
        "refusal",
        "message",
        "choices",
        "error",
    ):
        try:
            attr_value = getattr(value, attr_name)
        except Exception:
            continue
        if attr_value is not None:
            attrs[attr_name] = _normalize_provider_response(attr_value, _depth=_depth + 1, _seen=_seen)

    if attrs:
        return attrs

    public_attrs = getattr(value, "__dict__", None)
    if isinstance(public_attrs, dict):
        return {
            str(key): _normalize_provider_response(item, _depth=_depth + 1, _seen=_seen)
            for key, item in public_attrs.items()
            if not str(key).startswith("_")
        }

    return None


def _append_text_segment(segments: list[str], value: Any) -> None:
    if isinstance(value, str):
        text = compact_string(value)
        if text and text not in segments:
            segments.append(text)
        return
    for item in compact_list(value):
        if item and item not in segments:
            segments.append(item)


def _is_refusal_node(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    node_type = compact_string(value.get("type")).casefold()
    if node_type == "refusal":
        return True
    refusal = value.get("refusal")
    return isinstance(refusal, str) and bool(compact_string(refusal))


def _response_has_refusal(value: Any) -> bool:
    if isinstance(value, dict):
        if _is_refusal_node(value):
            return True
        return any(_response_has_refusal(item) for item in value.values())
    if isinstance(value, list):
        return any(_response_has_refusal(item) for item in value)
    return False


def _iter_content_text_segments(content: Any) -> list[str]:
    segments: list[str] = []
    content_items = content if isinstance(content, list) else [content]
    for content_item in content_items:
        if isinstance(content_item, str):
            _append_text_segment(segments, content_item)
            continue
        if not isinstance(content_item, dict) or _is_refusal_node(content_item):
            continue
        part_type = compact_string(content_item.get("type")).casefold()
        text = content_item.get("text")
        if part_type in {"", "output_text", "text"} and text:
            _append_text_segment(segments, text)
    return segments


def _iter_output_text_segments(normalized: Any) -> list[str]:
    segments: list[str] = []
    if not isinstance(normalized, dict):
        return segments

    _append_text_segment(segments, normalized.get("output_text"))

    choices = normalized.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if isinstance(message, dict):
                _append_text_segment(segments, message.get("content"))

    message = normalized.get("message")
    if isinstance(message, dict):
        _append_text_segment(segments, message.get("content"))

    for segment in _iter_content_text_segments(normalized.get("content")):
        _append_text_segment(segments, segment)

    output = normalized.get("output")
    if isinstance(output, list):
        for item in output:
            if isinstance(item, str):
                _append_text_segment(segments, item)
                continue
            if not isinstance(item, dict) or _is_refusal_node(item):
                continue
            item_type = compact_string(item.get("type")).casefold()
            if item_type == "output_text":
                _append_text_segment(segments, item.get("text"))
            if item_type in {"", "message", "output_text"}:
                for segment in _iter_content_text_segments(item.get("content")):
                    _append_text_segment(segments, segment)

    return segments


def _join_text_segments(segments: list[str]) -> str:
    clean = [compact_string(segment) for segment in segments if compact_string(segment)]
    if not clean:
        return ""
    return "\n".join(clean)


def provider_response_has_refusal(response: Any) -> bool:
    return _response_has_refusal(_normalize_provider_response(response))


def extract_response_text(response: Any) -> str:
    normalized = _normalize_provider_response(response)
    return _join_text_segments(_iter_output_text_segments(normalized))


def classify_provider_error(error: BaseException | str) -> str:
    text = redact_sensitive_text(error)
    lowered = text.lower()
    class_name = error.__class__.__name__.lower() if isinstance(error, BaseException) else ""
    combined = f"{class_name} {lowered}"
    if isinstance(error, ImportError) or "no module named" in combined or "does not expose openai" in combined:
        return "missing_openai_package"
    if "invalid model" in combined or "model_not_found" in combined or "does not exist" in combined:
        return "invalid_model"
    if "authentication" in combined or "invalid_api_key" in combined or "unauthorized" in combined:
        return "authentication_error"
    if "permission" in combined or "forbidden" in combined or "access denied" in combined:
        return "permission_error"
    if "insufficient_quota" in combined or "quota" in combined or "billing" in combined:
        return "quota_exceeded"
    if "rate_limit" in combined or "rate limit" in combined or "ratelimit" in combined:
        return "rate_limit"
    if "timeout" in combined or "timed out" in combined:
        return "timeout"
    if "connection" in combined or "network" in combined or "dns" in combined or "proxy" in combined:
        return "network_error"
    if "badrequest" in combined or "bad request" in combined or "400" in combined:
        return "bad_request"
    if isinstance(error, ProviderRefusalError) or "provider refusal" in combined or "refusal" in combined:
        return "provider_refusal"
    return "unknown_provider_error"


def status_for_error_class(error_class: str) -> str:
    if error_class == "missing_api_key":
        return "LIVE_SKIPPED_NO_API_KEY"
    if error_class in {"missing_openai_package", "invalid_live_config"}:
        return "LIVE_BLOCKED_BY_CONFIG"
    if error_class in {"quota_exceeded", "rate_limit"}:
        return "LIVE_BLOCKED_BY_QUOTA_OR_RATE_LIMIT"
    if error_class in {"invalid_model", "authentication_error", "permission_error", "bad_request", "provider_refusal"}:
        return "LIVE_BLOCKED_BY_PROVIDER"
    return "LIVE_FAILED_SAFE"


def live_next_action(status: str) -> str:
    if status == "LIVE_SUCCESS":
        return "REVIEW_PROMPT_BEFORE_CODEX"
    if status == "LIVE_SKIPPED_NO_API_KEY":
        return "CONFIGURE_API_KEY_OR_RUN_MOCK"
    if status == "LIVE_SKIPPED_NO_APPROVAL":
        return "APPROVE_LIVE_OR_RUN_MOCK"
    if status == "LIVE_BLOCKED_BY_CONFIG":
        return "FIX_LOCAL_LIVE_CONFIG_OR_RUN_MOCK"
    if status == "LIVE_BLOCKED_BY_QUOTA_OR_RATE_LIMIT":
        return "FIX_PROVIDER_QUOTA_OR_RATE_LIMIT_BEFORE_SEPARATE_RETRY"
    if status == "LIVE_BLOCKED_BY_PROVIDER":
        return "FIX_PROVIDER_ACCESS_OR_MODEL_BEFORE_SEPARATE_RETRY"
    return "STOP_REVIEW_SANITIZED_RESULT"


def base_controlled_result(
    plan: StepPlan,
    *,
    mode: str,
    status: str,
    output_prompt_path: Path,
    selected_model: str,
    provider: str,
    max_output_tokens: int,
    result_json_path: Path | None,
    sanitized_result_path: Path | None,
    api_key_present: bool,
    live_call_attempted: bool = False,
    live_call_count: int = 0,
    error_class: str | None = None,
    error_message: str | None = None,
    fallback_mode: str | None = None,
) -> dict[str, Any]:
    result_step_id = compact_string(plan.raw.get("controller_step_id")) or plan.step_id
    packet: dict[str, Any] = {
        "step_id": result_step_id,
        "source_plan_step_id": plan.step_id,
        "mode": mode,
        "status": status,
        "provider": provider,
        "selected_model": selected_model,
        "live_enabled": status == "LIVE_SUCCESS",
        "live_call_attempted": live_call_attempted,
        "live_call_count": live_call_count,
        "api_key_present": api_key_present,
        "api_key_logged": False,
        "raw_secret_logged": False,
        "authorization_header_logged": False,
        "output_prompt_path": str(output_prompt_path.resolve()),
        "prompt_path": str(output_prompt_path.resolve()),
        "result_json_path": str(result_json_path.resolve()) if result_json_path else "",
        "sanitized_result_path": str(sanitized_result_path.resolve()) if sanitized_result_path else "",
        "risk_level": plan.risk_level,
        "source_plan_path": str(plan.path),
        "source_format": plan.source_format,
        "max_output_tokens": max_output_tokens,
        "requires_alberto": status != "LIVE_SUCCESS" and status != "MOCK_SUCCESS",
        "next_action": live_next_action(status) if status in LIVE_STATUSES else "CODEX_DRY_RUN_READY",
    }
    if error_class:
        packet["error_class"] = error_class
    if error_message:
        packet["error_message"] = redact_sensitive_text(error_message)
    if fallback_mode:
        packet["fallback_mode"] = fallback_mode
    return sanitize_live_result(packet)


def sanitize_live_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return sanitize_data(dict(result))


def render_sanitized_markdown(result: Mapping[str, Any]) -> str:
    safe = sanitize_live_result(result)
    lines = [
        f"# {safe.get('step_id', '')} GPT Prompt Generator Controlled Result",
        "",
        f"- mode: {safe.get('mode')}",
        f"- status: {safe.get('status')}",
        f"- provider: {safe.get('provider')}",
        f"- selected_model: {safe.get('selected_model')}",
        f"- live_call_attempted: {safe.get('live_call_attempted')}",
        f"- live_call_count: {safe.get('live_call_count')}",
        f"- api_key_present: {safe.get('api_key_present')}",
        f"- api_key_logged: {safe.get('api_key_logged')}",
        f"- raw_secret_logged: {safe.get('raw_secret_logged')}",
        f"- authorization_header_logged: {safe.get('authorization_header_logged')}",
        f"- output_prompt_path: {safe.get('output_prompt_path')}",
        f"- next_action: {safe.get('next_action')}",
    ]
    if safe.get("fallback_mode"):
        lines.append(f"- fallback_mode: {safe.get('fallback_mode')}")
    if safe.get("error_class"):
        lines.append(f"- error_class: {safe.get('error_class')}")
    if safe.get("error_message"):
        lines.append(f"- error_message: {safe.get('error_message')}")
    lines.extend(["", "Raw provider request and raw provider response are not stored."])
    return "\n".join(lines) + "\n"


def write_controlled_result(
    result: Mapping[str, Any],
    *,
    result_json_path: Path | None = None,
    sanitized_result_path: Path | None = None,
) -> dict[str, Any]:
    packet = sanitize_live_result(result)
    if result_json_path:
        packet["result_json_path"] = str(write_text(result_json_path, render_json(packet)))
    if sanitized_result_path:
        packet["sanitized_result_path"] = str(write_text(sanitized_result_path, render_sanitized_markdown(packet)))
        if result_json_path:
            write_text(result_json_path, render_json(packet))
    return packet


def validate_live_configuration(output_path: Path, max_output_tokens: int) -> tuple[bool, str | None]:
    if not is_allowed_output_path(output_path):
        return False, "output path is outside repo, temp, or authorized Bridge codex_command scope"
    if max_output_tokens <= 0:
        return False, "max output tokens must be greater than zero"
    if max_output_tokens > MAX_LIVE_OUTPUT_TOKENS_CAP:
        return False, f"max output tokens exceeds controlled cap {MAX_LIVE_OUTPUT_TOKENS_CAP}"
    return True, None


def write_mock_fallback_prompt(plan: StepPlan, output_path: Path) -> Path:
    prompt = mock_generate_prompt(plan, generator_mode="mock-fallback")
    return write_text(output_path, prompt)


def live_generate_prompt(
    plan: StepPlan,
    *,
    output_path: Path,
    approve_live: bool,
    selected_model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    result_json_path: Path | None = None,
    sanitized_result_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
    client_factory: LiveClientFactory | None = None,
) -> dict[str, Any]:
    if environ is None:
        source = os.environ
    else:
        source = environ
    output_path = output_path.resolve()
    if result_json_path is None:
        result_json_path = default_result_json_path(plan)
    if sanitized_result_path is None:
        sanitized_result_path = result_markdown_path_from_json(result_json_path)

    api_key = source.get(OPENAI_API_KEY_ENV, "")
    api_key_present = bool(api_key)

    valid_config, config_error = validate_live_configuration(output_path, max_output_tokens)
    if not approve_live:
        write_mock_fallback_prompt(plan, output_path)
        result = base_controlled_result(
            plan,
            mode="live",
            status="LIVE_SKIPPED_NO_APPROVAL",
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=api_key_present,
            fallback_mode="mock",
        )
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)
    if not valid_config:
        result = base_controlled_result(
            plan,
            mode="live",
            status="LIVE_BLOCKED_BY_CONFIG",
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=api_key_present,
            error_class="invalid_live_config",
            error_message=config_error,
        )
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)
    if not api_key_present:
        write_mock_fallback_prompt(plan, output_path)
        result = base_controlled_result(
            plan,
            mode="live",
            status="LIVE_SKIPPED_NO_API_KEY",
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=False,
            error_class="missing_api_key",
            fallback_mode="mock",
        )
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)

    try:
        factory = client_factory
        if factory is None:
            factory = build_default_live_client
        client = factory(api_key)
    except ImportError as exc:
        write_mock_fallback_prompt(plan, output_path)
        error_class = classify_provider_error(exc)
        result = base_controlled_result(
            plan,
            mode="live",
            status=status_for_error_class(error_class),
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=True,
            error_class=error_class,
            error_message=str(exc),
            fallback_mode="mock",
        )
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)
    except LiveRetryConfigurationError as exc:
        result = base_controlled_result(
            plan,
            mode="live",
            status="LIVE_BLOCKED_BY_CONFIG",
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=True,
            error_class="invalid_live_config",
            error_message=str(exc),
        )
        result["automatic_retries_disabled"] = False
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)

    live_call_count = 0
    try:
        live_call_count += 1
        response = client.responses.create(
            model=selected_model,
            input=build_live_request_text(plan),
            max_output_tokens=max_output_tokens,
        )
        prompt_text = extract_response_text(response)
        if not prompt_text:
            if provider_response_has_refusal(response):
                raise ProviderRefusalError("Provider refusal returned instead of prompt text.")
            raise ValueError("Provider response did not contain prompt text.")
        prompt_path = write_text(output_path, redact_sensitive_text(prompt_text))
        result = base_controlled_result(
            plan,
            mode="live",
            status="LIVE_SUCCESS",
            output_prompt_path=prompt_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=True,
            live_call_attempted=True,
            live_call_count=live_call_count,
        )
        result["automatic_retries_disabled"] = client_factory is None
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)
    except Exception as exc:
        error_class = classify_provider_error(exc)
        status = status_for_error_class(error_class)
        write_mock_fallback_prompt(plan, output_path)
        result = base_controlled_result(
            plan,
            mode="live",
            status=status,
            output_prompt_path=output_path,
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            api_key_present=True,
            live_call_attempted=True,
            live_call_count=live_call_count,
            error_class=error_class,
            error_message=str(exc),
            fallback_mode="mock",
        )
        result["automatic_retries_disabled"] = client_factory is None
        return write_controlled_result(result, result_json_path=result_json_path, sanitized_result_path=sanitized_result_path)


def generate_prompt_from_plan(
    plan: StepPlan,
    *,
    output_path: Path | None = None,
    mode: str = DEFAULT_MODE,
    allow_live: bool = False,
    approve_live: bool = False,
    selected_model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    result_json_path: Path | None = None,
    sanitized_result_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
    client_factory: LiveClientFactory | None = None,
) -> dict[str, Any]:
    mode = compact_string(mode) or DEFAULT_MODE
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    prompt_output_path = output_path or default_output_path(plan)
    if mode == "live":
        return live_generate_prompt(
            plan,
            output_path=prompt_output_path,
            approve_live=bool(approve_live or allow_live),
            selected_model=selected_model,
            provider=provider,
            max_output_tokens=max_output_tokens,
            result_json_path=result_json_path,
            sanitized_result_path=sanitized_result_path,
            environ=environ,
            client_factory=client_factory,
        )

    prompt = mock_generate_prompt(plan, generator_mode="mock")
    prompt_path = write_text(output_path or default_output_path(plan), prompt)
    return {
        "step_id": plan.step_id,
        "mode": "mock",
        "selected_model": selected_model,
        "provider": provider,
        "live_enabled": False,
        "prompt_path": str(prompt_path),
        "output_prompt_path": str(prompt_path),
        "risk_level": plan.risk_level,
        "requires_alberto": False,
        "status": "PROMPT_READY",
        "controlled_status": "MOCK_SUCCESS",
        "next_action": "CODEX_DRY_RUN_READY",
        "source_plan_path": str(plan.path),
        "source_format": plan.source_format,
        "api_key_logged": False,
        "raw_secret_logged": False,
    }


def generate_prompt(
    plan_path: Path,
    *,
    output_path: Path | None = None,
    mode: str = DEFAULT_MODE,
    allow_live: bool = False,
    approve_live: bool = False,
    selected_model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    result_json_path: Path | None = None,
    sanitized_result_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
    client_factory: LiveClientFactory | None = None,
) -> dict[str, Any]:
    plan = load_plan(plan_path)
    return generate_prompt_from_plan(
        plan,
        output_path=output_path,
        mode=mode,
        allow_live=allow_live,
        approve_live=approve_live,
        selected_model=selected_model,
        provider=provider,
        max_output_tokens=max_output_tokens,
        result_json_path=result_json_path,
        sanitized_result_path=sanitized_result_path,
        environ=environ,
        client_factory=client_factory,
    )


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ASF Codex prompts in mock mode or controlled live mode.")
    parser.add_argument("--plan", required=True, help="Step plan JSON or Markdown path.")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=sorted(SUPPORTED_MODES), help="Generation mode.")
    parser.add_argument("--allow-live", action="store_true", help="Legacy alias for --approve-live.")
    parser.add_argument("--approve-live", action="store_true", help="Explicitly approve one controlled live attempt.")
    parser.add_argument("--output", help="Generated prompt output path.")
    parser.add_argument("--result-json", help="Controlled run result JSON output path.")
    parser.add_argument("--sanitized-result", help="Controlled run sanitized Markdown output path.")
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS, help="Controlled live output cap.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model label or controlled live model id.")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER, help="Provider label.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON.")
    return parser.parse_args(argv)


def blocked_packet(error: str, *, mode: str, plan_path: str) -> dict[str, Any]:
    return {
        "step_id": "",
        "mode": mode or DEFAULT_MODE,
        "selected_model": DEFAULT_MODEL,
        "provider": DEFAULT_PROVIDER,
        "live_enabled": False,
        "prompt_path": "",
        "risk_level": "UNKNOWN",
        "requires_alberto": True,
        "status": "PROMPT_BLOCKED",
        "next_action": "STOP",
        "source_plan_path": plan_path,
        "errors": [error],
    }


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        packet = generate_prompt(
            Path(args.plan),
            output_path=Path(args.output) if args.output else None,
            mode=args.mode,
            allow_live=bool(args.allow_live),
            approve_live=bool(args.approve_live),
            selected_model=args.model,
            provider=args.provider,
            max_output_tokens=args.max_output_tokens,
            result_json_path=Path(args.result_json) if args.result_json else None,
            sanitized_result_path=Path(args.sanitized_result) if args.sanitized_result else None,
        )
    except ValueError as exc:
        packet = blocked_packet(str(exc), mode=args.mode, plan_path=args.plan)
        print(render_json(packet), end="")
        return EXIT_INPUT_ERROR

    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["prompt_path"])
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
