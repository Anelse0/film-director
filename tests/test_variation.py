"""1.4.0 variation track: W30-W33 (variation_checks.py), the 节奏档 check sets, the 3.5 words/s
default, and the measure_clip visual profile. The regression fixture mirrors the shape of the
triggering case (reckless-rivals EP02 clip01 v2.1: 20 s / 7 fixed shots 3/3/2/3/3/3/3, close-ups
from shot 3 on, 节奏档 表演, L19, shot 5 repeats shot 1's composition, no 峰值镜) with placeholder
content; the real v2.1 run is recorded in CHANGELOG 1.4.0."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from variation_checks import parse_field, profile, variation_checks, size_rank  # noqa: E402
from validate_prompt import validate  # noqa: E402

HEAD = ('【素材绑定】无参考素材。\n【总述】20秒16:9，室内两人。\n【起始状态】A 画左，B 画右。\n【分镜时间线】\n')
TAIL = '\n【贯穿要求】无bgm，只有环境音；不要字幕。\n'
E = '| 项 | 值 |\n|---|---|\n| duration | 20 |\n'


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def codes(result):
    return [w.split()[0] for w in result['warnings']]


TRIGGER_SHAPE = HEAD + '\n'.join([
    '镜头1（0-3s）：【双人侧面特写，平视，固定】两人相距十厘米，谁也不动。',
    '镜头2（3-6s）：【全景缓推到双人中景，平视，随两人挪步】台词（C，画外，3-4s，English）："Closer. Shoulders." 两人并肩。',
    '镜头3（6-8s）：【B 正面近景，平视，固定】B 的眼睛看灯、看地板。',
    '镜头4（8-11s）：【越 C 与监视器拍双人中近景，平视，固定】台词（C，画外，8-11s，English）："Now turn. Look at him. Like you hate him." 两人转身面对面。',
    '镜头5（11-14s）：【双人侧面特写，平视，固定，与镜头1同构图】台词（A，12-14s，English）："You gonna keep staring?"（气声）；B 闭着嘴。',
    '镜头6（14-17s）：【B 正面近景，越 A 的肩，固定】B 低头约一秒再抬起。',
    '镜头7（17-20s）：【A 正面近景，越 B 的肩，固定】A 的视线落到 B 的耳根再回来。',
]) + TAIL + E + '| 节奏档 | 表演 |\n| 台词轨 | 窗口 |\n| 语速词每秒 | 3 |\n| 透镜 | L19 |\n| 无声段理由 | 冷开场；错位注视；高光 |\n'


class TriggerRegressionTests(unittest.TestCase):
    def test_v2_1_shape_reports_at_least_two_of_w30_w31_w32(self):
        result = run(TRIGGER_SHAPE)
        found = {c for c in codes(result) if c in {'W30', 'W31', 'W32'}}
        self.assertGreaterEqual(len(found), 2, result['warnings'])
        self.assertIn('W31', found)                       # 3/3/2/3/3/3/3: longest 3 < 2 x shortest 2
        self.assertIn('W32', found)                       # no 峰值镜, no 【变化】 fields
        self.assertTrue(any('同构图但未声明新增' in w for w in result['warnings']))   # G6 repeat of shot 1
        # 表演档 no longer exempts the clip: the check set still runs
        self.assertTrue(any('检查集 W24' in i for i in result['info']))

    def test_performance_mode_cannot_silence_the_variation_track(self):
        without_reason = TRIGGER_SHAPE.replace('| 无声段理由 | 冷开场；错位注视；高光 |\n', '')
        result = run(without_reason)
        self.assertIn('W24', codes(result))
        self.assertIn('W32', codes(result))

    def test_english_default_rate_is_3_5_and_the_photographer_line_fits(self):
        # "Now turn. Look at him. Like you hate him." = 9 words in a 3 s window:
        # 3 words/s -> 3.0 s > 3 x 0.9 -> W05; 3.5 words/s -> 2.57 s -> fits, and no W22 (rec 3.0, window 3).
        explicit = run(TRIGGER_SHAPE)
        self.assertTrue(any(w.startswith('W05 C') for w in explicit['warnings']), explicit['warnings'])
        default = run(TRIGGER_SHAPE.replace('| 语速词每秒 | 3 |\n', ''))
        self.assertFalse(any(w.startswith('W05') and '窗口' in w for w in default['warnings']), default['warnings'])
        self.assertFalse(any(w.startswith('W22') for w in default['warnings']), default['warnings'])
        self.assertTrue(any('3.5 词/s' in i for i in default['info']))


class FieldGrammarTests(unittest.TestCase):
    def test_parse_field_arrows_unchanged_and_new(self):
        f = parse_field('【近景，固定】【变化：景别 全→近｜机位 固定→推｜光 =｜幅度 1→3｜新增 第一次对眼】')
        self.assertEqual(f['景别'], ('全', '近', True))
        self.assertEqual(f['机位'], ('固定', '推', True))
        self.assertEqual(f['光'][2], False)
        self.assertEqual(f['幅度'], ('1', '3', True))
        self.assertEqual(f['新增'], '第一次对眼')
        self.assertIsNone(parse_field('【近景，固定】没有字段'))

    def test_same_size_with_a_note_is_not_a_change_and_english_grammar_parses(self):
        f = parse_field('【变化：景别 中→中（双人同框）｜幅度 2→2】')
        self.assertFalse(f['景别'][2])
        self.assertFalse(f['幅度'][2])
        g = parse_field('[CHANGE: size W→CU | camera static→push | light front→side | amp 1→3]')
        self.assertTrue(g['景别'][2] and g['机位'][2] and g['光'][2] and g['幅度'][2])
        self.assertEqual(size_rank('CU'), 4)
        self.assertEqual(size_rank('全景缓推到双人中景'), 2)   # the size the move ends in

    def test_inference_from_tags_when_field_missing(self):
        shots = [(1, 0, 3, '【特写，固定】'), (2, 3, 6, '【近景，固定】'), (3, 6, 9, '【近景，固定】'), (4, 9, 12, '【近景，缓推】')]
        rows = profile(shots, '')
        self.assertFalse(rows[0]['declared'])
        self.assertEqual(rows[1]['changes']['景别'], True)
        self.assertEqual(rows[2]['changes']['景别'], False)
        self.assertEqual(rows[3]['changes']['机位'], True)
        self.assertIsNone(rows[2]['changes']['光'])


def shots_text(tags, lengths):
    t, out = 0, []
    for i, (tag, L) in enumerate(zip(tags, lengths), start=1):
        out.append(f'镜头{i}（{t}-{t + L}s）：{tag}A 看着 B。台词（A，{t}-{t + L}s，中文）："第{i}句话在这里说完。"')
        t += L
    return HEAD + '\n'.join(out) + TAIL + E.replace('20', str(t)) + '| 语速字每秒 | 4 |\n'


class W30W33Tests(unittest.TestCase):
    def test_w30_three_consecutive_zero_change_shots(self):
        tags = ['【近景，固定】【变化：景别 近｜机位 固定｜光 正｜幅度 1】'] + \
               ['【近景，固定】【变化：景别 =｜机位 =｜光 =｜幅度 1→1】'] * 3 + \
               ['【中景，固定】【变化：景别 近→中｜机位 =｜光 正→侧｜幅度 1→3】']
        result = run(shots_text(tags, [3, 3, 3, 3, 6]) + '| 峰值镜 | 5 |\n')
        self.assertTrue(any(w.startswith('W30 镜头 2–4') for w in result['warnings']), result['warnings'])
        self.assertNotIn('W31', codes(result))   # 6 >= 2 x 3
        self.assertNotIn('W32', codes(result))
        self.assertNotIn('W33', codes(result))

    def test_w30_fewer_than_two_dimensions_change(self):
        tags = ['【全景，固定】【变化：景别 全｜机位 固定｜光 正｜幅度 1】',
                '【中景，固定】【变化：景别 全→中｜机位 =｜光 =｜幅度 =】',
                '【近景，固定】【变化：景别 中→近｜机位 =｜光 =｜幅度 =】',
                '【特写，固定】【变化：景别 近→特｜机位 =｜光 =｜幅度 =】']
        result = run(shots_text(tags, [3, 3, 3, 6]) + '| 峰值镜 | 4 |\n')
        self.assertTrue(any('只有 1 个维度变化过' in w for w in result['warnings']), result['warnings'])

    def test_w31_no_shot_length_contrast_needs_four_shots(self):
        tags = ['【全景，固定】【变化：景别 全｜机位 固定｜光 正｜幅度 1】',
                '【中景，推】【变化：景别 全→中｜机位 固定→推｜光 =｜幅度 1→3】',
                '【近景，固定】【变化：景别 中→近｜机位 推→固定｜光 正→侧｜幅度 3→1】',
                '【特写，固定】【变化：景别 近→特｜机位 =｜光 =｜幅度 1→2】']
        self.assertIn('W31', codes(run(shots_text(tags, [3, 3, 2, 3]) + '| 峰值镜 | 2 |\n')))
        self.assertNotIn('W31', codes(run(shots_text(tags, [2, 4, 2, 4]) + '| 峰值镜 | 2 |\n')))
        self.assertNotIn('W31', codes(run(shots_text(tags[:3], [3, 3, 2]) + '| 峰值镜 | 2 |\n')))   # 3 shots: not judged

    def test_w32_missing_peak_or_fields(self):
        tags = ['【全景，固定】【变化：景别 全｜机位 固定｜光 正｜幅度 1】',
                '【中景，推】【变化：景别 全→中｜机位 固定→推｜光 =｜幅度 1→3】',
                '【近景，固定】', '【特写，固定】【变化：景别 近→特｜机位 =｜光 正→侧｜幅度 1→2】']
        result = run(shots_text(tags, [2, 4, 2, 4]))
        self.assertTrue(any(w.startswith('W32 未声明峰值镜') for w in result['warnings']))
        self.assertTrue(any('镜头 [3] 缺【变化' in w for w in result['warnings']))
        result2 = run(shots_text(tags, [2, 4, 2, 4]) + '| 峰值镜 | 9 |\n')
        self.assertTrue(any('峰值镜 9 不在' in w for w in result2['warnings']))

    def test_w33_peak_in_wide_ots_or_fixed_while_another_moves(self):
        tags = ['【全景，固定】【变化：景别 全｜机位 固定｜光 正｜幅度 3】',
                '【中景，推】【变化：景别 全→中｜机位 固定→推｜光 =｜幅度 3→1】',
                '【近景，越 A 的肩，固定】【变化：景别 中→近｜机位 推→越肩固定｜光 正→侧｜幅度 1→2】',
                '【特写，固定】【变化：景别 近→特｜机位 越肩→正面固定｜光 =｜幅度 2→3】']
        text = shots_text(tags, [2, 4, 2, 4])
        wide = run(text + '| 峰值镜 | 1 |\n')['warnings']
        self.assertTrue(any(w.startswith('W33') and '最小可见景别' in w for w in wide), wide)
        ots = run(text + '| 峰值镜 | 3 |\n')['warnings']
        self.assertTrue(any(w.startswith('W33') and '越肩' in w for w in ots), ots)
        fixed = run(text + '| 峰值镜 | 4 |\n')['warnings']
        self.assertTrue(any(w.startswith('W33') and '固定机位，而运镜给了镜头 [2]' in w for w in fixed), fixed)
        self.assertFalse(any(w.startswith('W33') for w in run(text + '| 峰值镜 | 2 |\n')['warnings']))

    def test_g6_repeat_needs_a_new_element_only_in_romance(self):
        tags = ['【特写，固定】【变化：景别 特｜机位 固定｜光 正｜幅度 1】',
                '【中景，推】【变化：景别 特→中｜机位 固定→推｜光 =｜幅度 1→3】',
                '【近景，固定】【变化：景别 中→近｜机位 推→固定｜光 正→侧｜幅度 3→1】',
                '【特写，固定，与镜头1同构图】【变化：景别 近→特｜机位 =｜光 侧→正｜幅度 1→2】']
        text = shots_text(tags, [2, 4, 2, 4]) + '| 峰值镜 | 2 |\n'
        plain = run(text)
        self.assertFalse(any('同构图但未声明' in w for w in plain['warnings']))
        self.assertTrue(any('重复构图：镜头4 ← 镜头1' in i for i in plain['info']))
        romance = run(text + '| 透镜 | L19 |\n')
        self.assertTrue(any('同构图但未声明新增' in w for w in romance['warnings']))
        declared = run(text.replace('幅度 1→2】', '幅度 1→2｜新增 第二次多一个眼神】') + '| 透镜 | L19 |\n')
        self.assertFalse(any('同构图但未声明' in w for w in declared['warnings']))

    def test_single_shot_clip_skips_the_track(self):
        text = HEAD + '镜头1（0-10s）：【近景，固定】A 抬眼。' + TAIL + E.replace('20', '10')
        result = run(text)
        self.assertFalse(any(c in {'W30', 'W31', 'W32', 'W33'} for c in codes(result)))
        self.assertTrue(any('单镜 clip' in i for i in result['info']))


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'visual profile requires ffmpeg/ffprobe')
class VisualProfileTests(unittest.TestCase):
    def test_profile_detects_flat_and_changed_cuts_and_writes_frames(self):
        from measure_clip import visual_profile, contact_sheet
        with tempfile.TemporaryDirectory() as temp:
            video = Path(temp) / 'three.mp4'
            vf = ("drawbox=enable='between(t,2,4)':x=0:y=0:w=160:h=90:color=white:t=fill,"
                  "drawbox=enable='gte(t,4)':x=40:y=20:w=80:h=50:color=white:t=fill")
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=160x90:d=6:r=10',
                            '-f', 'lavfi', '-i', 'anullsrc=r=8000:cl=mono', '-vf', vf, '-t', '6', '-shortest',
                            '-pix_fmt', 'yuv420p', str(video)], check=True, capture_output=True)
            rows = visual_profile(video, [0, 2, 4, 6])
            self.assertEqual([r['no'] for r in rows], [1, 2, 3])
            self.assertFalse(rows[1]['flat'])   # black -> white
            self.assertFalse(rows[2]['flat'])   # white -> black with a white box (edges + subject share)
            same = visual_profile(video, [0, 1, 2])
            self.assertTrue(same[1]['flat'])    # both frames inside the black segment
            frames, sheet = contact_sheet(video, [0, 2, 4, 6], Path(temp) / 'frames')
            self.assertEqual(len(frames), 3)
            self.assertIsNotNone(sheet)
            self.assertTrue(Path(sheet).exists())


if __name__ == '__main__':
    unittest.main()
