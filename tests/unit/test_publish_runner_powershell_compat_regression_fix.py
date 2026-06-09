from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "asf_publish_step.ps1"
DOCX_HELPER = ROOT / "scripts" / "asf_minimal_docx.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_runner_avoids_missing_psnative_preference_dependency_safely() -> None:
    content = read(RUNNER)
    native_function = content[
        content.index("function Invoke-NativeChecked") : content.index("function Invoke-ArgvCommand")
    ]

    assert 'Get-Variable -Name "PSNativeCommandUseErrorActionPreference"' in content
    assert "System.Diagnostics.ProcessStartInfo" in native_function
    assert "RedirectStandardOutput" in native_function
    assert "RedirectStandardError" in native_function
    assert "Set-PSNativeCommandUseErrorActionPreferenceSafe" not in native_function
    assert "Restore-PSNativeCommandUseErrorActionPreferenceSafe" not in native_function
    assert "$oldPref = $PSNativeCommandUseErrorActionPreference" not in native_function
    assert "$PSNativeCommandUseErrorActionPreference = $oldPref" not in native_function


def test_stdout_native_runner_has_argumentlist_compatibility_fallback() -> None:
    content = read(RUNNER)
    stdout_function = content[
        content.index("function Invoke-NativeStdoutChecked") : content.index(
            "function Test-RepositoryChangedFileCandidate"
        )
    ]

    assert "function Add-ProcessStartInfoArguments" in content
    assert "ConvertTo-ProcessArgumentString" in content
    assert "Add-ProcessStartInfoArguments -StartInfo $startInfo" in stdout_function


def test_docx_helper_writes_valid_zip_docx(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.docx"
    input_path.write_text("STEP 0921\nDOCX bridge valido\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(DOCX_HELPER),
            "--output",
            str(output_path),
            "--input",
            str(input_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert zipfile.is_zipfile(output_path)
    with zipfile.ZipFile(output_path) as archive:
        names = set(archive.namelist())
        assert "[Content_Types].xml" in names
        assert "_rels/.rels" in names
        assert "word/document.xml" in names
