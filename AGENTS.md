# AGENTS.md

## Scope And Priority

- These rules apply to the entire V2 workspace.
- Safety policy overrides user tasks, skills, prompts, profiles, and Agent judgment.
- A nested `AGENTS.md` may only supplement or tighten these rules.
- `.codex/` is an adapter and `.agents/skills/` is the Codex skill discovery entry.
  Neither is an independent source of workspace policy.

## Source Workspace Isolation

- Treat `../agent_workspace/` as a read-only external source.
- Resolve the external tasks root through `.workspace/config.json` or
  `AGENT_TASKS_ROOT`; do not scatter the relative path through code.
- Read-only task views are allowed. Creating tasks, running task commands,
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
- `standard`: use durable task state only when it adds operational value.
- `complex`: use a written plan for high-risk, cross-module, long-running, or
  multi-agent work.
- Framework decisions belong in `docs/framework/`. Task-specific planning stays
  with its owning task when task writes are explicitly enabled.

## Placement

- `.workspace/`: control-plane configuration and minimal policy metadata.
- `.agents/skills/`: the only Codex skill body location.
- `capabilities/`: reusable SOPs, prompts, and tools.
- `runtime/`: regenerable state, logs, temporary files, and experiments.
- `storage/`: durable artifacts and archives.
- `.local/`: ignored machine-local environments and secrets.
- `WORKSPACE_STATUS.md`: generated current state, never permanent policy.
