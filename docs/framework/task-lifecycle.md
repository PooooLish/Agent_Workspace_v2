# Task Lifecycle

This document defines the task lifecycle contract shared with the source
workspace and the V2-specific external-root boundary.

## Design Goals

- Keep task state human-readable in Markdown and recoverable without replaying
  chat history.
- Keep simple work lightweight and free of standalone specification files.
- Require explicit intent before executing task-defined commands.
- Keep framework state in V2 and project state in the owning external task.
- Never infer write permission from tool availability.

## Complexity Levels

### Simple

Use for localized, low-risk work. Record the goal, acceptance criteria, next
action, and verification commands in `task.md`. Do not create standalone specs
or plans.

### Standard

Use for multi-file work that benefits from durable state. Keep decisions,
phase, progress, blockers, and verification commands in `task.md`.

### Complex

Use for ambiguous, high-risk, cross-module, long-running, or multi-agent work.
Task-local specifications may live under `docs/superpowers/`. Multi-agent work
uses `coordination/contract.md` for dependencies, owners, worktrees, allowed
paths, verification, and status.

## Phase-One Commands

```powershell
python -B capabilities/tools/workspace.py new my_task --complexity standard --dry-run
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py resume my_task
python -B capabilities/tools/workspace.py doctor my_task
python -B capabilities/tools/workspace.py verify my_task
```

The external root is `read_only`. Dry-run and read-only views are available;
actual `new`, `verify --run`, and `close` operations are blocked.

## State Ownership

`task.md` owns current execution state. `summary.md` owns the final outcome.
Task-local outputs, logs, and temporary files stay inside the task repository.
V2 framework runs and generated state stay under `runtime/`. V2 does not keep a
second registry containing private task details.

## Recovery

`resume` reports status, complexity, phase, goal, constraints, decisions,
progress, verification information, next action, blockers, and Git context when
available. Long logs are not loaded unless the task requires them.

## Verification Safety

`verify` previews one command per line. `verify --run` executes trusted shell
commands with the task directory as the working directory, but it is not a
sandbox. Commands may still access parent paths, absolute paths, the network,
and inherited environment variables. Actual isolation requires the Codex
sandbox, a container, or another restricted executor.

## Closeout Boundary

`close` validates lifecycle fields and completed summary sections, then updates
status fields. It does not execute verification, archive, publish, delete, or
commit a task. Those remain separate, explicitly approved actions.

## Future Write Gate

Before changing the external root to `read_write`, review the source-protection
baseline, task ownership model, applicable root rules, and rollback path.
Mutating commands must continue to use the centralized permission guard.
