from .process import run_cmd_capture
from ..core.json_extract import extract_plugins_list_json


def plugins_list_json() -> object | None:
    code, out, err = run_cmd_capture(["openclaw", "plugins", "list", "--json"])
    combined = (out or "") + "\n" + (err or "")
    if code != 0 and not combined.strip():
        return None
    return extract_plugins_list_json(combined)


def installed_plugin_ids_with_status() -> tuple[set[str], bool]:
    data = plugins_list_json()
    if not data:
        return set(), False
    plugins = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(plugins, list):
        return set(), False
    ids: set[str] = set()
    for item in plugins:
        if isinstance(item, dict):
            pid = item.get("id")
            if isinstance(pid, str) and pid:
                ids.add(pid)
    return ids, True


def plugins_install(args: list[str]) -> tuple[int, str, str]:
    return run_cmd_capture(args)
