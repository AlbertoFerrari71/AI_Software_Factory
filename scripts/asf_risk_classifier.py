from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2


class RiskLevel(Enum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4


@dataclass(frozen=True)
class RiskRule:
    rule_id: str
    level: RiskLevel
    source: str
    patterns: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ClassifierInput:
    text_items: tuple[str, ...] = ()
    file_items: tuple[str, ...] = ()
    command_items: tuple[str, ...] = ()
    keyword_items: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchedRule:
    rule_id: str
    risk_level: str
    source: str
    matched_value: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "risk_level": self.risk_level,
            "source": self.source,
            "matched_value": self.matched_value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class GatePolicy:
    required_gate: str
    gate_aliases: tuple[str, ...]
    default_allowed: bool
    next_action: str


GATE_POLICIES: dict[RiskLevel, GatePolicy] = {
    RiskLevel.L0: GatePolicy(
        required_gate="none",
        gate_aliases=("none",),
        default_allowed=True,
        next_action="Proceed with ordinary review and keep evidence if useful.",
    ),
    RiskLevel.L1: GatePolicy(
        required_gate="implicit_or_local_approval",
        gate_aliases=("implicit_or_local_approval", "local_approval", "implicit"),
        default_allowed=True,
        next_action="Proceed locally and keep generated artifacts scoped.",
    ),
    RiskLevel.L2: GatePolicy(
        required_gate="local_verification",
        gate_aliases=("local_verification", "verification", "verify", "pytest"),
        default_allowed=False,
        next_action="Run local verification before proceeding.",
    ),
    RiskLevel.L3: GatePolicy(
        required_gate="explicit_publish_approval",
        gate_aliases=("explicit_publish_approval", "approve_publish", "publish"),
        default_allowed=False,
        next_action="Stop until explicit publish approval is present.",
    ),
    RiskLevel.L4: GatePolicy(
        required_gate="elevated_manual_approval",
        gate_aliases=("elevated_manual_approval", "manual_approval", "double_confirmation"),
        default_allowed=False,
        next_action="Stop and require elevated manual approval, dry-run evidence and rollback planning.",
    ),
}


RULES: tuple[RiskRule, ...] = (
    RiskRule(
        "l4_destructive_action",
        RiskLevel.L4,
        "any",
        (
            r"\bdelete\b",
            r"\bremove\b",
            r"\berase\b",
            r"\bwipe\b",
            r"\bdestroy\b",
            r"\bpurge\b",
            r"\bdrop\s+table\b",
            r"\btruncate\b",
            r"\brm\s+-rf\b",
            r"\breset\s+--hard\b",
            r"\bclean\s+-fd\b",
            r"\bforce\s+push\b",
        ),
        "destructive or irreversible action signal",
    ),
    RiskRule(
        "l4_deploy_production_or_release",
        RiskLevel.L4,
        "any",
        (
            r"\bdeploy\b",
            r"\bproduction\b",
            r"\bprod\b",
            r"\brelease\s+publish\b",
            r"\bpublish\s+release\b",
            r"\bgo\s+live\b",
        ),
        "deployment, release or production impact signal",
    ),
    RiskRule(
        "l4_secret_or_credential",
        RiskLevel.L4,
        "any",
        (
            r"\bsecret\b",
            r"\bsecrets\b",
            r"\bapi\s*key\b",
            r"\btoken\b",
            r"\bcredential\b",
            r"\bcredentials\b",
            r"\bpassword\b",
            r"\bprivate\s+key\b",
            r"\.env\b",
        ),
        "secret, credential or private data signal",
    ),
    RiskRule(
        "l4_external_side_effect",
        RiskLevel.L4,
        "any",
        (
            r"\blive\s+provider\b",
            r"\bexternal\s+api\b",
            r"\bnetwork\s+call\b",
            r"\bhttp\s+request\b",
            r"\bwebhook\b",
            r"\bsmtp\b",
            r"\bsend\s+email\b",
            r"\bupload\b",
            r"\bexternal\s+side\s+effect",
            r"\bopenai\s+live\b",
        ),
        "external side effect, live provider or network signal",
    ),
    RiskRule(
        "l4_merge_action",
        RiskLevel.L4,
        "any",
        (
            r"\bmerge\b",
            r"\bauto\s+merge\b",
            r"\bmerge\s+pr\b",
            r"\bpr\s+merge\b",
            r"\bgh\s+pr\s+merge\b",
            r"\bgit\s+merge\b",
        ),
        "merge action signal",
    ),
    RiskRule(
        "l3_repository_publication",
        RiskLevel.L3,
        "any",
        (
            r"\bcommit\b",
            r"\bpush\b",
            r"\bpull\s+request\b",
            r"\bopen\s+pr\b",
            r"\bcreate\s+pr\b",
            r"\bpr\s+create\b",
            r"\bgh\s+pr\s+create\b",
            r"\bgit\s+commit\b",
            r"\bgit\s+push\b",
            r"\bbranch\s+publish\b",
            r"\brepository\s+publication\b",
        ),
        "repository publication action signal",
    ),
    RiskRule(
        "l3_workflow_security_or_dependency_surface",
        RiskLevel.L3,
        "any",
        (
            r"\bgithub\s+actions\b",
            r"\bci\b",
            r"\bworkflow\b",
            r"\bbranch\s+protection\b",
            r"\bruleset\b",
            r"\bdependency\b",
            r"\bdependencies\b",
            r"\bpyproject\b",
            r"\bpackage\s+manager\b",
        ),
        "workflow, security or dependency surface signal",
    ),
    RiskRule(
        "l4_dependency_install_command",
        RiskLevel.L4,
        "command",
        (
            r"\bpip\s+install\b",
            r"\bnpm\s+install\b",
            r"\bcargo\s+install\b",
            r"\bpoetry\s+add\b",
        ),
        "dependency install command may perform external side effects",
    ),
    RiskRule(
        "l3_sensitive_file_path",
        RiskLevel.L3,
        "file",
        (
            r"^\.github/workflows/",
            r"^policies/",
            r"(^|/)AGENTS\.md$",
            r"asf_publish_step\.ps1$",
        ),
        "sensitive workflow, policy or publication runner path",
    ),
    RiskRule(
        "l2_source_or_test_change",
        RiskLevel.L2,
        "file",
        (
            r"^src/",
            r"^scripts/.*\.(py|ps1)$",
            r"^tests/",
            r"\.py$",
            r"\.ps1$",
        ),
        "source or test change without external side effect",
    ),
    RiskRule(
        "l2_code_change_text",
        RiskLevel.L2,
        "text",
        (
            r"\bcode\b",
            r"\bsource\b",
            r"\bscript\b",
            r"\btest\b",
            r"\btests\b",
            r"\bimplement\b",
            r"\brefactor\b",
        ),
        "code, source, script or test change signal",
    ),
    RiskRule(
        "l1_local_artifact_or_example",
        RiskLevel.L1,
        "any",
        (
            r"\bexample\b",
            r"\bexamples\b",
            r"\bsample\b",
            r"\bartifact\b",
            r"\bartifacts\b",
            r"\bdry-run\b",
            r"\bdry\s+run\b",
            r"\btmp/",
            r"^examples/",
        ),
        "local generated artifact, sample or dry-run signal",
    ),
    RiskRule(
        "l1_local_verification_command",
        RiskLevel.L1,
        "command",
        (
            r"\bpython\s+-m\s+pytest\b",
            r"\bpytest\b",
            r"\bdiff\s+--check\b",
            r"\bstatus\s+--short\b",
            r"\bverify\.ps1\b",
            r"\bcheck_workflow_health\.py\b",
        ),
        "local verification command signal",
    ),
    RiskRule(
        "l0_docs_readonly_noop",
        RiskLevel.L0,
        "any",
        (
            r"\bdocs?\s+only\b",
            r"\bdocumentation\b",
            r"\bread-only\b",
            r"\bread\s+only\b",
            r"\bno-op\b",
            r"\bnoop\b",
            r"\binspect\b",
            r"\banalyze\b",
            r"\bREADME\.md\b",
            r"\bCHANGELOG\.md\b",
            r"^docs/",
            r"\.md$",
        ),
        "documentation, read-only or no-op signal",
    ),
)


def normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def compact_items(items: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    compacted = []
    for item in items:
        if item is None:
            continue
        value = str(item).strip()
        if value:
            compacted.append(value)
    return tuple(compacted)


def risk_sort_key(level: RiskLevel) -> int:
    return level.value


def compile_sources(input_data: ClassifierInput) -> dict[str, tuple[str, ...]]:
    text = compact_items(input_data.text_items)
    files = tuple(normalize_path(item) for item in compact_items(input_data.file_items))
    commands = compact_items(input_data.command_items)
    keywords = compact_items(input_data.keyword_items)
    all_items = text + files + commands + keywords
    return {
        "text": text,
        "file": files,
        "command": commands,
        "keyword": keywords,
        "any": all_items,
    }


def match_rule(rule: RiskRule, sources: dict[str, tuple[str, ...]]) -> list[MatchedRule]:
    values = sources.get(rule.source, ()) if rule.source != "any" else sources["any"]
    matches: list[MatchedRule] = []
    for value in values:
        candidate = normalize_path(value).casefold() if rule.source == "file" else value.casefold()
        for pattern in rule.patterns:
            if re.search(pattern, candidate, flags=re.IGNORECASE):
                matches.append(
                    MatchedRule(
                        rule_id=rule.rule_id,
                        risk_level=rule.level.name,
                        source=rule.source,
                        matched_value=value,
                        reason=rule.reason,
                    )
                )
                break
    return matches


def gate_satisfied(policy: GatePolicy, provided_gates: set[str]) -> bool:
    if policy.default_allowed:
        return True
    normalized = {gate.strip().casefold() for gate in provided_gates if gate.strip()}
    return any(alias.casefold() in normalized for alias in policy.gate_aliases)


def result_for_level(
    *,
    level: RiskLevel,
    matches: list[MatchedRule],
    fail_closed: bool,
    reasons: list[str],
    provided_gates: set[str],
) -> dict[str, Any]:
    policy = GATE_POLICIES[level]
    allowed = False if fail_closed else gate_satisfied(policy, provided_gates)
    next_action = (
        "Stop for human review because the input is incomplete or not recognized."
        if fail_closed
        else policy.next_action
    )
    return {
        "risk_level": level.name,
        "allowed": allowed,
        "required_gate": policy.required_gate,
        "reasons": reasons,
        "matched_rules": [match.as_dict() for match in matches],
        "fail_closed": fail_closed,
        "recommended_next_action": next_action,
    }


def classify(input_data: ClassifierInput, *, provided_gates: set[str] | None = None) -> dict[str, Any]:
    provided_gates = provided_gates or set()
    sources = compile_sources(input_data)
    if not sources["any"]:
        match = MatchedRule(
            rule_id="fail_closed_empty_input",
            risk_level=RiskLevel.L4.name,
            source="any",
            matched_value="",
            reason="input is empty or incomplete",
        )
        return result_for_level(
            level=RiskLevel.L4,
            matches=[match],
            fail_closed=True,
            reasons=["Input is empty or incomplete; classifier fails closed."],
            provided_gates=provided_gates,
        )

    matches: list[MatchedRule] = []
    for rule in RULES:
        matches.extend(match_rule(rule, sources))

    if not matches:
        match = MatchedRule(
            rule_id="fail_closed_unrecognized_input",
            risk_level=RiskLevel.L4.name,
            source="any",
            matched_value=" | ".join(sources["any"])[:240],
            reason="input did not match a known safe rule",
        )
        return result_for_level(
            level=RiskLevel.L4,
            matches=[match],
            fail_closed=True,
            reasons=["Input is not recognized; classifier fails closed."],
            provided_gates=provided_gates,
        )

    max_level = max((RiskLevel[match.risk_level] for match in matches), key=risk_sort_key)
    reasons = sorted({match.reason for match in matches if RiskLevel[match.risk_level] == max_level})
    return result_for_level(
        level=max_level,
        matches=matches,
        fail_closed=False,
        reasons=reasons,
        provided_gates=provided_gates,
    )


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


def list_from_json_field(raw: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    collected: list[str] = []
    for name in names:
        if name in raw:
            collected.extend(collect_string_values(raw[name]))
    return compact_items(collected)


def looks_like_file_path(value: str) -> bool:
    normalized = normalize_path(value)
    return (
        "/" in normalized
        or normalized.endswith((".md", ".py", ".ps1", ".json", ".yaml", ".yml", ".toml", ".txt"))
    )


def input_from_json(raw: dict[str, Any]) -> ClassifierInput:
    text_items = list_from_json_field(
        raw,
        (
            "text",
            "description",
            "summary",
            "objective",
            "title",
            "step_description",
            "notes",
        ),
    )
    file_items = list_from_json_field(
        raw,
        (
            "files",
            "file_paths",
            "files_changed",
            "modified_files",
            "expected_files",
        ),
    )
    command_items = list_from_json_field(
        raw,
        (
            "commands",
            "proposed_commands",
            "phase_a_checks",
            "phase_b_commands",
            "phase_c_checks",
        ),
    )
    keyword_items = list_from_json_field(
        raw,
        (
            "keywords",
            "actions",
            "operation_keywords",
            "forbidden_actions",
        ),
    )

    generic = [
        item
        for item in collect_string_values(raw)
        if item not in text_items and item not in file_items and item not in command_items and item not in keyword_items
    ]
    extra_files = [item for item in generic if looks_like_file_path(item)]
    extra_text = [item for item in generic if not looks_like_file_path(item)]
    return ClassifierInput(
        text_items=compact_items(list(text_items) + extra_text),
        file_items=compact_items(list(file_items) + extra_files),
        command_items=command_items,
        keyword_items=keyword_items,
    )


def merge_inputs(left: ClassifierInput, right: ClassifierInput) -> ClassifierInput:
    return ClassifierInput(
        text_items=left.text_items + right.text_items,
        file_items=left.file_items + right.file_items,
        command_items=left.command_items + right.command_items,
        keyword_items=left.keyword_items + right.keyword_items,
    )


def read_input_file(path: Path) -> ClassifierInput:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {path}: {exc}") from exc

    try:
        raw_json = json.loads(raw_text)
    except json.JSONDecodeError:
        return ClassifierInput(text_items=(raw_text,))

    if isinstance(raw_json, dict):
        return input_from_json(raw_json)
    if isinstance(raw_json, list):
        return ClassifierInput(text_items=tuple(collect_string_values(raw_json)))
    return ClassifierInput(text_items=tuple(collect_string_values(raw_json)))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify ASF step risk and return a fail-closed gate policy decision.",
    )
    parser.add_argument("--text", action="append", default=[], help="Text to classify. Can be passed more than once.")
    parser.add_argument("--input-file", help="JSON or text file to classify.")
    parser.add_argument("--gate", action="append", default=[], help="Provided gate token, such as local_verification.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser.parse_args(argv)


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"risk_level: {result['risk_level']}",
        f"allowed: {str(result['allowed']).lower()}",
        f"required_gate: {result['required_gate']}",
        f"fail_closed: {str(result['fail_closed']).lower()}",
        f"recommended_next_action: {result['recommended_next_action']}",
        "reasons:",
    ]
    lines.extend(f"- {reason}" for reason in result["reasons"])
    lines.append("matched_rules:")
    for match in result["matched_rules"]:
        lines.append(f"- {match['rule_id']} ({match['risk_level']}): {match['matched_value']}")
    return "\n".join(lines) + "\n"


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    input_data = ClassifierInput(text_items=compact_items(args.text))
    if args.input_file:
        try:
            input_data = merge_inputs(input_data, read_input_file(Path(args.input_file)))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_INPUT_ERROR

    result = classify(input_data, provided_gates=set(args.gate))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result), end="")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
