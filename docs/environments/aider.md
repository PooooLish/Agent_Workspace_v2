# Aider

Start Aider inside a task and pass framework context explicitly:

```powershell
aider --read ../../AGENTS.md --read AGENTS.md --read task.md
```

When a reusable workflow applies, also pass its canonical file, for example:

```powershell
aider --read ../../.agents/skills/code-review/SKILL.md
```

Aider does not natively discover this repository's `.agents/skills/` directory.
