import asyncio
import unittest

from agent.tools.generation.generate_tool import generate_password_tool


class GenerationPreferenceTestCase(unittest.TestCase):
    def test_manual_most_memorable_routes_to_passphrase(self):
        state = {
            "action_params": {},
            "gen_auto_mode": False,
            "gen_security_weight": 0.1,
            "messages": [{"role": "user", "content": "帮我生成一个密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["strategy"], "passphrase")
        self.assertEqual(tool_result["preference_profile"], "最好记")
        self.assertTrue(all("password" in item for item in tool_result["candidates"]))

    def test_manual_prefer_memorability_routes_to_pronounceable(self):
        state = {
            "action_params": {},
            "gen_auto_mode": False,
            "gen_security_weight": 0.3,
            "messages": [{"role": "user", "content": "帮我生成一个密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["strategy"], "pronounceable")
        self.assertEqual(tool_result["preference_profile"], "偏好记")
        self.assertTrue(all("password" in item for item in tool_result["candidates"]))

    def test_manual_high_security_keeps_random_constraints(self):
        state = {
            "action_params": {},
            "gen_auto_mode": False,
            "gen_security_weight": 0.9,
            "messages": [{"role": "user", "content": "帮我生成一个密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["strategy"], "random")
        self.assertEqual(tool_result["preference_profile"], "最高安全")
        self.assertEqual(tool_result["effective_constraints"]["min_length"], 16)

    def test_auto_mode_memorable_request_can_shift_profile(self):
        state = {
            "action_params": {},
            "gen_auto_mode": True,
            "gen_security_weight": 0.7,
            "messages": [{"role": "user", "content": "帮我生成一个好记一点的密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["strategy"], "pronounceable")
        self.assertEqual(tool_result["preference_profile"], "偏好记")
        self.assertEqual(tool_result["effective_security_weight"], 0.3)

    def test_explicit_constraints_keep_random_strategy(self):
        state = {
            "action_params": {"constraints": {"min_length": 18}},
            "gen_auto_mode": False,
            "gen_security_weight": 0.1,
            "messages": [{"role": "user", "content": "帮我生成一个密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        tool_result = result["_tool_result"]
        self.assertEqual(tool_result["strategy"], "random")
        self.assertEqual(tool_result["effective_constraints"]["min_length"], 18)

    def test_candidates_include_utility_scores(self):
        state = {
            "action_params": {},
            "gen_auto_mode": False,
            "gen_security_weight": 0.5,
            "messages": [{"role": "user", "content": "帮我生成一个密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        candidates = result["_tool_result"]["candidates"]

        self.assertTrue(candidates)
        for candidate in candidates:
            self.assertIn("security_score", candidate)
            self.assertIn("memorability_score", candidate)
            self.assertIn("constraint_penalty", candidate)
            self.assertIn("utility_score", candidate)

    def test_candidates_are_sorted_by_utility(self):
        state = {
            "action_params": {"constraints": {"min_length": 14}},
            "gen_auto_mode": False,
            "gen_security_weight": 0.9,
            "messages": [{"role": "user", "content": "帮我生成一个公司邮箱密码"}],
        }

        result = asyncio.run(generate_password_tool(state))
        scores = [
            candidate["utility_score"]
            for candidate in result["_tool_result"]["candidates"]
        ]

        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
