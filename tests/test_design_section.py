"""`## 表演设计稿` has a slot of its own (S4 §4.4a): stage_check S01 checks that it exists, all ten rows are there and no
template blank is left; check.py plan gives the same finding as a note at dock A. Content is never judged."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import stage_check  # noqa: E402
from test_check import HEAD, SECTIONS, run  # noqa: E402
from test_stage_check import DESIGN, OVERVIEW  # noqa: E402


class DesignSectionTests(unittest.TestCase):
    def test_filled_table_has_no_finding(self):
        self.assertEqual(stage_check.design_findings(DESIGN), [])

    def test_missing_section_is_s01(self):
        found = stage_check.design_findings('## 走位表\n…\n')
        self.assertTrue(found and found[0].startswith('S01') and '表演设计稿' in found[0])

    def test_thin_table_names_the_missing_rows(self):
        thin = '## 表演设计稿\n| 镜 | 心里这一拍 | 看得见的 |\n|---|---|---|\n| 每镜心理拍子 | 写了 | 写了 |\n'
        found = stage_check.design_findings(thin)
        self.assertTrue(any('缺行' in f and '控制证据' in f and '基线' in f for f in found), found)

    def test_template_blank_is_reported_and_not_applicable_is_not(self):
        self.assertTrue(any('没填' in f for f in stage_check.design_findings(DESIGN.replace('写了', '__', 1))))
        self.assertEqual(stage_check.design_findings(DESIGN.replace('写了', '不适用：无台词', 1)), [])

    def test_whole_section_not_applicable_passes(self):
        self.assertEqual(stage_check.design_findings('## 表演设计稿\n不适用：空镜，没有人物\n'), [])

    def test_template_itself_is_read_as_unfilled(self):
        card = (ROOT / 'templates' / 'shot-card.md').read_text(encoding='utf-8')
        self.assertTrue(any('没填' in f for f in stage_check.design_findings(card)))

    def test_plan_gives_a_note_not_a_code(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'clip.md'
            path.write_text(HEAD + SECTIONS.replace(DESIGN, '') + OVERVIEW + '最长连续无台词 | 2 s（镜 3）\n', encoding='utf-8')
            rc, out = run('plan', str(path))
        self.assertEqual(rc, 0, out)
        self.assertIn('缺必做段「## 表演设计稿」', out)
        self.assertNotIn('S01', out)


if __name__ == '__main__':
    unittest.main()
