"""1.12.0 W57 (layer_checks.py): A-layer vocabulary (emotion / judgment / intent words) leaking into the C / D layer.
Dictionary = the externalization lexicon's first column + its `## A 层词` section. Trigger `[实测]` offset EP06 s02 clip02 v3:
the bracket "觉得不可思议" and the prose "一脸不信" rendered as a confrontation in a light scene."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from layer_checks import load_vocabulary, scan_text  # noqa: E402
from test_render_lessons import build, run, codes, SHOT1, SHOT2, SHOT3, OVERVIEW, GLOBAL  # noqa: E402


class DictionaryTests(unittest.TestCase):
    def test_vocabulary_comes_from_the_lexicon(self):
        vocab = load_vocabulary()
        for w in ('悲伤', '惊讶', '不可思议', '极度', '慌慌张张', '真诚', '得意'):
            self.assertIn(w, vocab, w)
        for voice in ('随口', '懒洋洋', '轻描淡写', '带笑'):
            self.assertNotIn(voice, vocab, voice)

    def test_shapes_and_negation(self):
        vocab = load_vocabulary()
        self.assertEqual(scan_text('他眉毛一抬，鼻子里笑出一口气。', vocab), [])
        self.assertIn('一脸无辜', scan_text('他举起手，一脸无辜。', vocab))
        self.assertIn('觉得不可思议', scan_text('台词（Theo，11-14s，英语，觉得不可思议）：“…”', vocab))
        self.assertEqual(scan_text('两人都不生气、不质问，没有惊讶。', vocab), [])


class PromptTests(unittest.TestCase):
    def test_bracket_emotion_word_is_w57_and_names_the_bracket(self):
        shot = SHOT3.replace('台词（A，6-8s，英语，平平的）', '台词（A，6-8s，英语，声音不高，觉得不可思议）')
        result = run(build(shots=(SHOT1, SHOT2, shot)))
        hits = codes(result, 'W57')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('镜头3', hits[0])
        self.assertIn('台词括号里', hits[0])
        self.assertTrue(any(i.startswith('成片教训类提醒') and 'W57' in i for i in result['info']), result['info'])

    def test_prose_judgment_word_is_w57(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '他眉头一皱，一脸不信地看着画左的门。')
        hits = codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W57')
        self.assertTrue(hits and '一脸不信' in hits[0], hits)

    def test_voice_words_and_visible_beats_are_clean(self):
        shot = SHOT3.replace('台词（A，6-8s，英语，平平的）', '台词（A，6-8s，英语，随口，带笑）').replace('嘴角撇一下', '眉毛一抬，鼻子里笑出一口气')
        self.assertEqual(codes(run(build(shots=(SHOT1, SHOT2, shot))), 'W57'), [])

    def test_tone_words_in_overview_and_global_rules_are_not_scanned(self):
        overview = OVERVIEW.replace('整条轻松、生活化。', '整条轻松、愉快，两人都不生气；Theo 心虚，Rhett 得意。')
        glob = GLOBAL.replace('声音：', '表演约束：两人都不生气、不质问；不写惊讶。声音：')
        self.assertEqual(codes(run(build(overview=overview, global_rules=glob)), 'W57'), [])

    def test_examples_are_clean(self):
        from validate_prompt import validate
        for name in ('example-01-kitchen-keys', 'example-02-lens-B-haneke', 'example-03-yogurt-comedy',
                     'example-05-stairwell-letter', 'example-06-balcony-cigarette'):
            result = validate(ROOT / 'examples' / f'{name}.prompt.md')
            self.assertEqual([w for w in result['warnings'] if w.startswith('W57')], [], name)


if __name__ == '__main__':
    unittest.main()
