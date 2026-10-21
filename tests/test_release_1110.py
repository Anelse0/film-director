"""1.11.0 release wiring: one line does not cross a cut (W54 / W55 in speaker_checks.py, render-lesson class), the W24
longest-silence sub-item as a render lesson, W28 for any camera, S5 执行卡 + 镜头纵览 with stage_check.py, qa_check Q04.
Source: offset EP06 场 02 review proposal §4 items 0–5 and §7 M1 (user 2026-10-19)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.13.0')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.11.0', log)
        self.assertLess(log.index('## 1.11.0'), log.index('## 1.10.0'))
        self.assertIn('1.11.0', read('tests/test_protected_zone.py'))

    def test_new_files_in_the_zone(self):
        zone = read('tests/test_protected_zone.py')
        for name in ("'scripts/speaker_checks.py'", "'scripts/stage_check.py'"):
            self.assertIn(name, zone)

    def test_render_lesson_classes(self):
        from validate_prompt import RENDER_LESSON_CODES, is_render_lesson
        self.assertIn('W54', RENDER_LESSON_CODES)
        self.assertIn('W55', RENDER_LESSON_CODES)
        self.assertTrue(is_render_lesson('W24 最长连续无台词 7s（10-17s）> 3s'))
        self.assertFalse(is_render_lesson('W24 台词窗口外 16s（59% > 20%）'))
        self.assertFalse(is_render_lesson('W28 镜头1 4s 只承载一整句'))

    def test_rule_text(self):
        skill = read('SKILL.md')
        self.assertIn('但一句不跨镜', skill)
        self.assertIn('21. **镜头纵览与执行卡必做。**', skill)
        self.assertIn('stage_check.py', skill)
        self.assertIn('Q04', skill)
        rhythm = read('references/duration-rhythm.md')
        self.assertIn('3. **一句不跨镜**', rhythm)
        self.assertIn('| W54 |', read('references/checks.md'))
        self.assertIn('| W55 |', read('references/checks.md'))
        self.assertIn('最长连续无台词 ≤3 s', rhythm)
        self.assertNotIn('一句可以跨两镜', rhythm)
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('**6a 反应镜**', stage5)
        self.assertIn('**8a 无台词段预算**', stage5)
        self.assertIn('## 5.11 执行卡', stage5)
        stage6 = read('references/stage-6-prompt-compiler.md')
        self.assertIn('一句台词不分两段引号跨镜', stage6)
        self.assertIn('排除错误人物发声', stage6)
        stage7 = read('references/stage-7-qa-continuity.md')
        self.assertIn('3. **八道审阅**', stage7)
        self.assertIn('| 8 节奏与剪辑', stage7)
        self.assertIn('听者替说话人开了口', stage7)
        self.assertIn('Q04', stage7)
        self.assertIn('W54 / W55', read('references/stage-4-performance.md'))
        self.assertIn('## 执行卡', read('templates/shot-card.md'))
        self.assertIn('## 镜头纵览', read('templates/shot-card.md'))
        qa = read('templates/qa.md')
        self.assertIn('用户已点名', qa)
        self.assertIn('### 8 节奏与剪辑', qa)
        self.assertIn('待验证', read('references/validation-log.md'))
        self.assertIn('画外整句镜', read('references/validation-log.md'))

    def test_examples_with_off_screen_lines_carry_the_conditions(self):
        from validate_prompt import validate
        for name in ('examples/example-02-lens-B-haneke.prompt.md', 'examples/example-06-balcony-cigarette.prompt.md'):
            result = validate(ROOT / name)
            self.assertEqual([w for w in result['warnings'] if w.startswith('W55')], [], name)
            self.assertTrue(any('画外整句镜' in i for i in result['info']), name)

    def test_checkers_import(self):
        import speaker_checks  # noqa: F401
        import stage_check  # noqa: F401


if __name__ == '__main__':
    unittest.main()
