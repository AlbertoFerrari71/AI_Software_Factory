from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON_GENERATOR = ROOT / "scripts" / "generate_task_packet.py"
POWERSHELL_WRAPPER = ROOT / "scripts" / "generate_task_packet.ps1"
PACKAGING_DOC = ROOT / "docs" / "30_PROMPT_PACKET_GENERATOR_PACKAGING.md"
GENERATED_SAMPLE = ROOT / "examples" / "task_packets" / "generated" / "step_180_generated_packaging_sample.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_packaging_files_exist() -> None:
    assert PYTHON_GENERATOR.exists()
    assert POWERSHELL_WRAPPER.exists()
    assert PACKAGING_DOC.exists()
    assert GENERATED_SAMPLE.exists()


def test_powershell_wrapper_is_thin_and_delegates_to_python_cli() -> None:
    content = read(POWERSHELL_WRAPPER)

    assert "generate_task_packet.py" in content
    assert "& python @CliArgs" in content
    assert "exit $LASTEXITCODE" in content
    assert "argparse" not in content
    assert "def build_task_packet" not in content
    assert "validate_inputs" not in content
    assert len(content.splitlines()) < 90


def test_generated_packaging_sample_contains_minimum_sections() -> None:
    content = read(GENERATED_SAMPLE)

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


def test_generated_packaging_sample_is_strict_ready() -> None:
    content = read(GENERATED_SAMPLE)

    assert "Prompt Packet Generator Packaging" in content
    assert "validate_task_packet.py --strict" in content
    assert "step-180-prompt-packet-generator-packaging" in content


def test_packaging_document_describes_cli_wrapper_and_validation_modes() -> None:
    content = read(PACKAGING_DOC)

    required_fragments = [
        "Prompt Packet Generator Packaging",
        "scripts/generate_task_packet.py",
        "scripts/generate_task_packet.ps1",
        "Lite",
        "Strict",
        "PyPI",
        "examples/task_packets/generated/",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_180_changelog_decision_and_next_step_are_present() -> None:
    changelog = read(ROOT / "CHANGELOG.md")
    decisions = read(ROOT / "docs" / "11_DECISIONS.md")
    roadmap = read(ROOT / "docs" / "10_ROADMAP.md")

    assert "STEP 180 - Prompt Packet Generator Packaging" in changelog
    assert "DEC-038 - Prompt Packet Generator Packaging" in decisions
    assert "STEP 190" in roadmap
    assert "Prompt Packet Generator Release Smoke Workflow" in roadmap
