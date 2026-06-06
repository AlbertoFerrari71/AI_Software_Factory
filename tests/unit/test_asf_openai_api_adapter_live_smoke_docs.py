from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

NEW_FILES = [
    "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md",
    "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md",
    "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md",
    "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
    "tests/unit/test_asf_openai_api_adapter_live_smoke.py",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_live_smoke_files_exist() -> None:
    for relative_path in NEW_FILES:
        assert (ROOT / relative_path).exists(), relative_path


def test_live_smoke_docs_cover_required_safety_topics() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md",
            "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md",
            "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md",
            "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
        ]
    )

    for fragment in [
        "STEP 520",
        "OPENAI_API_KEY",
        "ASF_OPENAI_LIVE_ENABLED=1",
        "--allow-live",
        "I_UNDERSTAND_THIS_CALLS_OPENAI_API",
        "Return exactly ASF_OPENAI_LIVE_SMOKE_OK.",
        "store: false",
        "tmp/",
        "LIVE_SMOKE_NOT_RUN_MISSING_GATE",
        "LIVE_SMOKE_NOT_RUN_NETWORK_BLOCKED",
        "LIVE_SMOKE_UNEXPECTED_MODEL_OUTPUT",
        "LIVE_SMOKE_EXECUTED_AND_PASSED",
        "STEP 530",
        "540) OpenAI API Adapter Controlled Live Execution Pack",
        "provider_http_error",
        "quota_exceeded",
        "0560-F) Publish Provider-Blocked Live Run Diagnostic Pack",
    ]:
        assert fragment in combined


def test_live_smoke_uses_document_number_67_and_preserves_65_66() -> None:
    assert (ROOT / "docs/65_ASF_OPENAI_API_ADAPTER.md").exists()
    assert (ROOT / "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md").exists()
    assert (ROOT / "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md").exists()
    assert (ROOT / "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md").exists()
    assert (ROOT / "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md").exists()

    combined = "\n".join(
        read(path)
        for path in [
            "README.md",
            "CHANGELOG.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
            "docs/21_DOCUMENTATION_SYNC.md",
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/35_WORKFLOW_HEALTH_CHECK.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "docs/39_WORKFLOW_STATUS_DASHBOARD.md",
        ]
    )

    assert "docs/65_ASF_OPENAI_API_ADAPTER.md" in combined
    assert "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md" in combined
    assert "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md" in combined
    assert "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md" in combined
    assert "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md" in combined


def test_live_smoke_health_and_status_references_are_present() -> None:
    health = read("scripts/check_workflow_health.py")
    dashboard = read("scripts/show_workflow_status.py")

    for fragment in [
        "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md",
        "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md",
        "docs/0560-03-Diagnostic_OpenAI_Provider_HTTP_Error_And_Rate_Limit.md",
        "templates/codex_tasks/asf_openai_api_live_smoke_test_template.md",
        "ASF OpenAI API Adapter First Controlled Live Smoke Test",
        "ASF OpenAI API Adapter Live Smoke Result Hardening",
        "OpenAI Provider HTTP Error and Rate Limit Diagnostic",
    ]:
        assert fragment in health

    assert "docs/67_ASF_OPENAI_API_ADAPTER_FIRST_CONTROLLED_LIVE_SMOKE_TEST.md" in dashboard
    assert "docs/68_ASF_OPENAI_API_ADAPTER_LIVE_SMOKE_RESULT_HARDENING.md" in dashboard


def test_live_smoke_docs_do_not_contain_real_key_like_values_or_auth_headers() -> None:
    combined = "\n".join(read(path) for path in NEW_FILES if path.endswith(".md"))

    assert "setx OPENAI_API_KEY" not in combined
    assert "sk-proj-" not in combined
    assert "sk-svcacct-" not in combined
    assert "Authorization:" not in combined
