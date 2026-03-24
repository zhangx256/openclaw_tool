import json
import urllib.error
import urllib.request
from typing import Callable


def models_url(base_url: str) -> str:
    u = (base_url or "").strip().rstrip("/")
    ul = u.lower()
    if ul.endswith("/v1/models") or ul.endswith("/models"):
        return u
    if ul.endswith("/v1"):
        return f"{u}/models"
    return f"{u}/v1/models"


def test_openai_compatible(
    model_id: str,
    base_url: str,
    api_key: str,
    log: Callable[[str], None] | None = None,
) -> int:
    def _log(msg: str):
        if log is not None:
            log(msg)

    try:
        url = models_url(base_url)
        _log("模型检测")
        _log(f"模型检测中：GET {url}")

        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            status = getattr(resp, "status", None) or 200
            raw = resp.read().decode("utf-8", errors="replace")

        if status < 200 or status >= 300:
            _log(f"模型检测结果：失败（HTTP {status}）")
            return 1

        try:
            data = json.loads(raw)
        except Exception:
            _log("模型检测结果：失败（返回非JSON）")
            return 1

        models = None
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                models = data.get("data")
            elif isinstance(data.get("models"), list):
                models = data.get("models")

        if isinstance(models, list):
            ids: list[str] = []
            for item in models:
                if isinstance(item, dict):
                    mid = item.get("id")
                    if isinstance(mid, str):
                        ids.append(mid)
            if model_id in ids:
                _log("模型检测结果：成功")
                return 0
            _log("模型检测结果：失败（model_id未在/models返回列表中）")
            return 1

        _log("模型检测结果：成功（未返回可解析的模型列表）")
        return 0
    except urllib.error.HTTPError as e:
        _log(f"模型检测结果：失败（HTTP {e.code}）")
        return 1
    except Exception:
        _log("模型检测结果：失败（请求异常）")
        return 1

