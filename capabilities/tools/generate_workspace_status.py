#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from workspace_manifest import (
    CORE_MAINTENANCE_COMMANDS,
    PROJECT_COMMANDS,
    TASK_LIFECYCLE_COMMANDS,
    TOOL_DESCRIPTIONS,
)
from workspace_paths import (
    configured_path,
    load_workspace_config,
    resolve_external_root,
    workspace_root,
)


def markdown_items(root: Path, directory: Path) -> list[str]:
    return [
        f"- `{path.relative_to(root).as_posix()}`"
        for path in sorted(directory.glob("*.md"))
    ]


def skill_items(root: Path, directory: Path) -> list[str]:
    return [
        f"- `{path.parent.relative_to(root).as_posix()}`"
        for path in sorted(directory.glob("*/SKILL.md"))
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
    skills = configured_path(root, config, "skills")
    sops = configured_path(root, config, "sops")
    prompts = configured_path(root, config, "prompts")
    framework_docs = configured_path(root, config, "framework_docs")
    environment_docs = configured_path(root, config, "environment_docs")
    lines = [
        "# Workspace Status",
        "",
        "This generated file records the current V2 framework inventory. Permanent rules live in `AGENTS.md`.",
        "",
        "Regenerate it with:",
        "",
        "```powershell",
        "python -B capabilities/tools/workspace.py update-status",
        "```",
        "",
        "## Current Health",
        "",
        "- Layout: isolated V2 control plane and capability directories.",
        f"- External tasks access: `{tasks.access}`.",
        "- OS-level write isolation: not enforced by this configuration.",
        "",
        "## Reserved Control Plane",
        "",
        "- `.workspace/policies/`, `profiles/`, `registry/`, and `schemas/` are reserved extension points.",
        "- Their README files are documentation only; no policy engine, role system, registry loader, or schema enforcement is active.",
        "- `AGENTS.md` and implemented tool checks remain the enforceable workspace controls.",
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
        "## Local Project Policy",
        "",
        "- The workspace repository tracks only `projects/README.md` under `projects/`.",
        "- Concrete project directories are local and ignored by the workspace repository.",
        "- Archived or abandoned projects live under `storage/archives/projects/` and remain local.",
        "- Runtime state, artifact contents, and archive contents are not tracked by the workspace repository.",
        "- Long-lived or publishable projects should use independent Git repositories after explicit approval.",
        "- Project scaffolding does not initialize Git, install dependencies, or publish files.",
        "",
        "```powershell",
        *PROJECT_COMMANDS,
        "```",
        "",
        "## Review Proportionality",
        "",
        "- Simple work uses a short conversational plan, focused verification, one self-review, and a concise report.",
        "- Simple work does not require standalone specifications, implementation plans, or repeated human review gates.",
        "- Formal planning and review remain appropriate for high-risk, cross-module, long-running, destructive, or multi-agent work.",
        "",
        "## Current Tools",
        "",
        *tool_items(root),
        "",
        "## Current Skills",
        "",
        *skill_items(root, skills),
        "",
        "## Current SOPs",
        "",
        *markdown_items(root, sops),
        "",
        "## Current Prompts",
        "",
        *markdown_items(root, prompts),
        "",
        "## Current Framework Docs",
        "",
        *markdown_items(root, framework_docs),
        "",
        "## Environment Docs",
        "",
        *markdown_items(root, environment_docs),
        "",
        "## Runtime Policy",
        "",
        "- `runtime/` contains generated and locally disposable state; only directory README files are trackable.",
        "- `storage/` contains durable local data; only directory README contracts are trackable.",
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
