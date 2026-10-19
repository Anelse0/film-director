"""1.7.1 release wiring: W44 relaxed by the user's decision — the intent word's carrier is the director's choice (eye / face,
hand / body, voice or pause, an action toward the other character, or a delivery word in the bracket), not an eye beat. The
rule text says so wherever 1.7.0 wrote the eye-beat requirement, the W36 message no longer prescribes the beat's timing,
and W45 is unchanged."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

RULE_DOCS = ('references/stage-4-performance.md', 'references/stage-5-directing-storyboard.md', 'references/stage-6-prompt-compiler.md',
             'references/stage-7-qa-continuity.md', 'references/duration-rhythm.md', 'references/emotion-performance.md',
             'templates/shot-card.md', 'templates/prompt-templates.md', 'SKILL.md')


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.9.0')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.7.1', log)
        self.assertLess(log.index('## 1.7.1'), log.index('## 1.7.0'))
        self.assertIn('W45 服装状态维持原样', log)
        self.assertIn('1.7.1', read('tests/test_protected_zone.py'))

    def test_rule_text_names_every_carrier_and_drops_the_eye_mandate(self):
        stage4 = read('references/stage-4-performance.md')
        self.assertIn('载体由导演设计定，不限于眼神', stage4)
        for carrier in ('眼神 / 脸', '手与身体', '声音与停顿', '与对方的互动'):
            self.assertIn(carrier, stage4, carrier)
        self.assertIn('轻声 / 放慢 / 顿一拍 这类可执行的声音词也算', stage4)
        self.assertNotIn('眼神为主、幅度小、不设计表情转折', stage4)
        self.assertIn('1.7.1 放宽', read('references/duration-rhythm.md'))
        for doc in RULE_DOCS:
            text = read(doc)
            for phrase in ('同镜没有这个人的眼神拍子', '必须在镜头行有这个人的眼神拍子', '同镜要有这个人的眼神拍子', '同镜这个人的眼神拍子',
                           '写进镜头行作开口前一拍', '写进镜头行作开口前的一拍'):
                self.assertNotIn(phrase, text, (doc, phrase))
        self.assertIn('可执行拍子', read('references/stage-7-qa-continuity.md'))
        self.assertIn('载体由设计定', read('references/emotion-performance.md'))
        self.assertIn('载体写明', read('templates/shot-card.md'))
        self.assertIn('载体由导演设计定', read('SKILL.md'))
        self.assertIn('1.7.1 按用户决定放宽 W44', read('README.md'))

    def test_messages_follow_the_relaxed_rule(self):
        guide = read('scripts/guide_checks.py')
        self.assertIn('动作写进镜头行（不是搬进括号，W44）', guide)
        self.assertNotIn('作开口前的一拍', guide)
        subtext = read('scripts/subtext_checks.py')
        self.assertIn('不限于眼神', subtext)
        self.assertNotIn('眼神为主', subtext)
        self.assertIn('BACKGROUND_RE', subtext)
        self.assertIn('DELIVERY_RE', subtext)
        # W45 is untouched by this release.
        self.assertIn('1.7.0', read('scripts/costume_checks.py'))
        self.assertNotIn('1.7.1', read('scripts/costume_checks.py'))

    def test_code_table_row_lists_the_carriers(self):
        table = read('references/duration-rhythm.md')
        row = next(line for line in table.splitlines() if line.startswith('| W44 |'))
        for carrier in ('视线：', '手 / 头 / 身体', '声音与停顿', '对对方的动作', '轻声 / 放慢 / 顿一拍'):
            self.assertIn(carrier, row, carrier)
        self.assertTrue(re.search(r'画外 / 背对 / 后景', row), row)


if __name__ == '__main__':
    unittest.main()
