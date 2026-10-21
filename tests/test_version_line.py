"""1.14.1 版本行一行制: check.py gives a NOTE (not a code — the W-code freeze holds) when the shot card's version line or
the Prompt E-table 版本 row runs past 200 characters; the number block, codes and exit code are untouched."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import check  # noqa: E402
from test_check import HEAD, card_text, write_fixture, run, run_json  # noqa: E402

LONG_HEAD = HEAD.replace('**版本：v1.3 · 2026-10-20**（示例）', '**版本：v1.3 · 2026-10-20 · 状态：已确认**' + '停靠 B 第三轮改了什么' * 30)
CARD_NOTE = '分镜卡版本行'
PROMPT_NOTE = 'Prompt E 表「版本」行'


class VersionLineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_short_lines_give_no_note(self):
        card = card_text()
        self.assertEqual(check.version_line_notes(card_text=card, prompt_text='| 版本 | v1.2 · 2026-10-21 |\n'), [])
        card, prompt, _ = write_fixture(self.root)
        rc, out = run('s6', str(card), str(prompt))
        self.assertNotIn(CARD_NOTE, out)
        self.assertNotIn(PROMPT_NOTE, out)

    def test_long_card_line_notes_on_s5_and_plan_without_changing_exit(self):
        long_card = card_text().replace(HEAD, LONG_HEAD)
        self.assertIn(HEAD, card_text())
        card, _, _ = write_fixture(self.root, card=long_card)
        for sub in ('s5', 'plan'):
            rc, out = run(sub, str(card))
            self.assertEqual(rc, 0, out)
            self.assertIn(f'NOTE  {CARD_NOTE}', out)
            self.assertIn('>200）：版本行一行制', out)
            self.assertNotIn(PROMPT_NOTE, out)
        _, data = run_json('s5', str(card))
        self.assertTrue(any(n.startswith(CARD_NOTE) for n in data['notes']))
        self.assertEqual(data['exit'], 0)

    def test_long_prompt_version_row_notes_on_s6(self):
        card, prompt, _ = write_fixture(self.root)
        text = prompt.read_text(encoding='utf-8')
        self.assertIn('| 版本 | v1.2（2026-10-20：示例） |', text)
        prompt.write_text(text.replace('| 版本 | v1.2（2026-10-20：示例） |', '| 版本 | v1.2（2026-10-20：' + '改稿原话' * 60 + '） |'), encoding='utf-8')
        rc, out = run('s6', str(card), str(prompt))
        self.assertIn(f'NOTE  {PROMPT_NOTE}', out)
        self.assertNotIn(CARD_NOTE, out)
        # the version itself still parses (qa_check Q02 reads the first version in the row)
        row = re.search(r'\|\s*版本\s*\|\s*([^|\n]+)\|', prompt.read_text(encoding='utf-8'))
        self.assertTrue(row and row.group(1).strip().startswith('v1.2'), row)


if __name__ == '__main__':
    unittest.main()
