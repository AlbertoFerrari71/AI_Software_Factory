from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


EXIT_SUCCESS = 0
OK_UNTIL_CHARS = 20_000
OPERATIONAL_ATTENTION_UNTIL_CHARS = 30_000
VERY_HIGH_THRESHOLD_CHARS = 60_000
DEFAULT_MESSAGE = (
    "Il prompt monolitico da 20-30k caratteri resta il default ASF/Codex. "
    "L'advisor e' un guardrail leggero, non una packetizzazione obbligatoria."
)


def render_json(packet: Mapping[str, Any]) -> str:
    return json.dumps(dict(packet), indent=2, sort_keys=True) + "\n"


def classify_prompt_length(char_count: int) -> str:
    if char_count <= OK_UNTIL_CHARS:
        return "ok"
    if char_count <= OPERATIONAL_ATTENTION_UNTIL_CHARS:
        return "operational_attention"
    if char_count <= VERY_HIGH_THRESHOLD_CHARS:
        return "warning"
    return "manual_split_recommended"


def message_for_classification(classification: str) -> str:
    if classification == "ok":
        return DEFAULT_MESSAGE + " Lunghezza OK."
    if classification == "operational_attention":
        return DEFAULT_MESSAGE + " Operativamente accettabile con attenzione leggera."
    if classification == "warning":
        return DEFAULT_MESSAGE + " Sopra 30k caratteri: valutare taglio manuale se il prompt perde leggibilita'."
    return DEFAULT_MESSAGE + " Sopra soglia molto alta: consigliare suddivisione manuale, senza splitter automatico."


def advise_prompt_length(text: str) -> dict[str, Any]:
    char_count = len(text)
    classification = classify_prompt_length(char_count)
    return {
        "classification": classification,
        "char_count": char_count,
        "blocking": False,
        "monolithic_prompt_default": True,
        "automatic_packetization": False,
        "automatic_splitter_enabled": False,
        "human_final_decision": True,
        "thresholds": {
            "ok_until_chars": OK_UNTIL_CHARS,
            "operational_attention_until_chars": OPERATIONAL_ATTENTION_UNTIL_CHARS,
            "warning_above_chars": OPERATIONAL_ATTENTION_UNTIL_CHARS,
            "manual_split_recommended_above_chars": VERY_HIGH_THRESHOLD_CHARS,
        },
        "message": message_for_classification(classification),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lightweight ASF/Codex prompt length advisor.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt-file", help="Prompt file to inspect.")
    source.add_argument("--text", help="Prompt text to inspect.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    text = args.text if args.text is not None else Path(args.prompt_file).read_text(encoding="utf-8")
    packet = advise_prompt_length(text)
    if args.json:
        print(render_json(packet), end="")
    else:
        print(f"{packet['classification']}: {packet['message']}")
    return EXIT_SUCCESS


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
