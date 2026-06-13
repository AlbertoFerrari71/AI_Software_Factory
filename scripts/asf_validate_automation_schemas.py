from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SCHEMA_DIR = Path("schemas/asf_automation")
EXAMPLE_DIR = Path("examples/asf_automation")

SCHEMA_EXAMPLE_PAIRS = {
    "task_packet": (
        SCHEMA_DIR / "task_packet.schema.json",
        EXAMPLE_DIR / "task_packet_example.json",
    ),
    "state_card": (
        SCHEMA_DIR / "state_card.schema.json",
        EXAMPLE_DIR / "state_card_example.json",
    ),
    "context_pack": (
        SCHEMA_DIR / "context_pack.schema.json",
        EXAMPLE_DIR / "context_pack_example.json",
    ),
    "runner_state": (
        SCHEMA_DIR / "runner_state.schema.json",
        EXAMPLE_DIR / "runner_state_example.json",
    ),
    "ai_review": (
        SCHEMA_DIR / "ai_review.schema.json",
        EXAMPLE_DIR / "ai_review_example.json",
    ),
    "repair_packet": (
        SCHEMA_DIR / "repair_packet.schema.json",
        EXAMPLE_DIR / "repair_packet_example.json",
    ),
}


REQUIRED_EXAMPLE_FIELDS = {
    "task_packet": {
        "task_packet_version",
        "project",
        "step",
        "state",
        "scope",
        "allowed_files",
        "forbidden_actions",
        "deliverables",
        "gates",
        "report",
        "publish_policy",
        "human_gate_policy",
        "repair_policy",
    },
    "state_card": {
        "state_card_version",
        "project",
        "last_completed_step",
        "current_branch",
        "head_commit",
        "repo_clean",
        "last_gate_status",
        "last_ci_status",
        "capabilities_now_available",
        "open_warnings",
        "do_not_forget",
        "next_recommended_step",
        "human_decision_required",
    },
    "context_pack": {
        "context_pack_version",
        "project",
        "step",
        "max_size_policy",
        "included_summaries",
        "relevant_files",
        "previous_report_summary",
        "constraints",
        "gates",
        "stop_conditions",
        "auto_split_policy",
    },
    "runner_state": {
        "runner_state_version",
        "project",
        "step",
        "current_state",
        "status",
        "allowed_states",
        "history",
        "open_blockers",
        "updated_at",
    },
    "ai_review": {
        "ai_review_version",
        "project",
        "step",
        "reviewer",
        "verdict",
        "status",
        "risk_level",
        "scope_check",
        "tests_check",
        "gate_check",
        "deterministic_gate_status",
        "findings",
        "warnings",
        "evidence",
        "recommendation",
    },
    "repair_packet": {
        "repair_packet_version",
        "project",
        "step",
        "parent_step_id",
        "parent_task_packet_ref",
        "trigger",
        "scope",
        "allowed_files",
        "forbidden_actions",
        "repair_instructions",
        "gates",
        "max_attempts",
        "current_attempt",
        "escalation_policy",
        "report",
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"file not found: {path}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {path}: {exc.msg}"


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_instance(schema: dict[str, Any], instance: Any, path: str = "$") -> list[str]:
    errors: list[str] = []

    schema_type = schema.get("type")
    if isinstance(schema_type, str) and not type_matches(instance, schema_type):
        return [f"{path}: expected {schema_type}, got {type(instance).__name__}"]

    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and instance not in enum_values:
        errors.append(f"{path}: value {instance!r} is not in enum")

    if schema_type == "object" and isinstance(instance, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required field {key!r}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}

        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unexpected field {key!r}")

        for key, value in instance.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                errors.extend(validate_instance(child_schema, value, f"{path}.{key}"))

    if schema_type == "array" and isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} item(s)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item_schema, item, f"{path}[{index}]"))

    return errors


def validate_with_jsonschema(schema: dict[str, Any], instance: Any) -> list[str]:
    if importlib.util.find_spec("jsonschema") is None:
        return []

    try:
        import jsonschema  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - defensive only
        return [f"jsonschema import failed: {exc}"]

    try:
        validator_cls = jsonschema.Draft7Validator
        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        return [error.message for error in sorted(validator.iter_errors(instance), key=str)]
    except Exception as exc:
        return [f"jsonschema validation failed: {exc}"]


def validate_required_minimum(name: str, example: Any) -> list[str]:
    if not isinstance(example, dict):
        return [f"{name}: example must be an object"]
    missing = sorted(REQUIRED_EXAMPLE_FIELDS[name] - set(example))
    return [f"{name}: missing required example field {field}" for field in missing]


def validate_pairs(root: Path) -> list[str]:
    errors: list[str] = []

    for name, (schema_rel, example_rel) in SCHEMA_EXAMPLE_PAIRS.items():
        schema_path = root / schema_rel
        example_path = root / example_rel

        if not schema_path.is_file():
            errors.append(f"missing schema: {schema_rel}")
            continue
        if not example_path.is_file():
            errors.append(f"missing example: {example_rel}")
            continue

        schema, schema_error = read_json(schema_path)
        if schema_error:
            errors.append(f"invalid schema: {schema_error}")
            continue
        example, example_error = read_json(example_path)
        if example_error:
            errors.append(f"invalid example: {example_error}")
            continue

        if not isinstance(schema, dict):
            errors.append(f"invalid schema: {schema_rel}: root must be an object")
            continue

        errors.extend(validate_required_minimum(name, example))
        for error in validate_instance(schema, example):
            errors.append(f"{name}: {error}")
        for error in validate_with_jsonschema(schema, example):
            errors.append(f"{name}: {error}")

    return errors


def main(argv: list[str]) -> int:
    root = repo_root()
    errors = validate_pairs(root)

    if errors:
        print("ASF automation schema validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return EXIT_FAILURE

    print("ASF automation schema validation: PASS")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
