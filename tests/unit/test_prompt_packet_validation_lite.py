from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_prompt_packet_validation_lite_files_exist() -> None:
    assert (ROOT / "scripts" / "validate_task_packet.py").exists()
    assert (ROOT / "docs" / "26_PROMPT_PACKET_VALIDATION_LITE.md").exists()


def test_prompt_packet_validation_lite_document_contains_core_concepts() -> None:
    content = read_text("docs/26_PROMPT_PACKET_VALIDATION_LITE.md")
    lower_content = content.lower()

    required_fragments = [
        "Prompt Packet Validation Lite",
        "Verification Gate",
        "Documentation Sync",
        "Soft Protection",
        "STEP 150",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "exit codes" in lower_content


def test_prompt_packet_validation_lite_script_contains_expected_checks() -> None:
    content = read_text("scripts/validate_task_packet.py")

    required_fragments = [
        "main",
        "exit code 0",
        "exit code 1",
        "exit code 2",
        "Forbidden actions",
        "Allowed scope",
        "Forbidden scope",
        "Verification Gate",
        "Documentation Sync",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_validator_passes_on_central_task_packet_template() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_task_packet.py"),
            str(ROOT / "templates" / "codex_tasks" / "codex_task_packet_template.md"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Result: PASS" in result.stdout


def test_validator_fails_on_incomplete_packet(tmp_path: Path) -> None:
    incomplete = tmp_path / "incomplete_task.md"
    incomplete.write_text("# Incomplete task\n\n## Obiettivo\n\nFare qualcosa.\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_task_packet.py"), str(incomplete)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Result: FAIL" in result.stdout


def test_step_140_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 140 - Prompt Packet Validation Lite" in changelog
    assert "DEC-034 - Prompt Packet Validation Lite" in decisions
    assert "STEP 150" in roadmap
    assert "Prompt Packet Examples and Golden Samples" in roadmap
