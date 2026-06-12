from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class StepRecord:
    namespace: str
    step: str
    title: str
    status: str
    report_pattern: str
    next_step: str


KNOWN_STEPS: tuple[StepRecord, ...] = (
    StepRecord(
        namespace="motor",
        step="1030",
        title="ASF GPT Live Continuity Mega-Step",
        status="published",
        report_pattern="1030-Report_Codex.*",
        next_step="motor/1035",
    ),
    StepRecord(
        namespace="motor",
        step="1035",
        title="Provider Response Diagnostic Sanitized Review",
        status="published",
        report_pattern="1035-Report_Codex.*",
        next_step="motor/1040",
    ),
    StepRecord(
        namespace="motor",
        step="1050-1130",
        title="ASF V1 Supervised Operator Release Candidate",
        status="local_rc",
        report_pattern="1050-1130-Report_Codex.*",
        next_step="motor/1140",
    ),
)

NEXT_STEP_AFTER_RC = "1140) Prompt Injection Adversarial Samples and Fencing"


def records() -> list[dict[str, str]]:
    return [asdict(record) for record in KNOWN_STEPS]


def latest_record() -> StepRecord:
    return KNOWN_STEPS[-1]


def find_record(step: str | None) -> StepRecord:
    if not step or step == "latest":
        return latest_record()
    normalized = step.rsplit("/", 1)[-1]
    for record in KNOWN_STEPS:
        if record.step == normalized or normalized in record.step.split("-"):
            return record
    return StepRecord(
        namespace="motor",
        step=normalized,
        title="Unknown step",
        status="unknown",
        report_pattern=f"{normalized}-Report_Codex.*",
        next_step="ASK_ALBERTO",
    )


def docs_exist(root: Path) -> dict[str, bool]:
    return {
        "operator_rc": (root / "docs" / "motor" / "1130_ASF_V1_SUPERVISED_OPERATOR_RC.md").is_file(),
        "operator_runbook": (root / "docs" / "motor" / "1130_OPERATOR_RUNBOOK.md").is_file(),
        "known_limits": (root / "docs" / "motor" / "1130_KNOWN_LIMITS_AND_NEXT_ROADMAP.md").is_file(),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show ASF step registry data.")
    parser.add_argument("--step", default="latest", help="Step to inspect, or latest.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    record = find_record(args.step)
    payload = {"selected": asdict(record), "known_steps": records(), "docs_exist": docs_exist(Path.cwd())}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"namespace: {record.namespace}")
        print(f"step: {record.step}")
        print(f"title: {record.title}")
        print(f"status: {record.status}")
        print(f"next_step: {record.next_step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
