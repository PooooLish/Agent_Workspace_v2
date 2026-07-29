# Publish an Independent Task Repository

Use this SOP only after the user explicitly selects one `tasks/<task_name>/` directory for publication.

1. Confirm the exact task directory and separate GitHub repository name.
2. Read the root and task-level `AGENTS.md` and the task's `task.md`.
3. Audit the proposed repository for secrets, private data, logs, caches, generated
   output, local paths, binary files, and large files without printing secret values.
4. Confirm that intended final artifacts are in `deliverables/`; keep reproducible
   generated output in ignored `outputs/`.
5. Create or review the task-local `.gitignore`; `.env.example` may contain names and
   placeholders only, never real values.
6. Show the complete proposed first-commit file list and wait for user confirmation.
7. Initialize Git inside the selected task directory only.
8. Commit only the confirmed files and verify the commit contents.
9. Add only the confirmed independent remote and push only after explicit approval.

Never modify the root `.gitignore` to publish a task. Never publish a concrete experiment directory under `sandboxes/`; `sandboxes/README.md` is only a root-level policy placeholder.
