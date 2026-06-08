from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_publish_step.ps1"
CONFIG = ROOT / "examples" / "publish_step" / "0590_publish_config.example.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def run_pwsh(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_bridge_retry_helpers_are_bounded_and_explicit() -> None:
    content = read(SCRIPT)

    for fragment in [
        "function Set-ContentWithRetry",
        "function Copy-ItemWithRetry",
        "function Move-ItemWithRetry",
        "function Write-BridgeFileWithRetry",
        "function Update-LastFileWithRetry",
        "function New-FallbackBridgePath",
        "function Validate-BridgeLastOutputs",
        "[int]$MaxAttempts = 5",
        "for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++)",
        "Start-Sleep -Milliseconds $DelayMilliseconds",
        "fallback_",
    ]:
        assert fragment in content


def test_bridge_status_policy_keeps_gates_blocking_and_accessories_non_blocking() -> None:
    content = read(SCRIPT)

    for fragment in [
        "Gate failed = BLOCCATO",
        "Git, PR, tests, verify gate or diff-check failed = BLOCCATO",
        "COMPLETATO CON WARNING NON BLOCCANTE",
        "Compact Markdown is mandatory",
        "Mandatory compact Markdown Bridge output failed",
        "DOCX is best-effort",
        "DOCX accessory output failed without blocking",
    ]:
        assert fragment in content


def test_last_clipboard_contract_uses_content_not_path_parameter() -> None:
    content = read(SCRIPT)

    assert "Get-Content -Path $File -Raw | Set-Clipboard" in content
    assert "LAST-Output_Compatto.md" in content
    assert "Update-BridgeLastOutputs" in content
    assert "Validate-BridgeLastOutputs" in content
    assert "Set-Clipboard -Path" not in content


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_bridge_compact_primary_blocked_uses_fallback_without_failing_after_passed_gate(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    bridge_root.mkdir()
    primary_compact = bridge_root / "0000-Output_Compatto_SelfTest.md"
    primary_compact.mkdir()

    result = run_pwsh("-SelfTest", "-BridgeRoot", bridge_root)

    assert result.returncode == 0, result.stdout + result.stderr
    fallbacks = sorted(bridge_root.glob("0000-Output_Compatto_SelfTest_fallback_*.md"))
    assert fallbacks
    compact = read(bridge_root / "LAST-Output_Compatto.md")
    assert "COMPLETATO CON WARNING NON BLOCCANTE" in compact
    assert "primary blocked after retry" in compact
    assert "fallback" in compact
    assert "LAST validation PASS" in compact


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_failed_gate_remains_blocking(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_pwsh("-Config", CONFIG, "-Phase", "B", "-BridgeRoot", bridge_root)

    assert result.returncode == 1
    combined = result.stdout + result.stderr
    assert "Phase B requires -ApprovePublish" in combined
    compact = read(bridge_root / "LAST-Output_Compatto.md")
    assert "BLOCCATO" in compact
    assert "Machine status: `FAIL`" in compact
