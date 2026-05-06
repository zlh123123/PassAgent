import unittest

from agent.graphical_intent import infer_graphical_mode, is_graphical_intent_text
from agent.router import _match_graphical_mode


class GraphicalRoutingTestCase(unittest.TestCase):
    def test_helper_skips_generic_image_and_text_requests(self):
        self.assertIsNone(infer_graphical_mode("上传图片生成密码"))
        self.assertFalse(is_graphical_intent_text("上传图片生成密码"))
        self.assertIsNone(infer_graphical_mode("分析这段文本"))
        self.assertFalse(is_graphical_intent_text("分析这段文本"))

    def test_helper_keeps_explicit_graphical_modes(self):
        self.assertEqual(infer_graphical_mode("我想用图片设密码"), "image")
        self.assertEqual(infer_graphical_mode("可以用地图位置做密码吗"), "map")
        self.assertEqual(infer_graphical_mode("我想试试富文本标记"), "richtext")
        self.assertTrue(is_graphical_intent_text("我想玩一下 PassInfinity"))
        self.assertTrue(is_graphical_intent_text("我想玩一下图形化口令"))

    def test_router_does_not_misroute_generic_requests(self):
        image_state = {
            "messages": [{"role": "user", "content": "上传图片生成密码"}],
        }
        text_state = {
            "messages": [{"role": "user", "content": "分析这段文本"}],
        }

        self.assertIsNone(_match_graphical_mode(image_state))
        self.assertIsNone(_match_graphical_mode(text_state))

    def test_router_keeps_passinfinity_entry_and_follow_up(self):
        entry_state = {
            "messages": [{"role": "user", "content": "我想玩一下 PassInfinity"}],
        }
        follow_up_state = {
            "messages": [
                {"role": "user", "content": "我想玩一下 PassInfinity"},
                {"role": "assistant", "content": "可以先选图片、地图或富文本。"},
                {"role": "user", "content": "打开页面"},
            ],
        }
        image_state = {
            "messages": [{"role": "user", "content": "我想用图片设密码"}],
        }

        entry_match = _match_graphical_mode(entry_state)
        follow_up_match = _match_graphical_mode(follow_up_state)
        image_match = _match_graphical_mode(image_state)

        self.assertIsNotNone(entry_match)
        self.assertEqual(entry_match[0], "graphical-mode")
        self.assertEqual(entry_match[1][0]["tool_name"], "graphical_mode")
        self.assertIn("因子选择页", entry_match[1][0]["description"])

        self.assertIsNotNone(follow_up_match)
        self.assertEqual(follow_up_match[1][0]["tool_name"], "graphical_mode")

        self.assertIsNotNone(image_match)
        self.assertEqual(image_match[1][0]["tool_name"], "graphical_mode")
        self.assertIn("图片模式", image_match[1][0]["description"])


if __name__ == "__main__":
    unittest.main()
