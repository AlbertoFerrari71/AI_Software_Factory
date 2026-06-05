from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_cli_compatibility_probe.py"


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_fake_codex(tmp_path: Path) -> Path:
    if os.name == "nt":
        fake = tmp_path / "codex.cmd"
        fake.write_text(
            """@echo off
if "%1"=="--version" (
  echo codex 1.2.3
  exit /b 0
)
if "%1"=="--help" (
  echo Usage: codex [COMMAND]
  echo Commands: exec
  exit /b 0
)
if "%1"=="exec" (
  echo Usage: codex exec --sandbox read-only --json --output-last-message -
  echo Reads prompt from stdin when - is supplied.
  exit /b 0
)
exit /b 2
""",
            encoding="utf-8",
        )
        return fake

    fake = tmp_path / "codex"
    fake.write_text(
        """#!/bin/sh
if [ "$1" = "--version" ]; then
  echo "codex 1.2.3"
  exit 0
fi
if [ "$1" = "--help" ]; then
  echo "Usage: codex [COMMAND]"
  echo "Commands: exec"
  exit 0
fi
if [ "$1" = "exec" ]; then
  echo "Usage: codex exec --sandbox read-only --json --output-last-message -"
  echo "Reads prompt from stdin when - is supplied."
  exit 0
fi
exit 2
""",
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return fake


def test_cli_compatibility_probe_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--codex-command" in result.stdout
    assert "--output-json" in result.stdout


def test_cli_compatibility_probe_classifies_missing_codex_as_diagnostic(tmp_path: Path) -> None:
    output = tmp_path / "probe.json"

    result = run_script("--codex-command", "codex-command-that-does-not-exist", "--output-json", output)

    assert result.returncode == 0, result.stdout + result.stderr
    report = read_json(output)
    assert report["classifications"] == ["CODEX_NOT_AVAILABLE"]
    assert report["executable"]["present"] is False
    assert report["calls_model"] is False


def test_cli_compatibility_probe_detects_metadata_support_from_fake_codex(tmp_path: Path) -> None:
    fake = make_fake_codex(tmp_path)
    output = tmp_path / "probe.json"
    markdown = tmp_path / "probe.md"

    result = run_script("--codex-command", fake, "--output-json", output, "--output-markdown", markdown)

    assert result.returncode == 0, result.stdout + result.stderr
    report = read_json(output)
    assert "CODEX_AVAILABLE" in report["classifications"]
    assert "CLI_PROBE_AVAILABLE" in report["classifications"]
    for key in ["exec", "sandbox", "read_only", "json", "output_last_message", "stdin_dash"]:
        assert report["support"][key]["supported"] is True
    assert markdown.exists()
