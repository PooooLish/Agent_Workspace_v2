# Workspace Efficiency

`capabilities/tools/workspace.py` is the supported entry point:

```powershell
python capabilities/tools/workspace.py check
python capabilities/tools/workspace.py check --full
python capabilities/tools/workspace.py status
python capabilities/tools/workspace.py doctor
```

Path resolution is centralized in `workspace_paths.py`. New tools should consume
configured names rather than hard-code root directories. Tests place temporary
files under `runtime/tmp/` and must not recursively discover the external source
workspace.

Use `.agents/skills/` for reusable Codex skills, `capabilities/sops/` for
procedures, `capabilities/prompts/` for templates, and `capabilities/tools/` for
executables. This keeps policy, instructions, and implementation independently
reviewable.

Quick checks run focused regression tests, structure validation, Git candidate
auditing, and line-ending validation. Full checks additionally regenerate and
verify `WORKSPACE_STATUS.md` and summarize V2 Git candidates.

