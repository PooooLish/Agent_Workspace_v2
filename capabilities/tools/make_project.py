#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from task_names import validate_task_name
from workspace_paths import configured_path, load_workspace_config, workspace_root


PROJECT_DIRS = (
    "src",
    "tests",
    "docs",
    "scripts",
    "outputs",
    "tmp",
    "logs",
)

PROJECT_GITIGNORE = """outputs/
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


def write_if_missing(
    path: Path,
    content: str,
    created: list[str],
    skipped: list[str],
) -> None:
    if path.exists():
        skipped.append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    created.append(str(path))


def build_agents(project_name: str) -> str:
    return f"""# AGENTS.md

## Scope

- Work only inside this project unless the user explicitly expands the scope.
- Follow the workspace root `../../AGENTS.md`; this file may only tighten it.
- Keep project code, tests, documentation, and generated state inside this
  project.

## Safety

- Do not store or print real secrets.
- Do not delete files, install dependencies, or perform Git publishing actions
  without explicit approval.
- Keep generated outputs in `outputs/`, temporary files in `tmp/`, and logs in
  `logs/`.

## Workflow

1. Read `project.md`, `README.md`, and the relevant source files.
2. State a short plan appropriate to the change.
3. Make small, reviewable edits.
4. Run focused verification.
5. Review the diff and report remaining risks.

## Project

- `{project_name}`
"""


def build_project_md(project_name: str) -> str:
    return f"""# Project: {project_name}

## Goal

Describe the product or outcome.

## Scope

Describe what belongs in this project.

## Non-goals

List intentionally excluded work.

## Constraints

- Keep work inside this project directory.
- Do not store real secrets.

## Acceptance Criteria

List observable conditions for a usable first version.

## Verification

List commands that verify the project.
"""


def build_readme(project_name: str) -> str:
    return f"""# {project_name}

This project was scaffolded by Agent Workspace V2.

## Start

1. Define the goal and acceptance criteria in `project.md`.
2. Put implementation code in `src/`.
3. Put focused tests in `tests/`.
4. Record durable design and usage notes in `docs/`.

Git is intentionally not initialized by the scaffold command.
"""


def validate_project_target(projects_root: Path, project_name: str) -> Path:
    validate_task_name(project_name)
    resolved_projects_root = projects_root.resolve()
    project_root = projects_root / project_name
    resolved_project_root = project_root.resolve()
    if resolved_projects_root not in resolved_project_root.parents:
        raise ValueError("resolved project path must stay inside the projects directory")

    if projects_root.is_dir():
        for path in projects_root.iterdir():
            if path.name.casefold() == project_name.casefold():
                raise ValueError(f"project target already exists: {path.name}")
    elif projects_root.exists():
        raise ValueError(f"projects path is not a directory: {projects_root}")
    return project_root


def scaffold_project(
    projects_root: Path,
    project_name: str,
) -> tuple[list[str], list[str]]:
    project_root = validate_project_target(projects_root, project_name)
    projects_root.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []
    project_root.mkdir(parents=True, exist_ok=True)
    for dirname in PROJECT_DIRS:
        path = project_root / dirname
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))

    write_if_missing(
        project_root / "AGENTS.md",
        build_agents(project_name),
        created,
        skipped,
    )
    write_if_missing(
        project_root / "project.md",
        build_project_md(project_name),
        created,
        skipped,
    )
    write_if_missing(
        project_root / "README.md",
        build_readme(project_name),
        created,
        skipped,
    )
    write_if_missing(
        project_root / ".gitignore",
        PROJECT_GITIGNORE,
        created,
        skipped,
    )
    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local project scaffold.")
    parser.add_argument("project_name")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = workspace_root()
    config = load_workspace_config(root)
    projects_root = configured_path(root, config, "projects")
    project_root = projects_root / args.project_name

    if args.dry_run:
        try:
            project_root = validate_project_target(projects_root, args.project_name)
        except ValueError as error:
            print(f"Error: {error}.")
            return 1
        print(f"Dry run: project directory would be created at {project_root}")
        print("Git initialization, dependency installation, and publishing are excluded.")
        return 0

    try:
        created, skipped = scaffold_project(projects_root, args.project_name)
    except ValueError as error:
        print(f"Error: {error}.")
        return 1

    print("Created items:")
    for item in created:
        print(f"  + {item}")
    print("Skipped existing items:")
    for item in skipped:
        print(f"  = {item}")
    print(f"Project directory ready: {project_root}")
    print("Git was not initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
