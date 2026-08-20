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
The `policies/`, `profiles/`, and `schemas/` subdirectories are reserved
extension points. `.workspace/registry/skills.remote.json` is the active,
machine-readable remote Skill catalog; it is metadata, not a second Skill body
location or policy source. Implemented tool checks validate it against Git-tracked
Skill bodies.

`.agents/skills/` is the sole reusable Codex skill body location.
Remote Skill membership is declared in
`.workspace/registry/skills.remote.json`. Running
`workspace.py update-local-skills` writes every discovered non-remote Skill to
the ignored `runtime/skills.local.json`. Both catalogs use `version`, `scope`,
and ordered `skills` entries containing `name` and workspace-relative `path`.

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
Every direct concrete directory uses a top-level `AGENTS.md`. Default workspace
architecture checks exclude concrete project state; `workspace.py doctor` and
the explicit shallow local-project check inspect handoff contracts without
recursively scanning project contents.
Each concrete directory also requires `task.md` or `project.md`. Project state
documents contain status, goal, acceptance criteria, decisions, progress, next
action, blockers, and verification evidence. `workspace.py handoff <name>`
renders those sources plus current Git context without creating a duplicate
persistent handoff file.
Archived or abandoned projects move to
`storage/archives/projects/<project-name>/`. Concrete project contents remain
outside the workspace root repository at every lifecycle stage. Independent
project repositories are separate ownership domains from the workspace root.

## Policy Source

`AGENTS.md` is the only permanent policy source. This guide documents topology,
component responsibilities, and supported commands. Skills, SOPs, prompts,
framework notes, and generated status are operational or descriptive material,
not additional policy layers.

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

Workspace architecture checks intentionally exclude local project state, so an
ignored concrete project cannot block framework maintenance. Use `doctor` for
handoff readiness. The direct `check_workspace.py --local-projects` option is a
shallow contract diagnostic and does not recurse into project contents.

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

Open-source intake requirements are defined in `AGENTS.md`; the executable
workflow lives in `capabilities/sops/open_source_project_intake.md`. The guide
records only where the resulting assessment belongs.

The workspace repository owns the `projects/` area contract, not concrete task
or project contents. Independent project repositories are rooted inside their
own project directories. Archived project placement is
`storage/archives/projects/<project-name>/`.

## Adapter Boundaries

`.codex/` holds project-scoped Codex adapter configuration and no credentials.
`.agents/skills/` remains the skill entry. V2 does not copy `.superpowers/`
execution state or create `.worktrees/`.

## Maintenance

```powershell
python -B capabilities/tools/test_v2_workspace.py
python -B capabilities/tools/test_workspace_tools.py
python -B capabilities/tools/check_workspace.py
python -B capabilities/tools/check_workspace.py --local-projects
python -B capabilities/tools/workspace.py check
```

Workspace tests place temporary fixtures under `runtime/tmp/`. Baseline reports
support before-and-after comparison when evaluating framework changes.

## Document Roles

- `README.md`: user-facing introduction and quick start.
- `AGENTS.md`: mandatory top-level Agent and safety rules.
- `WORKSPACE_GUIDE.md`: architecture rationale and maintenance entry points.
- `WORKSPACE_STATUS.md`: deterministic inventory of Git-tracked remote architecture only.
