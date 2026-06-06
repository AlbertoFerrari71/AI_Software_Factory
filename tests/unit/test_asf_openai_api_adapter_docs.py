from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

NEW_FILES = [
    "scripts/asf_openai_api_adapter.py",
    "tests/unit/test_asf_openai_api_adapter.py",
    "tests/unit/test_asf_openai_api_adapter_docs.py",
    "docs/65_ASF_OPENAI_API_ADAPTER.md",
    "templates/codex_tasks/asf_openai_api_adapter_template.md",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_openai_api_adapter_files_exist() -> None:
    for relative_path in NEW_FILES:
        assert (ROOT / relative_path).exists(), relative_path


def test_openai_api_adapter_docs_cover_required_safety_topics() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/65_ASF_OPENAI_API_ADAPTER.md",
            "templates/codex_tasks/asf_openai_api_adapter_template.md",
        ]
    )

    required_fragments = [
        "STEP 500",
        "Responses-style",
        "OPENAI_API_KEY",
        "Do not paste API keys",
        "no live API calls",
        "network_performed",
        "mock",
        "dry-run",
        "LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500",
        "510) OpenAI API Adapter Live Boundary and Credential Gate",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_openai_api_adapter_health_and_status_references_are_present() -> None:
    health = read("scripts/check_workflow_health.py")
    dashboard = read("scripts/show_workflow_status.py")

    for fragment in [
        "docs/65_ASF_OPENAI_API_ADAPTER.md",
        "scripts/asf_openai_api_adapter.py",
        "templates/codex_tasks/asf_openai_api_adapter_template.md",
        "ASF OpenAI API Adapter",
    ]:
        assert fragment in health

    for fragment in [
        "docs/65_ASF_OPENAI_API_ADAPTER.md",
        "scripts/asf_openai_api_adapter.py",
    ]:
        assert fragment in dashboard


def test_openai_api_adapter_central_docs_track_step_500_and_next_step_510() -> None:
    changelog = read("CHANGELOG.md")
    roadmap = read("docs/10_ROADMAP.md")
    decisions = read("docs/11_DECISIONS.md")
    readme = read("README.md")

    for content in [changelog, roadmap, decisions, readme]:
        assert "STEP 500" in content
        assert "OpenAI API Adapter" in content
        assert "510) OpenAI API Adapter Live Boundary and Credential Gate" in content


def test_openai_api_adapter_script_and_docs_use_step_500_boundary() -> None:
    for relative_path in NEW_FILES:
        content = read(relative_path)
        if relative_path == "scripts/asf_openai_api_adapter.py":
            assert "LIVE_MODE_NOT_IMPLEMENTED_IN_STEP_500" in content
        if relative_path.endswith(".md"):
            assert "STEP 500" in content


def test_openai_api_adapter_script_avoids_forbidden_patterns() -> None:
    content = read("scripts/asf_openai_api_adapter.py")
    forbidden_patterns = [
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
        "gh release",
        "git merge",
        "git reset --hard",
        "git clean",
        "Set-ExecutionPolicy",
        "setx PATH",
        "urllib",
        "requests",
        "openai import",
        "shell=True",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content
