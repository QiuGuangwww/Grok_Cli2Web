import unittest

from server import visible_answer


class LeakTests(unittest.TestCase):
    def test_strips_web_search_fence(self):
        raw = "```html\nweb_search\nquery\nQiuGuang\nnum_results\n10\n```\n你好"
        self.assertEqual(visible_answer(raw), "你好")

    def test_strips_xml_tool(self):
        raw = "<code_interpreter>\nprint(1)\n</code_interpreter>\n答案是 1"
        self.assertEqual(visible_answer(raw), "答案是 1")

    def test_keeps_normal_code(self):
        raw = "用这段：\n```python\nprint('hi')\n```"
        self.assertIn("print('hi')", visible_answer(raw))

    def test_hides_incomplete_dump(self):
        raw = "先搜一下\n```html\nweb_search\nquery\n"
        self.assertEqual(visible_answer(raw), "先搜一下")


if __name__ == "__main__":
    unittest.main()
