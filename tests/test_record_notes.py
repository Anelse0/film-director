"""1.15.0 记录精简: `check.py qa` gives NOTEs (not codes — the W-code freeze holds) when a QA ## 历史 entry runs past 300
characters, when 「用户已点名」 runs past 200 (it holds categories and versions; the user's words live in ## 历史), and when a
## section name appears twice (an old review round kept instead of rewritten in place). Exit code and codes are untouched."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import check  # noqa: E402
from test_check import qa_text, run, run_json, write_fixture  # noqa: E402
from validate_prompt import validate  # noqa: E402

HISTORY = '## 历史\n\n- 分镜卡 v1.1（10-27）：镜 2 中近 → 中；用户：「往后退一点」\n- 分镜卡 v1（10-27）：初稿\n'


class RecordNoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.card, self.prompt, self.qa = write_fixture(Path(self.temp.name))
        fresh = sorted({w.split()[0] for w in validate(self.prompt)['warnings']})
        self.codes = '、'.join(fresh) if fresh else '无'

    def tearDown(self):
        self.temp.cleanup()

    def qa_with(self, history=HISTORY, **kw):
        return qa_text(codes=self.codes, **kw).replace('## 历史\n\n旧的审阅。\n\n', history)

    def test_short_records_give_no_note(self):
        self.assertEqual(check.record_notes(self.qa_with()), [])
        self.qa.write_text(self.qa_with(), encoding='utf-8')
        rc, out = run('qa', str(self.qa))
        self.assertEqual(rc, 0, out)
        self.assertNotIn('## 历史有', out)
        self.assertNotIn('同名的节', out)

    def test_long_history_entry_notes_without_changing_exit(self):
        long = HISTORY.replace('初稿', '初稿；' + '镜 3 的完整写法照抄一遍' * 30)
        self.qa.write_text(self.qa_with(history=long), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertEqual(data['exit'], 0)
        self.assertTrue(any(n.startswith('## 历史有 1 条超过 300 字（第 2 条') for n in data['notes']), data['notes'])

    def test_named_line_with_quotes_notes(self):
        named = '节奏（v1）、表演（v1.1）：' + '用户原话照抄' * 40
        notes = check.record_notes(self.qa_with(named=named))
        self.assertTrue(any(n.startswith('现行状态「用户已点名」') and '>200' in n for n in notes), notes)
        self.assertFalse(any('用户已点名' in n for n in check.record_notes(self.qa_with(named='节奏（v1、v1.7）、剪辑（v1.1）'))))

    def test_repeated_section_notes(self):
        text = self.qa_with()
        old_round = text[text.index('## 审阅'):text.index('## 历史')]
        twice = text.replace('## 历史', old_round.replace('## 审阅（S7 §7.1 八道）', '## 审阅（S7 §7.1 八道，旧一轮）') + '## 历史', 1)
        notes = check.record_notes(twice)
        self.assertTrue(any(n.startswith('同名的节出现不止一次') and '「## 审阅」×2' in n for n in notes), notes)

    def test_section_name_ignores_the_parenthetical(self):
        self.assertEqual(check.section_name('成片反馈，validation-log #31（上一条：Prompt v1.3）'), '成片反馈')
        self.assertEqual(check.section_name('审阅（S7 §7.1 八道）'), '审阅')
        self.assertEqual(check.section_name('历史（按时间倒序）'), '历史')


if __name__ == '__main__':
    unittest.main()
