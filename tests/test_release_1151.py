"""1.15.1 (user 2026-10-31): the Prompt compiler has no character limits — W38 retired (the 篇幅 INFO keeps the counts;
no budget, no trim order, no E-layer `字数上限`), and the shot tag has no ≤60 / 80-character cap. Flow, docks and every
other code, threshold and class unchanged."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from validate_prompt import validate  # noqa: E402
from prompt_structure import shot_tag, tag_text  # noqa: E402
from variation_checks import tag_of as variation_tag  # noqa: E402
from rhythm_checks import tag_of as rhythm_tag  # noqa: E402
from tone_checks import shot_tag as tone_tag  # noqa: E402
from test_guide_checks import numbered, run, codes  # noqa: E402


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


def run_text(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


class Release1151(unittest.TestCase):
    def test_version_and_documents(self):
        self.assertEqual(read('VERSION').strip(), '1.15.1')
        self.assertIn('## 1.15.1', read('CHANGELOG.md'))
        checks = read('references/checks.md')
        self.assertIn('| W38 | **退役**', checks)
        self.assertIn('W38 退役', checks)
        self.assertIn('W38 退役', read('SKILL.md'))
        stage6 = read('references/stage-6-prompt-compiler.md')
        for gone in ('| 字数上限 |', '默认 3000 字', '≤ 60 字', 'W38 的删减顺序'):
            self.assertNotIn(gone, stage6, gone)
        self.assertIn('不限字数', stage6)
        templates = read('templates/prompt-templates.md')
        for gone in ('| 字数上限 |', '≤60 字', '给 W38'):
            self.assertNotIn(gone, templates, gone)
        self.assertNotIn('W38 的删减顺序', read('references/stage-4-performance.md'))
        guide = read('scripts/guide_checks.py')
        for gone in ('CJK_LIMIT', 'OFFICIAL_NOTE', 'def limits('):
            self.assertNotIn(gone, guide, gone)

    def test_overlong_body_is_info_not_w38(self):
        filler = '人物放在画面中间区域。' * 600   # ~6,600 CJK characters, more than twice the old budget
        long = numbered().replace('不要字幕。\n', '不要字幕。' + filler + '\n')
        result = run(long)
        self.assertEqual(result['errors'], [], result['errors'])
        self.assertNotIn('W38', codes(result))
        self.assertFalse(any('预算' in i for i in result['info'] if i.startswith('篇幅')), result['info'])
        self.assertTrue(any('不设上限' in i for i in result['info'] if i.startswith('篇幅')), result['info'])
        english = long.replace('人物放在画面中间区域。', 'the character stays in the middle third of the frame ')
        self.assertNotIn('W38', codes(run(english)))

    def test_long_shot_tag_is_still_the_tag(self):
        tag = '近景，平视，固定，' + '构图：A 在画面右三分之一处，' * 8 + '焦点在 A（眼）'
        self.assertGreater(len(tag), 100)
        text = ('【素材绑定】无参考素材。\n【总述】6秒3:4竖屏，酒吧；声音：无 bgm，只有环境音与台词。\n【画面基调】暖光，深景深。\n'
                '【起始状态】A 坐在吧台外，在画面中间。\n【分镜时间线】\n'
                f'镜头1（0-3s）：【{tag}】A 坐下。视线：A 看着吧台里面。\n'
                f'镜头2（3-6s）：【{tag}，缓推】A 抬眼。视线：A 看着 B。\n'
                '【贯穿要求】A 的脸与图一致；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n'
                '\n| 项 | 值 |\n|---|---|\n| duration | 6 |\n| 峰值镜 | 2 |\n')
        result = run_text(text)
        self.assertFalse(any(w.startswith('W08') for w in result['warnings']), result['warnings'])
        m = shot_tag(f'【{tag}】A 坐下。')
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), tag)
        self.assertIsNone(shot_tag('x' * 130 + '【近景，固定】'))   # the tag still has to open the shot
        for reader in (tag_text, variation_tag, rhythm_tag, tone_tag):   # every checker sees the whole long tag
            self.assertEqual(reader(f'【{tag}】A 坐下。'), tag, reader)
        for name in ('validate_prompt', 'rhythm_checks', 'tone_checks', 'variation_checks'):
            self.assertNotIn('{2,80}', read(f'scripts/{name}.py'), name)
        self.assertIsNone(shot_tag('镜头里没有标注。'))


if __name__ == '__main__':
    unittest.main()
