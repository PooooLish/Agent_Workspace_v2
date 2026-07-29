#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from workspace_paths import (
    load_workspace_config,
    require_writable_external_root,
    resolve_external_root,
    workspace_root as resolve_workspace_root,
)

from task_names import TASK_NAME_RE, validate_task_name

TASK_DIRS = [
    ".agents/skills",
    "src",
    "scripts",
    "data",
    "outputs",
    "deliverables",
    "tests",
    "tmp",
    "logs",
    "docs",
    "docs/skills",
]

COMPLEXITIES = ("simple", "standard", "complex")


def write_if_missing(path: Path, content: str, created: list[str], skipped: list[str]) -> None:
    if path.exists():
        skipped.append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(str(path))


def build_task_agents(task_name: str) -> str:
    return f"""# AGENTS.md

## Task role

- Work only inside this task folder unless explicitly asked otherwise.
- Keep changes small, reviewable, and easy to verify.

## Rule relationship

- Follow the workspace root `../../AGENTS.md` first.
- This task-level `AGENTS.md` adds task-specific rules for `{task_name}`.
- The task rules may supplement or tighten the root rules.
- The task rules must not weaken the root safety rules.
- If two rules seem to conflict, follow the stricter rule.

## Safety rules

- Do not delete files without approval.
- Do not store or print real secrets.
- Keep outputs in `outputs/`, scratch files in `tmp/`, and logs in `logs/`.
- Keep executable task-specific skills under `.agents/skills/`.
- Keep task-specific notes, lessons, and checklists under `docs/skills/`.

## Workflow

1. Read the workspace root `../../AGENTS.md`.
2. Read this file, `task.md`, and `README.md`.
3. Inspect existing files.
4. Propose a short plan.
5. Make the minimum useful change.
6. Run the minimum verification command.
7. Report changed files, commands run, and verification result.

## Task name

- `{task_name}`
"""


def build_task_md(task_name: str, complexity: str = "standard") -> str:
    return f"""# Task: {task_name}

## Status

planning

## Complexity

{complexity}

## Phase

planning

## Goal

Describe the task objective here.

## Non-goals

List work that is intentionally outside this task.

## Constraints

- Keep work inside this task directory.
- Do not store real secrets.

## Inputs

List the files, data, or references needed for this task.

## Acceptance criteria

List the observable conditions that must be true for this task to be complete.

## Verification commands

List one command per line that proves the acceptance criteria.

## Decisions

Record durable implementation decisions and their reasons.

## Progress

Record completed milestones that matter for handoff.

## Next action

Describe the single next useful action.

## Blockers

Record blockers, or write `None`.
"""


def build_summary_md(task_name: str) -> str:
    return f"""# Summary: {task_name}

## Goal

## Outcome

## Changes

## Verification

## Open issues
"""


def build_readme(task_name: str) -> str:
    return f"""# {task_name}

This task folder was created by `capabilities/tools/make_task.py`.

## Suggested workflow

1. Fill in `task.md`.
2. Read the workspace root `../../AGENTS.md`.
3. Read local `AGENTS.md` and `README.md`.
4. Put source code in `src/`.
5. Put helper scripts in `scripts/`.
6. Put tests in `tests/`.
7. Put generated or reproducible results in `outputs/`.
8. Put reviewed, publishable final artifacts in `deliverables/`.
9. Put executable task-specific skills in `.agents/skills/`.
10. Put task-specific notes, lessons, and checklists in `docs/skills/`.
"""


TASK_GITIGNORE = """outputs/
tmp/
logs/
__pycache__/
.pytest_cache/
.venv/
node_modules/
dist/
build/
coverage/
.env
.env.*
!.env.example
"""

COMPLEX_PLANNING_README = """# Task Planning

Keep task-specific specifications and implementation plans in this directory.
Do not copy completed plans into the workspace root.
"""

COORDINATION_CONTRACT = """# Multi-Agent Coordination Contract

Use one row per independently reviewable work item.
Use relative paths inside the task directory. Dependent rows may reuse paths;
independent rows must not overlap. For single-agent complex work, add one row
whose values are `N/A` and whose status is `not-applicable`.
Escape a literal pipe inside a table cell as `\\|`.

| ID | Dependencies | Owner | Worktree | Allowed paths | Verification | Status |
| --- | --- | --- | --- | --- | --- | --- |
"""


def scaffold_task(
    tasks_root: Path,
    task_name: str,
    *,
    complexity: str = "standard",
) -> tuple[list[str], list[str]]:
    validate_task_name(task_name)
    if complexity not in COMPLEXITIES:
        raise ValueError(f"complexity must be one of: {', '.join(COMPLEXITIES)}")

    if tasks_root.exists():
        collisions = [
            path.name
            for path in tasks_root.iterdir()
            if path.is_dir()
            and path.name.casefold() == task_name.casefold()
            and path.name != task_name
        ]
        if collisions:
            raise ValueError(
                f"task_name conflicts case-insensitively with existing task: {collisions[0]}"
            )
    task_root = tasks_root / task_name
    resolved_task_root = task_root.resolve()
    resolved_tasks_root = tasks_root.resolve()
    if resolved_tasks_root not in resolved_task_root.parents:
        raise ValueError("resolved task path must stay inside the tasks directory")

    created: list[str] = []
    skipped: list[str] = []
    task_root.mkdir(parents=True, exist_ok=True)
    for dirname in TASK_DIRS:
        dir_path = task_root / dirname
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path))

    write_if_missing(task_root / "AGENTS.md", build_task_agents(task_name), created, skipped)
    write_if_missing(task_root / "task.md", build_task_md(task_name, complexity), created, skipped)
    write_if_missing(task_root / "README.md", build_readme(task_name), created, skipped)
    write_if_missing(task_root / "summary.md", build_summary_md(task_name), created, skipped)
    write_if_missing(task_root / ".gitignore", TASK_GITIGNORE, created, skipped)
    if complexity == "complex":
        write_if_missing(
            task_root / "docs" / "superpowers" / "README.md",
            COMPLEX_PLANNING_README,
            created,
            skipped,
        )
        write_if_missing(
            task_root / "coordination" / "contract.md",
            COORDINATION_CONTRACT,
            created,
            skipped,
        )
    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a private task scaffold.")
    parser.add_argument("task_name")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--complexity", choices=COMPLEXITIES, default="standard")
    args = parser.parse_args()
    task_name = args.task_name.strip()
    dry_run = args.dry_run

    if not task_name:
        print("Error: task_name cannot be empty.")
        return 1
    try:
        validate_task_name(task_name)
    except ValueError as error:
        print(f"Error: {error}.")
        return 1

    workspace_root = resolve_workspace_root()
    config = load_workspace_config(workspace_root)
    tasks = resolve_external_root(workspace_root, config, "tasks")
    tasks_root = tasks.path
    task_root = tasks_root / task_name
    try:
        require_writable_external_root(tasks, "create task")
    except PermissionError as error:
        print(f"Error: {error}.")
        return 1
    if dry_run:
        print(f"Dry run: task directory would be created at {task_root}")
        print("Planned directories:")
        for dirname in TASK_DIRS:
            print(f"  + {task_root / dirname}")
        print("Planned files:")
        for filename in ("AGENTS.md", "task.md", "README.md", "summary.md", ".gitignore"):
            print(f"  + {task_root / filename}")
        if args.complexity == "complex":
            print(f"  + {task_root / 'docs' / 'superpowers' / 'README.md'}")
            print(f"  + {task_root / 'coordination' / 'contract.md'}")
        return 0

    try:
        created, skipped = scaffold_task(
            tasks_root,
            task_name,
            complexity=args.complexity,
        )
    except ValueError as error:
        print(f"Error: {error}.")
        return 1

    print("Created items:")
    for item in created:
        print(f"  + {item}")

    print("Skipped existing items:")
    for item in skipped:
        print(f"  = {item}")

    print(f"Task directory ready: {task_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
