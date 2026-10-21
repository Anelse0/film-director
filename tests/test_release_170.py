"""1.7.0 release wiring: the three new review codes (W43 焦点与虚实, W44 台词括号里的意图, W45 服装参考与穿着状态) are documented
where every other code is, the rules they enforce are in the stage references and templates, the paused item (借秒 / W42) is
not in the release, and the shot tag may carry 焦点在 X up to 80 characters without tripping W08 / W17."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_prompt import validate  # noqa: E402

NEW_CODES = ('W43', 'W44', 'W45')


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


class WiringTests(unittest.TestCase):
    def test_version_and_code_table(self):
        self.assertEqual(read('VERSION').strip(), '1.14.0')
        table = read('references/checks.md')
        for code in NEW_CODES:
            self.assertIn(f'| {code} |', table, code)
        self.assertNotIn('| W42 |', table)
        self.assertNotIn('借秒', table)
        self.assertIn('| W43 |', read('references/checks.md'))
        self.assertIn('W43 (focus_checks.py)', read('scripts/validate_prompt.py'))
        self.assertFalse((ROOT / 'scripts/load_checks.py').exists())

    def test_rules_are_in_the_stage_references(self):
        stage4 = read('references/stage-4-performance.md')
        self.assertIn('7. 台词括号', stage4)
        self.assertIn('态度的可见拍子', stage4)
        self.assertIn('意图 / 潜台词', stage4)
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('焦点与虚实', stage5)
        self.assertIn('焦点在谁（部位）', stage5)
        stage5b = read('references/stage-5b-reference-assets.md')
        self.assertIn('服装图是衣物的样子，不是穿着状态', stage5b)
        self.assertIn('只用于本条从不出现的衣物', stage5b)
        stage6 = read('references/stage-6-prompt-compiler.md')
        self.assertIn('焦点在 X（换空间时加 日/夜·内/外）】', stage6)
        self.assertIn('一律按每一镜的文字', stage6)
        self.assertIn('（W44）', stage6)
        stage7 = read('references/stage-7-qa-continuity.md')
        for code in NEW_CODES:
            self.assertIn(code, stage7)
        self.assertIn('焦点在 {X（部位）}', read('templates/prompt-templates.md'))
        self.assertIn('焦点在谁（部位）', read('templates/shot-card.md'))
        self.assertIn('焦点即选择', read('references/director-grammar.md'))
        self.assertIn('焦点在谁', read('references/camera-vocabulary.md'))
        self.assertIn('穿着状态', read('templates/asset-registry.md'))

    def test_protected_zone_lists_the_new_modules(self):
        zone = read('tests/test_protected_zone.py')
        for module in ('focus_checks.py', 'subtext_checks.py', 'costume_checks.py'):
            self.assertIn(f"'scripts/{module}'", zone, module)
        self.assertIn('1.7.0', zone)

    def test_long_tag_with_focus_still_parses(self):
        tag = '中近景，平视，过道这头往里拍，长焦，镜头随他坐下轻轻下移，A 居中，焦点在 A 的眼睛'
        self.assertGreater(len(tag), 40)
        text = ('【素材绑定】无参考素材。\n【总述】6秒3:4竖屏，酒吧；声音：无 bgm，只有环境音与台词。\n【画面基调】暖光，深景深。\n'
                '【起始状态】A 坐在吧台外，在画面中间。\n【分镜时间线】\n'
                f'镜头1（0-3s）：【{tag}】A 坐下。视线：A 看着吧台里面。\n'
                f'镜头2（3-6s）：【{tag}，缓推】A 抬眼。视线：A 看着 B。\n'
                '【贯穿要求】A 的脸与图一致；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n'
                '\n| 项 | 值 |\n|---|---|\n| duration | 6 |\n| 峰值镜 | 2 |\n')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'clip.prompt.md'
            path.write_text(text, encoding='utf-8')
            result = validate(path)
        self.assertFalse(any(w.startswith('W08') for w in result['warnings']), result['warnings'])
        self.assertFalse(any(w.startswith('W43') for w in result['warnings']), result['warnings'])
        self.assertTrue(any(re.match(r'焦点：2/2', i) for i in result['info']), result['info'])


if __name__ == '__main__':
    unittest.main()
