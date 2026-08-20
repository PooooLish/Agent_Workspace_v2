#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from workspace_manifest import TOOL_DESCRIPTIONS
from workspace_paths import (
    configured_path,
    load_workspace_config,
    workspace_root,
)


def git_tracked_files(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode != 0:
        detail = result.stderr.strip() if result.stderr else "unknown Git error"
        raise RuntimeError(f"git tracked inventory failed: {detail}")
    return {item.replace("\\", "/") for item in result.stdout.split("\0") if item}


def markdown_items(
    root: Path,
    directory: Path,
    *,
    tracked_files: set[str] | None = None,
) -> list[str]:
    return [
        f"- `{path.relative_to(root).as_posix()}`"
        for path in sorted(
            directory.glob("*.md"),
            key=lambda item: item.relative_to(root).as_posix().casefold(),
        )
        if tracked_files is None
        or path.relative_to(root).as_posix() in tracked_files
    ]


def build_local_skill_catalog(
    root: Path,
    directory: Path,
    remote_catalog: dict[str, object],
) -> dict[str, object]:
    remote_paths = {
        entry["path"]
        for entry in remote_catalog.get("skills", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    skills = [
        {
            "name": path.parent.name,
            "path": path.parent.relative_to(root).as_posix(),
        }
        for path in sorted(
            directory.glob("*/SKILL.md"),
            key=lambda item: item.relative_to(root).as_posix().casefold(),
        )
        if path.parent.relative_to(root).as_posix() not in remote_paths
    ]
    return {
        "version": 1,
        "scope": "workspace-local",
        "skills": skills,
    }


def validate_remote_skill_catalog(
    root: Path,
    directory: Path,
    catalog: dict[str, object],
    tracked_files: set[str],
) -> None:
    if catalog.get("version") != 1:
        raise ValueError("remote skill catalog must use version 1")
    if catalog.get("scope") != "workspace-remote":
        raise ValueError("remote skill catalog scope must be workspace-remote")
    entries = catalog.get("skills")
    if not isinstance(entries, list):
        raise ValueError("remote skill catalog skills must be a list")

    directory_relative = directory.relative_to(root).as_posix()
    declared_files: set[str] = set()
    names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("remote skill catalog entries must be objects")
        name = entry.get("name")
        path = entry.get("path")
        if not isinstance(name, str) or not name:
            raise ValueError("remote skill catalog entry name must be non-empty")
        if not isinstance(path, str) or not path:
            raise ValueError(f"remote skill catalog path is invalid: {name}")
        expected_path = f"{directory_relative}/{name}"
        if path != expected_path:
            raise ValueError(
                f"remote skill catalog path must match its name: {name}"
            )
        if name in names:
            raise ValueError(f"duplicate remote skill catalog name: {name}")
        names.add(name)
        declared_files.add(f"{path}/SKILL.md")

    tracked_skill_files = {
        relative
        for relative in tracked_files
        if relative.startswith(f"{directory_relative}/")
        and relative.endswith("/SKILL.md")
        and relative.count("/") == directory_relative.count("/") + 2
    }
    missing = sorted(tracked_skill_files - declared_files, key=str.casefold)
    if missing:
        raise ValueError(
            "tracked skill body is missing from remote catalog: " + ", ".join(missing)
        )
    untracked = sorted(declared_files - tracked_skill_files, key=str.casefold)
    if untracked:
        raise ValueError(
            "remote catalog declares an untracked skill body: " + ", ".join(untracked)
        )


def load_remote_skill_catalog(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    if not isinstance(catalog, dict):
        raise ValueError(f"remote skill catalog must be an object: {path}")
    return catalog


def write_local_skill_catalog(
    path: Path,
    catalog: dict[str, object],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def tracked_tool_items(root: Path, tracked_files: set[str]) -> list[str]:
    return [
        f"- `{relative}`: {description}"
        for relative, description in sorted(TOOL_DESCRIPTIONS.items())
        if relative in tracked_files and (root / relative).is_file()
    ]


def remote_skill_items(catalog: dict[str, object]) -> list[str]:
    entries = catalog["skills"]
    assert isinstance(entries, list)
    return [
        f"- `{entry['path']}`"
        for entry in entries
        if isinstance(entry, dict)
    ]


def build_status(root: Path) -> str:
    config = load_workspace_config(root)
    tracked_files = git_tracked_files(root)
    skills = configured_path(root, config, "skills")
    sops = configured_path(root, config, "sops")
    prompts = configured_path(root, config, "prompts")
    framework_docs = configured_path(root, config, "framework_docs")
    environment_docs = configured_path(root, config, "environment_docs")
    remote_manifest = configured_path(root, config, "remote_skills_manifest")
    remote_catalog = load_remote_skill_catalog(remote_manifest)
    validate_remote_skill_catalog(root, skills, remote_catalog, tracked_files)
    lines = [
        "# Workspace Status",
        "",
        "This generated file records the version-controlled V2 remote architecture.",
        "Permanent policy lives only in `AGENTS.md`.",
        "",
        "Regenerate it with:",
        "",
        "```powershell",
        "python -B capabilities/tools/workspace.py update-status",
        "```",
        "",
        "## Remote Tools",
        "",
        *tracked_tool_items(root, tracked_files),
        "",
        "## Remote Skills",
        "",
        *remote_skill_items(remote_catalog),
        "",
        "## Remote SOPs",
        "",
        *markdown_items(root, sops, tracked_files=tracked_files),
        "",
        "## Remote Prompts",
        "",
        *markdown_items(root, prompts, tracked_files=tracked_files),
        "",
        "## Remote Framework Docs",
        "",
        *markdown_items(root, framework_docs, tracked_files=tracked_files),
        "",
        "## Remote Environment Docs",
        "",
        *markdown_items(root, environment_docs, tracked_files=tracked_files),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    root = workspace_root()
    output = root / "WORKSPACE_STATUS.md"
    output.write_text(build_status(root), encoding="utf-8", newline="\n")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
