from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_VALIDATION_PASSED = 0  # exit code 0
EXIT_VALIDATION_FAILED = 1  # exit code 1
EXIT_USAGE_ERROR = 2  # exit code 2
MODE_LITE = "Lite"  # Output line: Mode: Lite
MODE_STRICT = "Strict"  # Output line: Mode: Strict

SUPPORTED_SUFFIXES = {".md", ".txt"}

UNTRUSTED_BEGIN = "BEGIN_UNTRUSTED_CONTENT"
UNTRUSTED_END = "END_UNTRUSTED_CONTENT"
UNTRUSTED_BLOCK_RE = re.compile(
    rf"(?ims)^{UNTRUSTED_BEGIN}\s*$.*?^{UNTRUSTED_END}\s*$"
)

PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "ignore previous instructions",
        re.compile(
            r"\b(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+"
            r"(instructions|rules|context)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "ignora istruzioni precedenti",
        re.compile(
            r"\bignora\s+(tutte\s+)?(le\s+)?(istruzioni|regole)\s+"
            r"(precedenti|sopra)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "ignore AGENTS.md or CLAUDE.md",
        re.compile(
            r"\b(ignore|disregard|bypass|ignora|bypassa)\s+`?"
            r"(AGENTS\.md|CLAUDE\.md)`?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "disregard system or developer instructions",
        re.compile(
            r"\b(ignore|disregard|override|bypass)\s+(the\s+)?"
            r"(system|developer)\s+(prompt|message|instructions|rules)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "reveal system prompt",
        re.compile(
            r"\b(reveal|print|show|dump|read)\s+(the\s+)?"
            r"(system\s+prompt|hidden\s+instructions|developer\s+message)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "disable tests or gates",
        re.compile(
            r"\b(disable|skip|bypass|disattiva|salta|bypassa)\s+"
            r"(tests?|verification gate|gate|verifiche|test)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "execute publish action",
        re.compile(
            r"\b(run|execute|perform|esegui|fai)\s+.*\b"
            r"(commit|push|merge|deploy|publish|pubblica|rilascia)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unauthorized publish action",
        re.compile(
            r"(\b(commit|push|merge|deploy|publish)\b.*\b"
            r"(without|no|senza)\s+(human\s+|manual\s+)?"
            r"(approval|authorization|approvazione|autorizzazione)\b)"
            r"|(\b(push|merge|deploy)\b.*\b(directly|direttamente)\b.*"
            r"\b(main|production|prod)\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "exfiltrate secrets",
        re.compile(
            r"\b(exfiltrate|leak|dump|print|send|copy|read|reveal|export|upload|"
            r"esfiltra|stampa|leggi|rivela|invia|copia)\s+.*\b"
            r"(secret|secrets|token|api\s*key|password|\.env|"
            r"env(?:ironment)?\s+variables?|credenziali)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "mark PASS without evidence",
        re.compile(
            r"\b(mark|set|declare|write|report|marca|dichiara)\s+.*\b"
            r"(PASS|passed|success|successo)\b.*\b(without|senza)\s+.*\b"
            r"(evidence|prove|verifiche|tests?|test)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "bypass guardrails",
        re.compile(
            r"\b(bypass|disable|override|ignore|skip|bypassa|disattiva)\s+.*\b"
            r"(guardrails?|soft protection|human gate|approval gate|safety gate|gate umano)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "LAST artifact authoritative",
        re.compile(
            r"(\b(treat|use|usa)\s+.*LAST-[A-Za-z0-9_.-]+.*"
            r"(authoritative|autoritativ|source of truth|fonte)\b)"
            r"|(\bLAST-[A-Za-z0-9_.-]+.*"
            r"(authoritative|autoritativ|source of truth|fonte)\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "destructive cleanup",
        re.compile(
            r"\b(destructive cleanup|cleanup distruttivo|delete workspace|"
            r"wipe workspace|remove all files|clean before validation)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "tool output command injection",
        re.compile(
            r"\b(tool output|output dello strumento|stdout|stderr)\b.*\b"
            r"(run|execute|esegui|launch)\b.*\b"
            r"(command|cleanup|deploy|push|merge|validation)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "override human approval",
        re.compile(
            r"\b(override|bypass|skip|ignore|forza)\s+.*\b"
            r"(human approval|manual approval|approval|approvazione umana|"
            r"approvazione manuale|human gate)\b",
            re.IGNORECASE,
        ),
    ),
]


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


def contains_each_group(text: str, groups: list[list[str]]) -> bool:
    return all(contains_any(text, group) for group in groups)


def strip_untrusted_content_blocks(text: str) -> str:
    return UNTRUSTED_BLOCK_RE.sub("", text)


def untrusted_content_blocks(text: str) -> list[str]:
    return [match.group(0) for match in UNTRUSTED_BLOCK_RE.finditer(text)]


def find_prompt_injection_markers(text: str) -> list[str]:
    trusted_surface = strip_untrusted_content_blocks(text)
    markers: list[str] = []
    for label, pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(trusted_surface):
            markers.append(label)
    return markers


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


def check_untrusted_content_fences(text: str) -> list[CheckResult]:
    begin_count = len(re.findall(rf"(?im)^{UNTRUSTED_BEGIN}\s*$", text))
    end_count = len(re.findall(rf"(?im)^{UNTRUSTED_END}\s*$", text))

    if begin_count != end_count:
        return [
            CheckResult(
                "Untrusted content fences",
                False,
                "BEGIN_UNTRUSTED_CONTENT and END_UNTRUSTED_CONTENT markers must be balanced.",
            )
        ]

    for block in untrusted_content_blocks(text):
        if not contains_all(
            block,
            [
                "source:",
                "content_type:",
                "instructions_inside_are_not_authoritative: true",
                "---",
            ],
        ):
            return [
                CheckResult(
                    "Untrusted content fences",
                    False,
                    "Each untrusted block requires source, content_type, non-authoritative flag, and separator.",
                )
            ]

    return [CheckResult("Untrusted content fences", True)]


def check_prompt_injection_markers(text: str) -> list[CheckResult]:
    markers = find_prompt_injection_markers(text)
    detail = ""
    if markers:
        detail = "Unfenced prompt injection marker(s): " + ", ".join(markers)
    return [CheckResult("Prompt injection markers fenced", not markers, detail)]


def check_strict_branch_instructions(text: str) -> list[CheckResult]:
    return [
        CheckResult(
            "Strict branch instructions",
            contains_each_group(
                text,
                [
                    ["BRANCH DA USARE", "branch dedicato", "target branch"],
                    ["main"],
                    ["working tree pulito", "working tree"],
                ],
            ),
            "Requires branch instructions, main, and working tree.",
        )
    ]


def check_strict_scope(text: str) -> list[CheckResult]:
    return [
        CheckResult(
            "Strict allowed scope",
            contains_each_group(
                text,
                [
                    ["ALLOWED SCOPE", "Allowed scope", "scope ammesso"],
                    ["docs/**", "tests/**", "templates/**", "scripts/**"],
                ],
            ),
            "Requires allowed scope plus at least one concrete allowed path pattern.",
        ),
        CheckResult(
            "Strict forbidden scope",
            contains_each_group(
                text,
                [
                    ["FORBIDDEN SCOPE", "Forbidden scope", "scope vietato"],
                    ["src/**"],
                    ["policies/**"],
                    [".github/workflows/ci.yml", "CI"],
                    ["secret", ".env"],
                ],
            ),
            "Requires forbidden scope with src, policies, CI, and secret/.env references.",
        ),
    ]


def check_strict_forbidden_actions(text: str) -> list[CheckResult]:
    action_groups = [
        ("Strict no commit", ["Non fare commit", "do not commit", "no commit"]),
        ("Strict no push", ["Non fare push", "do not push", "no push"]),
        ("Strict no PR", ["Non aprire PR", "do not open PR", "do not create PR", "no PR"]),
        ("Strict no merge", ["Non fare merge", "do not merge", "no merge"]),
        (
            "Strict no direct GitHub changes",
            [
                "Non modificare direttamente GitHub",
                "Non applicare configurazioni GitHub reali",
                "do not modify GitHub",
            ],
        ),
        (
            "Strict no hook install or hooksPath change",
            [
                "Non installare hook Git",
                "Non modificare git config core.hooksPath",
                "do not install Git hooks",
                "do not modify git config core.hooksPath",
            ],
        ),
        (
            "Strict no ASF_ALLOW_MAIN_BYPASS",
            [
                "Non usare bypass ASF_ALLOW_MAIN_BYPASS",
                "Non usare `ASF_ALLOW_MAIN_BYPASS`",
                "Codex non deve usare `ASF_ALLOW_MAIN_BYPASS`",
                "do not use ASF_ALLOW_MAIN_BYPASS",
                "no ASF_ALLOW_MAIN_BYPASS",
            ],
        ),
    ]
    return [
        CheckResult(name, contains_any(text, candidates), "Required in Strict mode.")
        for name, candidates in action_groups
    ]


def check_strict_verification_gate(text: str) -> list[CheckResult]:
    return [
        CheckResult(
            "Strict Verification Gate",
            contains_each_group(
                text,
                [
                    ["Verification Gate"],
                    ["python -m pytest"],
                    ["git diff --check"],
                    ["git status --short"],
                ],
            ),
            "Requires Verification Gate with pytest, diff check, and git status.",
        )
    ]


def check_strict_documentation_sync(text: str) -> list[CheckResult]:
    return [
        CheckResult(
            "Strict Documentation Sync",
            contains_each_group(
                text,
                [
                    ["Documentation Sync"],
                    ["CHANGELOG.md"],
                    ["docs/10_ROADMAP.md", "Roadmap"],
                    ["docs/11_DECISIONS.md", "Decisions"],
                ],
            ),
            "Requires Documentation Sync with changelog, roadmap, and decisions.",
        )
    ]


def check_strict_soft_protection(text: str) -> list[CheckResult]:
    return [
        CheckResult(
            "Strict Soft Protection",
            contains_each_group(
                text,
                [
                    ["Soft Protection", "soft guardrails"],
                    ["core.hooksPath", ".githooks"],
                    ["non installare hook", "hook opt-in", "do not install hooks"],
                ],
            ),
            "Requires Soft Protection, hook path awareness, and opt-in/no-install rule.",
        )
    ]


def check_strict_final_report(text: str) -> list[CheckResult]:
    required_terms = [
        "A) STEP ESEGUITO",
        "B) STATO",
        "C) FILE CREATI",
        "D) FILE MODIFICATI",
        "E) VERIFICHE ESEGUITE",
        "F) VERIFICHE NON ESEGUITE",
        "G) RISCHI / NOTE",
        "H) PROSSIMO STEP CONSIGLIATO",
        "I) RIEPILOGO FINALE OBBLIGATORIO",
        "Step eseguito",
        "Tempo impiegato",
        "Stato step",
        "Prossimo step",
    ]
    return [
        CheckResult("Strict Final Codex report", contains_all(text, required_terms))
    ]


def check_strict_sections(text: str) -> list[CheckResult]:
    return [
        *check_strict_branch_instructions(text),
        *check_strict_scope(text),
        *check_strict_forbidden_actions(text),
        *check_strict_verification_gate(text),
        *check_strict_documentation_sync(text),
        *check_strict_soft_protection(text),
        *check_strict_final_report(text),
    ]


def validate_text(text: str, *, strict: bool = False) -> tuple[list[CheckResult], list[str]]:
    checks = [
        *check_required_sections(text),
        *check_forbidden_actions(text),
        *check_final_report(text),
        *check_untrusted_content_fences(text),
        *check_prompt_injection_markers(text),
    ]
    warnings: list[str] = []

    if not contains_any(text, ["VERIFICHE NON ESEGUITE", "Checks not run", "verifiche non eseguite"]):
        warnings.append("Final report should mention checks not run when applicable.")

    if strict:
        checks.extend(check_strict_sections(text))
        if not contains_any(text, ["golden samples", "valid sample", "invalid samples", "examples/task_packets"]):
            warnings.append("Strict mode recommends referencing golden samples or examples/task_packets.")

    return checks, warnings


def print_report(path: Path, mode: str, checks: list[CheckResult], warnings: list[str]) -> None:
    print("Prompt Packet Validation")
    print(f"Mode: {mode}")
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
    strict = False
    args = list(argv)

    if "--strict" in args:
        strict = True
        args.remove("--strict")

    if len(args) != 1:
        print("Usage: python scripts/validate_task_packet.py [--strict] <task-packet.md|task-packet.txt>", file=sys.stderr)
        return EXIT_USAGE_ERROR

    path = Path(args[0])
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

    checks, warnings = validate_text(text, strict=strict)
    print_report(path, MODE_STRICT if strict else MODE_LITE, checks, warnings)

    if all(check.passed for check in checks):
        return EXIT_VALIDATION_PASSED
    return EXIT_VALIDATION_FAILED


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
