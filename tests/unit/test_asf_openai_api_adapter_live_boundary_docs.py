from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

NEW_FILES = [
    "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md",
    "templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md",
    "tests/unit/test_asf_openai_api_adapter_live_boundary_gate.py",
    "tests/unit/test_asf_openai_api_adapter_live_boundary_docs.py",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_live_boundary_files_exist() -> None:
    for relative_path in NEW_FILES:
        assert (ROOT / relative_path).exists(), relative_path


def test_live_boundary_docs_cover_required_gate_topics() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md",
            "templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md",
        ]
    )

    for fragment in [
        "STEP 510",
        "OPENAI_API_KEY",
        "ASF_OPENAI_LIVE_ENABLED=1",
        "--allow-live",
        "I_UNDERSTAND_THIS_CALLS_OPENAI_API",
        "CREDENTIAL_MISSING",
        "LIVE_ENV_FLAG_MISSING",
        "LIVE_FLAG_MISSING",
        "LIVE_CONFIRMATION_MISSING",
        "LIVE_READY_FOR_SEPARATE_SMOKE_STEP",
        "LIVE_CALLS_NOT_IMPLEMENTED_IN_STEP_510",
        "network_call_performed",
        "520) OpenAI API Adapter First Controlled Live Smoke Test",
    ]:
        assert fragment in combined


def test_live_boundary_uses_document_number_66_and_preserves_64_65() -> None:
    assert (ROOT / "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md").exists()
    assert (ROOT / "docs/65_ASF_OPENAI_API_ADAPTER.md").exists()
    assert (ROOT / "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md").exists()

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

    assert "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md" in combined
    assert "docs/65_ASF_OPENAI_API_ADAPTER.md" in combined
    assert "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md" in combined


def test_live_boundary_health_and_status_references_are_present() -> None:
    health = read("scripts/check_workflow_health.py")
    dashboard = read("scripts/show_workflow_status.py")

    for fragment in [
        "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md",
        "templates/codex_tasks/asf_openai_api_live_boundary_gate_template.md",
        "ASF OpenAI API Adapter Live Boundary Credential Gate",
    ]:
        assert fragment in health

    assert "docs/66_ASF_OPENAI_API_ADAPTER_LIVE_BOUNDARY_CREDENTIAL_GATE.md" in dashboard


def test_live_boundary_docs_do_not_recommend_setx_or_contain_real_key_like_values() -> None:
    combined = "\n".join(read(path) for path in NEW_FILES if path.endswith(".md"))

    assert "setx OPENAI_API_KEY" not in combined
    assert "sk-proj-" not in combined
    assert "sk-svcacct-" not in combined
    assert "Authorization:" not in combined


def test_central_docs_track_step_510_and_next_step_520() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "README.md",
            "CHANGELOG.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
        ]
    )

    assert "STEP 510" in combined
    assert "OpenAI API Adapter Live Boundary and Credential Gate" in combined
    assert "520) OpenAI API Adapter First Controlled Live Smoke Test" in combined
