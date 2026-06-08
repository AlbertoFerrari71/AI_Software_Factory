from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "motor" / "0830_MVP_REAL_STEP_PILOT_4_SLIGHTLY_MORE_OPERATIONAL.md"
MANIFEST = ROOT / "examples" / "publish_runner" / "0830_prepare_config_pilot.json"


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


def test_step_0830_document_exists_and_covers_operational_flow() -> None:
    assert DOC.exists()
    content = read(DOC)
    folded = content.casefold()

    for fragment in [
        "PrepareConfig",
        "scope discovery",
        "review umana dello scope",
        "Phase B",
        "Phase C",
        "Bridge/LAST validation",
        "gate bloccanti",
        "warning non bloccanti",
        "fallback",
        "LF/CRLF",
        "DOCX",
        "no-false-`COMPLETATO`",
    ]:
        assert fragment.casefold() in folded


def test_step_0830_manifest_exists_and_is_safe_json() -> None:
    assert MANIFEST.exists()
    manifest = json.loads(read(MANIFEST))

    for key in [
        "step",
        "name",
        "branch",
        "intent",
        "risk_level",
        "expected_files",
        "changed_files",
        "phase_a_checks",
        "phase_c_checks",
        "allow_no_github_checks_reported",
        "notes",
    ]:
        assert key in manifest

    assert manifest["step"] == "0830"
    assert manifest["is_example"] is True
    assert manifest["not_for_automatic_publish"] is True
    assert manifest["expected_files"]
    assert manifest["changed_files"]
    assert manifest["allow_no_github_checks_reported"] is True


def test_step_0830_manifest_does_not_auto_approve_merge_or_deploy() -> None:
    manifest = json.loads(read(MANIFEST))
    dangerous_true_flags = {
        "approve_merge",
        "approve_deploy",
        "auto_merge",
        "auto_deploy",
        "automatic_merge_allowed",
        "automatic_deploy_allowed",
        "automatic_publish_allowed",
    }

    for key, value in walk_items(manifest):
        if key in dangerous_true_flags:
            assert value is False

    serialized = json.dumps(manifest, sort_keys=True).casefold()
    for forbidden in [
        '"approve_merge": true',
        '"approve_deploy": true',
        '"auto_merge": true',
        '"auto_deploy": true',
        '"automatic_merge_allowed": true',
        '"automatic_deploy_allowed": true',
        '"automatic_publish_allowed": true',
    ]:
        assert forbidden not in serialized


def test_step_0830_references_are_linked_from_core_docs() -> None:
    required = {
        ROOT / "README.md": [
            "STEP 0830",
            "docs/motor/0830_MVP_REAL_STEP_PILOT_4_SLIGHTLY_MORE_OPERATIONAL.md",
        ],
        ROOT / "docs" / "10_ROADMAP.md": [
            "MVP Real Step Pilot 4 - Slightly More Operational",
            "Completato con warning",
        ],
        ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md": [
            "docs/motor/0830_MVP_REAL_STEP_PILOT_4_SLIGHTLY_MORE_OPERATIONAL.md",
            "examples/publish_runner/0830_prepare_config_pilot.json",
        ],
        ROOT / "CHANGELOG.md": [
            "STEP 0830 - MVP Real Step Pilot 4 - Slightly More Operational",
            "tests/unit/test_mvp_real_step_pilot_4.py",
        ],
    }

    for path, fragments in required.items():
        content = read(path)
        for fragment in fragments:
            assert fragment in content
