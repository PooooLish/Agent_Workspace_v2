# Workspace Guide

## Design

V2 is a self-contained workspace architecture. It does not depend on or resolve
paths into a separate historical workspace.

```text
AGENT_WORKSPACE_V2/
|-- .workspace/          control configuration
|-- .agents/skills/      Codex skill discovery
|-- capabilities/        SOPs, prompts, and tools
|-- projects/            ignored current tasks and projects
|-- runtime/             local regenerable state
|-- storage/             durable artifacts and archives
|-- .local/              ignored environments and secrets
|-- docs/                maintained documentation
`-- .codex/              Codex adapter configuration
```

## Directory Contracts

`.workspace/` contains the internal path map and minimal future extension
points. It is not a framework competing with Codex.
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

`runtime/` contains derived task indexes, framework run records, intermediate
outputs, logs, temporary data, and disposable sandboxes. Canonical task state
remains in `projects/<name>/task.md`. Only runtime README contracts are intended
for Git.

`storage/artifacts/` is for reviewed local deliverables. `storage/archives/` is
for durable local historical or normative material, not caches. Only their
README contracts are intended for the workspace repository.

`.local/envs/` and `.local/secrets/` are ignored and outside the default Agent
read scope. Reproducible environment definitions should live in a future
tracked infrastructure area, not under `.local/`.

`projects/` is the local concrete work area for both lifecycle-managed tasks
and standalone projects. The V2 workspace repository tracks only
`projects/README.md`; concrete directories are ignored and excluded
from workspace-wide recursive scans. Drafts may remain local without Git.
Every direct concrete directory requires a top-level `AGENTS.md`; workspace
checks verify only that shallow contract and do not recursively inspect project
contents. Stable rules live in `AGENTS.md`, while changing execution and
handoff state remains in the owning task or project documentation.
Each concrete directory also requires `task.md` or `project.md`. Project state
documents contain status, goal, acceptance criteria, decisions, progress, next
action, blockers, and verification evidence. `workspace.py handoff <name>`
renders those sources plus current Git context without creating a duplicate
persistent handoff file.
Archived or abandoned projects move to
`storage/archives/projects/<project-name>/`. Concrete project contents remain
outside the workspace root repository at every lifecycle stage. Long-lived or
publishable projects may use independent Git repositories only after explicit
approval.

## Common Operating Principles

These principles define the common operating model for the workspace:

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

## Current Tasks And Projects

Preview or create a lifecycle-managed task under `projects/`:

```powershell
python -B capabilities/tools/workspace.py new my-task --complexity standard --dry-run
python -B capabilities/tools/workspace.py new my-task --complexity standard
```

The task scaffold provides `task.md`, `summary.md`, task-local rules, source,
tests, outputs, deliverables, temporary files, and logs. It uses only the
workspace-root Skills and does not create a task-private Skill tree. Status,
resume, verification, and closeout remain task-specific. Doctor and handoff
support both task state in `task.md` and standalone-project state in
`project.md`.

Before changing Agents, update the owning state file and review a generated
handoff packet:

```powershell
python -B capabilities/tools/workspace.py doctor my-task
python -B capabilities/tools/workspace.py handoff my-task
```

Preview or create a minimal project scaffold:

```powershell
python -B capabilities/tools/workspace.py project new my-project --dry-run
python -B capabilities/tools/workspace.py project new my-project
```

Standalone projects use `project.md` for current handoff state. Run
`workspace.py doctor my-project` and `workspace.py handoff my-project` before
changing Agents.

The command creates project-local rules, goal documentation, source, tests,
scripts, documentation, outputs, temporary files, and log directories. It does
not initialize Git, install dependencies, or publish anything. It also creates
`docs/open-source-assessment.md`.

Before implementation, use read-only web and repository research to compare
current open-source options. Prefer three to five viable candidates when
available, and evaluate the reviewed source/version, license obligations,
maintenance, security, technical fit, integration cost, and reuse boundary.
Choose `greenfield`, `reference`, `integrate`, or `fork` and record the evidence
in the generated assessment. A simple project may use a concise table and does
not need repeated human review.

Research alone does not authorize mutation. Cloning, downloading, installing a
dependency, copying code, or creating a fork requires explicit approval.
Missing, ambiguous, or incompatible licensing rules out code reuse; preserve
required notices and attribution for approved reuse.

The workspace repository owns the `projects/` area contract, not concrete task
or project contents.
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
