#!/usr/bin/env python3
"""Quick import smoke test: does every integration module still load?

This is not a substitute for the test suite - it only catches the class of
breakage that makes Home Assistant refuse to load the integration at all
(syntax errors, renamed constants, imports of modules that moved to the
external ``violet-poolController-api`` package).

Usage:
    python scripts/quick-import-test.py

Requires the development environment (``pip install -r requirements-dev.txt``),
because the integration imports Home Assistant.
"""
# ruff: noqa: T201

from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "custom_components.violet_pool_controller"
PACKAGE_DIR = PROJECT_ROOT / "custom_components" / "violet_pool_controller"

sys.path.insert(0, str(PROJECT_ROOT))


def module_names() -> list[str]:
    """Every importable module inside the integration, in a stable order."""
    names: list[str] = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(PACKAGE_DIR).with_suffix("")
        parts = [part for part in relative.parts if part != "__init__"]
        names.append(".".join([PACKAGE, *parts]) if parts else PACKAGE)
    return names


def main() -> int:
    print("=" * 60)
    print("Violet Pool Controller - quick import test")
    print("=" * 60)

    try:
        const = importlib.import_module(f"{PACKAGE}.const")
    except Exception:
        print("\nFAIL: const.py does not import\n")
        traceback.print_exc()
        return 1

    print(f"\nDomain:  {const.DOMAIN}")
    print(f"Version: {const.INTEGRATION_VERSION}\n")

    failures: list[tuple[str, BaseException]] = []
    names = module_names()
    for name in names:
        try:
            importlib.import_module(name)
        except Exception as err:  # noqa: BLE001 - report, do not abort
            failures.append((name, err))
            print(f"  FAIL {name}: {err.__class__.__name__}: {err}")
        else:
            print(f"  ok   {name}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} of {len(names)} modules failed to import.")
        return 1
    print(f"All {len(names)} modules imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
