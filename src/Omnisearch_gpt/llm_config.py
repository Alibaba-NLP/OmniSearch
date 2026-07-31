import os
import time

import requests

workers=4
skip_lines = 0

LIMIT = 1000000000000
retry_attempt = 10


# Provider registry. Each provider exposes the OpenAI-compatible chat completions
# endpoint(s) it can be served from. The endpoints are keyed by region so that a
# global and a China-region base URL can coexist for the same provider.
#
# Add a new provider by extending this table with its OpenAI-compatible base URLs
# per region; call_gpt picks the configured region automatically.
PROVIDERS = {
    "openai": {
        "endpoints": {
            "global_en": "https://api.openai.com/v1",
        },
        "default_region": "global_en",
    },
    "minimax": {
        "endpoints": {
            "global_en": "https://api.minimax.io/v1",
            "cn_zh": "https://api.minimaxi.com/v1",
        },
        "default_region": "global_en",
    },
}


def _resolve_region(provider):
    # Allow a deployment to switch regions (e.g. to the China endpoint) without
    # editing source. Defaults to each provider's default_region when unset.
    region = os.environ.get("MINIMAX_REGION") or os.environ.get("LLM_REGION")
    if region:
        return region
    return PROVIDERS[provider]["default_region"]


def _resolve_base_url(provider):
    region = _resolve_region(provider)
    endpoints = PROVIDERS[provider]["endpoints"]
    if region not in endpoints:
        raise ValueError(
            f"Region '{region}' is not configured for provider '{provider}'. "
            f"Available regions: {list(endpoints)}"
        )
    return endpoints[region], region


def provider_for_model(model):
    # Route models whose id starts with the MiniMax provider prefix to that
    # provider; anything else falls back to the OpenAI-compatible default so
    # existing callers keep working unchanged.
    if isinstance(model, str) and model.lower().startswith("minimax"):
        return "minimax"
    return "openai"


def call_gpt(model, messages, idx, headers ):
    # 准备请求数据，包括模型、对话信息等参数
    data = {
        "model": model,
        "messages": messages,
        "n": 1,  # 回答数量
        "max_tokens": 4096
    }

    # Resolve the provider and its regional chat completions endpoint from the
    # registry instead of hard-coding a single endpoint.
    provider = provider_for_model(model)
    base_url, region = _resolve_base_url(provider)
    url = f"{base_url}/chat/completions"

    answer = None
    while answer is None:
        try:

            r = requests.post(
                url,
                json=data,
                headers=headers
            )
            resp = r.json()

            if r.status_code != 200:
                print('请求失败，重试中！')
                print(resp)
                continue

            if 'choices' in resp and resp['choices'][0].get('finish_reason') in ['content_filter', 'ResponsibleAIPolicyViolation']:
                print('内容不符合策略要求，返回空结果')
                return (False, idx, "", "", 0, 0, 0)
            message = resp['choices'][0]['message']
            answer = message['content']

            return (True, idx, message, answer)

        except Exception as e:
            print(e)
            print('发生异常，重试中！')
            time.sleep(1)  # 等待一段时间再重试
            continue
