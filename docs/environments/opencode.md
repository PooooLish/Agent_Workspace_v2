# OpenCode

把这份说明当作共享 `agent_workspace` 里的 OpenCode 快速参考。

## 当前本机状态

- OpenCode CLI 已安装，可直接使用 `opencode`
- 已验证命令：`opencode --version`
- 推荐启动位置：`tasks/<task_name>/` 下的具体任务目录

## 推荐工作流

1. 先创建或进入一个任务目录。
2. 在该任务目录中启动 OpenCode。
3. 让它先读取根目录 `AGENTS.md`、当前任务 `AGENTS.md`、当前任务 `task.md`。
4. 默认只允许它修改当前 task 目录，除非你明确要更新共享资产。
5. 每次关键修改后运行最小验证命令。

## 常用命令

```powershell
opencode .
opencode run "read AGENTS.md and task.md, then propose a plan"
opencode web .
opencode providers list
opencode --help
```

## Provider 设置

优先使用环境变量，不要把真实密钥写入仓库。

当前终端临时设置示例：

```powershell
$env:OPENAI_API_KEY="your_key_here"
opencode .
```

参考模板：

- `secrets/env.example`

不要提交真实密钥。如果你需要更长期的本地凭据，请放在仓库外部。

## 建议输出格式

建议要求 OpenCode 最后汇报：

- changed files
- commands run
- verification result
