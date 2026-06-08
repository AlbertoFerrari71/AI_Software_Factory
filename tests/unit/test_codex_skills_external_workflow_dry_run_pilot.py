from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "motor" / "0860_CODEX_SKILLS_EXTERNAL_WORKFLOW_DRY_RUN_PILOT.md"
READINESS = ROOT / "docs" / "motor" / "0860_CODEX_SKILLS_READINESS_REPORT.md"
PREVIEW = ROOT / "docs" / "motor" / "0860_CODEX_SKILLS_CHANGED_FILES_PREVIEW.md"
GATE = ROOT / "docs" / "motor" / "0860_CODEX_SKILLS_HUMAN_APPROVAL_GATE.md"
PLAN = ROOT / "examples" / "publish_runner" / "0860_codex_skills_external_dry_run_plan.example.json"
EVIDENCE = ROOT / "examples" / "publish_runner" / "0860_codex_skills_dry_run_evidence_manifest.example.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def walk_items(value: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_items(child)


def test_step_0860_documents_and_examples_exist() -> None:
    for path in [DOC, READINESS, PREVIEW, GATE, PLAN, EVIDENCE]:
        assert path.exists()


def test_step_0860_document_covers_read_only_dry_run_scope() -> None:
    content = read(DOC)
    folded = content.casefold()

    for fragment in [
        "codex_skills",
        "read-only / dry-run",
        "commit, push, pr, merge, deploy",
        "readiness assessment",
        "risk assessment",
        "changed-files preview",
        "human approval gate",
        "0870) Codex_Skills First Controlled Write Pilot",
    ]:
        assert fragment.casefold() in folded


def test_step_0860_readiness_report_records_observed_external_state() -> None:
    content = read(READINESS)
    folded = content.casefold()

    for fragment in [
        "c:\\users\\alberto.ferrari\\.agents\\skills",
        "esistenza path: si",
        "branch corrente: `main`",
        "stato git short: clean",
        "albertoferrari71/codex_skills",
        "skill.md",
        "validators",
        "nessun file esterno e' stato modificato",
    ]:
        assert fragment.casefold() in folded


def test_step_0860_dry_run_plan_is_valid_and_non_writing() -> None:
    plan = json.loads(read(PLAN))

    for key in [
        "step",
        "name",
        "status",
        "external_repo",
        "read_only",
        "external_repo_write_allowed",
        "human_gate_required",
        "automatic_commit_push_pr_merge_deploy",
        "allowed_actions",
        "forbidden_actions",
        "expected_evidence",
        "next_step",
    ]:
        assert key in plan

    assert plan["step"] == "0860"
    assert plan["status"] == "dry_run_only"
    assert plan["external_repo"] == "Codex_Skills"
    assert plan["read_only"] is True
    assert plan["external_repo_write_allowed"] is False
    assert plan["human_gate_required"] is True
    assert plan["automatic_commit_push_pr_merge_deploy"] is False
    assert plan["automatic_git_publication_allowed"] is False
    assert plan["next_step"].startswith("0870)")


def test_step_0860_plan_forbids_publication_and_external_write_actions() -> None:
    plan = json.loads(read(PLAN))
    dangerous_true_flags = {
        "external_repo_write_allowed",
        "automatic_commit_push_pr_merge_deploy",
        "automatic_git_publication_allowed",
        "automatic_commit_allowed",
        "automatic_push_allowed",
        "automatic_pr_allowed",
        "automatic_merge_allowed",
        "automatic_deploy_allowed",
        "approve_publish",
        "approve_merge",
        "auto_publish",
        "auto_merge",
        "auto_deploy",
    }

    for key, value in walk_items(plan):
        if key in dangerous_true_flags:
            assert value is False

    forbidden_actions = set(plan["forbidden_actions"])
    for action in [
        "write_external_repo",
        "commit",
        "push",
        "open_pr",
        "merge",
        "deploy",
        "tag",
        "destructive_cleanup",
    ]:
        assert action in forbidden_actions


def test_step_0860_changed_files_preview_is_hypothetical() -> None:
    content = read(PREVIEW)
    folded = content.casefold()

    assert "candidate only - no files modified in external repo" in folded
    assert "nessun file esterno e' stato modificato" in folded
    assert "human gate required" in folded
    assert "0870" in folded


def test_step_0860_evidence_manifest_is_valid_and_confirms_no_external_write() -> None:
    manifest = json.loads(read(EVIDENCE))

    assert manifest["step"] == "0860"
    assert manifest["status"] == "dry_run_completed"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["external_repo_write_performed"] is False
    assert manifest["git_write_actions_performed"] is False
    assert manifest["read_only_checks"]["path_exists"] is True
    assert manifest["read_only_checks"]["git_status_checked"] is True
    assert manifest["human_gate_required_for_next_step"] is True
    assert manifest["next_step"].startswith("0870)")


def test_step_0860_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0860 - Codex_Skills External Workflow Dry-Run Pilot",
            "docs/motor/0860_CODEX_SKILLS_EXTERNAL_WORKFLOW_DRY_RUN_PILOT.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Codex_Skills External Workflow Dry-Run Pilot",
            "Codex_Skills First Controlled Write Pilot",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0860_CODEX_SKILLS_EXTERNAL_WORKFLOW_DRY_RUN_PILOT.md",
            "examples/publish_runner/0860_codex_skills_external_dry_run_plan.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0860 - Codex_Skills External Workflow Dry-Run Pilot",
            "tests/unit/test_codex_skills_external_workflow_dry_run_pilot.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
