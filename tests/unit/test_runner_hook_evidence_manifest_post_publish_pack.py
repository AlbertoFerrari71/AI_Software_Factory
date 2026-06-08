from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0840_RUNNER_HOOK_EVIDENCE_MANIFEST_POST_PUBLISH_PACK.md"
)
EXAMPLE = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0840_post_publish_evidence_manifest.example.json"
)


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


def test_step_0840_document_exists_and_defines_post_publish_pack() -> None:
    assert DOC.exists()
    content = read(DOC)
    folded = content.casefold()

    for fragment in [
        "post-publish evidence pack",
        "pr",
        "merge commit",
        "check finali",
        "bridge output",
        "last",
        "manifest/evidence json",
        "next step",
    ]:
        assert fragment.casefold() in folded


def test_step_0840_document_distinguishes_gates_warnings_outputs_and_evidence() -> None:
    content = read(DOC)
    folded = content.casefold()

    for fragment in [
        "gate bloccanti",
        "warning accettati",
        "output accessori",
        "evidence post-publish",
        "non deve eseguire commit, push, pr, merge, deploy o tag",
    ]:
        assert fragment.casefold() in folded


def test_step_0840_example_manifest_is_valid_and_contains_minimum_fields() -> None:
    assert EXAMPLE.exists()
    manifest = json.loads(read(EXAMPLE))

    for key in [
        "step",
        "status",
        "pr_number",
        "merge_commit",
        "checks",
        "bridge_outputs",
        "next_step",
    ]:
        assert key in manifest

    assert manifest["is_example"] is True
    assert manifest["not_live_evidence"] is True
    assert manifest["not_for_automatic_publish"] is True
    assert manifest["step"] == "0830"
    assert manifest["status"] == "published"
    assert manifest["pr_number"] == 76
    assert manifest["merge_commit"] == "a759546"
    assert isinstance(manifest["checks"], dict)
    assert isinstance(manifest["bridge_outputs"], dict)


def test_step_0840_example_manifest_does_not_authorize_automatic_publication() -> None:
    manifest = json.loads(read(EXAMPLE))
    dangerous_true_flags = {
        "automatic_commit_allowed",
        "automatic_push_allowed",
        "automatic_pr_allowed",
        "automatic_merge_allowed",
        "automatic_deploy_allowed",
        "automatic_tag_allowed",
        "approve_publish",
        "approve_merge",
        "approve_deploy",
        "auto_publish",
        "auto_merge",
        "auto_deploy",
    }

    for key, value in walk_items(manifest):
        if key in dangerous_true_flags:
            assert value is False

    serialized = json.dumps(manifest, sort_keys=True).casefold()
    for forbidden in [
        '"automatic_commit_allowed": true',
        '"automatic_push_allowed": true',
        '"automatic_pr_allowed": true',
        '"automatic_merge_allowed": true',
        '"automatic_deploy_allowed": true',
        '"automatic_tag_allowed": true',
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
    ]:
        assert forbidden not in serialized


def test_step_0840_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0840 - Runner Hook Evidence Manifest Post-Publish Pack",
            "docs/motor/0840_RUNNER_HOOK_EVIDENCE_MANIFEST_POST_PUBLISH_PACK.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Runner Hook Evidence Manifest Post-Publish Pack",
            "Completato",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0840_RUNNER_HOOK_EVIDENCE_MANIFEST_POST_PUBLISH_PACK.md",
            "examples/publish_runner/0840_post_publish_evidence_manifest.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0840 - Runner Hook Evidence Manifest Post-Publish Pack",
            "tests/unit/test_runner_hook_evidence_manifest_post_publish_pack.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
