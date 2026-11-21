"""W54 / W55 (speaker_checks.py): a line carried across two shots, and an off-screen line over another character's face.
1.11.0 banned both; 1.16.0 (references/shot-requirements.md R1, user decision 2026-11-21) treats off-screen sound as an
ordinary technique and checks that the off-screen segment is written out in full: whose voice, the visible listener's
mouth closed, the line-count and exclusion sentences in 【贯穿要求】. A complete one is an INFO."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from test_render_lessons import build, run, codes, SHOT1, SHOT2, SHOT3, GLOBAL, E  # noqa: E402

# A speaks in shot 1; the tail of the same line is written 画外 on B's close-up in shot 2 (the v1.6 shape).
SPLIT1 = ('镜头1（0-3s）：【近景，正对门，轻微手持，焦点在 A】画面深处是走廊尽头的门。A 在画面中间，门在他的画左。'
          '台词（A，1-3s，英语，随口）："Your stuff is on the rack."；此时 B 闭着嘴。话说到这里就切。\n')
SPLIT2 = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】画面深处是走廊尽头的门。B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，嘴角带着笑。'
          'A 的后半句从画外接上。台词（A，3-4s，英语，画外，同一个声音接上）："The black one."；此时 B 闭着嘴。\n')
# Whole off-screen line on B's face, no conditions written.
OFF_WHOLE = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】画面深处是走廊尽头的门。B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，眉毛一抬。'
             '台词（A，3-5s，英语，画外，随口）："Your stuff is on the rack, the black one."；此时 B 在听。\n')
# Project whole-line off-screen shot: ≥3 s, whole line, listener's mouth closed, exclusion sentence in GLOBAL.
OFF_OK = ('镜头2（3-6s）：【中景，正对门，轻微手持，焦点在 B】画面深处是走廊尽头的门。B（@B-基础形象，穿 @01_B_outfit）在画面中间，脸朝画左，眉毛一抬。'
          '台词（A，3-5s，英语，画外，随口）："Your stuff is on the rack, the black one."；此时 B 闭着嘴，在听。\n')
GLOBAL_EXCL = GLOBAL.replace('声音：', '全条只有这两句台词，此外没有人说话；排除错误人物发声、多人同时说话。声音：')
# Off-screen line with no other face: an object insert.
OFF_OBJECT = '镜头2（3-6s）：【特写，衣架上的黑色礼服，固定】画面深处是衣架后的墙。衣架上三件分开挂着。台词（A，3-5s，英语，画外，随口）："The black one."\n'
SHOT3B = SHOT3.replace('镜头3（6-9s）', '镜头3（6-9s）')


class SplitTests(unittest.TestCase):
    def test_cut_to_listener_not_written_in_full_is_w54(self):
        result = run(build(shots=(SPLIT1, SPLIT2, SHOT3B)))
        self.assertEqual(result['errors'], [], result['errors'])
        w54 = codes(result, 'W54')
        self.assertEqual(len(w54), 1, w54)
        self.assertIn('镜头1→镜头2', w54[0])
        self.assertIn('句中切听者', w54[0])
        self.assertIn('画外段还没写全', w54[0])
        self.assertIn('排除错误人物发声', w54[0])
        self.assertIn('只有这 N 句台词', w54[0])
        self.assertEqual(codes(result, 'W55'), [], 'the carried segment is reported once, by W54')

    def test_cut_to_listener_written_in_full_is_info(self):
        result = run(build(shots=(SPLIT1, SPLIT2, SHOT3B), global_rules=GLOBAL_EXCL))
        self.assertEqual(codes(result, 'W54') + codes(result, 'W55'), [], result['warnings'])
        self.assertTrue(any(i.startswith('画外段 镜头1→镜头2') and '句中切听者' in i for i in result['info']), result['info'])

    def test_two_finished_sentences_are_not_a_split(self):
        """A speaks a whole sentence on camera, then another whole sentence off-screen over B: that is a 画外整句 (W55)."""
        shot2 = SPLIT2.replace('A 的后半句从画外接上。', '').replace('画外，同一个声音接上', '画外音')
        result = run(build(shots=(SPLIT1, shot2, SHOT3B)))
        self.assertEqual(codes(result, 'W54'), [], result['warnings'])
        self.assertEqual(len(codes(result, 'W55')), 1, result['warnings'])

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
        self.assertTrue(any(i.startswith('画外整句') and '写法齐' in i for i in result['info']), result['info'])

    def test_short_shot_is_fine_when_written_in_full(self):
        """1.16.0: the ≥3 s floor of the old 画外整句镜 exception is gone; an off-screen segment is meant to be short."""
        short = OFF_OK.replace('镜头2（3-6s）', '镜头2（3-5s）').replace('3-5s，英语', '3-5s，英语')
        shot3 = SHOT3B.replace('镜头3（6-9s）', '镜头3（5-9s）')
        result = run(build(shots=(SHOT1, short, shot3), global_rules=GLOBAL_EXCL))
        self.assertEqual(codes(result, 'W55'), [], result['warnings'])

    def test_missing_line_count_sentence_is_named(self):
        glob = GLOBAL.replace('声音：', '排除错误人物发声、多人同时说话。声音：')
        w55 = codes(run(build(shots=(SHOT1, OFF_OK, SHOT3B), global_rules=glob)), 'W55')
        self.assertTrue(w55 and '只有这 N 句台词' in w55[0] and '排除错误人物发声' not in w55[0].split('还没写全：')[1], w55)

    def test_voice_over_needs_the_lips_closed(self):
        vo = ('镜头2（3-6s）：【近景，正对门，固定，焦点在 B】画面深处是走廊尽头的门。B（@B-基础形象，穿 @01_B_outfit）在画面中间，低头看着手里的票。'
              '台词（B，V.O.，3-5s，英语）："I can do this."\n')
        w55 = codes(run(build(shots=(SHOT1, vo, SHOT3B), global_rules=GLOBAL_EXCL)), 'W55')
        self.assertTrue(w55 and 'V.O.' in w55[0] and '嘴唇闭合' in w55[0], w55)
        closed = vo.replace('低头看着手里的票。', '低头看着手里的票，嘴唇闭合。')
        self.assertEqual(codes(run(build(shots=(SHOT1, closed, SHOT3B), global_rules=GLOBAL_EXCL)), 'W55'), [])

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

    def test_w54_w55_are_no_longer_render_lessons(self):
        result = run(build(shots=(SPLIT1, SPLIT2, SHOT3B)))
        lesson = [i for i in result['info'] if i.startswith('成片教训类提醒')]
        self.assertFalse(any('W54' in i or 'W55' in i for i in lesson), lesson)  # 1.16.0: ordinary WARNs, not render lessons


if __name__ == '__main__':
    unittest.main()
