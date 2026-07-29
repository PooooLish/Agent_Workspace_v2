#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from workspace_manifest import CORE_MAINTENANCE_COMMANDS, TASK_LIFECYCLE_COMMANDS, TOOL_DESCRIPTIONS
from workspace_paths import load_workspace_config, resolve_external_root, workspace_root


def markdown_items(root: Path, directory: str) -> list[str]:
    return [
        f"- `{path.relative_to(root).as_posix()}`"
        for path in sorted((root / directory).glob("*.md"))
    ]


def skill_items(root: Path) -> list[str]:
    return [
        f"- `{path.parent.relative_to(root).as_posix()}`"
        for path in sorted((root / ".agents" / "skills").glob("*/SKILL.md"))
    ]


def tool_items(root: Path) -> list[str]:
    return [
        f"- `{relative}`: {description}"
        for relative, description in sorted(TOOL_DESCRIPTIONS.items())
        if (root / relative).is_file()
    ]


def build_status(root: Path) -> str:
    config = load_workspace_config(root)
    tasks = resolve_external_root(root, config, "tasks")
    lines = [
        "# Workspace Status",
        "",
        "This generated file records the current V2 framework inventory. Permanent rules live in `AGENTS.md`.",
        "",
        "Regenerate it with:",
        "",
        "```powershell",
        "python capabilities/tools/generate_workspace_status.py",
        "```",
        "",
        "## Current Health",
        "",
        "- Layout: isolated V2 control plane and capability directories.",
        f"- External tasks access: `{tasks.access}`.",
        f"- External tasks source: `{tasks.source}`.",
        f"- External tasks available: `{'yes' if tasks.path.is_dir() else 'no'}`.",
        "- OS-level write isolation: not enforced by this configuration.",
        "",
        "## Core Commands",
        "",
        "```powershell",
        *TASK_LIFECYCLE_COMMANDS,
        *CORE_MAINTENANCE_COMMANDS,
        "```",
        "",
        "Task creation, verification execution, and closeout are disabled while the external task root is read-only.",
        "",
        "## Current Tools",
        "",
        *tool_items(root),
        "",
        "## Current Skills",
        "",
        *skill_items(root),
        "",
        "## Current SOPs",
        "",
        *markdown_items(root, "capabilities/sops"),
        "",
        "## Current Prompts",
        "",
        *markdown_items(root, "capabilities/prompts"),
        "",
        "## Environment Docs",
        "",
        *markdown_items(root, "docs/environments"),
        "",
        "## Runtime Policy",
        "",
        "- `runtime/` contains generated and locally disposable state; only directory README files are trackable.",
        "- `.local/envs/` and `.local/secrets/` are local-only and ignored.",
        "- No task, Superpowers snapshot, worktree, secret, output, log, or cache was copied from the source workspace.",
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
