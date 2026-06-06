from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2

SKILL_NAME = "as-common-pwsh-command-pack"
INSTALLABLE_RELATIVE_PATH = Path(
    "templates/pwsh_command_pack/export/as-common-pwsh-command-pack/SKILL.md"
)
DESTINATION_FILE_NAME = "SKILL.md"
SUSPICIOUS_PATH_TOKENS = ("*", "?", "\0")
SECRET_MARKERS = (
    "sk" + "-",
    "ghp" + "_",
    "BEGIN " + "PRIVATE KEY",
    "BEGIN OPENSSH " + "PRIVATE KEY",
)
REQUIRED_SKILL_FRAGMENTS = (
    "Safe Bootstrap PowerShell Command Pack",
    "generated `.ps1`",
    "[scriptblock]::Create",
    "ArgList",
    "git status --porcelain=v1 --untracked-files=all",
    "PR-first",
    "numbered and `LAST`",
    "DOCX is best-effort",
    "Do not default to `git push origin main`",
)


class InstallError(ValueError):
    pass


@dataclass(frozen=True)
class InstallPlan:
    source: Path
    destination: Path
    apply: bool
    confirm_overwrite: bool
    target_kind: str
    action: str
    backup_path: Path | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run/apply installer for the as-common-pwsh-command-pack skill export."
    )
    parser.add_argument(
        "--source",
        default=str(INSTALLABLE_RELATIVE_PATH),
        help="Installable SKILL.md source. Defaults to the ASF export folder.",
    )
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument(
        "--target-user-skills",
        action="store_true",
        help="Target %%USERPROFILE%%\\.agents\\skills\\as-common-pwsh-command-pack\\SKILL.md.",
    )
    targets.add_argument(
        "--target-dir",
        help=(
            "Explicit target skills root or exact skill folder. If the path name is not "
            f"{SKILL_NAME}, the installer appends {SKILL_NAME}."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes. Without this flag the installer is dry-run only.",
    )
    parser.add_argument(
        "--confirm-overwrite",
        action="store_true",
        help="Required with --apply when an existing destination SKILL.md has different content.",
    )
    return parser.parse_args(argv)


def resolve_source(root: Path, source_value: str) -> Path:
    source = Path(source_value).expanduser()
    if not source.is_absolute():
        source = root / source
    return source.resolve()


def reject_suspicious_raw_path(raw_path: str, label: str) -> None:
    if not raw_path or raw_path.strip() != raw_path:
        raise InstallError(f"{label} must be a non-empty path without leading or trailing spaces.")
    if any(token in raw_path for token in SUSPICIOUS_PATH_TOKENS):
        raise InstallError(f"{label} contains unsupported wildcard or null characters.")
    raw_parts = re.split(r"[\\/]+", raw_path)
    if ".." in raw_parts:
        raise InstallError(f"{label} must not contain '..' path traversal segments.")


def resolve_target(args: argparse.Namespace) -> tuple[Path, str]:
    if args.target_user_skills:
        skills_root = Path.home() / ".agents" / "skills"
        target_kind = "user-skills"
    else:
        reject_suspicious_raw_path(args.target_dir, "--target-dir")
        skills_root = Path(args.target_dir).expanduser()
        target_kind = "explicit-dir"

    skills_root = skills_root.resolve()
    skill_dir = skills_root if skills_root.name == SKILL_NAME else skills_root / SKILL_NAME
    destination = skill_dir / DESTINATION_FILE_NAME
    return destination.resolve(), target_kind


def validate_source(source: Path) -> str:
    if not source.is_file():
        raise InstallError(f"Source export file does not exist: {source}")

    text = source.read_text(encoding="utf-8")
    if not re.search(r"(?m)^name:\s*[\"']?as-common-pwsh-command-pack[\"']?\s*$", text):
        raise InstallError("Installable SKILL.md does not declare name: as-common-pwsh-command-pack.")

    missing_fragments = [fragment for fragment in REQUIRED_SKILL_FRAGMENTS if fragment not in text]
    if missing_fragments:
        missing = ", ".join(missing_fragments)
        raise InstallError(f"Installable SKILL.md is missing required standard concepts: {missing}")

    leaked_markers = [marker for marker in SECRET_MARKERS if marker in text]
    if leaked_markers:
        raise InstallError("Installable SKILL.md contains a forbidden secret marker.")

    return text


def validate_destination(destination: Path) -> None:
    if destination.name != DESTINATION_FILE_NAME:
        raise InstallError("Destination must resolve to a SKILL.md file.")
    if destination.parent.name != SKILL_NAME:
        raise InstallError(f"Destination skill folder must be named {SKILL_NAME}.")
    if destination.parent.exists() and not destination.parent.is_dir():
        raise InstallError(f"Destination skill path is not a directory: {destination.parent}")
    if destination.exists() and not destination.is_file():
        raise InstallError(f"Destination SKILL.md path is not a file: {destination}")
    if destination.exists():
        existing = destination.read_text(encoding="utf-8")
        if "name:" in existing and not re.search(
            r"(?m)^name:\s*[\"']?as-common-pwsh-command-pack[\"']?\s*$", existing
        ):
            raise InstallError("Existing destination SKILL.md has a different skill name.")


def backup_path_for(destination: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return destination.with_name(f"{destination.name}.bak.{stamp}")


def build_plan(args: argparse.Namespace, root: Path) -> InstallPlan:
    source = resolve_source(root, args.source)
    source_text = validate_source(source)
    destination, target_kind = resolve_target(args)
    validate_destination(destination)

    if not destination.exists():
        action = "create"
        backup_path = None
    else:
        destination_text = destination.read_text(encoding="utf-8")
        if destination_text == source_text:
            action = "noop"
            backup_path = None
        else:
            action = "overwrite"
            backup_path = backup_path_for(destination)
            if args.apply and not args.confirm_overwrite:
                raise InstallError(
                    "Destination SKILL.md exists and differs. Re-run with --apply --confirm-overwrite to back up and overwrite."
                )

    return InstallPlan(
        source=source,
        destination=destination,
        apply=args.apply,
        confirm_overwrite=args.confirm_overwrite,
        target_kind=target_kind,
        action=action,
        backup_path=backup_path,
    )


def apply_plan(plan: InstallPlan) -> None:
    if not plan.apply or plan.action == "noop":
        return

    source_text = plan.source.read_text(encoding="utf-8")
    plan.destination.parent.mkdir(parents=True, exist_ok=True)

    if plan.action == "overwrite":
        if plan.backup_path is None:
            raise InstallError("Internal error: overwrite requires a backup path.")
        plan.backup_path.write_text(plan.destination.read_text(encoding="utf-8"), encoding="utf-8")

    plan.destination.write_text(source_text, encoding="utf-8", newline="\n")


def print_report(plan: InstallPlan) -> None:
    mode = "APPLY" if plan.apply else "DRY-RUN"
    print("as-common-pwsh-command-pack installer")
    print(f"Mode: {mode}")
    print(f"Target kind: {plan.target_kind}")
    print(f"Source: {plan.source}")
    print(f"Destination: {plan.destination}")
    print(f"Action: {plan.action}")
    if plan.backup_path is not None:
        print(f"Backup path: {plan.backup_path}")
    if not plan.apply:
        print("Dry-run only: no files were written. Pass --apply to write.")
    elif plan.action == "noop":
        print("Destination already matches source. No files were written.")
    elif plan.action == "overwrite":
        print("Existing SKILL.md was backed up before overwrite.")
    else:
        print("Install completed.")


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        plan = build_plan(args, repo_root())
        apply_plan(plan)
        print_report(plan)
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
