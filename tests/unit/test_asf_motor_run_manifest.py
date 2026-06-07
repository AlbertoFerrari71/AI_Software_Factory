from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_motor_run_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_motor_run_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def complete_evidence_dir(base: Path) -> Path:
    evidence = base / "evidence"
    write_json(
        evidence / "input_step.json",
        {
            "step": "0700-smoke",
            "scenario": "code-unit-to-ready-to-publish",
            "checks": ["python -m pytest tests/unit/test_example_component.py"],
        },
    )
    write_json(evidence / "risk_report.json", {"risk_level": "L2", "allowed": True})
    write_json(evidence / "dry_run_report.json", {"risk_checkpoint": {"status": "PASS"}})
    write_json(
        evidence / "gate_decision_packet.json",
        {
            "decision": "APPROVE_LOCAL_ONLY",
            "allowed": True,
            "checks_required": ["python -m pytest tests/unit/test_example_component.py"],
            "checks_reported": [
                {
                    "name": "unit tests",
                    "status": "PASSED",
                    "command": "python -m pytest tests/unit/test_example_component.py",
                    "exit_code": 0,
                    "required": True,
                    "description": "Targeted smoke unit test.",
                }
            ],
        },
    )
    write_json(evidence / "verification_profile.json", {"profile": "code-unit"})
    write_json(evidence / "publish_config.json", {"verification_profile": "code-unit"})
    write_json(evidence / "state_before.json", {"current_state": "LOCAL_VERIFIED"})
    write_json(evidence / "state_after.json", {"current_state": "READY_TO_PUBLISH"})
    (evidence / "evidence_summary.md").write_text("# Summary\n", encoding="utf-8")
    write_json(
        evidence / "evidence_summary.json",
        {
            "scenario": "code-unit-to-ready-to-publish",
            "status": "ok",
            "blockers": [],
            "warnings": ["Synthetic smoke evidence."],
        },
    )
    return evidence


def ready_input_payload() -> dict[str, object]:
    return {
        "run_id": "sample-ready-run",
        "created_at": "2026-06-07T12:00:00Z",
        "step": "0710-sample",
        "scenario": "ready-input",
        "status": "ready_to_publish",
        "decision": "READY_TO_PUBLISH",
        "risk": {"risk_level": "L2"},
        "gate": {"decision": "APPROVE_LOCAL_ONLY"},
        "verification_profile": {"profile": "code-unit"},
        "state": {"after": {"current_state": "READY_TO_PUBLISH"}},
        "publish_config": {"verification_profile": "code-unit"},
        "artifacts": [
            {
                "name": "input_step",
                "path": "embedded/input_step.json",
                "kind": "input",
                "exists": True,
                "size_bytes": 10,
                "sha256": "0" * 64,
                "required": True,
                "description": "Embedded sample artifact.",
            }
        ],
        "checks": [
            {
                "name": "unit tests",
                "status": "PASSED",
                "command": "python -m pytest tests/unit/test_example_component.py",
                "exit_code": 0,
                "required": True,
                "description": "Sample passing check.",
            }
        ],
        "warnings": [],
        "blockers": [],
        "fail_closed": False,
    }


def test_manifest_created_from_complete_evidence_dir(tmp_path: Path) -> None:
    module = load_module()
    evidence = complete_evidence_dir(tmp_path)
    out_dir = tmp_path / "manifest"

    code = module.run(
        [
            "--evidence-dir",
            str(evidence),
            "--step",
            "0700-smoke",
            "--scenario",
            "code-unit-to-ready-to-publish",
            "--out-dir",
            str(out_dir),
            "--json",
        ]
    )

    manifest = read_json(out_dir / "motor_run_manifest.json")
    assert code == 0
    assert manifest["schema_version"] == module.SCHEMA_VERSION
    assert manifest["decision"] == "READY_TO_PUBLISH"
    assert manifest["status"] == "ready_to_publish"
    assert manifest["state"]["current_state"] == "READY_TO_PUBLISH"
    assert (out_dir / "motor_run_summary.md").is_file()


def test_manifest_created_from_input_json(tmp_path: Path) -> None:
    module = load_module()
    input_file = tmp_path / "ready.json"
    write_json(input_file, ready_input_payload())

    code = module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out"), "--markdown"])

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert code == 0
    assert manifest["run_id"] == "sample-ready-run"
    assert manifest["decision"] == "READY_TO_PUBLISH"
    assert "sample-ready-run" in (tmp_path / "out" / "motor_run_summary.md").read_text(encoding="utf-8")


def test_artifact_sha256_is_calculated_for_existing_file(tmp_path: Path) -> None:
    module = load_module()
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("hello manifest\n", encoding="utf-8")
    input_file = tmp_path / "input.json"
    payload = ready_input_payload()
    payload["artifacts"] = [
        {
            "name": "real_artifact",
            "path": "artifact.txt",
            "kind": "text",
            "required": True,
            "description": "Real temporary artifact.",
        }
    ]
    write_json(input_file, payload)

    assert module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out")]) == 0

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    item = manifest["artifacts"][0]
    expected = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert item["exists"] is True
    assert item["sha256"] == expected


def test_missing_required_artifact_produces_incomplete(tmp_path: Path) -> None:
    module = load_module()
    evidence = complete_evidence_dir(tmp_path)
    (evidence / "publish_config.json").unlink()

    assert module.run(["--evidence-dir", str(evidence), "--step", "0700-smoke", "--out-dir", str(tmp_path / "out")]) == 0

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert manifest["decision"] == "INCOMPLETE"
    assert "publish_config" in manifest["machine_readable"]["required_artifacts_missing"]


def test_fail_closed_input_produces_fail_closed_decision(tmp_path: Path) -> None:
    module = load_module()
    payload = ready_input_payload()
    payload["run_id"] = "sample-fail-closed"
    payload["fail_closed"] = True
    payload["decision"] = "FAIL_CLOSED"
    input_file = tmp_path / "fail_closed.json"
    write_json(input_file, payload)

    assert module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out")]) == 0

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert manifest["decision"] == "FAIL_CLOSED"
    assert manifest["status"] == "fail_closed"


def test_blocker_input_produces_blocked_decision(tmp_path: Path) -> None:
    module = load_module()
    payload = ready_input_payload()
    payload["run_id"] = "sample-blocked"
    payload["blockers"] = ["Manual approval missing."]
    input_file = tmp_path / "blocked.json"
    write_json(input_file, payload)

    assert module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out")]) == 0

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert manifest["decision"] == "BLOCKED"
    assert manifest["status"] == "blocked"


def test_markdown_contains_key_manifest_sections(tmp_path: Path) -> None:
    module = load_module()
    input_file = tmp_path / "ready.json"
    write_json(input_file, ready_input_payload())

    assert module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out")]) == 0

    markdown = (tmp_path / "out" / "motor_run_summary.md").read_text(encoding="utf-8")
    assert "sample-ready-run" in markdown
    assert "status" in markdown.casefold()
    assert "decision" in markdown.casefold()
    assert "artifacts" in markdown.casefold()
    assert "recommended next action" in markdown.casefold()


def test_output_json_is_valid_and_bridge_uses_temporary_root(tmp_path: Path) -> None:
    module = load_module()
    input_file = tmp_path / "ready.json"
    bridge_root = tmp_path / "bridge"
    write_json(input_file, ready_input_payload())

    code = module.run(
        [
            "--input-file",
            str(input_file),
            "--out-dir",
            str(tmp_path / "out"),
            "--write-bridge",
            "--bridge-root",
            str(bridge_root),
        ]
    )

    assert code == 0
    read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert (bridge_root / "LAST-Run_Manifest.json").is_file()
    assert (bridge_root / "LAST-Run_Summary.md").is_file()
    assert (bridge_root / "LAST-Output_Completo.txt").is_file()
    assert list(bridge_root.glob("0710-Run_Manifest_*.json"))
    assert str(bridge_root).startswith(str(tmp_path))


def test_corrupt_input_json_writes_fail_closed_manifest(tmp_path: Path) -> None:
    module = load_module()
    input_file = tmp_path / "corrupt.json"
    input_file.write_text("{not-json", encoding="utf-8")

    code = module.run(["--input-file", str(input_file), "--out-dir", str(tmp_path / "out")])

    manifest = read_json(tmp_path / "out" / "motor_run_manifest.json")
    assert code == module.EXIT_INPUT_ERROR
    assert manifest["decision"] == "FAIL_CLOSED"
    assert manifest["fail_closed"] is True
    assert manifest["blockers"]
