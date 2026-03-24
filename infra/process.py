import os
import subprocess


def run_cmd_capture(args: list[str]) -> tuple[int, str, str]:
    cmdline = subprocess.list2cmdline(args)
    cmd = ["cmd.exe", "/c", cmdline]

    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    r = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=os.getcwd(),
        env=os.environ.copy(),
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    return r.returncode, r.stdout, r.stderr


def powershell_run(script: str) -> int:
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "-",
    ]

    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    r = subprocess.run(
        cmd,
        input=script,
        text=True,
        capture_output=True,
        cwd=os.getcwd(),
        env=os.environ.copy(),
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    return r.returncode
