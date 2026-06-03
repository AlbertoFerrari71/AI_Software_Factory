from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_codex_report_intake.py"
DOC = ROOT / "docs" / "47_ASF_CODEX_REPORT_INTAKE.md"
TEMPLATE = ROOT / "templates" / "codex_tasks" / "asf_codex_report_intake_template.md"


FORBIDDEN_PATTERNS = [
    "git commit",
    "git push",
    "gh pr create",
    "gh pr merge",
    "gh release",
    "git merge",
    "git reset --hard",
    "git clean",
    "codex run",
    "codex exec",
    "gh api",
    "api.github.com",
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
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


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


def write_codex_report(path: Path) -> None:
    path.write_text(
        """# Report Codex

A. STEP ESEGUITO
580) Example step

B. STATO
Completato

C. BRANCH CORRENTE
step-580-example

D. FILE CREATI
- docs/example.md

E. FILE MODIFICATI
- README.md

F. COMANDI ESEGUITI
- python -m pytest: PASS

G. VERIFICHE NON ESEGUITE
nessuna

H. RISCHI / NOTE
nessuna

I. CONFERME VINCOLI
vincoli rispettati

J. PROSSIMO STEP
590) Next step

K. RIEPILOGO FINALE
Step eseguito: 580) Example step
""",
        encoding="utf-8",
    )


def test_codex_report_intake_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--report-path" in result.stdout
    assert "--repo-path" in result.stdout


def test_codex_report_intake_generates_report(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    report_path = tmp_path / "codex_report.md"
    output_dir = tmp_path / "intake"
    write_codex_report(report_path)

    result = run_script(
        "--report-path",
        report_path,
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "580",
        "--output-dir",
        output_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    intake = output_dir / "Temp_Project" / "step_580" / "codex_report_intake.md"
    assert intake.exists()

    content = read(intake)
    required_fragments = [
        "ASF Codex Report Intake",
        "Temp_Project",
        "580",
        "PASS",
        "Target Git status",
        "working tree",
        "Sections found",
        "Sections missing",
        "non equivale ad approval",
    ]
    lowered = content.casefold()
    for fragment in required_fragments:
        assert fragment.casefold() in lowered


def test_codex_report_intake_missing_report_fails(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)

    result = run_script(
        "--report-path",
        tmp_path / "missing.md",
        "--project-name",
        "Temp_Project",
        "--repo-path",
        repo,
        "--step",
        "580",
        "--output-dir",
        tmp_path / "intake",
    )

    assert result.returncode != 0
    assert "report-path" in result.stderr


def test_codex_report_intake_files_exist_and_docs_are_present() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert TEMPLATE.exists()

    doc = read(DOC).casefold()
    for fragment in ["PASS", "WARNING", "FAIL", "non equivale ad approval", "non invoca Codex"]:
        assert fragment.casefold() in doc


def test_codex_report_intake_script_avoids_operational_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content
