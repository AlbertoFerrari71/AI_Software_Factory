from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_workflow_health.py"
DOC = ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md"
INDEX = ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md"
CLOSURE_PACK = ROOT / "docs" / "motor" / "0730_END_TO_END_MVP_CLOSURE_PACK.md"
PILOT_NOTES = ROOT / "docs" / "motor" / "0740_MVP_REAL_STEP_PILOT.md"
HOOK_DOC = ROOT / "docs" / "motor" / "0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_health_check_files_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert CLOSURE_PACK.exists()
    assert PILOT_NOTES.exists()
    assert HOOK_DOC.exists()


def test_workflow_health_check_script_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Workflow Health Check PASSED" in result.stdout


def test_workflow_health_check_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    forbidden_patterns = [
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
        "gh release",
        "git merge",
        "git reset --hard",
        "git clean",
        "Set-ExecutionPolicy",
        "setx PATH",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in content


def test_workflow_health_check_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "Verification Gate",
        "Documentation Sync",
        "Release Smoke Workflow",
        "Project Workflow Index",
        "read-only",
        "local-first",
        "CI",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_project_workflow_index_mentions_health_check() -> None:
    content = read(INDEX)

    assert "docs/35_WORKFLOW_HEALTH_CHECK.md" in content
    assert "scripts/check_workflow_health.py" in content


def test_workflow_health_tracks_mvp_closure_pack() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    closure_pack = read(CLOSURE_PACK)

    indexed_fragments = [
        "docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md",
        "MVP STATUS: GO WITH WARNINGS",
        "GO/WARNING/NO-GO",
        "0740) MVP Real Step Pilot",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    closure_fragments = [
        "MVP STATUS: GO WITH WARNINGS",
        "GO/WARNING/NO-GO",
        "0740) MVP Real Step Pilot",
    ]

    for fragment in closure_fragments:
        assert fragment in closure_pack


def test_workflow_health_tracks_mvp_real_step_pilot() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    pilot_notes = read(PILOT_NOTES)

    indexed_fragments = [
        "docs/motor/0740_MVP_REAL_STEP_PILOT.md",
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0740_mvp_real_step_pilot",
        "0750) State Machine Publish Runner Event Hooks",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    pilot_fragments = [
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0740_mvp_real_step_pilot",
        "0750) State Machine Publish Runner Event Hooks",
    ]

    for fragment in pilot_fragments:
        assert fragment in pilot_notes


def test_workflow_health_tracks_state_machine_publish_runner_event_hooks() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    hook_doc = read(HOOK_DOC)

    indexed_fragments = [
        "docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md",
        "state_machine_enabled",
        "phase_b_started",
        "phase_c_started",
        "main_verified",
        "examples/publish_step/0750_publish_config_state_hooks.example.json",
        "-ApprovePublish",
        "-ApproveMerge",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    hook_fragments = [
        "state_machine_enabled",
        "phase_b_started",
        "phase_b_failed",
        "phase_c_started",
        "phase_c_failed",
        "main_verified",
        "state_close_on_phase_c_success",
        "0760) MVP Real Step Pilot 2 with State Hooks",
    ]

    for fragment in hook_fragments:
        assert fragment in hook_doc
