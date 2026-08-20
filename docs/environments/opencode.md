# OpenCode

把这份说明当作 `AGENT_WORKSPACE_V2` 里的 OpenCode 快速参考。

## 当前本机状态

- OpenCode CLI 1.18.13 已通过 npm 安装。
- V2 专用启动器是 `capabilities/tools/opencode-v2.ps1`。
- 启动器默认以 V2 根目录为项目目录，也可用 `-Project projects/<name>`
  进入具体项目。
- OpenCode 的机器私有配置位于 `.local/opencode/`；数据、缓存、状态、日志和
  临时文件位于 `runtime/opencode/`。这些目录不会进入工作区仓库。

直接运行全局 `opencode` 不会应用 V2 的路径隔离。日常使用应通过启动器。

## 推荐工作流

1. 在 V2 根目录调用启动器，或通过 `-Project` 选择 `projects/` 下的项目。
2. 让 OpenCode 先读取根 `AGENTS.md` 和项目内适用的规则、README 与任务说明。
3. 默认只允许它修改当前项目目录，除非你明确要更新 V2 共享资产。
4. 不向 OpenCode 提供工作区外的历史任务路径；需要迁移的内容由人工单独处理。
5. 每次关键修改后运行最小验证命令。

## 常用命令

```powershell
# 从 V2 根目录启动
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1

# 从 V2 内的具体项目启动
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1 `
  -Project projects/my-project

# 非交互运行、Provider 管理和路径核查
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1 `
  run "read the applicable AGENTS.md files, then propose a plan"
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1 providers list
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1 debug paths
powershell -NoProfile -File capabilities/tools/opencode-v2.ps1 --version
```

## Provider 设置

通过 V2 启动器运行 Provider 管理命令，确保 OpenCode 的机器私有配置留在
`.local/opencode/`。不要把真实密钥写入受版本控制的文件、命令记录或文档。

如需用环境变量提供临时凭据，只在当前终端中设置，并继续通过 V2 启动器运行
OpenCode。长期机器私有材料应遵守根 `AGENTS.md` 对 `.local/` 的限制。

## 建议输出格式

建议要求 OpenCode 最后汇报：

- changed files
- commands run
- verification result
