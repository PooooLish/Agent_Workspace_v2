#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


CONFIG_PATH = Path(".workspace/config.json")


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_workspace_config(root: Path | None = None) -> dict[str, object]:
    resolved_root = (root or workspace_root()).resolve()
    path = resolved_root / CONFIG_PATH
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if config.get("version") != 1:
        raise ValueError(f"unsupported workspace config version in {path}")
    return config


def configured_path(
    root: Path,
    config: Mapping[str, object],
    name: str,
) -> Path:
    paths = config.get("paths")
    if not isinstance(paths, dict) or name not in paths:
        raise KeyError(f"workspace path is not configured: {name}")
    value = paths[name]
    if not isinstance(value, str):
        raise TypeError(f"workspace path must be a string: {name}")
    resolved = (root / value).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"workspace path escapes V2 root: {name}")
    return resolved
