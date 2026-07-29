#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from workspace_paths import configured_path, load_workspace_config, workspace_root


def default_targets(root: Path, config: Mapping[str, object]) -> list[Path]:
    return [configured_path(root, config, "tools")]


def python_files(targets: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for target in targets:
        if target.is_file() and target.suffix == ".py":
            files.add(target)
        elif target.is_dir():
            files.update(path for path in target.rglob("*.py") if path.is_file())
    return sorted(files)


def check_syntax(targets: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in python_files(targets):
        try:
            compile(path.read_bytes(), str(path), "exec")
        except SyntaxError as error:
            errors.append(f"{path}:{error.lineno}: {error.msg}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Python syntax without writing bytecode.")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    root = workspace_root()
    targets = args.paths or default_targets(root, load_workspace_config(root))
    errors = check_syntax([path.resolve() for path in targets])
    if errors:
        print("Python syntax check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Python syntax check passed ({len(python_files(targets))} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
