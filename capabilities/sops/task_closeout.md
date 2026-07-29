# Task Closeout SOP

1. Preview verification with `python capabilities/tools/workspace.py verify <task_name>`.
2. Review every command. Execution remains disabled while the external tasks root is read-only.
3. Clean up task notes so another agent can understand the result.
4. Complete `summary.md` with goal, outcome, changes, verification, and open issues.
5. Run `python capabilities/tools/workspace.py doctor <task_name>`.
6. Closeout is disabled while the external tasks root is read-only.
7. Keep reproducible generated results in `outputs/`, stable docs in `docs/`, and
   reviewed publishable final artifacts in `deliverables/`.
8. Archive only as a separate, deliberate action after write access is explicitly enabled.
9. Do not archive secrets or unnecessary temporary files.
10. Publish a selected task only through an independent Git repository inside that task directory.
