from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_gate_decision_report.py"
DRY_RUN_RUNNER = ROOT / "scripts" / "asf_dry_run_loop_runner.py"
RISK_CLASSIFIER = ROOT / "scripts" / "asf_risk_classifier.py"
EXAMPLES = ROOT / "examples" / "gate_decision"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_gate_decision_report", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_l1_local_produces_local_only_decision() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l1_local_docs.json"))

    assert packet["risk_level"] == "L1"
    assert packet["decision"] == "APPROVE_LOCAL_ONLY"
    assert packet["allowed"] is True
    assert packet["fail_closed"] is False


def test_l2_missing_checks_needs_human() -> None:
    module = load_module()
    payload = read_json(EXAMPLES / "sample_l2_code_change_checked.json")
    payload["checks_reported"] = []

    packet = module.build_approval_packet(payload)

    assert packet["risk_level"] == "L2"
    assert packet["decision"] == "NEEDS_HUMAN"
    assert packet["gate_status"] == "MISSING"


def test_l2_passed_checks_produces_local_only_decision() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l2_code_change_checked.json"))

    assert packet["risk_level"] == "L2"
    assert packet["decision"] == "APPROVE_LOCAL_ONLY"
    assert packet["gate_status"] == "SATISFIED"


def test_l3_without_publish_approval_needs_human() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l3_publish_needs_approval.json"))

    assert packet["risk_level"] == "L3"
    assert packet["decision"] == "NEEDS_HUMAN"
    assert any("explicit_publish_approval" in item for item in packet["blockers"])


def test_l3_with_publish_approval_produces_publish_report_decision() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l3_publish_approved.json"))

    assert packet["risk_level"] == "L3"
    assert packet["decision"] == "APPROVE_PUBLISH"
    assert packet["allowed"] is True
    assert packet["machine_readable"]["no_operational_actions_executed"] is True


def test_l4_is_blocked_or_fail_closed() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l4_blocked.json"))

    assert packet["risk_level"] == "L4"
    assert packet["decision"] in {"BLOCKED", "FAIL_CLOSED"}
    assert packet["allowed"] is False


def test_invalid_or_ambiguous_input_fails_closed() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_invalid_fail_closed.json"))

    assert packet["decision"] == "FAIL_CLOSED"
    assert packet["fail_closed"] is True
    assert packet["allowed"] is False


def test_json_output_is_valid_and_contains_required_fields() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l2_code_change_checked.json"))
    payload = json.loads(module.render_json(packet))

    for field in [
        "step",
        "title",
        "decision",
        "risk_level",
        "required_gate",
        "gate_status",
        "allowed",
        "fail_closed",
        "summary",
        "files_in_scope",
        "checks_required",
        "checks_reported",
        "blockers",
        "warnings",
        "recommended_next_action",
        "human_approval_text",
        "machine_readable",
    ]:
        assert field in payload


def test_markdown_contains_risk_gate_blockers_and_next_action() -> None:
    module = load_module()
    packet = module.build_approval_packet(read_json(EXAMPLES / "sample_l3_publish_needs_approval.json"))
    markdown = module.render_markdown(packet)

    for fragment in ["## Risk", "## Gate", "## Blockers", "## Next action", "L3"]:
        assert fragment in markdown


def test_cli_json_and_out_dir_work(tmp_path: Path) -> None:
    result = run_cli("--input-file", EXAMPLES / "sample_l3_publish_approved.json", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["decision"] == "APPROVE_PUBLISH"

    out_dir = tmp_path / "packet"
    result = run_cli("--input-file", EXAMPLES / "sample_l1_local_docs.json", "--out-dir", out_dir)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (out_dir / "approval_packet.json").exists()
    assert (out_dir / "approval_packet.md").exists()
    assert (out_dir / "approval_packet.txt").exists()


def test_dry_run_runner_regression_help_still_works() -> None:
    result = subprocess.run(
        [sys.executable, str(DRY_RUN_RUNNER), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "--request-json" in result.stdout


def test_risk_classifier_regression_l3_sample_still_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RISK_CLASSIFIER),
            "--input-file",
            str(ROOT / "examples" / "risk_classifier" / "sample_l3_publish.json"),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["risk_level"] == "L3"
    assert payload["required_gate"] == "explicit_publish_approval"
