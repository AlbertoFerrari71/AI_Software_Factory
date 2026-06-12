from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_handoff_pack_generator.py"
GENERATOR_SCRIPT = ROOT / "scripts" / "asf_gpt_prompt_generator.py"
DISCOVERY_SCRIPT = ROOT / "scripts" / "asf_bridge_report_discovery.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_plan(path: Path) -> Path:
    payload = {
        "step_id": "1030",
        "title": "Manual loop smoke",
        "objective": "Generate a mock prompt for safe smoke.",
        "risk_level": "L1",
        "phase": "unit-test",
        "allowed_paths": ["docs/motor"],
        "forbidden_actions": ["commit", "push", "PR", "merge", "deploy"],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_handoff_generator_writes_markdown_json_and_next_prompt(tmp_path: Path, monkeypatch) -> None:
    module = load_module(SCRIPT, "asf_handoff_pack_generator")
    bridge = tmp_path / "bridge"
    repo = tmp_path / "repo"
    out_dir = tmp_path / "handoff"
    repo.mkdir()
    (bridge / "codex_command").mkdir(parents=True)
    (bridge / "codex_command" / "1030-Report_Codex.md").write_text("# Report\n", encoding="utf-8")
    (bridge / "pwsh_command").mkdir()
    (bridge / "pwsh_command" / "1030-Output_Compatto.md").write_text("# Output\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "run_command",
        lambda argv, *, cwd, timeout_seconds=8: {
            "command": argv,
            "status": "UNAVAILABLE" if argv[0] == "gh" else "PASS",
            "exit_code": 0 if argv[0] != "gh" else None,
            "stdout": "main" if "branch" in argv else ("abc123" if "rev-parse" in argv else ""),
            "stderr": "",
        },
    )

    packet = module.generate_handoff_pack(
        bridge_root=bridge,
        root=repo,
        step="1030",
        title="ASF GPT Live Continuity Mega-Step",
        status="PASS",
        output_dir=out_dir,
        checks=[{"name": "unit", "status": "PASS"}],
    )

    assert Path(packet["outputs"]["markdown"]).is_file()
    assert Path(packet["outputs"]["json"]).is_file()
    assert Path(packet["outputs"]["start_next_chat_prompt"]).is_file()
    payload = json.loads(Path(packet["outputs"]["json"]).read_text(encoding="utf-8"))
    assert payload["step"] == "1030"
    assert payload["status"] == "PASS"
    assert payload["bridge"]["reports"]


def test_handoff_generator_is_fail_soft_when_git_and_gh_are_unavailable(tmp_path: Path, monkeypatch) -> None:
    module = load_module(SCRIPT, "asf_handoff_pack_generator_unavailable")
    bridge = tmp_path / "missing-bridge"
    repo = tmp_path / "repo"
    repo.mkdir()

    def unavailable(argv: list[str], *, cwd: Path, timeout_seconds: int = 8) -> dict[str, Any]:
        return {"command": argv, "status": "UNAVAILABLE", "exit_code": None, "stdout": "", "stderr": "missing"}

    monkeypatch.setattr(module, "run_command", unavailable)

    packet = module.generate_handoff_pack(
        bridge_root=bridge,
        root=repo,
        step="1030",
        title="ASF GPT Live Continuity Mega-Step",
        output_dir=tmp_path / "handoff",
    )

    assert packet["repo"]["working_tree"] == "unknown"
    assert packet["bridge"]["status"] == "BRIDGE_MISSING"
    assert packet["github"]["status"] == "UNAVAILABLE"


def test_handoff_outputs_do_not_include_secret_sentinel(tmp_path: Path, monkeypatch) -> None:
    module = load_module(SCRIPT, "asf_handoff_pack_generator_secret")
    bridge = tmp_path / "bridge"
    repo = tmp_path / "repo"
    out_dir = tmp_path / "handoff"
    repo.mkdir()
    bridge.mkdir()
    secret = "sk-" + "proj-secretvalue123456"
    (bridge / "state.json").write_text(json.dumps({"note": f"api_key={secret}"}), encoding="utf-8")

    monkeypatch.setattr(
        module,
        "run_command",
        lambda argv, *, cwd, timeout_seconds=8: {
            "command": argv,
            "status": "PASS",
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        },
    )

    packet = module.generate_handoff_pack(
        bridge_root=bridge,
        root=repo,
        step="1030",
        title="ASF GPT Live Continuity Mega-Step",
        output_dir=out_dir,
        include_gh=False,
    )

    combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in packet["outputs"].values())
    assert secret not in combined
    assert module.SECRET_REDACTION in combined


def test_1030_safe_smoke_links_generator_discovery_and_handoff(tmp_path: Path, monkeypatch) -> None:
    prompt_module = load_module(GENERATOR_SCRIPT, "asf_gpt_prompt_generator_1030_smoke")
    discovery_module = load_module(DISCOVERY_SCRIPT, "asf_bridge_report_discovery_1030_smoke")
    handoff_module = load_module(SCRIPT, "asf_handoff_pack_generator_1030_smoke")
    bridge = tmp_path / "bridge"
    repo = tmp_path / "repo"
    repo.mkdir()
    plan = write_plan(tmp_path / "plan.json")

    prompt_module.generate_prompt(
        plan,
        output_path=bridge / "codex_command" / "1030-Smoke-Prompt.md",
        mode="mock",
    )
    (bridge / "codex_command" / "1030-Report_Codex.md").write_text("status: PASS\n", encoding="utf-8")
    (bridge / "pwsh_command").mkdir()
    (bridge / "pwsh_command" / "1030-Output_Compatto.md").write_text("status: PASS\n", encoding="utf-8")

    discovery = discovery_module.discover_reports(bridge, expected_step="1030", kind="any")
    assert discovery["status"] in {"FOUND", "AMBIGUOUS"}

    monkeypatch.setattr(
        handoff_module,
        "run_command",
        lambda argv, *, cwd, timeout_seconds=8: {
            "command": argv,
            "status": "PASS",
            "exit_code": 0,
            "stdout": "main" if "branch" in argv else "",
            "stderr": "",
        },
    )
    packet = handoff_module.generate_handoff_pack(
        bridge_root=bridge,
        root=repo,
        step="1030",
        title="ASF GPT Live Continuity Mega-Step",
        status="PASS",
        output_dir=bridge / "handoff",
        include_gh=False,
    )

    assert Path(packet["outputs"]["start_next_chat_prompt"]).is_file()
    assert "1030-Report_Codex.md" in Path(packet["outputs"]["json"]).read_text(encoding="utf-8")
