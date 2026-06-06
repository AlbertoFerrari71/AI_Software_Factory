from __future__ import annotations

import argparse
import json
import os
import sys
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

STEP_ID = "0560"
RUN_NAME = "OpenAI API Adapter First Authorized Live Run"
ADAPTER_NAME = "scripts.asf_openai_api_adapter.run_live"
ASF_OPENAI_MODEL_ENV = "ASF_OPENAI_MODEL"
ASF_OPENAI_LIVE_RUN_ENV = "ASF_OPENAI_LIVE_RUN"
ASF_OPENAI_LIVE_RUN_VALUE = "1"
DEFAULT_REPORT_PATH = "docs/0560-01-Report_OpenAI_API_Adapter_First_Authorized_Live_Run.md"
DEFAULT_EVIDENCE_PATH = "docs/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json"
DEFAULT_RUNTIME_ARTIFACT_PATH = (
    "tmp/asf_openai_first_authorized_live_run/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json"
)
DEFAULT_MAX_OUTPUT_TOKENS = 16
DEFAULT_TIMEOUT_SECONDS = 15.0

BLOCKED_CLASSIFICATIONS = {
    "credential_missing",
    "not_configured",
    "disabled",
    "live_not_allowed",
    "auth_error",
    "rate_limited",
    "network_error",
    "provider_error",
}
RATE_OR_QUOTA_PROVIDER_CLASSES = {"rate_limited", "quota_exceeded"}


@dataclass(frozen=True)
class FirstAuthorizedLiveRunConfig:
    live: bool = False
    model: str | None = None
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    report_path: str = DEFAULT_REPORT_PATH
    evidence_path: str = DEFAULT_EVIDENCE_PATH


def environment_source(environ: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def resolve_repo_output_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise adapter.InputError("Output paths must stay inside the repository.") from exc
    return resolved


def relative_display_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def validate_first_authorized_config(config: FirstAuthorizedLiveRunConfig) -> None:
    if config.max_output_tokens < 1 or config.max_output_tokens > 32:
        raise adapter.InputError("--max-output-tokens must be between 1 and 32.")
    if config.timeout_seconds <= 0 or config.timeout_seconds > 30:
        raise adapter.InputError("--timeout-seconds must be greater than 0 and no more than 30.")
    for option_name, path_value in (
        ("--report-path", config.report_path),
        ("--evidence-path", config.evidence_path),
    ):
        path = resolve_repo_output_path(path_value)
        if path.name.startswith("LAST-"):
            raise adapter.InputError(f"{option_name} must not use LAST-* artifacts.")


def live_authorized(config: FirstAuthorizedLiveRunConfig, source: Mapping[str, str]) -> bool:
    return config.live or source.get(ASF_OPENAI_LIVE_RUN_ENV) == ASF_OPENAI_LIVE_RUN_VALUE


def authorization_source(config: FirstAuthorizedLiveRunConfig, source: Mapping[str, str]) -> str:
    sources: list[str] = []
    if config.live:
        sources.append("--live")
    if source.get(ASF_OPENAI_LIVE_RUN_ENV) == ASF_OPENAI_LIVE_RUN_VALUE:
        sources.append(f"{ASF_OPENAI_LIVE_RUN_ENV}=1")
    return " + ".join(sources) if sources else "missing"


def selected_model(config: FirstAuthorizedLiveRunConfig, source: Mapping[str, str]) -> str:
    return config.model or source.get(ASF_OPENAI_MODEL_ENV) or adapter.DEFAULT_MODEL


def adapter_environ(source: Mapping[str, str], *, authorized: bool) -> dict[str, str]:
    mapped = dict(source)
    if authorized:
        mapped[adapter.ASF_OPENAI_LIVE_ENABLED_ENV] = adapter.ASF_OPENAI_LIVE_ENABLED_VALUE
    return mapped


def build_adapter_config(
    config: FirstAuthorizedLiveRunConfig,
    source: Mapping[str, str],
    *,
    authorized: bool,
) -> adapter.OpenAIAdapterConfig:
    return adapter.OpenAIAdapterConfig(
        mode="live",
        input_text=adapter.DEFAULT_LIVE_SMOKE_INPUT,
        model=selected_model(config, source),
        reasoning_effort="none",
        text_verbosity="low",
        allow_live=authorized,
        live_confirm=adapter.LIVE_CONFIRMATION_VALUE if authorized else None,
        max_output_tokens=config.max_output_tokens,
        timeout_seconds=config.timeout_seconds,
    )


def output_check(adapter_result: Mapping[str, Any]) -> dict[str, Any]:
    diagnosis = adapter_result.get("failure_reason")
    if not diagnosis:
        if adapter_result.get("status") == "success":
            diagnosis = "success_with_marker"
        elif adapter_result.get("output_text_present") and not adapter_result.get("expected_marker_found"):
            diagnosis = "marker_missing"
        elif not adapter_result.get("output_text_present"):
            diagnosis = "output_text_absent"
        else:
            diagnosis = "unknown"

    return {
        "expected_marker": adapter.EXPECTED_LIVE_SMOKE_MARKER,
        "expected_marker_found": bool(adapter_result.get("expected_marker_found")),
        "output_text_present": bool(adapter_result.get("output_text_present")),
        "minimal_success_evidence_present": bool(adapter_result.get("minimal_success_evidence_present")),
        "diagnosis": str(diagnosis),
        "provider_error_class": adapter_result.get("provider_error_class"),
    }


def classify_step_status(adapter_result: Mapping[str, Any], *, authorized: bool) -> str:
    if adapter_result.get("status") == "success":
        return "COMPLETATO"
    if not authorized:
        return "BLOCKED"
    if adapter_result.get("status") == "skipped":
        return "BLOCKED"
    if adapter_result.get("failure_reason") == "provider_http_error":
        if str(adapter_result.get("provider_error_class")) in RATE_OR_QUOTA_PROVIDER_CLASSES:
            return "BLOCKED_BY_RATE_LIMIT_OR_QUOTA"
        return "BLOCKED_BY_PROVIDER_HTTP_ERROR"
    if str(adapter_result.get("classification")) in BLOCKED_CLASSIFICATIONS:
        return "BLOCKED"
    return "FALLITO"


def retry_hint(status: str, adapter_result: Mapping[str, Any], *, authorized: bool) -> str:
    classification = str(adapter_result.get("classification", ""))
    if status == "COMPLETATO":
        return "Do not retry in this step. A separate authorized step is required for any further live call."
    if not authorized:
        return "Retry only after passing --live or setting ASF_OPENAI_LIVE_RUN=1 in the local shell."
    if classification == "credential_missing":
        return "Set OPENAI_API_KEY only in the local shell, never print it, then retry with --live."
    if adapter_result.get("suggested_next_action"):
        return str(adapter_result.get("suggested_next_action"))
    if classification in {"network_error", "rate_limited", "auth_error", "provider_error"}:
        return "Keep fail-closed and retry only in a separate authorized attempt after fixing the external condition."
    return "Inspect the sanitized report and tests before any separate authorized retry."


def safe_summary(
    config: FirstAuthorizedLiveRunConfig,
    source: Mapping[str, str],
    adapter_result: Mapping[str, Any],
    *,
    authorized: bool,
) -> dict[str, Any]:
    report_path = resolve_repo_output_path(config.report_path)
    evidence_path = resolve_repo_output_path(config.evidence_path)
    status = classify_step_status(adapter_result, authorized=authorized)
    summary: dict[str, Any] = {
        "step": STEP_ID,
        "status": status,
        "timestamp_utc": str(adapter_result.get("timestamp", adapter.utc_timestamp())),
        "adapter_name": ADAPTER_NAME,
        "model": selected_model(config, source),
        "live_authorized": authorized,
        "authorization_source": authorization_source(config, source),
        "request_count": int(adapter_result.get("network_call_count", 0)),
        "latency_ms": int(adapter_result.get("duration_ms", 0)),
        "adapter_status": adapter_result.get("status"),
        "adapter_classification": adapter_result.get("classification"),
        "adapter_decision": adapter_result.get("decision"),
        "network_call_attempted": bool(adapter_result.get("network_call_attempted")),
        "network_call_performed": bool(adapter_result.get("network_call_performed")),
        "output_check": output_check(adapter_result),
        "usage_available": isinstance(adapter_result.get("usage"), dict),
        "response_id_hash_16": adapter_result.get("response_id_hash_16"),
        "report_path": relative_display_path(report_path),
        "evidence_path": relative_display_path(evidence_path) if status == "COMPLETATO" else None,
        "retry_hint": retry_hint(status, adapter_result, authorized=authorized),
        "secret_safety": {
            "api_key_value_logged": False,
            "auth_header_value_logged": False,
            "raw_payload_logged": False,
            "credential_presence_only_boolean": True,
        },
    }
    if isinstance(adapter_result.get("missing_gates"), list):
        summary["missing_gates"] = adapter.redact_data(adapter_result["missing_gates"])
    if adapter_result.get("error_category"):
        summary["error_category"] = adapter_result.get("error_category")
    if adapter_result.get("failure_reason"):
        summary["failure_reason"] = adapter_result.get("failure_reason")
    for key in (
        "provider_error_class",
        "provider_http_status",
        "provider_error_type",
        "provider_error_code",
        "provider_message",
        "retryable",
        "suggested_next_action",
    ):
        if adapter_result.get(key) is not None:
            summary[key] = adapter.redact_data(adapter_result[key])
    if isinstance(adapter_result.get("response_diagnostics"), dict):
        summary["response_diagnostics"] = adapter.redact_data(adapter_result["response_diagnostics"])
    return adapter.redact_data(summary)


def build_evidence(summary: Mapping[str, Any], adapter_result: Mapping[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "step": summary["step"],
        "status": summary["status"],
        "timestamp_utc": summary["timestamp_utc"],
        "adapter_name": summary["adapter_name"],
        "model": summary["model"],
        "live_authorized": summary["live_authorized"],
        "request_count": summary["request_count"],
        "latency_ms": summary["latency_ms"],
        "output_check": summary["output_check"],
        "notes": [
            "Sanitized evidence generated only after a successful authorized live smoke.",
            "No API key, auth header value, raw payload, raw prompt or raw response body is included.",
        ],
    }
    if isinstance(adapter_result.get("usage"), dict):
        evidence["usage"] = adapter.redact_data(adapter_result["usage"])
    if summary.get("response_id_hash_16"):
        evidence["response_id_hash_16"] = summary["response_id_hash_16"]
    return adapter.redact_data(evidence)


def build_report(summary: Mapping[str, Any]) -> str:
    output_check_json = json.dumps(summary.get("output_check", {}), indent=2, sort_keys=True)
    response_diagnostics_json = json.dumps(
        adapter.redact_data(summary.get("response_diagnostics", {})),
        indent=2,
        sort_keys=True,
    )
    missing_gates = summary.get("missing_gates", [])
    if isinstance(missing_gates, list) and missing_gates:
        missing_gate_text = "\n".join(f"- {gate}" for gate in missing_gates)
    else:
        missing_gate_text = "- none"

    evidence_line = summary.get("evidence_path") or "not written; created only after a successful live run"
    return "\n".join(
        [
            f"# {RUN_NAME}",
            "",
            f"Step: {summary.get('step')}",
            f"Status: {summary.get('status')}",
            f"Timestamp UTC: {summary.get('timestamp_utc')}",
            "",
            "## Safe Result",
            "",
            f"- Adapter: {summary.get('adapter_name')}",
            f"- Model: {summary.get('model')}",
            f"- Live authorized: {summary.get('live_authorized')}",
            f"- Authorization source: {summary.get('authorization_source')}",
            f"- Adapter status: {summary.get('adapter_status')}",
            f"- Adapter classification: {summary.get('adapter_classification')}",
            f"- Adapter decision: {summary.get('adapter_decision')}",
            f"- Error category: {summary.get('error_category', '')}",
            f"- Failure reason: {summary.get('failure_reason', '')}",
            f"- Provider error class: {summary.get('provider_error_class', '')}",
            f"- Provider HTTP status: {summary.get('provider_http_status', '')}",
            f"- Provider error type: {summary.get('provider_error_type', '')}",
            f"- Provider error code: {summary.get('provider_error_code', '')}",
            f"- Provider message: {summary.get('provider_message', '')}",
            f"- Retryable: {summary.get('retryable', '')}",
            f"- Suggested next action: {summary.get('suggested_next_action', '')}",
            f"- Request count: {summary.get('request_count')}",
            f"- Latency ms: {summary.get('latency_ms')}",
            f"- Network attempted: {summary.get('network_call_attempted')}",
            f"- Network performed: {summary.get('network_call_performed')}",
            f"- Usage available: {summary.get('usage_available')}",
            f"- Response id hash present: {bool(summary.get('response_id_hash_16'))}",
            f"- Evidence JSON: {evidence_line}",
            "",
            "## Output Check",
            "",
            "```json",
            output_check_json,
            "```",
            "",
            "## Response Diagnostics",
            "",
            "```json",
            response_diagnostics_json,
            "```",
            "",
            "## Missing Gates",
            "",
            missing_gate_text,
            "",
            "## Retry Guidance",
            "",
            str(summary.get("retry_hint")),
            "",
            "Safe retry shape:",
            "",
            "```powershell",
            '$env:OPENAI_API_KEY = "<set in current shell only; never print>"',
            '$env:ASF_OPENAI_LIVE_RUN = "1"',
            "# Optional: $env:ASF_OPENAI_MODEL = \"<model id>\"",
            "python scripts/asf_openai_first_authorized_live_run.py --live",
            "```",
            "",
            "## Secret Guardrails",
            "",
            "- API key value was not printed or written.",
            "- HTTP auth header value was not printed or written.",
            "- Raw request payload and raw response body were not written to this report.",
            "- Credential presence is represented only through safe booleans from the adapter.",
            "- This wrapper delegates the live request path to the repository adapter.",
            "",
        ]
    )


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, data: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(adapter.redact_data(dict(data)), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def run_first_authorized_live(
    config: FirstAuthorizedLiveRunConfig,
    environ: Mapping[str, str] | None = None,
    *,
    http_post_json: adapter.HttpPostJson | None = None,
) -> dict[str, Any]:
    validate_first_authorized_config(config)
    source = environment_source(environ)
    authorized = live_authorized(config, source)
    live_config = build_adapter_config(config, source, authorized=authorized)
    live_result = adapter.run_live(
        live_config,
        environ=adapter_environ(source, authorized=authorized),
        http_post_json=http_post_json,
        runtime_artifact_path=DEFAULT_RUNTIME_ARTIFACT_PATH,
    )
    return safe_summary(config, source, live_result, authorized=authorized)


def write_run_outputs(
    config: FirstAuthorizedLiveRunConfig,
    summary: Mapping[str, Any],
    adapter_result: Mapping[str, Any] | None = None,
) -> tuple[Path, Path | None]:
    report_path = resolve_repo_output_path(config.report_path)
    evidence_path = resolve_repo_output_path(config.evidence_path)
    write_text(report_path, build_report(summary))
    if summary.get("status") == "COMPLETATO" and adapter_result is not None:
        evidence = build_evidence(summary, adapter_result)
        return report_path, write_json(evidence_path, evidence)
    return report_path, None


def run_and_write(
    config: FirstAuthorizedLiveRunConfig,
    environ: Mapping[str, str] | None = None,
    *,
    http_post_json: adapter.HttpPostJson | None = None,
) -> dict[str, Any]:
    validate_first_authorized_config(config)
    source = environment_source(environ)
    authorized = live_authorized(config, source)
    live_config = build_adapter_config(config, source, authorized=authorized)
    live_result = adapter.run_live(
        live_config,
        environ=adapter_environ(source, authorized=authorized),
        http_post_json=http_post_json,
        runtime_artifact_path=DEFAULT_RUNTIME_ARTIFACT_PATH,
    )
    summary = safe_summary(config, source, live_result, authorized=authorized)
    report_path, evidence_path = write_run_outputs(config, summary, live_result)
    summary["report_written"] = relative_display_path(report_path)
    summary["evidence_written"] = relative_display_path(evidence_path) if evidence_path else None
    return adapter.redact_data(summary)


def emit_console_summary(summary: Mapping[str, Any]) -> None:
    print(RUN_NAME)
    print(f"Status: {summary.get('status')}")
    print(f"Live authorized: {summary.get('live_authorized')}")
    print(f"Model: {summary.get('model')}")
    print(f"Request count: {summary.get('request_count')}")
    print(f"Latency ms: {summary.get('latency_ms')}")
    print(f"Output check: {json.dumps(summary.get('output_check', {}), sort_keys=True)}")
    print(f"Report: {summary.get('report_written', summary.get('report_path'))}")
    print(f"Evidence: {summary.get('evidence_written') or 'not written'}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run STEP 0560 OpenAI adapter live smoke through ASF guardrails.")
    parser.add_argument("--live", action="store_true", help="Authorize the single live smoke attempt for this step.")
    parser.add_argument("--model", help=f"Model override. Defaults to {ASF_OPENAI_MODEL_ENV} or adapter default.")
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help=f"Low output ceiling. Default: {DEFAULT_MAX_OUTPUT_TOKENS}.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Live timeout ceiling. Default: {DEFAULT_TIMEOUT_SECONDS}.",
    )
    parser.add_argument("--report-path", default=DEFAULT_REPORT_PATH, help="Versioned Markdown report path.")
    parser.add_argument("--evidence-path", default=DEFAULT_EVIDENCE_PATH, help="Versioned JSON evidence path.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> FirstAuthorizedLiveRunConfig:
    return FirstAuthorizedLiveRunConfig(
        live=args.live,
        model=args.model,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
        report_path=args.report_path,
        evidence_path=args.evidence_path,
    )


def run(argv: list[str]) -> int:
    summary = run_and_write(build_config(parse_args(argv)))
    emit_console_summary(summary)
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
