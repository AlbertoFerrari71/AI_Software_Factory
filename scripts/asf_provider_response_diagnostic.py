from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Mapping as MappingABC
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asf_gpt_prompt_generator import (  # noqa: E402
    DEFAULT_MODEL,
    OPENAI_API_KEY_ENV,
    LiveRetryConfigurationError,
    build_default_live_client,
    classify_provider_error,
    extract_response_text,
    redact_sensitive_text,
)


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3
STEP = "1035"
SANITIZER_VERSION = "1035"
EXPECTED_SENTINEL = "ASF_1035_OK"
DEFAULT_MAX_OUTPUT_TOKENS = 32
DEFAULT_BRIDGE_CODEX_COMMAND = Path(
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command"
)
SHAPE_FILENAME = "1035-Provider-Shape-Sanitized.json"
DIAGNOSTIC_FILENAME = "1035-Provider-Diagnostic-Sanitized.md"

SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "password",
    "credential",
    "cookie",
    "set-cookie",
    "x-api-key",
    "bearer",
    "key",
}
SENSITIVE_KEY_FRAGMENTS = (
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "password",
    "credential",
    "cookie",
    "bearer",
)
RAW_TEXT_KEYS = {
    "text",
    "content",
    "output_text",
    "message",
    "input",
    "prompt",
    "instructions",
    "response",
    "stdout",
    "stderr",
}
ENUM_KEYS = {"object", "type", "role", "status", "finish_reason"}
KNOWN_ATTRS = (
    "id",
    "object",
    "created_at",
    "model",
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
    "incomplete_details",
    "finish_reason",
    "usage",
)


LiveClientFactory = Callable[[str], Any]


def utc_now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def render_json(packet: Mapping[str, Any]) -> str:
    return json.dumps(dict(packet), indent=2, sort_keys=True) + "\n"


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, MappingABC):
        return "dict"
    if isinstance(value, list | tuple):
        return "list"
    return "object"


def normalize_key(key: Any) -> str:
    return str(key).strip().casefold().replace("-", "_")


def is_sensitive_key(key: Any) -> bool:
    normalized = normalize_key(key)
    dashed = normalized.replace("_", "-")
    if normalized in SENSITIVE_KEYS or dashed in SENSITIVE_KEYS:
        return True
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def path_last_key(path: str) -> str:
    if not path:
        return ""
    last = path.split(".")[-1]
    last = re.sub(r"\[\d+\]$", "", last)
    return normalize_key(last)


def normalized_path(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def is_raw_text_path(path: str) -> bool:
    return path_last_key(path) in RAW_TEXT_KEYS


def is_enum_path(path: str) -> bool:
    last = path_last_key(path)
    normalized = normalized_path(path).replace("[].", ".")
    return (
        last in ENUM_KEYS
        or normalized.endswith("error.code")
        or normalized.endswith("incomplete_details.reason")
    )


def _call_serializer(value: Any, name: str) -> tuple[bool, Any]:
    serializer = getattr(value, name, None)
    if not callable(serializer):
        return False, None
    try:
        if name == "model_dump":
            try:
                return True, serializer(mode="json")
            except TypeError:
                return True, serializer()
        return True, serializer()
    except Exception as exc:
        return True, {"serializer_error": redact_sensitive_text(str(exc))}


def object_to_plain_data(value: Any, *, _depth: int = 0, _seen: set[int] | None = None) -> Any:
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
            str(key): object_to_plain_data(item, _depth=_depth + 1, _seen=_seen)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [object_to_plain_data(item, _depth=_depth + 1, _seen=_seen) for item in value]

    for serializer_name in ("model_dump", "to_dict", "dict"):
        called, serialized = _call_serializer(value, serializer_name)
        if called and serialized is not value:
            return object_to_plain_data(serialized, _depth=_depth + 1, _seen=_seen)

    attrs: dict[str, Any] = {}
    for attr_name in KNOWN_ATTRS:
        try:
            attr_value = getattr(value, attr_name)
        except Exception:
            continue
        if attr_value is not None:
            attrs[attr_name] = object_to_plain_data(attr_value, _depth=_depth + 1, _seen=_seen)
    if attrs:
        return attrs

    public_attrs = getattr(value, "__dict__", None)
    if isinstance(public_attrs, dict):
        return {
            str(key): object_to_plain_data(item, _depth=_depth + 1, _seen=_seen)
            for key, item in public_attrs.items()
            if not str(key).startswith("_")
        }
    return None


def redacted_leaf(value: Any, *, sensitive_key: bool = False) -> dict[str, Any]:
    packet: dict[str, Any] = {"type": type_name(value), "redacted": True}
    if sensitive_key:
        packet["sensitive_key"] = True
    if isinstance(value, str):
        packet["length"] = len(value)
        packet["empty"] = value == ""
    return packet


def sanitize_provider_response_shape(
    value: Any,
    *,
    path: str = "",
    max_depth: int = 8,
    max_list_items: int = 5,
    _depth: int = 0,
    _seen: set[int] | None = None,
) -> dict[str, Any]:
    if _depth > max_depth:
        return {"type": "max_depth", "redacted": True}

    if _seen is None:
        _seen = set()

    value_type = type_name(value)
    if value is None:
        return {"type": "null", "value": None}
    if isinstance(value, bool | int | float) and not isinstance(value, bool) or isinstance(value, bool):
        return {"type": value_type, "value": value}
    if isinstance(value, str):
        packet: dict[str, Any] = {"type": "str", "length": len(value), "empty": value == ""}
        if is_enum_path(path) and not is_raw_text_path(path):
            packet["value"] = redact_sensitive_text(value)
            packet["redacted"] = False
        else:
            packet["redacted"] = True
        return packet

    object_id = id(value)
    if object_id in _seen:
        return {"type": value_type, "cycle": True, "redacted": True}
    _seen.add(object_id)

    if isinstance(value, MappingABC):
        keys = [redact_sensitive_text(str(key)) for key in value.keys()]
        packet = {
            "type": "dict",
            "key_count": len(keys),
            "keys": keys,
            "values": {},
        }
        values: dict[str, Any] = {}
        for key, item in value.items():
            key_text = redact_sensitive_text(str(key))
            child_path = key_text if not path else f"{path}.{key_text}"
            if is_sensitive_key(key):
                values[key_text] = redacted_leaf(item, sensitive_key=True)
                continue
            values[key_text] = sanitize_provider_response_shape(
                item,
                path=child_path,
                max_depth=max_depth,
                max_list_items=max_list_items,
                _depth=_depth + 1,
                _seen=_seen,
            )
        packet["values"] = values
        return packet

    if isinstance(value, list | tuple):
        items = []
        for index, item in enumerate(list(value)[:max_list_items]):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            items.append(
                sanitize_provider_response_shape(
                    item,
                    path=child_path,
                    max_depth=max_depth,
                    max_list_items=max_list_items,
                    _depth=_depth + 1,
                    _seen=_seen,
                )
            )
        return {
            "type": "list",
            "length": len(value),
            "items": items,
            "omitted_count": max(0, len(value) - len(items)),
        }

    plain = object_to_plain_data(value)
    if plain is None or plain is value:
        return {"type": "object", "class_name": value.__class__.__name__, "redacted": True}
    return {
        "type": "object",
        "class_name": value.__class__.__name__,
        "shape": sanitize_provider_response_shape(
            plain,
            path=path,
            max_depth=max_depth,
            max_list_items=max_list_items,
            _depth=_depth + 1,
            _seen=set(),
        ),
    }


def count_sensitive_redactions(shape: Any) -> int:
    if isinstance(shape, dict):
        current = 1 if shape.get("sensitive_key") is True else 0
        return current + sum(count_sensitive_redactions(item) for item in shape.values())
    if isinstance(shape, list):
        return sum(count_sensitive_redactions(item) for item in shape)
    return 0


def candidate_from_value(path: str, value: Any, *, expected_sentinel: str | None) -> dict[str, Any]:
    is_string = isinstance(value, str)
    exists = value is not _MISSING
    empty = (value == "") if is_string else False
    usable = is_string and bool(value.strip()) and not normalized_path(path).endswith("refusal")
    contains: bool | None = None
    if expected_sentinel is not None and is_string:
        contains = expected_sentinel in value
    elif expected_sentinel is not None and exists:
        contains = False
    return {
        "path": path,
        "exists": exists,
        "type": type_name(value) if exists else "missing",
        "length": len(value) if is_string else None,
        "empty": empty,
        "redacted": True,
        "usable_text_candidate": usable,
        "contains_expected_sentinel": contains,
    }


class _MissingValue:
    pass


_MISSING = _MissingValue()


def add_candidate(
    candidates: list[dict[str, Any]],
    path: str,
    value: Any = _MISSING,
    *,
    expected_sentinel: str | None,
) -> None:
    candidates.append(candidate_from_value(path, value, expected_sentinel=expected_sentinel))


def detect_candidate_text_paths(value: Any, *, expected_sentinel: str | None = None) -> list[dict[str, Any]]:
    data = object_to_plain_data(value)
    candidates: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return candidates

    add_candidate(candidates, "output_text", data.get("output_text", _MISSING), expected_sentinel=expected_sentinel)

    output = data.get("output")
    if isinstance(output, list):
        for output_index, output_item in enumerate(output):
            if not isinstance(output_item, dict):
                add_candidate(
                    candidates,
                    f"output[{output_index}]",
                    output_item,
                    expected_sentinel=expected_sentinel,
                )
                continue
            if "text" in output_item:
                add_candidate(
                    candidates,
                    f"output[{output_index}].text",
                    output_item.get("text"),
                    expected_sentinel=expected_sentinel,
                )
            content = output_item.get("content")
            content_items = content if isinstance(content, list) else ([content] if content is not None else [])
            for content_index, content_item in enumerate(content_items):
                if isinstance(content_item, dict):
                    for key in ("text", "refusal"):
                        if key in content_item:
                            add_candidate(
                                candidates,
                                f"output[{output_index}].content[{content_index}].{key}",
                                content_item.get(key),
                                expected_sentinel=expected_sentinel,
                            )
                else:
                    add_candidate(
                        candidates,
                        f"output[{output_index}].content[{content_index}]",
                        content_item,
                        expected_sentinel=expected_sentinel,
                    )

    choices = data.get("choices")
    if isinstance(choices, list):
        for choice_index, choice in enumerate(choices):
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if isinstance(message, dict):
                add_candidate(
                    candidates,
                    f"choices[{choice_index}].message.content",
                    message.get("content", _MISSING),
                    expected_sentinel=expected_sentinel,
                )

    message = data.get("message")
    if isinstance(message, dict):
        add_candidate(
            candidates,
            "message.content",
            message.get("content", _MISSING),
            expected_sentinel=expected_sentinel,
        )

    content = data.get("content")
    if isinstance(content, list):
        for content_index, content_item in enumerate(content):
            if isinstance(content_item, dict):
                for key in ("text", "refusal"):
                    if key in content_item:
                        add_candidate(
                            candidates,
                            f"content[{content_index}].{key}",
                            content_item.get(key),
                            expected_sentinel=expected_sentinel,
                        )
            else:
                add_candidate(candidates, f"content[{content_index}]", content_item, expected_sentinel=expected_sentinel)
    elif content is not None:
        add_candidate(candidates, "content", content, expected_sentinel=expected_sentinel)

    return candidates


def build_shape_packet(
    value: Any,
    *,
    source: str,
    expected_sentinel: str | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    data = object_to_plain_data(value)
    shape = sanitize_provider_response_shape(data)
    candidates = detect_candidate_text_paths(data, expected_sentinel=expected_sentinel)
    parser_text = extract_response_text(data)
    parser_result = {
        "type": "str",
        "length": len(parser_text),
        "empty": parser_text == "",
        "redacted": True,
        "contains_expected_sentinel": expected_sentinel in parser_text if expected_sentinel else None,
    }
    return {
        "step": STEP,
        "source": source,
        "raw_payload_saved": False,
        "raw_text_saved": False,
        "sanitizer_version": SANITIZER_VERSION,
        "summary": {
            "top_level_type": type_name(data),
            "top_level_keys": list(data.keys()) if isinstance(data, dict) else [],
            "candidate_text_paths_count": len(candidates),
            "sensitive_fields_redacted_count": count_sensitive_redactions(shape),
            "parser_extracted_text": not parser_result["empty"],
            "parser_contains_expected_sentinel": parser_result["contains_expected_sentinel"],
        },
        "shape": shape,
        "candidate_text_paths": candidates,
        "parser_result": parser_result,
        "errors": errors or [],
    }


def classification_from_error(error_class: str) -> str:
    if error_class in {"authentication_error", "missing_api_key"}:
        return "missing_credentials"
    if error_class == "quota_exceeded":
        return "quota_exceeded"
    if error_class == "rate_limit":
        return "rate_limited"
    if error_class in {"invalid_model", "permission_error", "bad_request", "provider_refusal"}:
        return "provider_blocked"
    return "failed_sanitized"


def run_live_diagnostic(
    *,
    approve_live: bool,
    shape_output: Path,
    diagnostic_output: Path,
    selected_model: str = DEFAULT_MODEL,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    environ: Mapping[str, str] | None = None,
    client_factory: LiveClientFactory | None = None,
) -> dict[str, Any]:
    source = os.environ if environ is None else environ
    api_key_present = bool(source.get(OPENAI_API_KEY_ENV))
    result: dict[str, Any] = {
        "step": STEP,
        "status": "not_attempted",
        "attempted": False,
        "live_call_count": 0,
        "automatic_retries_disabled": True,
        "selected_model": selected_model,
        "max_output_tokens": max_output_tokens,
        "contains_expected_sentinel": None,
        "shape_file": str(shape_output.resolve()),
        "diagnostic_file": str(diagnostic_output.resolve()),
        "api_key_logged": False,
        "authorization_header_logged": False,
        "raw_request_saved": False,
        "raw_response_saved": False,
        "raw_text_saved": False,
        "sanitization_applied": True,
        "notes": "",
    }
    shape_packet = build_shape_packet(
        {},
        source="not_available",
        expected_sentinel=EXPECTED_SENTINEL,
        errors=[],
    )

    if not approve_live:
        result["status"] = "not_attempted"
        result["notes"] = "Live diagnostic not attempted because --approve-live was not supplied."
        write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
        return result
    if not api_key_present:
        result["status"] = "missing_credentials"
        result["notes"] = "Live diagnostic not attempted because credential is missing."
        write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
        return result
    if max_output_tokens <= 0 or max_output_tokens > 256:
        result["status"] = "skipped_no_safe_runner"
        result["notes"] = "Live diagnostic blocked by max output token safety cap."
        write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
        return result

    try:
        factory = client_factory or build_default_live_client
        client = factory(source[OPENAI_API_KEY_ENV])
    except (ImportError, LiveRetryConfigurationError) as exc:
        result["status"] = "skipped_no_safe_runner"
        result["notes"] = redact_sensitive_text(str(exc))
        write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
        return result
    except Exception as exc:
        error_class = classify_provider_error(exc)
        result["status"] = classification_from_error(error_class)
        result["notes"] = redact_sensitive_text(str(exc))
        write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
        return result

    try:
        result["attempted"] = True
        result["live_call_count"] = 1
        response = client.responses.create(
            model=selected_model,
            input=f"Return exactly {EXPECTED_SENTINEL}.",
            max_output_tokens=max_output_tokens,
            store=False,
        )
        shape_packet = build_shape_packet(
            response,
            source="live_provider_response",
            expected_sentinel=EXPECTED_SENTINEL,
            errors=[],
        )
        contains = any(
            item.get("contains_expected_sentinel") is True for item in shape_packet["candidate_text_paths"]
        ) or shape_packet["parser_result"].get("contains_expected_sentinel") is True
        result["contains_expected_sentinel"] = contains
        if contains:
            result["status"] = "success"
            result["notes"] = "Expected public sentinel found in sanitized candidate analysis."
        else:
            result["status"] = "failed_sanitized"
            result["notes"] = "No candidate path contained the expected public sentinel."
    except TypeError as exc:
        result["status"] = "skipped_no_safe_runner"
        result["notes"] = redact_sensitive_text(str(exc))
    except Exception as exc:
        error_class = classify_provider_error(exc)
        result["status"] = classification_from_error(error_class)
        result["notes"] = redact_sensitive_text(str(exc))

    write_diagnostic_outputs(shape_output, diagnostic_output, shape_packet, result)
    return result


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path.resolve()


def write_diagnostic_outputs(
    shape_output: Path,
    diagnostic_output: Path,
    shape_packet: Mapping[str, Any],
    result: Mapping[str, Any],
) -> None:
    write_text(shape_output, render_json(shape_packet))
    write_text(diagnostic_output, render_diagnostic_markdown(shape_packet, result))


def render_diagnostic_markdown(shape_packet: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    summary = shape_packet.get("summary", {})
    candidates = shape_packet.get("candidate_text_paths", [])
    lines = [
        "# 1035 - Provider Diagnostic Sanitized",
        "",
        f"- generated_at_utc: {utc_now()}",
        f"- source: {shape_packet.get('source')}",
        f"- live_status: {result.get('status')}",
        f"- live_call_count: {result.get('live_call_count')}",
        f"- automatic_retries_disabled: {result.get('automatic_retries_disabled')}",
        f"- selected_model: {result.get('selected_model')}",
        f"- raw_request_saved: {result.get('raw_request_saved')}",
        f"- raw_response_saved: {result.get('raw_response_saved')}",
        f"- raw_text_saved: {result.get('raw_text_saved')}",
        f"- top_level_type: {summary.get('top_level_type')}",
        f"- top_level_keys: {', '.join(summary.get('top_level_keys') or [])}",
        f"- candidate_text_paths_count: {summary.get('candidate_text_paths_count')}",
        f"- sensitive_fields_redacted_count: {summary.get('sensitive_fields_redacted_count')}",
        f"- parser_extracted_text: {summary.get('parser_extracted_text')}",
        f"- parser_contains_expected_sentinel: {summary.get('parser_contains_expected_sentinel')}",
        "",
        "## Candidate paths",
        "",
        "| Path | Exists | Type | Length | Empty | Usable | Contains sentinel |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| {path} | {exists} | {type} | {length} | {empty} | {usable} | {sentinel} |".format(
                path=candidate.get("path"),
                exists=candidate.get("exists"),
                type=candidate.get("type"),
                length=candidate.get("length"),
                empty=candidate.get("empty"),
                usable=candidate.get("usable_text_candidate"),
                sentinel=candidate.get("contains_expected_sentinel"),
            )
        )
    lines.extend(
        [
            "",
            "Raw request, raw response and raw text are not stored in this diagnostic.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a sanitized ASF provider response diagnostic.")
    parser.add_argument("--approve-live", action="store_true", help="Approve one controlled live diagnostic call.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Provider model id.")
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--shape-output", default=str(DEFAULT_BRIDGE_CODEX_COMMAND / SHAPE_FILENAME))
    parser.add_argument("--diagnostic-output", default=str(DEFAULT_BRIDGE_CODEX_COMMAND / DIAGNOSTIC_FILENAME))
    parser.add_argument("--json", action="store_true", help="Print sanitized JSON result.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    packet = run_live_diagnostic(
        approve_live=args.approve_live,
        shape_output=Path(args.shape_output),
        diagnostic_output=Path(args.diagnostic_output),
        selected_model=args.model,
        max_output_tokens=args.max_output_tokens,
    )
    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["status"])
    return EXIT_SUCCESS


def main() -> int:
    try:
        return run()
    except ValueError as exc:
        print(f"ERROR: {redact_sensitive_text(str(exc))}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {redact_sensitive_text(str(exc))}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
