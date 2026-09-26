"""W22-W26 duration / rhythm review hints (rhythm_checks.py)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from rhythm_checks import recommended_window, rhythm_checks, scene_mode, track_schedule, track_mode, DEFAULTS  # noqa: E402

META = '| 项 | 值 |\n|---|---|\n| duration | 30 |\n| 语速词每秒 | 3 |\n'


def row(shot, speaker, start, end, words):
    return {'speaker': speaker, 'text': 'x ' * words, 'start': float(start), 'end': float(end),
            'estimate': words / 3, 'explicit': True, 'shot': str(shot)}


class RhythmTests(unittest.TestCase):
    def test_recommended_window_rounds_up_to_half_second_with_one_second_floor(self):
        self.assertEqual(recommended_window(11 / 3, 0.9), 4.5)   # 3.67 / 0.9 = 4.07 -> 4.5
        self.assertEqual(recommended_window(1.0, 0.9), 1.5)      # 1.11 -> 1.5
        self.assertEqual(recommended_window(1 / 3, 0.9), 1.0)    # one word still needs 1 s

    def test_wide_window_is_w22_but_recommended_plus_one_second_is_not(self):
        shots = [(1, 0, 3, '【近景，固定】'), (2, 3, 6, '【近景，固定】')]
        rows = [row(1, 'A', 0, 3, 4), row(2, 'B', 3, 6, 9)]  # A: 1.33 s -> rec 1.5, window 3 -> +1.5
        warns, _, _ = rhythm_checks(shots, rows, 6, META.replace('30', '6'))
        self.assertTrue(any(w.startswith('W22 A') for w in warns))
        self.assertFalse(any(w.startswith('W22 B') for w in warns))   # 3 s -> rec 3.5, window 3

    def test_dialogue_led_clip_flags_silence_long_shot_asl_and_redundancy(self):
        shots = [(1, 0, 2, '【全景，固定】'), (2, 2, 8, '【中景，固定】'), (3, 8, 14, '【中景，固定】'),
                 (4, 14, 19, '【近景，固定】'), (5, 19, 24, '【近景，固定】'), (6, 24, 30, '【全景，固定】')]
        rows = [row(2, 'A', 2, 7, 11), row(3, 'B', 8, 12, 10), row(4, 'A', 14, 17, 8), row(5, 'B', 19, 23, 10)]
        warns, infos, stats = rhythm_checks(shots, rows, 30, META)
        codes = {w.split()[0] for w in warns}
        self.assertIn('W23', codes)   # shot 6: 6 s, no line, fixed camera
        self.assertIn('W24', codes)   # 30 - 16 = 14 s outside windows (47 %), trailing 7 s
        self.assertIn('W25', codes)   # ASL 5.0 > 4.5
        self.assertIn('W26', codes)   # track 13.0/0.9 = 14.4 + 8 silent = 23 vs 30
        self.assertEqual(stats['derived'], 23)
        self.assertTrue(any('平均镜长 5.0s' in i for i in infos))

    def test_performance_led_single_shot_only_reports_info(self):
        shots = [(1, 0, 20, '【中景，固定】')]
        rows = [row(1, 'A', 6, 8, 3)]
        warns, infos, _ = rhythm_checks(shots, rows, 20, META.replace('30', '20'))
        self.assertEqual(warns, [])
        self.assertTrue(any('节奏档 表演' in i for i in infos))

    def test_performance_mode_selects_a_check_set_not_info_only(self):
        # 1.4.0: 表演档 = W24 (silent stretches carry a declared function) + W30-W33; W22 / W23 / W25-W29 off.
        shots = [(1, 0, 10, '【中景，固定】'), (2, 10, 20, '【近景，固定】')]
        rows = [row(1, 'A', 2, 8, 3)]                 # 1 s of speech in a 6 s window: W22 would fire in 对话
        meta = META.replace('30', '20')
        warns, infos, stats = rhythm_checks(shots, rows, 20, meta)
        self.assertEqual(stats['mode'], '表演')
        self.assertTrue(any(w.startswith('W24 表演档') for w in warns), warns)
        self.assertFalse(any(w.startswith(('W22', 'W23', 'W25', 'W26', 'W27', 'W28', 'W29')) for w in warns), warns)
        self.assertTrue(any('检查集 W24' in i and 'W30–W33' in i for i in infos))
        warns2, infos2, _ = rhythm_checks(shots, rows, 20, meta + '| 无声段理由 | 开头建立；结尾出画停留 |\n')
        self.assertEqual(warns2, [])
        self.assertTrue(any('已登记功能' in i for i in infos2))
        # the dialogue set is unchanged: the same wide window is W22 there
        warns3, infos3, _ = rhythm_checks(shots, rows, 20, meta + '| 节奏档 | 对话 |\n')
        self.assertTrue(any(w.startswith('W22') for w in warns3))
        self.assertTrue(any('检查集 W22–W29 + W30–W33' in i for i in infos3))

    def test_e_layer_overrides_mode_and_beats(self):
        shots = [(1, 0, 5, '【中景，固定】'), (2, 5, 10, '【中景，固定】')]
        rows = [row(1, 'A', 0, 4, 9), row(2, 'B', 5, 9, 9)]
        meta = META.replace('30', '10')
        self.assertEqual(scene_mode(meta + '| 节奏档 | 表演 |\n', 6, 10, 2, DEFAULTS), '表演')
        with self.assertRaises(ValueError):
            scene_mode(meta + '| 节奏档 | 快 |\n', 6, 10, 2, DEFAULTS)
        _, infos, stats = rhythm_checks(shots, rows, 10, meta + '| 动作节拍秒数 | 2 |\n')
        self.assertEqual(stats['derived'], 9)   # 3.5 + 3.5 + 0 + 2 = 9

    def test_w05_threshold_follows_fill_setting(self):
        from prompt_structure import Document, dialogue_checks
        text = '镜头1（0-4s）：【近景，固定】\n台词（A，0-4s，英语）："one two three four five six seven eight nine ten eleven"\n'
        doc = Document(text)
        _, w9, _, _ = dialogue_checks(doc, 4, (4.0, 3.0, 1.0))             # 3.67 > 3.6 -> W05
        _, w10, _, _ = dialogue_checks(doc, 4, (4.0, 3.0, 1.0), fill=1.0)   # 3.67 <= 4.0 -> clean
        self.assertTrue(any(w.startswith('W05') for w in w9))
        self.assertFalse(any(w.startswith('W05') for w in w10))

    def test_whole_line_in_fixed_four_second_shot_is_w28(self):
        shots = [(1, 0, 4, '【中景，固定】'), (2, 4, 6, '【近景，固定】'), (3, 6, 10, '【中景，缓推】')]
        rows = [row(1, 'A', 0, 4, 11), row(2, 'B', 4, 6, 5), row(3, 'A', 6, 10, 11)]
        warns, _, _ = rhythm_checks(shots, rows, 10, META.replace('30', '10'))
        self.assertTrue(any(w.startswith('W28 镜头1') for w in warns))
        self.assertFalse(any('镜头2' in w and w.startswith('W28') for w in warns))  # 2 s
        self.assertFalse(any('镜头3' in w and w.startswith('W28') for w in warns))  # camera moves

    def test_continuous_track_allows_spill_and_flags_pileup(self):
        rows = [row(1, 'A', 4, 6, 9), row(2, 'B', 6, 8, 3), row(3, 'A', 8, 10, 8)]   # 2.7 s in a 2 s window spills 0.7
        warns, finishes, slack = track_schedule(rows, 21, 1.0)
        self.assertEqual(warns, [])
        self.assertAlmostEqual(finishes[0], 7.0, places=1)   # 9 words / 3 = 3.0 s from 4
        rows2 = [row(1, 'A', 4, 6, 15), row(2, 'B', 6, 8, 3)]                     # 5 s from 4 -> 9, pileup 3 s
        warns2, _, _ = track_schedule(rows2, 21, 1.0)
        self.assertTrue(any(w.startswith('W29') for w in warns2))
        warns3, _, _ = track_schedule([row(1, 'A', 18, 20, 12)], 20, 1.0)          # 4 s from 18 > 20
        self.assertTrue(any('片长' in w for w in warns3))

    def test_track_mode_setting_and_track_sum_derivation(self):
        self.assertEqual(track_mode(META), '连续')             # dialogue-led default
        self.assertEqual(track_mode(META, '表演'), '窗口')
        self.assertEqual(track_mode(META + '| 台词轨 | 窗口 |\n'), '窗口')
        with self.assertRaises(ValueError):
            track_mode(META + '| 台词轨 | 快 |\n')
        shots = [(1, 0, 2, '【中景，固定】'), (2, 2, 4, '【近景，固定】'), (3, 4, 6, '【近景，固定】'), (4, 6, 8, '【近景，固定】')]
        rows = [row(2, 'A', 2, 4, 8), row(3, 'B', 4, 6, 8), row(4, 'A', 6, 8, 8)]   # 24 words = 8.0 s track
        _, infos, stats = rhythm_checks(shots, rows, 8, META.replace('30', '8') + '| 台词填充率 | 1.0 |\n')   # no 台词轨 field: dialogue-led -> 连续
        self.assertEqual(stats['derived'], 10)   # ceil(8.0 + 2 silent) — not 3 x ceil(2.67)=9 + 2 = 11
        self.assertEqual(stats['track_mode'], '连续')


# ---------- 1.12.0: user rhythm baseline (rhythm_baseline.py, R01-R04 / W38) and W28 for several lines ----------
from rhythm_baseline import baseline_checks, load_profile, BASELINE  # noqa: E402

FIXTURE = ROOT / 'tests' / 'fixtures' / 'rhythm' / 'offset-ep01-s04-clip01-v4.prompt.md'


def rrow(shot, speaker, start, end, words, text=None, rate=4.0):
    return {'speaker': speaker, 'text': text or ('x ' * words).strip() + '.', 'start': float(start), 'end': float(end),
            'estimate': words / rate, 'explicit': True, 'shot': str(shot)}


def codes(items, prefix):
    return [x for x in items if x.startswith(prefix)]


# Offset EP01 s04 v4 as shots and lines (words at 4 w/s): 2/2/2/6/2/6 s, 3 s silent head, ~2.8 s silent tail.
S04_SHOTS = [(1, 0, 2, '【近景，胸以上，侧跟拍，平视】【变化：景别 近｜机位 侧跟｜光 白光｜幅度 3】'),
             (2, 2, 4, '【中景，腰以上，正面，平视，固定】【变化：景别 近→中｜机位 侧跟→正面固定｜光 =｜幅度 3→2】'),
             (3, 4, 6, '【中近景，胸以上，正侧面，平视，固定】【变化：景别 中→中近｜机位 正面→正侧面｜光 暖→侧逆｜幅度 2→1】'),
             (4, 6, 12, '【近景，头肩，3/4正面，平视，固定，长焦浅景深】【变化：景别 中近→近｜机位 正侧面→3/4正面｜光 侧逆→暖｜幅度 1→1】'),
             (5, 12, 14, '【中景，腰以上，正面，平视，固定】【变化：景别 近→中｜机位 3/4正面→正面｜光 暖→闪光｜幅度 1→1】'),
             (6, 14, 20, '【近景偏特写，正面，平视，长焦浅景深，随前倾缓推】【变化：景别 中→近偏特写｜机位 正面→随前倾缓推｜光 闪光→暖｜幅度 3→2】')]
S04_ROWS = [rrow(2, '记者甲', 3, 4, 3, "When you're not working,"),
            rrow(3, '记者甲', 4, 6, 7, 'do you still spend time alone together?'),
            rrow(4, 'Theo', 6, 10, 17, "We're really good friends. He texts me at two in the morning with notes on my work."),
            rrow(4, 'Theo', 11, 12, 5, 'Most of them are good.'),
            rrow(5, '记者乙', 12, 14, 6, 'Rhett just told us he picked you.'),
            rrow(6, '记者乙', 14, 17, 13, 'So — are you and Rhett together, or are you letting people believe that?')]
S04_META = ('| 项 | 值 |\n|---|---|\n| duration | 20 |\n| 语速词每秒 | 4 |\n| 台词填充率 | 1.0 |\n| 台词轨 | 连续 |\n'
            '| 节奏档 | 对话 |\n| 动作节拍秒数 | 5 |\n| 无声段理由 | 镜1 承接；镜2 物件行动；镜6 结尾峰值 |\n')


class BaselineTests(unittest.TestCase):
    """The user's baseline is the default for dialogue-led clips; violations are errors, not review hints."""

    def test_s04_layout_errors_on_both_long_shots_and_both_ends(self):
        errors, warns, infos, stats = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META)
        self.assertEqual(sorted(e.split()[1] for e in codes(errors, 'R01')), ['镜头4', '镜头6'])
        self.assertTrue(any(e.startswith('R02 开头 3.0s') for e in errors), errors)
        self.assertTrue(any(e.startswith('R02 结尾 2.8s') for e in errors), errors)   # chained: last line ends 17.25
        self.assertEqual(stats['status'], 'failed')
        self.assertTrue(any(i.startswith('节奏基准逐镜：') and '镜4 6s' in i and 'R01' in i for i in infos), infos)
        # the written 无声段理由 does not keep R02: the baseline has no reason path for it
        self.assertIn('无声段理由', S04_META)
        # the legacy review hints are still there, unchanged (W24 keeps its own threshold and wording)
        rw, _, _ = rhythm_checks(S04_SHOTS, S04_ROWS, 20, S04_META)
        self.assertTrue(any(w.startswith('W24 开头 3s 无台词 > 2s') for w in rw), rw)
        self.assertTrue(any(w.startswith('W28 镜头4 6s 固定机位承载 2 段台词 / 3 句') for w in rw), rw)

    def test_two_to_four_second_layout_with_chained_lines_passes(self):
        shots = [(1, 0, 2, '【中景，固定】'), (2, 2, 5, '【近景，固定】'), (3, 5, 8, '【近景，固定】'),
                 (4, 8, 10, '【特写，固定】'), (5, 10, 14, '【中近景，缓推】'), (6, 14, 16, '【近景，固定】')]
        rows = [rrow(1, 'A', 0.5, 2, 9), rrow(2, 'B', 2.8, 5, 9), rrow(3, 'A', 5, 8, 12),
                rrow(4, 'B', 8, 10, 8), rrow(5, 'A', 10, 14, 14), rrow(6, 'B', 14, 16, 5)]
        errors, warns, infos, stats = baseline_checks(shots, rows, 16, '| 项 | 值 |\n| 无声段理由 | 开头建立 |\n')
        self.assertEqual(errors, [])
        self.assertEqual(codes(warns, 'W38'), [])
        self.assertEqual(stats['status'], 'passed')
        # an ending silence of 1-2 s is allowed but must name its function (镜号 or 结尾) in 无声段理由
        short = rows[:-1] + [rrow(6, 'B', 14, 16, 3)]                       # ends 14.75 -> 1.25 s silent
        errors2, warns2, _, _ = baseline_checks(shots, short, 16, '| 项 | 值 |\n| 无声段理由 | 开头建立 |\n')
        self.assertEqual(errors2, [])
        self.assertTrue(any(w.startswith('W38 基准：结尾 1.2s') for w in warns2), warns2)
        _, warns3, _, _ = baseline_checks(shots, short, 16, '| 项 | 值 |\n| 无声段理由 | 开头建立；镜6 出画停留 |\n')
        self.assertEqual(codes(warns3, 'W38'), [])

    def test_long_shot_reason_must_name_the_shot_and_hold_on_it(self):
        # 运镜 holds on the push-in shot 6; 持续动作 does not hold on shot 4 (amplitude 1); a free reason is unreadable
        meta = S04_META + '| 长镜理由 | 镜6 运镜：随前倾缓推到嘴唇离话筒一寸；镜4 持续动作：Theo 说话；镜4 太重要了 |\n'
        errors, warns, infos, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, meta)
        self.assertEqual([e.split()[1] for e in codes(errors, 'R01')], ['镜头4'])
        self.assertTrue(any('长镜理由成立：镜头6 6s 运镜' in i for i in infos), infos)
        self.assertTrue(any('幅度 1' in w for w in codes(warns, 'W38')), warns)
        self.assertTrue(any('读不出' in w for w in codes(warns, 'W38')), warns)
        # 运镜 on a fixed shot does not hold
        errors2, warns2, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META + '| 长镜理由 | 镜4 运镜：推 |\n')
        self.assertIn('镜头4', ' '.join(codes(errors2, 'R01')))
        self.assertTrue(any('没有运镜' in w for w in warns2), warns2)
        # R02 is not touched by a long-shot reason
        self.assertEqual(len(codes(errors, 'R02')), 2)

    def test_long_line_type_needs_one_sentence_that_does_not_fit_four_seconds(self):
        shots = [(1, 0, 2, '【中景，固定】'), (2, 2, 7, '【近景，固定】'), (3, 7, 9, '【近景，固定】')]
        one = [rrow(1, 'A', 0, 2, 7), rrow(2, 'B', 2, 7, 18, 'x ' * 17 + 'y'), rrow(3, 'A', 7, 9, 7)]   # 18 words = 4.5 s
        meta = '| 项 | 值 |\n| 长镜理由 | 镜2 长句：一口气的质问 |\n'
        errors, _, infos, _ = baseline_checks(shots, one, 9, meta)
        self.assertEqual(codes(errors, 'R01'), [])
        self.assertTrue(any('长镜理由成立：镜头2 5s 长句' in i for i in infos))
        two = [one[0], rrow(2, 'B', 2, 7, 18, 'x ' * 8 + 'y. ' + 'x ' * 8 + 'y.'), one[2]]
        errors2, warns2, _, _ = baseline_checks(shots, two, 9, meta)
        self.assertTrue(codes(errors2, 'R01'))
        self.assertTrue(any('2 句' in w for w in warns2), warns2)

    def test_user_override_is_the_only_way_to_keep_r01_to_r03(self):
        meta = S04_META + '| 基准豁免 | 结尾 2.8 s：黑在问题上（用户指定 2026-09-26）；镜4 6s：两句一镜（用户指定）；开头 3 s：承接 |\n'
        errors, warns, infos, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, meta)
        self.assertFalse(any(e.startswith('R02 结尾') for e in errors), errors)
        self.assertTrue(any(e.startswith('R02 开头') for e in errors), errors)          # item without 用户指定
        self.assertEqual([e.split()[1] for e in codes(errors, 'R01')], ['镜头6'])
        self.assertTrue(any('没写「用户指定」' in w for w in warns), warns)
        self.assertTrue(any(i.startswith('基准豁免（用户指定）：结尾') for i in infos), infos)
        off, _, off_infos, stats = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META + '| 基准豁免 | 全部：试验版（用户指定 2026-09-27） |\n')
        self.assertEqual(off, [])
        self.assertEqual(stats['status'], 'off')

    def test_gaps_between_lines_warn_then_error(self):
        shots = [(1, 0, 3, '【中景，固定】'), (2, 3, 6, '【近景，固定】'), (3, 6, 9, '【近景，固定】'), (4, 9, 12, '【中景，固定】')]
        rows = [rrow(1, 'A', 0, 3, 8), rrow(2, 'B', 3.5, 6, 4), rrow(3, 'A', 6, 9, 4), rrow(4, 'B', 10, 12, 8)]
        # A 0-2 | gap 2-3.5 (1.5 s) | B 3.5-4.5 | A 6-7 (gap 1.5 s) | gap 7-10 (3 s) | B 10-12
        errors, warns, _, stats = baseline_checks(shots, rows, 12, '| 项 | 值 |\n')
        self.assertEqual(len(codes(errors, 'R03')), 1)
        self.assertIn('7.0–10.0s', codes(errors, 'R03')[0])
        self.assertEqual(len([w for w in warns if '句间空' in w]), 2)
        self.assertEqual(len(stats['gaps']), 3)

    def test_performance_declaration_on_a_dialogue_clip_is_r04(self):
        meta = S04_META.replace('| 节奏档 | 对话 |', '| 节奏档 | 表演 |')
        errors, _, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, meta)
        self.assertTrue(codes(errors, 'R04'))
        self.assertTrue(codes(errors, 'R01'))                       # checked as dialogue anyway
        ok, _, infos, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, meta + '| 基准豁免 | 节奏档 表演：长镜头测试（用户指定） |\n')
        self.assertEqual(ok, [])
        self.assertTrue(any('R01–R03 不查' in i for i in infos))
        # a clip that is performance-led by speech share reports INFO only (examples 01 / 05 / 06 stay clean)
        shots = [(1, 0, 8, '【中景，固定】'), (2, 8, 12, '【近景，固定】')]
        quiet, qwarns, qinfos, qstats = baseline_checks(shots, [rrow(2, 'A', 9, 11, 4)], 12, '| 项 | 值 |\n')
        self.assertEqual((quiet, codes(qwarns, 'W38'), qstats['status']), ([], [], 'not_applicable'))
        self.assertTrue(any('镜1 8s' in i for i in qinfos))

    def test_e_layer_tightens_but_cannot_loosen(self):
        loose = S04_META + '| 镜长上限 | 6 |\n| 首尾无声上限 | 3 |\n'
        errors, warns, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, loose)
        self.assertEqual(len(codes(errors, 'R01')), 2)
        self.assertEqual(len(codes(errors, 'R02')), 2)
        self.assertEqual(len([w for w in warns if '只能收紧' in w]), 2)
        tight, _, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META + '| 镜长上限 | 1.5 |\n')
        self.assertEqual(len(codes(tight, 'R01')), 6)

    def test_speech_rate_below_floor_needs_a_stated_delivery(self):
        slow = S04_META.replace('| 语速词每秒 | 4 |', '| 语速词每秒 | 3 |')
        _, warns, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, slow)
        self.assertTrue(any('语速词每秒 3 <' in w for w in warns), warns)
        _, warns2, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, slow + '| 语速理由 | 念定稿，一字一顿 |\n')
        self.assertFalse(any('语速词每秒 3 <' in w for w in warns2))

    def test_project_profile_is_found_upward_and_loosening_needs_the_user(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / 'ep01' / '06_prompts' / 'x.prompt.md'
            prompt.parent.mkdir(parents=True)
            prompt.write_text('镜头1（0-2s）：【近景，固定】A 抬眼。\n', encoding='utf-8')
            self.assertIsNone(load_profile(prompt))
            (root / 'production-profile.md').write_text('# 档案\n\n| 字段 | 约定 |\n|---|---|\n| 节奏 | 2–4 秒 |\n', encoding='utf-8')
            self.assertIsNone(load_profile(prompt))                  # no 节奏基准项 table: not a rhythm profile
            (root / 'rhythm-profile.md').write_text('| 节奏基准项 | 值 |\n|---|---|\n| 镜长上限 | 6 |\n| 首尾无声上限 | 3 |\n',
                                                     encoding='utf-8')
            profile = load_profile(prompt)
            self.assertTrue(profile['path'].endswith('rhythm-profile.md'))
            errors, warns, _, _ = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META, profile)
            self.assertEqual(len(codes(errors, 'R01')), 2)          # loosening without the user is ignored
            self.assertTrue(any('来源」没写用户决定' in w for w in warns), warns)
            (root / 'rhythm-profile.md').write_text('| 节奏基准项 | 值 |\n|---|---|\n| 镜长上限 | 6 |\n| 首尾无声上限 | 3 |\n'
                                                     '| 来源 | 用户 2026-09-27 定 |\n', encoding='utf-8')
            errors, _, infos, stats = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META, load_profile(prompt))
            self.assertEqual(errors, [])
            self.assertEqual(stats['values']['镜长上限'], 6.0)
            (root / 'ep01' / 'rhythm-profile.md').write_text('| 节奏基准项 | 值 |\n|---|---|\n| 基准 | 关 |\n| 来源 | 用户 |\n',
                                                               encoding='utf-8')
            self.assertTrue(load_profile(prompt)['path'].endswith('ep01/rhythm-profile.md'))   # nearest wins
            _, _, _, stats = baseline_checks(S04_SHOTS, S04_ROWS, 20, S04_META, load_profile(prompt))
            self.assertEqual(stats['status'], 'off')
        self.assertEqual(BASELINE['镜长上限'], 4.0)

    def test_s04_fixture_end_to_end(self):
        from validate_prompt import validate
        result = validate(FIXTURE)
        self.assertEqual([e for e in result['errors'] if not e.startswith('R')], [])
        self.assertEqual(result['checks']['format'], 'passed')
        self.assertEqual(result['checks']['rhythm_baseline'], 'failed')
        self.assertEqual(sorted(e.split()[1] for e in codes(result['errors'], 'R01')), ['镜头4', '镜头6'])
        self.assertEqual(len(codes(result['errors'], 'R02')), 2)
        self.assertTrue(any(w.startswith('W28 镜头4') for w in result['warnings']))
        self.assertTrue(any(w.startswith('W24') for w in result['warnings']))    # W24 unchanged beside R02


class SeveralLinesW28Tests(unittest.TestCase):
    def test_fixed_shot_holding_several_lines_or_sentences_is_w28(self):
        shots = [(1, 0, 5, '【中景，固定】'), (2, 5, 10, '【近景，固定】'), (3, 10, 15, '【近景，缓推】'), (4, 15, 18, '【中景，固定】')]
        rows = [row(1, 'A', 0, 3, 6), row(1, 'B', 3, 5, 5),                                   # two lines fill shot 1
                {**row(2, 'A', 5, 9, 11), 'text': 'You said nine. You came at ten.'},       # one line, two sentences, 4 of 5 s
                row(3, 'B', 10, 12, 5), row(3, 'A', 12, 15, 8),                               # camera moves
                row(4, 'B', 15, 16, 3), row(4, 'A', 16, 18, 5)]                               # 3 s shot
        warns, _, _ = rhythm_checks(shots, rows, 18, META.replace('30', '18'))
        w28 = [w for w in warns if w.startswith('W28')]
        self.assertTrue(any(w.startswith('W28 镜头1 5s 固定机位承载 2 段台词') for w in w28), w28)
        self.assertTrue(any(w.startswith('W28 镜头2 5s 固定机位承载 1 段台词 / 2 句') for w in w28), w28)
        self.assertFalse(any('镜头3' in w or '镜头4' in w for w in w28), w28)

    def test_original_single_line_w28_wording_is_kept(self):
        shots = [(1, 0, 4, '【中景，固定】'), (2, 4, 6, '【近景，固定】')]
        warns, _, _ = rhythm_checks(shots, [row(1, 'A', 0, 4, 11), row(2, 'B', 4, 6, 5)], 6, META.replace('30', '6'))
        self.assertIn('W28 镜头1 4s 固定机位只承载一整句（A）：在信息变化处切——前半句画内、后半句画外落在听者 / 插入 / 视线对象，或换景别（duration-rhythm §九）', warns)

    def test_sentence_count(self):
        from rhythm_checks import sentence_count
        self.assertEqual(sentence_count("We're really good friends. He texts me at two in the morning with notes on my work."), 2)
        self.assertEqual(sentence_count('So — are you and Rhett together, or are you letting people believe that?'), 1)
        self.assertEqual(sentence_count('你上个月也是六点的飞机。你每次都是六点的飞机。'), 2)
        self.assertEqual(sentence_count('Mr. Hale, sit down.'), 1)


class BaselineWiringTests(unittest.TestCase):
    """The baseline is wired through SKILL, S5, S7, templates and duration-rhythm; earlier clauses stay."""

    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_new_clauses_are_present(self):
        skill = self.read('SKILL.md')
        for token in ('R01–R04', '基准豁免', '长镜理由', 'rhythm-profile.md'):
            self.assertTrue(token in skill, token)
        self.assertTrue('整条重核' in skill, '整条重核')
        dr = self.read('references/duration-rhythm.md')
        for token in ('## 十二', 'R01', 'R02', 'R03', 'R04', 'W38', '节奏基准项', 'D07b'):
            self.assertTrue(token in dr, token)
        s5 = self.read('references/stage-5-directing-storyboard.md')
        self.assertTrue('逐镜核对节奏基准' in s5, '逐镜核对节奏基准')
        s7 = self.read('references/stage-7-qa-continuity.md')
        self.assertTrue('整条重核' in s7, '整条重核')
        self.assertTrue('R01–R04' in s7, 'R01–R04')
        self.assertTrue('节奏基准核对' in self.read('templates/shot-card.md'), '节奏基准核对')
        self.assertTrue('长镜理由' in self.read('templates/prompt-templates.md'), '长镜理由')

    def test_earlier_clauses_are_kept(self):
        dr = self.read('references/duration-rhythm.md')
        self.assertTrue('一镜多句（走位中的连续交锋）可 5–8 s，在 A 层写"为什么不能切"' in dr, '一镜多句（走位中的连续交锋）可 5–8 s，在 A 层写"为什么不能切"')
        self.assertTrue('超出报 W24，写理由即可保留' in dr, '超出报 W24，写理由即可保留')
        self.assertTrue('W30' in dr, 'W30')
        self.assertTrue('WARN 逐条写"保留理由"或修改' in self.read('references/stage-7-qa-continuity.md'), 'WARN 逐条写"保留理由"或修改')
        skill = self.read('SKILL.md')
        self.assertTrue('写明理由才保留' in skill, '写明理由才保留')
        self.assertTrue('变化轨' in skill, '变化轨')
        self.assertTrue('W22–W29' in skill, 'W22–W29')


if __name__ == '__main__':
    unittest.main()
