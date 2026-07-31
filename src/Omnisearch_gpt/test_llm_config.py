import llm_config


def test_provider_for_model_routes_minimax():
    for model_id in ["MiniMax-M3", "MiniMax-M2.7", "minimax-m3"]:
        assert llm_config.provider_for_model(model_id) == "minimax", model_id


def test_provider_for_model_defaults_to_openai():
    assert llm_config.provider_for_model("gpt-4o") == "openai"
    assert llm_config.provider_for_model(None) == "openai"


def test_minimax_global_endpoint_default_region():
    base_url, region = llm_config._resolve_base_url("minimax")
    assert region == "global_en"
    assert base_url == "https://api.minimax.io/v1"


def test_minimax_china_endpoint_via_env(monkeypatch):
    monkeypatch.setenv("MINIMAX_REGION", "cn_zh")
    base_url, region = llm_config._resolve_base_url("minimax")
    assert region == "cn_zh"
    assert base_url == "https://api.minimaxi.com/v1"


def test_minimax_unknown_region_raises(monkeypatch):
    monkeypatch.setenv("MINIMAX_REGION", "mars")
    try:
        llm_config._resolve_base_url("minimax")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown region")


def test_openai_endpoint_default_region():
    base_url, region = llm_config._resolve_base_url("openai")
    assert region == "global_en"
    assert base_url == "https://api.openai.com/v1"
