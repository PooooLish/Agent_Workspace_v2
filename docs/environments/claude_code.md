# Claude Code

Start Claude Code inside a task. Ask it to read `../../AGENTS.md`, local
`AGENTS.md`, and `task.md` before editing.

Claude Code does not natively discover this repository's `.agents/skills/`
directory. When a Skill applies, explicitly ask it to read the canonical file,
for example `../../.agents/skills/code-review/SKILL.md`.
