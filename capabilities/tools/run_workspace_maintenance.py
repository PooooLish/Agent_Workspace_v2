#!/usr/bin/env python3
from __future__ import annotations

from workspace import run_checks
from workspace_paths import workspace_root


def main() -> int:
    root = workspace_root()
    code = run_checks(root, full=True)
    if code == 0:
        print("\nMaintenance checks completed.", flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
