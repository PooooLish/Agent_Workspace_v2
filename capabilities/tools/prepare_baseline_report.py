#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
from workspace_paths import configured_path, load_workspace_config, workspace_root


def load_legacy_report_tool(root: Path):
    config = load_workspace_config(root)
    path = configured_path(root, config, "tools") / "prepare_first_commit_report.py"
    spec = importlib.util.spec_from_file_location("prepare_first_commit_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load capabilities/tools/prepare_first_commit_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = workspace_root()
    return load_legacy_report_tool(root).main()


if __name__ == "__main__":
    raise SystemExit(main())
