from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_repeatable_trial.py"


FORBIDDEN_PATTERNS = [
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
    "workspace-write",
    "danger-full-access",
    "shell=True",
]


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


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)


def require_git() -> None:
    if shutil.which("git") is None:
        pytest.skip("git executable not available")


def test_repeatable_trial_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "prepare-only" in result.stdout
    assert "run-readonly-if-safe" in result.stdout


def test_prepare_only_creates_synthetic_clean_target_and_report(tmp_path: Path) -> None:
    require_git()
    output_dir = tmp_path / "trials"

    result = run_script(
        "--mode",
        "prepare-only",
        "--trial-name",
        "step_450_prepare_test",
        "--step",
        "450",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trial_dir = output_dir / "step_450_prepare_test"
    for dirname in ["target_repo", "inputs", "approval", "invocation", "capture", "safety", "reports"]:
        assert (trial_dir / dirname).is_dir(), dirname

    target_repo = trial_dir / "target_repo"
    assert (target_repo / ".git").exists()
    assert (target_repo / "README.md").is_file()
    assert (target_repo / "docs" / "NOTES.md").is_file()
    assert (target_repo / "src" / "demo.txt").is_file()
    assert (trial_dir / "inputs" / "handoff.md").is_file()

    report = read(trial_dir / "reports" / "repeatable_trial_report.md")
    assert "classification: `PREPARED_ONLY`" in report
    assert "Codex was not executed" in report
    assert run_git(target_repo, "status", "--short").stdout.strip() == ""


def test_run_readonly_without_confirmation_fails(tmp_path: Path) -> None:
    result = run_script(
        "--mode",
        "run-readonly-if-safe",
        "--trial-name",
        "step_450_missing_confirm",
        "--step",
        "450",
        "--output-dir",
        tmp_path / "trials",
    )

    assert result.returncode != 0
    assert "confirm-readonly-execution" in result.stderr


def test_run_readonly_with_missing_codex_is_controlled_and_clean(tmp_path: Path) -> None:
    require_git()
    output_dir = tmp_path / "trials"

    result = run_script(
        "--mode",
        "run-readonly-if-safe",
        "--trial-name",
        "step_450_missing_codex",
        "--step",
        "450",
        "--output-dir",
        output_dir,
        "--codex-command",
        "codex-command-that-does-not-exist",
        "--confirm-readonly-execution",
        "YES_I_APPROVE_READONLY_CODEX_EXECUTION",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trial_dir = output_dir / "step_450_missing_codex"
    target_repo = trial_dir / "target_repo"
    report = read(trial_dir / "reports" / "repeatable_trial_report.md")

    assert "classification: `CODEX_NOT_AVAILABLE`" in report
    assert "Codex availability: `CODEX_NOT_AVAILABLE`" in report
    assert "capture status: `WARNING`" in report
    assert "safety gate status: `WARNING_REVIEW_REQUIRED`" in report
    assert run_git(target_repo, "status", "--short").stdout.strip() == ""


def test_repeatable_trial_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content

