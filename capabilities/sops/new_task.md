# New Task SOP

1. Choose a portable task name in snake_case or kebab-case.
2. Classify the task as `simple`, `standard`, or `complex`.
3. Preview the target and scaffold with
   `python -B capabilities/tools/workspace.py new <task_name> --complexity <level> --dry-run`.
4. Confirm the target is `projects/<task_name>/`, that no project or task
   already uses the name, and obtain explicit approval for the scaffold write.
5. Run
   `python -B capabilities/tools/workspace.py new <task_name> --complexity <level>`.
6. Open `projects/<task_name>/task.md` and record the goal,
   non-goals, constraints, inputs, acceptance criteria, and verification commands.
7. Read the workspace rules and the task-local `AGENTS.md`; the stricter
   safety rule applies.
8. Use only the workspace-root Skills; do not create a task-private Skill tree.
9. Keep task work inside that task folder. Store generated results in
   `outputs/`, reviewed artifacts in `deliverables/`, scratch files in `tmp/`,
   and logs in `logs/`.
10. Run `python -B capabilities/tools/workspace.py doctor <task_name>` after
    filling the task state.
11. Update the task `README.md` when its workflow changes.

Keep `Status`, `Progress`, `Next action`, and `Blockers` current after meaningful work so another agent can resume without reconstructing the task history. Use the generated `summary.md` for the final outcome, changes, verification, and open issues.

Simple tasks must not create standalone specification or plan files. Complex
tasks use `docs/superpowers/` for task-local planning and
`coordination/contract.md` for multi-agent boundaries.
