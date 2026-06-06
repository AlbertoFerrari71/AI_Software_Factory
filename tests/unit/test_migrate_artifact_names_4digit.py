from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "migrate_artifact_names_4digit.py"


def run_migration(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_converts_three_digit_prompt_codex_to_four_digit_iteration(tmp_path: Path) -> None:
    source = tmp_path / "010-Prompt_Codex_test.md"
    source.write_text("prompt", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not source.exists()
    assert (tmp_path / "0010-01-Prompt_Codex_test.md").read_text(encoding="utf-8") == "prompt"


def test_converts_three_digit_output_compatto_to_four_digit_iteration(tmp_path: Path) -> None:
    source = tmp_path / "530-Output_Compatto_x.md"
    source.write_text("compact", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not source.exists()
    assert (tmp_path / "0530-01-Output_Compatto_x.md").read_text(encoding="utf-8") == "compact"


def test_converts_four_digit_without_iteration_only_when_safe(tmp_path: Path) -> None:
    source = tmp_path / "0550-Prompt_Codex_x.md"
    source.write_text("safe", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not source.exists()
    assert (tmp_path / "0550-01-Prompt_Codex_x.md").read_text(encoding="utf-8") == "safe"


def test_does_not_touch_already_standard_artifact(tmp_path: Path) -> None:
    source = tmp_path / "0550-01-Prompt_Codex_x.md"
    source.write_text("standard", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert source.read_text(encoding="utf-8") == "standard"
    assert "already_standard" in result.stdout


def test_does_not_touch_two_digit_structural_roadmap_doc(tmp_path: Path) -> None:
    source = tmp_path / "10_ROADMAP.md"
    source.write_text("roadmap", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert source.exists()
    assert "structural_numbered_doc" in result.stdout


def test_does_not_touch_two_digit_structural_workflow_index_doc(tmp_path: Path) -> None:
    source = tmp_path / "34_PROJECT_WORKFLOW_INDEX.md"
    source.write_text("index", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert source.exists()
    assert "structural_numbered_doc" in result.stdout


def test_does_not_touch_last_artifact(tmp_path: Path) -> None:
    source = tmp_path / "LAST-Prompt_Codex.md"
    source.write_text("last", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert source.exists()
    assert "historical_last_artifact" in result.stdout


def test_dry_run_reports_without_modifying_files(tmp_path: Path) -> None:
    source = tmp_path / "010-Prompt_Codex_test.md"
    source.write_text("prompt", encoding="utf-8")

    result = run_migration(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert source.exists()
    assert not (tmp_path / "0010-01-Prompt_Codex_test.md").exists()
    assert "would_rename" in result.stdout


def test_apply_renames_file(tmp_path: Path) -> None:
    source = tmp_path / "010-Prompt_Codex_test.md"
    destination = tmp_path / "0010-01-Prompt_Codex_test.md"
    source.write_text("prompt", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not source.exists()
    assert destination.exists()
    assert "rename" in result.stdout


def test_collision_is_reported_and_apply_is_blocked(tmp_path: Path) -> None:
    source = tmp_path / "010-Prompt_Codex_test.md"
    destination = tmp_path / "0010-01-Prompt_Codex_test.md"
    source.write_text("legacy", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 3
    assert source.exists()
    assert destination.read_text(encoding="utf-8") == "existing"
    assert "collision" in result.stdout
    assert "destination_exists" in result.stdout


def test_content_is_preserved_after_apply(tmp_path: Path) -> None:
    source = tmp_path / "530-Output_Compatto_x.md"
    content = "# Report\n\nbody\n"
    source.write_text(content, encoding="utf-8")

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "0530-01-Output_Compatto_x.md").read_text(encoding="utf-8") == content


def test_timestamp_is_preserved_as_far_as_filesystem_allows(tmp_path: Path) -> None:
    source = tmp_path / "0550-Prompt_Codex_x.md"
    destination = tmp_path / "0550-01-Prompt_Codex_x.md"
    source.write_text("timestamp", encoding="utf-8")
    old_time = time.time() - 3600
    os.utime(source, (old_time, old_time))
    before_mtime = source.stat().st_mtime

    result = run_migration(tmp_path, "--apply")

    assert result.returncode == 0, result.stdout + result.stderr
    assert destination.exists()
    assert abs(destination.stat().st_mtime - before_mtime) < 2
