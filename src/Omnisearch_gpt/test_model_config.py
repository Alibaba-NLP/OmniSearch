import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

import requests

from agent import QAAgent
from model_config import (
    MINIMAX_DEFAULT_MODEL,
    MINIMAX_DEFAULT_REGION,
    MINIMAX_MODELS,
    MINIMAX_REGIONAL_ENDPOINTS,
)


class MiniMaxModelConfigTest(unittest.TestCase):
    def test_supported_model_ids(self):
        self.assertEqual(MINIMAX_DEFAULT_MODEL, "MiniMax-M3.1-Flash")
        self.assertEqual(
            list(MINIMAX_MODELS),
            ["MiniMax-M3.1-Flash", "MiniMax-M3"],
        )

    def test_model_metadata(self):
        flash = MINIMAX_MODELS[MINIMAX_DEFAULT_MODEL]
        self.assertEqual(flash["context_window"], 1_000_000)
        self.assertEqual(flash["max_output_tokens"], 524_288)
        self.assertEqual(flash["thinking"], ("adaptive",))
        self.assertEqual(
            flash["reasoning_effort"], ("low", "medium", "high", "xhigh", "max")
        )
        self.assertEqual(flash["default_reasoning_effort"], "max")
        self.assertEqual(
            flash["pricing_usd_per_million_tokens"],
            {"input": 0.15, "output": 0.60, "cache_read": 0.015, "cache_write": None},
        )
        m3 = MINIMAX_MODELS["MiniMax-M3"]
        self.assertEqual(m3["thinking"], ("adaptive", "disabled"))
        self.assertEqual(m3["pricing_usd_per_million_tokens"]["input"], 0.3)
        self.assertEqual(m3["pricing_usd_per_million_tokens_above_512k"]["input"], 0.6)
        self.assertEqual(m3["priority_price_multiplier"], 1.5)
        for config in MINIMAX_MODELS.values():
            self.assertEqual(config["input_modalities"], ("text", "image", "video"))

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

    @staticmethod
    def response():
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({
            "choices": [{
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "Final Answer: ok",
                    "reasoning_content": "Preserved reasoning.",
                },
            }],
        }).encode()
        return response

    def test_cli_defaults_explicit_models_regions_and_saved_results(self):
        # Exercise CLI -> main -> ConversationManager -> QAAgent -> Requests.
        source = Path(__file__).resolve().parent
        models = (None, "MiniMax-M3", "MiniMax-M2.7", "custom-model")
        for region, host in (("global_en", "api.minimax.io"), ("cn_zh", "api.minimaxi.com")):
            for selected in models:
                with self.subTest(region=region, model=selected):
                    with tempfile.TemporaryDirectory(dir=source) as directory:
                        root = Path(directory)
                        dataset = root / "questions.jsonl"
                        item = {
                            "question": "What is shown?",
                            "question_id": "question-1",
                            "image_url": "https://example.invalid/image.png",
                        }
                        dataset.write_text(json.dumps(item) + "\n", encoding="utf-8")
                        argv = [
                            str(source / "main.py"),
                            "--test_dataset", str(dataset),
                            "--dataset_name", "fixture",
                            "--meta_save_path", str(root),
                        ]
                        if region != "global_en":
                            argv += ["--region", region]
                        if selected is not None:
                            argv += ["--model", selected]
                        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                            with patch("requests.adapters.HTTPAdapter.send", return_value=self.response()) as send:
                                runpy.run_path(str(source / "main.py"), run_name="__main__")
                                self.assertEqual(send.call_count, 1)
                                request = send.call_args.args[0]
                                payload = json.loads(request.body)
                                self.assertEqual(request.url, f"https://{host}/v1/chat/completions")
                                self.assertEqual(payload["model"], selected or "MiniMax-M3.1-Flash")
                                self.assertEqual(payload["max_tokens"], 4096)
                                self.assertEqual(set(payload), {"model", "messages", "n", "max_tokens"})
                                content = payload["messages"][0]["content"]
                                self.assertEqual(content[0]["type"], "text")
                                self.assertEqual(content[1], {
                                    "type": "image_url",
                                    "image_url": {"url": item["image_url"], "detail": "high"},
                                })
                                output = root / "fixture" / "output_from_gpt4v.jsonl"
                                saved = json.loads(output.read_text(encoding="utf-8"))
                                self.assertEqual(saved, dict(item, prediction="ok"))
                                # Resuming a saved result must not resubmit or overwrite it.
                                runpy.run_path(str(source / "main.py"), run_name="__main__")
                                self.assertEqual(send.call_count, 1)
                                self.assertEqual(json.loads(output.read_text(encoding="utf-8")), saved)

    def test_agent_preserves_custom_endpoint_multimodal_and_reasoning_history(self):
        messages = [{"role": "user", "content": [
            {"type": "text", "text": "Describe this."},
            {"type": "image_url", "image_url": {"url": "https://example.invalid/image.png"}},
            {"type": "video_url", "video_url": {"url": "mm_file://fixture"}},
        ]}]
        agent = QAAgent("custom-model", {"Authorization": "Bearer test"}, "https://example.invalid/v1/")
        with patch("requests.adapters.HTTPAdapter.send", return_value=self.response()) as send:
            success, idx, message, answer = agent.ask_gpt(messages, "question-1")
            self.assertTrue(success)
            self.assertEqual(idx, "question-1")
            self.assertEqual(answer, "Final Answer: ok")
            request = send.call_args.args[0]
            self.assertEqual(request.url, "https://example.invalid/v1/chat/completions")
            self.assertEqual(json.loads(request.body)["messages"], messages)
            messages.append(message)
            agent.ask_gpt(messages, "question-2")
            payload = json.loads(send.call_args.args[0].body)
            self.assertEqual(payload["model"], "custom-model")
            self.assertEqual(payload["messages"][-1]["reasoning_content"], "Preserved reasoning.")

    def test_cli_help_lists_only_current_catalog(self):
        source = Path(__file__).resolve().parent
        output = io.StringIO()
        with patch.object(sys, "argv", ["main.py", "--help"]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(source / "main.py"), run_name="__main__")
        self.assertEqual(result.exception.code, 0)
        help_text = " ".join(output.getvalue().split())
        self.assertIn("MiniMax-M3.1-Flash, MiniMax-M3", help_text)
        self.assertNotIn("MiniMax-M2.7", help_text)


if __name__ == "__main__":
    unittest.main()
