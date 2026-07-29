# Workspace Efficiency

## Stable Entry Point

`capabilities/tools/workspace.py` is the supported front door:

```powershell
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py check --full
python -B capabilities/tools/workspace.py update-status
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py resume my_task
python -B capabilities/tools/workspace.py doctor my_task
python -B capabilities/tools/workspace.py verify my_task
python -B capabilities/tools/workspace.py new my_task --dry-run
```

## Common Operating Principles

- `simple` work uses a short conversational plan and no standalone spec.
- `standard` work uses durable task state only when it adds operational value.
- `complex` work may use task-local plans and a coordination contract.
- Verification commands are previewed by default and are never assumed safe
  merely because they are recorded in a task.
- Generated output, logs, caches, and local credentials remain ignored.
- Framework rules and cross-task capabilities stay separate from task content.

## Path And Capability Boundaries

Path resolution is centralized in `workspace_paths.py`. New tools consume
configured names instead of hard-coding root directories. Tests use
`runtime/tmp/` and must not recursively discover the external source workspace.

Use `.agents/skills/` for intent-matched reusable Skills,
`capabilities/sops/` for directly followed procedures,
`capabilities/prompts/` for non-authoritative templates, and
`capabilities/tools/` for executable helpers.

## Maintenance

Quick checks run syntax checks, focused regressions, structure validation, Git
candidate auditing, and line-ending validation. Full checks additionally
summarize V2 Git candidates and verify `WORKSPACE_STATUS.md` without rewriting it.
Run `workspace.py update-status` explicitly when the generated inventory changes.

Compatibility report scripts remain callable, but new documentation and
automation should use `workspace.py`.
