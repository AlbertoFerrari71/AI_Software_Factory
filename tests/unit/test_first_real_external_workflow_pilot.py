from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "motor" / "0850_FIRST_REAL_EXTERNAL_WORKFLOW_PILOT.md"
EXAMPLE = ROOT / "examples" / "publish_runner" / "0850_external_workflow_pilot_plan.example.json"


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


def test_step_0850_document_exists_and_covers_external_pilot_scope() -> None:
    assert DOC.exists()
    content = read(DOC)
    folded = content.casefold()

    for fragment in [
        "external workflow pilot",
        "codex_skills",
        "family_photo_organizer",
        "mansionario_vivo",
        "rischio alto",
        "safety boundaries",
        "human gate",
        "0860) Codex_Skills External Workflow Dry-Run Pilot",
    ]:
        assert fragment.casefold() in folded


def test_step_0850_document_recommends_codex_skills_and_keeps_other_repos_bounded() -> None:
    content = read(DOC)
    folded = content.casefold()

    assert "repo consigliata" in folded
    assert "codex_skills" in folded
    assert "family_photo_organizer" in folded
    assert "candidata futura" in folded
    assert "non e' adatto come primo pilot esterno" in folded
    assert "nessuna repo esterna e' stata modificata" in folded


def test_step_0850_example_manifest_is_valid_planning_only_json() -> None:
    assert EXAMPLE.exists()
    manifest = json.loads(read(EXAMPLE))

    for key in [
        "step",
        "name",
        "status",
        "recommended_external_repo",
        "risk_level",
        "human_gate_required",
        "automatic_commit_push_pr_merge_deploy",
        "allowed_actions_in_next_step",
        "forbidden_actions",
        "expected_evidence",
        "next_step",
    ]:
        assert key in manifest

    assert manifest["is_example"] is True
    assert manifest["not_live_evidence"] is True
    assert manifest["not_for_automatic_publish"] is True
    assert manifest["step"] == "0850"
    assert manifest["status"] == "planning_only"
    assert manifest["recommended_external_repo"] == "Codex_Skills"
    assert manifest["human_gate_required"] is True
    assert manifest["automatic_commit_push_pr_merge_deploy"] is False
    assert manifest["automatic_git_publication_allowed"] is False
    assert manifest["external_repo_write_allowed"] is False
    assert manifest["next_step"].startswith("0860)")


def test_step_0850_example_manifest_forbids_publication_actions() -> None:
    manifest = json.loads(read(EXAMPLE))
    dangerous_true_flags = {
        "automatic_commit_push_pr_merge_deploy",
        "automatic_git_publication_allowed",
        "external_repo_write_allowed",
        "automatic_commit_allowed",
        "automatic_push_allowed",
        "automatic_pr_allowed",
        "automatic_merge_allowed",
        "automatic_deploy_allowed",
        "automatic_tag_allowed",
        "approve_publish",
        "approve_merge",
        "auto_publish",
        "auto_merge",
        "auto_deploy",
    }

    for key, value in walk_items(manifest):
        if key in dangerous_true_flags:
            assert value is False

    forbidden_actions = set(manifest["forbidden_actions"])
    for action in [
        "commit",
        "push",
        "open_pr",
        "merge",
        "deploy",
        "tag",
        "destructive_cleanup",
    ]:
        assert action in forbidden_actions

    serialized = json.dumps(manifest, sort_keys=True).casefold()
    for forbidden in [
        '"automatic_commit_push_pr_merge_deploy": true',
        '"automatic_git_publication_allowed": true',
        '"external_repo_write_allowed": true',
        '"automatic_commit_allowed": true',
        '"automatic_push_allowed": true',
        '"automatic_merge_allowed": true',
        '"automatic_deploy_allowed": true',
    ]:
        assert forbidden not in serialized


def test_step_0850_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0850 - First Real External Workflow Pilot",
            "docs/motor/0850_FIRST_REAL_EXTERNAL_WORKFLOW_PILOT.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "First Real External Workflow Pilot",
            "Codex_Skills External Workflow Dry-Run Pilot",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0850_FIRST_REAL_EXTERNAL_WORKFLOW_PILOT.md",
            "examples/publish_runner/0850_external_workflow_pilot_plan.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0850 - First Real External Workflow Pilot",
            "tests/unit/test_first_real_external_workflow_pilot.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
