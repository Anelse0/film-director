"""1.9.0 release wiring: render lessons from offset EP06 s01 clip01 / clip02 — C09 bearing check on the camera plan,
W46-W49 / W51 / W52 in validate_prompt, and the user's decision that camera design starts from the reference images
the user already provided (no request for new or regenerated images)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.12.1')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.9.0', log)
        self.assertLess(log.index('## 1.9.0'), log.index('## 1.8.0'))
        self.assertIn('不要求用户补图或重出参考图', log)
        self.assertIn('1.9.0', read('tests/test_protected_zone.py'))

    def test_validator_imports_the_new_modules(self):
        source = read('scripts/validate_prompt.py')
        for module in ('wording_checks', 'continuity_checks', 'viewpoint_checks'):
            self.assertIn(f'from {module} import {module}', source)
        import validate_prompt  # noqa: F401  (import must succeed)

    def test_new_modules_are_in_the_zone(self):
        zone = read('tests/test_protected_zone.py')
        for module in ('wording_checks', 'continuity_checks', 'viewpoint_checks'):
            self.assertIn(f"'scripts/{module}.py'", zone)

    def test_rule_text(self):
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('机位从用户现有的参考图出发', stage5)
        self.assertNotIn('还压不住就出一张反方向的场景图', stage5)
        self.assertIn('**方位**', stage5)
        self.assertIn('**可达**', stage5)
        self.assertIn('C09', stage5)
        self.assertIn('W51', stage5)
        self.assertIn('每张场景图写视角', read('references/stage-5b-reference-assets.md'))
        stage6 = read('references/stage-6-prompt-compiler.md')
        for code in ('W46', 'W47', 'W48', 'W49', 'W51', 'W52'):
            self.assertIn(code, stage6, code)
        self.assertNotIn('语气 / 音量 / 语速）', stage6)
        stage7 = read('references/stage-7-qa-continuity.md')
        self.assertIn('上游成片末帧（不是 Prompt）', stage7)
        self.assertIn('台词挤成一团', stage7)
        self.assertIn('反打镜被生成成参考图的视角', stage7)
        self.assertIn('方位：', read('templates/shot-card.md'))
        self.assertNotIn('音量 / 语速 / 音色', read('templates/prompt-templates.md'))
        table = read('references/checks.md')  # 1.12.1: the code table moved out of duration-rhythm §七
        for code in ('W46', 'W47', 'W48', 'W49', 'W50', 'W51', 'W52'):
            self.assertIn(f'| {code} |', table, code)

    def test_skill_rules(self):
        skill = read('SKILL.md')
        self.assertIn('不要求补图', skill)
        self.assertIn('C01–C10', skill)
        self.assertIn('| W46 |', read('references/checks.md'))

    def test_no_new_image_request_in_checker_messages(self):
        for module in ('viewpoint_checks', 'camera_plan_check'):
            source = read(f'scripts/{module}.py')
            self.assertNotIn('出一张', source, module)
            self.assertNotIn('同视角的场景图替换', source, module)


if __name__ == '__main__':
    unittest.main()
