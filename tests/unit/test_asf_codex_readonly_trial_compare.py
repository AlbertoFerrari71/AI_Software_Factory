from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_trial_compare.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_fake_report(path: Path, *, trial: str, classification: str, safety: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# ASF Codex Read-Only Repeatable Trial Report

## Summary

- trial-name: `{trial}`
- step: `450`
- mode: `run-readonly-if-safe`
- approval status: `GO`
- invocation status: `EXECUTE_READONLY_COMPLETED`
- capture status: `PASS`
- safety gate status: `{safety}`
- Codex availability: `AVAILABLE`
- exit code: `0`
- classification: `{classification}`

## Notes

- stderr non vuoto and output incompleto require review.
""",
        encoding="utf-8",
    )


def test_trial_compare_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--reports" in result.stdout
    assert "--output-dir" in result.stdout


def test_trial_compare_generates_report_with_recommendation(tmp_path: Path) -> None:
    report_a = tmp_path / "trial_a.md"
    report_b = tmp_path / "trial_b.md"
    output_dir = tmp_path / "comparison"
    write_fake_report(
        report_a,
        trial="trial_a",
        classification="READONLY_EXECUTED_CLEAN",
        safety="GO_TO_WORKSPACE_WRITE_DESIGN",
    )
    write_fake_report(
        report_b,
        trial="trial_b",
        classification="READONLY_EXECUTED_WARNING",
        safety="WARNING_REVIEW_REQUIRED",
    )

    result = run_script("--reports", report_a, report_b, "--output-dir", output_dir)

    assert result.returncode == 0, result.stdout + result.stderr
    comparison = read(output_dir / "trial_comparison_report.md")
    assert "trial_a" in comparison
    assert "trial_b" in comparison
    assert "READONLY_EXECUTED_CLEAN" in comparison
    assert "READONLY_EXECUTED_WARNING" in comparison
    assert "Raccomandazione" in comparison
    assert "stderr/output incomplete" in comparison


def test_trial_compare_fails_for_missing_report(tmp_path: Path) -> None:
    result = run_script("--reports", tmp_path / "missing.md", "--output-dir", tmp_path / "comparison")

    assert result.returncode != 0
    assert "does not exist" in result.stderr

