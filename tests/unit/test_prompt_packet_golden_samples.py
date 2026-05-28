from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALID_SAMPLE = ROOT / "examples" / "task_packets" / "valid" / "step_valid_minimal_task_packet.md"
INVALID_SAMPLES = [
    ROOT / "examples" / "task_packets" / "invalid" / "missing_forbidden_actions.md",
    ROOT / "examples" / "task_packets" / "invalid" / "missing_scope.md",
    ROOT / "examples" / "task_packets" / "invalid" / "missing_final_report.md",
]
VALIDATOR = ROOT / "scripts" / "validate_task_packet.py"


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_prompt_packet_golden_sample_files_exist() -> None:
    assert VALID_SAMPLE.exists()
    for sample in INVALID_SAMPLES:
        assert sample.exists()

    assert (ROOT / "docs" / "27_PROMPT_PACKET_GOLDEN_SAMPLES.md").exists()


def test_validator_passes_on_valid_golden_sample() -> None:
    result = run_validator(VALID_SAMPLE)

    assert result.returncode == 0
    assert "Result: PASS" in result.stdout


def test_validator_fails_on_invalid_golden_samples() -> None:
    for sample in INVALID_SAMPLES:
        result = run_validator(sample)

        assert result.returncode == 1, sample
        assert "Result: FAIL" in result.stdout


def test_golden_samples_document_contains_core_concepts() -> None:
    content = read_text("docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md")
    lower_content = content.lower()

    assert "Prompt Packet Examples and Golden Samples" in content
    assert "valid" in lower_content
    assert "invalid" in lower_content
    assert "strict mode" in lower_content
    assert "STEP 160" in content


def test_step_150_changelog_decision_and_next_step_are_present() -> None:
    changelog = read_text("CHANGELOG.md")
    decisions = read_text("docs/11_DECISIONS.md")
    roadmap = read_text("docs/10_ROADMAP.md")

    assert "STEP 150 - Prompt Packet Examples and Golden Samples" in changelog
    assert "DEC-035 - Prompt Packet golden samples" in decisions
    assert "STEP 160" in roadmap
    assert "Prompt Packet Validation Strict Mode" in roadmap
