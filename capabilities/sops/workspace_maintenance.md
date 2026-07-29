# Workspace Maintenance SOP

Use this SOP after broad workspace edits, before handoff, and periodically while the workspace evolves.

## Procedure

1. Run `python -B capabilities/tools/workspace.py check` for a quick, read-only routine check.
2. Run `python -B capabilities/tools/workspace.py check --full` before broad framework handoff.
3. Review `WORKSPACE_STATUS.md` after a full check.
4. Run `git ls-files runtime .local` and confirm only intended README contracts
   are tracked from local or regenerable areas.
5. Update root docs when the workspace structure, tools, SOPs, prompts, or safety model changes.
6. Keep task-specific details inside task folders unless the knowledge is reusable across tasks.
7. Do not recursively scan or modify the external tasks root during framework
   maintenance.

Task creation is disabled while the external tasks root is configured read-only.

## When To Run

- after adding or changing root tools
- after changing `.gitignore` or `.gitattributes`
- after adding, archiving, or reorganizing tasks
- before the first workspace commit
- before handing the workspace to another agent

## Safety Rules

- Do not delete cleanup candidates without explicit approval.
- Do not stage generated outputs, logs, dependency folders, raw media, or local secrets.
- Treat `python -B capabilities/tools/audit_git_readiness.py` as the default commit gate.
- Treat `python -B capabilities/tools/audit_git_readiness.py --max-mb 1` as a stricter review reminder, not an automatic failure.

## Expected Report

End with:

- maintenance command result
- Git candidate count
- readiness audit result
- workspace status freshness result
- line ending drift reminders, if any
- strict large-file reminders, if any
- private task tracking check
