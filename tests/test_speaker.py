"""1.11.0 W54 / W55 (speaker_checks.py): a line split across two shots, and an off-screen line landing on another
character's face. Trigger `[实测]` offset EP06 s02 clip01 v1.6: "The black one." written 画外 on Theo's shot was spoken by Theo."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from test_render_lessons import build, run, codes, SHOT1, SHOT2, SHOT3, GLOBAL, E  # noqa: E402

# A speaks in shot 1; the tail of the same line is written 画外 on B's close-up in shot 2 (the v1.6 shape).
SPLIT1 = ('镜头1（0-3s）：【近景，正对门，轻微手持，焦点在 A】A 在画面中间，门在他的画左。'
          '台词（A，1-3s，英语，随口）："Your stuff is on the rack."；此时 B 闭着嘴。话说到这里就切。\n')
SPLIT2 = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，嘴角带着笑。'
          'A 的后半句从画外接上。台词（A，3-4s，英语，画外，同一个声音接上）："The black one."；此时 B 闭着嘴。\n')
# Whole off-screen line on B's face, no conditions written.
OFF_WHOLE = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，眉毛一抬。'
             '台词（A，3-5s，英语，画外，随口）："Your stuff is on the rack, the black one."；此时 B 在听。\n')
# Project whole-line off-screen shot: ≥3 s, whole line, listener's mouth closed, exclusion sentence in GLOBAL.
OFF_OK = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，眉毛一抬。'
          '台词（A，3-5s，英语，画外，随口）："Your stuff is on the rack, the black one."；此时 B 闭着嘴，在听。\n')
GLOBAL_EXCL = GLOBAL.replace('声音：', '排除错误人物发声、多人同时说话。声音：')
# Off-screen line with no other face: an object insert.
OFF_OBJECT = '镜头2（3-6s）：【特写，衣架上的黑色礼服，固定】衣架上三件分开挂着。台词（A，3-5s，英语，画外，随口）："The black one."\n'
SHOT3B = SHOT3.replace('镜头3（6-9s）', '镜头3（6-9s）')


class SplitTests(unittest.TestCase):
    def test_tail_off_screen_on_next_shot_is_w54_and_w55(self):
        result = run(build(shots=(SPLIT1, SPLIT2, SHOT3B)))
        self.assertEqual(result['errors'], [], result['errors'])
        w54 = codes(result, 'W54')
        self.assertEqual(len(w54), 1, w54)
        self.assertIn('镜头1→镜头2', w54[0])
        self.assertIn('A', w54[0])
        w55 = codes(result, 'W55')
        self.assertEqual(len(w55), 1, w55)
        self.assertIn('B 的脸', w55[0])
        self.assertIn('不是整句', w55[0])

    def test_spill_wording_is_w54(self):
        shot1 = SPLIT1.replace('话说到这里就切。', '这句的最后几个词落在下一镜的开头。')
        result = run(build(shots=(shot1, SHOT2, SHOT3B)))
        w54 = codes(result, 'W54')
        self.assertTrue(w54 and '溢出' in w54[0], w54)

    def test_clean_fixture_has_neither(self):
        result = run(build())
        self.assertEqual(codes(result, 'W54'), [])
        self.assertEqual(codes(result, 'W55'), [])


class OffScreenTests(unittest.TestCase):
    def test_whole_off_screen_line_on_other_face_is_w55_listing_missing_conditions(self):
        result = run(build(shots=(SHOT1, OFF_WHOLE, SHOT3B)))
        w55 = codes(result, 'W55')
        self.assertEqual(len(w55), 1, w55)
        self.assertIn('没写B闭着嘴', w55[0])
        self.assertIn('排除错误人物发声', w55[0])
        self.assertEqual(codes(result, 'W54'), [])

    def test_project_whole_line_shot_downgrades_to_info(self):
        result = run(build(shots=(SHOT1, OFF_OK, SHOT3B), global_rules=GLOBAL_EXCL))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])
        self.assertTrue(any('画外整句镜' in i for i in result['info']), result['info'])

    def test_short_shot_keeps_w55_even_with_conditions(self):
        short = OFF_OK.replace('镜头2（3-6s）', '镜头2（3-5s）').replace('3-5s，英语', '3-5s，英语')
        shot3 = SHOT3B.replace('镜头3（6-9s）', '镜头3（5-9s）')
        result = run(build(shots=(SHOT1, short, shot3), global_rules=GLOBAL_EXCL))
        w55 = codes(result, 'W55')
        self.assertTrue(w55 and '镜长 2s < 3s' in w55[0], w55)

    def test_min_shot_is_tunable(self):
        short = OFF_OK.replace('镜头2（3-6s）', '镜头2（3-5s）')
        shot3 = SHOT3B.replace('镜头3（6-9s）', '镜头3（5-9s）')
        result = run(build(shots=(SHOT1, short, shot3), global_rules=GLOBAL_EXCL, e=E + '| 画外整句镜最短秒数 | 2 |\n'))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])

    def test_off_screen_line_on_an_object_insert_is_fine(self):
        result = run(build(shots=(SHOT1, OFF_OBJECT, SHOT3B)))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])

    def test_back_turned_listener_is_not_a_face(self):
        back = OFF_WHOLE.replace('脸朝画左，眉毛一抬', '背对镜头，只有后背')
        result = run(build(shots=(SHOT1, back, SHOT3B)))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])

    def test_narration_is_not_checked(self):
        narr = OFF_WHOLE.replace('画外，随口', '旁白')
        result = run(build(shots=(SHOT1, narr, SHOT3B)))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])

    def test_render_lesson_info_lists_the_codes(self):
        result = run(build(shots=(SPLIT1, SPLIT2, SHOT3B)))
        lesson = [i for i in result['info'] if i.startswith('成片教训类提醒')]
        self.assertTrue(lesson and 'W54' in lesson[0] and 'W55' in lesson[0], lesson)


if __name__ == '__main__':
    unittest.main()
