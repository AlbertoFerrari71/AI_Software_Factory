from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md"
)
STATE = ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_EXTERNAL_REPO_STATE_REPORT.md"
MATRIX = ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_DECISION_MATRIX.md"
COMMANDS = (
    ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md"
)
EVIDENCE = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0880_codex_skills_controlled_write_review_decision.example.json"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_0880_artifacts_exist() -> None:
    for path in [DOC, STATE, MATRIX, COMMANDS, EVIDENCE]:
        assert path.exists()


def test_step_0880_evidence_manifest_is_valid_and_non_writing() -> None:
    manifest = json.loads(read(EVIDENCE))

    assert manifest["step"] == "0880"
    assert manifest["status"] == "decision_pack_created"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["external_repo_write_performed_in_0880"] is False
    assert manifest["prepared_commands_executed"] is False
    assert manifest["default_recommendation"] == "rollback"
    assert manifest["human_gate_required_for_next_step"] is True

    for key in [
        "external_repo_commit_performed",
        "external_repo_push_performed",
        "external_repo_pr_performed",
        "external_repo_merge_performed",
        "external_repo_deploy_performed",
        "external_repo_tag_performed",
        "skill_sync_performed",
    ]:
        assert manifest[key] is False


def test_step_0880_decision_doc_covers_options_and_stop_conditions() -> None:
    content = read(DOC).casefold()

    for fragment in [
        "rollback",
        "keep local",
        "future controlled commit",
        "raccomandazione default",
        "criteri per procedere al rollback",
        "criteri per procedere a commit controllato",
        "criteri di stop",
        "0890) codex_skills rollback or controlled commit execution",
    ]:
        assert fragment in content


def test_step_0880_prepared_commands_are_not_executed_or_automatic() -> None:
    content = read(COMMANDS)
    folded = content.casefold()

    assert "NON ESEGUITO" in content
    assert "DA USARE SOLO DOPO APPROVAZIONE ESPLICITA" in content
    assert "non eseguire automaticamente" in folded
    assert "Remove-Item -Path" in content
    assert "git -C" in content
    assert "git clean" in content
    assert "git reset" in content


def test_step_0880_state_report_and_matrix_capture_recommendation() -> None:
    state = read(STATE).casefold()
    matrix = read(MATRIX).casefold()

    for fragment in [
        "?? docs/asf_external_pilot/",
        "file letto: si",
        "modifiche inattese: no",
        "readiness rollback: si",
        "raccomandazione default: rollback",
    ]:
        assert fragment in state

    for fragment in [
        "a) rollback del file 0870",
        "b) keep local temporaneo",
        "c) commit controllato futuro",
        "default consigliato",
        "solo con approvazione esplicita",
    ]:
        assert fragment in matrix


def test_step_0880_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0880 - Codex_Skills Controlled Write Review and Rollback/Commit Decision",
            "docs/motor/0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Codex_Skills Controlled Write Review and Rollback/Commit Decision",
            "0890) Codex_Skills Rollback or Controlled Commit Execution",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md",
            "examples/publish_runner/0880_codex_skills_controlled_write_review_decision.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0880 - Codex_Skills Controlled Write Review and Rollback/Commit Decision",
            "tests/unit/test_codex_skills_controlled_write_review_decision.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
