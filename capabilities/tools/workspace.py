#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

from generate_workspace_status import build_status
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
    require_writable_external_root,
    resolve_external_root,
    workspace_root,
)


FULL_CHECK_STEPS = QUICK_CHECK_STEPS + FULL_ONLY_STEPS
Runner = Callable[..., subprocess.CompletedProcess[str]]


def task_workspace_root(root: Path) -> Path:
    config = load_workspace_config(root)
    tasks = resolve_external_root(root, config, "tasks")
    return tasks.path


def require_task_write(root: Path, action: str) -> None:
    config = load_workspace_config(root)
    tasks = resolve_external_root(root, config, "tasks")
    require_writable_external_root(tasks, action)


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
    if not dry_run:
        require_task_write(root, "create task")
    config = load_workspace_config(root)
    command = [
        sys.executable,
        "-B",
        str(configured_path(root, config, "tools") / "make_task.py"),
        task_name,
    ]
    if dry_run:
        command.append("--dry-run")
    command.extend(("--complexity", complexity))
    return subprocess.run(command, cwd=root, check=False).returncode


def compact_field(value: str, width: int, *, fallback: str = "unknown") -> str:
    text = " ".join(value.split()) or fallback
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def run_status(root: Path) -> int:
    names = discover_task_names(root)
    if not names:
        print("No private task directories found.")
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
        print("No private task directories found.")
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

    new_parser = subparsers.add_parser("new", help="create a private task scaffold")
    new_parser.add_argument("task_name")
    new_parser.add_argument("--dry-run", action="store_true")
    new_parser.add_argument("--complexity", choices=COMPLEXITIES, default="standard")

    check_parser = subparsers.add_parser("check", help="run workspace checks")
    check_parser.add_argument("--full", action="store_true", help="run extended read-only verification")

    subparsers.add_parser("update-status", help="regenerate the tracked workspace status")

    subparsers.add_parser("status", help="list private task lifecycle state")

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
    task_root = task_workspace_root(root)
    if args.command == "new":
        try:
            return run_new(
                root,
                args.task_name,
                dry_run=args.dry_run,
                complexity=args.complexity,
            )
        except PermissionError as error:
            print(f"Error: {error}.")
            return 1
    if args.command == "check":
        return run_checks(root, full=args.full)
    if args.command == "update-status":
        return run_update_status(root)
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
            if args.run:
                require_task_write(root, "run task verification")
            return verify_task(load_task(task_root, args.task_name), run=args.run)
        except (PermissionError, ValueError) as error:
            print(f"Error: {error}.")
            return 1
    try:
        require_task_write(root, "close task")
        close_task(load_task(task_root, args.task_name))
    except (PermissionError, ValueError) as error:
        print(f"Error: {error}.")
        return 1
    print(f"Task closed: {args.task_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
