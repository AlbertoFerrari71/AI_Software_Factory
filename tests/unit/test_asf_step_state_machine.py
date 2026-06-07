from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_step_state_machine.py"
GENERATOR = ROOT / "scripts" / "asf_publish_config_generator.py"
RUNNER = ROOT / "scripts" / "asf_publish_step.ps1"
SELECTOR = ROOT / "scripts" / "asf_verification_profile_selector.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_step_state_machine", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pwsh_available() -> bool:
    return shutil.which("pwsh") is not None


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_sequence(module, step: str, events: list[str]) -> dict[str, object]:
    state = module.initial_state(step)
    for event in events:
        packet, updated = module.apply_event(state, event=event)
        assert packet["allowed"], packet
        assert updated is not None
        state = updated
    return state


def test_initializes_from_planned() -> None:
    module = load_module()
    state = module.initial_state("0670")

    assert state["step"] == "0670"
    assert state["current_state"] == "PLANNED"
    assert state["history"] == []
    assert "timestamps" in state


def test_normal_flow_reaches_closed() -> None:
    module = load_module()
    events = [
        "prompt_saved",
        "codex_started",
        "codex_completed",
        "local_checks_passed",
        "publish_config_generated",
        "phase_b_started",
        "phase_b_passed",
        "phase_c_started",
        "phase_c_passed",
        "main_verified",
    ]
    state = apply_sequence(module, "0670", events)

    assert state["current_state"] == "CLOSED"
    assert state["last_event"] == "main_verified"
    assert len(state["history"]) == len(events)


def test_invalid_transition_fails_closed() -> None:
    module = load_module()
    state = module.initial_state("0670")

    packet, updated = module.apply_event(state, event="phase_c_started")

    assert updated is None
    assert packet["allowed"] is False
    assert packet["fail_closed"] is True
    assert packet["next_state"] == "PLANNED"


def test_phase_c_started_without_pr_blocks() -> None:
    module = load_module()
    state = apply_sequence(module, "0670", ["prompt_saved", "codex_started", "codex_completed"])

    packet, updated = module.apply_event(state, event="phase_c_started")

    assert updated is None
    assert packet["fail_closed"] is True
    assert any("PR_CREATED" in reason for reason in packet["reasons"])


def test_close_step_before_publish_blocks() -> None:
    module = load_module()
    state = apply_sequence(module, "0670", ["prompt_saved", "codex_started", "codex_completed", "local_checks_passed"])

    packet, updated = module.apply_event(state, event="close_step")

    assert updated is None
    assert packet["allowed"] is False
    assert packet["fail_closed"] is True


def test_phase_c_failed_moves_to_recovery_required_without_completion_claim() -> None:
    module = load_module()
    state = apply_sequence(
        module,
        "0670",
        [
            "prompt_saved",
            "codex_started",
            "codex_completed",
            "local_checks_passed",
            "publish_config_generated",
            "phase_b_started",
            "phase_b_passed",
            "phase_c_started",
        ],
    )

    packet, updated = module.apply_event(state, event="phase_c_failed")
    text = json.dumps(packet)

    assert packet["allowed"] is True
    assert packet["fail_closed"] is False
    assert packet["next_state"] == "RECOVERY_REQUIRED"
    assert updated is not None
    assert updated["current_state"] == "RECOVERY_REQUIRED"
    assert "COMPLETATO" not in text


def test_combined_recovery_step_is_representable() -> None:
    module = load_module()
    state = module.initial_state("0650-0660")

    packet, updated = module.apply_event(state, event="recovery_completed", target_state="CLOSED")

    assert packet["allowed"] is True
    assert packet["next_state"] == "CLOSED"
    assert updated is not None
    assert updated["current_state"] == "CLOSED"
    assert any("Combined step" in warning for warning in packet["warnings"])


def test_missing_state_file_is_created(tmp_path: Path) -> None:
    state_file = tmp_path / "0670_state.json"

    result = run_cli("--step", "0670", "--event", "prompt_saved", "--state-file", state_file, "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    assert state_file.exists()
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    payload = json.loads(result.stdout)
    assert saved["current_state"] == "PROMPT_PREPARED"
    assert payload["next_state"] == "PROMPT_PREPARED"


def test_corrupt_state_file_fails_closed(tmp_path: Path) -> None:
    state_file = tmp_path / "corrupt.json"
    state_file.write_text("{not valid json", encoding="utf-8")

    result = run_cli("--step", "0670", "--event", "codex_completed", "--state-file", state_file, "--json")

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert payload["fail_closed"] is True
    assert payload["next_state"] == "RECOVERY_REQUIRED"


def test_json_output_is_valid() -> None:
    module = load_module()
    state = module.initial_state("0670")
    packet, _ = module.apply_event(state, event="prompt_saved")

    payload = json.loads(module.render_json(packet))

    for field in [
        "step",
        "current_state",
        "event",
        "next_state",
        "allowed",
        "fail_closed",
        "reasons",
        "warnings",
        "required_gates",
        "missing_gates",
        "recommended_next_action",
        "history",
        "machine_readable",
    ]:
        assert field in payload


def test_markdown_output_is_readable() -> None:
    module = load_module()
    state = module.initial_state("0670")
    packet, _ = module.apply_event(state, event="prompt_saved")
    markdown = module.render_markdown(packet)

    for fragment in ["Step Execution State Machine", "## Summary", "## Required Gates", "## Recommended Next Action"]:
        assert fragment in markdown
    assert "PROMPT_PREPARED" in markdown


def test_cli_base_resume_works(tmp_path: Path) -> None:
    state_file = tmp_path / "0670_state.json"
    first = run_cli("--step", "0670", "--event", "prompt_saved", "--state-file", state_file, "--json")
    second = run_cli("--event", "codex_completed", "--state-file", state_file, "--markdown")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "IMPLEMENTED" in second.stdout
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert saved["current_state"] == "IMPLEMENTED"


def test_write_bridge_generates_progressive_and_last_files(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    state_file = tmp_path / "0680_state.json"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--state-file",
        state_file,
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    for relative in [
        "0680-State_step_0680.json",
        "0680-Event_step_0680.json",
        "0680-Output_Compatto_step_0680.md",
        "0680-Output_Completo_step_0680.txt",
        "LAST-State.json",
        "LAST-Event.json",
        "LAST-Output_Compatto.md",
        "LAST-Output_Completo.txt",
    ]:
        assert (bridge_root / relative).is_file()


def test_bridge_last_state_and_event_are_valid_json(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    state = read_json(bridge_root / "LAST-State.json")
    event = read_json(bridge_root / "LAST-Event.json")
    assert state["step"] == "0680"
    assert state["current_state"] == "PROMPT_PREPARED"
    assert state["last_event"] == "prompt_saved"
    assert state["state_file"] == str(bridge_root / "LAST-State.json")
    assert event["event"] == "prompt_saved"
    assert event["from_state"] == "PLANNED"
    assert event["to_state"] == "PROMPT_PREPARED"


def test_bridge_compact_output_contains_state_event_and_next_action(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--markdown",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    compact = (bridge_root / "LAST-Output_Compatto.md").read_text(encoding="utf-8")
    assert "PROMPT_PREPARED" in compact
    assert "prompt_saved" in compact
    assert "Recommended Next Action" in compact
    assert "LAST-State.json" in compact
    assert "LAST-Output_Completo.txt" in compact
    assert "Set-Clipboard" in compact


def test_bridge_complete_output_contains_history_and_safety_note(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    state_file = tmp_path / "0680_state.json"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--state-file",
        state_file,
        "--write-bridge",
        "--bridge-root",
        bridge_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    complete = (bridge_root / "LAST-Output_Completo.txt").read_text(encoding="utf-8")
    assert "History completa" in complete
    assert "prompt_saved" in complete
    assert "No Phase B, Phase C, GitHub, publish, commit, push, PR, merge, or deploy action was executed." in complete


def test_bridge_custom_root_uses_temporary_directory_not_real_bridge(tmp_path: Path) -> None:
    module = load_module()
    bridge_root = tmp_path / "custom_state_machine_bridge"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert str(bridge_root) != module.DEFAULT_STATE_MACHINE_BRIDGE_ROOT
    assert module.DEFAULT_STATE_MACHINE_BRIDGE_ROOT not in result.stdout
    assert (bridge_root / "LAST-State.json").is_file()


def test_invalid_transition_with_bridge_writes_fail_closed_outputs(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "phase_c_started",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert result.returncode == 2
    event = read_json(bridge_root / "LAST-Event.json")
    state = read_json(bridge_root / "LAST-State.json")
    assert event["allowed"] is False
    assert event["fail_closed"] is True
    assert state["fail_closed"] is True
    assert state["blockers"]


def test_write_bridge_without_state_file_uses_last_state_as_state_file(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    first = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )
    second = run_cli(
        "--event",
        "codex_completed",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    state = read_json(bridge_root / "LAST-State.json")
    assert state["state_file"] == str(bridge_root / "LAST-State.json")
    assert state["current_state"] == "IMPLEMENTED"
    assert len(state["history"]) == 2


def test_cli_base_write_bridge_returns_bridge_paths(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"

    result = run_cli(
        "--step",
        "0680",
        "--event",
        "prompt_saved",
        "--write-bridge",
        "--bridge-root",
        bridge_root,
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["bridge_root"] == str(bridge_root)
    assert any("LAST-State.json" in path for path in payload["bridge_files"])


def test_state_machine_script_has_no_runner_side_effect_path() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert "subprocess" not in content
    assert "asf_publish_step.ps1" not in content
    assert "-Phase B" not in content
    assert "-Phase C" not in content


def test_publish_config_generator_regression_for_state_machine_scope(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--step",
            "0670",
            "--name",
            "Step_Execution_State_Machine",
            "--risk-level",
            "L2",
            "--verification-phase",
            "local",
            "--expected-files",
            "scripts/asf_step_state_machine.py",
            "tests/unit/test_asf_step_state_machine.py",
            "--out-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    config = json.loads(Path(payload["config_path"]).read_text(encoding="utf-8"))
    assert config["verification_profile"] == "motor-core"
    phase_a = [" ".join(command["argv"]) for command in config["phase_a_checks"]]
    assert any("test_asf_step_state_machine.py" in text for text in phase_a)


@pytest.mark.skipif(not pwsh_available(), reason="pwsh executable not available")
def test_publish_runner_plan_regression_still_works(tmp_path: Path) -> None:
    config = ROOT / "examples" / "publish_step" / "0640_publish_config_motor_core.example.json"
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUNNER),
            "-Config",
            str(config),
            "-Phase",
            "Plan",
            "-BridgeRoot",
            str(tmp_path / "bridge"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PLAN - config validated" in result.stdout


def test_verification_profile_selector_regression_for_state_machine_scope() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SELECTOR),
            "--risk-level",
            "L2",
            "--changed-files",
            "scripts/asf_step_state_machine.py",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "motor-core"
