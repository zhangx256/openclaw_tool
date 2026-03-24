from dataclasses import dataclass

from ..core.ps import ps_dq
from ..infra.gateway_vbs import ensure_gateway_vbs_exists


@dataclass(frozen=True)
class CommandPlan:
    title: str
    script: str


def _json5_escape_single_quoted(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def _json5_sq(s: str) -> str:
    return f"'{_json5_escape_single_quoted(s)}'"


def _openclaw_escape_config_path_segment(s: str) -> str:
    return s.replace("\\", "\\\\").replace(".", "\\.")


def build_add_plan(channel: str, app_id: str, app_secret: str) -> CommandPlan | None:
    gateway_vbs = ensure_gateway_vbs_exists()
    if channel == "飞书":
        script = "\n".join(
            [
                "openclaw config set channels.feishu.enabled true",
                f"openclaw config set channels.feishu.appId {ps_dq(app_id)}",
                f"openclaw config set channels.feishu.appSecret {ps_dq(app_secret)}",
                'openclaw config set channels.feishu.connectionMode "websocket"',
                'openclaw config set channels.feishu.domain "feishu"',
                'openclaw config set channels.feishu.groupPolicy "open"',
                "openclaw config set channels.feishu.dmPolicy open",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="飞书", script=script)

    if channel == "QQ":
        token = f"{app_id}:{app_secret}"
        script = "\n".join(
            [
                f"openclaw channels add --channel qqbot --token {ps_dq(token)}",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="QQ", script=script)

    if channel == "企业微信":
        script = "\n".join(
            [
                "openclaw config set channels.wecom.enabled true",
                f"openclaw config set channels.wecom.botId {ps_dq(app_id)}",
                f"openclaw config set channels.wecom.secret {ps_dq(app_secret)}",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="企业微信", script=script)

    if channel == "钉钉":
        script = "\n".join(
            [
                "openclaw config set channels.dingtalk-connector.enabled true",
                f"openclaw config set channels.dingtalk-connector.clientId {ps_dq(app_id)}",
                f"openclaw config set channels.dingtalk-connector.clientSecret {ps_dq(app_secret)}",
                r"openclaw config set channels.dingtalk-connector.gatewayToken (Get-Content -Raw -Path $env:USERPROFILE\.openclaw\openclaw.json | ConvertFrom-Json).gateway.auth.token",
                "openclaw config set gateway.http.endpoints.chatCompletions.enabled true",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="钉钉", script=script)

    if channel == "微信":
        script = "\n".join(
            [
                "openclaw config set plugins.entries.openclaw-weixin.enabled true",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="微信", script=script)

    return None


def build_delete_plan(channel: str) -> CommandPlan | None:
    gateway_vbs = ensure_gateway_vbs_exists()
    if channel == "飞书":
        script = "\n".join(
            [
                "openclaw channels remove --channel feishu --delete",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="飞书", script=script)

    if channel == "QQ":
        script = "\n".join(
            [
                "openclaw channels remove --channel qqbot --delete",
                f"& {ps_dq(gateway_vbs)}",
            ]
        )
        return CommandPlan(title="QQ", script=script)

    if channel == "企业微信":
        script = "openclaw channels remove --channel wecom --delete"
        return CommandPlan(title="企业微信", script=script)

    if channel == "钉钉":
        script = "openclaw config unset channels.dingtalk-connector"
        return CommandPlan(title="钉钉", script=script)

    return None


def build_custom_model_plan(provider_id: str, model_id: str, base_url: str, api_key: str) -> CommandPlan:
    gateway_vbs = ensure_gateway_vbs_exists()
    provider_obj = (
        "{"
        f"baseUrl:{_json5_sq(base_url)},"
        f"apiKey:{_json5_sq(api_key)},"
        f"api:{_json5_sq('openai-completions')},"
        "models:["
        "{"
        f"id:{_json5_sq(model_id)},"
        f"name:{_json5_sq(f'{model_id} (Custom Provider)')},"
        "reasoning:false,"
        "input:['text'],"
        "cost:{input:0,output:0,cacheRead:0,cacheWrite:0},"
        "contextWindow:16000,"
        "maxTokens:4096"
        "}"
        "]"
        "}"
    )
    provider_key = _openclaw_escape_config_path_segment(provider_id)
    agent_default_map_id = _openclaw_escape_config_path_segment(f"{provider_id}/{model_id}")
    agent_default_key = f"agents.defaults.models.{agent_default_map_id}"
    script = "\n".join(
        [
            "$modelsModeOut = (openclaw config get models.mode 2>&1 | Out-String)",
            'if ($modelsModeOut -match "Config path not found:\\s*models\\.mode") { openclaw config set models.mode "merge" }',
            f"openclaw config set models.providers.{provider_key} {ps_dq(provider_obj)}",
            f"openclaw config set {ps_dq(agent_default_key)} {ps_dq('{}')}",
            f"& {ps_dq(gateway_vbs)}",
        ]
    )
    return CommandPlan(title="自定义模型", script=script)
