MINIMAX_DEFAULT_MODEL = "MiniMax-M3.1-Flash"
MINIMAX_DEFAULT_REGION = "global_en"

# Current catalog: https://platform.minimax.io/docs/guides/models-intro
# Pricing: https://platform.minimax.io/docs/pricing/overview#models/text
MINIMAX_MODELS = {
    "MiniMax-M3.1-Flash": {
        "context_window": 1_000_000,
        "max_output_tokens": 524_288,
        "pricing_usd_per_million_tokens": {
            "input": 0.15,
            "output": 0.60,
            "cache_read": 0.015,
            "cache_write": None,
        },
        "input_modalities": ("text", "image", "video"),
        "thinking": ("adaptive",),
        "reasoning_effort": ("low", "medium", "high", "xhigh", "max"),
        "default_reasoning_effort": "max",
    },
    "MiniMax-M3": {
        "context_window": 1_000_000,
        # Standard pricing for up to 512k input tokens.
        "pricing_usd_per_million_tokens": {
            "input": 0.3,
            "output": 1.2,
            "cache_read": 0.06,
            "cache_write": None,
        },
        "pricing_usd_per_million_tokens_above_512k": {
            "input": 0.6,
            "output": 2.4,
            "cache_read": 0.12,
            "cache_write": None,
        },
        "priority_price_multiplier": 1.5,
        "input_modalities": ("text", "image", "video"),
        "thinking": ("adaptive", "disabled"),
    },
}

MINIMAX_REGIONAL_ENDPOINTS = {
    "global_en": {
        "openai_base_url": "https://api.minimax.io/v1",
        "anthropic_base_url": "https://api.minimax.io/anthropic",
        "docs_root": "https://platform.minimax.io/docs",
    },
    "cn_zh": {
        "openai_base_url": "https://api.minimaxi.com/v1",
        "anthropic_base_url": "https://api.minimaxi.com/anthropic",
        "docs_root": "https://platform.minimaxi.com/docs",
    },
}
