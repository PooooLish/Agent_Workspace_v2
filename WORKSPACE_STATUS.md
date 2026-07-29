# Workspace Status

This generated file records the current V2 framework inventory. Permanent rules live in `AGENTS.md`.

Regenerate it with:

```powershell
python -B capabilities/tools/workspace.py update-status
```

## Current Health

- Layout: isolated V2 control plane and capability directories.
- External tasks access: `read_only`.
- OS-level write isolation: not enforced by this configuration.

## Reserved Control Plane

- `.workspace/policies/`, `profiles/`, `registry/`, and `schemas/` are reserved extension points.
- Their README files are documentation only; no policy engine, role system, registry loader, or schema enforcement is active.
- `AGENTS.md` and implemented tool checks remain the enforceable workspace controls.

## Core Commands

```powershell
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py resume my_task
python -B capabilities/tools/workspace.py doctor my_task
python -B capabilities/tools/workspace.py verify my_task
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py check --full
python -B capabilities/tools/workspace.py update-status
```

Task creation, verification execution, and closeout are disabled while the external task root is read-only.

## Local Project Policy

- The workspace repository tracks only `projects/README.md` under `projects/`.
- Concrete project directories are local and ignored by the workspace repository.
- Archived or abandoned projects live under `storage/archives/projects/` and remain local.
- Runtime state, artifact contents, and archive contents are not tracked by the workspace repository.
- Long-lived or publishable projects should use independent Git repositories after explicit approval.
- Project scaffolding does not initialize Git, install dependencies, or publish files.

```powershell
python -B capabilities/tools/workspace.py project new my-project --dry-run
python -B capabilities/tools/workspace.py project new my-project
```

## Review Proportionality

- Simple work uses a short conversational plan, focused verification, one self-review, and a concise report.
- Simple work does not require standalone specifications, implementation plans, or repeated human review gates.
- Formal planning and review remain appropriate for high-risk, cross-module, long-running, destructive, or multi-agent work.

## Open Source Intake

- Research current open-source repositories and authoritative documentation before implementing a new software project.
- Record source/version, license, maintenance, security, fit, reuse boundary, and a `greenfield`, `reference`, `integrate`, or `fork` decision.
- Simple projects may use a concise assessment without repeated human review.
- Cloning, downloading, dependency installation, code copying, and forking require explicit approval.
- Missing, ambiguous, or incompatible licensing prohibits code reuse.

## Current Tools

- `capabilities/tools/audit_git_readiness.py`: checks V2 Git candidates for risky files and secret-like content.
- `capabilities/tools/audit_line_endings.py`: reports line ending drift against `.gitattributes` policy.
- `capabilities/tools/check_python_syntax.py`: checks maintained Python source without writing bytecode.
- `capabilities/tools/check_workspace.py`: checks the V2 structure, ignore policy, adapters, and external-root boundary.
- `capabilities/tools/generate_workspace_status.py`: regenerates the current-state summary.
- `capabilities/tools/make_project.py`: creates a local project scaffold without initializing Git.
- `capabilities/tools/make_task.py`: contains task scaffolding helpers; its CLI honors the external-root access policy.
- `capabilities/tools/prepare_baseline_report.py`: provides a compatibility entry for the V2 first-commit report.
- `capabilities/tools/prepare_first_commit_report.py`: writes a bounded V2 first-commit recommendation report.
- `capabilities/tools/run_workspace_maintenance.py`: runs the full V2 maintenance chain.
- `capabilities/tools/summarize_git_candidates.py`: summarizes V2 Git candidates.
- `capabilities/tools/task_lifecycle.py`: parses task state and implements read-only lifecycle views.
- `capabilities/tools/task_names.py`: validates portable task names.
- `capabilities/tools/test_v2_workspace.py`: tests path resolution and read-only external-root enforcement.
- `capabilities/tools/test_workspace_tools.py`: runs focused regression tests for V2 tools.
- `capabilities/tools/verify_baseline_report.py`: provides a compatibility entry for V2 report verification.
- `capabilities/tools/verify_first_commit_report.py`: verifies the generated V2 first-commit report.
- `capabilities/tools/verify_workspace_status.py`: verifies that `WORKSPACE_STATUS.md` is current.
- `capabilities/tools/workspace.py`: provides the unified V2 checks and read-only task views.
- `capabilities/tools/workspace_manifest.py`: centralizes V2 tool metadata and maintenance commands.
- `capabilities/tools/workspace_paths.py`: resolves configured internal and external paths.

## Current Skills

- `.agents/skills/cli-tool-setup`
- `.agents/skills/code-review`
- `.agents/skills/documentation-writer`
- `.agents/skills/linux-debugging`
- `.agents/skills/open-source-project-research`
- `.agents/skills/python-project-setup`
- `.agents/skills/visual-design-review`

## Current SOPs

- `capabilities/sops/debug_error.md`
- `capabilities/sops/git_first_commit.md`
- `capabilities/sops/line_endings.md`
- `capabilities/sops/modify_existing_project.md`
- `capabilities/sops/new_task.md`
- `capabilities/sops/open_source_project_intake.md`
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

## Current Framework Docs

- `docs/framework/agent-compatibility.md`
- `docs/framework/git-task-isolation.md`
- `docs/framework/task-lifecycle.md`
- `docs/framework/workspace-efficiency.md`

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
- `storage/` contains durable local data; only directory README contracts are trackable.
- `.local/envs/` and `.local/secrets/` are local-only and ignored.
- No task, Superpowers snapshot, worktree, secret, output, log, or cache was copied from the source workspace.
