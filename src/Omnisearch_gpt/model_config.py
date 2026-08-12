MINIMAX_MODELS = {
    "MiniMax-M3": {
        "context_window": 1_000_000,
        "pricing_usd_per_million_tokens": {
            "input": 0.6,
            "output": 2.4,
            "cache_read": 0.12,
            "cache_write": None,
        },
        "input_modalities": ("text", "image", "video"),
        "thinking": ("adaptive", "disabled"),
    },
    "MiniMax-M2.7": {
        "context_window": 204_800,
        "pricing_usd_per_million_tokens": {
            "input": 0.3,
            "output": 1.2,
            "cache_read": 0.06,
            "cache_write": 0.375,
        },
        "input_modalities": ("text",),
        "thinking": ("always_on",),
    },
}
