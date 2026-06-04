from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


NEW_FILES = [
    "scripts/asf_codex_readonly_invoke.py",
    "scripts/asf_codex_result_capture.py",
    "scripts/asf_codex_readonly_safety_gate.py",
    "docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md",
    "docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md",
    "docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md",
    "templates/codex_tasks/asf_codex_readonly_invocation_template.md",
    "templates/codex_tasks/asf_codex_invocation_result_capture_template.md",
    "templates/codex_tasks/asf_codex_readonly_safety_gate_template.md",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_readonly_invocation_pack_files_exist() -> None:
    for relative_path in NEW_FILES:
        assert (ROOT / relative_path).exists(), relative_path


def test_readonly_invocation_pack_docs_cover_required_topics() -> None:
    combined = "\n".join(read(path) for path in NEW_FILES if path.endswith(".md"))

    required_fragments = [
        "Read-Only Invocation",
        "execute-readonly",
        "YES_I_APPROVE_READONLY_CODEX_EXECUTION",
        "PASS",
        "WARNING",
        "FAIL",
        "GO_TO_WORKSPACE_WRITE_DESIGN",
        "NO_GO",
        "read-only",
        "Alberto",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_health_check_includes_readonly_invocation_pack_files() -> None:
    health = read("scripts/check_workflow_health.py")

    for fragment in NEW_FILES:
        assert fragment in health


def test_status_dashboard_includes_readonly_invocation_pack_files() -> None:
    dashboard = read("scripts/show_workflow_status.py")

    for fragment in [
        "docs/52_ASF_CODEX_READONLY_INVOCATION_PROTOTYPE.md",
        "docs/53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md",
        "docs/54_ASF_CODEX_READONLY_SAFETY_GATE.md",
        "scripts/asf_codex_readonly_invoke.py",
        "scripts/asf_codex_result_capture.py",
        "scripts/asf_codex_readonly_safety_gate.py",
    ]:
        assert fragment in dashboard


def test_readonly_invocation_pack_changelog_decision_and_next_step_are_present() -> None:
    changelog = read("CHANGELOG.md")
    decisions = read("docs/11_DECISIONS.md")
    roadmap = read("docs/10_ROADMAP.md")

    assert "MEGA-STEP 400-420 - ASF Codex Read-Only Invocation Prototype Pack" in changelog
    assert "DEC-054 - ASF Codex Read-Only Invocation Prototype Pack" in decisions
    assert "STEP 430 - ASF Codex Read-Only Invocation First Manual Trial" in roadmap


def test_readonly_invocation_pack_scripts_avoid_forbidden_patterns() -> None:
    forbidden_patterns = [
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
        "gh release",
        "git merge",
        "git reset --hard",
        "git clean",
        "Set-ExecutionPolicy",
        "setx PATH",
        "workspace-write",
        "danger-full-access",
        "shell=True",
    ]

    for relative_path in [
        "scripts/asf_codex_readonly_invoke.py",
        "scripts/asf_codex_result_capture.py",
        "scripts/asf_codex_readonly_safety_gate.py",
    ]:
        content = read(relative_path)
        for pattern in forbidden_patterns:
            assert pattern not in content
