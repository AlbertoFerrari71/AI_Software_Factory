from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "generate_task_packet.py"
VALIDATOR = ROOT / "scripts" / "validate_task_packet.py"


def run_generator(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_validator(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def base_args(output: Path) -> list[str | Path]:
    return [
        "--step",
        "170",
        "--title",
        "Prompt Packet Generator CLI Hardening",
        "--branch",
        "step-170-prompt-packet-generator-cli-hardening",
        "--objective",
        "Harden the prompt packet generator CLI.",
        "--output",
        output,
    ]


def test_generator_help_is_available() -> None:
    assert GENERATOR.exists()

    result = run_generator("--help")

    assert result.returncode == 0
    assert "--step" in result.stdout
    assert "--title" in result.stdout
    assert "--branch" in result.stdout


def test_generator_creates_valid_task_packet_file(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    result = run_generator(*base_args(output))

    assert result.returncode == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")

    required_fragments = [
        "Project context",
        "BRANCH DA USARE",
        "Objective",
        "ALLOWED SCOPE",
        "FORBIDDEN SCOPE",
        "FORBIDDEN ACTIONS",
        "Verification Gate",
        "Documentation Sync",
        "Soft Protection awareness",
        "Output finale richiesto",
        "A) STEP ESEGUITO",
        "Tempo impiegato",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_generator_fails_when_output_exists_without_force(tmp_path: Path) -> None:
    output = tmp_path / "existing.md"
    output.write_text("existing", encoding="utf-8")

    result = run_generator(*base_args(output))

    assert result.returncode != 0
    assert "already exists" in result.stderr


def test_generator_overwrites_when_force_is_used(tmp_path: Path) -> None:
    output = tmp_path / "existing.md"
    output.write_text("existing", encoding="utf-8")

    result = run_generator(*base_args(output), "--force")

    assert result.returncode == 0
    content = output.read_text(encoding="utf-8")
    assert "existing" not in content
    assert "STEP 170 - Prompt Packet Generator CLI Hardening" in content


def test_generator_fails_on_non_numeric_step(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    args = base_args(output)
    args[1] = "abc"

    result = run_generator(*args)

    assert result.returncode != 0
    assert "--step must be numeric" in result.stderr


def test_generator_fails_on_step_not_multiple_of_10(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    args = base_args(output)
    args[1] = "171"

    result = run_generator(*args)

    assert result.returncode != 0
    assert "--step must be a multiple of 10" in result.stderr


def test_generator_fails_on_branch_with_spaces(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    args = base_args(output)
    args[5] = "branch with spaces"

    result = run_generator(*args)

    assert result.returncode != 0
    assert "--branch must not contain spaces" in result.stderr


def test_generator_strict_ready_note_is_optional_and_explicit(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    result = run_generator(*base_args(output), "--strict-ready")

    assert result.returncode == 0
    content = output.read_text(encoding="utf-8")
    assert "validate_task_packet.py --strict" in content


def test_generated_task_packet_passes_lite_validation(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    generate_result = run_generator(*base_args(output))
    assert generate_result.returncode == 0

    validate_result = run_validator(output)

    assert validate_result.returncode == 0
    assert "Mode: Lite" in validate_result.stdout
    assert "Result: PASS" in validate_result.stdout


def test_generated_task_packet_is_strict_compatible(tmp_path: Path) -> None:
    output = tmp_path / "generated.md"
    generate_result = run_generator(*base_args(output), "--strict-ready")
    assert generate_result.returncode == 0

    validate_result = run_validator("--strict", output)

    assert validate_result.returncode == 0
    assert "Mode: Strict" in validate_result.stdout
    assert "Result: PASS" in validate_result.stdout


def test_generator_cli_hardening_document_contains_core_concepts() -> None:
    path = ROOT / "docs" / "29_PROMPT_PACKET_GENERATOR_CLI_HARDENING.md"
    assert path.exists()

    content = path.read_text(encoding="utf-8")
    required_fragments = [
        "Prompt Packet Generator CLI Hardening",
        "--step",
        "--title",
        "--branch",
        "--output",
        "--strict-ready",
        "Lite",
        "Strict",
        "does not call GitHub API",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_170_changelog_decision_and_next_step_are_present() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    decisions = (ROOT / "docs" / "11_DECISIONS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "10_ROADMAP.md").read_text(encoding="utf-8")

    assert "STEP 170 - Prompt Packet Generator CLI Hardening" in changelog
    assert "DEC-037 - Prompt Packet Generator CLI Hardening" in decisions
    assert "STEP 180" in roadmap
    assert "Prompt Packet Generator Packaging" in roadmap
