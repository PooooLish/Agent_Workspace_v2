#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


CONFIG_PATH = Path(".workspace/config.yaml")


@dataclass(frozen=True)
class ExternalRoot:
    path: Path
    access: str
    source: str


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


def resolve_external_root(
    root: Path,
    config: Mapping[str, object],
    name: str,
) -> ExternalRoot:
    external_roots = config.get("external_roots")
    if not isinstance(external_roots, dict) or name not in external_roots:
        raise KeyError(f"external root is not configured: {name}")
    item = external_roots[name]
    if not isinstance(item, dict):
        raise TypeError(f"external root must be an object: {name}")

    configured = item.get("path")
    access = item.get("access")
    environment_name = item.get("env")
    if not isinstance(configured, str) or not isinstance(access, str):
        raise TypeError(f"external root path and access must be strings: {name}")

    override = (
        os.environ.get(environment_name)
        if isinstance(environment_name, str)
        else None
    )
    raw_path = override or configured
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    return ExternalRoot(
        path=path.resolve(),
        access=access,
        source=environment_name if override else CONFIG_PATH.as_posix(),
    )


def require_writable_external_root(external: ExternalRoot, action: str) -> None:
    if external.access != "read_write":
        raise PermissionError(
            f"cannot {action}: external root is read-only ({external.path})"
        )
