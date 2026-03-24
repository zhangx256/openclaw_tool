import json
import re


def extract_json_object(text: str) -> dict | None:
    start = text.find("{")
    if start < 0:
        return None
    end = text.rfind("}")
    if end <= start:
        return None

    cur_end = end
    while cur_end > start:
        candidate = text[start : cur_end + 1]
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        cur_end = text.rfind("}", start, cur_end)
        if cur_end < 0:
            break
    return None


def extract_json_value(text: str) -> object | None:
    start_obj = text.find("{")
    start_arr = text.find("[")
    if start_obj < 0 and start_arr < 0:
        return None
    if start_obj < 0:
        start = start_arr
    elif start_arr < 0:
        start = start_obj
    else:
        start = min(start_obj, start_arr)
    stack: list[str] = []
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            stack.append("}")
            continue
        if ch == "[":
            stack.append("]")
            continue
        if stack and ch == stack[-1]:
            stack.pop()
            if not stack:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def extract_plugins_list_json(text: str) -> dict | None:
    def _try_parse_at(start: int) -> tuple[object, int] | None:
        stack: list[str] = []
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                stack.append("}")
                continue
            if ch == "[":
                stack.append("]")
                continue
            if stack and ch == stack[-1]:
                stack.pop()
                if not stack:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate), i
                    except Exception:
                        return None
        return None

    def _plugins_list_from_obj(obj: object) -> tuple[list[object], bool] | None:
        if isinstance(obj, dict):
            plugins = obj.get("plugins")
            if isinstance(plugins, list):
                return plugins, True
            return None
        if isinstance(obj, list):
            return obj, False
        return None

    def _score_plugins_list(plugins: list[object], has_plugins_key: bool) -> tuple[int, int, int, int]:
        plugin_like = 0
        id_count = 0
        for item in plugins:
            if not isinstance(item, dict):
                continue
            keys = item.keys()
            if ("id" in keys) or ("name" in keys) or ("version" in keys) or ("origin" in keys) or ("status" in keys):
                plugin_like += 1
            pid = item.get("id")
            if isinstance(pid, str) and pid:
                id_count += 1
        return (1 if has_plugins_key else 0, id_count, plugin_like, len(plugins))

    best_obj: object | None = None
    best_score: tuple[int, int, int, int] | None = None

    i = 0
    while i < len(text):
        ch = text[i]
        if ch not in "{[":
            i += 1
            continue
        parsed = _try_parse_at(i)
        if parsed is None:
            i += 1
            continue
        obj, end_i = parsed

        plugins_info = _plugins_list_from_obj(obj)
        if plugins_info is not None:
            plugins_list, has_plugins_key = plugins_info
            score = _score_plugins_list(plugins_list, has_plugins_key)
            if score[2] > 0:
                if best_score is None or score > best_score:
                    best_score = score
                    best_obj = obj

        i = end_i + 1

    if best_obj is not None:
        if isinstance(best_obj, dict) and isinstance(best_obj.get("plugins"), list):
            return best_obj
        if isinstance(best_obj, list):
            return {"plugins": best_obj}

    m = re.search(r'"plugins"\s*:\s*\[', text)
    if m:
        start = text.find("[", m.start())
        if start >= 0:
            parsed = _try_parse_at(start)
            if parsed is not None:
                arr, _ = parsed
                if isinstance(arr, list):
                    score = _score_plugins_list(arr, True)
                    if score[2] > 0:
                        return {"plugins": arr}
    return None
