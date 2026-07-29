# Workspace Guide

## Design

V2 is built beside the source workspace, not migrated in place. The source
workspace remains an external asset and is not a fallback write location.

```text
AGENT_WORKSPACE_V2/
|-- .workspace/          control configuration
|-- .agents/skills/      Codex skill discovery
|-- capabilities/        SOPs, prompts, and tools
|-- runtime/             local regenerable state
|-- storage/             durable artifacts and archives
|-- .local/              ignored environments and secrets
|-- docs/                maintained documentation
`-- .codex/              Codex adapter configuration
```

## Directory Contracts

`.workspace/` contains the path map, external-root access policy, and minimal
future extension points. It is not a framework competing with Codex.

`.agents/skills/` contains reusable Codex skills. Do not duplicate skill bodies
under `capabilities/`.

`capabilities/sops/` contains repeatable procedures. `capabilities/prompts/`
contains prompt templates without authority to weaken policy.
`capabilities/tools/` contains executable helpers and focused tests.

`runtime/` contains generated task state, run records, intermediate outputs,
logs, temporary data, and disposable sandboxes. Only its README contracts are
intended for Git.

`storage/artifacts/` is for reviewed deliverables. `storage/archives/` is for
durable historical or normative material, not caches.

`.local/envs/` and `.local/secrets/` are ignored and outside the default Agent
read scope. Reproducible environment definitions should live in a future
tracked infrastructure area, not under `.local/`.

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
