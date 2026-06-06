from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts import asf_openai_controlled_live_execution_pack as pack


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_openai_controlled_live_execution_pack.py"
RUNBOOK = ROOT / "docs" / "69_ASF_OPENAI_API_ADAPTER_CONTROLLED_LIVE_EXECUTION_PACK.md"
PWSH_TEMPLATE = ROOT / "templates" / "pwsh_command_pack" / "step_540_openai_controlled_live_execution_pack_template.ps1"
FAKE_KEY = "test-openai-key-step540-secret-value"


def encode(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def live_env(**overrides: str) -> dict[str, str]:
    values = {
        "OPENAI_API_KEY": FAKE_KEY,
        "ASF_OPENAI_LIVE_ENABLED": "1",
    }
    values.update(overrides)
    return values


def config(**overrides: object) -> pack.ControlledLiveConfig:
    values: dict[str, object] = {
        "output_dir": "tmp/test_step_540_controlled_live_pack",
    }
    values.update(overrides)
    return pack.ControlledLiveConfig(**values)


def clean_env() -> dict[str, str]:
    safe_names = ["PATH", "PATHEXT", "SystemRoot", "COMSPEC", "TEMP", "TMP"]
    return {name: os.environ[name] for name in safe_names if name in os.environ}


def assert_base_schema(report: dict[str, object], *, status: str, classification: str) -> None:
    assert report["status"] == status
    assert report["classification"] == classification
    assert report["provider"] == "openai"
    assert report["model"] == "gpt-5.5"
    assert isinstance(report["live_enabled"], bool)
    assert isinstance(report["credential_present"], bool)
    assert isinstance(report["dry_run"], bool)
    assert isinstance(report["network_call_count"], int)
    assert isinstance(report["duration_ms"], int)
    assert isinstance(report["timestamp"], str)
    assert report["schema_version"] == pack.PACK_SCHEMA_VERSION
    assert FAKE_KEY not in encode(report)


def assert_no_secret_derivative_fields(value: object) -> None:
    forbidden = [
        "fingerprint",
        "api_key_length",
        "key_length",
        "credential_length",
        "api_key_sha",
        "credential_sha",
        "prefix",
        "suffix",
    ]
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).casefold()
            for fragment in forbidden:
                assert fragment not in lowered
            assert_no_secret_derivative_fields(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_secret_derivative_fields(item)


def test_dry_run_default_is_fail_closed_and_no_network() -> None:
    report = pack.run_controlled_live(config(), environ={})

    assert_base_schema(report, status="skipped", classification="disabled")
    assert report["dry_run"] is True
    assert report["network_performed"] is False
    assert report["network_call_attempted"] is False
    assert report["network_call_count"] == 0
    assert report["credential_present"] is False
    assert report["decision"] == pack.CONTROLLED_LIVE_DECISION_DRY_RUN
    assert report["missing_gates"] == []


def test_cli_default_writes_safe_json_and_markdown_without_key() -> None:
    output_dir = "tmp/test_step_540_cli_default"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", output_dir],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=clean_env(),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Credential present: False" in result.stdout
    assert "Network call count: 0" in result.stdout

    json_path = ROOT / output_dir / pack.DEFAULT_JSON_NAME
    markdown_path = ROOT / output_dir / pack.DEFAULT_MARKDOWN_NAME
    data = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert_base_schema(data, status="skipped", classification="disabled")
    assert ("sk-" + "proj-") not in result.stdout
    assert ("sk-" + "proj-") not in result.stderr
    assert ("sk-" + "proj-") not in markdown
    assert "API key value is not printed or saved." in markdown


def test_live_requested_without_api_key_classifies_credential_missing() -> None:
    report = pack.run_controlled_live(
        config(execution_mode="live", confirm_live_openai=True),
        environ={"ASF_OPENAI_LIVE_ENABLED": "1"},
    )

    assert_base_schema(report, status="skipped", classification="credential_missing")
    assert report["network_call_count"] == 0
    assert "OPENAI_API_KEY" in report["missing_gates"]


def test_api_key_present_but_live_not_enabled_is_not_configured() -> None:
    report = pack.run_controlled_live(
        config(execution_mode="live", confirm_live_openai=True),
        environ={"OPENAI_API_KEY": FAKE_KEY},
    )

    assert_base_schema(report, status="skipped", classification="not_configured")
    assert report["credential_present"] is True
    assert report["live_enabled"] is False
    assert "ASF_OPENAI_LIVE_ENABLED=1" in report["missing_gates"]


def test_live_enabled_but_confirmation_missing_is_live_not_allowed() -> None:
    report = pack.run_controlled_live(
        config(execution_mode="live", confirm_live_openai=False),
        environ=live_env(),
    )

    assert_base_schema(report, status="skipped", classification="live_not_allowed")
    assert report["network_call_count"] == 0
    assert "--confirm-live-openai" in report["missing_gates"]


def test_mock_provider_with_all_gates_uses_no_network() -> None:
    report = pack.run_controlled_live(
        config(execution_mode="mock", confirm_live_openai=True),
        environ=live_env(),
    )

    assert_base_schema(report, status="success", classification="success")
    assert report["network_performed"] is False
    assert report["network_call_attempted"] is False
    assert report["network_call_count"] == 0
    assert report["mock_provider_call_count"] == 1
    assert report["credential_present"] is True
    assert FAKE_KEY not in encode(report)


def test_artifacts_are_safe_and_contain_no_secret_derivatives() -> None:
    report = pack.run_controlled_live(
        config(execution_mode="mock", confirm_live_openai=True, output_dir="tmp/test_step_540_artifacts"),
        environ=live_env(),
    )
    json_path, markdown_path = pack.write_artifacts(report)

    json_text = json_path.read_text(encoding="utf-8")
    markdown = markdown_path.read_text(encoding="utf-8")
    combined = json_text + "\n" + markdown

    assert FAKE_KEY not in combined
    assert "test-openai-key-step540" not in combined
    assert "credential_present" in json_text
    assert "Credential present: True" in markdown
    assert_no_secret_derivative_fields(json.loads(json_text))


def test_runbook_and_template_document_required_guardrails() -> None:
    combined = RUNBOOK.read_text(encoding="utf-8") + "\n" + PWSH_TEMPLATE.read_text(encoding="utf-8")

    for fragment in [
        "API key presente != autorizzazione a chiamare OpenAI",
        "ASF_OPENAI_LIVE_ENABLED=1",
        "--confirm-live-openai",
        "Codex non deve eseguire live call",
        "credential_present",
        "network_call_count",
        "DOCX best-effort/non bloccante",
        "[scriptblock]::Create",
        "pwsh -NoProfile -ExecutionPolicy Bypass -File",
        "git --no-pager",
        "0540-01-Output_Compatto_openai_controlled_live_execution_pack.md",
        "Artifact rule: NNNN-II-Tipo_Nome.ext; no LAST artifacts.",
        "branch + PR",
    ]:
        assert fragment in combined

    assert ("OPENAI_API_KEY=" + "sk-") not in combined
    assert ("sk-" + "proj") not in combined
    assert "setx OPENAI_API_KEY" not in combined


def test_powershell_template_parse_check_passes_and_avoids_fragile_patterns() -> None:
    template_text = PWSH_TEMPLATE.read_text(encoding="utf-8")
    lowered = template_text.casefold()

    for forbidden in ["@'", '@"', " finally", "git push origin main", " danger-full-access"]:
        assert forbidden not in lowered

    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            f"[scriptblock]::Create((Get-Content -LiteralPath '{PWSH_TEMPLATE}' -Raw)) | Out-Null",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
