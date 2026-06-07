from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_e2e_mvp_smoke.py"
PUBLISH_RUNNER = ROOT / "scripts" / "asf_publish_step.ps1"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_e2e_mvp_smoke", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_positive_scenario_produces_complete_evidence_pack(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_positive(tmp_path / "out", write_bridge=False, bridge_root=tmp_path / "bridge")

    assert result.exit_code == 0
    assert result.status == "ok"
    summary = read_json(tmp_path / "out" / "evidence_summary.json")
    assert summary["status"] == "ok"
    assert summary["final_state"] == "READY_TO_PUBLISH"
    assert summary["ready_config_produced"] is True

    expected = [
        "input_step.json",
        "risk_report.json",
        "dry_run_report.json",
        "gate_decision_packet.json",
        "verification_profile.json",
        "publish_config.json",
        "state_before.json",
        "state_after.json",
        "evidence_summary.md",
        "evidence_summary.json",
        "evidence_pack.json",
    ]
    for name in expected:
        assert (tmp_path / "out" / name).is_file(), name

    assert read_json(tmp_path / "out" / "state_before.json")["current_state"] == "LOCAL_VERIFIED"
    assert read_json(tmp_path / "out" / "state_after.json")["current_state"] == "READY_TO_PUBLISH"
    assert read_json(tmp_path / "out" / "gate_decision_packet.json")["decision"] == "APPROVE_LOCAL_ONLY"
    assert read_json(tmp_path / "out" / "verification_profile.json")["profile"] == "code-unit"
    assert read_json(tmp_path / "out" / "publish_config.json")["verification_profile"] == "code-unit"


def test_positive_scenario_does_not_execute_publication_or_github_actions(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_positive(tmp_path / "out", write_bridge=False, bridge_root=tmp_path / "bridge")
    guardrails = result.summary["guardrails"]

    assert guardrails["phase_b_executed"] is False
    assert guardrails["phase_c_executed"] is False
    assert guardrails["commit_executed"] is False
    assert guardrails["push_executed"] is False
    assert guardrails["pull_request_created"] is False
    assert guardrails["merge_executed"] is False
    assert guardrails["deploy_executed"] is False
    assert guardrails["github_operation_executed"] is False
    assert guardrails["external_api_call_executed"] is False
    flattened = " ".join(" ".join(command) for command in guardrails["subprocesses"])
    assert "-Phase" not in flattened
    assert "asf_publish_step.ps1" not in flattened
    assert PUBLISH_RUNNER.is_file()


def test_negative_scenario_fails_closed_and_does_not_produce_ready_config(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_negative(tmp_path / "out", write_bridge=False, bridge_root=tmp_path / "bridge")

    assert result.exit_code == 0
    assert result.status == "fail_closed"
    summary = read_json(tmp_path / "out" / "evidence_summary.json")
    negative = read_json(tmp_path / "out" / "negative_fail_closed.json")
    assert summary["status"] == "fail_closed"
    assert summary["ready_config_produced"] is False
    assert summary["final_state"] == "IMPLEMENTED"
    assert negative["observed_fail_closed"] is True
    assert negative["ready_config_produced"] is False
    assert not (tmp_path / "out" / "publish_config.json").exists()


def test_cli_json_and_markdown_outputs_are_valid(tmp_path: Path, capsys) -> None:
    module = load_module()

    code = module.run(
        [
            "--scenario",
            module.SCENARIO_POSITIVE,
            "--out-dir",
            str(tmp_path / "json_out"),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["scenario"] == module.SCENARIO_POSITIVE
    assert payload["status"] == "ok"

    code = module.run(
        [
            "--scenario",
            module.SCENARIO_NEGATIVE,
            "--out-dir",
            str(tmp_path / "md_out"),
            "--markdown",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert "# ASF E2E MVP Smoke Evidence Summary" in captured.out
    assert "invalid-state-to-publish-config" in captured.out


def test_write_bridge_uses_explicit_temporary_root_and_writes_last_files(tmp_path: Path) -> None:
    module = load_module()
    bridge_root = tmp_path / "bridge"
    result = module.run_positive(tmp_path / "out", write_bridge=True, bridge_root=bridge_root)

    assert result.exit_code == 0
    assert str(bridge_root) in result.summary["bridge_paths"]["last_pack"]
    assert (bridge_root / "LAST-Evidence_Summary.md").is_file()
    assert (bridge_root / "LAST-Evidence_Pack.json").is_file()
    assert list(bridge_root.glob("0700-*-Evidence_Summary_*.md"))
    assert list(bridge_root.glob("0700-*-Evidence_Pack_*.json"))
    pack = read_json(bridge_root / "LAST-Evidence_Pack.json")
    assert pack["summary"]["scenario"] == module.SCENARIO_POSITIVE


def test_component_regression_signals_are_present_in_evidence(tmp_path: Path) -> None:
    module = load_module()
    result = module.run_positive(tmp_path / "out", write_bridge=False, bridge_root=tmp_path / "bridge")
    pack = result.evidence_pack

    assert pack["risk_report"]["risk_level"] == "L2"
    assert pack["dry_run_report"]["risk_checkpoint"]["status"] == "PASS"
    assert pack["gate_decision_packet"]["allowed"] is True
    assert pack["verification_profile"]["profile"] == "code-unit"
    assert pack["publish_config"]["verification_profile"] == "code-unit"
    assert pack["state_after"]["current_state"] == "READY_TO_PUBLISH"
    assert result.summary["generator_payload"]["status"] == "ok"


def test_actual_smoke_script_scope_is_motor_core_for_future_publication(tmp_path: Path) -> None:
    module = load_module()
    components = module.load_components()
    selector = components["selector"]

    packet = selector.select_profile(
        selector.SelectorInput(
            risk_level="L2",
            changed_files=(
                "scripts/asf_e2e_mvp_smoke.py",
                "tests/unit/test_asf_e2e_mvp_smoke.py",
            ),
            step_type="motor-core",
            phase="local",
            intent=("local motor smoke",),
            checks_already_run=(),
            provided_gates=("local_verification",),
        )
    )
    assert packet["profile"] == "motor-core"

    generator_input = module.build_generator_input(bridge_root=tmp_path / "bridge")
    generator_input.update(
        {
            "expected_files": [
                "scripts/asf_e2e_mvp_smoke.py",
                "tests/unit/test_asf_e2e_mvp_smoke.py",
            ],
            "changed_files": [
                "scripts/asf_e2e_mvp_smoke.py",
                "tests/unit/test_asf_e2e_mvp_smoke.py",
            ],
            "profile_selector_expected_profile": "motor-core",
        }
    )
    import asf_publish_config_generator as generator

    result = generator.generate(generator_input, out_dir=tmp_path / "generator", strict_required=True)
    assert result.status == "ok", result.errors
    config = read_json(result.config_path)
    assert config["verification_profile"] == "motor-core"
    phase_a = [" ".join(command["argv"]) for command in config["phase_a_checks"]]
    assert any("test_asf_e2e_mvp_smoke.py" in command for command in phase_a)
