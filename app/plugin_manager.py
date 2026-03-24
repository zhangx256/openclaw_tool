import subprocess
from typing import Callable

from ..infra.openclaw_cli import installed_plugin_ids_with_status, plugins_install


def _log_line(log: Callable[[str], None] | None, msg: str):
    if log is not None:
        log(msg)


def ensure_channel_plugin(channel_title: str, log: Callable[[str], None] | None = None) -> tuple[bool, str | None]:
    required = {
        "QQ": ("openclaw-qqbot", ["openclaw", "plugins", "install", "@tencent-connect/openclaw-qqbot@latest"]),
        "钉钉": ("dingtalk-connector", ["openclaw", "plugins", "install", "@dingtalk-real-ai/dingtalk-connector"]),
        "企业微信": ("wecom-openclaw-plugin", ["openclaw", "plugins", "install", "@wecom/wecom-openclaw-plugin"]),
        "微信": ("openclaw-weixin", ["openclaw", "plugins", "install", "@tencent-weixin/openclaw-weixin"]),
    }.get(channel_title)

    if not required:
        return True, None

    plugin_id, install_cmd = required
    _log_line(log, "插件检测")
    _log_line(log, f"插件检测中：{channel_title} ({plugin_id})")
    ids, ok = installed_plugin_ids_with_status()
    if ok:
        _log_line(log, f"插件检测结果：{'已安装' if plugin_id in ids else '未安装'}")
    else:
        _log_line(log, "插件检测结果：无法解析，尝试安装")

    if plugin_id in ids:
        return True, None

    _log_line(log, "插件安装")
    _log_line(log, f"插件{channel_title}安装中")
    install_cmdline = subprocess.list2cmdline(install_cmd)
    _log_line(log, f"插件{channel_title}安装命令：{install_cmdline}")

    install_code, _, _ = plugins_install(install_cmd)
    ids2, ok2 = installed_plugin_ids_with_status()
    if ok2 and plugin_id in ids2:
        _log_line(log, f"插件{channel_title}安装结果：成功")
        return True, None

    _log_line(log, f"插件{channel_title}安装结果：失败（退出码: {install_code}）")
    return False, install_cmdline
