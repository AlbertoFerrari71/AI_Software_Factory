from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PROMPT_TEMPLATE_FILES = [
    ROOT / "templates" / "prompts" / "chatgpt_project_prompt.md",
    ROOT / "templates" / "prompts" / "codex_ask_only_prompt.md",
    ROOT / "templates" / "prompts" / "codex_code_controlled_prompt.md",
    ROOT / "templates" / "prompts" / "codex_review_prompt.md",
    ROOT / "templates" / "prompts" / "codex_repair_prompt.md",
]

TASK_TEMPLATE_FILES = [
    ROOT / "templates" / "codex_tasks" / "codex_task_packet_template.md",
    ROOT / "templates" / "codex_tasks" / "example_040_family_photo_organizer_prompt_packet.md",
]

REQUIRED_SECTIONS = [
    "## Obiettivo",
    "## Contesto",
    "## Livello rischio L0-L4",
    "## File da leggere",
    "## File modificabili",
    "## File vietati",
    "## Vincoli",
    "## Output atteso",
    "## Criteri di accettazione",
    "## Test / verifica",
    "## Rollback / safe stop",
    "## Cosa NON fare",
]


def test_prompt_packet_documentation_exists() -> None:
    required_files = [
        ROOT / "docs" / "19_PROMPT_PACKET_GENERATOR.md",
        ROOT / "docs" / "checklists" / "040_PROMPT_PACKET_CHECKLIST.md",
    ]

    missing = [path.relative_to(ROOT).as_posix() for path in required_files if not path.exists()]
    assert missing == []


def test_main_prompt_templates_exist() -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in PROMPT_TEMPLATE_FILES if not path.exists()]
    assert missing == []


def test_codex_task_templates_exist() -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in TASK_TEMPLATE_FILES if not path.exists()]
    assert missing == []


def test_prompt_templates_have_required_sections() -> None:
    missing_sections: dict[str, list[str]] = {}

    for path in PROMPT_TEMPLATE_FILES + TASK_TEMPLATE_FILES:
        content = path.read_text(encoding="utf-8")
        missing = [section for section in REQUIRED_SECTIONS if section not in content]
        if missing:
            missing_sections[path.relative_to(ROOT).as_posix()] = missing

    assert missing_sections == {}


def test_templates_reference_safety_levels_and_safe_stop() -> None:
    for path in PROMPT_TEMPLATE_FILES + TASK_TEMPLATE_FILES:
        content = path.read_text(encoding="utf-8")
        assert "L0" in content
        assert "L4" in content
        assert "safe stop" in content.lower()


def test_family_photo_organizer_example_is_read_only() -> None:
    example = TASK_TEMPLATE_FILES[1].read_text(encoding="utf-8")
    assert "Family Photo Organizer" in example
    assert "L0 - Read only" in example
    assert "Nessuno" in example
    assert "Non cancellare" in example
