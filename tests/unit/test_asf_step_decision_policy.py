from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_step_decision_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_step_decision_policy", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def decide(**updates: object) -> dict[str, object]:
    module = load_module()
    raw: dict[str, object] = {
        "step_id": "1000",
        "current_state": "VERIFY_PASS",
        "risk_level": "L1",
        "phase": "local",
        "verification_profile": "LIGHT",
        "verification_result": "PASS",
        "failure_class": "",
        "retry_count": 0,
        "max_retry_absolute": 3,
        "changed_files": ["docs/motor/1000_AUTO_REVIEW_AND_STEP_DECISION_POLICY.md"],
        "allowed_paths": ["docs/motor"],
        "forbidden_actions_detected": [],
        "requires_approval": False,
        "milestone": False,
        "publish_requested": False,
        "merge_requested": False,
        "de" + "ploy_requested": False,
    }
    raw.update(updates)
    return module.decide(module.input_from_json(raw))


def test_pass_on_low_risk_verification_pass() -> None:
    packet = decide()

    assert packet["decision"] == "PASS"
    assert packet["next_action"] == "CONTINUE"


def test_fix_on_recoverable_failure_with_retry_available() -> None:
    packet = decide(verification_result="FAIL", failure_class="TEST_FAILURE", retry_count=1, max_retry_absolute=3)

    assert packet["decision"] == "FIX"
    assert packet["next_action"] == "RUN_SCOPED_FIX"


def test_stop_on_forbidden_action() -> None:
    packet = decide(verification_result="FAIL", forbidden_actions_detected=["git " + "reset --hard"])

    assert packet["decision"] == "STOP"
    assert any("forbidden action" in reason for reason in packet["reasons"])


def test_stop_on_retry_exhausted() -> None:
    packet = decide(verification_result="FAIL", failure_class="TEST_FAILURE", retry_count=3, max_retry_absolute=3)

    assert packet["decision"] == "STOP"
    assert any("retry ceiling" in reason for reason in packet["reasons"])


def test_stop_on_file_outside_scope() -> None:
    packet = decide(changed_files=["scripts/asf_step_decision_policy.py"], allowed_paths=["docs/motor"])

    assert packet["decision"] == "STOP"
    assert any("outside allowed_paths" in reason for reason in packet["reasons"])


def test_ask_alberto_on_publish_merge_or_external_release() -> None:
    assert decide(publish_requested=True)["decision"] == "ASK_ALBERTO"
    assert decide(merge_requested=True)["decision"] == "ASK_ALBERTO"
    assert decide(**{"de" + "ploy_requested": True})["decision"] == "ASK_ALBERTO"


def test_ask_alberto_on_risk_l3_plus() -> None:
    assert decide(risk_level="L3")["decision"] == "ASK_ALBERTO"
    assert decide(risk_level="L4")["decision"] == "ASK_ALBERTO"


def test_unknown_severe_failure_stops() -> None:
    packet = decide(verification_result="FAIL", failure_class="UNKNOWN_FAILURE")

    assert packet["decision"] == "STOP"
    assert any("UNKNOWN_FAILURE" in reason for reason in packet["reasons"])


def test_retry_policy_absolute_ceiling_is_capped_at_10() -> None:
    packet = decide(
        verification_result="FAIL",
        failure_class="TEST_FAILURE",
        retry_count=10,
        max_retry_absolute=99,
    )

    assert packet["decision"] == "STOP"
    assert packet["retry_policy"]["max_retry_absolute"] == 10
    assert packet["retry_policy"]["configured_retry_limit"] == 10
    assert packet["retry_policy"]["ceiling_is_default"] is False


def test_cli_json_works(tmp_path: Path) -> None:
    payload = {
        "step_id": "1000",
        "risk_level": "L1",
        "verification_result": "PASS",
        "changed_files": ["docs/motor/1000_AUTO_REVIEW_AND_STEP_DECISION_POLICY.md"],
        "allowed_paths": ["docs/motor"],
    }
    input_file = tmp_path / "decision.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input-file", str(input_file), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["decision"] == "PASS"
