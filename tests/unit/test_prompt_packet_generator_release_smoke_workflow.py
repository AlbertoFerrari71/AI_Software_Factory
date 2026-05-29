from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE_SCRIPT = ROOT / "scripts" / "smoke_prompt_packet_release.ps1"
SMOKE_DOC = ROOT / "docs" / "31_PROMPT_PACKET_GENERATOR_RELEASE_SMOKE_WORKFLOW.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_release_smoke_workflow_files_exist() -> None:
    assert SMOKE_SCRIPT.exists()
    assert SMOKE_DOC.exists()


def test_smoke_script_uses_wrapper_and_validates_lite_and_strict() -> None:
    content = read(SMOKE_SCRIPT)

    assert "generate_task_packet.ps1" in content
    assert "validate_task_packet.py" in content
    assert "Lite Mode" in content
    assert "Strict Mode" in content
    assert "--strict" in content
    assert "tmp\\smoke_prompt_packet_release.md" in content


def test_smoke_script_avoids_dangerous_or_remote_operations() -> None:
    content = read(SMOKE_SCRIPT).casefold()

    forbidden_fragments = [
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
        "gh release",
        "git merge",
        "git reset --hard",
        "git clean",
        "set-executionpolicy",
        "$env:path",
        "install-package",
        "pip install",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in content


def test_smoke_document_describes_core_concepts() -> None:
    content = read(SMOKE_DOC)

    required_fragments = [
        "Prompt Packet Generator Release Smoke Workflow",
        "smoke workflow",
        "Lite Mode",
        "Strict Mode",
        "Verification Gate",
        "CI",
        "local-first",
        "tmp\\smoke_prompt_packet_release.md",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_190_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 190 - Prompt Packet Generator Release Smoke Workflow" in changelog
    assert "DEC-039 - Prompt Packet Generator Release Smoke Workflow" in decisions
    assert "STEP 200" in roadmap
    assert "Prompt Packet Generator Developer Onboarding" in roadmap
