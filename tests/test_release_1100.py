"""1.10.0 release wiring: W50 paused (user 2026-10-19), C10 card-vs-prompt cross-check, seven review passes with WARN classes,
QA current-state template and qa_check.py, platform-difference note in the capability table."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.15.1')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.10.0', log)
        self.assertLess(log.index('## 1.10.0'), log.index('## 1.9.0'))
        self.assertIn('1.10.0', read('tests/test_protected_zone.py'))

    def test_w50_is_paused(self):
        """User 2026-10-19: "pause:W50". Like 借秒 (W42) in 1.7.0, the draft stays out of the repo and the code is reserved."""
        source = read('scripts/validate_prompt.py')
        self.assertNotIn('action_load_checks', source)
        self.assertFalse((ROOT / 'scripts/action_load_checks.py').exists())
        self.assertIn('| W50 | **暂停**', read('references/checks.md'))
        self.assertIn('RENDER_LESSON_CODES', source)
        self.assertNotIn('"W50"', source.split('RENDER_LESSON_CODES =')[1].split('\n')[0])

    def test_new_files_in_the_zone(self):
        zone = read('tests/test_protected_zone.py')
        for name in ("'scripts/qa_check.py'", "'templates/qa.md'"):
            self.assertIn(name, zone)

    def test_rule_text(self):
        stage7 = read('references/stage-7-qa-continuity.md')
        self.assertIn('3. **八道审阅**', stage7)  # 1.11.0 added the eighth pass
        self.assertIn('成片教训类', stage7)
        self.assertIn('C10', stage7)
        self.assertIn('qa_check.py', stage7)
        self.assertIn('templates/qa.md', stage7)
        self.assertIn('C10', read('references/stage-6-prompt-compiler.md'))
        self.assertIn('平台差异', read('references/seedance-2.5-capabilities.md'))
        self.assertIn('platform.md', read('references/stage-5-directing-storyboard.md'))
        self.assertIn('## 现行状态', read('templates/qa.md'))
        skill = read('SKILL.md')
        self.assertIn('qa_check.py', skill)
        self.assertIn('成片教训类', skill)
        self.assertIn('W50 暂停', skill)

    def test_checkers_import(self):
        import camera_plan_check  # noqa: F401
        import qa_check  # noqa: F401


if __name__ == '__main__':
    unittest.main()
