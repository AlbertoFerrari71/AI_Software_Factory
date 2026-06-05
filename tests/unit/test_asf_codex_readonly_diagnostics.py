from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_diagnostics.py"


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_readonly_diagnostics_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--reports" in result.stdout
    assert "--output-json" in result.stdout


def test_readonly_diagnostics_classifies_execution_warning_evidence(tmp_path: Path) -> None:
    source = tmp_path / "capture.json"
    output = tmp_path / "diagnostics.json"
    markdown = tmp_path / "diagnostics.md"
    write_json(
        source,
        {
            "report_type": "synthetic_result_capture",
            "classification": "WARNING",
            "codex_availability": "AVAILABLE",
            "exit_code": 1,
            "stdout": "",
            "stderr": "OpenAI Codex metadata on stderr",
            "output_incomplete": True,
            "target_working_tree_after": "CLEAN",
        },
    )

    result = run_script("--reports", source, "--output-json", output, "--output-markdown", markdown)

    assert result.returncode == 0, result.stdout + result.stderr
    diagnostics = read_json(output)
    classifications = diagnostics["classifications"]
    for expected in [
        "CODEX_AVAILABLE",
        "EXECUTION_FAILED",
        "STDERR_NONEMPTY",
        "STDOUT_EMPTY",
        "OUTPUT_INCOMPLETE",
        "EXIT_CODE_NONZERO",
        "TARGET_CLEAN_AFTER_READONLY",
    ]:
        assert expected in classifications
    assert markdown.exists()


def test_readonly_diagnostics_reports_missing_and_malformed_inputs(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    missing = tmp_path / "missing.json"
    output = tmp_path / "diagnostics.json"
    malformed.write_text("{not-json", encoding="utf-8")

    result = run_script("--reports", malformed, missing, "--output-json", output)

    assert result.returncode == 0, result.stdout + result.stderr
    diagnostics = read_json(output)
    assert "REPORT_MALFORMED" in diagnostics["classifications"]
    assert "REPORT_MISSING" in diagnostics["classifications"]
    states = {entry["state"] for entry in diagnostics["reports"]}
    assert states == {"MALFORMED", "MISSING"}


def test_readonly_diagnostics_classifies_dirty_target_as_serious_evidence(tmp_path: Path) -> None:
    source = tmp_path / "repeatable_trial.json"
    output = tmp_path / "diagnostics.json"
    write_json(
        source,
        {
            "classification": "READONLY_EXECUTED_CLEAN",
            "exit_code": 0,
            "target_working_tree_after": "DIRTY",
        },
    )

    result = run_script("--reports", source, "--output-json", output)

    assert result.returncode == 0, result.stdout + result.stderr
    diagnostics = read_json(output)
    assert "EXECUTION_COMPLETED" in diagnostics["classifications"]
    assert "TARGET_DIRTY_AFTER_READONLY" in diagnostics["classifications"]

