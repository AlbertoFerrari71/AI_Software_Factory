from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3

LOOP_STATES = (
    "PLAN_NEXT_STEP",
    "BUILD_TASK_PACKET",
    "RISK_CLASSIFY",
    "EXECUTE_DRY_OR_WRITE",
    "RUN_TESTS",
    "INDEPENDENT_REVIEW",
    "GATE_DECISION",
    "COMMIT_OR_HOLD",
)

LIVE_PROVIDER_SIGNALS = (
    "external_provider_call",
    "live_provider_call",
    "call_openai",
    "openai_live",
    "anthropic_live",
    "network_call",
    "http_request",
    "api_key",
)

PUBLICATION_SIGNALS = (
    "git_commit",
    "git_push",
    "pr_create",
    "pr_merge",
    "git_merge_action",
    "deploy_live",
    "release_publish",
)


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    status: str
    diff_stat: str
    recent_commits: str

    @property
    def working_tree_state(self) -> str:
        return "CLEAN" if not self.status else "DIRTY"


@dataclass(frozen=True)
class LoopRequest:
    project_name: str
    repo_path: str
    step: str
    title: str
    branch: str
    objective: str
    allowed_scope: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    checks: tuple[str, ...]
    provided_gates: tuple[str, ...]


@dataclass(frozen=True)
class StateEvent:
    sequence: int
    state: str
    status: str
    checkpoint: str
    summary: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "state": self.state,
            "status": self.status,
            "checkpoint": self.checkpoint,
            "summary": self.summary,
        }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local ASF dry-run loop from a simulated request without provider calls or Git publication.",
    )
    parser.add_argument("--request-json", required=True, help="Path to the simulated step request JSON.")
    parser.add_argument("--plan-json", help="Optional dry-run execution plan JSON. If omitted, a plan is generated.")
    parser.add_argument("--output-dir", default="tmp/asf_dry_run_loop", help="Output base directory.")
    parser.add_argument(
        "--fail-on-dirty",
        action="store_true",
        help="Classify a dirty target working tree as FAIL instead of NEEDS_HUMAN.",
    )
    return parser.parse_args(argv)


def resolve_path(value: str, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"JSON file is not valid: {path}: {exc.msg}") from exc


def require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"request field '{key}' must be a non-empty string.")
    return value.strip()


def optional_string_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise InputError(f"request field '{key}' must be a list of strings.")
    return tuple(item.strip() for item in value if item.strip())


def optional_string_list_any(data: dict[str, Any], keys: tuple[str, ...]) -> tuple[str, ...]:
    collected: list[str] = []
    for key in keys:
        collected.extend(optional_string_list(data, key))
    return tuple(dict.fromkeys(collected))


def validate_step(step: str) -> None:
    if not step.isdigit() or int(step) <= 0:
        raise InputError("request field 'step' must be a positive numeric string.")


def validate_branch(branch: str) -> None:
    if re.search(r"\s", branch):
        raise InputError("request field 'branch' must not contain spaces.")


def load_request(path: Path) -> LoopRequest:
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise InputError("request JSON must be an object.")

    request = LoopRequest(
        project_name=require_string(raw, "project_name"),
        repo_path=require_string(raw, "repo_path"),
        step=require_string(raw, "step"),
        title=require_string(raw, "title"),
        branch=require_string(raw, "branch"),
        objective=require_string(raw, "objective"),
        allowed_scope=optional_string_list(raw, "allowed_scope"),
        forbidden_actions=optional_string_list(raw, "forbidden_actions"),
        checks=optional_string_list(raw, "checks"),
        provided_gates=optional_string_list_any(raw, ("provided_gates", "declared_gates", "satisfied_gates")),
    )
    validate_step(request.step)
    validate_branch(request.branch)
    return request


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "project"


def output_step_dir(args: argparse.Namespace, request: LoopRequest, root: Path) -> Path:
    base = resolve_path(args.output_dir, base=root)
    return base / safe_path_component(request.project_name) / f"step_{safe_path_component(request.step)}"


def resolve_target_repo(repo_path: str, root: Path) -> Path:
    path = resolve_path(repo_path, base=root)
    if not path.exists():
        raise InputError(f"repo_path does not exist: {path}")
    if not path.is_dir():
        raise InputError(f"repo_path is not a directory: {path}")
    if not (path / ".git").exists():
        raise InputError(f"repo_path is not a Git repository with .git: {path}")
    return path


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def read_git_snapshot(repo: Path) -> GitSnapshot:
    commands = {
        "branch": ["git", "branch", "--show-current"],
        "status": ["git", "status", "--short"],
        "diff_stat": ["git", "--no-pager", "diff", "--stat"],
        "recent_commits": ["git", "--no-pager", "log", "--oneline", "--max-count=10"],
    }
    results: dict[str, str] = {}
    errors: list[str] = []

    for key, command in commands.items():
        result = run_command(command, cwd=repo)
        if result.returncode != 0:
            errors.append(f"{key}: {result.stderr.strip() or result.stdout.strip()}")
        results[key] = result.stdout.strip()

    if errors:
        raise InputError("unable to read target Git snapshot: " + " | ".join(errors))

    return GitSnapshot(
        branch=results["branch"] or "(detached or unavailable)",
        status=results["status"],
        diff_stat=results["diff_stat"],
        recent_commits=results["recent_commits"],
    )


def normalize_request(request: LoopRequest, target_repo: Path) -> dict[str, Any]:
    return {
        "project_name": request.project_name,
        "repo_path": str(target_repo),
        "step": request.step,
        "title": request.title,
        "branch": request.branch,
        "objective": request.objective,
        "allowed_scope": list(request.allowed_scope),
        "forbidden_actions": list(request.forbidden_actions),
        "checks": list(request.checks),
        "provided_gates": list(request.provided_gates),
    }


def default_plan(request: LoopRequest) -> dict[str, Any]:
    checks = list(request.checks) or ["python -m pytest", "workflow health check", "verify gate", "diff check"]
    return {
        "plan_id": f"dry-run-loop-{request.step}",
        "mode": "dry-run",
        "states": [
            {
                "state": "PLAN_NEXT_STEP",
                "checkpoint": "request_loaded",
                "actions": ["load_request", "read_target_git_snapshot"],
            },
            {
                "state": "BUILD_TASK_PACKET",
                "checkpoint": "task_packet_generated",
                "actions": ["generate_dry_run_task_packet", "write_manifest"],
            },
            {
                "state": "RISK_CLASSIFY",
                "checkpoint": "risk_report_generated",
                "actions": ["classify_with_asf_risk_classifier", "record_gate_policy"],
            },
            {
                "state": "EXECUTE_DRY_OR_WRITE",
                "checkpoint": "dry_run_preview_generated",
                "actions": ["write_inert_execution_preview", "do_not_modify_target_repo"],
            },
            {
                "state": "RUN_TESTS",
                "checkpoint": "test_plan_report_generated",
                "actions": ["record_required_checks_without_running_target_mutations"],
                "checks": checks,
            },
            {
                "state": "INDEPENDENT_REVIEW",
                "checkpoint": "review_generated",
                "actions": ["verify_artifacts", "verify_target_status_unchanged"],
            },
            {
                "state": "GATE_DECISION",
                "checkpoint": "gate_decision_generated",
                "actions": ["decide_needs_human_or_fail"],
            },
            {
                "state": "COMMIT_OR_HOLD",
                "checkpoint": "final_hold_report_generated",
                "actions": ["hold_for_human_review", "do_not_publish"],
            },
        ],
        "external_provider_calls": False,
        "git_publication_actions": False,
        "writes_target_repo": False,
    }


def load_or_generate_plan(path_value: str | None, root: Path, request: LoopRequest) -> dict[str, Any]:
    if not path_value:
        return default_plan(request)
    path = resolve_path(path_value, base=root)
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise InputError("plan JSON must be an object.")
    return raw


def collect_string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        collected: list[str] = []
        for item in value:
            collected.extend(collect_string_values(item))
        return collected
    if isinstance(value, dict):
        collected = []
        for item in value.values():
            collected.extend(collect_string_values(item))
        return collected
    return []


def plan_risk_items(value: Any) -> tuple[str, ...]:
    risk_keys = {
        "actions",
        "checks",
        "commands",
        "phase_a_checks",
        "phase_b_commands",
        "phase_c_checks",
        "phase_commands",
        "proposed_commands",
    }
    collected: list[str] = []

    if isinstance(value, dict):
        for key, item in value.items():
            if key in risk_keys:
                collected.extend(collect_string_values(item))
            else:
                collected.extend(plan_risk_items(item))
    elif isinstance(value, list):
        for item in value:
            collected.extend(plan_risk_items(item))

    return tuple(item.strip() for item in collected if item.strip())


def plan_provided_gates(plan: dict[str, Any]) -> tuple[str, ...]:
    collected: list[str] = []
    for key in ("provided_gates", "declared_gates", "satisfied_gates"):
        value = plan.get(key, [])
        if isinstance(value, str):
            collected.append(value)
        elif isinstance(value, list):
            collected.extend(str(item) for item in value if str(item).strip())
    return tuple(dict.fromkeys(item.strip() for item in collected if item.strip()))


def plan_value_text(plan: dict[str, Any]) -> str:
    return "\n".join(collect_string_values(plan)).casefold()


def validate_plan_shape(plan: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if plan.get("mode") != "dry-run":
        blockers.append("plan mode must be dry-run.")

    states = plan.get("states")
    if not isinstance(states, list) or not states:
        blockers.append("plan must contain a non-empty states list.")
    else:
        seen: list[str] = []
        for item in states:
            if not isinstance(item, dict):
                blockers.append("each plan state must be an object.")
                continue
            state = item.get("state")
            if not isinstance(state, str):
                blockers.append("each plan state must include a string state.")
                continue
            seen.append(state)
        missing = [state for state in LOOP_STATES if state not in seen]
        if missing:
            blockers.append("plan is missing loop states: " + ", ".join(missing))

    if plan.get("external_provider_calls") is True:
        blockers.append("plan declares external provider calls.")
    if plan.get("git_publication_actions") is True:
        blockers.append("plan declares Git publication actions.")
    if plan.get("writes_target_repo") is True:
        blockers.append("plan declares target repository writes.")

    lowered = plan_value_text(plan)
    for signal in LIVE_PROVIDER_SIGNALS:
        if signal in lowered:
            blockers.append(f"plan contains live/provider signal: {signal}")
    for signal in PUBLICATION_SIGNALS:
        if signal in lowered:
            blockers.append(f"plan contains publication signal: {signal}")
    if "danger-full-access" in lowered:
        blockers.append("plan contains forbidden sandbox signal.")

    return blockers


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def bullets(items: list[str] | tuple[str, ...], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_json(path: Path, content: dict[str, Any]) -> None:
    write_text(path, json.dumps(content, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, events: list[StateEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(event.as_dict(), sort_keys=True) for event in events]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_task_packet(request: LoopRequest, snapshot: GitSnapshot, plan: dict[str, Any]) -> str:
    return f"""# STEP {request.step} - {request.title}

## Dry-run loop request

- project-name: `{request.project_name}`
- branch expected: `{request.branch}`
- current branch: `{snapshot.branch}`
- working tree: `{snapshot.working_tree_state}`
- plan-id: `{plan.get("plan_id", "provided-plan")}`
- mode: `dry-run`

## Objective

{request.objective}

## Allowed scope

{bullets(request.allowed_scope, fallback="No additional scope declared by the simulated request.")}

## Forbidden actions

{bullets(request.forbidden_actions, fallback="No extra forbidden actions declared by the simulated request.")}

## Provided gates declared by input

{bullets(request.provided_gates, fallback="No gate token declared by the simulated request.")}

Always forbidden for this runner:

- no live provider calls;
- no secret or API key usage;
- no commit, push, PR, merge, deploy or release;
- no target repository write;
- no destructive cleanup.

## Required checks to record

{bullets(request.checks, fallback="Use the repository verification gate documented for the target.")}

## Target Git snapshot

Status:

```text
{markdown_block(snapshot.status)}
```

Diff stat:

```text
{markdown_block(snapshot.diff_stat)}
```

Recent commits:

```text
{markdown_block(snapshot.recent_commits)}
```

## Dry-run rule

This task packet is generated as evidence for the loop runner. It is not an authorization to write, publish or call a provider.
"""


def fail_closed_classifier_result(reason: str) -> dict[str, Any]:
    return {
        "risk_level": "L4",
        "allowed": False,
        "required_gate": "elevated_manual_approval",
        "reasons": [reason],
        "matched_rules": [
            {
                "rule_id": "dry_run_runner_fail_closed",
                "risk_level": "L4",
                "source": "runner",
                "matched_value": reason,
                "reason": "risk classification could not be completed safely",
            }
        ],
        "fail_closed": True,
        "recommended_next_action": "Stop for human review because risk classification could not be completed.",
    }


def validate_classifier_result(result: Any) -> str | None:
    if not isinstance(result, dict):
        return "classifier result is not a JSON object."

    required = {
        "risk_level": str,
        "allowed": bool,
        "required_gate": str,
        "reasons": list,
        "matched_rules": list,
        "fail_closed": bool,
        "recommended_next_action": str,
    }
    for key, expected_type in required.items():
        if key not in result:
            return f"classifier result is missing '{key}'."
        if not isinstance(result[key], expected_type):
            return f"classifier result field '{key}' has invalid type."

    if result["risk_level"] not in {"L0", "L1", "L2", "L3", "L4"}:
        return "classifier result contains an unknown risk level."
    return None


def build_classifier_result(request: LoopRequest, plan: dict[str, Any]) -> dict[str, Any]:
    try:
        from asf_risk_classifier import ClassifierInput, classify
    except Exception as exc:  # pragma: no cover - defensive fail-closed path
        return fail_closed_classifier_result(f"Unable to import asf_risk_classifier: {exc}")

    provided_gates = set(request.provided_gates + plan_provided_gates(plan))
    request_input = ClassifierInput(
        text_items=(request.title, request.objective),
        file_items=request.allowed_scope,
        command_items=request.checks,
        keyword_items=(),
    )
    request_result = classify(request_input, provided_gates=provided_gates)
    invalid = validate_classifier_result(request_result)
    if invalid:
        return fail_closed_classifier_result(invalid)
    if request_result["fail_closed"]:
        return request_result

    combined_input = ClassifierInput(
        text_items=request_input.text_items,
        file_items=request_input.file_items,
        command_items=request_input.command_items + plan_risk_items(plan),
        keyword_items=request_input.keyword_items,
    )
    combined_result = classify(combined_input, provided_gates=provided_gates)
    invalid = validate_classifier_result(combined_result)
    if invalid:
        return fail_closed_classifier_result(invalid)
    return combined_result


def build_risk_checkpoint(request: LoopRequest, plan: dict[str, Any], plan_blockers: list[str]) -> dict[str, Any]:
    risk = build_classifier_result(request, plan)
    provided_gates = tuple(dict.fromkeys(request.provided_gates + plan_provided_gates(plan)))
    l4_blocked = risk["risk_level"] == "L4" and not risk["allowed"]
    runner_fail_closed = bool(plan_blockers or risk["fail_closed"] or l4_blocked)
    status = "FAIL" if runner_fail_closed else "PASS"

    return {
        "checkpoint": "RISK_CLASSIFY",
        "status": status,
        "risk": risk,
        "gate": {
            "required_gate": risk["required_gate"],
            "provided_gates": list(provided_gates),
            "declared_satisfied": risk["allowed"],
            "dry_run_enforced": True,
            "runner_executes_gate": False,
        },
        "dry_run": {
            "fail_closed": runner_fail_closed,
            "blocked_in_dry_run": status == "FAIL",
            "no_live_provider_calls": True,
            "no_target_repo_writes": True,
            "no_git_publication": True,
        },
        "plan_blockers": plan_blockers,
    }


def build_risk_markdown(request: LoopRequest, risk_report: dict[str, Any]) -> str:
    risk = risk_report["risk"]
    return f"""# ASF Dry-run Loop Risk Report

## Summary

- step: `{request.step}`
- title: `{request.title}`
- checkpoint: `{risk_report["checkpoint"]}`
- status: `{risk_report["status"]}`
- risk-level: `{risk["risk_level"]}`
- required-gate: `{risk["required_gate"]}`
- gate-declared-satisfied: `{risk_report["gate"]["declared_satisfied"]}`
- runner-fail-closed: `{risk_report["dry_run"]["fail_closed"]}`

## Reasons

{bullets(list(risk["reasons"]))}

## Matched rules

{bullets([f"{match['rule_id']} ({match['risk_level']}): {match['reason']}" for match in risk["matched_rules"]])}

## Policy

- live provider calls allowed: `false`
- target writes allowed: `false`
- Git publication allowed: `false`
- external costs allowed: `false`
- runner executes gates: `false`

## Next action

{risk["recommended_next_action"]}
"""


def build_execution_preview(request: LoopRequest, plan: dict[str, Any]) -> str:
    state_lines = []
    for item in plan.get("states", []):
        if isinstance(item, dict):
            state = item.get("state", "(missing)")
            checkpoint = item.get("checkpoint", "(missing)")
            actions = item.get("actions", [])
            if not isinstance(actions, list):
                actions = []
            state_lines.append(f"- `{state}` -> `{checkpoint}`: {', '.join(str(action) for action in actions)}")

    return f"""# ASF Dry-run Execution Preview

## Summary

- step: `{request.step}`
- mode: `dry-run`
- provider calls: `not allowed`
- target writes: `not allowed`
- publication: `not allowed`

## Planned states

{chr(10).join(state_lines) if state_lines else "- none"}

## Not executed

- no live provider call;
- no target repository write;
- no commit, push, PR, merge, deploy or release;
- no destructive command.
"""


def build_test_report(request: LoopRequest, plan: dict[str, Any]) -> str:
    checks: list[str] = []
    for item in plan.get("states", []):
        if isinstance(item, dict) and item.get("state") == "RUN_TESTS":
            raw_checks = item.get("checks", [])
            if isinstance(raw_checks, list):
                checks.extend(str(check) for check in raw_checks)
    if not checks:
        checks.extend(request.checks)

    return f"""# ASF Dry-run Loop Test Report

## Summary

- step: `{request.step}`
- status: `DRY_RUN_RECORDED`
- runner-executed-target-tests: `false`

## Checks recorded for supervised execution

{bullets(checks, fallback="No checks declared.")}

## Note

The loop runner records the test checkpoint and required checks. It does not execute target test commands as part of this dry-run step.
"""


def review_artifacts(
    *,
    request: LoopRequest,
    risk_report: dict[str, Any],
    plan_blockers: list[str],
    before: GitSnapshot,
    after: GitSnapshot,
    artifact_paths: dict[str, Path],
    fail_on_dirty: bool,
) -> dict[str, Any]:
    blocking: list[str] = []
    warnings: list[str] = []

    if risk_report["status"] != "PASS":
        blocking.append("risk checkpoint is not PASS.")
    blocking.extend(plan_blockers)

    if before.status != after.status:
        blocking.append("target Git status changed during dry-run.")
    if before.branch != request.branch:
        warnings.append("target branch differs from simulated request branch.")
    if before.status:
        if fail_on_dirty:
            blocking.append("target working tree is dirty and fail-on-dirty is active.")
        else:
            warnings.append("target working tree is dirty; human review required.")

    missing = [label for label, path in artifact_paths.items() if not path.is_file()]
    for label in missing:
        blocking.append(f"required artifact missing: {label}")

    verdict = "FAIL" if blocking else "PASS"
    return {
        "verdict": verdict,
        "step": request.step,
        "blocking_findings": blocking,
        "warnings": warnings,
        "checks": {
            "risk_pass": risk_report["status"] == "PASS",
            "target_status_unchanged": before.status == after.status,
            "artifacts_present": not missing,
            "live_provider_absent": not any("provider" in item.casefold() for item in plan_blockers),
            "publication_absent": not any("publication" in item.casefold() for item in plan_blockers),
        },
    }


def decide_gate(review: dict[str, Any]) -> dict[str, Any]:
    if review["verdict"] == "FAIL":
        decision = "FAIL"
        next_action = "Stop and correct blocking findings before rerunning the loop."
    else:
        decision = "NEEDS_HUMAN"
        next_action = "Review evidence manually before any future executor, write or publication step."

    return {
        "decision": decision,
        "reason": "Dry-run loop completed; supervised gate remains mandatory."
        if decision == "NEEDS_HUMAN"
        else "Dry-run loop detected blocking findings.",
        "next_action": next_action,
        "not_authorized": [
            "live provider calls",
            "target repository writes",
            "commit",
            "push",
            "PR",
            "merge",
            "deploy",
            "release",
        ],
    }


def build_gate_markdown(request: LoopRequest, gate: dict[str, Any], review: dict[str, Any]) -> str:
    return f"""# ASF Dry-run Loop Gate Decision

## Summary

- step: `{request.step}`
- title: `{request.title}`
- decision: `{gate["decision"]}`
- review-verdict: `{review["verdict"]}`

## Reason

{gate["reason"]}

## Blocking findings

{bullets(review["blocking_findings"])}

## Warnings

{bullets(review["warnings"])}

## Next action

{gate["next_action"]}
"""


def build_final_report(
    *,
    request: LoopRequest,
    target_repo: Path,
    before: GitSnapshot,
    after: GitSnapshot,
    risk_report: dict[str, Any],
    review: dict[str, Any],
    gate: dict[str, Any],
    artifact_paths: dict[str, Path],
) -> str:
    artifacts = [f"- `{label}`: `{path}`" for label, path in artifact_paths.items()]
    risk = risk_report["risk"]
    return f"""# ASF Dry-run Loop Runner Final Report

## Summary

- step: `{request.step}`
- title: `{request.title}`
- project-name: `{request.project_name}`
- target-repo: `{target_repo}`
- decision: `{gate["decision"]}`
- risk: `{risk["risk_level"]}` / `{risk_report["status"]}`
- required-gate: `{risk["required_gate"]}`
- gate-declared-satisfied: `{risk_report["gate"]["declared_satisfied"]}`
- review: `{review["verdict"]}`

## Target state

- branch before: `{before.branch}`
- branch after: `{after.branch}`
- working tree before: `{before.working_tree_state}`
- working tree after: `{after.working_tree_state}`
- target status unchanged: `{before.status == after.status}`

## Artifacts

{chr(10).join(artifacts)}

## Non-actions confirmed

- No live provider call was made.
- No secret or API key was read.
- No target repository write was performed by the runner.
- No commit, push, PR, merge, deploy or release was performed.
- No destructive command was executed.

## Residual limits

- The test checkpoint records required commands; it does not execute target tests.
- The independent review is deterministic and local; it is not a substitute for Alberto review.
- The gate decision is a hold point, not an approval to proceed.
- `allowed` in the risk report means only that the declared gate token matched the policy; it is not an operational authorization.

## Next recommended step

0620) Gate Decision Report and Human Approval Packet
"""


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    request_path = resolve_path(args.request_json, base=root)
    request = load_request(request_path)
    target_repo = resolve_target_repo(request.repo_path, root)
    output_dir = output_step_dir(args, request, root)

    plan = load_or_generate_plan(args.plan_json, root, request)
    plan_blockers = validate_plan_shape(plan)
    before = read_git_snapshot(target_repo)

    artifact_paths = {
        "normalized_request_json": output_dir / "normalized_request.json",
        "execution_plan_json": output_dir / "execution_plan.json",
        "state_log_jsonl": output_dir / "state_log.jsonl",
        "task_packet_md": output_dir / "dry_run_task_packet.md",
        "risk_report_json": output_dir / "risk_report.json",
        "risk_report_md": output_dir / "risk_report.md",
        "execution_preview_md": output_dir / "execution_preview.md",
        "test_report_md": output_dir / "test_report.md",
        "independent_review_json": output_dir / "independent_review.json",
        "gate_decision_json": output_dir / "gate_decision.json",
        "gate_decision_md": output_dir / "gate_decision.md",
        "final_report_md": output_dir / "final_report.md",
    }

    events: list[StateEvent] = [
        StateEvent(1, "PLAN_NEXT_STEP", "PASS", "request_loaded", "Simulated request and target Git snapshot loaded."),
        StateEvent(2, "BUILD_TASK_PACKET", "PASS", "task_packet_generated", "Dry-run task packet generated."),
    ]

    write_json(artifact_paths["normalized_request_json"], normalize_request(request, target_repo))
    write_json(artifact_paths["execution_plan_json"], plan)
    write_text(artifact_paths["task_packet_md"], build_task_packet(request, before, plan))

    risk_report = build_risk_checkpoint(request, plan, plan_blockers)
    events.append(
        StateEvent(
            3,
            "RISK_CLASSIFY",
            risk_report["status"],
            "risk_report_generated",
            (
                f"Risk classified as {risk_report['risk']['risk_level']} "
                f"with gate {risk_report['risk']['required_gate']}."
            ),
        )
    )
    write_json(artifact_paths["risk_report_json"], risk_report)
    write_text(artifact_paths["risk_report_md"], build_risk_markdown(request, risk_report))

    events.append(
        StateEvent(
            4,
            "EXECUTE_DRY_OR_WRITE",
            "PASS" if not plan_blockers else "FAIL",
            "dry_run_preview_generated",
            "Inert execution preview generated; no target write attempted.",
        )
    )
    write_text(artifact_paths["execution_preview_md"], build_execution_preview(request, plan))

    events.append(
        StateEvent(
            5,
            "RUN_TESTS",
            "PASS",
            "test_plan_report_generated",
            "Required checks recorded for supervised execution.",
        )
    )
    write_text(artifact_paths["test_report_md"], build_test_report(request, plan))

    after = read_git_snapshot(target_repo)
    review_input_artifacts = {
        key: artifact_paths[key]
        for key in (
            "normalized_request_json",
            "execution_plan_json",
            "task_packet_md",
            "risk_report_json",
            "risk_report_md",
            "execution_preview_md",
            "test_report_md",
        )
    }
    review = review_artifacts(
        request=request,
        risk_report=risk_report,
        plan_blockers=plan_blockers,
        before=before,
        after=after,
        artifact_paths=review_input_artifacts,
        fail_on_dirty=args.fail_on_dirty,
    )
    events.append(
        StateEvent(
            6,
            "INDEPENDENT_REVIEW",
            review["verdict"],
            "review_generated",
            "Deterministic local review generated.",
        )
    )
    write_json(artifact_paths["independent_review_json"], review)

    gate = decide_gate(review)
    events.append(
        StateEvent(
            7,
            "GATE_DECISION",
            gate["decision"],
            "gate_decision_generated",
            gate["reason"],
        )
    )
    write_json(artifact_paths["gate_decision_json"], gate)
    write_text(artifact_paths["gate_decision_md"], build_gate_markdown(request, gate, review))

    events.append(
        StateEvent(
            8,
            "COMMIT_OR_HOLD",
            "HOLD",
            "final_hold_report_generated",
            "Runner stopped at supervised hold; no publication action performed.",
        )
    )
    write_jsonl(artifact_paths["state_log_jsonl"], events)
    write_text(
        artifact_paths["final_report_md"],
        build_final_report(
            request=request,
            target_repo=target_repo,
            before=before,
            after=after,
            risk_report=risk_report,
            review=review,
            gate=gate,
            artifact_paths=artifact_paths,
        ),
    )

    print(f"Dry-run loop artifacts generated: {output_dir}")
    print(f"Decision: {gate['decision']}")
    print(f"Final report: {artifact_paths['final_report_md']}")
    return EXIT_RUNTIME_ERROR if gate["decision"] == "FAIL" else EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
