## openclaw_tool

openclaw配置工具，目前支持自定义模型的添加、测试与配置以及国内常见即时通讯软件机器人（企业微信、微信、飞书、钉钉、QQ）的对接，涉及的相关参数需要自己手动获取。

### 声明

- 本项目代码由 AI 工具辅助生成与整理。
- 本项目为第三方工具，与 OpenClaw 官方无隶属关系；OpenClaw 及其商标归原权利人所有。
- 如你认为本仓库内容侵犯了你的权利，请在本仓库提交 Issue 联系，我会尽快核实并处理（删除/替换/补充署名等）。

### 文档

- 终端用户（exe）：`USER_GUIDE.md`
- 开发者（源码/打包）：`DEVELOPER.md`
- 开源协议：`LICENSE`

### 目录结构

- `ui/`：Qt 界面、事件绑定、线程与信号
- `app/`：业务编排（插件检查/安装、命令 plan 生成、模型测试）
- `infra/`：与系统交互（调用 openclaw、PowerShell、创建 gateway vbs）
- `core/`：纯工具函数（PowerShell 字符串处理、JSON 容错提取、插件列表健壮解析）
- `qt_import.py`：Qt 绑定动态导入（PyQt5 / PySide6）

入口脚本：`openclaw_tool/run_openclaw_config_tool.py`

### 快速开始

- 终端用户使用 exe：看 `USER_GUIDE.md`
- 从源码运行 / 打包发布：看 `DEVELOPER.md`

### 界面截图

![OpenClaw 配置工具主界面](images/ui-main.png)

将运行界面截图保存为 `split_workspace/openclaw_tool/images/ui-main.png`，GitHub/本地查看 README 即可展示。

### 安全与行为边界（开源说明建议）

- 工具不会主动上传用户的 `api_key`，日志会对 `api_key` 做掩码显示。
- 工具会在当前用户目录创建 `%USERPROFILE%\HOpenclaw-gateway.vbs`，用于无窗口重启 OpenClaw gateway。
- 工具的核心行为是调用 `openclaw` 命令行修改本机配置、安装插件、重启 gateway。

### 可能执行的命令（便于审计）

- 插件检测：
  - `openclaw plugins list --json`
- 插件检测输出兼容：
  - `openclaw plugins list --json` 的 stdout/stderr 可能混入告警/日志；工具会从混杂输出中稳健提取 plugins 列表，并仅基于 plugins 列表元素的 id 判定是否安装
- 插件安装（按渠道）：
  - `openclaw plugins install @tencent-connect/openclaw-qqbot@latest`
  - `openclaw plugins install @dingtalk-real-ai/dingtalk-connector`
  - `openclaw plugins install @wecom/wecom-openclaw-plugin`
- 自定义模型：
  - `openclaw config get models.mode`
  - `openclaw config set models.mode "merge"`（当 models.mode 不存在时）
  - `openclaw config set models.providers.<provider> <provider_obj>`
  - `openclaw config set "agents.defaults.models.<provider>/<model_id>" "{}"`
- 渠道配置（示例，实际按按钮触发）：
  - `openclaw config set ...` / `openclaw config unset ...`
  - `openclaw channels add ...` / `openclaw channels remove ...`
- 重启 gateway：
  - 通过执行 `%USERPROFILE%\HOpenclaw-gateway.vbs`
