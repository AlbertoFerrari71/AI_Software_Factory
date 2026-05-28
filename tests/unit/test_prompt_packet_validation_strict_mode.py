from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_task_packet.py"
CENTRAL_TEMPLATE = ROOT / "templates" / "codex_tasks" / "codex_task_packet_template.md"
VALID_MINIMAL_SAMPLE = ROOT / "examples" / "task_packets" / "valid" / "step_valid_minimal_task_packet.md"
VALID_STRICT_SAMPLE = ROOT / "examples" / "task_packets" / "valid" / "step_valid_strict_task_packet.md"
STRICT_INVALID_SAMPLE = ROOT / "examples" / "task_packets" / "invalid" / "strict_missing_bypass_guard.md"
LEGACY_INVALID_SAMPLES = [
    ROOT / "examples" / "task_packets" / "invalid" / "missing_forbidden_actions.md",
    ROOT / "examples" / "task_packets" / "invalid" / "missing_scope.md",
    ROOT / "examples" / "task_packets" / "invalid" / "missing_final_report.md",
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def run_validator(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_strict_mode_files_exist() -> None:
    assert (ROOT / "docs" / "28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md").exists()
    assert VALID_STRICT_SAMPLE.exists()
    assert STRICT_INVALID_SAMPLE.exists()


def test_lite_mode_still_passes_existing_valid_inputs() -> None:
    for path in [CENTRAL_TEMPLATE, VALID_MINIMAL_SAMPLE]:
        result = run_validator(path)

        assert result.returncode == 0
        assert "Mode: Lite" in result.stdout
        assert "Result: PASS" in result.stdout


def test_strict_mode_passes_on_strict_valid_sample() -> None:
    result = run_validator("--strict", VALID_STRICT_SAMPLE)

    assert result.returncode == 0
    assert "Mode: Strict" in result.stdout
    assert "Result: PASS" in result.stdout


def test_strict_mode_fails_on_missing_bypass_guard() -> None:
    result = run_validator("--strict", STRICT_INVALID_SAMPLE)

    assert result.returncode == 1
    assert "Mode: Strict" in result.stdout
    assert "Strict no ASF_ALLOW_MAIN_BYPASS" in result.stdout
    assert "Result: FAIL" in result.stdout


def test_existing_invalid_samples_still_fail_lite_validation() -> None:
    for path in LEGACY_INVALID_SAMPLES:
        result = run_validator(path)

        assert result.returncode == 1, path
        assert "Result: FAIL" in result.stdout


def test_strict_mode_document_contains_core_concepts() -> None:
    content = read_text("docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md")
    lower_content = content.lower()

    required_fragments = [
        "Prompt Packet Validation Strict Mode",
        "Lite",
        "Strict",
        "Verification Gate",
        "Documentation Sync",
        "Soft Protection",
        "STEP 170",
    ]
    for fragment in required_fragments:
        assert fragment in content

    assert "exit codes" in lower_content


def test_strict_mode_script_contains_cli_markers() -> None:
    content = read_text("scripts/validate_task_packet.py")

    assert "--strict" in content
    assert "Mode: Strict" in content
    assert "Mode: Lite" in content


def test_step_160_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 160 - Prompt Packet Validation Strict Mode" in changelog
    assert "DEC-036 - Prompt Packet Validation Strict Mode" in decisions
    assert "STEP 170" in roadmap
    assert "Prompt Packet Generator CLI Hardening" in roadmap
