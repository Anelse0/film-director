"""1.5.0: 剧本场面轨对本 skill 是参考不是锁定——列场地 / 场景清单，分镜合计与剧本估时对照（≥1.2 只提醒），
场级方案写"与场面轨的差异"。校准样本：THE ORDER EP03 场 4 v4.1 剧本页与项目实际的 clip01–04、场级方案。
1.5.1: film-creative 3.7.0 把赌注卡与场面轨合成"## 事件轨"（一行一次变化），标题正则同时认两种；
样本 theorder-ep03-s04-v4.1-events.md 取自 film-creative tests/fixtures/review/（v3.7.0）。
1.6.0: 场级方案 clip 切分表的"交付变化"列——每条 clip 交付事件轨至少一个变化行，余韵不计入、不单独成 clip，
同一变化只交付一次。样本 theorder-ep03-s04-plan-delivery.md = 项目方案快照 + 维护者回填的这一列（非盲）：
clip04 只有余韵第 11 行（用户问"这 16 s 存在的意义是？"）。"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scene_track as st  # noqa: E402

FIX = ROOT / 'tests' / 'fixtures' / 'scene-track'
SCRIPT = FIX / 'theorder-ep03-s04-v4.1-track.md'
EVENTS = FIX / 'theorder-ep03-s04-v4.1-events.md'
CLIPS = sorted(FIX.glob('theorder-ep03-s04-clip0*.md'))
PLAN = FIX / 'theorder-ep03-s04-plan.md'
PLAN_D = FIX / 'theorder-ep03-s04-plan-delivery.md'
CLIP04_ROW = next(l for l in PLAN_D.read_text(encoding='utf-8').splitlines() if l.startswith('| s04-clip04'))


def tmp_file(d, name, text):
    p = Path(d) / name
    p.write_text(text, encoding='utf-8')
    return p


# 没有事件轨时分镜自己写的交付变化（"谁：进 → 出"）
LEGACY_SUBS = [('| 第 1–2 行 |', '| Isa：队伍中段 → 被叫到最前面 |'), ('| 第 3–6 行 |', '| Beckett：只提条件 → 压上名字 |'),
               ('| 第 7–10 行 |', '| Isa：并排 → 领先一个身位 |')]


def plan_variant(d, subs=(), extra=''):
    """回填方案的变体：subs = [(旧, 新)]，extra 追加在文末（如差异行）。"""
    text = PLAN_D.read_text(encoding='utf-8')
    for a, b in subs:
        assert a in text, a
        text = text.replace(a, b)
    return tmp_file(d, 'plan.md', text + extra)


class ReferenceListTests(unittest.TestCase):
    def test_places_segments_jumps_and_script_total(self):
        r = st.run(SCRIPT)
        self.assertEqual(list(r['places']), ['Sharks 球场外圈跑道', '牛棚'])
        self.assertIn('最后直道', r['places']['Sharks 球场外圈跑道'])
        self.assertEqual(len(r['segments']), 5)
        self.assertEqual(r['jumps'], 1)
        self.assertEqual((r['script_total'], r['script_total_source']), (69.0, '场面轨总估时'))
        text = st.render(r)
        self.assertIn('参考，不锁定', text)
        self.assertIn('场地 / 场景 2 处', text)

    def test_legacy_script_without_track_falls_back_and_needs_no_diff_line(self):
        with tempfile.TemporaryDirectory() as d:
            s = tmp_file(d, 's.md', '## 剧本页\n场 02 · 木板路 · 夜\n\n## 节拍表\n\n总窗口 ≈ 80 s\n')
            c = tmp_file(d, 'c.md', 'clip 时长 82 s · 9:16\n')
            p = tmp_file(d, 'plan.md', '合计 82 s\n')
            r = st.run(s, [c], p)
        self.assertEqual(r['segments'], [])
        self.assertEqual(r['script_total_source'], '节拍表总窗口（无场面轨）')
        self.assertEqual(r['ratio'], 1.02)
        self.assertIsNone(r['reminder'])
        self.assertEqual(r['problems'], [])
        self.assertIn('没有场面轨或事件轨', st.render(r))
        self.assertIsNone(r['track_kind'])


class EventTrackTests(unittest.TestCase):
    """film-creative 3.7+ 的事件轨：同一场 v4.1，11 行变化（10、11 为余韵），地点 / 活动 / 时间 / 锚句 / 估时列照读。"""

    def test_event_track_is_read_like_scene_track(self):
        r = st.run(EVENTS)
        self.assertEqual(r['track_kind'], '事件轨')
        self.assertEqual(len(r['segments']), 11)
        self.assertEqual([x['seg'] for x in r['segments']], [str(i) for i in range(1, 12)])
        self.assertEqual(list(r['places']), ['Sharks 球场外圈跑道', '牛棚'])
        self.assertEqual(r['places']['Sharks 球场外圈跑道'], ['队伍最前面', '并排', '最后直道', '白线', '登记桌'])
        self.assertEqual(r['jumps'], 1)  # 只有第 11 行"跳：几分钟后"
        self.assertEqual((r['script_total'], r['script_total_source']), (69.0, '事件轨总估时'))
        last = r['segments'][-1]
        self.assertEqual((last['loc'], last['act'], last['est']), ('牛棚（围栏内外）', '拉伸、等待', '15'))
        self.assertEqual(last['anchor'], '几分钟后，牛棚边。')
        text = st.render(r)
        self.assertIn('事件轨（参考，不锁定）：11 行', text)
        self.assertNotIn('没有场面轨', text)

    def test_event_track_total_ratio_and_diff_line(self):
        r = st.run(EVENTS, CLIPS, PLAN)
        self.assertEqual((r['production_total'], r['ratio']), (88.0, 1.28))
        self.assertIn('与事件轨的差异', r['problems'][0])
        with tempfile.TemporaryDirectory() as d:
            for line in ('与事件轨的差异：牛棚段单独 clip04', '与场面轨的差异：牛棚段单独 clip04'):
                p = tmp_file(d, 'plan.md', PLAN.read_text(encoding='utf-8') + '\n' + line + '\n')
                probs = st.run(EVENTS, CLIPS, p)['problems']
                self.assertFalse(any('差异' in x for x in probs), (line, probs))

    def test_event_track_without_total_sums_rows_and_ignores_cast_list(self):
        text = EVENTS.read_text(encoding='utf-8').replace('总估时 ≈ 69 s', '')
        with tempfile.TemporaryDirectory() as d:
            r = st.run(tmp_file(d, 's.md', text))
        self.assertEqual((r['script_total'], r['script_total_source']), (69.0, '事件轨各段估时之和'))
        self.assertEqual(len(r['segments']), 11)  # 人物清单"- **Isa**｜…"不是表行

    def test_old_scene_track_heading_still_read(self):
        r = st.run(SCRIPT)
        self.assertEqual(r['track_kind'], '场面轨')
        self.assertIn('场面轨（参考，不锁定）：5 段', st.render(r))


class TotalAndReminderTests(unittest.TestCase):
    def test_ep03_s04_total_ratio_and_reminder_does_not_fail(self):
        r = st.run(SCRIPT, CLIPS)
        self.assertEqual([s for _, s in r['clips']], [22.0, 28.0, 22.0, 16.0])
        self.assertEqual(r['production_total'], 88.0)
        self.assertEqual(r['ratio'], 1.28)
        self.assertIn('多 28%', r['reminder'])
        self.assertIn('照常继续', r['reminder'])
        self.assertIn('由用户定', r['reminder'])
        self.assertEqual(r['problems'], [])  # 提醒不是问题
        with redirect_stdout(io.StringIO()):
            self.assertEqual(st.main([str(SCRIPT), '--clips', *map(str, CLIPS)]), 0)

    def test_small_overrun_is_not_reminded(self):
        with tempfile.TemporaryDirectory() as d:
            c = tmp_file(d, 'c.md', 'clip 时长 80 s\n')  # 80 / 69 = 1.16
            r = st.run(SCRIPT, [c])
        self.assertEqual(r['ratio'], 1.16)
        self.assertIsNone(r['reminder'])

    def test_clip_without_duration_header_is_unparseable(self):
        with tempfile.TemporaryDirectory() as d:
            c = tmp_file(d, 'c.md', '# 没有时长\n')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(st.main([str(SCRIPT), '--clips', str(c)]), 2)


class PlanDiffLineTests(unittest.TestCase):
    def test_current_plan_lacks_diff_line(self):
        r = st.run(SCRIPT, CLIPS, PLAN)
        self.assertIsNone(r['plan_diff'])
        self.assertIn('与场面轨的差异', r['problems'][0])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(st.main([str(SCRIPT), '--clips', *map(str, CLIPS), '--plan', str(PLAN)]), 1)

    def test_plan_with_diff_line_passes_even_when_locations_changed(self):
        with tempfile.TemporaryDirectory() as d:
            p = plan_variant(d, LEGACY_SUBS + [('| 第 11 行 |', '| Diego：绑护腿 → 蹲好等他 |')],
                             '\n与场面轨的差异：跑道段按内容拆成 clip01–03，牛棚段单独 clip04；'
                             '剧本第 4 段"队伍跑进太阳"并进 clip03 结尾（用户采用时要求保留）\n')
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = st.main([str(SCRIPT), '--clips', *map(str, CLIPS), '--plan', str(p), '--json'])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertTrue(data['plan_diff'].startswith('跑道段按内容拆成'))
        self.assertEqual(data['ratio'], 1.28)
        with tempfile.TemporaryDirectory() as d:
            p = tmp_file(d, 'plan.md', '与场面轨的差异：无\n')
            self.assertEqual(st.run(SCRIPT, (), p)['plan_diff'], '无')


class DeliveryTests(unittest.TestCase):
    """1.6.0 方案 C：每条 clip 交付事件轨哪几行；删掉这条 clip 观众少的 = 那几行的"删掉损失"。"""

    def test_ep03_s04_clip04_delivers_only_linger_and_fails(self):
        r = st.run(EVENTS, CLIPS, PLAN_D)
        probs = [x for x in r['problems'] if '交付' in x]
        self.assertEqual(len(probs), 1, r['problems'])
        self.assertTrue(probs[0].startswith('s04-clip04：没有交付任何变化行（只列了余韵第 11 行）'))
        self.assertIn('余韵不单独成 clip', probs[0])
        self.assertIn('峰值事件、观众问题、无声段理由照常要写，但不能代替交付变化', probs[0])
        got = {c['clip']: [(x['n'], x['linger']) for x in c['rows']] for c in r['delivery']}
        self.assertEqual(got['s04-clip01'], [(1, False), (2, False)])
        self.assertEqual(got['s04-clip03'], [(7, False), (8, False), (9, False), (10, True)])  # 余韵尾巴可以写上
        self.assertEqual(got['s04-clip04'], [(11, True)])
        self.assertEqual(r['undelivered'], [])
        text = st.render(r)
        self.assertIn('s04-clip04 16 s ← 第 11 行 无（余韵：Isa 没答应，Diego 在等他）（余韵，不计入交付）', text)
        self.assertIn('｜删掉损失：竞技回报：他赢了队长', text)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(st.main([str(EVENTS), '--plan', str(PLAN_D)]), 1)

    def test_drop_or_merge_clip04_passes(self):
        with tempfile.TemporaryDirectory() as d:
            drop = plan_variant(d, [(CLIP04_ROW + '\n', '')], '\n与事件轨的差异：第 11 行（余韵，牛棚）不拍，已提醒用户\n')
            r = st.run(EVENTS, (), drop)
            self.assertEqual(r['problems'], [])
            self.assertIsNone(r['delivery_reminder'])
            merge = plan_variant(d, [(CLIP04_ROW + '\n', ''), ('| 第 7–10 行 |', '| 第 7–11 行 |')],
                                 '\n与事件轨的差异：第 11 行并进 clip03 尾部\n')
            self.assertEqual(st.run(EVENTS, (), merge)['problems'], [])

    def test_same_change_delivered_twice_is_a_problem(self):
        with tempfile.TemporaryDirectory() as d:
            p = plan_variant(d, [('| 第 11 行 |', '| 第 9、11 行 |')], '\n与事件轨的差异：无\n')
            probs = st.run(EVENTS, (), p)['problems']
        self.assertEqual(probs, ['第 9 行同时由 s04-clip03 和 s04-clip04 交付：一次变化只交付一次（后一条在重演它，或行号写错）'])

    def test_empty_wu_and_unknown_rows_are_problems(self):
        with tempfile.TemporaryDirectory() as d:
            for cell, want in (('无', '交付变化写的是"无"'), ('—', '交付变化写的是"—"'),
                               ('第 12 行', '事件轨没有这一行')):
                p = plan_variant(d, [('| 第 11 行 |', f'| {cell} |')], '\n与事件轨的差异：无\n')
                probs = st.run(EVENTS, (), p)['problems']
                self.assertTrue(any(want in x for x in probs), (cell, probs))
                self.assertTrue(any(x.startswith('s04-clip04：没有交付任何变化行') for x in probs), (cell, probs))

    def test_undelivered_change_rows_are_only_reminded(self):
        with tempfile.TemporaryDirectory() as d:
            p = plan_variant(d, [(CLIP04_ROW + '\n', ''), ('| 第 7–10 行 |', '| 第 7 行 |')], '\n与事件轨的差异：无\n')
            r = st.run(EVENTS, (), p)
        self.assertEqual(r['problems'], [])
        self.assertEqual(r['undelivered'], [8, 9])
        self.assertIn('第 8 行 观众：刚看他赢', r['delivery_reminder'])
        self.assertIn('写进差异行', r['delivery_reminder'])
        self.assertIn('提醒：没有 clip 交付的变化行', st.render(r))

    def test_plan_without_delivery_column_or_clip_table(self):
        for script in (EVENTS, SCRIPT):  # 新旧格式都要这一列
            probs = st.run(script, (), PLAN)['problems']
            self.assertTrue(any('缺"交付变化"列' in x for x in probs), (script.name, probs))
        with tempfile.TemporaryDirectory() as d:
            p = tmp_file(d, 'plan.md', '与事件轨的差异：无\n')
            self.assertIn('找不到 clip 切分表', st.run(EVENTS, (), p)['problems'][0])
            self.assertEqual(st.run(SCRIPT, (), tmp_file(d, 'p2.md', '与场面轨的差异：无\n'))['problems'], [])

    def test_without_event_track_director_writes_the_change(self):
        """规则不依赖模板：场面轨 / 无轨剧本由分镜自己写"谁：进 → 出"。自填的变化脚本放行（已知边界）。"""
        base = LEGACY_SUBS
        with tempfile.TemporaryDirectory() as d:
            ok = plan_variant(d, base + [('| 第 11 行 |', '| Diego：绑护腿 -> 蹲好等他 |')], '\n与场面轨的差异：无\n')
            r = st.run(SCRIPT, (), ok)
            self.assertEqual(r['problems'], [])
            self.assertEqual(r['delivery'][3]['rows'], [])  # 没有行号可核，只查写没写出变化
            for cell in ('无', 'Diego 在牛棚里等他', '第 11 行'):
                bad = plan_variant(d, base + [('| 第 11 行 |', f'| {cell} |')], '\n与场面轨的差异：无\n')
                probs = st.run(SCRIPT, (), bad)['problems']
                self.assertEqual(len(probs), 1, (cell, probs))
                self.assertTrue(probs[0].startswith(f's04-clip04：交付变化写的是"{cell}"'), probs)
                self.assertIn('谁：进 → 出', probs[0])
            with tempfile.TemporaryDirectory() as d2:
                s = tmp_file(d2, 's.md', '## 剧本页\n场 02 · 木板路 · 夜\n\n总窗口 ≈ 20 s\n')
                p = tmp_file(d2, 'p.md', '| clip | 时长 | 交付变化 |\n|---|---|---|\n| s02-clip01 | 20 s | 无（余韵） |\n')
                self.assertIn('写成"谁：进 → 出"', st.run(s, (), p)['problems'][0])

    def test_parse_refs(self):
        self.assertEqual(st.parse_refs('第 3–6 行（Isa 说出怕，第 9 行另算）'), [3, 4, 5, 6])
        self.assertEqual(st.parse_refs('第 1、2 行'), [1, 2])
        self.assertEqual(st.parse_refs('第 7 行、第 9 行'), [7, 9])
        self.assertEqual(st.parse_refs('7-9'), [7, 8, 9])
        self.assertEqual(st.parse_refs('Isa 领先 1 个身位'), [])
        self.assertEqual(st.parse_refs('无'), [])

    def test_json_carries_delivery(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            st.main([str(EVENTS), '--plan', str(PLAN_D), '--json'])
        data = json.loads(buf.getvalue())
        self.assertEqual([c['clip'] for c in data['delivery']], ['s04-clip01', 's04-clip02', 's04-clip03', 's04-clip04'])
        self.assertEqual(data['delivery'][3]['sec'], 16.0)


class WiringTests(unittest.TestCase):
    def test_docs_make_track_a_reference_not_a_lock(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('场面轨是参考，不是锁定', skill)
        self.assertIn('与场面轨的差异', skill)
        self.assertIn('scripts/scene_track.py', skill)
        self.assertNotIn('已确认的台词与场景是锁定内容', skill)
        self.assertIn('已确认的台词是锁定内容', skill)
        rhythm = (ROOT / 'references' / 'duration-rhythm.md').read_text(encoding='utf-8')
        self.assertIn('## 十一、场级合计与剧本场面轨 / 事件轨', rhythm)
        self.assertIn('不退回', rhythm)
        intake = (ROOT / 'references' / 'stage-1-intake.md').read_text(encoding='utf-8')
        self.assertIn('**参考，不锁定**', intake)
        tpl = (ROOT / 'templates' / 'script-scene.md').read_text(encoding='utf-8')
        self.assertLess(tpl.index('## 事件轨'), tpl.index('## 剧本页'))
        self.assertIn('事件轨', skill)
        self.assertIn('事件轨', intake)

    def test_delivery_rule_is_wired_without_replacing_variation_track(self):
        """1.6.0 加的是前置条件，不是替代：变化轨（硬规则 19、§5.1f、W30–W33）与审阅表原有各项都还在。"""
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('20. **每条 clip 至少交付一次变化。**', skill)
        self.assertIn('19. **镜与镜之间必须有变化（变化轨', skill)
        self.assertIn('互不代替', skill)
        self.assertIn('"这 N 秒存在的意义是？"', skill)
        s5 = (ROOT / 'references' / 'stage-5-directing-storyboard.md').read_text(encoding='utf-8')
        self.assertIn('6. **每条 clip 至少交付一次变化**', s5)
        self.assertIn('**不单独成 clip**', s5)
        self.assertIn('峰值事件从本条交付的变化行里选', s5)
        self.assertIn('1. **峰值事件**：每条 clip 先声明一个峰值事件', s5)  # 原条款保留
        self.assertIn('## 5.1f 变化轨', s5)
        s7 = (ROOT / 'references' / 'stage-7-qa-continuity.md').read_text(encoding='utf-8')
        for row in ('| 交付变化 |', '| 导演语法 |', '| 起止状态 |', '| 表演与时间 |', '画面始终没有变化的感觉'):
            self.assertIn(row, s7)
        self.assertIn('"这 N 秒存在的意义是？"', s7)
        rhythm = (ROOT / 'references' / 'duration-rhythm.md').read_text(encoding='utf-8')
        self.assertIn('6. **交付变化**', rhythm)
        self.assertIn('这一列不取代变化轨', rhythm)
        self.assertIn('**变化轨**（相邻两镜之间的差异', rhythm)


if __name__ == '__main__':
    unittest.main()
