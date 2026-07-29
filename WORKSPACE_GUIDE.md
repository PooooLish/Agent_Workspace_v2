# Workspace Guide

## Design

V2 is built beside the source workspace, not migrated in place. The source
workspace remains an external asset and is not a fallback write location.

```text
AGENT_WORKSPACE_V2/
|-- .workspace/          control configuration
|-- .agents/skills/      Codex skill discovery
|-- capabilities/        SOPs, prompts, and tools
|-- projects/            ignored local projects with independent ownership
|-- runtime/             local regenerable state
|-- storage/             durable artifacts and archives
|-- .local/              ignored environments and secrets
|-- docs/                maintained documentation
`-- .codex/              Codex adapter configuration
```

## Directory Contracts

`.workspace/` contains the path map, external-root access policy, and minimal
future extension points. It is not a framework competing with Codex.
The `policies/`, `profiles/`, `registry/`, and `schemas/` subdirectories are
reserved placeholders in phase one. Their README files do not activate a policy
engine, multi-agent role system, registry loader, or schema enforcement.
Only `AGENTS.md`, `.workspace/config.json`, and implemented tool checks currently
affect behavior.

`.agents/skills/` contains reusable Codex skills. Do not duplicate skill bodies
under `capabilities/`.

`capabilities/sops/` contains repeatable procedures. `capabilities/prompts/`
contains prompt templates without authority to weaken policy.
`capabilities/tools/` contains executable helpers and focused tests.

`runtime/` contains generated task state, run records, intermediate outputs,
logs, temporary data, and disposable sandboxes. Only its README contracts are
intended for Git.

`storage/artifacts/` is for reviewed local deliverables. `storage/archives/` is
for durable local historical or normative material, not caches. Only their
README contracts are intended for the workspace repository.

`.local/envs/` and `.local/secrets/` are ignored and outside the default Agent
read scope. Reproducible environment definitions should live in a future
tracked infrastructure area, not under `.local/`.

`projects/` is the local project area. The V2 workspace repository tracks only
`projects/README.md`; concrete project directories are ignored and excluded
from workspace-wide recursive scans. Drafts may remain local without Git.
Archived or abandoned projects move to
`storage/archives/projects/<project-name>/`. Concrete project contents remain
outside the workspace root repository at every lifecycle stage. Long-lived or
publishable projects may use independent Git repositories only after explicit
approval.

## Common Operating Principles

These principles are shared with the source workspace even though V2 uses a
different directory layout:

- Safety rules outrank tasks, Skills, prompts, profiles, and autonomous judgment.
- Nested rules may tighten but never weaken the root safety rules.
- Skills match reusable intent, SOPs define procedures, prompts provide
  non-authoritative templates, and task notes stay with their owning task.
- Simple changes use a short conversational plan, focused verification, one
  self-review, and no standalone spec, implementation plan, or repeated human
  review cycle.
- Standard work records durable state only when it improves recovery.
- Complex or multi-agent work may use task-local plans and coordination
  contracts.
- Verification evidence is required before completion claims.
- Publishing, archiving, deleting, executing task commands, and changing access
  policy are separate actions requiring explicit scope and approval.

## External Tasks

The authoritative configuration is `.workspace/config.json`:

```json
{
  "external_roots": {
    "tasks": {
      "path": "../agent_workspace/tasks",
      "access": "read_only",
      "env": "AGENT_TASKS_ROOT"
    }
  }
}
```

The file uses JSON so the standard-library resolver can parse it without an
additional dependency. The optional environment variable changes only the path.
Permission remains controlled by the configuration.

Tools must use `workspace_paths.resolve_external_root()`. Phase-one scanners may
check availability and read task metadata only when explicitly invoked; they
must not recursively scan the external root during normal workspace checks.

`new --dry-run` may preview a task target without changing access. Actual task
creation, command execution, and closeout remain disabled until the ownership
model, applicable root rules, source baseline, and rollback path are reviewed.

## Local Projects

Preview or create a minimal project scaffold:

```powershell
python -B capabilities/tools/workspace.py project new my-project --dry-run
python -B capabilities/tools/workspace.py project new my-project
```

The command creates project-local rules, goal documentation, source, tests,
scripts, documentation, outputs, temporary files, and log directories. It does
not initialize Git, install dependencies, or publish anything.

The workspace repository owns the project-area contract, not project contents.
When a project becomes durable or publishable, review its local files and then
explicitly initialize an independent repository from inside that project.
When a project is archived or abandoned, move it to
`storage/archives/projects/<project-name>/`; the archive remains local and
ignored by the workspace repository.

## Adapter Boundaries

`.codex/` holds project-scoped Codex adapter configuration and no credentials.
`.agents/skills/` remains the skill entry. V2 does not copy `.superpowers/`
execution state or create `.worktrees/`.

## Maintenance

```powershell
python -B capabilities/tools/test_v2_workspace.py
python -B capabilities/tools/test_workspace_tools.py
python -B capabilities/tools/check_workspace.py
python -B capabilities/tools/workspace.py check
```

Temporary test directories must be created under `runtime/tmp/`. Before treating
V2 as a replacement candidate, compare the source-protection baseline captured
before and after construction and investigate any difference without attempting
automatic repair.

## Document Roles

- `README.md`: user-facing introduction and quick start.
- `AGENTS.md`: mandatory top-level Agent and safety rules.
- `WORKSPACE_GUIDE.md`: architecture, maintenance, and extension rules.
- `WORKSPACE_STATUS.md`: generated inventory and current state only.
