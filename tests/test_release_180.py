"""1.8.0 release wiring: the camera-position plan (S5 §5.1g) is a mandatory S5 step with a presence checker."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.13.0')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.8.0', log)
        self.assertLess(log.index('## 1.8.0'), log.index('## 1.7.1'))
        self.assertIn('1.8.0', read('tests/test_protected_zone.py'))

    def test_rule_text_and_template(self):
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('## 5.1g 机位设计（必做', stage5)
        for item in ('左右：', '换边：', '动作可行：', '参考图视角：', '上一条成片：'):
            self.assertIn(item, stage5, item)
        self.assertIn('## 机位设计', read('templates/shot-card.md'))
        skill = read('SKILL.md')
        self.assertIn('camera_plan_check.py', skill)
        self.assertIn('20. **机位设计必做', skill)
        self.assertIn('| 机位设计 |', read('references/stage-7-qa-continuity.md'))

    def test_per_clip_recheck(self):
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('颗粒度按 clip', stage5)
        self.assertIn('4. **复核**', stage5)
        self.assertIn('### 复核', read('templates/shot-card.md'))
        skill = read('SKILL.md')
        self.assertIn('--stage s5', skill)
        self.assertIn('复核', skill)
        self.assertIn('wrong case', read('CHANGELOG.md'))

    def test_checker_is_in_the_zone(self):
        self.assertIn("'scripts/camera_plan_check.py'", read('tests/test_protected_zone.py'))


if __name__ == '__main__':
    unittest.main()
