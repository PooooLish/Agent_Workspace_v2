# Task Closeout SOP

1. Preview verification with `python -B capabilities/tools/workspace.py verify <task_name>`.
2. Review every command and obtain explicit approval before `verify --run`.
3. Clean up task notes so another agent can understand the result.
4. Complete `summary.md` with goal, outcome, changes, verification, and open issues.
5. Run `python -B capabilities/tools/workspace.py doctor <task_name>`.
6. Run `python -B capabilities/tools/workspace.py close <task_name>` after
   explicit approval.
7. Keep reproducible generated results in `outputs/`, stable docs in `docs/`, and
   reviewed publishable final artifacts in `deliverables/`.
8. Archive only as a separate, deliberate action after explicit approval.
9. Do not archive secrets or unnecessary temporary files.
10. Publish a selected task only through an independent Git repository inside that task directory.
