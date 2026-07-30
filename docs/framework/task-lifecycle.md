# Task Lifecycle

This document defines the lifecycle contract for current tasks under
`projects/` and the separate read-only boundary around legacy tasks.

## Design Goals

- Keep task state human-readable in Markdown and recoverable without replaying
  chat history.
- Keep simple work lightweight and free of standalone specification files.
- Require explicit intent before executing task-defined commands.
- Keep framework state in V2 and task state in its owning `projects/<name>/`.
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

## Commands

```powershell
python -B capabilities/tools/workspace.py new my_task --complexity standard --dry-run
python -B capabilities/tools/workspace.py new my_task --complexity standard
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py resume my_task
python -B capabilities/tools/workspace.py doctor my_task
python -B capabilities/tools/workspace.py verify my_task
```

These commands operate only on lifecycle-managed directories under `projects/`.
The legacy external root remains `read_only` and is not a fallback target.
Scaffolding, `verify --run`, and `close` are writes or command execution and
therefore require explicit approval.

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

## Legacy Boundary

Do not change the legacy external task root to `read_write` for normal V2
operation. Historical inspection must use the centralized external-root
resolver, remain read-only, and never be mixed into current lifecycle commands.
