#!/usr/bin/env python3
"""Install hunyuan-grounded-audit as a standalone CodeBuddy Code skill."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from install_common import SKILL_NAME, InstallError, install_to


def destination_for(scope: str, project: Path | None) -> Path:
    if scope == "project":
        if project is None:
            raise InstallError("--project is required with --scope project")
        project = project.expanduser().resolve()
        if not project.is_dir():
            raise InstallError(f"project directory does not exist: {project}")
        return project / ".codebuddy" / "skills" / SKILL_NAME
    if project is not None:
        raise InstallError("--project is only valid with --scope project")
    return Path.home() / ".codebuddy" / "skills" / SKILL_NAME


def install(scope: str, project: Path | None, force: bool, dry_run: bool) -> Path:
    return install_to(destination_for(scope, project), force, dry_run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Install {SKILL_NAME} as a standalone CodeBuddy Code skill."
    )
    parser.add_argument(
        "--scope",
        choices=("personal", "project"),
        default=None,
        help=(
            "personal installs under ~/.codebuddy/skills; "
            "project installs under <repo>/.codebuddy/skills."
        ),
    )
    parser.add_argument(
        "--project",
        type=Path,
        help="Repository root for --scope project.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite runtime files in an existing installation; local memory is preserved.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the destination and files without writing.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scope = args.scope or ("project" if args.project else "personal")
    if args.scope == "personal" and args.project:
        print("error: --project requires --scope project", file=sys.stderr)
        return 2
    try:
        destination = install(scope, args.project, args.force, args.dry_run)
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("Dry run only; no files were written.")
        return 0

    print(f"Installed {SKILL_NAME} to {destination}")
    if scope == "project":
        print(
            f"Commit .codebuddy/skills/{SKILL_NAME} only if the target repository "
            "is intended to distribute this audit skill."
        )
        print(
            "Project skills can shadow a user-level skill with the same name; "
            "verify the active source with /skills before auditing."
        )
    else:
        print(
            f"Restart CodeBuddy Code, then run /{SKILL_NAME} or use /skills "
            "to verify that this user-level skill is active."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
