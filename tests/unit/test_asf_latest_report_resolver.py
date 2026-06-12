from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_latest_report_resolver.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_latest_report_resolver", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json_report(path: Path, *, status: str = "PASS", step: str = "1050") -> None:
    payload = {
        "schema_version": "1.0",
        "project": "AI_Software_Factory",
        "step": step,
        "step_title": "Sample",
        "status": status,
        "started_at": None,
        "finished_at": None,
        "branch": "step/sample",
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
        "checks": [{"name": "pytest", "command": "python -m pytest", "status": "PASS", "exit_code": 0, "notes": ""}],
        "risks": [],
        "decisions_required": [],
        "next_step": "1060",
        "report_markdown_path": str(path.with_suffix(".md")),
        "bridge_paths": [],
        "forbidden_actions_confirmed": True,
        "human_gate_required": True,
        "summary": "Sample report.",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_json_report_is_preferred_when_valid(tmp_path: Path) -> None:
    module = load_module()
    write_json_report(tmp_path / "1050-Report_Codex.json")
    (tmp_path / "1050-Report_Codex.md").write_text("B. Stato: PASS\n", encoding="utf-8")

    result = module.resolve_latest_report(tmp_path, expected_step="1050")

    assert result["resolution_status"] == "FOUND"
    assert result["status"] == "PASS"
    assert result["selected_report"].endswith("1050-Report_Codex.json")
    assert result["selected_markdown"].endswith("1050-Report_Codex.md")


def test_markdown_only_report_is_degraded(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "1050-Report_Codex.md").write_text("A. Step\n\nB. Stato: PASS\n", encoding="utf-8")

    result = module.resolve_latest_report(tmp_path, expected_step="1050")

    assert result["resolution_status"] == "DEGRADED"
    assert result["status"] == "PASS"
    assert "JSON sidecar is missing" in result["warnings"][0]


def test_incoherent_json_does_not_become_pass(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "1050-Report_Codex.json").write_text('{"status": "PASS"}', encoding="utf-8")
    (tmp_path / "1050-Report_Codex.md").write_text("B. Stato: PASS\n", encoding="utf-8")

    result = module.resolve_latest_report(tmp_path, expected_step="1050")

    assert result["resolution_status"] == "INCOHERENT"
    assert result["status"] == "INCOHERENT_REPORT"


def test_old_report_is_not_selected_for_expected_step(tmp_path: Path) -> None:
    module = load_module()
    write_json_report(tmp_path / "1040-Report_Codex.json", step="1040")

    result = module.resolve_latest_report(tmp_path, expected_step="1050")

    assert result["resolution_status"] == "MISSING"
    assert result["selected_report"] is None


def test_missing_bridge_has_operational_message(tmp_path: Path) -> None:
    module = load_module()

    result = module.resolve_latest_report(tmp_path / "missing", expected_step="1050")

    assert result["resolution_status"] == "MISSING"
    assert result["status"] == "MISSING_BRIDGE"
    assert "Bridge folder not found" in result["warnings"][0]
