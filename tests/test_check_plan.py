"""1.14.0 check.py plan (停靠 A · 方案, S5 §5.2 after step 8): camera_plan_check --stage s5 plus the overview-table
arithmetic — rows, time continuity, dialogue rows, silent seconds, the longest-silence line — without stage_check,
because at dock A the per-shot sections and the execution card do not exist yet. Notes, not codes (W-code freeze)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from test_check import HEAD, SECTIONS, CAMERA_PLAN, card_text, run, run_json  # noqa: E402
from test_stage_check import OVERVIEW  # noqa: E402

DOCK_A = HEAD + SECTIONS + OVERVIEW + '最长连续无台词 | 2 s（镜 3）\n'


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.card = Path(self.temp.name) / 'clip.md'

    def tearDown(self):
        self.temp.cleanup()

    def write(self, text):
        self.card.write_text(text, encoding='utf-8')
        return str(self.card)

    def test_dock_a_card_without_shots_or_execution_card_passes(self):
        rc, out = run('plan', self.write(DOCK_A))
        self.assertEqual(rc, 0, out)
        self.assertIn('== check.py plan', out)
        self.assertIn('镜头纵览 3 行，逐镜小节还没写（停靠 A 正常）；时间止于 6s', out)
        self.assertIn('台词行 2；无台词秒 合计 3s / 单镜最大 2s；表下最长连续无台词 2s', out)
        self.assertIn('- 机位设计：camera_plan_check 0 ERROR；WARN 无', out)
        self.assertNotIn('S01', out)
        self.assertNotIn('执行卡：', out)

    def test_full_card_counts_shots(self):
        rc, data = run_json('plan', self.write(card_text()))
        self.assertEqual(rc, 0)
        tools = [r['tool'] for r in data['runs']]
        self.assertEqual(tools, ['camera_plan_check --stage s5', '镜头纵览算术'])
        self.assertTrue(any('分镜卡已有「## 镜头 N」3 个' in i['message'] for i in data['info']), data['info'])

    def test_time_gap_and_long_silence_are_notes(self):
        text = DOCK_A.replace('| 2 | 2-4s |', '| 2 | 3-4s |').replace('最长连续无台词 | 2 s（镜 3）', '最长连续无台词 | 5 s（镜 2–3）')
        rc, out = run('plan', self.write(text))
        self.assertEqual(rc, 0, out)
        self.assertIn('NOTE  纵览时间不连续：镜 2 从 3s 起，上一镜止于 2s', out)
        self.assertIn('NOTE  表下最长连续无台词 5s > 3 s：停靠 A 就要用户点头', out)

    def test_row_count_mismatch_is_a_note_not_an_error(self):
        short = card_text().replace('| 3 | 4-6s | 中景 | 横移 | A | 无 | 2 | 侧面 | 横移 |\n', '')
        rc, out = run('plan', self.write(short))
        self.assertEqual(rc, 0, out)
        self.assertIn('NOTE  纵览 2 行 ≠ 「## 镜头 N」3 个', out)

    def test_missing_overview_is_a_note(self):
        rc, out = run('plan', self.write(HEAD + SECTIONS))
        self.assertEqual(rc, 0, out)
        self.assertIn('NOTE  没有「## 镜头纵览」表', out)

    def test_missing_camera_plan_is_still_c01(self):
        rc, out = run('plan', self.write(DOCK_A.replace(CAMERA_PLAN, '')))
        self.assertEqual(rc, 1, out)
        self.assertIn('ERROR [camera_plan_check --stage s5] C01', out)


if __name__ == '__main__':
    unittest.main()
