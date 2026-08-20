# Workspace Maintenance SOP

Use this SOP after broad workspace edits, before handoff, and periodically while the workspace evolves.

## Procedure

1. Run `python -B capabilities/tools/workspace.py check` for a quick, read-only routine check.
2. Run `python -B capabilities/tools/workspace.py check --full` before broad framework handoff.
3. Run `python -B capabilities/tools/workspace.py update-local-skills` when local
   Skill discovery changes, then review the ignored `runtime/skills.local.json`.
4. Review `WORKSPACE_STATUS.md` as the Git-tracked remote architecture inventory
   after a full check; regenerate it explicitly with `workspace.py update-status`.
5. Run `git ls-files runtime storage .local` and confirm only intended README
   contracts are tracked from local, durable, or regenerable areas.
6. Update root docs when the workspace structure, tools, SOPs, prompts, or safety model changes.
7. Keep task-specific details inside task folders unless the knowledge is reusable across tasks.
8. Run `workspace.py doctor` separately when local project handoff health is in
   scope. Do not recursively scan concrete `projects/` contents during framework
   maintenance.

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
- concrete task and project tracking check
