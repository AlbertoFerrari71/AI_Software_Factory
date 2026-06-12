from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from asf_risk_classifier import ClassifierInput, classify


DEFAULT_DATASET = Path("examples/eval/risk_classifier/golden.jsonl")
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_INPUT_ERROR = 2


def level_value(level: str) -> int:
    cleaned = str(level).strip().upper()
    if not cleaned.startswith("L") or not cleaned[1:].isdigit():
        raise ValueError(f"Invalid risk level: {level}")
    return int(cleaned[1:])


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(payload)
    return records


def input_for_record(record: dict[str, Any]) -> ClassifierInput:
    return ClassifierInput(
        text_items=tuple(str(item) for item in record.get("input_text_items", [record.get("input_text", "")])),
        file_items=tuple(str(item) for item in record.get("file_items", [])),
        command_items=tuple(str(item) for item in record.get("command_items", [])),
        keyword_items=tuple(str(item) for item in record.get("keyword_items", [])),
    )


def evaluate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for record in records:
        expected_level = str(record["expected_risk_level"]).upper()
        expected_gate = str(record["expected_required_gate"])
        result = classify(input_for_record(record))
        actual_level = str(result["risk_level"]).upper()
        actual_gate = str(result["required_gate"])
        comparison = {
            "id": record.get("id"),
            "expected_risk_level": expected_level,
            "actual_risk_level": actual_level,
            "expected_required_gate": expected_gate,
            "actual_required_gate": actual_gate,
            "expected_policy_outcome": record.get("expected_policy_outcome"),
        }
        results.append(comparison)

        if level_value(actual_level) < level_value(expected_level):
            failures.append({**comparison, "reason": "risk downgrade"})
            continue
        if level_value(actual_level) > level_value(expected_level):
            warnings.append({**comparison, "reason": "more conservative risk classification"})
            continue
        if actual_gate != expected_gate:
            failures.append({**comparison, "reason": "required gate mismatch at same risk level"})

    return {
        "status": "PASS" if not failures else "FAIL",
        "records": len(records),
        "failures": failures,
        "warnings": warnings,
        "results": results,
        "policy": "zero downgrade: any L3->L2 or L4->L3 downgrade fails",
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "Risk Classifier Golden Eval",
        f"status: {payload['status']}",
        f"records: {payload['records']}",
        f"failures: {len(payload['failures'])}",
        f"warnings: {len(payload['warnings'])}",
        f"policy: {payload['policy']}",
    ]
    if payload["failures"]:
        lines.append("failure_details:")
        for failure in payload["failures"]:
            lines.append(
                f"- {failure['id']}: expected {failure['expected_risk_level']}/"
                f"{failure['expected_required_gate']} got {failure['actual_risk_level']}/"
                f"{failure['actual_required_gate']} ({failure['reason']})"
            )
    if payload["warnings"]:
        lines.append("warning_details:")
        for warning in payload["warnings"]:
            lines.append(
                f"- {warning['id']}: expected {warning['expected_risk_level']} got "
                f"{warning['actual_risk_level']} ({warning['reason']})"
            )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ASF risk classifier golden eval with zero-downgrade policy.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="JSONL golden dataset.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    dataset = Path(args.dataset)
    if not dataset.is_file():
        print(f"ERROR: dataset not found: {dataset}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    try:
        payload = evaluate_records(load_records(dataset))
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return EXIT_SUCCESS if payload["status"] == "PASS" else EXIT_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
