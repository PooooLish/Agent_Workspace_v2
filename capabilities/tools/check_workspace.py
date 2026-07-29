#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Callable, Iterator

from workspace_manifest import TOOL_DESCRIPTIONS
from workspace_paths import (
    CONFIG_PATH,
    configured_path,
    load_workspace_config,
    resolve_external_root,
    workspace_root,
)


REQUIRED_ITEMS = (
    "AGENTS.md",
    "README.md",
    "WORKSPACE_GUIDE.md",
    "WORKSPACE_STATUS.md",
    ".gitignore",
    ".gitattributes",
    ".github/workflows/workspace-check.yml",
    ".workspace/config.json",
    ".workspace/policies/README.md",
    ".workspace/profiles/README.md",
    ".workspace/registry/README.md",
    ".workspace/schemas/README.md",
    ".agents/skills",
    ".codex/config.toml",
    "capabilities/sops",
    "capabilities/prompts",
    "capabilities/tools",
    "runtime/task-state/README.md",
    "runtime/runs/README.md",
    "runtime/outputs/README.md",
    "runtime/logs/README.md",
    "runtime/tmp/README.md",
    "runtime/sandboxes/README.md",
    "storage/artifacts/README.md",
    "storage/archives/README.md",
    ".local/README.md",
    "docs/framework",
    "docs/environments",
)

REQUIRED_IGNORE_PATTERNS = (
    ".local/envs/**",
    ".local/secrets/**",
    "runtime/task-state/**",
    "runtime/runs/**",
    "runtime/outputs/**",
    "runtime/logs/**",
    "runtime/tmp/**",
    "runtime/sandboxes/**",
    "**/__pycache__/",
    ".env",
    ".env.*",
)

LEGACY_ROOTS = ("tools", "prompts", "sops", "outputs", "logs", "tmp", "envs", "archives")
LINK_SCAN_ROOTS = (
    ".workspace",
    ".agents",
    ".codex",
    ".github",
    "capabilities",
    "docs",
    "storage",
)
WINDOWS_REPARSE_POINT = 0x400
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def skill_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    return {}


def skill_issues(skills_root: Path) -> list[str]:
    issues: list[str] = []
    names: dict[str, str] = {}
    for skill in sorted(skills_root.iterdir()) if skills_root.is_dir() else ():
        if not skill.is_dir():
            continue
        if not SKILL_NAME_RE.fullmatch(skill.name):
            issues.append(f"skill directory must use kebab-case: {skill.name}")
        skill_file = skill / "SKILL.md"
        if not skill_file.is_file():
            issues.append(f"skill is missing SKILL.md: {skill.name}")
            continue
        metadata = skill_frontmatter(skill_file)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name:
            issues.append(f"skill frontmatter is missing name: {skill.name}")
        elif name != skill.name:
            issues.append(
                f"skill frontmatter name does not match directory: {skill.name} != {name}"
            )
        if not description:
            issues.append(f"skill frontmatter is missing description: {skill.name}")
        if name:
            if name in names:
                issues.append(
                    f"duplicate skill name: {name} ({names[name]}, {skill.name})"
                )
            else:
                names[name] = skill.name
    return issues


def git_tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
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
        raise RuntimeError(f"git ls-files failed: {detail}")
    return [item for item in result.stdout.split("\0") if item]


def is_link_or_junction(
    path: Path,
    *,
    lstat: Callable[[Path], object] = os.lstat,
) -> bool:
    if path.is_symlink():
        return True
    attributes = getattr(lstat(path), "st_file_attributes", 0)
    return bool(attributes & WINDOWS_REPARSE_POINT)


def iter_link_candidates(root: Path) -> Iterator[Path]:
    for relative in LINK_SCAN_ROOTS:
        scan_root = root / relative
        if not os.path.lexists(scan_root):
            continue
        yield scan_root
        if is_link_or_junction(scan_root) or not scan_root.is_dir():
            continue
        pending = [scan_root]
        while pending:
            current = pending.pop()
            with os.scandir(current) as entries:
                for entry in sorted(entries, key=lambda item: item.name):
                    path = Path(entry.path)
                    yield path
                    if is_link_or_junction(path):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(path)


def check_workspace(root: Path) -> list[str]:
    issues: list[str] = []
    for relative in REQUIRED_ITEMS:
        if not (root / relative).exists():
            issues.append(f"missing required path: {relative}")

    for legacy in LEGACY_ROOTS:
        if (root / legacy).exists():
            issues.append(f"legacy root should not exist in V2: {legacy}/")

    config = load_workspace_config(root)
    paths = config.get("paths")
    if not isinstance(paths, dict):
        issues.append(f"invalid paths mapping: {CONFIG_PATH.as_posix()}")
    else:
        for name in paths:
            try:
                configured_path(root, config, name)
            except (KeyError, TypeError, ValueError) as error:
                issues.append(str(error))

    tasks = resolve_external_root(root, config, "tasks")
    if tasks.access != "read_only":
        issues.append("external tasks root must be read_only")
    if tasks.path.is_relative_to(root):
        issues.append("external tasks root unexpectedly resolves inside V2")
    gitignore_path = root / ".gitignore"
    if gitignore_path.is_file():
        lines = {
            line.strip()
            for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        for pattern in REQUIRED_IGNORE_PATTERNS:
            if pattern not in lines:
                issues.append(f"missing .gitignore pattern: {pattern}")

    for path in iter_link_candidates(root):
        if is_link_or_junction(path):
            issues.append(f"link or junction is not allowed in phase one: {path.relative_to(root)}")

    skills_root = configured_path(root, config, "skills")
    issues.extend(skill_issues(skills_root))

    tracked = set(git_tracked_files(root))
    for relative in tracked:
        normalized = relative.replace("\\", "/")
        if normalized.startswith((".local/envs/", ".local/secrets/", "runtime/")):
            if not normalized.endswith("/README.md"):
                issues.append(f"private/runtime file is tracked: {normalized}")

    tools_root = configured_path(root, config, "tools")
    actual_tools = {
        path.relative_to(root).as_posix()
        for path in tools_root.glob("*.py")
        if path.is_file()
    }
    for relative in TOOL_DESCRIPTIONS:
        if not (root / relative).is_file():
            issues.append(f"registered tool is missing: {relative}")
    for relative in actual_tools - set(TOOL_DESCRIPTIONS):
        issues.append(f"Python tool is not registered: {relative}")
    return sorted(set(issues))


def workspace_warnings(root: Path) -> list[str]:
    config = load_workspace_config(root)
    tasks = resolve_external_root(root, config, "tasks")
    warnings: list[str] = []
    if not tasks.path.is_dir():
        warnings.append(
            f"external tasks root is unavailable; task commands are disabled: {tasks.path}"
        )
    return warnings


def main() -> int:
    root = workspace_root()
    issues = check_workspace(root)
    for warning in workspace_warnings(root):
        print(f"Warning: {warning}")
    if issues:
        print("Workspace check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Workspace check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
