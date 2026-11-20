#!/usr/bin/env python3
"""Build a deterministic WorkBuddy skill archive from the runtime files."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Sequence

from install_common import PACKAGE_NAME, ROOT, SKILL_NAME, InstallError, load_runtime_files


def _version() -> str:
    manifest = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        raise InstallError("skill.json has no version")
    return version


def _output_path(output: Path | None) -> Path:
    if output is None:
        return ROOT / "dist" / "workbuddy" / f"{PACKAGE_NAME}-{_version()}-workbuddy.zip"
    resolved = output.expanduser().resolve()
    if resolved.suffix.lower() != ".zip":
        raise InstallError("WorkBuddy package output must end with .zip")
    return resolved


def build_package(output: Path | None = None) -> Path:
    destination = _output_path(output)
    files = load_runtime_files()

    for relative in files:
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise InstallError(f"missing regular source file: {relative}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            source = ROOT / relative
            info = zipfile.ZipInfo(
                filename=f"{SKILL_NAME}/{relative}",
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes())

    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination .zip path; defaults to dist/workbuddy/<package>-<version>-workbuddy.zip.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        destination = build_package(args.output)
    except (InstallError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Built WorkBuddy skill package: {destination}")
    print(f"Root folder: {SKILL_NAME}/")
    print(f"Size: {destination.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
