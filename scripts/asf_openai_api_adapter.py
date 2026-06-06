from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_TEXT_VERBOSITY = "medium"

SUPPORTED_REASONING_EFFORTS = ("none", "low", "medium", "high", "xhigh")
SUPPORTED_TEXT_VERBOSITY = ("low", "medium", "high")
SUPPORTED_MODES = ("check-env", "dry-run", "mock", "live")

LIVE_MODE_NOT_IMPLEMENTED = "LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500"
MOCK_OUTPUT_TEXT = "ASF OpenAI adapter mock response."

OPENAI_API_KEY_PATTERN = re.compile(r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}")
REDACTION_MARKER = "[REDACTED_OPENAI_API_KEY]"


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class OpenAIAdapterConfig:
    mode: str = "dry-run"
    input_text: str = ""
    instructions: str | None = None
    model: str = DEFAULT_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    text_verbosity: str = DEFAULT_TEXT_VERBOSITY


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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def redact_secret(value: str) -> str:
    return OPENAI_API_KEY_PATTERN.sub(REDACTION_MARKER, value)


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


def build_responses_payload(
    input_text: str,
    *,
    instructions: str | None = None,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    text_verbosity: str = DEFAULT_TEXT_VERBOSITY,
) -> dict[str, Any]:
    config = OpenAIAdapterConfig(
        input_text=input_text,
        instructions=instructions,
        model=model,
        reasoning_effort=reasoning_effort,
        text_verbosity=text_verbosity,
    )
    validate_adapter_config(config)

    payload: dict[str, Any] = {
        "model": model,
        "input": input_text,
    }
    if instructions and instructions.strip():
        payload["instructions"] = instructions
    payload["reasoning"] = {"effort": reasoning_effort}
    payload["text"] = {"verbosity": text_verbosity}
    return payload


def check_environment(environ: Mapping[str, str] | None = None) -> dict[str, bool]:
    source = os.environ if environ is None else environ
    return {"openai_api_key_present": bool(source.get("OPENAI_API_KEY"))}


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


def run_live(config: OpenAIAdapterConfig) -> dict[str, Any]:
    validate_adapter_config(config)
    raise InputError(LIVE_MODE_NOT_IMPLEMENTED)


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
    parser.add_argument("--output-json", help="Optional path for deterministic JSON evidence.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> OpenAIAdapterConfig:
    return OpenAIAdapterConfig(
        mode=args.mode,
        input_text=read_input_text(args.input_text, args.input_file),
        instructions=args.instructions,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        text_verbosity=args.text_verbosity,
    )


def write_json(path_value: str, data: dict[str, Any]) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(redact_data(data), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def emit_result(data: dict[str, Any], output_json: str | None) -> None:
    safe_data = redact_data(data)
    if output_json:
        output_path = write_json(output_json, safe_data)
        print(f"OpenAI adapter evidence written: {output_path}")
        return
    print(json.dumps(safe_data, indent=2, sort_keys=True))


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    config = build_config(args)

    if config.mode == "check-env":
        data = run_check_env()
    elif config.mode == "dry-run":
        data = run_dry_run(config)
    elif config.mode == "mock":
        data = run_mock(config)
    elif config.mode == "live":
        data = run_live(config)
    else:
        raise InputError(f"Unsupported mode: {config.mode}")

    emit_result(data, args.output_json)
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
