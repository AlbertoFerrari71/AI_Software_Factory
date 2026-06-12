from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LATEST = ROOT / "scripts" / "asf_latest_report_resolver.py"
READY = ROOT / "scripts" / "asf_publish_readiness_gate.py"
REVIEWER = ROOT / "scripts" / "asf_reviewer_packet_builder.py"
PROMPT = ROOT / "scripts" / "asf_codex_next_prompt_builder.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_report(path: Path, *, status: str = "PASS") -> None:
    payload = {
        "schema_version": "1.0",
        "project": "AI_Software_Factory",
        "step_range": "1050-1130",
        "step_title": "Operator RC",
        "status": status,
        "started_at": None,
        "finished_at": None,
        "branch": "step/1050-1130",
        "files_created": ["scripts/asf_operator_status.py"],
        "files_modified": [],
        "files_deleted": [],
        "checks": [{"name": "pytest", "command": "python -m pytest", "status": "PASS", "exit_code": 0, "notes": ""}],
        "risks": [],
        "decisions_required": [],
        "next_step": "1140",
        "report_markdown_path": str(path.with_suffix(".md")),
        "bridge_paths": [],
        "forbidden_actions_confirmed": True,
        "human_gate_required": True,
        "summary": "Operator RC sample.",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    path.with_suffix(".md").write_text("B. Stato: PASS\n", encoding="utf-8")


def load_readiness_module():
    spec = importlib.util.spec_from_file_location("asf_publish_readiness_gate", READY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    scripts_path = str(ROOT / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_resolver_cli_json(tmp_path: Path) -> None:
    write_report(tmp_path / "1050-1130-Report_Codex.json")

    result = run_script(LATEST, "--bridge", str(tmp_path), "--expected-step", "1050", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["resolution_status"] == "FOUND"
    assert payload["status"] == "PASS"


def test_publish_readiness_green_for_pass_report(tmp_path: Path) -> None:
    module = load_readiness_module()
    write_report(tmp_path / "1050-1130-Report_Codex.json")

    payload = module.evaluate_readiness(bridge=tmp_path, expected_step="1050", root=ROOT)

    assert payload["semaphore"] == "GREEN"
    assert payload["publish_command_allowed"] is False
    assert payload["human_approval_required_for_publish"] is True


def test_publish_readiness_red_for_missing_report(tmp_path: Path) -> None:
    module = load_readiness_module()

    payload = module.evaluate_readiness(bridge=tmp_path, expected_step="1050", root=ROOT)

    assert payload["semaphore"] == "RED"


def test_publish_readiness_red_for_fail_report(tmp_path: Path) -> None:
    module = load_readiness_module()
    write_report(tmp_path / "1050-1130-Report_Codex.json", status="FAIL")

    payload = module.evaluate_readiness(bridge=tmp_path, expected_step="1050", root=ROOT)

    assert payload["semaphore"] == "RED"


def test_reviewer_packet_is_generated(tmp_path: Path) -> None:
    write_report(tmp_path / "1050-1130-Report_Codex.json")

    result = run_script(REVIEWER, "--bridge", str(tmp_path), "--expected-step", "1050")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS / FIX / STOP / ASK_ALBERTO" in result.stdout
    assert "scripts/asf_operator_status.py" in result.stdout


def test_draft_prompt_contains_forbidden_actions() -> None:
    result = run_script(
        PROMPT,
        "--step",
        "1140",
        "--title",
        "Prompt Injection Samples",
        "--objective",
        "Add adversarial samples.",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "DRAFT" in result.stdout
    assert "Do not commit." in result.stdout
    assert "Do not push." in result.stdout
