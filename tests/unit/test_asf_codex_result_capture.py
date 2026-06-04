from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_result_capture.py"
DOC = ROOT / "docs" / "53_ASF_CODEX_INVOCATION_RESULT_CAPTURE.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_codex_invocation_result_capture_template.md"


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


def write_invocation(invocation_dir: Path, *, exit_code: int = 0) -> None:
    invocation_dir.mkdir(parents=True)
    (invocation_dir / "stdout.txt").write_text("analysis complete\n", encoding="utf-8")
    (invocation_dir / "stderr.txt").write_text("", encoding="utf-8")
    (invocation_dir / "exit_code.txt").write_text(f"{exit_code}\n", encoding="utf-8")
    (invocation_dir / "codex_readonly_invocation_result.md").write_text(
        f"""# ASF Codex Read-Only Invocation Result

- exit code: `{exit_code}`
- classification: `{"PASS" if exit_code == 0 else "FAIL"}`
""",
        encoding="utf-8",
    )


def base_args(repo: Path, invocation_dir: Path, output_dir: Path) -> list[str | Path]:
    return [
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "590",
        "--invocation-dir",
        invocation_dir,
        "--output-dir",
        output_dir,
    ]


def test_result_capture_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--invocation-dir" in result.stdout


def test_result_capture_classifies_pass_for_zero_exit_and_clean_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    invocation_dir = tmp_path / "invocation"
    output_dir = tmp_path / "capture"
    write_invocation(invocation_dir, exit_code=0)

    result = run_script(*base_args(repo, invocation_dir, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    capture = output_dir / "Temp_Project" / "step_590" / "codex_result_capture.md"
    content = read(capture)
    assert "classification: `PASS`" in content
    assert "analysis complete" in content


def test_result_capture_classifies_fail_for_nonzero_exit(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    invocation_dir = tmp_path / "invocation"
    output_dir = tmp_path / "capture"
    write_invocation(invocation_dir, exit_code=7)

    result = run_script(*base_args(repo, invocation_dir, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "codex_result_capture.md")
    assert "classification: `FAIL`" in content
    assert "exit code: `7`" in content


def test_result_capture_accepts_utf8_bom_exit_code(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    invocation_dir = tmp_path / "invocation"
    output_dir = tmp_path / "capture"
    write_invocation(invocation_dir, exit_code=0)
    (invocation_dir / "exit_code.txt").write_bytes(b"\xef\xbb\xbf0\r\n")

    result = run_script(*base_args(repo, invocation_dir, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "codex_result_capture.md")
    assert "classification: `PASS`" in content
    assert "exit code: `0`" in content


def test_result_capture_classifies_fail_for_dirty_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    invocation_dir = tmp_path / "invocation"
    output_dir = tmp_path / "capture"
    write_invocation(invocation_dir, exit_code=0)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = run_script(*base_args(repo, invocation_dir, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "codex_result_capture.md")
    assert "classification: `FAIL`" in content
    assert "target working tree: `DIRTY`" in content


def test_result_capture_classifies_warning_for_preview_only(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    invocation_dir = tmp_path / "invocation"
    output_dir = tmp_path / "capture"
    invocation_dir.mkdir()
    (invocation_dir / "readonly_invocation_preview.md").write_text("Codex was not executed.\n", encoding="utf-8")

    result = run_script(*base_args(repo, invocation_dir, output_dir))

    assert result.returncode == 0, result.stdout + result.stderr
    content = read(output_dir / "Temp_Project" / "step_590" / "codex_result_capture.md")
    assert "classification: `WARNING`" in content
    assert "readonly_invocation_preview.md" in content


def test_result_capture_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC)
    for fragment in ["PASS", "WARNING", "FAIL", "stdout", "stderr", "exit code"]:
        assert fragment in doc
