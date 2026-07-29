# Local Projects

This directory is the V2 project area.

- The workspace repository tracks this file only.
- Concrete project directories are ignored by the workspace repository.
- Active, archived, and abandoned project contents always remain local.
- Create a project scaffold with:

  ```powershell
  python -B capabilities/tools/workspace.py project new my-project
  ```

- The command does not initialize Git, install dependencies, or publish files.
- A long-lived or publishable project should become an independent Git
  repository only after explicit approval.
- Workspace maintenance tools must not recursively scan project contents.
