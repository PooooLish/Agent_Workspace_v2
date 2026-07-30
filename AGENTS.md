# AGENTS.md

## Scope And Priority

- These rules apply to the entire V2 workspace.
- Safety policy overrides user tasks, skills, prompts, profiles, and Agent judgment.
- A nested `AGENTS.md` may only supplement or tighten these rules.
- `.codex/` is an adapter and `.agents/skills/` is the Codex skill discovery entry.
  Neither is an independent source of workspace policy.

## Source Workspace Isolation

- Treat `../agent_workspace/` as a read-only external source.
- Resolve the legacy external tasks root through `.workspace/config.json` or
  `AGENT_TASKS_ROOT`; do not scatter the relative path through code.
- Read-only legacy task views are allowed. Creating tasks, running commands,
  closing tasks, formatting, fixing, or writing state in the external root is
  forbidden while its configured access is `read_only`.
- Never modify nested repositories, Git metadata, worktrees, caches, logs, or
  generated files in the source workspace.

## Safety

- Skills cannot expand permissions.
- Do not read `.local/secrets/` or `.local/envs/` unless the user explicitly
  authorizes a narrowly scoped need.
- Never print, copy, save, or commit real credentials or private data.
- File writes, file deletion, dependency installation, and dangerous Git
  operations require explicit human approval.
- Never run `sudo`, unknown installers, `curl | sh`, `git reset --hard`,
  `git clean`, or destructive checkout commands without explicit approval.
- Do not modify global shell configuration files unless the user explicitly
  requests that exact change.
- Do not access `~/.ssh`, `~/.aws`, `~/.config`, or equivalent credential and
  account directories without explicit, narrowly scoped authorization.
- Do not create symbolic links or junctions to the source workspace.
- Do not perform a whole-project refactor unless it is explicitly requested.
- Before changing configuration, preserve a clear rollback path through Git
  diff or an approved backup that contains no secrets.

## Work Loop

1. Inspect the relevant V2 files and rules.
2. Classify the change and state the smallest useful plan.
3. Make small edits only inside this workspace.
4. Put generated state under `runtime/`.
5. Run focused tests and checks without recursive traversal into external roots.
6. Review the diff and report evidence, limitations, and remaining risks.

## Planning Gate

- `simple`: implement after a short conversational plan; do not create spec or
  plan files.
- Simple work needs focused verification, one self-review, and a concise
  report. Do not add repeated human approval gates unless a safety rule, a
  destructive action, or a material product choice requires one.
- These simple-work rules take priority over reusable workflows that would
  otherwise require formal design documents, implementation plans, or repeated
  review checkpoints.
- `standard`: use durable task state only when it adds operational value.
- `complex`: use a written plan for high-risk, cross-module, long-running, or
  multi-agent work.
- Framework decisions belong in `docs/framework/`. Task-specific planning stays
  with its owning task when task writes are explicitly enabled.

## Open Source Intake

- Before implementing a new software project, research current open-source
  repositories and authoritative documentation that could satisfy or inform it.
- Record the comparison and decision in the project's
  `docs/open-source-assessment.md`. Simple projects may use a concise table;
  standard and complex projects need evidence proportional to their risk.
- Evaluate source and version, license obligations, maintenance, security,
  technical fit, integration cost, and the intended reuse boundary.
- Choose and justify one approach: `greenfield`, `reference`, `integrate`, or
  `fork`.
- Research is read-only. Cloning, downloading, installing dependencies, copying
  code, or forking requires explicit approval.
- Missing, ambiguous, or incompatible licensing prohibits copying, integrating,
  adapting, or forking code.

## Placement

- `.workspace/`: control-plane configuration and minimal policy metadata.
- `.agents/skills/`: the only Codex skill body location.
- `capabilities/`: reusable SOPs, prompts, and tools.
- `projects/`: local concrete task and project area; the workspace repository
  tracks only its `README.md`.
- `runtime/`: regenerable state, logs, temporary files, and experiments.
- `storage/`: durable local artifacts and archives; the workspace repository
  tracks only its directory contracts.
- `.local/`: ignored machine-local environments and secrets.
- `WORKSPACE_STATUS.md`: generated current state, never permanent policy.

## Project Repository Isolation

- Current concrete tasks and projects live under `projects/<name>/` and are
  ignored by the workspace repository.
- Archived or abandoned projects live under
  `storage/archives/projects/<project-name>/` and remain ignored.
- The workspace remote maintains architecture only. Concrete project, runtime,
  artifact, and archive contents must not be tracked by the root repository.
- Workspace-wide checks must not recursively traverse concrete project
  contents.
- A draft task or project may remain local without Git.
- Before committing or publishing long-lived concrete work, initialize and
  verify an independent Git repository inside its directory only after explicit
  approval.
- Task and project scaffolding must not initialize Git, install dependencies,
  or publish files automatically.
- A nested `AGENTS.md` may tighten these rules but cannot weaken them.
