from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md"
)
STATE = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PUSH_ROLLBACK_STATE_REPORT.md"
)
MATRIX = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PUSH_ROLLBACK_DECISION_MATRIX.md"
)
COMMANDS = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md"
)
EVIDENCE = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0900_codex_skills_push_or_rollback_decision.example.json"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_0900_artifacts_exist() -> None:
    for path in [DOC, STATE, MATRIX, COMMANDS, EVIDENCE]:
        assert path.exists()


def test_step_0900_evidence_manifest_is_valid_and_non_executing() -> None:
    manifest = json.loads(read(EVIDENCE))

    assert manifest["step"] == "0900"
    assert manifest["status"] == "decision_pack_created"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["local_commit_hash"] == "b488745"
    assert manifest["external_repo_status_clean"] is True
    assert manifest["asf_step_0890_found_on_main"] is True
    assert manifest["push_performed_in_0900"] is False
    assert manifest["rollback_performed_in_0900"] is False
    assert manifest["commit_performed_in_0900"] is False
    assert manifest["pr_performed_in_0900"] is False
    assert manifest["merge_performed_in_0900"] is False
    assert manifest["deploy_performed_in_0900"] is False
    assert manifest["tag_performed_in_0900"] is False
    assert manifest["prepared_commands_executed"] is False
    assert manifest["human_gate_required_for_next_step"] is True


def test_step_0900_decision_doc_and_commands_are_decisional_only() -> None:
    doc = read(DOC).casefold()
    commands = read(COMMANDS)

    for fragment in [
        "push controllato",
        "rollback locale",
        "keep local temporaneo",
        "non esegue nessuna delle tre opzioni",
        "0910) codex_skills controlled push execution or local rollback",
    ]:
        assert fragment in doc

    assert "NON ESEGUITI" in commands
    assert "git -C \"C:\\Users\\alberto.ferrari\\.agents\\skills\" push origin main" in commands
    assert "reset --soft HEAD~1" in commands
    assert "Remove-Item -Path" in commands


def test_step_0900_state_and_matrix_capture_observed_commit() -> None:
    state = read(STATE)
    matrix = read(MATRIX)

    for fragment in [
        "b488745 0870 add ASF controlled write pilot note",
        "docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md",
        "ahead 1",
        "non verificato live per vincolo no-fetch",
    ]:
        assert fragment in state

    for fragment in [
        "A) Push controllato del commit `b488745`",
        "B) Rollback locale del commit `b488745`",
        "C) Keep local temporaneo",
        "Nessuna opzione viene eseguita nello STEP 0900",
    ]:
        assert fragment in matrix


def test_step_0900_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0900 - Codex_Skills Controlled Push or Rollback Decision",
            "docs/motor/0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Codex_Skills Controlled Push or Rollback Decision",
            "0910) Codex_Skills Controlled Push Execution or Local Rollback",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md",
            "examples/publish_runner/0900_codex_skills_push_or_rollback_decision.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0900 - Codex_Skills Controlled Push or Rollback Decision",
            "tests/unit/test_codex_skills_push_or_rollback_decision.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
