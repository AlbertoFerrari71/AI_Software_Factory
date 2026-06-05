from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DOCS = [
    ROOT / "docs" / "61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md",
    ROOT / "docs" / "62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md",
    ROOT / "docs" / "63_ASF_CODEX_READONLY_DECISION_GATE.md",
]
SCRIPTS = [
    ROOT / "scripts" / "asf_codex_readonly_diagnostics.py",
    ROOT / "scripts" / "asf_codex_cli_compatibility_probe.py",
    ROOT / "scripts" / "asf_codex_readonly_decision_gate.py",
]
TEMPLATES = [
    ROOT / "templates" / "codex_tasks" / "asf_codex_readonly_diagnostics_template.md",
    ROOT / "templates" / "codex_tasks" / "asf_codex_cli_compatibility_probe_template.md",
    ROOT / "templates" / "codex_tasks" / "asf_codex_readonly_decision_gate_template.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_460_480_docs_scripts_and_templates_exist() -> None:
    for path in [*DOCS, *SCRIPTS, *TEMPLATES]:
        assert path.exists(), path


def test_step_460_480_docs_describe_required_decisions_and_classifications() -> None:
    docs = "\n".join(read(path) for path in DOCS)
    for fragment in [
        "CODEX_NOT_AVAILABLE",
        "STDERR_NONEMPTY",
        "TARGET_DIRTY_AFTER_READONLY",
        "GO_TO_WORKSPACE_WRITE_DESIGN",
        "GO_TO_MORE_READONLY_TRIALS",
        "WARNING_REVIEW_REQUIRED",
        "HOLD",
        "NO_GO",
        "read-only",
    ]:
        assert fragment in docs


def test_step_460_480_is_linked_from_workflow_indexes_and_changelog() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "docs" / "10_ROADMAP.md",
            ROOT / "docs" / "11_DECISIONS.md",
            ROOT / "docs" / "21_DOCUMENTATION_SYNC.md",
            ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md",
            ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md",
            ROOT / "docs" / "36_WORKFLOW_QUICK_REFERENCE.md",
            ROOT / "docs" / "38_WORKFLOW_COMMAND_COOKBOOK.md",
            ROOT / "docs" / "39_WORKFLOW_STATUS_DASHBOARD.md",
        ]
    )
    for fragment in [
        "docs/61_ASF_CODEX_READONLY_DIAGNOSTICS_HARDENING.md",
        "docs/62_ASF_CODEX_CLI_COMPATIBILITY_PROBE.md",
        "docs/63_ASF_CODEX_READONLY_DECISION_GATE.md",
        "scripts/asf_codex_readonly_diagnostics.py",
        "scripts/asf_codex_cli_compatibility_probe.py",
        "scripts/asf_codex_readonly_decision_gate.py",
    ]:
        assert fragment in combined
