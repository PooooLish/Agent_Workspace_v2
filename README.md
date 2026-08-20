# Agent Workspace V2

一个隔离构建的 Codex 工作空间骨架。它将控制规则、可复用能力、运行状态、
长期产物和本机私有数据分层。当前任务和项目统一位于 `projects/`。

## 快速开始

```powershell
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py update-local-skills
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py doctor
python -B capabilities/tools/workspace.py new my-task --dry-run
python -B capabilities/tools/workspace.py project new my-project --dry-run
```

当前任务目录由 `.workspace/config.json` 的 `paths.projects` 统一解析到
`projects/`。V2 不配置、解析或维护工作区外的历史任务目录。

目录入口：

- `.workspace/`：工作空间控制配置
- `.agents/skills/`：Codex Skill 发现入口
- `capabilities/`：SOP、Prompt 和工具
- `projects/`：当前具体任务和项目区；V2 根仓库只跟踪入口说明
- `runtime/`：本地运行状态与临时数据
- `storage/`：仅本地保存的长期产物与归档
- `.local/`：本机环境和凭据，默认禁止读取并由 Git 忽略
- `docs/`：框架与环境文档

## 文档入口

- [AGENTS.md](AGENTS.md) 是唯一的永久政策来源。
- [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) 解释目录结构、组件职责和维护入口，不定义政策。
- [WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) 是仅基于 Git 跟踪内容生成的远端架构清单，不定义政策。
- `.workspace/registry/skills.remote.json` 是远端 Skill 权威清单；
  `runtime/skills.local.json` 是忽略的本机 Skill 清单。
- Skill 用于意图匹配，SOP 用于具体流程，Prompt 用于非强制模板。
- `workspace.py check` 检查可提交架构，`workspace.py doctor` 检查本地任务和项目交接状态。
- V2 远端只保存 workspace 架构；本地工作区由 Git 边界与 `AGENTS.md` 约束。

完整政策直接阅读 [AGENTS.md](AGENTS.md)。

<details>
<summary><strong>English</strong></summary>

## Overview

Agent Workspace V2 is an isolated Codex workspace scaffold. It separates control
configuration, reusable capabilities, runtime state, durable storage, and
machine-local private data. Current tasks and projects live under `projects/`.

## Quick Start

```powershell
python -B capabilities/tools/workspace.py check
python -B capabilities/tools/workspace.py update-local-skills
python -B capabilities/tools/workspace.py status
python -B capabilities/tools/workspace.py doctor
python -B capabilities/tools/workspace.py new my-task --dry-run
python -B capabilities/tools/workspace.py project new my-project --dry-run
```

`.workspace/config.json` resolves current tasks through `paths.projects`. V2
does not configure, resolve, or maintain historical task directories outside
this workspace.

## Document Entry Points

- [AGENTS.md](AGENTS.md) is the only permanent policy source.
- [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) explains architecture and maintenance
  entry points without defining policy.
- [WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) is remote architecture inventory
  generated only from Git-tracked content, not policy.
- `.workspace/registry/skills.remote.json` is the authoritative remote Skill
  catalog; `runtime/skills.local.json` is the ignored machine-local catalog.
- Skills match intent, SOPs describe procedures, and prompts are optional templates.
- `workspace.py check` validates publishable architecture; `workspace.py doctor`
  reports local task and project handoff health.
- The V2 remote stores workspace architecture only; Git boundaries and
  `AGENTS.md` govern local content.

</details>
