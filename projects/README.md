# Local Tasks And Projects

This directory is the V2 area for current concrete tasks and projects.

- The workspace repository tracks this file only.
- Concrete task and project directories are ignored by the workspace repository.
- Active, archived, and abandoned concrete contents always remain local.
- Every concrete directory must contain a top-level `AGENTS.md`. Agents read
  the workspace root rules first and then the concrete directory rules before
  changing files.
- Keep stable scope, safety, workflow, and verification rules in `AGENTS.md`.
  Keep changing progress, decisions, next action, blockers, and verification
  results in the task or project's state documentation.
- Every concrete directory must contain `task.md` or `project.md`. Before
  changing Agents, update that state and review the generated packet:

  ```powershell
  python -B capabilities/tools/workspace.py handoff <name>
  ```
- Create a lifecycle-managed task scaffold with:

  ```powershell
  python -B capabilities/tools/workspace.py new my-task
  ```

- Create a project scaffold with:

  ```powershell
  python -B capabilities/tools/workspace.py project new my-project
  ```

- The command does not initialize Git, install dependencies, or publish files.
- Task scaffolds use only shared root Skills; they do not create private Skill
  directories.
- The scaffold creates `docs/open-source-assessment.md`. Complete its read-only
  candidate, license, maintenance, security, fit, decision, and reuse-boundary
  review before implementation.
- Simple projects may keep that assessment concise. Cloning, downloading,
  installing dependencies, copying code, and forking still require explicit
  approval.
- A long-lived or publishable project should become an independent Git
  repository only after explicit approval.
- Workspace maintenance tools must not recursively scan concrete contents.
