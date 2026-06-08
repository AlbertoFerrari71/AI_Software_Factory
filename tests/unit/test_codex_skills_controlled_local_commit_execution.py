from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md"
)
RESULT = (
    ROOT
    / "docs"
    / "motor"
    / "0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_RESULT.md"
)
EVIDENCE = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0890_codex_skills_controlled_local_commit_evidence.example.json"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_0890_artifacts_exist() -> None:
    for path in [DOC, RESULT, EVIDENCE]:
        assert path.exists()


def test_step_0890_evidence_manifest_is_valid_and_non_publishing() -> None:
    manifest = json.loads(read(EVIDENCE))

    assert manifest["step"] == "0890"
    assert manifest["status"] == "local_commit_completed"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["external_repo_path"] == "C:\\Users\\alberto.ferrari\\.agents\\skills"
    assert manifest["external_repo_commit_performed"] is True
    assert manifest["committed_files"] == [
        "docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md"
    ]
    assert manifest["commit_hash"] == "b488745"
    assert manifest["external_repo_push_performed"] is False
    assert manifest["external_repo_pr_performed"] is False
    assert manifest["external_repo_merge_performed"] is False
    assert manifest["external_repo_deploy_performed"] is False
    assert manifest["external_repo_tag_performed"] is False
    assert manifest["human_gate_required_for_push"] is True


def test_step_0890_document_captures_human_decision_and_guardrails() -> None:
    content = read(DOC).casefold()

    for fragment in [
        "b) commit locale controllato su codex_skills, senza push",
        "nessun push",
        "nessuna pr",
        "nessun merge",
        "nessun deploy",
        "nessun tag",
        "qualunque push futuro richiede un human gate separato",
        "0900) codex_skills controlled push or rollback decision",
    ]:
        assert fragment in content


def test_step_0890_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0890 - Codex_Skills Controlled Local Commit Execution",
            "docs/motor/0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "Codex_Skills Controlled Local Commit Execution",
            "0900) Codex_Skills Controlled Push or Rollback Decision",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md",
            "examples/publish_runner/0890_codex_skills_controlled_local_commit_evidence.example.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0890 - Codex_Skills Controlled Local Commit Execution",
            "tests/unit/test_codex_skills_controlled_local_commit_execution.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
