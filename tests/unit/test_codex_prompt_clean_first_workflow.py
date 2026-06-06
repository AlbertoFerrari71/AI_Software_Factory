from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_step_535_primary_clean_first_rule_is_documented() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "AGENTS.md",
            "docs/08_CODEX_WORKFLOW.md",
        ]
    )

    for fragment in [
        "Clean Codex prompt first by default",
        "PowerShell only when archiving, auditing, or publishing",
        "prompt Codex pulito",
        "senza wrapper PowerShell",
        "Bridge Dropbox",
        "ChatGPT Bridge",
        "file numerati",
        "file `LAST`",
        "audit trail",
        "intake gate",
        "pwsh/publication command pack",
        "Non mischiare prompt Codex e script PowerShell",
    ]:
        assert fragment in combined


def test_step_535_workflow_references_keep_layers_separate() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
        ]
    )

    for fragment in [
        "prompt Codex pulito",
        "eventuale salvataggio Bridge",
        "intake gate",
        "publication command pack",
        "non e' il wrapper default dei prompt Codex",
        "Non mischiare prompt Codex e script PowerShell",
        "Codex command pack PowerShell",
        "pwsh/publication command pack",
    ]:
        assert fragment in combined


def test_step_535_tracking_documents_are_updated() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "README.md",
            "CHANGELOG.md",
            "docs/10_ROADMAP.md",
            "docs/11_DECISIONS.md",
        ]
    )

    for fragment in [
        "STEP 535 - Codex Prompt Clean-First Workflow Update",
        "Codex Prompt Clean-First Workflow Update",
        "DEC-063 - Codex prompt clean-first workflow",
        "540) OpenAI API Adapter Controlled Live Execution Pack",
    ]:
        assert fragment in combined


def test_step_535_docs_do_not_make_powershell_the_default_prompt_wrapper() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "AGENTS.md",
            "docs/08_CODEX_WORKFLOW.md",
            "docs/34_PROJECT_WORKFLOW_INDEX.md",
            "docs/36_WORKFLOW_QUICK_REFERENCE.md",
            "docs/38_WORKFLOW_COMMAND_COOKBOOK.md",
            "docs/64_ASF_PWSH_COMMAND_PACK_SKILL_HARDENING.md",
        ]
    ).casefold()

    forbidden_fragments = [
        "ogni prompt codex deve sempre essere generato tramite powershell",
        "every codex prompt must always be generated through powershell",
        "powershell wrapper di default",
        "default powershell wrapper",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in combined
