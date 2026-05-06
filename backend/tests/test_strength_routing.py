import unittest

from agent.router import _build_strength_assessment_todo


class StrengthRoutingTestCase(unittest.TestCase):
    def test_default_strength_plan_uses_multi_evidence_chain(self):
        todo = _build_strength_assessment_todo("帮我检测一下 qwerty123 安全吗")
        tool_names = [item["tool_name"] for item in todo]

        self.assertEqual(tool_names[0], "retrieve_memory")
        self.assertIn("zxcvbn_check", tool_names)
        self.assertIn("basic_analysis", tool_names)
        self.assertIn("pattern_detect", tool_names)
        self.assertIn("weak_list_match", tool_names)
        self.assertIn("pcfg_analyze", tool_names)
        self.assertIn("personal_info_check", tool_names)
        self.assertIn("passtsl_prob", tool_names)
        self.assertEqual(tool_names[-1], "respond")
        self.assertNotIn("pass2rule", tool_names)

    def test_pass2rule_is_conditionally_added_for_old_password_context(self):
        todo = _build_strength_assessment_todo("这是我的旧密码 password123，看看可能会改成什么变体")
        tool_names = [item["tool_name"] for item in todo]

        self.assertIn("pass2rule", tool_names)
        self.assertLess(tool_names.index("passtsl_prob"), tool_names.index("pass2rule"))
        self.assertEqual(tool_names[-1], "respond")

    def test_pass2rule_uses_recent_context_for_follow_up(self):
        todo = _build_strength_assessment_todo(
            "这个容易会变成什么口令啊",
            "帮我看下 zhanglinghao123 这个口令的强度如何",
        )
        tool_names = [item["tool_name"] for item in todo]

        self.assertIn("pass2rule", tool_names)


if __name__ == "__main__":
    unittest.main()
