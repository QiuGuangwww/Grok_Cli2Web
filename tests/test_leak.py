import unittest

from server import (
    CrewState,
    apply_user_choice,
    arbitrate_conflicts,
    both_solid,
    budget_policy,
    promote_remaining_contested,
    clamp_budget,
    estimate_usage,
    execute_local_tool,
    extract_function_calls,
    format_budget,
    parse_usage,
    permission_decision,
    resolve_local_path,
    attach_human_notes,
    can_see_contested,
    collect_merged_ask,
    commit_facts,
    contested_items,
    format_contested,
    is_verifier,
    pick_verify_spec,
    CREW_RUNS,
    coverage_score,
    filter_facts,
    find_conflicts,
    format_contract,
    harvest_facts,
    parse_facts,
    close_crew_run,
    decide_review,
    is_drop_error,
    looks_complete,
    loop_detected,
    machine_assigns,
    merge_asks,
    merge_feedback,
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

    def test_drop_error_and_complete(self):
        self.assertTrue(is_drop_error(RuntimeError("peer closed connection without sending complete message body (incomplete chunked read)")))
        self.assertFalse(is_drop_error(RuntimeError("bad request")))
        self.assertTrue(looks_complete("这段已经写完，可以交给后面步骤。" * 30))
        self.assertFalse(looks_complete("正在检索"))

    def test_parse_and_filter_facts(self):
        facts = parse_facts(
            '稿\n{"facts":[{"claim":"RT-2 uses PaLM-E","source":"arxiv:2307","confidence":"high","for":["write"]},'
            '{"claim":"maybe 1e9 demos","confidence":"hypothesis","for":["algo"]}]}'
        )
        self.assertEqual(len(facts), 2)
        writer = filter_facts(
            harvest_facts({"content": '{"facts":[{"claim":"RT-2 uses PaLM-E","confidence":"high","for":["write"]}]}', "name": "调研", "id": "a"}),
            {"id": "write", "name": "成文", "role": "worker", "step": "write"},
        )
        self.assertEqual(writer[0]["claim"], "RT-2 uses PaLM-E")
        algo = filter_facts(
            [{"claim": "RT-2 uses PaLM-E", "confidence": "high", "for": ["write"], "owner": "调研"}],
            {"id": "algo", "name": "算法", "role": "worker", "step": "algo"},
        )
        self.assertEqual(algo, [])
        text = format_contract([{"claim": "ok", "confidence": "high", "source": "p", "owner": "调研"}])
        self.assertIn("[high]", text)
        self.assertIn("ok", text)

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

    def test_conflict_arbitration(self):
        facts = [
            {"claim": "模型不支持 tool use", "source": "", "confidence": "low", "owner_id": "a", "status": "active"},
            {"claim": "模型支持 tool use", "source": "docs.x.ai", "confidence": "high", "owner_id": "b", "status": "active"},
        ]
        pairs = find_conflicts(facts)
        self.assertEqual(len(pairs), 1)
        verdicts = arbitrate_conflicts(facts)
        self.assertTrue(any(item.get("status") == "superseded" for item in facts))
        self.assertTrue(any("arbitrated" in str(item.get("source") or "") for item in verdicts))
        even = [
            {"claim": "A 不是最优", "confidence": "medium", "owner_id": "a", "status": "active"},
            {"claim": "A 是最优", "confidence": "medium", "owner_id": "b", "status": "active"},
        ]
        tied = arbitrate_conflicts(even)
        self.assertTrue(all(item.get("status") == "contested" for item in even))
        self.assertTrue(any(item.get("status") == "contested" for item in tied))
        worker = {"id": "algo", "name": "算法", "role": "worker", "step": "algo"}
        cite = {"id": "cite", "name": "核源", "role": "worker", "brief": "核对出处"}
        hidden = filter_facts(even + tied, worker)
        self.assertFalse(any(item.get("status") == "contested" for item in hidden))
        shown = filter_facts(even + tied, cite)
        self.assertTrue(any(item.get("status") == "contested" for item in shown))
        self.assertTrue(can_see_contested(cite))
        self.assertFalse(can_see_contested(worker))
        self.assertTrue(is_verifier(cite))
        self.assertFalse(is_verifier(worker))
        picked = pick_verify_spec([{"id": "algo", "name": "算法", "role": "worker"}, cite])
        self.assertEqual(picked["id"], "cite")
        fallback = pick_verify_spec([{"id": "write", "name": "成文", "role": "worker"}])
        self.assertEqual(fallback["id"], "verify")
        brief = format_contested(even)
        self.assertIn("最优", brief)
        self.assertEqual(len(contested_items(even)), 2)
        sourced = [
            {"claim": "官方口径 A：销量 100 万", "source": "gov.cn/a", "confidence": "high", "owner_id": "a", "status": "active", "for": ["write"]},
            {"claim": "官方口径不是 100 万而是 80 万", "source": "stats.gov.cn/b", "confidence": "high", "owner_id": "b", "status": "active", "for": ["write"]},
        ]
        self.assertTrue(both_solid(sourced[0], sourced[1]))
        verdicts = arbitrate_conflicts(sourced)
        self.assertTrue(all(item.get("status") == "superseded" for item in sourced))
        self.assertTrue(any(item.get("status") == "disputed" for item in verdicts))
        self.assertIn("gov.cn", verdicts[0]["source"])
        self.assertEqual(coverage_score(sourced + verdicts, ["write"])["conflicts"], 0)
        writer = {"id": "write", "name": "成文", "role": "worker", "step": "write"}
        shown = filter_facts(sourced + verdicts, writer)
        self.assertTrue(any(item.get("status") == "disputed" for item in shown))
        self.assertIn("[disputed]", format_contract(sourced + verdicts, writer))
        weak = [
            {"claim": "也许不支持导出", "source": "", "confidence": "low", "owner_id": "a", "status": "contested"},
            {"claim": "也许支持导出", "source": "", "confidence": "low", "owner_id": "b", "status": "contested"},
        ]
        promoted = promote_remaining_contested(weak)
        self.assertTrue(promoted)
        self.assertEqual(contested_items(weak), [])
        self.assertTrue(any(item.get("status") == "disputed" for item in weak))

    def test_commit_facts_replaces_owner_and_arbitrates(self):
        board = []
        commit_facts(
            board,
            {"id": "a", "name": "甲", "content": '{"facts":[{"claim":"接口不支持流式","confidence":"low"}]}'},
        )
        commit_facts(
            board,
            {
                "id": "b",
                "name": "乙",
                "content": '{"facts":[{"claim":"接口支持流式","source":"doc","confidence":"high"}]}',
            },
        )
        self.assertTrue(any(item.get("status") == "superseded" for item in board))
        self.assertTrue(any(item.get("source", "").startswith("arbitrated") for item in board))
        text = format_contract(board)
        self.assertNotIn("不支持流式", text)
        self.assertIn("支持流式", text)

    def test_merge_feedback_and_asks(self):
        merged = merge_feedback(
            [
                {"to": "cite", "ask": "核对论文出处"},
                {"to": "cite", "ask": "核对一下论文出处"},
                {"to": "algo", "ask": "补一组召回指标"},
            ]
        )
        self.assertEqual(len(merged), 2)
        asks = merge_asks(
            [
                {
                    "question": "更偏召回还是精度？",
                    "options": [{"id": "a", "label": "召回"}, {"id": "b", "label": "精度"}],
                },
                {
                    "question": "覆盖优先还是准确优先？",
                    "options": [{"id": "c", "label": "覆盖"}, {"id": "d", "label": "准确"}],
                },
            ]
        )
        self.assertIn("召回", asks["question"] + "".join(o["label"] for o in asks["options"]))
        self.assertLessEqual(len(asks["options"]), 4)
        one = collect_merged_ask(
            [
                '{"ask":{"question":"选方向","options":["先搜","先写"]}}',
                '{"ask":{"question":"怎么推进","options":["先搜","先改"]}}',
            ]
        )
        self.assertEqual(len(one["options"]), 3)

    def test_coverage_score_and_convergence(self):
        facts = [
            {"claim": "覆盖 explore", "confidence": "high", "for": ["explore"], "status": "active"},
            {"claim": "覆盖 write", "confidence": "medium", "for": ["write"], "status": "active"},
        ]
        score = coverage_score(facts, ["explore", "write"], ["覆盖 explore"])
        self.assertGreaterEqual(score["coverage"], 0.9)
        self.assertEqual(score["conflicts"], 0)
        self.assertGreaterEqual(score["acceptance"], 0.9)
        review = {"explicit_pass": False, "issues": ["还差一点"], "feedback": [{"to": "algo", "ask": "再补"}]}
        self.assertEqual(decide_review(review, "", 0, 2, score), "rework")
        self.assertEqual(decide_review(review, "", 1, 2, {**score, "confidence": 0.7}), "pass")
        conflicted = {**score, "conflicts": 1}
        self.assertEqual(decide_review({"explicit_pass": True, "issues": [], "feedback": []}, "", 0, 2, conflicted), "rework")
        self.assertEqual(decide_review(review, "", 2, 2, score), "stop")

    def test_plan_version_and_steer_sync(self):
        state = CrewState("r2")
        self.assertEqual(state.plan_version, 1)
        state.briefs["algo"] = "先建基线"
        state.record_steer("algo", "改成先看召回")
        self.assertEqual(state.plan_version, 2)
        self.assertIn("纠偏", state.briefs["algo"])
        self.assertIn("先看召回", state.changelog_since(1))
        self.assertEqual(state.changelog_since(2), "")
        self.assertIn("改成先看召回", state.acceptance)
        board = []
        apply_user_choice(state, board, "先覆盖再精修", "user answered")
        self.assertEqual(state.plan_version, 3)
        self.assertEqual(board[0]["source"], "user-decision")
        run_id = open_crew_run()
        CREW_RUNS[run_id]["machine"] = state
        self.assertTrue(push_guidance(run_id, "write", "不要扩写成终稿"))
        self.assertIn("不要扩写成终稿", state.briefs["write"])
        self.assertGreaterEqual(state.plan_version, 4)
        close_crew_run(run_id)

    def test_budget_stops_and_policy(self):
        self.assertEqual(clamp_budget(0), 0)
        self.assertEqual(clamp_budget(-3), 0)
        self.assertEqual(clamp_budget(480_000), 500_000)
        self.assertEqual(format_budget(0, True), "♾️")
        self.assertEqual(format_budget(0), "0")
        self.assertEqual(format_budget(1_200_000), "1.2M")
        self.assertEqual(format_budget(50_000), "50K")
        tight = budget_policy(50_000, 40)
        self.assertEqual(tight["workers"], 3)
        self.assertEqual(tight["max_review"], 0)
        self.assertEqual(budget_policy(0, 12)["workers"], 12)
        self.assertEqual(parse_usage({"usage": {"input_tokens": 10, "output_tokens": 5}}), 15)
        self.assertGreater(estimate_usage({"input": [{"role": "user", "content": "hello" * 40}]}, "ok"), 0)
        state = CrewState("r3")
        state.budget_tokens = 100
        state.add_usage(40)
        self.assertTrue(state.can_spend())
        state.add_usage(80)
        self.assertTrue(state.budget_hit)
        self.assertFalse(state.can_spend())
        self.assertEqual(state.snapshot()["spend"]["used"], 120)

    def test_local_files_and_permissions(self):
        self.assertEqual(permission_decision("ask", "read_file"), "ask")
        self.assertEqual(permission_decision("auto", "read_file"), "allow")
        self.assertEqual(permission_decision("auto", "write_file"), "deny")
        self.assertEqual(permission_decision("all", "write_file"), "allow")
        self.assertEqual(permission_decision("all", "run_command"), "allow")
        with self.assertRaises(ValueError):
            resolve_local_path("/etc/passwd")
        with self.assertRaises(ValueError):
            resolve_local_path("~/.ssh/id_rsa")
        with self.assertRaises(ValueError):
            resolve_local_path("~/.grok/auth.json")
        here = resolve_local_path(__file__)
        self.assertTrue(here.is_file())
        from pathlib import Path as _P
        self.assertEqual(resolve_local_path("Download"), (_P.home() / "Downloads").resolve())
        self.assertEqual(resolve_local_path("下载文件夹"), (_P.home() / "Downloads").resolve())
        text = execute_local_tool("read_file", {"path": __file__, "limit": 5})
        self.assertIn("import unittest", text)
        listed = execute_local_tool("list_dir", {"path": str(here.parent)})
        self.assertIn("test_leak.py", listed)
        home_list = execute_local_tool("list_dir", {})
        self.assertTrue(home_list)
        self.assertNotIn("缺少路径", home_list)
        self.assertIn("缺少路径", execute_local_tool("read_file", {}))
        calls = extract_function_calls(
            {"output": [{"type": "function_call", "name": "read_file", "call_id": "c1", "arguments": '{"path":"~/x"}'}]}
        )
        self.assertEqual(calls[0]["name"], "read_file")
        self.assertEqual(calls[0]["arguments"]["path"], "~/x")


if __name__ == "__main__":
    unittest.main()
