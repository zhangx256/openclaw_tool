import os
from pathlib import Path

_USER_HOME = os.environ.get("USERPROFILE") or str(Path.home())
GATEWAY_VBS_PATH = os.path.join(_USER_HOME, "HOpenclaw-gateway.vbs")
GATEWAY_VBS_CONTENT = 'CreateObject("WScript.Shell").Run "cmd /c C:\\Users\\%USERNAME%\\.openclaw\\gateway.cmd",0\r\n'


def ensure_gateway_vbs_exists() -> str:
    try:
        if not os.path.isfile(GATEWAY_VBS_PATH):
            with open(GATEWAY_VBS_PATH, "w", encoding="utf-8", newline="") as f:
                f.write(GATEWAY_VBS_CONTENT)
    except Exception:
        pass
    return GATEWAY_VBS_PATH

