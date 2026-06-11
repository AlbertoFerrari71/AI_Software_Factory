from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "motor" / "0950_BRIDGE_STATE_AND_SEMAPHORE_PROTOCOL.md"
STATE_TEMPLATE = ROOT / "docs" / "templates" / "0950_SUPERVISED_LOOP_STATE_JSON_TEMPLATE.json"
EVENT_LOG_TEMPLATE = ROOT / "docs" / "templates" / "0950_SUPERVISED_LOOP_EVENT_LOG_TEMPLATE.jsonl"

REQUIRED_STATES = [
    "IDLE",
    "PLAN_REQUESTED",
    "GPT_PLANNING",
    "GPT_PLAN_READY",
    "POWERSHELL_READY",
    "POWERSHELL_RUNNING",
    "POWERSHELL_DONE",
    "POWERSHELL_FAILED",
    "POWERSHELL_HUNG",
    "CODEX_READY",
    "CODEX_RUNNING",
    "CODEX_DONE",
    "CODEX_FAILED",
    "REVIEW_REQUESTED",
    "GPT_REVIEWING",
    "REVIEW_PASS",
    "REVIEW_FIX_REQUIRED",
    "VERIFY_RUNNING",
    "VERIFY_PASS",
    "VERIFY_FAIL",
    "RETRY_READY",
    "RETRY_RUNNING",
    "NEEDS_ALBERTO_APPROVAL",
    "STOPPED",
    "COMPLETED",
]

REQUIRED_FLAGS = [
    "READY_FOR_GPT.flag",
    "GPT_PROMPT_DONE.flag",
    "POWERSHELL_RUNNING.flag",
    "POWERSHELL_DONE.flag",
    "POWERSHELL_FAILED.flag",
    "POWERSHELL_HUNG.flag",
    "CODEX_RUNNING.flag",
    "CODEX_DONE.flag",
    "CODEX_FAILED.flag",
    "VERIFY_RUNNING.flag",
    "VERIFY_DONE.flag",
    "NEEDS_ALBERTO_APPROVAL.flag",
    "STOPPED.flag",
    "COMPLETED.flag",
]


def test_protocol_doc_contains_required_states_flags_and_rules() -> None:
    content = DOC.read_text(encoding="utf-8")

    for fragment in REQUIRED_STATES + REQUIRED_FLAGS:
        assert fragment in content
    for fragment in [
        "state.json",
        "append-only",
        "stop_reason",
        "approval_reason",
        "nessun cambio stato silenzioso",
        "GPT-discretionary bounded retry policy",
        "max retry assoluto: 10",
    ]:
        assert fragment in content


def test_state_json_template_is_valid_and_complete() -> None:
    payload = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "0950.1"
    assert payload["state"] == "IDLE"
    assert payload["retry_policy"]["max_retry_absolute"] == 10
    assert payload["retry_policy"]["ceiling_is_default"] is False
    assert set(REQUIRED_STATES).issubset(set(payload["allowed_states"]))
    assert set(REQUIRED_FLAGS).issubset(set(payload["flags"]))
    assert "stop_reason" in payload
    assert "approval_reason" in payload


def test_event_log_template_is_jsonl_append_only_shape() -> None:
    lines = [line for line in EVENT_LOG_TEMPLATE.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(lines) >= 3
    for line in lines:
        event = json.loads(line)
        for field in [
            "event_id",
            "timestamp_utc",
            "step_id",
            "from_state",
            "to_state",
            "actor",
            "reason",
            "stop_reason",
            "approval_reason",
        ]:
            assert field in event
        assert event["from_state"] in REQUIRED_STATES
        assert event["to_state"] in REQUIRED_STATES
