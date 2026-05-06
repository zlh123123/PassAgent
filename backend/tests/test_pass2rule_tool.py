import asyncio
import unittest

from agent.tools.strength import pass2rule_tool as module


class FakePass2RulePredictor:
    def predict(self, password: str, **kwargs):
        return {
            "input_password": password,
            "device": "cpu",
            "decode": kwargs,
            "rules": [
                {
                    "rank": 1,
                    "ptn_rule": "A:!",
                    "description": "末尾追加「!」",
                    "score": -0.1,
                }
            ],
            "candidates": [
                {
                    "rank": 1,
                    "password": f"{password}!",
                    "ptn_rule": "A:!",
                    "rule_description": "末尾追加「!」",
                    "score": -0.1,
                }
            ],
            "count": 1,
        }


class Pass2RuleToolTestCase(unittest.TestCase):
    def test_missing_password_returns_error(self):
        result = asyncio.run(module.pass2rule_tool({"action_params": {}}))
        self.assertIn("error", result["_tool_result"])
        self.assertEqual(result["_tool_result"]["candidates"], [])

    def test_tool_uses_predictor_and_clamps_options(self):
        original_predictor = module._PREDICTOR
        module._PREDICTOR = FakePass2RulePredictor()
        try:
            result = asyncio.run(
                module.pass2rule_tool(
                    {
                        "action_params": {
                            "password": "password123",
                            "top_k": 999,
                            "beam_size": 999,
                            "label_budget": 9999,
                            "decode_len": 999,
                            "include_input": False,
                        }
                    }
                )
            )
        finally:
            module._PREDICTOR = original_predictor

        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["input_password"], "password123")
        self.assertEqual(tool_result["candidates"][0]["password"], "password123!")
        self.assertEqual(tool_result["decode"]["top_k"], 50)
        self.assertEqual(tool_result["decode"]["beam_size"], 200)
        self.assertEqual(tool_result["decode"]["label_budget"], 1000)
        self.assertEqual(tool_result["decode"]["decode_len"], 60)
        self.assertFalse(tool_result["decode"]["include_input"])


if __name__ == "__main__":
    unittest.main()
