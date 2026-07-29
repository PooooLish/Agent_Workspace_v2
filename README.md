# Agent Workspace V2

一个隔离构建的 Codex 工作空间骨架。它将控制规则、可复用能力、运行状态、
长期产物和本机私有数据分层，并以只读外部根引用旧工作空间中的任务。

## 快速开始

```powershell
python capabilities/tools/workspace.py check
python capabilities/tools/workspace.py status
python capabilities/tools/workspace.py doctor
```

任务目录由 `.workspace/config.yaml` 统一解析。第一阶段配置为
`../agent_workspace/tasks`、`read_only`；因此状态查看可用，而新建任务、
执行任务验证和关闭任务会被拒绝。`AGENT_TASKS_ROOT` 可覆盖路径，但不能覆盖
访问级别。

目录入口：

- `.workspace/`：工作空间控制配置
- `.agents/skills/`：Codex Skill 发现入口
- `capabilities/`：SOP、Prompt 和工具
- `runtime/`：本地运行状态与临时数据
- `storage/`：长期产物与归档
- `.local/`：本机环境和凭据，默认禁止读取并由 Git 忽略
- `docs/`：框架与环境文档

完整设计与维护规则见 [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md)，Agent 顶层规则
见 [AGENTS.md](AGENTS.md)，当前状态见 [WORKSPACE_STATUS.md](WORKSPACE_STATUS.md)。

<details>
<summary><strong>English</strong></summary>

## Overview

Agent Workspace V2 is an isolated Codex workspace scaffold. It separates control
configuration, reusable capabilities, runtime state, durable storage, and
machine-local private data. Existing tasks are referenced as an external
read-only root rather than copied.

## Quick Start

```powershell
python capabilities/tools/workspace.py check
python capabilities/tools/workspace.py status
python capabilities/tools/workspace.py doctor
```

`.workspace/config.yaml` resolves the tasks root. Phase one points to
`../agent_workspace/tasks` with `read_only` access. Read-only views work, while
task creation, verification execution, and task closeout are blocked.
`AGENT_TASKS_ROOT` may override the location but not its access policy.

See [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) for architecture and maintenance,
[AGENTS.md](AGENTS.md) for mandatory Agent rules, and
[WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) for generated current state.

</details>

