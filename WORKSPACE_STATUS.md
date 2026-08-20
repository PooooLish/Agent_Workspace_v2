# Workspace Status

This generated file records the version-controlled V2 remote architecture.
Permanent policy lives only in `AGENTS.md`.

Regenerate it with:

```powershell
python -B capabilities/tools/workspace.py update-status
```

## Remote Tools

- `capabilities/tools/audit_git_readiness.py`: checks V2 Git candidates for risky files and secret-like content.
- `capabilities/tools/audit_line_endings.py`: reports line ending drift against `.gitattributes` policy.
- `capabilities/tools/check_python_syntax.py`: checks maintained Python source without writing bytecode.
- `capabilities/tools/check_workspace.py`: checks the V2 structure, ignore policy, adapters, and legacy external-root boundary.
- `capabilities/tools/generate_workspace_status.py`: regenerates the tracked remote architecture inventory.
- `capabilities/tools/make_project.py`: creates a local project scaffold without initializing Git.
- `capabilities/tools/make_task.py`: creates lifecycle-managed task scaffolds under the configured projects root.
- `capabilities/tools/prepare_baseline_report.py`: provides a compatibility entry for the V2 first-commit report.
- `capabilities/tools/prepare_first_commit_report.py`: writes a bounded V2 first-commit recommendation report.
- `capabilities/tools/run_workspace_maintenance.py`: runs the full V2 maintenance chain.
- `capabilities/tools/summarize_git_candidates.py`: summarizes V2 Git candidates.
- `capabilities/tools/task_lifecycle.py`: parses and manages lifecycle state for current tasks under projects.
- `capabilities/tools/task_names.py`: validates portable task names.
- `capabilities/tools/test_opencode_v2.py`: tests V2 OpenCode path isolation and project-boundary enforcement.
- `capabilities/tools/test_v2_workspace.py`: tests configured V2 project-path isolation.
- `capabilities/tools/test_workspace_tools.py`: runs focused regression tests for V2 tools.
- `capabilities/tools/verify_baseline_report.py`: provides a compatibility entry for V2 report verification.
- `capabilities/tools/verify_first_commit_report.py`: verifies the generated V2 first-commit report.
- `capabilities/tools/verify_workspace_status.py`: verifies that `WORKSPACE_STATUS.md` is current.
- `capabilities/tools/workspace.py`: provides unified V2 checks and current task lifecycle commands.
- `capabilities/tools/workspace_manifest.py`: centralizes V2 tool metadata and maintenance commands.
- `capabilities/tools/workspace_paths.py`: resolves configured internal workspace paths.

## Remote Skills

- `.agents/skills/cli-tool-setup`
- `.agents/skills/code-review`
- `.agents/skills/dependency-and-security-review`
- `.agents/skills/documentation-writer`
- `.agents/skills/grill-me`
- `.agents/skills/grilling`
- `.agents/skills/linux-debugging`
- `.agents/skills/open-source-project-research`
- `.agents/skills/python-project-setup`
- `.agents/skills/systematic-debugging`
- `.agents/skills/verification-before-completion`
- `.agents/skills/visual-design-review`

## Remote SOPs

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

## Remote Prompts

- `capabilities/prompts/aider_default.md`
- `capabilities/prompts/claude_code_default.md`
- `capabilities/prompts/code_review.md`
- `capabilities/prompts/codex_default.md`
- `capabilities/prompts/opencode_default.md`
- `capabilities/prompts/safe_debug.md`
- `capabilities/prompts/safe_setup.md`

## Remote Framework Docs

- `docs/framework/agent-compatibility.md`
- `docs/framework/git-task-isolation.md`
- `docs/framework/task-lifecycle.md`
- `docs/framework/workspace-efficiency.md`

## Remote Environment Docs

- `docs/environments/aider.md`
- `docs/environments/base_python.md`
- `docs/environments/claude_code.md`
- `docs/environments/codex_cli.md`
- `docs/environments/external_api.md`
- `docs/environments/node_tools.md`
- `docs/environments/opencode.md`
- `docs/environments/README.md`
