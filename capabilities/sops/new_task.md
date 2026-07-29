# New Task SOP

1. Choose a clear task name in snake_case or kebab-case.
2. Classify the task as `simple`, `standard`, or `complex`.
3. Confirm the configured external tasks root is explicitly `read_write`.
4. Run `python capabilities/tools/workspace.py new <task_name> --complexity <level>`.
4. Open `tasks/<task_name>/task.md` and write the goal, non-goals, constraints, inputs, acceptance criteria, and verification commands.
5. From the task directory, read `../../AGENTS.md` and the local `AGENTS.md`.
6. Do all task work inside that task folder.
8. Keep generated results in `outputs/`, reviewed publishable artifacts in
   `deliverables/`, scratch files in `tmp/`, and logs in `logs/`.
9. Run `python capabilities/tools/workspace.py doctor <task_name>` after filling the task state.

Phase one keeps the external tasks root `read_only`, so task creation is
intentionally unavailable.
9. Update `README.md` inside the task folder if the workflow changes.

Keep `Status`, `Progress`, `Next action`, and `Blockers` current after meaningful work so another agent can resume without reconstructing the task history. Use the generated `summary.md` for the final outcome, changes, verification, and open issues.

Simple tasks must not create standalone specification or plan files. Complex
tasks use `docs/superpowers/` for task-local planning and
`coordination/contract.md` for multi-agent boundaries.
