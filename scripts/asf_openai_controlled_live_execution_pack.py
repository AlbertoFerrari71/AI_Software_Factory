from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import asf_openai_api_adapter as adapter


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

PACK_NAME = "ASF OpenAI API Adapter Controlled Live Execution Pack"
PACK_SCHEMA_VERSION = "1.0"
DEFAULT_OUTPUT_DIR = "tmp/asf_openai_controlled_live_execution_pack"
DEFAULT_JSON_NAME = "asf_openai_controlled_live_execution_pack.json"
DEFAULT_MARKDOWN_NAME = "asf_openai_controlled_live_execution_pack.md"
DEFAULT_CONTROLLED_MAX_OUTPUT_TOKENS = 16
MAX_CONTROLLED_MAX_OUTPUT_TOKENS = 32
DEFAULT_CONTROLLED_TIMEOUT_SECONDS = 15.0
MAX_CONTROLLED_TIMEOUT_SECONDS = 30.0
SUPPORTED_EXECUTION_MODES = ("dry-run", "mock", "live")
ALLOWED_CONTROLLED_LIVE_MODELS = (adapter.DEFAULT_MODEL,)
CONTROLLED_LIVE_DECISION_DRY_RUN = "CONTROLLED_LIVE_DRY_RUN_ONLY"
CONTROLLED_LIVE_DECISION_MOCK = "CONTROLLED_LIVE_MOCK_PROVIDER_ONLY"
CONTROLLED_LIVE_DECISION_BLOCKED = "CONTROLLED_LIVE_BLOCKED_BY_GATE"
CONTROLLED_LIVE_DECISION_EXECUTED = "CONTROLLED_LIVE_EXECUTED"


@dataclass(frozen=True)
class ControlledLiveConfig:
    execution_mode: str = "dry-run"
    model: str = adapter.DEFAULT_MODEL
    max_output_tokens: int = DEFAULT_CONTROLLED_MAX_OUTPUT_TOKENS
    timeout_seconds: float = DEFAULT_CONTROLLED_TIMEOUT_SECONDS
    confirm_live_openai: bool = False
    output_dir: str = DEFAULT_OUTPUT_DIR
    output_json: str | None = None
    output_markdown: str | None = None


def utc_timestamp() -> str:
    return adapter.utc_timestamp()


def elapsed_ms(started_perf: float) -> int:
    return max(0, int(round((time.perf_counter() - started_perf) * 1000)))


def environment_source(environ: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def resolve_output_path(path_value: str) -> Path:
    return adapter.resolve_output_path(path_value)


def require_repo_tmp_path(path: Path, option_name: str) -> None:
    if not adapter.is_under_repo_tmp(path):
        raise adapter.InputError(f"{option_name} must stay under tmp/.")


def default_output_paths(config: ControlledLiveConfig) -> tuple[Path, Path]:
    output_dir = resolve_output_path(config.output_dir)
    json_path = resolve_output_path(config.output_json) if config.output_json else output_dir / DEFAULT_JSON_NAME
    markdown_path = (
        resolve_output_path(config.output_markdown)
        if config.output_markdown
        else output_dir / DEFAULT_MARKDOWN_NAME
    )
    return json_path, markdown_path


def validate_controlled_config(config: ControlledLiveConfig) -> None:
    if config.execution_mode not in SUPPORTED_EXECUTION_MODES:
        allowed = ", ".join(SUPPORTED_EXECUTION_MODES)
        raise adapter.InputError(f"--execution-mode must be one of: {allowed}")
    if config.model not in ALLOWED_CONTROLLED_LIVE_MODELS:
        allowed = ", ".join(ALLOWED_CONTROLLED_LIVE_MODELS)
        raise adapter.InputError(f"--model must be one of the controlled live allowlist: {allowed}")
    if config.max_output_tokens < 1 or config.max_output_tokens > MAX_CONTROLLED_MAX_OUTPUT_TOKENS:
        raise adapter.InputError(f"--max-output-tokens must be between 1 and {MAX_CONTROLLED_MAX_OUTPUT_TOKENS}.")
    if config.timeout_seconds <= 0 or config.timeout_seconds > MAX_CONTROLLED_TIMEOUT_SECONDS:
        raise adapter.InputError(f"--timeout-seconds must be greater than 0 and no more than {MAX_CONTROLLED_TIMEOUT_SECONDS}.")

    json_path, markdown_path = default_output_paths(config)
    require_repo_tmp_path(json_path, "--output-json")
    require_repo_tmp_path(markdown_path, "--output-markdown")


def controlled_adapter_config(config: ControlledLiveConfig) -> adapter.OpenAIAdapterConfig:
    return adapter.OpenAIAdapterConfig(
        mode="live",
        input_text=adapter.DEFAULT_LIVE_SMOKE_INPUT,
        model=config.model,
        reasoning_effort="none",
        text_verbosity="low",
        allow_live=config.confirm_live_openai,
        live_confirm=adapter.LIVE_CONFIRMATION_VALUE if config.confirm_live_openai else None,
        max_output_tokens=config.max_output_tokens,
        timeout_seconds=config.timeout_seconds,
    )


def credential_present(source: Mapping[str, str]) -> bool:
    return bool(source.get(adapter.OPENAI_API_KEY_ENV))


def live_enabled(source: Mapping[str, str]) -> bool:
    return source.get(adapter.ASF_OPENAI_LIVE_ENABLED_ENV) == adapter.ASF_OPENAI_LIVE_ENABLED_VALUE


def live_env_configured(source: Mapping[str, str]) -> bool:
    return adapter.ASF_OPENAI_LIVE_ENABLED_ENV in source


def base_cost_guard(config: ControlledLiveConfig) -> dict[str, Any]:
    return {
        "prompt": "tiny fixed non-sensitive smoke prompt",
        "max_output_tokens": config.max_output_tokens,
        "max_output_tokens_ceiling": MAX_CONTROLLED_MAX_OUTPUT_TOKENS,
        "model_allowlist": list(ALLOWED_CONTROLLED_LIVE_MODELS),
        "timeout_seconds": config.timeout_seconds,
        "planned_live_network_calls": 1 if config.execution_mode == "live" else 0,
        "parallel_live_calls": 0,
        "automatic_retries": 0,
        "store": False,
    }


def gate_report(config: ControlledLiveConfig, source: Mapping[str, str], json_path: Path) -> dict[str, Any]:
    adapter_config = controlled_adapter_config(config)
    return {
        "credential_present": credential_present(source),
        "live_enabled": live_enabled(source),
        "live_env_required": f"{adapter.ASF_OPENAI_LIVE_ENABLED_ENV}={adapter.ASF_OPENAI_LIVE_ENABLED_VALUE}",
        "live_env_configured": live_env_configured(source),
        "confirm_live_openai": config.confirm_live_openai,
        "confirm_flag_required": "--confirm-live-openai",
        "api_key_is_authorization": False,
        "model_allowed": config.model in ALLOWED_CONTROLLED_LIVE_MODELS,
        "runtime_artifact_under_tmp": adapter.is_under_repo_tmp(json_path),
        "tiny_non_sensitive_prompt": adapter.is_tiny_non_sensitive_live_prompt(adapter_config.input_text),
    }


def missing_live_gates(gates: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    if not gates["credential_present"]:
        missing.append(adapter.OPENAI_API_KEY_ENV)
    if not gates["live_enabled"]:
        missing.append(gates["live_env_required"])
    if not gates["confirm_live_openai"]:
        missing.append(gates["confirm_flag_required"])
    if not gates["model_allowed"]:
        missing.append("controlled model allowlist")
    if not gates["runtime_artifact_under_tmp"]:
        missing.append("runtime artifact path under tmp/")
    if not gates["tiny_non_sensitive_prompt"]:
        missing.append("tiny non-sensitive live smoke prompt")
    return missing


def classify_controlled_gate(config: ControlledLiveConfig, gates: Mapping[str, Any], source: Mapping[str, str]) -> str:
    if config.execution_mode == "dry-run":
        return "disabled"
    if not gates["credential_present"]:
        return "credential_missing"
    if not gates["live_enabled"]:
        if not live_env_configured(source):
            return "not_configured"
        return "disabled"
    if not gates["confirm_live_openai"]:
        return "live_not_allowed"
    if not gates["model_allowed"] or not gates["runtime_artifact_under_tmp"] or not gates["tiny_non_sensitive_prompt"]:
        return "not_configured"
    return "success"


def operator_next_step(status: str, classification: str, execution_mode: str) -> str:
    if execution_mode == "dry-run":
        return "Review the dry-run artifacts; keep live disabled until a separate authorized live step is approved."
    if execution_mode == "mock":
        return "Review mock-provider evidence; use it only to validate gates and artifacts before a separate live step."
    if status == "success":
        return "Review the redacted live artifact and require a separate human-approved step before any further live call."
    if classification == "credential_missing":
        return "Set the credential only in the local shell for a future approved live step; never paste or log it."
    if classification in {"not_configured", "disabled", "live_not_allowed"}:
        return "Keep the run fail-closed until the missing gate is intentionally configured."
    return "Keep the system fail-closed, inspect the classification, and retry only through a separate authorized step."


def build_request_plan(config: ControlledLiveConfig) -> dict[str, Any]:
    adapter_config = controlled_adapter_config(config)
    return adapter.build_live_request_plan(adapter_config)


def base_controlled_result(
    config: ControlledLiveConfig,
    source: Mapping[str, str],
    *,
    json_path: Path,
    markdown_path: Path,
    timestamp: str,
) -> dict[str, Any]:
    gates = gate_report(config, source, json_path)
    classification = classify_controlled_gate(config, gates, source)
    missing_gates = [] if config.execution_mode == "dry-run" else missing_live_gates(gates)
    status = "skipped"
    decision = CONTROLLED_LIVE_DECISION_DRY_RUN if config.execution_mode == "dry-run" else CONTROLLED_LIVE_DECISION_BLOCKED

    return {
        "status": status,
        "classification": classification,
        "provider": "openai",
        "model": config.model,
        "live_enabled": gates["live_enabled"],
        "credential_present": gates["credential_present"],
        "dry_run": config.execution_mode == "dry-run",
        "network_performed": False,
        "network_call_attempted": False,
        "network_call_count": 0,
        "duration_ms": 0,
        "timestamp": timestamp,
        "schema_version": PACK_SCHEMA_VERSION,
        "pack": "openai_api_adapter_controlled_live_execution_pack",
        "execution_mode": config.execution_mode,
        "decision": decision,
        "message": "Controlled live execution pack generated without an OpenAI network call.",
        "missing_gates": missing_gates,
        "gates": gates,
        "cost_guard": base_cost_guard(config),
        "live_request_plan": build_request_plan(config),
        "artifacts": {
            "json": adapter.relative_display_path(json_path),
            "markdown": adapter.relative_display_path(markdown_path),
        },
        "operator_next_step": operator_next_step(status, classification, config.execution_mode),
        "secret_safety": {
            "credential_presence_only_boolean": True,
            "no_secret_value": True,
            "no_secret_derivatives": True,
            "no_serialized_credential": True,
        },
    }


def success_mock_response() -> adapter.HttpJsonResponse:
    return adapter.HttpJsonResponse(
        status_code=200,
        body_text=json.dumps(
            {
                "id": "resp_mock_controlled_live_pack",
                "object": "response",
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": adapter.EXPECTED_LIVE_SMOKE_MARKER,
                            }
                        ]
                    }
                ],
            }
        ),
    )


def apply_adapter_live_result(
    result: dict[str, Any],
    live_result: Mapping[str, Any],
    *,
    execution_mode: str,
    mock_provider_call_count: int = 0,
) -> None:
    result["status"] = str(live_result.get("status", result["status"]))
    result["classification"] = str(live_result.get("classification", result["classification"]))
    result["decision"] = (
        CONTROLLED_LIVE_DECISION_MOCK if execution_mode == "mock" else CONTROLLED_LIVE_DECISION_EXECUTED
    )
    result["message"] = str(live_result.get("message", result["message"]))
    result["operator_next_step"] = operator_next_step(
        str(result["status"]),
        str(result["classification"]),
        execution_mode,
    )
    result["adapter_decision"] = live_result.get("decision")
    result["adapter_safe_details"] = live_result.get("safe_details")
    result["mock_provider_call_count"] = mock_provider_call_count

    if execution_mode == "live":
        result["network_performed"] = bool(live_result.get("network_call_performed"))
        result["network_call_attempted"] = bool(live_result.get("network_call_attempted"))
        result["network_call_count"] = int(live_result.get("network_call_count", 0))
    else:
        result["network_performed"] = False
        result["network_call_attempted"] = False
        result["network_call_count"] = 0


def run_controlled_live(
    config: ControlledLiveConfig,
    environ: Mapping[str, str] | None = None,
    *,
    http_post_json: adapter.HttpPostJson | None = None,
) -> dict[str, Any]:
    validate_controlled_config(config)
    started_perf = time.perf_counter()
    timestamp = utc_timestamp()
    source = environment_source(environ)
    json_path, markdown_path = default_output_paths(config)
    result = base_controlled_result(
        config,
        source,
        json_path=json_path,
        markdown_path=markdown_path,
        timestamp=timestamp,
    )

    gates = result["gates"]
    if config.execution_mode == "dry-run" or missing_live_gates(gates):
        result["duration_ms"] = elapsed_ms(started_perf)
        return adapter.redact_data(result)

    live_config = controlled_adapter_config(config)
    runtime_artifact_path = adapter.relative_display_path(json_path)

    if config.execution_mode == "mock":
        calls = 0

        def fake_post(
            endpoint: str,
            payload: dict[str, Any],
            api_key: str,
            timeout_seconds: float,
        ) -> adapter.HttpJsonResponse:
            nonlocal calls
            calls += 1
            return success_mock_response()

        live_result = adapter.run_live(
            live_config,
            environ=source,
            http_post_json=fake_post,
            runtime_artifact_path=runtime_artifact_path,
        )
        apply_adapter_live_result(result, live_result, execution_mode="mock", mock_provider_call_count=calls)
        result["duration_ms"] = elapsed_ms(started_perf)
        return adapter.redact_data(result)

    live_result = adapter.run_live(
        live_config,
        environ=source,
        http_post_json=http_post_json,
        runtime_artifact_path=runtime_artifact_path,
    )
    apply_adapter_live_result(result, live_result, execution_mode="live")
    result["duration_ms"] = elapsed_ms(started_perf)
    return adapter.redact_data(result)


def build_operator_markdown(data: Mapping[str, Any]) -> str:
    safe_data = adapter.redact_data(dict(data))
    safe_details_json = json.dumps(safe_data.get("adapter_safe_details", {}), indent=2, sort_keys=True)
    gates_json = json.dumps(safe_data.get("gates", {}), indent=2, sort_keys=True)
    return "\n".join(
        [
            "# ASF OpenAI API Adapter Controlled Live Execution Pack",
            "",
            f"- Status: {safe_data.get('status')}",
            f"- Classification: {safe_data.get('classification')}",
            f"- Execution mode: {safe_data.get('execution_mode')}",
            f"- Provider: {safe_data.get('provider')}",
            f"- Model: {safe_data.get('model')}",
            f"- Live enabled: {safe_data.get('live_enabled')}",
            f"- Credential present: {safe_data.get('credential_present')}",
            f"- Dry-run: {safe_data.get('dry_run')}",
            f"- Network performed: {safe_data.get('network_performed')}",
            f"- Network call count: {safe_data.get('network_call_count')}",
            f"- Decision: {safe_data.get('decision')}",
            f"- Next step: {safe_data.get('operator_next_step')}",
            "",
            "## Gates",
            "",
            "```json",
            gates_json,
            "```",
            "",
            "## Adapter Safe Details",
            "",
            "```json",
            safe_details_json,
            "```",
            "",
            "## Secret Safety",
            "",
            "- API key value is not printed or saved.",
            "- API key hash, length, prefix, suffix and fingerprint are not recorded.",
            "- Credential presence is represented only as a boolean.",
            "",
        ]
    )


def write_artifacts(data: dict[str, Any]) -> tuple[Path, Path]:
    artifacts = data.get("artifacts", {})
    json_path_value = str(artifacts["json"])
    markdown_path_value = str(artifacts["markdown"])
    json_path = resolve_output_path(json_path_value)
    markdown_path = resolve_output_path(markdown_path_value)
    require_repo_tmp_path(json_path, "json artifact")
    require_repo_tmp_path(markdown_path, "markdown artifact")

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(adapter.redact_data(data), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(build_operator_markdown(data), encoding="utf-8", newline="\n")
    return json_path, markdown_path


def emit_console_summary(data: Mapping[str, Any]) -> None:
    safe_data = adapter.redact_data(dict(data))
    artifacts = safe_data.get("artifacts", {})
    print(PACK_NAME)
    print(f"Status: {safe_data.get('status')}")
    print(f"Classification: {safe_data.get('classification')}")
    print(f"Execution mode: {safe_data.get('execution_mode')}")
    print(f"Live enabled: {safe_data.get('live_enabled')}")
    print(f"Credential present: {safe_data.get('credential_present')}")
    print(f"Network call count: {safe_data.get('network_call_count')}")
    print(f"JSON artifact: {artifacts.get('json')}")
    print(f"Markdown artifact: {artifacts.get('markdown')}")
    print(f"Next step: {safe_data.get('operator_next_step')}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a fail-closed OpenAI API Adapter controlled live execution pack.",
    )
    parser.add_argument(
        "--execution-mode",
        choices=SUPPORTED_EXECUTION_MODES,
        default="dry-run",
        help="Execution posture. Default: dry-run.",
    )
    parser.add_argument("--model", default=adapter.DEFAULT_MODEL, help=f"Controlled model. Default: {adapter.DEFAULT_MODEL}.")
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_CONTROLLED_MAX_OUTPUT_TOKENS,
        help=f"Low output ceiling. Default: {DEFAULT_CONTROLLED_MAX_OUTPUT_TOKENS}.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_CONTROLLED_TIMEOUT_SECONDS,
        help=f"Live timeout ceiling. Default: {DEFAULT_CONTROLLED_TIMEOUT_SECONDS}.",
    )
    parser.add_argument(
        "--confirm-live-openai",
        action="store_true",
        help="Second explicit consent gate for a future live run. API key presence alone is not authorization.",
    )
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory under tmp/.")
    parser.add_argument("--output-json", help="Optional JSON artifact path under tmp/.")
    parser.add_argument("--output-markdown", help="Optional Markdown artifact path under tmp/.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> ControlledLiveConfig:
    return ControlledLiveConfig(
        execution_mode=args.execution_mode,
        model=args.model,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
        confirm_live_openai=args.confirm_live_openai,
        output_dir=args.output_dir,
        output_json=args.output_json,
        output_markdown=args.output_markdown,
    )


def run(argv: list[str]) -> int:
    config = build_config(parse_args(argv))
    data = run_controlled_live(config)
    write_artifacts(data)
    emit_console_summary(data)
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except adapter.InputError as exc:
        print(f"ERROR: {adapter.redact_secret(str(exc))}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {adapter.redact_secret(str(exc))}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
