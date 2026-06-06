from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_BLOCKED = 3

LAST_ARTIFACT_RE = re.compile(r"^LAST[-_].+")
STRUCTURAL_DOC_RE = re.compile(r"^\d{2}_.+")
STANDARD_ARTIFACT_RE = re.compile(r"^\d{4}-\d{2}-.+")
LEGACY_ARTIFACT_RE = re.compile(r"^(?P<step>\d{3,4})-(?P<rest>.+)$")
DIGIT_PREFIX_RE = re.compile(r"^\d+-.+")
KNOWN_ARTIFACT_TYPES = (
    "Richiesta_Generazione",
    "Prompt_Codex",
    "Comando_Eseguito",
    "Output_Completo",
    "Output_Compatto",
)


@dataclass(frozen=True)
class ArtifactPlan:
    old_path: Path
    new_path: Path | None
    action: str
    reason: str


class MigrationError(ValueError):
    pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run/apply migration from legacy artifact names to "
            "NNNN-II-Tipo_Nome.ext."
        )
    )
    parser.add_argument("target_dir", help="Directory to scan recursively.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rename files. Without this flag the command is dry-run only.",
    )
    return parser.parse_args(argv)


def resolve_target(raw_target: str) -> Path:
    if not raw_target or raw_target.strip() != raw_target:
        raise MigrationError("target_dir must be a non-empty path without surrounding spaces.")
    if any(token in raw_target for token in ("*", "?", "\0")):
        raise MigrationError("target_dir must not contain wildcard or null characters.")

    target = Path(raw_target).expanduser().resolve()
    if not target.exists():
        raise MigrationError(f"target_dir does not exist: {target}")
    if not target.is_dir():
        raise MigrationError(f"target_dir is not a directory: {target}")
    return target


def classify_file(path: Path) -> ArtifactPlan:
    name = path.name

    if LAST_ARTIFACT_RE.match(name):
        return ArtifactPlan(path, None, "skip", "historical_last_artifact")
    if STRUCTURAL_DOC_RE.match(name):
        return ArtifactPlan(path, None, "skip", "structural_numbered_doc")
    if STANDARD_ARTIFACT_RE.match(name):
        return ArtifactPlan(path, None, "skip", "already_standard")

    legacy_match = LEGACY_ARTIFACT_RE.match(name)
    if legacy_match:
        step_text = legacy_match.group("step")
        rest = legacy_match.group("rest")
        if not rest.strip():
            return ArtifactPlan(path, None, "ambiguous", "missing_artifact_name")
        if not is_known_artifact_rest(rest):
            return ArtifactPlan(path, None, "ambiguous", "unsupported_artifact_type")
        step_number = int(step_text)
        new_name = f"{step_number:04d}-01-{rest}"
        return ArtifactPlan(path, path.with_name(new_name), "would_rename", "legacy_safe")

    if DIGIT_PREFIX_RE.match(name):
        return ArtifactPlan(path, None, "ambiguous", "unsupported_step_width")

    return ArtifactPlan(path, None, "skip", "not_legacy_artifact")


def is_known_artifact_rest(rest: str) -> bool:
    return any(
        rest == artifact_type
        or rest.startswith(f"{artifact_type}_")
        or rest.startswith(f"{artifact_type}.")
        for artifact_type in KNOWN_ARTIFACT_TYPES
    )


def iter_target_files(target_dir: Path) -> list[Path]:
    return sorted(path for path in target_dir.rglob("*") if path.is_file())


def build_plan(target_dir: Path) -> list[ArtifactPlan]:
    initial = [classify_file(path) for path in iter_target_files(target_dir)]
    candidates = [plan for plan in initial if plan.action == "would_rename" and plan.new_path]
    destination_to_sources: dict[Path, list[Path]] = {}
    for plan in candidates:
        assert plan.new_path is not None
        destination_to_sources.setdefault(plan.new_path, []).append(plan.old_path)

    collision_reasons: dict[Path, str] = {}
    for plan in candidates:
        assert plan.new_path is not None
        if plan.new_path.exists():
            collision_reasons[plan.old_path] = "destination_exists"

    for destination, sources in destination_to_sources.items():
        if len(sources) > 1:
            for source in sources:
                collision_reasons[source] = f"duplicate_new_path:{destination.name}"

    final: list[ArtifactPlan] = []
    for plan in initial:
        if plan.old_path in collision_reasons:
            final.append(
                ArtifactPlan(
                    plan.old_path,
                    plan.new_path,
                    "collision",
                    collision_reasons[plan.old_path],
                )
            )
        else:
            final.append(plan)
    return final


def apply_plan(plans: list[ArtifactPlan]) -> list[ArtifactPlan]:
    blockers = [plan for plan in plans if plan.action in {"collision", "ambiguous"}]
    if blockers:
        blocker_count = len(blockers)
        raise MigrationError(
            f"apply blocked by {blocker_count} collision or ambiguous artifact plan(s)."
        )

    applied: list[ArtifactPlan] = []
    for plan in plans:
        if plan.action != "would_rename":
            applied.append(plan)
            continue

        if plan.new_path is None:
            raise MigrationError(f"internal error: missing new path for {plan.old_path}")
        if plan.new_path.exists():
            raise MigrationError(f"destination exists before rename: {plan.new_path}")
        plan.old_path.rename(plan.new_path)
        applied.append(ArtifactPlan(plan.old_path, plan.new_path, "rename", "applied"))
    return applied


def display_path(path: Path | None, base: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(base)).replace("\\", "/")
    except ValueError:
        return str(path)


def print_report(plans: list[ArtifactPlan], target_dir: Path) -> None:
    print("old_path\tnew_path\taction\treason")
    for plan in plans:
        print(
            "\t".join(
                [
                    display_path(plan.old_path, target_dir),
                    display_path(plan.new_path, target_dir),
                    plan.action,
                    plan.reason,
                ]
            )
        )


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        target_dir = resolve_target(args.target_dir)
        plans = build_plan(target_dir)
        if args.apply:
            plans = apply_plan(plans)
        print_report(plans, target_dir)
    except MigrationError as exc:
        if "apply blocked" in str(exc):
            try:
                args = parse_args(argv)
                target_dir = resolve_target(args.target_dir)
                print_report(build_plan(target_dir), target_dir)
            except MigrationError:
                pass
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_BLOCKED
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
