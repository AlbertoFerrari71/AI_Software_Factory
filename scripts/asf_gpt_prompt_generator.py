from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

DEFAULT_MODE = "mock"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_PROVIDER = "openai"
SUPPORTED_MODES = {"mock", "live"}


@dataclass(frozen=True)
class StepPlan:
    path: Path
    step_id: str
    title: str
    objective: str
    risk_level: str
    phase: str
    allowed_paths: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    source_format: str
    raw: dict[str, Any]


def compact_string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return []
    if isinstance(value, list | tuple | set):
        items: list[str] = []
        for item in value:
            text = compact_string(item)
            if text:
                items.append(text)
        return items
    text = compact_string(value)
    return [text] if text else []


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def infer_step_id(text: str, fallback: str) -> str:
    match = re.search(r"\b(\d{4}(?:-\d{4})?)\b", text)
    return match.group(1) if match else fallback


def first_markdown_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def load_plan(path: Path) -> StepPlan:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read plan: {path}: {exc}") from exc

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        heading = first_markdown_heading(text)
        step_id = infer_step_id(text, path.stem)
        raw = {
            "step_id": step_id,
            "title": heading or path.stem,
            "objective": heading or "Generate a deterministic Codex prompt from the supplied Markdown plan.",
            "risk_level": "L1",
            "phase": "mock-planning",
            "allowed_paths": [],
            "forbidden_actions": [],
            "source_excerpt": "\n".join(text.splitlines()[:20]),
        }
        return StepPlan(
            path=path.resolve(),
            step_id=step_id,
            title=compact_string(raw["title"]),
            objective=compact_string(raw["objective"]),
            risk_level=compact_string(raw["risk_level"]) or "L1",
            phase=compact_string(raw["phase"]) or "mock-planning",
            allowed_paths=(),
            forbidden_actions=(),
            source_format="markdown",
            raw=raw,
        )

    if not isinstance(parsed, dict):
        raise ValueError("Plan JSON must be an object.")

    step_id = compact_string(parsed.get("step_id") or parsed.get("id") or parsed.get("step"))
    title = compact_string(parsed.get("title") or parsed.get("name") or parsed.get("step_name"))
    objective = compact_string(parsed.get("objective") or parsed.get("goal") or parsed.get("summary"))
    risk_level = compact_string(parsed.get("risk_level") or parsed.get("risk") or "L1")
    phase = compact_string(parsed.get("phase") or parsed.get("current_phase") or "mock-planning")
    if not step_id:
        step_id = infer_step_id(json.dumps(parsed, sort_keys=True), path.stem)
    if not title:
        title = step_id
    if not objective:
        objective = title

    return StepPlan(
        path=path.resolve(),
        step_id=step_id,
        title=title,
        objective=objective,
        risk_level=risk_level,
        phase=phase,
        allowed_paths=tuple(compact_list(parsed.get("allowed_paths"))),
        forbidden_actions=tuple(compact_list(parsed.get("forbidden_actions"))),
        source_format="json",
        raw=parsed,
    )


def render_mock_prompt(plan: StepPlan) -> str:
    plan_json = json.dumps(plan.raw, indent=2, sort_keys=True)
    allowed = "\n".join(f"- {item}" for item in plan.allowed_paths) or "- none declared"
    forbidden = "\n".join(f"- {item}" for item in plan.forbidden_actions) or "- none declared"
    return "\n".join(
        [
            f"# Codex Prompt - {plan.step_id}",
            "",
            "## Objective",
            plan.objective,
            "",
            "## Operating Mode",
            "- generator_mode: mock",
            "- live_provider_calls: disabled",
            "- credential_reading: disabled",
            "- network_access: disabled",
            "",
            "## Step Context",
            f"- step_id: {plan.step_id}",
            f"- title: {plan.title}",
            f"- risk_level: {plan.risk_level}",
            f"- phase: {plan.phase}",
            f"- source_format: {plan.source_format}",
            "",
            "## Allowed Paths",
            allowed,
            "",
            "## Forbidden Actions",
            forbidden,
            "",
            "## Required Agent Behavior",
            "- Work locally and keep changes scoped to the declared plan.",
            "- Do not publish, merge, tag, release, or run uncontrolled external actions.",
            "- Use deterministic checks and report every warning explicitly.",
            "",
            "## Normalized Plan JSON",
            "```json",
            plan_json,
            "```",
            "",
        ]
    )


def write_text(path: Path, content: str) -> Path:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return resolved


def default_output_path(plan: StepPlan) -> Path:
    return repo_root() / "tmp" / "asf_gpt_prompt_generator" / f"{plan.step_id}-generated-prompt.md"


def generate_prompt_from_plan(
    plan: StepPlan,
    *,
    output_path: Path | None = None,
    mode: str = DEFAULT_MODE,
    allow_live: bool = False,
    selected_model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
) -> dict[str, Any]:
    mode = compact_string(mode) or DEFAULT_MODE
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if mode == "live":
        if not allow_live:
            raise ValueError("Live mode requested without explicit allow-live flag.")
        raise ValueError("Live mode is reserved for a future controlled step and is disabled here.")

    prompt = render_mock_prompt(plan)
    prompt_path = write_text(output_path or default_output_path(plan), prompt)
    return {
        "step_id": plan.step_id,
        "mode": "mock",
        "selected_model": selected_model,
        "provider": provider,
        "live_enabled": False,
        "prompt_path": str(prompt_path),
        "risk_level": plan.risk_level,
        "requires_alberto": False,
        "status": "PROMPT_READY",
        "next_action": "CODEX_DRY_RUN_READY",
        "source_plan_path": str(plan.path),
        "source_format": plan.source_format,
    }


def generate_prompt(
    plan_path: Path,
    *,
    output_path: Path | None = None,
    mode: str = DEFAULT_MODE,
    allow_live: bool = False,
    selected_model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
) -> dict[str, Any]:
    plan = load_plan(plan_path)
    return generate_prompt_from_plan(
        plan,
        output_path=output_path,
        mode=mode,
        allow_live=allow_live,
        selected_model=selected_model,
        provider=provider,
    )


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic ASF Codex prompts in mock mode.")
    parser.add_argument("--plan", required=True, help="Step plan JSON or Markdown path.")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=sorted(SUPPORTED_MODES), help="Generation mode.")
    parser.add_argument("--allow-live", action="store_true", help="Reserved future live gate; still disabled here.")
    parser.add_argument("--output", help="Generated prompt output path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model label recorded in mock output.")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER, help="Provider label recorded in mock output.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON.")
    return parser.parse_args(argv)


def blocked_packet(error: str, *, mode: str, plan_path: str) -> dict[str, Any]:
    return {
        "step_id": "",
        "mode": mode or DEFAULT_MODE,
        "selected_model": DEFAULT_MODEL,
        "provider": DEFAULT_PROVIDER,
        "live_enabled": False,
        "prompt_path": "",
        "risk_level": "UNKNOWN",
        "requires_alberto": True,
        "status": "PROMPT_BLOCKED",
        "next_action": "STOP",
        "source_plan_path": plan_path,
        "errors": [error],
    }


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        packet = generate_prompt(
            Path(args.plan),
            output_path=Path(args.output) if args.output else None,
            mode=args.mode,
            allow_live=bool(args.allow_live),
            selected_model=args.model,
            provider=args.provider,
        )
    except ValueError as exc:
        packet = blocked_packet(str(exc), mode=args.mode, plan_path=args.plan)
        print(render_json(packet), end="")
        return EXIT_INPUT_ERROR

    if args.json:
        print(render_json(packet), end="")
    else:
        print(packet["prompt_path"])
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
