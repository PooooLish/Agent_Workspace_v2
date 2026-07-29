# Task Lifecycle

The V2 task lifecycle is deliberately read-only in phase one.

```powershell
python capabilities/tools/workspace.py status
python capabilities/tools/workspace.py resume my_task
python capabilities/tools/workspace.py doctor my_task
python capabilities/tools/workspace.py verify my_task
```

`verify` without `--run` previews declared commands. `new`, `verify --run`, and
`close` are blocked by the external-root access policy.

If a later phase enables writes, change the access policy only after the source
baseline and task ownership model are reviewed. Mutating commands must continue
to use the centralized guard. Task-local outputs, logs, and temporary files stay
inside the task repository; V2 framework state stays under `runtime/`.

