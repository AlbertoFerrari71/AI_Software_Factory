from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

STEP_530_DOC = "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_step_530_document_exists() -> None:
    assert (ROOT / STEP_530_DOC).exists()


def test_step_530_docs_cover_result_schema_and_classifications() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            STEP_530_DOC,
            "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md",
            "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
        ]
    )

    for fragment in [
        "STEP 530",
        "status",
        "classification",
        "safe_details",
        "provider",
        "model",
        "live_enabled",
        "credential_present",
        "duration_ms",
        "timestamp",
        "not_configured",
        "disabled",
        "credential_missing",
        "live_not_allowed",
        "provider_error",
        "network_error",
        "rate_limited",
        "auth_error",
        "schema_error",
        "unknown_error",
        "--output-markdown",
        "540) OpenAI API Adapter Controlled Live Execution Pack",
    ]:
        assert fragment in combined


def test_step_530_docs_cover_secret_and_no_live_constraints() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            STEP_530_DOC,
            "CHANGELOG.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
            "docs/21_DOCUMENTATION_SYNC.md",
        ]
    )

    for fragment in [
        "mocked tests",
        "without network",
        "without real credentials",
        "never printed",
        "hash",
        "truncated",
        "fingerprint",
        "Codex must not execute live OpenAI API tests",
        "separate task packet",
    ]:
        assert fragment in combined


def test_step_530_references_are_in_workflow_indexes() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "README.md",
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/35_WORKFLOW_HEALTH_CHECK.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "docs/39_WORKFLOW_STATUS_DASHBOARD.md",
            "scripts/check_workflow_health.py",
            "scripts/show_workflow_status.py",
        ]
    )

    assert STEP_530_DOC in combined
    assert "ASF OpenAI API Adapter Live Smoke Result Hardening" in combined


def test_step_530_docs_do_not_contain_real_key_like_values_or_auth_headers() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            STEP_530_DOC,
            "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
        ]
    )

    assert "setx OPENAI_API_KEY" not in combined
    assert "sk-proj-" not in combined
    assert "sk-svcacct-" not in combined
    assert "Authorization:" not in combined
