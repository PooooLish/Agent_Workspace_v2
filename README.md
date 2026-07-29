# Agent Workspace V2

一个隔离构建的 Codex 工作空间骨架。它将控制规则、可复用能力、运行状态、
长期产物和本机私有数据分层，并以只读外部根引用旧工作空间中的任务。

## 快速开始

```powershell
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py doctor
python -B capabilities/tools/workspace.py project new my-project --dry-run
```

任务目录由 `.workspace/config.json` 统一解析。第一阶段配置为
`../agent_workspace/tasks`、`read_only`；因此状态查看可用，而新建任务、
执行任务验证和关闭任务会被拒绝。`AGENT_TASKS_ROOT` 可覆盖路径，但不能覆盖
访问级别。

目录入口：

- `.workspace/`：工作空间控制配置
- `.agents/skills/`：Codex Skill 发现入口
- `capabilities/`：SOP、Prompt 和工具
- `projects/`：本地项目区；V2 根仓库只跟踪入口说明
- `runtime/`：本地运行状态与临时数据
- `storage/`：仅本地保存的长期产物与归档
- `.local/`：本机环境和凭据，默认禁止读取并由 Git 忽略
- `docs/`：框架与环境文档

## 工作方式

- `AGENTS.md` 是强制规则；Skill、SOP 和 Prompt 都不能降低其安全要求。
- Skill 用于按意图匹配可复用能力，SOP 用于直接执行固定流程，Prompt 只是非强制模板。
- 简单任务只需简短对话计划、聚焦验证和一次自审，不创建规格/计划文件，也不增加
  不必要的多轮人工确认；复杂或多 Agent 任务才使用正式计划与协调契约。
- `workspace.py check --full` 只验证状态，不自动重写文档；需要更新清单时显式运行
  `workspace.py update-status`。
- 外部任务默认只读。`new --dry-run` 可以预览，新建、执行命令和关闭任务仍被阻止。
- 发布 V2 或独立任务前，分别检查候选文件、密钥、私有数据、大文件和目标仓库。
- V2 远端仓库只维护 workspace 架构。具体项目、运行状态、产物和归档均保持本地；
  根仓库只跟踪这些目录的规则说明。

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
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py doctor
python -B capabilities/tools/workspace.py project new my-project --dry-run
```

`.workspace/config.json` resolves the tasks root. Phase one points to
`../agent_workspace/tasks` with `read_only` access. Read-only views work, while
task creation, verification execution, and task closeout are blocked.
`AGENT_TASKS_ROOT` may override the location but not its access policy.

## Operating Model

- `AGENTS.md` is mandatory; Skills, SOPs, and prompts cannot weaken its safety
  rules.
- Skills match reusable intent, SOPs define direct procedures, and prompts are
  non-authoritative templates.
- Simple work uses a short conversational plan, focused verification, one
  self-review, and no formal spec or repeated approval cycle. Complex or
  multi-agent work may use task-local plans and coordination contracts.
- `workspace.py check --full` verifies tracked status without rewriting it. Run
  `workspace.py update-status` explicitly when the inventory changes.
- External tasks are read-only by default. `new --dry-run` previews a target;
  creation, command execution, and closeout remain blocked.
- The V2 remote maintains workspace architecture only. Concrete projects,
  runtime state, artifacts, and archives remain local; only their directory
  contracts are tracked.
- Review candidates, secrets, private data, large files, and the destination
  repository separately before publishing V2 or an independent task.

See [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) for architecture and maintenance,
[AGENTS.md](AGENTS.md) for mandatory Agent rules, and
[WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) for generated current state.

</details>
