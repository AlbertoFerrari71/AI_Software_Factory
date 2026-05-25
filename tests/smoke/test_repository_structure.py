from __future__ import annotations

import importlib
from pathlib import Path


def test_package_is_importable() -> None:
    package = importlib.import_module("ai_software_factory")
    assert package.__version__ == "0.3.0"


def test_required_root_files_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    required_files = [
        "README.md",
        "AGENTS.md",
        "CHANGELOG.md",
        "LICENSE",
        ".env.example",
        ".gitignore",
        "pyproject.toml",
        "docs/05_SECURITY_MODEL.md",
        "docs/10_ROADMAP.md",
        "docs/11_DECISIONS.md",
        "policies/safety_policy.v0.json",
        "policies/safety_policy.v0.yaml",
        "policies/path_policy.v0.json",
        ".github/workflows/ci.yml",
        ".github/pull_request_template.md",
    ]

    missing = [path for path in required_files if not (root / path).exists()]
    assert missing == []


def test_required_directories_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    required_dirs = [
        "docs",
        "docs/checklists",
        "policies",
        "templates",
        "templates/safety",
        "src/ai_software_factory",
        "tests/smoke",
        "tests/unit",
        ".github/ISSUE_TEMPLATE",
        ".github/workflows",
    ]

    missing = [path for path in required_dirs if not (root / path).is_dir()]
    assert missing == []
