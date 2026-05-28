from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_VALIDATION_PASSED = 0  # exit code 0
EXIT_VALIDATION_FAILED = 1  # exit code 1
EXIT_USAGE_ERROR = 2  # exit code 2

SUPPORTED_SUFFIXES = {".md", ".txt"}


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains_any(text: str, candidates: list[str]) -> bool:
    lowered = text.casefold()
    return any(candidate.casefold() in lowered for candidate in candidates)


def contains_all(text: str, candidates: list[str]) -> bool:
    lowered = text.casefold()
    return all(candidate.casefold() in lowered for candidate in candidates)


def check_required_sections(text: str) -> list[CheckResult]:
    checks = [
        CheckResult(
            "Project context",
            contains_any(text, ["CONTESTO PROGETTO", "Project context", "contesto progetto"]),
        ),
        CheckResult(
            "Branch instructions",
            contains_any(text, ["BRANCH DA USARE", "target branch", "branch dedicato"]),
        ),
        CheckResult(
            "Allowed scope",
            contains_any(text, ["ALLOWED SCOPE", "Allowed scope", "scope ammesso"]),
        ),
        CheckResult(
            "Forbidden scope",
            contains_any(text, ["FORBIDDEN SCOPE", "Forbidden scope", "scope vietato"]),
        ),
        CheckResult(
            "Forbidden actions",
            contains_any(text, ["FORBIDDEN ACTIONS", "Forbidden actions", "azioni vietate"]),
        ),
        CheckResult("Verification Gate", contains_any(text, ["Verification Gate"])),
        CheckResult("Documentation Sync", contains_any(text, ["Documentation Sync"])),
        CheckResult(
            "Soft Protection awareness",
            contains_any(text, ["Soft Protection", "Soft Protection Guardrails", "soft guardrails"]),
        ),
    ]
    return checks


def check_forbidden_actions(text: str) -> list[CheckResult]:
    action_groups = [
        ("No commit", ["Non fare commit", "do not commit", "no commit"]),
        ("No push", ["Non fare push", "do not push", "no push"]),
        ("No PR", ["Non aprire PR", "do not open PR", "do not create PR", "no PR"]),
        ("No merge", ["Non fare merge", "do not merge", "no merge"]),
    ]

    return [
        CheckResult(name, contains_any(text, candidates), "Required forbidden action")
        for name, candidates in action_groups
    ]


def check_final_report(text: str) -> list[CheckResult]:
    required_terms = [
        "STEP ESEGUITO",
        "STATO",
        "FILE CREATI",
        "FILE MODIFICATI",
        "VERIFICHE ESEGUITE",
        "PROSSIMO STEP",
        "Tempo impiegato",
    ]
    return [
        CheckResult("Final Codex report", contains_all(text, required_terms))
    ]


def validate_text(text: str) -> tuple[list[CheckResult], list[str]]:
    checks = [
        *check_required_sections(text),
        *check_forbidden_actions(text),
        *check_final_report(text),
    ]
    warnings: list[str] = []

    if not contains_any(text, ["VERIFICHE NON ESEGUITE", "Checks not run", "verifiche non eseguite"]):
        warnings.append("Final report should mention checks not run when applicable.")

    return checks, warnings


def print_report(path: Path, checks: list[CheckResult], warnings: list[str]) -> None:
    print("Prompt Packet Validation Lite")
    print(f"File: {path}")
    print()
    print("Required checks:")
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        suffix = f" - {check.detail}" if check.detail and not check.passed else ""
        print(f"[{status}] {check.name}{suffix}")

    print()
    print("Warnings:")
    if warnings:
        for warning in warnings:
            print(f"[WARN] {warning}")
    else:
        print("[WARN] None")

    result = "PASS" if all(check.passed for check in checks) else "FAIL"
    print()
    print(f"Result: {result}")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: python scripts/validate_task_packet.py <task-packet.md|task-packet.txt>", file=sys.stderr)
        return EXIT_USAGE_ERROR

    path = Path(argv[0])
    if not path.exists():
        print(f"Input error: file not found: {path}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if not path.is_file():
        print(f"Input error: path is not a file: {path}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        print("Input error: only .md and .txt files are supported.", file=sys.stderr)
        return EXIT_USAGE_ERROR

    try:
        text = read_text(path)
    except UnicodeDecodeError:
        print(f"Input error: file is not valid UTF-8: {path}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    checks, warnings = validate_text(text)
    print_report(path, checks, warnings)

    if all(check.passed for check in checks):
        return EXIT_VALIDATION_PASSED
    return EXIT_VALIDATION_FAILED


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
