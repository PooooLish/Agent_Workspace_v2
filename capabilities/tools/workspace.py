#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

from generate_workspace_status import build_status
from make_project import scaffold_project, validate_project_target
from make_task import scaffold_task, validate_task_target
from task_lifecycle import (
    COMPLEXITIES,
    build_resume_packet,
    close_task,
    diagnose_task,
    discover_task_names,
    load_task,
    verify_task,
)
from workspace_manifest import FULL_ONLY_STEPS, QUICK_CHECK_STEPS, StepSpec
from workspace_paths import (
    configured_path,
    load_workspace_config,
    workspace_root,
)


FULL_CHECK_STEPS = QUICK_CHECK_STEPS + FULL_ONLY_STEPS
Runner = Callable[..., subprocess.CompletedProcess[str]]


def task_workspace_root(root: Path) -> Path:
    config = load_workspace_config(root)
    return configured_path(root, config, "projects")


def resolve_command(command: tuple[str, ...]) -> list[str]:
    resolved: list[str] = []
    for part in command:
        if part == "{python}":
            resolved.extend((sys.executable, "-B"))
        else:
            resolved.append(part)
    return resolved


def run_steps(
    root: Path,
    steps: Sequence[StepSpec],
    *,
    runner: Runner = subprocess.run,
) -> int:
    for step in steps:
        command = resolve_command(step.command)
        print(f"\n== {step.name} ==", flush=True)
        print(" ".join(command), flush=True)
        result = runner(
            command,
            cwd=root,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.STDOUT,
        )
        if result.returncode == 0:
            continue
        if step.allow_nonzero:
            print(f"Reminder step returned exit {result.returncode}; review output above.", flush=True)
            continue
        print(f"Step failed: {step.name} (exit {result.returncode})", flush=True)
        return result.returncode
    return 0


def run_checks(root: Path, *, full: bool) -> int:
    steps = FULL_CHECK_STEPS if full else QUICK_CHECK_STEPS
    code = run_steps(root, steps)
    if code == 0:
        mode = "Full" if full else "Quick"
        print(f"\n{mode} workspace checks completed.", flush=True)
    return code


def run_update_status(root: Path) -> int:
    output = root / "WORKSPACE_STATUS.md"
    output.write_text(build_status(root), encoding="utf-8", newline="\n")
    print(f"Wrote {output}")
    return 0


def run_new(root: Path, task_name: str, *, dry_run: bool, complexity: str) -> int:
    projects_root = task_workspace_root(root)
    task_root = validate_task_target(projects_root, task_name)
    if dry_run:
        print(f"Dry run: task directory would be created at {task_root}")
        print("Git initialization, dependency installation, and publishing are excluded.")
        return 0

    created, skipped = scaffold_task(
        projects_root,
        task_name,
        complexity=complexity,
    )
    print("Created items:")
    for item in created:
        print(f"  + {item}")
    print("Skipped existing items:")
    for item in skipped:
        print(f"  = {item}")
    print(f"Task directory ready: {task_root}")
    print("Git was not initialized.")
    return 0


def run_project_new(root: Path, project_name: str, *, dry_run: bool) -> int:
    config = load_workspace_config(root)
    projects_root = configured_path(root, config, "projects")
    project_root = projects_root / project_name
    if dry_run:
        project_root = validate_project_target(projects_root, project_name)
        print(f"Dry run: project directory would be created at {project_root}")
        print("Git initialization, dependency installation, and publishing are excluded.")
        return 0

    created, skipped = scaffold_project(projects_root, project_name)
    print("Created items:")
    for item in created:
        print(f"  + {item}")
    print("Skipped existing items:")
    for item in skipped:
        print(f"  = {item}")
    print(f"Project directory ready: {project_root}")
    print("Git was not initialized.")
    return 0


def compact_field(value: str, width: int, *, fallback: str = "unknown") -> str:
    text = " ".join(value.split()) or fallback
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def run_status(root: Path) -> int:
    names = discover_task_names(root)
    if not names:
        print("No lifecycle-managed task directories found under projects.")
        return 0
    print(f"{'Task':<28} {'Status':<12} {'Complexity':<12} {'Phase':<16} Next action")
    print("-" * 112)
    for name in names:
        try:
            task = load_task(root, name)
        except ValueError as error:
            error_text = compact_field(str(error), 40)
            print(f"{compact_field(name, 28):<28} invalid      -            -                {error_text}")
            continue
        known_statuses = ("planning", "active", "blocked", "completed", "abandoned")
        status = task.status if task.status in known_statuses else "legacy"
        complexity = task.complexity if task.complexity in COMPLEXITIES else "legacy"
        print(
            f"{compact_field(task.name, 28):<28} {status:<12} "
            f"{complexity:<12} {compact_field(task.phase, 16):<16} "
            f"{compact_field(task.next_action, 40, fallback='-')}"
        )
    return 0


def run_doctor(root: Path, task_name: str | None) -> int:
    names = [task_name] if task_name else discover_task_names(root)
    if not names:
        print("No lifecycle-managed task directories found under projects.")
        return 0
    finding_count = 0
    for name in names:
        try:
            task = load_task(root, name)
            findings = diagnose_task(task)
        except ValueError as error:
            findings = [str(error)]
        if not findings:
            print(f"[ok] {name}")
            continue
        print(f"[review] {name}")
        for finding in findings:
            print(f"  - {finding}")
        finding_count += len(findings)
    print(f"Doctor found {finding_count} item(s) requiring review.")
    return 2 if finding_count else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage tasks and check the agent workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="create a task scaffold under projects")
    new_parser.add_argument("task_name")
    new_parser.add_argument("--dry-run", action="store_true")
    new_parser.add_argument("--complexity", choices=COMPLEXITIES, default="standard")

    project_parser = subparsers.add_parser("project", help="manage local projects")
    project_subparsers = project_parser.add_subparsers(
        dest="project_command",
        required=True,
    )
    project_new_parser = project_subparsers.add_parser(
        "new",
        help="create a local project scaffold without initializing Git",
    )
    project_new_parser.add_argument("project_name")
    project_new_parser.add_argument("--dry-run", action="store_true")

    check_parser = subparsers.add_parser("check", help="run workspace checks")
    check_parser.add_argument("--full", action="store_true", help="run extended read-only verification")

    subparsers.add_parser("update-status", help="regenerate the tracked workspace status")

    subparsers.add_parser("status", help="list current task lifecycle state under projects")

    resume_parser = subparsers.add_parser("resume", help="print a compact task recovery packet")
    resume_parser.add_argument("task_name")

    doctor_parser = subparsers.add_parser("doctor", help="report incomplete task lifecycle state")
    doctor_parser.add_argument("task_name", nargs="?")

    verify_parser = subparsers.add_parser("verify", help="preview or run task verification commands")
    verify_parser.add_argument("task_name")
    verify_parser.add_argument("--run", action="store_true", help="execute commands inside the task directory")

    close_parser = subparsers.add_parser("close", help="validate summary and mark a task completed")
    close_parser.add_argument("task_name")
    return parser


def main() -> int:
    root = workspace_root()
    args = build_parser().parse_args()
    if args.command == "project":
        try:
            return run_project_new(
                root,
                args.project_name,
                dry_run=args.dry_run,
            )
        except ValueError as error:
            print(f"Error: {error}.")
            return 1
    if args.command == "new":
        try:
            return run_new(
                root,
                args.task_name,
                dry_run=args.dry_run,
                complexity=args.complexity,
            )
        except ValueError as error:
            print(f"Error: {error}.")
            return 1
    if args.command == "check":
        return run_checks(root, full=args.full)
    if args.command == "update-status":
        return run_update_status(root)
    task_root = task_workspace_root(root)
    if args.command == "status":
        return run_status(task_root)
    if args.command == "resume":
        try:
            print(build_resume_packet(load_task(task_root, args.task_name)))
            return 0
        except ValueError as error:
            print(f"Error: {error}.")
            return 1
    if args.command == "doctor":
        return run_doctor(task_root, args.task_name)
    if args.command == "verify":
        try:
            return verify_task(load_task(task_root, args.task_name), run=args.run)
        except ValueError as error:
            print(f"Error: {error}.")
            return 1
    try:
        close_task(load_task(task_root, args.task_name))
    except ValueError as error:
        print(f"Error: {error}.")
        return 1
    print(f"Task closed: {args.task_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
