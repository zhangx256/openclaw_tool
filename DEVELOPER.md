## 开发者说明（源码构建与发布）

本文档面向需要从源码运行/打包/二次开发的开发者。终端用户请优先使用 GitHub Release 中的 exe。

### 运行环境

- Windows 10/11
- Python 3.10.18（建议与打包环境保持一致）
- OpenClaw 已安装并可在命令行直接运行 `openclaw`

可选：

- PowerShell（工具内部会通过 PowerShell 执行部分命令）

### 从源码运行

在包含 `openclaw_tool` 目录的路径下执行：

```powershell
python .\openclaw_tool\run_openclaw_config_tool.py
```

如果缺少 Qt 绑定，按你的偏好安装其一（示例）：

```powershell
pip install PyQt5
```


### 打包为 exe（PyInstaller）

示例（按需调整参数）：

```powershell
pip install pyinstaller
pyinstaller -F --noconsole --name openclaw_config_tool .\openclaw_tool\run_openclaw_config_tool.py
```

### 近期实现要点（便于二次开发）

- 插件检测基于 `openclaw plugins list --json`，该命令输出可能在 JSON 前后混入告警/日志；工具在 `core/json_extract.py` 中提供 plugins 列表的健壮提取逻辑，并在 `infra/openclaw_cli.py` 中仅基于 plugins 列表元素的 id 判定是否安装。

可选：使用 UPX 压缩 exe 体积

- 需要你额外安装 UPX，并将其路径传给 `--upx-dir`
- 示例：

```powershell
pyinstaller --upx-dir "D:\UPX" -F --noconsole --name openclaw_config_tool .\openclaw_tool\run_openclaw_config_tool.py
```

### 发布建议（GitHub Releases）

- 源码：推送到仓库
- 二进制：将打包生成的 exe 上传到 GitHub Release 的 Assets
- 建议在 Release 描述里写明：
  - OpenClaw 版本要求
  - Python 版本
  - PyInstaller 版本
  - 选用的 Qt 绑定（PyQt5 或 PySide6）
