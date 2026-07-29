# New Task SOP

1. Choose a portable task name in snake_case or kebab-case.
2. Classify the task as `simple`, `standard`, or `complex`.
3. Preview the target and scaffold with
   `python -B capabilities/tools/workspace.py new <task_name> --complexity <level> --dry-run`.
4. Stop after the preview while the configured external tasks root remains
   `read_only`; do not weaken the policy merely to create a task.
5. Before a future write-enabled phase, confirm the exact external root, task
   ownership, applicable root `AGENTS.md`, source baseline, and explicit user
   approval.
6. Only after that review, configure `read_write` and run
   `python -B capabilities/tools/workspace.py new <task_name> --complexity <level>`.
7. Open `<external_tasks_root>/<task_name>/task.md` and record the goal,
   non-goals, constraints, inputs, acceptance criteria, and verification commands.
8. Read the owning workspace rules and the task-local `AGENTS.md`; the stricter
   safety rule applies.
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
