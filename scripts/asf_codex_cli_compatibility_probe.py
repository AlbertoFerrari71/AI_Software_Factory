from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class ProbeRun:
    label: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe local Codex CLI metadata compatibility without calling the model.",
    )
    parser.add_argument("--codex-command", default="codex", help="Codex command name or path. Default: codex.")
    parser.add_argument(
        "--output-json",
        default="tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json",
        help="Stable JSON output path.",
    )
    parser.add_argument("--output-markdown", help="Optional Markdown summary output path.")
    parser.add_argument("--timeout-seconds", type=int, default=10, help="Per-command timeout. Default: 10.")
    return parser.parse_args(argv)


def resolve_path(value: str | Path, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def excerpt(value: str, *, limit: int = 2000) -> str:
    cleaned = value.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "\n..."


def run_probe(label: str, command: list[str], timeout_seconds: int) -> ProbeRun:
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
        return ProbeRun(label, command, result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired as exc:
        return ProbeRun(label, command, 124, exc.stdout or "", exc.stderr or "probe timed out")
    except OSError as exc:
        return ProbeRun(label, command, 127, "", str(exc))


def support_entry(supported: bool, evidence: str) -> dict[str, Any]:
    return {"supported": supported, "evidence": evidence}


def contains_flag(text: str, flag: str) -> bool:
    return flag.casefold() in text.casefold()


def detect_stdin_dash(exec_help: str) -> bool:
    lowered = exec_help.casefold()
    if "stdin" in lowered and re.search(r"(?m)(^|\s)-(\s|$|,)", exec_help):
        return True
    if "read from stdin" in lowered or "prompt from stdin" in lowered:
        return True
    return False


def build_probe_report(*, codex_command: str, resolved: str | None, probes: list[ProbeRun]) -> dict[str, Any]:
    combined_help = "\n".join(f"{probe.stdout}\n{probe.stderr}" for probe in probes)
    executable_present = resolved is not None
    version_run = next((probe for probe in probes if probe.label == "version"), None)
    help_run = next((probe for probe in probes if probe.label == "help"), None)
    exec_help_run = next((probe for probe in probes if probe.label == "exec_help"), None)
    exec_help = "" if exec_help_run is None else f"{exec_help_run.stdout}\n{exec_help_run.stderr}"
    help_text = "" if help_run is None else f"{help_run.stdout}\n{help_run.stderr}"

    exec_supported = bool(exec_help_run and exec_help_run.returncode == 0) or "exec" in help_text.casefold()
    classifications = ["CODEX_AVAILABLE", "CLI_PROBE_AVAILABLE"] if executable_present else ["CODEX_NOT_AVAILABLE"]
    return {
        "schema_version": "1.0",
        "report_type": "asf_codex_cli_compatibility_probe",
        "mode": "metadata-only",
        "calls_model": False,
        "codex_command": codex_command,
        "executable": {
            "present": executable_present,
            "path": resolved or "",
        },
        "classifications": classifications,
        "version": {
            "available": bool(version_run and version_run.returncode == 0),
            "stdout": excerpt(version_run.stdout if version_run else ""),
            "stderr": excerpt(version_run.stderr if version_run else ""),
            "exit_code": None if version_run is None else version_run.returncode,
        },
        "support": {
            "exec": support_entry(exec_supported, "exec help returned success or top-level help mentions exec"),
            "sandbox": support_entry(contains_flag(combined_help, "--sandbox"), "--sandbox found in help output"),
            "read_only": support_entry("read-only" in combined_help.casefold(), "read-only found in help output"),
            "json": support_entry(contains_flag(combined_help, "--json"), "--json found in help output"),
            "output_last_message": support_entry(
                contains_flag(combined_help, "--output-last-message"),
                "--output-last-message found in help output",
            ),
            "stdin_dash": support_entry(detect_stdin_dash(exec_help), "stdin prompt using dash found in exec help"),
        },
        "probes": [
            {
                "label": probe.label,
                "command": probe.command,
                "exit_code": probe.returncode,
                "stdout_excerpt": excerpt(probe.stdout),
                "stderr_excerpt": excerpt(probe.stderr),
            }
            for probe in probes
        ],
        "limits": [
            "metadata-only probe",
            "did not call the model",
            "did not run codex exec with a prompt",
            "did not modify any repository",
        ],
    }


def markdown_summary(report: dict[str, Any]) -> str:
    support = report["support"]
    lines = [
        "# ASF Codex CLI Compatibility Probe",
        "",
        "## Summary",
        "",
        f"- mode: `{report['mode']}`",
        f"- calls-model: `{report['calls_model']}`",
        f"- codex-command: `{report['codex_command']}`",
        f"- executable-present: `{report['executable']['present']}`",
        f"- executable-path: `{report['executable']['path'] or '(none)'}`",
        f"- classifications: `{', '.join(report['classifications'])}`",
        "",
        "## Support Evidence",
        "",
    ]
    for key in sorted(support):
        lines.append(f"- {key}: `{support[key]['supported']}` - {support[key]['evidence']}")
    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- Metadata-only probe.",
            "- Codex model execution was not attempted.",
            "- No repository target was modified.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    root = repo_root()
    args = parse_args(argv)
    if args.timeout_seconds <= 0:
        raise InputError("--timeout-seconds must be positive.")

    command = args.codex_command.strip() or "codex"
    resolved = shutil.which(command)
    probes: list[ProbeRun] = []
    if resolved:
        probes = [
            run_probe("version", [resolved, "--version"], args.timeout_seconds),
            run_probe("help", [resolved, "--help"], args.timeout_seconds),
            run_probe("exec_help", [resolved, "exec", "--help"], args.timeout_seconds),
        ]

    report = build_probe_report(codex_command=command, resolved=resolved, probes=probes)
    output_json = resolve_path(args.output_json, base=root)
    write_json(output_json, report)
    print(f"Codex CLI compatibility probe JSON generated: {output_json}")
    print(f"Classifications: {', '.join(report['classifications'])}")

    if args.output_markdown:
        output_markdown = resolve_path(args.output_markdown, base=root)
        write_text(output_markdown, markdown_summary(report))
        print(f"Codex CLI compatibility probe Markdown generated: {output_markdown}")
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
