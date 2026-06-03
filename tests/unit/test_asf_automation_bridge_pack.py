from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


NEW_FILES = [
    "scripts/asf_human_approval_gate.py",
    "scripts/asf_codex_invocation_dry_run.py",
    "docs/49_ASF_HUMAN_APPROVAL_GATE.md",
    "docs/50_ASF_CODEX_INVOCATION_DESIGN.md",
    "docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md",
    "templates/codex_tasks/asf_human_approval_gate_template.md",
    "templates/codex_tasks/asf_codex_invocation_dry_run_template.md",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_automation_bridge_pack_files_exist() -> None:
    for relative_path in NEW_FILES:
        assert (ROOT / relative_path).exists(), relative_path


def test_automation_bridge_pack_docs_cover_required_topics() -> None:
    combined = "\n".join(read(path) for path in NEW_FILES if path.endswith(".md"))

    required_fragments = [
        "Human Approval Gate",
        "GO",
        "WARNING",
        "HOLD",
        "NO-GO",
        "Codex Invocation Design",
        "Level 0",
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
        "Level 5",
        "codex exec",
        "read-only",
        "workspace-write-preview",
        "DO NOT RUN",
        "Alberto",
    ]
    for fragment in required_fragments:
        assert fragment in combined


def test_health_check_includes_automation_bridge_pack_files() -> None:
    health = read("scripts/check_workflow_health.py")

    required_fragments = [
        "docs/49_ASF_HUMAN_APPROVAL_GATE.md",
        "docs/50_ASF_CODEX_INVOCATION_DESIGN.md",
        "docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md",
        "scripts/asf_human_approval_gate.py",
        "scripts/asf_codex_invocation_dry_run.py",
        "templates/codex_tasks/asf_human_approval_gate_template.md",
        "templates/codex_tasks/asf_codex_invocation_dry_run_template.md",
    ]
    for fragment in required_fragments:
        assert fragment in health


def test_status_dashboard_includes_automation_bridge_pack_files() -> None:
    dashboard = read("scripts/show_workflow_status.py")

    for fragment in [
        "docs/49_ASF_HUMAN_APPROVAL_GATE.md",
        "docs/50_ASF_CODEX_INVOCATION_DESIGN.md",
        "docs/51_ASF_CODEX_INVOCATION_DRY_RUN_PACK.md",
        "scripts/asf_human_approval_gate.py",
        "scripts/asf_codex_invocation_dry_run.py",
    ]:
        assert fragment in dashboard


def test_automation_bridge_pack_changelog_decision_and_next_step_are_present() -> None:
    changelog = read("CHANGELOG.md")
    decisions = read("docs/11_DECISIONS.md")
    roadmap = read("docs/10_ROADMAP.md")

    assert "MEGA-STEP 370-390 - ASF Automation Bridge Pack" in changelog
    assert "DEC-053 - ASF Automation Bridge Pack" in decisions
    assert "STEP 400 - ASF Codex Invocation Read-Only Prototype" in roadmap
    assert "ASF Codex Invocation Read-Only Prototype" in roadmap


def test_automation_bridge_operational_scripts_do_not_execute_forbidden_actions() -> None:
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
    ]

    for relative_path in [
        "scripts/asf_human_approval_gate.py",
        "scripts/asf_codex_invocation_dry_run.py",
    ]:
        content = read(relative_path)
        for pattern in forbidden_patterns:
            assert pattern not in content

    dry_run_script = read("scripts/asf_codex_invocation_dry_run.py")
    assert "codex exec" in dry_run_script
    assert '["codex"' not in dry_run_script
    assert "['codex'" not in dry_run_script
    assert "shell=True" not in dry_run_script
