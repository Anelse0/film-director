"""1.8.0 camera library: a byte-identical copy of the user's AI运镜提示词库 (46 entries, five parts each), a Chinese
reading index, lookup / fill-template script, and W34-W35 in validate_prompt. Calibration: THE ORDER EP03 s04
clip01 shot 1 pasted shot-19 verbatim (English, generic End) into a Chinese Prompt at the user's request;
the fixture is that Prompt unchanged."""
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import camera_library as cl  # noqa: E402
from camera_checks import camera_checks, sources  # noqa: E402
from validate_prompt import validate  # noqa: E402

FIX = ROOT / 'tests' / 'fixtures' / 'camera' / 'theorder-ep03-s04-clip01.prompt.md'
SOURCE_SHA = '0f3136a56e593db3f721db97358681d641e6c941a0840df4fa5ea2ac9f0e88ec'  # all_prompts.json, 2026-09-23
FILLED_SHOT1 = ('【全景，侧跟拍，队伍从画右跑向画左】【变化：景别 全｜机位 侧跟拍｜光 逆光｜幅度 2】机位在跑道内侧与队伍平行移动，'
                '速度跟慢跑一致；Beckett 保持在画面中间偏左、侧脸对镜头，队伍在他身后排开，机位距离不变；'
                '止于 Beckett 喊完转回身、整排侧影横穿画面。画面：')


def codes(result, code):
    return [w for w in result['warnings'] if w.startswith(code)]


def variant(d, text):
    p = Path(d) / 'p.prompt.md'
    p.write_text(text, encoding='utf-8')
    return p


def with_source(text, row):
    return text.replace('| 表演来源 | free |', f'| 表演来源 | free |\n| 运镜来源 | {row} |')


class LibraryTests(unittest.TestCase):
    def test_vendored_copy_is_the_users_file(self):
        data = (ROOT / 'assets' / 'camera-library.json').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), SOURCE_SHA)
        self.assertIn(SOURCE_SHA[:8], (ROOT / 'references' / 'camera-library.md').read_text(encoding='utf-8'))
        entries = cl.load_library()
        self.assertEqual(len(entries), 46)
        self.assertEqual(len({e['category'] for e in entries.values()}), 7)
        for e in entries.values():
            self.assertTrue(e['prompt'].startswith('Camera: '), e['id'])

    def test_index_covers_every_entry_with_every_field(self):
        entries, index = cl.load_library(), cl.load_index()
        self.assertEqual(set(index), set(entries))
        fields = ('zh', 'terms', 'function', 'grammar', 'avoid', 'subject', 'carrier', 'official', 'vocab')
        grammar = (ROOT / 'references' / 'director-grammar.md').read_text(encoding='utf-8')
        for i, row in index.items():
            for f in fields:
                self.assertTrue(row.get(f), (i, f))
            for sec in re.findall(r'§(\d+\.\d+)', row['grammar']):
                self.assertIn(f'### {sec}', grammar, (i, sec))
            if row['grammar'].startswith('无'):
                self.assertIn('推论', row['grammar'] + row['function'], i)  # 库外新增的职能标推论

    def test_lookup_slots_and_raw(self):
        e, note = cl.load_library()['shot-19'], cl.load_index()['shot-19']
        text = cl.slots(e, note)
        self.assertIn('侧跟拍（Side tracking）', text)
        self.assertIn('动机（A 层，库里没有）', text)
        self.assertIn('End → 本镜终点构图（止于……），不用库里的通用句', text)
        self.assertIn('需要看见前方目的地时', text)
        out = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'camera_library.py'), '--raw', 'shot-19'],
                             capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, e['prompt'])
        hits = cl.select(cl.load_library(), cl.load_index(), query='侧跟')
        self.assertEqual([h['id'] for h in hits], ['shot-19'])
        with self.assertRaises(ValueError):
            cl.select(cl.load_library(), {}, ids=['shot-99'])

    def test_phrases_skip_short_generic_speed_words(self):
        phrases = {p for p, _, _ in cl.library_phrases()}
        self.assertIn(cl.norm("keep the subject in side profile or three-quarter profile at a stable distance."), phrases)
        self.assertNotIn(cl.norm("still and steady."), phrases)          # 3 词，自然英文里会出现
        self.assertNotIn(cl.norm("match the subject's pace."), phrases)  # 4 词


class ValidatorTests(unittest.TestCase):
    def test_ep03_verbatim_paste_is_w34(self):
        r = validate(FIX)
        w = codes(r, 'W34')
        self.assertEqual(len(w), 1, r['warnings'])
        self.assertTrue(w[0].startswith('W34 镜头1 照抄运镜库通用句（shot-19 end, shot-19 framing, shot-19 movement）'))
        self.assertIn('镜1 shot-XX 原文', w[0])
        self.assertEqual(codes(r, 'W35'), [])

    def test_declared_raw_passes_and_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            r = validate(variant(d, with_source(FIX.read_text(encoding='utf-8'), '镜1 shot-19 原文')))
        self.assertEqual(codes(r, 'W34') + codes(r, 'W35'), [])
        self.assertIn('运镜：镜1 shot-19 原文（用户指定）', r['info'])
        self.assertEqual(r['camera'], {1: {'id': 'shot-19', 'mode': '原文'}})

    def test_filled_version_passes(self):
        text = FIX.read_text(encoding='utf-8')
        start = text.index('【全景，侧跟拍')
        end = text.index('画面：', start) + len('画面：')
        filled = text[:start] + FILLED_SHOT1 + text[end:]
        with tempfile.TemporaryDirectory() as d:
            r = validate(variant(d, with_source(filled, '镜1 shot-19 填写')))
        self.assertEqual(codes(r, 'W34') + codes(r, 'W35'), [])
        self.assertIn('运镜：镜1 shot-19 填写', r['info'])

    def test_english_skeleton_in_chinese_prompt_without_library_sentences(self):
        text = FIX.read_text(encoding='utf-8')
        start = text.index('Camera: side tracking shot.')
        end = text.index('画面：', start)
        own = ('Camera: side tracking. Movement: run beside Beckett on the grass side. Speed: jogging pace. '
               'Framing: Beckett center-left in profile. End: he turns back to run. ')
        with tempfile.TemporaryDirectory() as d:
            r = validate(variant(d, text[:start] + own + text[end:]))
        w = codes(r, 'W34')
        self.assertEqual(len(w), 1, r['warnings'])
        self.assertIn('中文 Prompt 里夹着英文运镜五段骨架', w[0])

    def test_bad_source_rows_are_w35(self):
        base = FIX.read_text(encoding='utf-8')
        cases = {'镜1 shot-99 填写': '不在运镜库里', '镜9 shot-19 填写': 'Prompt 里没有这一镜',
                 '镜1 原文': '没有条目编号', '镜1 shot-19 照搬': '方式应为', '第一镜侧跟': '读不出'}
        with tempfile.TemporaryDirectory() as d:
            for row, want in cases.items():
                r = validate(variant(d, with_source(base, row)))
                self.assertTrue(any(want in w for w in codes(r, 'W35')), (row, r['warnings']))

    def test_source_row_parsing(self):
        got, probs = sources('| 运镜来源 | 镜1 shot-19 原文；镜3 SHOT-08；镜4 库外 |\n')
        self.assertEqual(got, {1: ('shot-19', '原文'), 3: ('shot-08', '填写'), 4: (None, '库外')})
        self.assertEqual(probs, [])
        self.assertEqual(sources('| 运镜来源 | 无 |\n'), ({}, []))

    def test_english_prompt_may_use_its_own_camera_words(self):
        shots = [(1, 0, 4, 'Camera: slow push toward Mara. Movement: forward along the hallway. '
                          'Speed: 3 seconds. Framing: Mara stays center, the door on the left. End: close-up of her eyes.')]
        w, _, _ = camera_checks(shots, '')
        self.assertEqual(w, [])  # 英文 Prompt、写的是本镜内容：不报


class WiringTests(unittest.TestCase):
    def test_docs_route_library_after_motive(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('references/camera-library.md', skill)
        self.assertIn('只在动机定下后提供五段写法', skill)
        self.assertIn('"用运镜库 / 这个运镜怎么写"', skill)
        s5 = (ROOT / 'references' / 'stage-5-directing-storyboard.md').read_text(encoding='utf-8')
        self.assertIn('**运镜库（1.8.0）**', s5)
        self.assertIn('库不决定要不要动', s5)
        self.assertIn('本场运动逻辑', s5)
        self.assertLess(s5.index('| 揭示信息 | 摇 / 横移 / 后拉 |'), s5.index('**运镜库（1.8.0）**'))  # 动机表在前
        s6 = (ROOT / 'references' / 'stage-6-prompt-compiler.md').read_text(encoding='utf-8')
        self.assertIn('| 运镜来源 |', s6)
        self.assertIn('**运镜库条目**', s6)
        s7 = (ROOT / 'references' / 'stage-7-qa-continuity.md').read_text(encoding='utf-8')
        self.assertIn('| 运镜库 |', s7)
        card = (ROOT / 'templates' / 'shot-card.md').read_text(encoding='utf-8')
        self.assertIn('运镜库条目（可选', card)
        grammar = (ROOT / 'references' / 'director-grammar.md').read_text(encoding='utf-8')
        self.assertIn('### 2.4 运镜库：执行语法', grammar)
        self.assertIn('### 2.1 动机原则', grammar)  # 动机原则原文保留
        vocab = (ROOT / 'references' / 'camera-vocabulary.md').read_text(encoding='utf-8')
        self.assertIn('camera-index.json', vocab)


if __name__ == '__main__':
    unittest.main()
