#!/usr/bin/env python3
from __future__ import annotations

from generate_workspace_status import build_status
from workspace_paths import workspace_root


def main() -> int:
    root = workspace_root()
    path = root / "WORKSPACE_STATUS.md"
    if not path.is_file():
        print("WORKSPACE_STATUS.md is missing.")
        return 1
    if path.read_text(encoding="utf-8") != build_status(root):
        print("WORKSPACE_STATUS.md is stale. Run:")
        print("  python capabilities/tools/generate_workspace_status.py")
        return 1
    print("WORKSPACE_STATUS.md is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
