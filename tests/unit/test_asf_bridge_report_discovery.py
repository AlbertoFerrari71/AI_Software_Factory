from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_bridge_report_discovery.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_bridge_report_discovery", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def touch(path: Path, text: str = "content", *, timestamp: int = 1_800_000_000) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.utime(path, (timestamp, timestamp))
    return path


def test_finds_expected_codex_report(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1020-Report_Codex.md")
    touch(bridge / "codex_command" / "1030-Report_Codex.md", timestamp=1_800_000_100)

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")

    assert packet["status"] == "FOUND"
    assert packet["selected"]["name"] == "1030-Report_Codex.md"
    assert packet["selected"]["score"] >= 100
    assert packet["summary"]["report_status"] == "UNKNOWN"


def test_finds_latest_pwsh_compact_output(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "pwsh_command" / "1030-01-Output_Compatto.md", timestamp=1_800_000_000)
    touch(bridge / "pwsh_command" / "1030-02-Output_Compatto.md", timestamp=1_800_000_200)

    packet = module.discover_reports(bridge, expected_step="1030", kind="pwsh")

    assert packet["status"] == "FOUND"
    assert packet["selected"]["name"] == "1030-02-Output_Compatto.md"


def test_filters_by_expected_step(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1020-Report_Codex.md")

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")

    assert packet["status"] == "NOT_FOUND"
    assert packet["matches"] == []
    assert any("1030" not in pattern for pattern in packet["searched"])
    assert "incolla" in packet["summary"]["manual_paste_instruction"].lower()


def test_missing_bridge_returns_bridge_missing(tmp_path: Path) -> None:
    module = load_module()

    packet = module.discover_reports(tmp_path / "missing", expected_step="1030", kind="any")

    assert packet["status"] == "BRIDGE_MISSING"


def test_json_output_is_stable(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1030-Report_Codex.md")

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")
    rendered = module.render_json(packet)

    assert json.loads(rendered)["status"] == "FOUND"
    assert rendered == json.dumps(packet, indent=2, sort_keys=True) + "\n"


def test_ambiguous_match_is_selected_deterministically(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1030-A-Report_Codex.md", timestamp=1_800_000_000)
    touch(bridge / "codex_command" / "1030-B-Report_Codex.md", timestamp=1_800_000_000)

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")

    assert packet["status"] == "AMBIGUOUS"
    assert packet["selected"]["name"] == "1030-A-Report_Codex.md"
    assert packet["selected"]["selection_reason"] == "best_score_tie_selected_deterministically"


def test_prefers_structured_codex_report_json_over_markdown(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1030-Report_Codex.md", "# Report\nStato: PASS\n")
    touch(
        bridge / "codex_command" / "1030-Report_Codex.json",
        json.dumps({"step": "1030", "status": "PARTIAL", "tests": [{"status": "PASS"}]}),
        timestamp=1_800_000_100,
    )

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")

    assert packet["status"] == "FOUND"
    assert packet["selected"]["name"] == "1030-Report_Codex.json"
    assert packet["summary"]["report_status"] == "PARTIAL"
    assert "tests=1" in packet["summary"]["summary"]


def test_markdown_summary_does_not_invent_pass_without_evidence(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    touch(bridge / "codex_command" / "1030-Report_Codex.md", "# Report\nNessuna evidenza conclusiva.\n")

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")

    assert packet["status"] == "FOUND"
    assert packet["summary"]["report_status"] == "UNKNOWN"


def test_summary_redacts_secret_sentinel(tmp_path: Path) -> None:
    module = load_module()
    bridge = tmp_path / "bridge"
    secret = "sk-" + "proj-secretvalue123456"
    touch(bridge / "codex_command" / "1030-Report_Codex.md", f"# Report\n- token: {secret}\n")

    packet = module.discover_reports(bridge, expected_step="1030", kind="codex")
    rendered = json.dumps(packet, sort_keys=True)

    assert secret not in rendered
    assert module.SECRET_REDACTION in rendered
