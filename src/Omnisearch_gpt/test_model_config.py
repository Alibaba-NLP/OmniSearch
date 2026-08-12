import sys
import unittest
from unittest.mock import Mock, patch

sys.modules.setdefault("requests", Mock())

from llm_config import call_gpt
from model_config import (
    MINIMAX_DEFAULT_MODEL,
    MINIMAX_DEFAULT_REGION,
    MINIMAX_MODELS,
    MINIMAX_REGIONAL_ENDPOINTS,
)


class MiniMaxModelConfigTest(unittest.TestCase):
    def test_supported_model_ids(self):
        self.assertEqual(MINIMAX_DEFAULT_MODEL, "MiniMax-M3")
        self.assertEqual(
            list(MINIMAX_MODELS),
            ["MiniMax-M3", "MiniMax-M2.7"],
        )

    def test_model_metadata(self):
        self.assertEqual(MINIMAX_MODELS["MiniMax-M3"]["context_window"], 1_000_000)
        self.assertEqual(
            MINIMAX_MODELS["MiniMax-M2.7"]["context_window"],
            204_800,
        )
        self.assertEqual(
            MINIMAX_MODELS["MiniMax-M3"]["input_modalities"],
            ("text", "image", "video"),
        )
        self.assertEqual(
            MINIMAX_MODELS["MiniMax-M2.7"]["thinking"],
            ("always_on",),
        )

    def test_regional_endpoints(self):
        self.assertEqual(MINIMAX_DEFAULT_REGION, "global_en")
        self.assertEqual(
            MINIMAX_REGIONAL_ENDPOINTS["global_en"]["openai_base_url"],
            "https://api.minimax.io/v1",
        )
        self.assertEqual(
            MINIMAX_REGIONAL_ENDPOINTS["cn_zh"]["anthropic_base_url"],
            "https://api.minimaxi.com/anthropic",
        )

    @patch("llm_config.requests.post")
    def test_chat_completions_uses_configured_base_url(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "ok"},
                }
            ]
        }
        post.return_value = response

        success, _, _, answer = call_gpt(
            "MiniMax-M3",
            [{"role": "user", "content": "hello"}],
            "question-1",
            {"Authorization": "Bearer test"},
            MINIMAX_REGIONAL_ENDPOINTS["cn_zh"]["openai_base_url"],
        )

        self.assertTrue(success)
        self.assertEqual(answer, "ok")
        self.assertEqual(
            post.call_args.args[0],
            "https://api.minimaxi.com/v1/chat/completions",
        )


if __name__ == "__main__":
    unittest.main()
