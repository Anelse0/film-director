"""1.5.0: 剧本场面轨对本 skill 是参考不是锁定——列场地 / 场景清单，分镜合计与剧本估时对照（≥1.2 只提醒），
场级方案写"与场面轨的差异"。校准样本：THE ORDER EP03 场 4 v4.1 剧本页与项目实际的 clip01–04、场级方案。"""
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
CLIPS = sorted(FIX.glob('theorder-ep03-s04-clip0*.md'))
PLAN = FIX / 'theorder-ep03-s04-plan.md'


def tmp_file(d, name, text):
    p = Path(d) / name
    p.write_text(text, encoding='utf-8')
    return p


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
        self.assertIn('没有场面轨', st.render(r))


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
        plan = PLAN.read_text(encoding='utf-8') + (
            '\n与场面轨的差异：跑道段按内容拆成 clip01–03，牛棚段单独 clip04；'
            '剧本第 4 段"队伍跑进太阳"并进 clip03 结尾（用户采用时要求保留）\n')
        with tempfile.TemporaryDirectory() as d:
            p = tmp_file(d, 'plan.md', plan)
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


class WiringTests(unittest.TestCase):
    def test_docs_make_track_a_reference_not_a_lock(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('场面轨是参考，不是锁定', skill)
        self.assertIn('与场面轨的差异', skill)
        self.assertIn('scripts/scene_track.py', skill)
        self.assertNotIn('已确认的台词与场景是锁定内容', skill)
        self.assertIn('已确认的台词是锁定内容', skill)
        rhythm = (ROOT / 'references' / 'duration-rhythm.md').read_text(encoding='utf-8')
        self.assertIn('## 十一、场级合计与剧本场面轨', rhythm)
        self.assertIn('不退回', rhythm)
        intake = (ROOT / 'references' / 'stage-1-intake.md').read_text(encoding='utf-8')
        self.assertIn('**参考，不锁定**', intake)
        tpl = (ROOT / 'templates' / 'script-scene.md').read_text(encoding='utf-8')
        self.assertLess(tpl.index('## 场面轨'), tpl.index('## 剧本页'))


if __name__ == '__main__':
    unittest.main()
