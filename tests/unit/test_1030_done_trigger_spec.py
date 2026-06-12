from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "motor" / "1030_DONE_TRIGGER_SPEC.md"


def test_done_trigger_spec_documents_codex_and_pwsh_triggers() -> None:
    text = SPEC.read_text(encoding="utf-8")

    for fragment in [
        "Codex fatto",
        "Codex ok",
        "CF",
        "COK",
        "Pwsh fatto",
        "Pwsh ok",
        "PF",
        "POK",
        "PowerShell fatto",
    ]:
        assert fragment in text


def test_done_trigger_spec_documents_bridge_first_and_no_invention_rule() -> None:
    text = SPEC.read_text(encoding="utf-8")

    for fragment in [
        "cercare automaticamente il report/output nel Bridge",
        "chiedere ad Alberto di incollare solo se il Bridge non e' accessibile",
        "PASS",
        "FAIL",
        "BLOCKED",
        "LIVE_FAILED_SAFE",
        "PARTIAL_PASS",
        "non inventare nulla",
        "AMBIGUOUS",
    ]:
        assert fragment in text
