from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_prompt_length_advisor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_prompt_length_advisor", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_small_prompt_is_ok() -> None:
    module = load_module()

    packet = module.advise_prompt_length("x" * 100)

    assert packet["classification"] == "ok"
    assert packet["blocking"] is False


def test_20_to_30k_prompt_is_operational_attention() -> None:
    module = load_module()

    packet = module.advise_prompt_length("x" * 25_000)

    assert packet["classification"] == "operational_attention"
    assert packet["monolithic_prompt_default"] is True


def test_above_30k_prompt_is_warning_without_splitter() -> None:
    module = load_module()

    packet = module.advise_prompt_length("x" * 30_001)

    assert packet["classification"] == "warning"
    assert packet["automatic_packetization"] is False
    assert packet["automatic_splitter_enabled"] is False


def test_very_long_prompt_recommends_manual_split_only() -> None:
    module = load_module()

    packet = module.advise_prompt_length("x" * 60_001)

    assert packet["classification"] == "manual_split_recommended"
    assert packet["human_final_decision"] is True
    assert "suddivisione manuale" in packet["message"]


def test_policy_message_documents_monolithic_default() -> None:
    module = load_module()

    packet = module.advise_prompt_length("x")

    assert "Il prompt monolitico da 20-30k caratteri resta il default ASF/Codex" in packet["message"]
    assert "guardrail leggero" in packet["message"]
    assert "non una packetizzazione obbligatoria" in packet["message"]
