import unittest

from server import (
    CrewState,
    attach_human_notes,
    close_crew_run,
    decide_review,
    loop_detected,
    machine_assigns,
    next_recovery,
    open_crew_run,
    parse_ask,
    parse_feedback,
    parse_plan,
    parse_review,
    parse_rework,
    peek_guidance_ids,
    plan_waves,
    push_guidance,
    recover_model,
    resolve_agent,
    strip_ask_json,
    take_guidance,
    trim_loop,
    visible_answer,
    _is_reviewer,
)


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

    def test_parse_plan_json(self):
        plan = parse_plan(
            '{"lead":"查并总结","agents":[{"id":"research","name":"调研","brief":"找来源"},{"id":"write","name":"写作","brief":"成文"}]}'
        )
        self.assertEqual(plan["lead"], "查并总结")
        self.assertEqual(len(plan["agents"]), 2)
        self.assertEqual(plan["agents"][0]["name"], "调研")
        self.assertEqual(plan["agents"][1]["id"], "write")

    def test_parse_plan_fallback(self):
        plan = parse_plan("not json")
        self.assertGreaterEqual(len(plan["agents"]), 2)
        self.assertTrue(plan["lead"])

    def test_parse_plan_count_and_deps(self):
        plan = parse_plan(
            '{"lead":"分波","agents":[{"id":"research","name":"调研","brief":"找","depends_on":[]},{"id":"write","name":"写作","brief":"写","depends_on":["research"]}]}',
            3,
        )
        self.assertEqual(len(plan["agents"]), 2)
        write = next(a for a in plan["agents"] if a["id"] == "write")
        self.assertEqual(write["depends_on"], ["research"])
        waves = plan_waves(plan["steps"])
        self.assertGreaterEqual(len(waves), 2)
        self.assertTrue(any(s["id"] == "explore" for s in waves[0]))

    def test_parse_plan_steps_parallel(self):
        plan = parse_plan(
            '{"lead":"并行","steps":[{"id":"explore","name":"调研","depends_on":[],"agents":[{"id":"a","name":"甲","brief":"1"},{"id":"b","name":"乙","brief":"2"}]},{"id":"build","name":"实现","depends_on":["explore"],"agents":[{"id":"c","name":"丙","brief":"3"}]}]}',
            3,
        )
        self.assertEqual(len(plan["steps"]), 2)
        self.assertEqual(len(plan["steps"][0]["agents"]), 2)
        waves = plan_waves(plan["steps"])
        self.assertEqual(len(waves), 2)
        self.assertEqual(waves[0][0]["id"], "explore")

    def test_parse_feedback(self):
        items = parse_feedback('草稿\n{"feedback":[{"to":"cite","ask":"核对出处"}]}')
        self.assertEqual(items[0]["to"], "cite")
        self.assertIn("出处", items[0]["ask"])

    def test_parse_review_send_back(self):
        review = parse_review('{"pass":false,"issues":["缺评测"],"feedback":[{"to":"lead","ask":"补评测"}]}')
        self.assertFalse(review["pass"])
        self.assertTrue(review["explicit_pass"])
        self.assertEqual(review["feedback"][0]["to"], "lead")
        self.assertEqual(decide_review(review, "", 0), "rework")
        self.assertEqual(decide_review(review, "", 2), "stop")
        passed = parse_review('{"pass":true,"notes":"ok"}')
        self.assertTrue(passed["explicit_pass"])
        self.assertEqual(decide_review(passed, "", 0), "pass")
        self.assertEqual(decide_review({"explicit_pass": False, "issues": [], "feedback": []}, "还有不足", 0), "rework")

    def test_machine_assigns_and_phase(self):
        roster = [{"id": "algo", "name": "算法", "role": "worker"}, {"id": "write", "name": "成文", "role": "worker"}]
        review = {"feedback": [{"to": "algo", "ask": "补指标"}]}
        assigns = machine_assigns(review, roster, {}, [])
        self.assertEqual(assigns[0]["id"], "algo")
        state = CrewState("r1")
        snap = state.enter("reviewing", ["reviewer"])
        self.assertEqual(snap["phase"], "reviewing")
        state.mark_sent_back("algo")
        stopped = state.stop("max-rework")
        self.assertEqual(stopped["phase"], "stopped")
        self.assertEqual(stopped["stop"], "max-rework")

    def test_recovery_layers(self):
        self.assertEqual(recover_model("grok-4.6"), "grok-4.5")
        payload = {"model": "grok-4.6", "reasoning": {"effort": "high"}, "input": [{"role": "system", "content": "s"}, {"role": "user", "content": "task"}]}
        first = next_recovery(payload, 0)
        self.assertIn("重试", first["label"])
        second = next_recovery(payload, 1)
        self.assertEqual(second["payload"]["model"], "grok-4.5")
        third = next_recovery(payload, 2)
        self.assertIn("缩小", third["label"])
        self.assertIsNone(next_recovery(payload, 3))

    def test_parse_rework_reuse(self):
        rework = parse_rework('{"rework":true,"reuse":["algo"],"assigns":[{"id":"algo","brief":"补指标"}]}')
        self.assertTrue(rework["rework"])
        self.assertTrue(rework["explicit"])
        self.assertEqual(rework["assigns"][0]["id"], "algo")
        declined = parse_rework('{"rework":false,"notes":"终稿里说明即可"}')
        self.assertFalse(declined["rework"])
        self.assertTrue(declined["explicit"])

    def test_resolve_agent_and_reviewer(self):
        roster = [{"id": "cite", "name": "核源", "brief": "核对出处"}]
        self.assertEqual(resolve_agent("核源", roster)["id"], "cite")
        self.assertTrue(_is_reviewer({"id": "qa", "name": "审核", "brief": "打回不足"}))
        self.assertFalse(_is_reviewer({"id": "algo", "name": "算法", "brief": "建模"}))

    def test_guidance_queue(self):
        run_id = open_crew_run()
        self.assertTrue(push_guidance(run_id, "algo", "补一组评测"))
        self.assertEqual(peek_guidance_ids(run_id), ["algo"])
        self.assertEqual(take_guidance(run_id, "algo"), ["补一组评测"])
        self.assertEqual(take_guidance(run_id, "algo"), [])
        close_crew_run(run_id)
        self.assertFalse(push_guidance(run_id, "algo", "再补"))

    def test_parse_ask_and_ignore_plan(self):
        ask = parse_ask(
            '先确认一下\n{"ask":{"question":"更偏哪边？","options":[{"id":"recall","label":"召回","desc":"先覆盖"},{"id":"prec","label":"精度"}]}}'
        )
        self.assertEqual(ask["question"], "更偏哪边？")
        self.assertEqual(len(ask["options"]), 2)
        self.assertIsNone(parse_ask('{"lead":"拆","agents":[{"id":"a","name":"甲","brief":"1"}]}'))
        visible = strip_ask_json('说明一下\n{"ask":{"question":"选一个","options":["甲","乙"]}}')
        self.assertEqual(visible, "说明一下")

    def test_loop_detected_and_trim(self):
        looping = "I'll keep the report for later steps.\n" + "I'll go. I'll execute. I'll call. I'll run. I'll invoke. I'll do it. " * 8
        self.assertTrue(loop_detected(looping))
        kept = trim_loop(looping)
        self.assertIn("later steps", kept)
        self.assertNotIn("I'll invoke", kept)
        self.assertFalse(loop_detected("I'll start by checking the engine, then write the alignment report."))

    def test_attach_human_notes(self):
        payload = attach_human_notes(
            {"input": [{"role": "system", "content": "s"}, {"role": "user", "content": "任务"}]},
            ["先看召回"],
        )
        user = payload["input"][1]["content"]
        self.assertIn("任务", user)
        self.assertIn("先看召回", user)


if __name__ == "__main__":
    unittest.main()
