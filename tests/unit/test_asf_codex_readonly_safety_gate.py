from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_readonly_safety_gate.py"
DOC = ROOT / "docs" / "54_ASF_CODEX_READONLY_SAFETY_GATE.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_codex_readonly_safety_gate_template.md"

FORBIDDEN_PATTERNS = [
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
    "workspace-write",
    "danger-full-access",
    "shell=True",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)


def make_git_repo(tmp_path: Path) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git executable not available")

    repo = tmp_path / "target_repo"
    repo.mkdir()
    init_result = run_git(repo, "init", "-b", "main")
    if init_result.returncode != 0:
        init_result = run_git(repo, "init")
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr

    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "user.name", "ASF Test")
    (repo / "README.md").write_text("# Temporary repo\n", encoding="utf-8")
    assert run_git(repo, "add", "README.md").returncode == 0
    commit_result = run_git(repo, "commit", "-m", "initial commit")
    assert commit_result.returncode == 0, commit_result.stdout + commit_result.stderr
    return repo


def write_capture(tmp_path: Path, classification: str) -> Path:
    capture = tmp_path / f"capture_{classification.lower()}.md"
    extra = ""
    if classification == "WARNING":
        extra = "\nOutputs missing: stdout.txt\nManual review required.\n"
    capture.write_text(
        f"""# ASF Codex Invocation Result Capture

- classification: `{classification}`
- exit code: `{"0" if classification != "FAIL" else "2"}`
- target working tree: `CLEAN`
{extra}
""",
        encoding="utf-8",
    )
    return capture


def write_generated_pass_capture(tmp_path: Path) -> Path:
    capture = tmp_path / "generated_pass_capture.md"
    capture.write_text(
        """# ASF Codex Invocation Result Capture

## Summary

- classification: `PASS`
- exit code: `0`
- target working tree: `CLEAN`

## Outputs present

- stdout.txt
- stderr.txt
- exit_code.txt
- codex_readonly_invocation_result.md

## Outputs missing

- none

## Preview outputs present

- readonly_invocation_preview.md
- codex_readonly_command_preview.ps1

## stdout summary

```text
Read-only analysis completed without file modifications.
No target file modifications detected.
```

## Classification criteria

- `PASS`: exit code is `0`, required outputs are present, and target working tree is `CLEAN`.
- `WARNING`: outputs are incomplete or only preview artifacts are present, with no fail signal detected.
- `FAIL`: exit code is nonzero or target working tree is `DIRTY` after read-only execution.

## Limits

- This capture did not invoke Codex.
- This capture did not modify the target repository.
""",
        encoding="utf-8",
    )
    return capture


def base_args(repo: Path, capture: Path, output_dir: Path) -> list[str | Path]:
    return [
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "590",
        "--result-capture",
        capture,
        "--output-dir",
        output_dir,
    ]


def test_readonly_safety_gate_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--result-capture" in result.stdout


def test_readonly_safety_gate_go_for_pass_capture_and_clean_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    capture = write_capture(tmp_path, "PASS")
    output_dir = tmp_path / "gate"

    result = run_script(*base_args(repo, capture, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "readonly_safety_gate.md")
    assert "decisione: `GO_TO_WORKSPACE_WRITE_DESIGN`" in content


def test_readonly_safety_gate_go_for_generated_pass_capture_with_criteria_section(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    capture = write_generated_pass_capture(tmp_path)
    output_dir = tmp_path / "gate"

    result = run_script(*base_args(repo, capture, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "readonly_safety_gate.md")
    assert "decisione: `GO_TO_WORKSPACE_WRITE_DESIGN`" in content
    assert "result capture WARNING evidence detected" not in content
    assert "file modifications after read-only execution" not in content


def test_readonly_safety_gate_no_go_for_fail_capture(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    capture = write_capture(tmp_path, "FAIL")
    output_dir = tmp_path / "gate"

    result = run_script(*base_args(repo, capture, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "readonly_safety_gate.md")
    assert "decisione: `NO_GO`" in content


def test_readonly_safety_gate_hold_for_missing_capture(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    missing_capture = tmp_path / "missing.md"
    output_dir = tmp_path / "gate"

    result = run_script(*base_args(repo, missing_capture, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "readonly_safety_gate.md")
    assert "decisione: `HOLD`" in content
    assert "result capture is missing" in content


def test_readonly_safety_gate_warning_for_incomplete_capture(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    capture = write_capture(tmp_path, "WARNING")
    output_dir = tmp_path / "gate"

    result = run_script(*base_args(repo, capture, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "readonly_safety_gate.md")
    assert "decisione: `WARNING_REVIEW_REQUIRED`" in content


def test_readonly_safety_gate_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC)
    for fragment in ["GO_TO_WORKSPACE_WRITE_DESIGN", "WARNING_REVIEW_REQUIRED", "HOLD", "NO_GO"]:
        assert fragment in doc


def test_readonly_safety_gate_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content
