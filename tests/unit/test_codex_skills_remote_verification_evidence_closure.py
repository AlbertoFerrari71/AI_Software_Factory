from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0920_CODEX_SKILLS_REMOTE_VERIFICATION_AND_EVIDENCE_CLOSURE.md"
)
EVIDENCE_REPORT = (
    ROOT / "docs" / "motor" / "0920_CODEX_SKILLS_REMOTE_PUSH_EVIDENCE_REPORT.md"
)
EVIDENCE_JSON = (
    ROOT
    / "examples"
    / "publish_runner"
    / "0920_codex_skills_remote_verification_evidence.example.json"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_0920_artifacts_exist() -> None:
    for path in [CLOSURE_DOC, EVIDENCE_REPORT, EVIDENCE_JSON]:
        assert path.exists()


def test_step_0920_evidence_json_is_valid_and_records_push() -> None:
    manifest = json.loads(read(EVIDENCE_JSON))

    assert manifest["step"] == "0920"
    assert manifest["external_repo"] == "Codex_Skills"
    assert manifest["external_repo_push_step"] == "0910A-3"
    assert manifest["push_completed"] is True
    assert manifest["push_exit_code"] == 0
    assert manifest["push_output_summary"] == "36b065d..bec96ff main -> main"

    pushed_hashes = {commit["hash"] for commit in manifest["pushed_commits"]}
    assert "b488745" in pushed_hashes
    assert "bec96ff" in pushed_hashes

    forbidden = manifest["forbidden_actions_not_performed"]
    for action in [
        "commit",
        "add",
        "pr",
        "merge",
        "deploy",
        "tag",
        "reset",
        "clean",
        "pull",
        "fetch",
        "rebase",
        "force_push",
    ]:
        assert forbidden[action] is True

    note = manifest["remote_verification_note"].casefold()
    assert "no fetch or pull" in note
    assert "local tracking state after successful push" in note


def test_step_0920_documents_capture_context_and_guardrails() -> None:
    for path in [CLOSURE_DOC, EVIDENCE_REPORT]:
        content = read(path)
        folded = content.casefold()

        assert "$env:USERPROFILE" in content
        assert "0910A-3" in content
        assert "Codex_Skills" in content
        assert "36b065d..bec96ff main -> main" in content
        assert "b488745" in content
        assert "bec96ff" in content
        assert "remote verification is based on local tracking state" in folded
        assert "without fetch/pull" in folded

        for fragment in ["PR", "merge", "deploy", "tag"]:
            assert fragment in content
