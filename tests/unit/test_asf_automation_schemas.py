from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas" / "asf_automation"
EXAMPLE_DIR = ROOT / "examples" / "asf_automation"
VALIDATOR = ROOT / "scripts" / "asf_validate_automation_schemas.py"

SCHEMAS = {
    "task_packet": SCHEMA_DIR / "task_packet.schema.json",
    "state_card": SCHEMA_DIR / "state_card.schema.json",
    "context_pack": SCHEMA_DIR / "context_pack.schema.json",
    "runner_state": SCHEMA_DIR / "runner_state.schema.json",
    "ai_review": SCHEMA_DIR / "ai_review.schema.json",
    "repair_packet": SCHEMA_DIR / "repair_packet.schema.json",
}

EXAMPLES = {
    "task_packet": EXAMPLE_DIR / "task_packet_example.json",
    "state_card": EXAMPLE_DIR / "state_card_example.json",
    "context_pack": EXAMPLE_DIR / "context_pack_example.json",
    "runner_state": EXAMPLE_DIR / "runner_state_example.json",
    "ai_review": EXAMPLE_DIR / "ai_review_example.json",
    "repair_packet": EXAMPLE_DIR / "repair_packet_example.json",
}

REQUIRED_RUNNER_STATES = {
    "PLANNED",
    "READY_FOR_CONTEXT",
    "CONTEXT_PACK_BUILT",
    "TASK_PACKET_BUILT",
    "WAITING_HUMAN_APPROVAL",
    "READY_FOR_CODEX",
    "CODEX_RUNNING",
    "CODEX_DONE",
    "REPORT_COLLECTED",
    "LOCAL_GATE_RUNNING",
    "LOCAL_GATE_PASS",
    "LOCAL_GATE_FAIL",
    "AI_REVIEW_RUNNING",
    "AI_REVIEW_PASS",
    "AI_REVIEW_FAIL",
    "REPAIR_PACKET_BUILT",
    "REPAIR_RUNNING",
    "READY_FOR_PUBLISH",
    "PUBLISH_RUNNING",
    "PUBLISHED",
    "CI_RUNNING",
    "CI_PASS",
    "CI_FAIL",
    "DONE",
    "BLOCKED",
    "ABORTED",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator_module() -> Any:
    spec = importlib.util.spec_from_file_location("asf_validate_automation_schemas", VALIDATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def walk_values(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, dict):
        for item in value.values():
            values.extend(walk_values(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(walk_values(item))
    return values


def test_all_schema_files_exist() -> None:
    for path in SCHEMAS.values():
        assert path.is_file(), path


def test_all_example_files_exist() -> None:
    for path in EXAMPLES.values():
        assert path.is_file(), path


def test_examples_are_valid_json() -> None:
    for path in EXAMPLES.values():
        assert isinstance(read_json(path), dict), path


def test_validator_returns_exit_code_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ASF automation schema validation: PASS" in result.stdout


def test_runner_state_schema_contains_all_required_states() -> None:
    schema = read_json(SCHEMAS["runner_state"])
    current_state_enum = set(schema["properties"]["current_state"]["enum"])
    allowed_state_enum = set(schema["properties"]["allowed_states"]["items"]["enum"])
    assert REQUIRED_RUNNER_STATES <= current_state_enum
    assert REQUIRED_RUNNER_STATES <= allowed_state_enum


def test_task_packet_contains_forbidden_actions() -> None:
    schema = read_json(SCHEMAS["task_packet"])
    example = read_json(EXAMPLES["task_packet"])
    assert "forbidden_actions" in schema["required"]
    assert "forbidden_actions" in example
    assert {"commit", "push", "merge", "deploy"} <= set(example["forbidden_actions"])


def test_state_card_contains_next_recommended_step() -> None:
    schema = read_json(SCHEMAS["state_card"])
    example = read_json(EXAMPLES["state_card"])
    assert "next_recommended_step" in schema["required"]
    assert example["next_recommended_step"].startswith("1300-1390")


def test_context_pack_contains_auto_split_policy() -> None:
    schema = read_json(SCHEMAS["context_pack"])
    example = read_json(EXAMPLES["context_pack"])
    assert "auto_split_policy" in schema["required"]
    assert example["auto_split_policy"]["enabled"] is True


def test_repair_packet_contains_parent_step_id() -> None:
    schema = read_json(SCHEMAS["repair_packet"])
    example = read_json(EXAMPLES["repair_packet"])
    assert "parent_step_id" in schema["required"]
    assert example["parent_step_id"] == "1200-1290"


def test_ai_review_contains_structured_verdict_and_status() -> None:
    schema = read_json(SCHEMAS["ai_review"])
    example = read_json(EXAMPLES["ai_review"])
    assert "verdict" in schema["required"]
    assert "status" in schema["required"]
    assert set(schema["properties"]["verdict"]["enum"]) == {
        "PASS",
        "PASS_WITH_WARNINGS",
        "FAIL",
        "BLOCKED",
    }
    assert example["verdict"] == "PASS_WITH_WARNINGS"
    assert example["status"] == "PASS_WITH_WARNINGS"


def test_schemas_reject_arbitrary_fields_when_additional_properties_false() -> None:
    validator = load_validator_module()
    schema = read_json(SCHEMAS["task_packet"])
    example = read_json(EXAMPLES["task_packet"])
    example["unexpected_root_field"] = "must fail"
    errors = validator.validate_instance(schema, example)
    assert any("unexpected field" in error for error in errors)


def test_examples_do_not_authorize_publish_actions_without_policy() -> None:
    action_keys = {
        "commit_allowed",
        "push_allowed",
        "pr_allowed",
        "merge_allowed",
        "tag_allowed",
        "deploy_allowed",
    }
    for path in EXAMPLES.values():
        data = read_json(path)
        for value in walk_values(data):
            if isinstance(value, dict):
                for key in action_keys & set(value):
                    assert value[key] is False, f"{path}: {key} must be false"
