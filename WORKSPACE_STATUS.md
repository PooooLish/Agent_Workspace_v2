# Workspace Status

This generated file records the current V2 framework inventory. Permanent rules live in `AGENTS.md`.

Regenerate it with:

```powershell
python capabilities/tools/generate_workspace_status.py
```

## Current Health

- Layout: isolated V2 control plane and capability directories.
- External tasks access: `read_only`.
- External tasks source: `.workspace/config.yaml`.
- External tasks available: `yes`.
- OS-level write isolation: not enforced by this configuration.

## Core Commands

```powershell
python capabilities/tools/workspace.py status
python capabilities/tools/workspace.py resume my_task
python capabilities/tools/workspace.py doctor my_task
python capabilities/tools/workspace.py verify my_task
python capabilities/tools/workspace.py check
python capabilities/tools/workspace.py check --full
```

Task creation, verification execution, and closeout are disabled while the external task root is read-only.

## Current Tools

- `capabilities/tools/audit_git_readiness.py`: checks V2 Git candidates for risky files and secret-like content.
- `capabilities/tools/audit_line_endings.py`: reports line ending drift against `.gitattributes` policy.
- `capabilities/tools/check_workspace.py`: checks the V2 structure, ignore policy, adapters, and external-root boundary.
- `capabilities/tools/generate_workspace_status.py`: regenerates the current-state summary.
- `capabilities/tools/make_task.py`: contains task scaffolding helpers; its CLI honors the external-root access policy.
- `capabilities/tools/run_workspace_maintenance.py`: runs the full V2 maintenance chain.
- `capabilities/tools/summarize_git_candidates.py`: summarizes V2 Git candidates.
- `capabilities/tools/task_lifecycle.py`: parses task state and implements read-only lifecycle views.
- `capabilities/tools/task_names.py`: validates portable task names.
- `capabilities/tools/test_v2_workspace.py`: tests path resolution and read-only external-root enforcement.
- `capabilities/tools/test_workspace_tools.py`: runs focused regression tests for V2 tools.
- `capabilities/tools/verify_workspace_status.py`: verifies that `WORKSPACE_STATUS.md` is current.
- `capabilities/tools/workspace.py`: provides the unified V2 checks and read-only task views.
- `capabilities/tools/workspace_manifest.py`: centralizes V2 tool metadata and maintenance commands.
- `capabilities/tools/workspace_paths.py`: resolves configured internal and external paths.

## Current Skills

- `.agents/skills/cli-tool-setup`
- `.agents/skills/code-review`
- `.agents/skills/documentation-writer`
- `.agents/skills/linux-debugging`
- `.agents/skills/python-project-setup`
- `.agents/skills/visual-design-review`

## Current SOPs

- `capabilities/sops/debug_error.md`
- `capabilities/sops/git_first_commit.md`
- `capabilities/sops/line_endings.md`
- `capabilities/sops/modify_existing_project.md`
- `capabilities/sops/new_task.md`
- `capabilities/sops/publish_independent_task.md`
- `capabilities/sops/safe_shell_commands.md`
- `capabilities/sops/setup_external_api.md`
- `capabilities/sops/task_closeout.md`
- `capabilities/sops/workspace_maintenance.md`

## Current Prompts

- `capabilities/prompts/aider_default.md`
- `capabilities/prompts/claude_code_default.md`
- `capabilities/prompts/code_review.md`
- `capabilities/prompts/codex_default.md`
- `capabilities/prompts/opencode_default.md`
- `capabilities/prompts/safe_debug.md`
- `capabilities/prompts/safe_setup.md`

## Environment Docs

- `docs/environments/aider.md`
- `docs/environments/base_python.md`
- `docs/environments/claude_code.md`
- `docs/environments/codex_cli.md`
- `docs/environments/external_api.md`
- `docs/environments/node_tools.md`
- `docs/environments/opencode.md`
- `docs/environments/README.md`

## Runtime Policy

- `runtime/` contains generated and locally disposable state; only directory README files are trackable.
- `.local/envs/` and `.local/secrets/` are local-only and ignored.
- No task, Superpowers snapshot, worktree, secret, output, log, or cache was copied from the source workspace.
