from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CODEX_PROMPTS = [
    ROOT / "templates" / "prompts" / "codex_ask_only_prompt.md",
    ROOT / "templates" / "prompts" / "codex_code_controlled_prompt.md",
    ROOT / "templates" / "prompts" / "codex_review_prompt.md",
    ROOT / "templates" / "prompts" / "codex_repair_prompt.md",
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_codex_workflow_document_exists() -> None:
    assert (ROOT / "docs" / "08_CODEX_WORKFLOW.md").exists()


def test_codex_workflow_document_contains_required_sections() -> None:
    content = read_text("docs/08_CODEX_WORKFLOW.md")
    required_fragments = [
        "Codex CLI locale",
        "Codex Web/Cloud",
        "Ask/Suggest",
        "Auto Edit controllato",
        "Review",
        "Repair",
        "Full Auto",
        "no commit, no push, no merge",
        "Output finale obbligatorio",
        "GitHub Workflow STEP 050",
        "Safety Model L0-L4",
        "Procedura locale standard",
        "Safe stop",
        "Rollback",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_step_060_supporting_files_are_present() -> None:
    required_paths = [
        "docs/checklists/060_CODEX_WORKFLOW_CHECKLIST.md",
        "templates/codex_tasks/example_060_codex_workflow_task.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert missing == []


def test_codex_prompts_contain_required_guardrails() -> None:
    required_keywords = [
        "no commit",
        "no push",
        "no merge",
        "safety level",
        "file da non toccare",
        "output atteso",
    ]

    missing_by_prompt: dict[str, list[str]] = {}
    for path in CODEX_PROMPTS:
        content = path.read_text(encoding="utf-8").lower()
        missing = [keyword for keyword in required_keywords if keyword not in content]
        if missing:
            missing_by_prompt[path.relative_to(ROOT).as_posix()] = missing

    assert missing_by_prompt == {}
