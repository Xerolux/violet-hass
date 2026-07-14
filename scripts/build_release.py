#!/usr/bin/env python3
"""Build a deterministic ZIP release for the Home Assistant integration."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

DEFAULT_SOURCE = Path("custom_components/violet_pool_controller")
DEFAULT_OUTPUT = Path("violet_pool_controller.zip")


def _include(path: Path, source: Path) -> bool:
    relative = path.relative_to(source)
    if any(part == "__pycache__" or part.startswith(".git") for part in relative.parts):
        return False
    if path.name == ".DS_Store" or path.suffix == ".pyc":
        return False
    return not (path.name.startswith("test_") and path.suffix == ".py")


def build_release(source: Path, output: Path) -> str:
    """Write the release archive and return its SHA-256 digest."""
    if not source.is_dir():
        raise FileNotFoundError(f"Integration directory not found: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or not _include(path, source):
                continue
            info = ZipInfo(path.relative_to(source).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(f"{output.suffix}.sha256").write_text(f"{digest}  {output.name}\n")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    digest = build_release(args.source, args.output)
    sys.stdout.write(f"Built {args.output} (sha256: {digest})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
