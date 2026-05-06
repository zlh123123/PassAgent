import unittest

from agent.skill_executor import _maybe_forced_strength_action


class StrengthExecutorTestCase(unittest.TestCase):
    def test_forces_current_strength_tool_from_todo(self):
        state = {
            "messages": [
                {
                    "role": "user",
                    "content": "帮我看下zhanglinghao123这个口令的强度如何",
                }
            ],
            "loop_count": 2,
        }
        current_step = {
            "description": "结合用户记忆检测个人信息命中",
            "tool_name": "personal_info_check",
        }

        result = _maybe_forced_strength_action(
            state,
            "strength-assessment",
            current_step,
            [current_step],
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["next_action"], "personal_info_check")
        self.assertEqual(result["action_params"], {"password": "zhanglinghao123"})

    def test_forces_retrieve_memory_before_strength_tools(self):
        state = {
            "messages": [{"role": "user", "content": "帮我检测 qwerty123"}],
            "loop_count": 0,
        }
        current_step = {
            "description": "检索用户记忆，获取个人信息与偏好",
            "tool_name": "retrieve_memory",
        }

        result = _maybe_forced_strength_action(
            state,
            "strength-assessment",
            current_step,
            [current_step],
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["next_action"], "retrieve_memory")
        self.assertEqual(result["action_params"]["query"], "帮我检测 qwerty123")

    def test_follow_up_reuses_previous_password(self):
        state = {
            "messages": [
                {
                    "role": "user",
                    "content": "帮我看下 zhanglinghao123 这个口令的强度如何",
                },
                {
                    "role": "assistant",
                    "content": "zhanglinghao123 容易被猜中。",
                },
                {
                    "role": "user",
                    "content": "这个容易会变成什么口令啊",
                },
            ],
            "tool_history": [],
            "loop_count": 2,
        }
        current_step = {
            "description": "用 Pass2Rule 预测旧口令可能变体和演化规则",
            "tool_name": "pass2rule",
        }

        result = _maybe_forced_strength_action(
            state,
            "strength-assessment",
            current_step,
            [current_step],
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["next_action"], "pass2rule")
        self.assertEqual(result["action_params"], {"password": "zhanglinghao123"})

    def test_does_not_force_other_skills(self):
        result = _maybe_forced_strength_action(
            {"messages": [], "loop_count": 0},
            "password-generation",
            {"tool_name": "generate_password"},
            [],
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
