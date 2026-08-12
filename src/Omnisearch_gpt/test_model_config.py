import unittest

from model_config import MINIMAX_MODELS


class MiniMaxModelConfigTest(unittest.TestCase):
    def test_supported_model_ids(self):
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


if __name__ == "__main__":
    unittest.main()
