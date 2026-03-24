from ..qt_import import import_qt
from ..infra.process import powershell_run
from ..app.plugin_manager import ensure_channel_plugin
from ..app.model_test import test_openai_compatible
from ..app.plans import CommandPlan
import subprocess
import os
import re

QtCore, _, _ = import_qt()

_OPENCLAW_NOISE_LINE_RE = re.compile(r"^\s*\d{2}:\d{2}:\d{2}\s+\[plugins\]\s+")

def _is_qr_line(s: str) -> bool:
    return ("█" in s) or ("▄" in s) or ("▀" in s)

def _is_openclaw_noise_line(s: str) -> bool:
    t = s.strip()
    if not t:
        return False
    if t.startswith("🦞 OpenClaw"):
        return True
    if t.startswith("[plugins]"):
        return True
    if "plugins.allow is empty" in t:
        return True
    return _OPENCLAW_NOISE_LINE_RE.match(t) is not None

def _is_openclaw_not_found_line(s: str) -> bool:
    t = s.strip().lower()
    if not t:
        return False
    if "is not recognized as an internal or external command" in t:
        return True
    if "不是内部或外部命令" in t:
        return True
    if "无法将" in t and "openclaw" in t and "识别" in t:
        return True
    return False

def _decode_console_line(raw: bytes) -> str:
    if not raw:
        return ""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")

class Runner(QtCore.QThread):
    finished_run = QtCore.pyqtSignal(int) if hasattr(QtCore, "pyqtSignal") else QtCore.Signal(int)
    log_line = QtCore.pyqtSignal(str) if hasattr(QtCore, "pyqtSignal") else QtCore.Signal(str)

    def __init__(self, plan: CommandPlan, channel_title: str, action: str):
        super().__init__()
        self._plan = plan
        self._channel_title = channel_title
        self._action = action

    def run(self):
        if self._action == "添加":
            ok, hint = ensure_channel_plugin(self._channel_title, self.log_line.emit)
            if not ok:
                if hint:
                    self.log_line.emit("插件未安装或安装失败，请手动执行：")
                    self.log_line.emit(hint)
                self.finished_run.emit(2)
                return
        if self._channel_title == "微信" and self._action == "添加":
            code = powershell_run(self._plan.script)
            if code != 0:
                self.finished_run.emit(code)
                return
            self.log_line.emit("微信登录")
            creationflags = 0
            startupinfo = None
            if os.name == "nt":
                creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            openclaw_args = ["openclaw", "channels", "login", "--channel", "openclaw-weixin"]
            cmdline = subprocess.list2cmdline(openclaw_args)
            p = subprocess.Popen(
                ["cmd.exe", "/c", cmdline],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd(),
                env=os.environ.copy(),
                creationflags=creationflags,
                startupinfo=startupinfo,
            )
            if p.stdout is not None:
                emit_mode = False
                qr_mode = False
                for raw in iter(p.stdout.readline, b""):
                    if not raw:
                        break
                    s = _decode_console_line(raw).rstrip("\r\n")
                    if _is_openclaw_not_found_line(s):
                        emit_mode = True
                        qr_mode = False
                        self.log_line.emit("微信登录失败：找不到 openclaw 命令，请确认已安装并在 PATH 中")
                        self.log_line.emit(s)
                        continue
                    if _is_openclaw_noise_line(s):
                        continue
                    if "正在启动微信扫码登录" in s:
                        emit_mode = True
                        self.log_line.emit(s)
                        continue
                    if "使用微信扫描以下二维码" in s:
                        emit_mode = True
                        qr_mode = True
                        self.log_line.emit(s)
                        continue
                    if "等待连接结果" in s:
                        emit_mode = True
                        qr_mode = False
                        self.log_line.emit(s)
                        continue
                    if qr_mode:
                        if _is_qr_line(s) or not s.strip():
                            self.log_line.emit(s)
                        continue
                    if emit_mode:
                        self.log_line.emit(s)
                try:
                    p.stdout.close()
                except Exception:
                    pass
            self.finished_run.emit(p.wait())
            return
        code = powershell_run(self._plan.script)
        self.finished_run.emit(code)


class ModelTestRunner(QtCore.QThread):
    finished_test = QtCore.pyqtSignal(int) if hasattr(QtCore, "pyqtSignal") else QtCore.Signal(int)
    log_line = QtCore.pyqtSignal(str) if hasattr(QtCore, "pyqtSignal") else QtCore.Signal(str)

    def __init__(self, model_id: str, base_url: str, api_key: str):
        super().__init__()
        self._model_id = model_id
        self._base_url = base_url
        self._api_key = api_key

    def run(self):
        code = test_openai_compatible(
            model_id=self._model_id,
            base_url=self._base_url,
            api_key=self._api_key,
            log=self.log_line.emit,
        )
        self.finished_test.emit(code)
