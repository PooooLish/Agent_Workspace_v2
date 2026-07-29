# Agent Compatibility

## Capability Matrix

| Agent | Root rules | `.agents/skills/` discovery | Recommended use |
| --- | --- | --- | --- |
| Codex | `AGENTS.md` | Native | Start in V2 and allow intent-based Skill matching. |
| OpenCode | `AGENTS.md` | Native | Start in V2 and allow intent-based Skill matching. |
| Claude Code | Explicit prompt or `CLAUDE.md` adapter | Not native | Prompt it to read the relevant `.agents/skills/<name>/SKILL.md`. |
| Aider | `--read` files | Not native | Pass root rules and selected Skill files with `--read`. |

`.agents/skills/` is the single source of truth in this repository. Do not copy
Skill bodies into tool-specific directories because duplicated instructions
drift. For tools without native discovery, select a relevant Skill explicitly
and provide its path as context.

Tasks are external and read-only in phase one. Agents start in V2, resolve the
task root through `.workspace/config.yaml`, and must not infer write permission
from another framework's capabilities.
