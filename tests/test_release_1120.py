"""1.12.0 release wiring (offset EP06 s02 review proposal §12, user 2026-10-19): S4 lands in production — three-segment
表演翻译 (stage_check S04 / S05 / W-C9), the bracket carries voice parameters only, A-layer words stay out of C / D (W57
backed by the lexicon; W40 / W49 folded in), tone as a parameter, six light-variant lexicon rows, new-code freeze."""
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
        self.assertIn('## 1.12.0', log)
        self.assertLess(log.index('## 1.12.0'), log.index('## 1.11.0'))
        self.assertIn('1.12.0', read('tests/test_protected_zone.py'))
        self.assertIn("'scripts/layer_checks.py'", read('tests/test_protected_zone.py'))

    def test_w40_w49_folded_into_w57(self):
        from validate_prompt import RENDER_LESSON_CODES
        self.assertIn('W57', RENDER_LESSON_CODES)
        self.assertNotIn('W49', RENDER_LESSON_CODES)
        self.assertNotIn('warns.append(f"W40', read('scripts/guide_checks.py'))
        self.assertNotIn('warns.append(f"W49', read('scripts/wording_checks.py'))
        table = read('references/checks.md')
        self.assertIn('| W57 |', table)
        self.assertIn('| W40 | **并入 W57', table)
        self.assertIn('| W49 | **并入 W57', table)

    def test_lexicon_rows_and_section(self):
        lex = read('references/externalization-lexicon.md')
        for row in ('| 不信 / 被拆穿（轻松） |', '| 被逗到 / 认了（轻松） |', '| 被看着 / 撞上目光（轻松） |',
                    '| 等对方（出去 / 回答）（轻松） |', '| 装无辜 / 明知故问（轻松） |', '| 随口 / 不当回事（轻松） |'):
            self.assertIn(row, lex, row)
        self.assertIn('## A 层词', lex)

    def test_rule_text(self):
        skill = read('SKILL.md')
        self.assertIn('情绪的**声音翻译**', skill)
        self.assertIn('A 层词不进 C / D', skill)
        self.assertIn('## 规则维护', skill)
        self.assertIn('新 W 码冻结', skill)
        stage4 = read('references/stage-4-performance.md')
        self.assertIn('**基调是参数，不是形容词**', stage4)
        self.assertIn('不进括号、不进镜头行', stage4)
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('**固定三段**', stage5)
        self.assertIn('S04 / S05', stage5)
        self.assertIn('W57', read('references/stage-6-prompt-compiler.md'))
        self.assertIn('成片在"演"一个形容词', read('references/stage-7-qa-continuity.md'))
        self.assertIn('强度 / 方向决定查外化词典的哪一行', read('references/scene-parameters.md'))
        self.assertIn('表演翻译（固定三段', read('templates/shot-card.md'))
        self.assertIn('不写情绪 / 判断 / 意图词（W57', read('templates/prompt-templates.md'))
        self.assertIn('A 层词边界', read('references/validation-log.md'))

    def test_checkers_import(self):
        import layer_checks  # noqa: F401
        import stage_check
        self.assertTrue(hasattr(stage_check, 'translation_checks'))


if __name__ == '__main__':
    unittest.main()
