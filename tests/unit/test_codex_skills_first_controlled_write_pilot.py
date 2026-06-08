from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md"
RESULT = ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_CONTROLLED_WRITE_RESULT.md"
ROLLBACK = ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_ROLLBACK_PLAN.md"
EVIDENCE = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0870_codex_skills_controlled_write_evidence.example.json"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_0870_artifacts_exist() -> None:
    for path in [DOC, RESULT, ROLLBACK, EVIDENCE]:
        assert path.exists()


def test_step_0870_evidence_manifest_is_valid_and_non_publishing() -> None:
    manifest = json.loads(read(EVIDENCE))

    assert manifest["step"] == "0870"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["external_repo_write_performed"] is True
    assert manifest["human_gate_required_for_next_step"] is True
    assert manifest["created_or_modified_files"] == [
        "docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md"
    ]

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


def test_step_0870_document_covers_human_gate_rollback_and_no_publish() -> None:
    content = read(DOC).casefold()

    for fragment in [
        "human gate",
        "rollback",
        "nessun commit/push/pr/merge",
        "nessun deploy",
        "nessun tag",
        "local controlled write",
        "0880) codex_skills controlled write review",
    ]:
        assert fragment in content


def test_step_0870_result_distinguishes_completed_and_blocked_write() -> None:
    content = read(RESULT).casefold()

    for fragment in [
        "write consentito: `si`",
        "write eseguito: `si`",
        "write bloccato: `no`",
        "se anche uno dei guardrail fosse fallito",
        "nessun commit/push/pr/merge",
    ]:
        assert fragment in content


def test_step_0870_rollback_plan_is_manual_and_scoped() -> None:
    content = read(ROLLBACK).casefold()

    for fragment in [
        "solo dopo review umana",
        "remove-item -path",
        "0870_controlled_write_pilot.md",
        "non usare comandi di cleanup ampio",
        "git clean",
        "git reset",
    ]:
        assert fragment in content


def test_step_0870_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0870 - Codex_Skills First Controlled Write Pilot",
            "docs/motor/0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Codex_Skills First Controlled Write Pilot",
            "0880) Codex_Skills Controlled Write Review and Rollback/Commit Decision",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md",
            "examples/publish_runner/0870_codex_skills_controlled_write_evidence.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0870 - Codex_Skills First Controlled Write Pilot",
            "tests/unit/test_codex_skills_first_controlled_write_pilot.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
