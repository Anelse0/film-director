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

    def test_performance_led_clip_only_reports_info(self):
        shots = [(1, 0, 20, '【中景，固定】')]
        rows = [row(1, 'A', 6, 8, 3)]
        warns, infos, _ = rhythm_checks(shots, rows, 20, META.replace('30', '20'))
        self.assertEqual(warns, [])
        self.assertTrue(any('节奏档 表演' in i for i in infos))

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


if __name__ == '__main__':
    unittest.main()
