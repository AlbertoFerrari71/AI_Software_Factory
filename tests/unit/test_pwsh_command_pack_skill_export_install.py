from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = ROOT / "templates" / "pwsh_command_pack" / "export" / "as-common-pwsh-command-pack"
EXPORT_SKILL = EXPORT_DIR / "SKILL.md"
INSTALLER = ROOT / "scripts" / "install_pwsh_command_pack_skill.py"
DOC = ROOT / "docs" / "71_ASF_PWSH_COMMAND_PACK_SKILL_EXPORT_INSTALL.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_installer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSTALLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_export_folder_and_skill_file_exist() -> None:
    assert EXPORT_DIR.is_dir()
    assert EXPORT_SKILL.is_file()


def test_export_skill_contains_name_and_required_standard() -> None:
    content = read(EXPORT_SKILL)

    required_fragments = [
        "name: as-common-pwsh-command-pack",
        "Safe Bootstrap PowerShell Command Pack",
        "generated `.ps1`",
        "parse-check",
        "ArgList",
        "git status --porcelain=v1 --untracked-files=all",
        "PR-first",
        "NNNN-II-Tipo_Nome.ext",
        "Do not generate `LAST-*` files",
        "Non usare `Set-Clipboard -Path`",
        "Get-Content -Path <file> -Raw | Set-Clipboard",
        "DOCX is best-effort",
        "Do not default to `git push origin main`",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_installer_dry_run_does_not_write(tmp_path: Path) -> None:
    target_root = tmp_path / "skills-root"

    result = run_installer("--target-dir", str(target_root))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Mode: DRY-RUN" in result.stdout
    assert "Dry-run only" in result.stdout
    assert not target_root.exists()


def test_installer_apply_is_required_before_write(tmp_path: Path) -> None:
    target_root = tmp_path / "skills-root"

    result = run_installer("--target-dir", str(target_root))

    assert result.returncode == 0, result.stdout + result.stderr
    assert not (target_root / "as-common-pwsh-command-pack" / "SKILL.md").exists()


def test_installer_apply_writes_to_explicit_target(tmp_path: Path) -> None:
    target_root = tmp_path / "skills-root"

    result = run_installer("--target-dir", str(target_root), "--apply")

    installed = target_root / "as-common-pwsh-command-pack" / "SKILL.md"
    assert result.returncode == 0, result.stdout + result.stderr
    assert installed.is_file()
    assert read(installed) == read(EXPORT_SKILL)


def test_installer_requires_confirm_overwrite_for_different_existing_file(tmp_path: Path) -> None:
    target_root = tmp_path / "skills-root"
    skill_dir = target_root / "as-common-pwsh-command-pack"
    skill_dir.mkdir(parents=True)
    installed = skill_dir / "SKILL.md"
    installed.write_text("---\nname: as-common-pwsh-command-pack\n---\nold\n", encoding="utf-8")

    result = run_installer("--target-dir", str(target_root), "--apply")

    assert result.returncode == 2
    assert "--confirm-overwrite" in result.stderr
    assert read(installed).endswith("old\n")
    assert not list(skill_dir.glob("SKILL.md.bak.*"))


def test_installer_backups_before_overwrite_when_confirmed(tmp_path: Path) -> None:
    target_root = tmp_path / "skills-root"
    skill_dir = target_root / "as-common-pwsh-command-pack"
    skill_dir.mkdir(parents=True)
    installed = skill_dir / "SKILL.md"
    installed.write_text("---\nname: as-common-pwsh-command-pack\n---\nold\n", encoding="utf-8")

    result = run_installer("--target-dir", str(target_root), "--apply", "--confirm-overwrite")

    backups = list(skill_dir.glob("SKILL.md.bak.*"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(backups) == 1
    assert read(backups[0]).endswith("old\n")
    assert read(installed) == read(EXPORT_SKILL)


def test_installer_rejects_suspicious_target_path(tmp_path: Path) -> None:
    target_with_traversal = tmp_path / ".." / "skills-root"

    result = run_installer("--target-dir", str(target_with_traversal))

    assert result.returncode == 2
    assert "path traversal" in result.stderr


def test_installer_uses_no_personal_hardcoded_default_and_does_not_delete() -> None:
    content = read(INSTALLER)

    forbidden_fragments = [
        "alberto.ferrari",
        "C:\\Users\\alberto",
        "shutil.rmtree",
        "Remove-Item",
        ".unlink(",
        "rmdir(",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in content


def test_documentation_mentions_dry_run_apply_backup_and_external_limits() -> None:
    content = read(DOC)

    required_fragments = [
        "dry-run",
        "--apply",
        "--target-user-skills",
        "--target-dir",
        "Codex non installa direttamente",
        "Codex_Skills",
        "backup",
        "templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_new_files_do_not_contain_real_secret_markers() -> None:
    combined = "\n".join(read(path) for path in [EXPORT_SKILL, INSTALLER, DOC])

    forbidden_markers = [
        "sk-",
        "ghp_",
        "BEGIN PRIVATE KEY",
        "BEGIN OPENSSH PRIVATE KEY",
    ]
    for marker in forbidden_markers:
        assert marker not in combined
