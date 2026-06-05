from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_decision_gate.py"


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


def write_cli_probe(path: Path, *, available: bool = True) -> None:
    classifications = ["CODEX_AVAILABLE", "CLI_PROBE_AVAILABLE"] if available else ["CODEX_NOT_AVAILABLE"]
    write_json(
        path,
        {
            "report_type": "asf_codex_cli_compatibility_probe",
            "classifications": classifications,
            "support": {
                "exec": {"supported": available},
                "sandbox": {"supported": available},
                "read_only": {"supported": available},
            },
        },
    )


def write_diagnostics(path: Path, classifications: list[str]) -> None:
    write_json(
        path,
        {
            "report_type": "asf_codex_readonly_diagnostics",
            "classifications": classifications,
            "reports": [{"state": "OK", "classifications": classifications}],
        },
    )


def write_comparison(path: Path, classifications: list[str]) -> None:
    write_json(
        path,
        {
            "report_type": "asf_codex_readonly_trial_comparison",
            "classifications": classifications,
            "repeated_readonly_trials_clean": "READONLY_EXECUTED_CLEAN" in classifications,
        },
    )


def decision_from(result_path: Path) -> str:
    return str(read_json(result_path)["decision"])


def base_args(diagnostics: Path, cli_probe: Path, comparison: Path | None, output: Path) -> list[str | Path]:
    args: list[str | Path] = ["--diagnostics", diagnostics, "--cli-probe", cli_probe, "--output-json", output]
    if comparison is not None:
        args.extend(["--trial-comparison", comparison])
    return args


def test_decision_gate_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--diagnostics" in result.stdout
    assert "--cli-probe" in result.stdout


def test_decision_gate_go_only_for_complete_clean_evidence(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    cli_probe = tmp_path / "cli_probe.json"
    comparison = tmp_path / "comparison.json"
    output = tmp_path / "decision.json"
    write_diagnostics(
        diagnostics,
        ["CODEX_AVAILABLE", "EXECUTION_COMPLETED", "TARGET_CLEAN_AFTER_READONLY"],
    )
    write_cli_probe(cli_probe, available=True)
    write_comparison(comparison, ["READONLY_EXECUTED_CLEAN"])

    result = run_script(*base_args(diagnostics, cli_probe, comparison, output))

    assert result.returncode == 0, result.stdout + result.stderr
    assert decision_from(output) == "GO_TO_WORKSPACE_WRITE_DESIGN"


def test_decision_gate_no_go_for_dirty_target_evidence(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    cli_probe = tmp_path / "cli_probe.json"
    comparison = tmp_path / "comparison.json"
    output = tmp_path / "decision.json"
    write_diagnostics(diagnostics, ["EXECUTION_COMPLETED", "TARGET_DIRTY_AFTER_READONLY"])
    write_cli_probe(cli_probe, available=True)
    write_comparison(comparison, ["READONLY_EXECUTED_CLEAN"])

    result = run_script(*base_args(diagnostics, cli_probe, comparison, output))

    assert result.returncode == 0, result.stdout + result.stderr
    assert decision_from(output) == "NO_GO"


def test_decision_gate_hold_for_missing_or_malformed_core_report(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    cli_probe = tmp_path / "cli_probe.json"
    output = tmp_path / "decision.json"
    write_diagnostics(diagnostics, ["REPORT_MISSING"])
    write_cli_probe(cli_probe, available=True)

    result = run_script(*base_args(diagnostics, cli_probe, None, output))

    assert result.returncode == 0, result.stdout + result.stderr
    assert decision_from(output) == "HOLD"


def test_decision_gate_warning_for_stderr_or_incomplete_output_with_clean_target(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    cli_probe = tmp_path / "cli_probe.json"
    comparison = tmp_path / "comparison.json"
    output = tmp_path / "decision.json"
    write_diagnostics(
        diagnostics,
        ["EXECUTION_COMPLETED", "TARGET_CLEAN_AFTER_READONLY", "STDERR_NONEMPTY", "OUTPUT_INCOMPLETE"],
    )
    write_cli_probe(cli_probe, available=True)
    write_comparison(comparison, ["READONLY_EXECUTED_CLEAN"])

    result = run_script(*base_args(diagnostics, cli_probe, comparison, output))

    assert result.returncode == 0, result.stdout + result.stderr
    assert decision_from(output) == "WARNING_REVIEW_REQUIRED"


def test_decision_gate_more_trials_when_codex_is_unavailable(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    cli_probe = tmp_path / "cli_probe.json"
    comparison = tmp_path / "comparison.json"
    output = tmp_path / "decision.json"
    write_diagnostics(diagnostics, ["CODEX_NOT_AVAILABLE", "TARGET_CLEAN_AFTER_READONLY"])
    write_cli_probe(cli_probe, available=False)
    write_comparison(comparison, [])

    result = run_script(*base_args(diagnostics, cli_probe, comparison, output))

    assert result.returncode == 0, result.stdout + result.stderr
    assert decision_from(output) == "GO_TO_MORE_READONLY_TRIALS"

