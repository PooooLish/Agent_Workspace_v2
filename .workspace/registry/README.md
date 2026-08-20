# Registry

`skills.remote.json` is the authoritative, version-controlled catalog of Skills
published with the workspace architecture. Each entry has a unique `name` and
its workspace-relative Skill directory `path`; `scope` is `workspace-remote`.

Skill bodies remain under `.agents/skills/`. Run
`python -B capabilities/tools/workspace.py update-local-skills` to write the
separate ignored catalog at `runtime/skills.local.json`; its scope is
`workspace-local` and it contains only discovered Skills absent from the remote
catalog.
