from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0

DECISION_APPROVE_LOCAL_ONLY = "APPROVE_LOCAL_ONLY"
DECISION_NEEDS_HUMAN = "NEEDS_HUMAN"
DECISION_APPROVE_PUBLISH = "APPROVE_PUBLISH"
DECISION_BLOCKED = "BLOCKED"
DECISION_FAIL_CLOSED = "FAIL_CLOSED"

RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
PASS_STATUSES = {"PASS", "PASSED", "OK", "SUCCESS", "SUCCEEDED", "TRUE", "0"}
FAIL_STATUSES = {"FAIL", "FAILED", "ERROR", "BLOCKED", "NO_GO", "FALSE", "1"}


def compact_string(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text


def compact_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return []
    if isinstance(value, list | tuple):
        items: list[str] = []
        for item in value:
            text = compact_string(item)
            if text:
                items.append(text)
        return items
    text = compact_string(value)
    return [text] if text else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_string(*values: Any, fallback: str = "") -> str:
    for value in values:
        text = compact_string(value)
        if text:
            return text
    return fallback


def first_list(*values: Any) -> list[str]:
    for value in values:
        items = compact_list(value)
        if items:
            return items
    return []


def nested_dict(raw: dict[str, Any], *keys: str) -> dict[str, Any]:
    current: Any = raw
    for key in keys:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return as_dict(current)


def nested_value(raw: dict[str, Any], *keys: str) -> Any:
    current: Any = raw
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def normalize_gate(value: str) -> str:
    return value.strip().casefold()


def normalize_check_name(value: str) -> str:
    return " ".join(value.casefold().replace("\\", "/").split())


def extract_risk_container(raw: dict[str, Any]) -> dict[str, Any]:
    for key in ("risk_report", "risk_checkpoint", "risk_result"):
        value = raw.get(key)
        if isinstance(value, dict):
            return value
    if isinstance(raw.get("risk"), dict) or "risk_level" in raw:
        return raw
    return {}


def extract_risk(raw: dict[str, Any], risk_container: dict[str, Any]) -> dict[str, Any]:
    risk = risk_container.get("risk")
    if isinstance(risk, dict):
        return risk
    if "risk_level" in risk_container:
        return risk_container
    risk = raw.get("risk")
    return as_dict(risk)


def extract_gate(raw: dict[str, Any], risk_container: dict[str, Any]) -> dict[str, Any]:
    gate = risk_container.get("gate")
    if isinstance(gate, dict):
        return gate
    return as_dict(raw.get("gate"))


def extract_dry_run(raw: dict[str, Any], risk_container: dict[str, Any]) -> dict[str, Any]:
    dry_run = risk_container.get("dry_run")
    if isinstance(dry_run, dict):
        return dry_run
    return as_dict(raw.get("dry_run"))


def extract_step(raw: dict[str, Any]) -> str:
    return first_string(
        raw.get("step"),
        nested_value(raw, "request", "step"),
        nested_value(raw, "normalized_request", "step"),
        fallback="unknown",
    )


def extract_title(raw: dict[str, Any]) -> str:
    return first_string(
        raw.get("title"),
        raw.get("name"),
        nested_value(raw, "request", "title"),
        nested_value(raw, "normalized_request", "title"),
        fallback="Gate Decision Report",
    )


def extract_files_in_scope(raw: dict[str, Any]) -> list[str]:
    return first_list(
        raw.get("files_in_scope"),
        raw.get("allowed_scope"),
        raw.get("files"),
        raw.get("expected_files"),
        raw.get("files_changed"),
        nested_value(raw, "request", "allowed_scope"),
        nested_value(raw, "normalized_request", "allowed_scope"),
    )


def extract_checks_required(raw: dict[str, Any]) -> list[str]:
    return first_list(
        raw.get("checks_required"),
        raw.get("required_checks"),
        raw.get("checks"),
        raw.get("phase_a_checks"),
        nested_value(raw, "request", "checks"),
        nested_value(raw, "normalized_request", "checks"),
    )


def status_from_value(value: Any) -> str:
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    text = compact_string(value)
    if not text:
        return "UNKNOWN"
    upper = text.upper()
    if upper in PASS_STATUSES:
        return "PASS"
    if upper in FAIL_STATUSES:
        return "FAIL"
    if "PASS" in upper or "SUCC" in upper:
        return "PASS"
    if "FAIL" in upper or "ERROR" in upper or "BLOCK" in upper:
        return "FAIL"
    return "UNKNOWN"


def parse_check_string(value: str, index: int, required: list[str]) -> dict[str, str]:
    text = value.strip()
    name = text
    status = "UNKNOWN"
    if ":" in text:
        left, right = text.rsplit(":", 1)
        if status_from_value(right) != "UNKNOWN":
            name = left.strip()
            status = status_from_value(right)
    else:
        status = status_from_value(text)
        if status != "UNKNOWN" and index < len(required):
            name = required[index]
    return {"name": name, "status": status}


def normalize_check_results(value: Any, required: list[str]) -> list[dict[str, str]]:
    if value is None:
        return []
    if isinstance(value, dict):
        if any(key in value for key in ("name", "check", "command", "status", "result", "outcome", "passed")):
            name = first_string(value.get("name"), value.get("check"), value.get("command"))
            status = status_from_value(
                value.get("passed")
                if "passed" in value
                else first_string(value.get("status"), value.get("result"), value.get("outcome"), value.get("conclusion"))
            )
            return [{"name": name, "status": status}]
        results: list[dict[str, str]] = []
        for key, item in value.items():
            if isinstance(item, dict):
                nested = normalize_check_results(item, required)
                for result in nested:
                    if not result["name"]:
                        result["name"] = str(key)
                    results.append(result)
            else:
                results.append({"name": str(key), "status": status_from_value(item)})
        return results
    if isinstance(value, list | tuple):
        results = []
        for index, item in enumerate(value):
            if isinstance(item, dict):
                parsed = normalize_check_results(item, required)
                if parsed and not parsed[0]["name"] and index < len(required):
                    parsed[0]["name"] = required[index]
                results.extend(parsed)
            else:
                results.append(parse_check_string(str(item), index, required))
        return results
    if isinstance(value, str):
        return [parse_check_string(value, 0, required)]
    return []


def extract_checks_reported(raw: dict[str, Any], required: list[str]) -> list[dict[str, str]]:
    for key in ("checks_reported", "check_results", "verification_results", "reported_checks"):
        value = raw.get(key)
        results = normalize_check_results(value, required)
        if results:
            return results
    test_report = raw.get("test_report")
    if isinstance(test_report, dict):
        for key in ("checks_reported", "check_results", "verification_results"):
            results = normalize_check_results(test_report.get(key), required)
            if results:
                return results
    return []


def check_names_match(required: str, reported: str) -> bool:
    req = normalize_check_name(required)
    rep = normalize_check_name(reported)
    if not req or not rep:
        return False
    return req == rep or req in rep or rep in req


def evaluate_checks(required: list[str], reported: list[dict[str, str]]) -> dict[str, Any]:
    if not required:
        return {
            "status": "MISSING",
            "missing": ["No checks_required field was declared."],
            "failed": [],
            "unknown": [],
        }
    if not reported:
        return {
            "status": "MISSING",
            "missing": required,
            "failed": [],
            "unknown": [],
        }

    missing: list[str] = []
    failed: list[str] = []
    unknown: list[str] = []
    used: set[int] = set()
    for required_check in required:
        match_index = None
        for index, result in enumerate(reported):
            if index in used:
                continue
            if check_names_match(required_check, result.get("name", "")):
                match_index = index
                break
        if match_index is None:
            missing.append(required_check)
            continue
        used.add(match_index)
        result = reported[match_index]
        status = status_from_value(result.get("status"))
        if status == "FAIL":
            failed.append(required_check)
        elif status != "PASS":
            unknown.append(required_check)

    if failed:
        status = "FAILED"
    elif missing or unknown:
        status = "MISSING"
    else:
        status = "PASSED"
    return {"status": status, "missing": missing, "failed": failed, "unknown": unknown}


def extract_blockers(raw: dict[str, Any], risk_container: dict[str, Any]) -> list[str]:
    blockers = []
    blockers.extend(compact_list(raw.get("blockers")))
    blockers.extend(compact_list(risk_container.get("plan_blockers")))
    blockers.extend(compact_list(nested_value(raw, "independent_review", "blocking_findings")))
    blockers.extend(compact_list(nested_value(raw, "review", "blocking_findings")))
    return list(dict.fromkeys(blockers))


def extract_warnings(raw: dict[str, Any]) -> list[str]:
    warnings = []
    warnings.extend(compact_list(raw.get("warnings")))
    warnings.extend(compact_list(nested_value(raw, "independent_review", "warnings")))
    warnings.extend(compact_list(nested_value(raw, "review", "warnings")))
    return list(dict.fromkeys(warnings))


def extract_provided_gates(raw: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    gates = []
    gates.extend(compact_list(gate.get("provided_gates")))
    gates.extend(compact_list(raw.get("provided_gates")))
    gates.extend(compact_list(raw.get("declared_gates")))
    gates.extend(compact_list(raw.get("satisfied_gates")))
    gates.extend(compact_list(nested_value(raw, "request", "provided_gates")))
    gates.extend(compact_list(nested_value(raw, "normalized_request", "provided_gates")))
    return list(dict.fromkeys(gates))


def approval_declared(raw: dict[str, Any], gate_name: str, provided_gates: list[str], classifier_allowed: bool) -> bool:
    approvals = nested_dict(raw, "approvals")
    direct = raw.get(gate_name)
    nested = approvals.get(gate_name)
    if isinstance(direct, bool) and direct:
        return True
    if isinstance(nested, bool) and nested:
        return True
    normalized = {normalize_gate(item) for item in provided_gates}
    aliases = {
        "explicit_publish_approval": {"explicit_publish_approval", "approve_publish", "publish"},
        "elevated_manual_approval": {"elevated_manual_approval", "manual_approval", "double_confirmation"},
        "local_verification": {"local_verification", "verification", "verify", "pytest"},
    }
    if normalized.intersection(aliases.get(gate_name, {gate_name})):
        return True
    required_gate = first_string(raw.get("required_gate"), gate_name)
    return bool(classifier_allowed and required_gate == gate_name)


def fail_closed_packet(
    *,
    step: str = "unknown",
    title: str = "Gate Decision Report",
    reason: str,
    source_input_file: str | None = None,
) -> dict[str, Any]:
    return {
        "step": step,
        "title": title,
        "decision": DECISION_FAIL_CLOSED,
        "risk_level": "UNKNOWN",
        "required_gate": "elevated_manual_approval",
        "gate_status": "FAIL_CLOSED",
        "allowed": False,
        "fail_closed": True,
        "summary": "Input non valido o ambiguo: il report fallisce chiuso.",
        "files_in_scope": [],
        "checks_required": [],
        "checks_reported": [],
        "blockers": [reason],
        "warnings": [],
        "recommended_next_action": "Stop: correggere l'input e rieseguire il Gate Decision Report.",
        "human_approval_text": (
            "Input non valido o ambiguo. Procedura bloccata in modalita' fail-closed. "
            "Serve revisione manuale prima di qualunque azione."
        ),
        "machine_readable": {
            "schema_version": "1.0",
            "source_input_file": source_input_file,
            "classifier_allowed": False,
            "provided_gates": [],
            "checks_summary": {"status": "MISSING", "missing": [], "failed": [], "unknown": []},
            "no_operational_actions_executed": True,
            "publish_runner": "scripts/asf_publish_step.ps1",
        },
    }


def build_human_approval_text(
    *,
    risk_level: str,
    decision: str,
    required_gate: str,
    checks_status: str,
    recommended_next_action: str,
) -> str:
    checks_text = "I check locali risultano passati." if checks_status == "PASSED" else "L'evidence dei check locali non e' completa."
    if decision == DECISION_APPROVE_PUBLISH:
        return (
            f"Richiesta classificata {risk_level}. Sono coinvolte azioni di pubblicazione. "
            f"Per procedere e' presente approvazione esplicita di pubblicazione. {checks_text} "
            "Azione consigliata: usare il runner `scripts/asf_publish_step.ps1` con `-ApprovePublish`."
        )
    if risk_level == "L4":
        return (
            "Richiesta classificata L4. Sono presenti azioni distruttive, deploy, segreti "
            "o side effect esterni. Procedura bloccata in modalita' fail-closed. "
            "Serve approvazione manuale elevata e revisione separata."
        )
    if decision == DECISION_NEEDS_HUMAN:
        return (
            f"Richiesta classificata {risk_level}. Gate richiesto: `{required_gate}`. "
            f"{checks_text} Azione consigliata: {recommended_next_action}"
        )
    if decision == DECISION_BLOCKED:
        return (
            f"Richiesta classificata {risk_level}. Sono presenti blocker o check falliti. "
            "Procedura bloccata: correggere i blocker e rieseguire le verifiche."
        )
    return (
        f"Richiesta classificata {risk_level}. Il pacchetto e' coerente per una decisione locale. "
        f"Azione consigliata: {recommended_next_action}"
    )


def build_approval_packet(raw: Any, *, source_input_file: str | None = None) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return fail_closed_packet(reason="Input JSON must be an object.", source_input_file=source_input_file)

    risk_container = extract_risk_container(raw)
    risk = extract_risk(raw, risk_container)
    gate = extract_gate(raw, risk_container)
    dry_run = extract_dry_run(raw, risk_container)
    step = extract_step(raw)
    title = extract_title(raw)

    risk_level = first_string(risk.get("risk_level"), raw.get("risk_level")).upper()
    if risk_level not in RISK_LEVELS:
        return fail_closed_packet(
            step=step,
            title=title,
            reason="Missing or unknown risk_level; refusing to infer safety.",
            source_input_file=source_input_file,
        )

    required_gate = first_string(risk.get("required_gate"), gate.get("required_gate"), raw.get("required_gate"), fallback="unknown")
    classifier_allowed = bool(risk.get("allowed", False))
    source_fail_closed = bool(risk.get("fail_closed", False) or dry_run.get("fail_closed", False) or raw.get("fail_closed", False))
    files_in_scope = extract_files_in_scope(raw)
    checks_required = extract_checks_required(raw)
    checks_reported = extract_checks_reported(raw, checks_required)
    checks_summary = evaluate_checks(checks_required, checks_reported)
    blockers = extract_blockers(raw, risk_container)
    warnings = extract_warnings(raw)
    provided_gates = extract_provided_gates(raw, gate)

    if source_fail_closed:
        blockers.append("Source risk evidence declares fail_closed.")
        decision = DECISION_FAIL_CLOSED
        gate_status = "FAIL_CLOSED"
    elif blockers:
        decision = DECISION_BLOCKED
        gate_status = "BLOCKED"
    elif risk_level in {"L0", "L1"}:
        if checks_summary["failed"]:
            decision = DECISION_BLOCKED
            gate_status = "BLOCKED"
            blockers.extend(f"Reported check failed: {item}" for item in checks_summary["failed"])
        else:
            decision = DECISION_APPROVE_LOCAL_ONLY
            gate_status = "NOT_REQUIRED" if required_gate == "none" else "SATISFIED"
    elif risk_level == "L2":
        if checks_summary["failed"]:
            decision = DECISION_BLOCKED
            gate_status = "BLOCKED"
            blockers.extend(f"Required local check failed: {item}" for item in checks_summary["failed"])
        elif checks_summary["status"] != "PASSED":
            decision = DECISION_NEEDS_HUMAN
            gate_status = "MISSING"
            warnings.append("Local verification evidence is missing or incomplete.")
        else:
            decision = DECISION_APPROVE_LOCAL_ONLY
            gate_status = "SATISFIED"
            if not classifier_allowed:
                warnings.append("Classifier gate was not declared satisfied; check evidence is reported separately.")
    elif risk_level == "L3":
        explicit_publish = approval_declared(raw, "explicit_publish_approval", provided_gates, classifier_allowed)
        if checks_summary["failed"]:
            decision = DECISION_BLOCKED
            gate_status = "BLOCKED"
            blockers.extend(f"Required pre-publish check failed: {item}" for item in checks_summary["failed"])
        elif checks_summary["status"] != "PASSED":
            decision = DECISION_NEEDS_HUMAN
            gate_status = "MISSING"
            warnings.append("Pre-publish local verification evidence is missing or incomplete.")
        elif not explicit_publish:
            decision = DECISION_NEEDS_HUMAN
            gate_status = "MISSING"
            blockers.append("Missing explicit_publish_approval for L3 publication intent.")
        else:
            decision = DECISION_APPROVE_PUBLISH
            gate_status = "SATISFIED"
    else:
        decision = DECISION_BLOCKED
        gate_status = "BLOCKED"
        blockers.append("L4 requires elevated manual approval and separate review.")
        if approval_declared(raw, "elevated_manual_approval", provided_gates, classifier_allowed):
            warnings.append("Elevated approval is declared, but L4 remains blocked for separate review.")

    allowed = decision in {DECISION_APPROVE_LOCAL_ONLY, DECISION_APPROVE_PUBLISH}
    fail_closed = decision == DECISION_FAIL_CLOSED
    if decision == DECISION_APPROVE_PUBLISH:
        recommended_next_action = "Usare `scripts/asf_publish_step.ps1` con `-ApprovePublish` dopo review umana."
    elif decision == DECISION_APPROVE_LOCAL_ONLY:
        recommended_next_action = "Procedere con review locale; nessuna pubblicazione e' eseguita da questo report."
    elif decision == DECISION_NEEDS_HUMAN and risk_level == "L3":
        recommended_next_action = "Ottenere approvazione esplicita di pubblicazione e verifiche locali complete."
    elif decision == DECISION_NEEDS_HUMAN:
        recommended_next_action = "Completare le verifiche locali richieste e rieseguire il report."
    elif decision == DECISION_BLOCKED:
        recommended_next_action = "Correggere blocker e warning critici prima di procedere."
    else:
        recommended_next_action = "Stop: input o evidence non sicuri, rieseguire con dati completi."

    summary = f"Step {step} classificato {risk_level}; decisione {decision}; gate {required_gate}: {gate_status}."
    human_approval_text = build_human_approval_text(
        risk_level=risk_level,
        decision=decision,
        required_gate=required_gate,
        checks_status=checks_summary["status"],
        recommended_next_action=recommended_next_action,
    )

    return {
        "step": step,
        "title": title,
        "decision": decision,
        "risk_level": risk_level,
        "required_gate": required_gate,
        "gate_status": gate_status,
        "allowed": allowed,
        "fail_closed": fail_closed,
        "summary": summary,
        "files_in_scope": files_in_scope,
        "checks_required": checks_required,
        "checks_reported": checks_reported,
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": list(dict.fromkeys(warnings)),
        "recommended_next_action": recommended_next_action,
        "human_approval_text": human_approval_text,
        "machine_readable": {
            "schema_version": "1.0",
            "source_input_file": source_input_file,
            "classifier_allowed": classifier_allowed,
            "provided_gates": provided_gates,
            "checks_summary": checks_summary,
            "no_operational_actions_executed": True,
            "publish_runner": "scripts/asf_publish_step.ps1",
            "decision_values": [
                DECISION_APPROVE_LOCAL_ONLY,
                DECISION_NEEDS_HUMAN,
                DECISION_APPROVE_PUBLISH,
                DECISION_BLOCKED,
                DECISION_FAIL_CLOSED,
            ],
        },
    }


def read_packet_input(path: Path) -> dict[str, Any]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return fail_closed_packet(reason=f"Unable to read input file: {exc}", source_input_file=str(path))
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return fail_closed_packet(reason=f"Input file is not valid JSON: {exc.msg}", source_input_file=str(path))
    return build_approval_packet(raw, source_input_file=str(path))


def bullets(items: list[Any], *, fallback: str = "none") -> str:
    if not items:
        return f"- {fallback}"
    lines = []
    for item in items:
        if isinstance(item, dict):
            lines.append("- " + json.dumps(item, sort_keys=True))
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def render_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def render_markdown(packet: dict[str, Any]) -> str:
    return f"""# Gate Decision Report and Human Approval Packet

## Summary

- step: `{packet["step"]}`
- title: `{packet["title"]}`
- decision: `{packet["decision"]}`
- allowed: `{str(packet["allowed"]).lower()}`
- fail-closed: `{str(packet["fail_closed"]).lower()}`

{packet["summary"]}

## Risk

- risk_level: `{packet["risk_level"]}`
- required_gate: `{packet["required_gate"]}`

## Gate

- gate_status: `{packet["gate_status"]}`
- no operational actions executed: `true`

## Files in scope

{bullets(packet["files_in_scope"])}

## Checks required

{bullets(packet["checks_required"])}

## Checks reported

{bullets(packet["checks_reported"])}

## Blockers

{bullets(packet["blockers"])}

## Warnings

{bullets(packet["warnings"])}

## Human approval text

{packet["human_approval_text"]}

## Next action

{packet["recommended_next_action"]}

## Machine-readable

```json
{json.dumps(packet["machine_readable"], indent=2, sort_keys=True)}
```
"""


def render_text(packet: dict[str, Any]) -> str:
    return (
        f"decision: {packet['decision']}\n"
        f"risk_level: {packet['risk_level']}\n"
        f"required_gate: {packet['required_gate']}\n"
        f"gate_status: {packet['gate_status']}\n"
        f"allowed: {str(packet['allowed']).lower()}\n"
        f"fail_closed: {str(packet['fail_closed']).lower()}\n"
        f"recommended_next_action: {packet['recommended_next_action']}\n"
    )


def write_outputs(packet: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "approval_packet.json").write_text(render_json(packet), encoding="utf-8", newline="\n")
    (out_dir / "approval_packet.md").write_text(render_markdown(packet), encoding="utf-8", newline="\n")
    (out_dir / "approval_packet.txt").write_text(render_text(packet), encoding="utf-8", newline="\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an ASF Gate Decision Report and Human Approval Packet from dry-run/risk JSON evidence.",
    )
    parser.add_argument("--input-file", required=True, help="Input JSON evidence from or compatible with the dry-run runner.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report.")
    parser.add_argument("--text", action="store_true", help="Print compact text.")
    parser.add_argument("--out-dir", help="Write JSON, Markdown and compact text files to this directory.")
    return parser.parse_args(argv)


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    packet = read_packet_input(Path(args.input_file))
    if args.out_dir:
        write_outputs(packet, Path(args.out_dir))

    printed = False
    if args.json:
        print(render_json(packet), end="")
        printed = True
    if args.markdown:
        print(render_markdown(packet), end="")
        printed = True
    if args.text:
        print(render_text(packet), end="")
        printed = True
    if not printed and not args.out_dir:
        print(render_text(packet), end="")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
