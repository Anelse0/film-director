"""1.9.0 W46-W49 (wording_checks.py), W51 (continuity_checks.py), W52 (viewpoint_checks.py): wording the model executed
literally in the offset EP06 s01 clip01 / clip02 renders. 1.10.0: the closing INFO for the render-lesson warning class
(W50 per-shot action load was paused by the user; draft and tests parked outside the repo). Fixtures are placeholder corridor prompts (A / B) in the EP06
shape: A stands by the end-wall door, B walks in holding a phone. Wiring lives in test_release_190.py."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_prompt import validate  # noqa: E402

REFS = ('【素材绑定】\n@A-基础形象：A 的人物参考，只参考面部与发型。A 的衣着一律按 @01_A_outfit。\n@01_A_outfit：A 身上唯一的服装。\n'
        '@B-基础形象：B 的人物参考，只参考面部与发型。B 的衣着一律按 @01_B_outfit。\n@01_B_outfit：B 身上唯一的服装。\n'
        '@01_hall：走廊的空间、陈设、材质与光色参考：尽头正中一扇门，门左右各一截窄墙。人物站位以门右边那截窄墙为准：人站在那里时，门在他的画左。\n')
OVERVIEW = '【总述】9秒3:4竖屏，走廊（@01_hall），B 走来跟 A 说一句话。整条轻松、生活化。声音：无 bgm，只有环境音与台词。\n【画面基调】暖光，深景深。\n'
OPENING = '【起始状态】A（@A-基础形象，穿 @01_A_outfit）站在门右边那截窄墙前，门在他的画左。\n'
SHOT1 = '镜头1（0-3s）：【近景，正对门，轻微手持，焦点在 A】A 在画面中间，门在他的画左。他抬眼看着画左的门。\n'
SHOT2 = ('镜头2（3-6s）：【中景双人，正对门，轻微手持，焦点在 B】B（@B-基础形象，穿 @01_B_outfit）从画左前景入画，停在 A 前方。'
         '台词（B，3-5s，英语，随口）："You good?"；此时 A 闭着嘴。\n')
SHOT3 = '镜头3（6-9s）：【近景，正对门，轻微手持，焦点在 A】A 在画面中间，嘴角撇一下。台词（A，6-8s，英语，平平的）："Fine."；此时 B 闭着嘴。\n'
GLOBAL = ('【贯穿要求】保持一致：A、B 的脸和衣着与参考图一致。空间与机位：门在 A 的画左。'
          '声音：A 是 21 岁男声，偏低；B 是 25 岁女声，干脆。无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音与台词；不要字幕。\n')
E = '\n| 项 | 值 |\n|---|---|\n| duration | 9 |\n| 上传与角色 | @A-基础形象、@01_A_outfit、@B-基础形象、@01_B_outfit、@01_hall |\n'


def build(refs=REFS, overview=OVERVIEW, opening=OPENING, shots=(SHOT1, SHOT2, SHOT3), global_rules=GLOBAL, e=E):
    return refs + overview + opening + '【分镜时间线】\n' + ''.join(shots) + global_rules + e


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def codes(result, code):
    return [w for w in result['warnings'] if w.startswith(code)]


class BaselineTests(unittest.TestCase):
    def test_clean_fixture_has_none_of_the_new_codes(self):
        result = run(build())
        self.assertEqual(result['errors'], [], result['errors'])
        for code in ('W46', 'W47', 'W48', 'W49', 'W51', 'W52'):
            self.assertEqual(codes(result, code), [], code)


class SideWordTests(unittest.TestCase):
    def test_body_side_as_screen_position(self):
        shot = SHOT1.replace('门在他的画左。', '门框就在他右肩旁边，名牌在他头的右边。')
        hits = codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W46')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('右肩', hits[0])
        self.assertIn('头的右边', hits[0])

    def test_frame_side_in_the_same_clause_anchors_it(self):
        shot = SHOT1.replace('门在他的画左。', '门框在他右肩旁边的画左一侧。')
        self.assertEqual(codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W46'), [])

    def test_step_toward_own_side(self):
        shot = SHOT1.replace('他抬眼', '他往左挪一步，抬眼')
        hits = codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W46')
        self.assertTrue(hits and '往左挪' in hits[0], hits)

    def test_over_shoulder_side_must_match_corner(self):
        bad = '镜头1（0-3s）：【近景，过 A 的右肩，轻微手持，焦点在 B】画左下角是 A 虚化的右肩，只占一小块；B 在画面中间。\n'
        good = bad.replace('画左下角', '画右下角')
        hits = codes(run(build(shots=(bad, SHOT2, SHOT3))), 'W46')
        self.assertTrue(any('过肩镜' in h for h in hits), hits)
        self.assertEqual(codes(run(build(shots=(good, SHOT2, SHOT3))), 'W46'), [])

    def test_landmark_side_defined_in_binding_is_fine_undefined_is_not(self):
        self.assertEqual(codes(run(build()), 'W46'), [])
        shot = SHOT3.replace('A 在画面中间，', 'A 在画面中间，身后是走廊左侧的墙纸，')
        hits = codes(run(build(shots=(SHOT1, SHOT2, shot))), 'W46')
        self.assertTrue(hits and '走廊左侧' in hits[0], hits)

    def test_holding_hand_is_not_a_position(self):
        shot = SHOT2.replace('停在 A 前方。', '停在 A 前方，右手拿着手机，正常握法：四指托在背面。')
        self.assertEqual(codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W46'), [])

    def test_rule_sentence_is_not_reported(self):
        glob = GLOBAL.replace('门在 A 的画左。', '门在 A 的画左。画面里的左右一律指画左、画右，不指人物自己的左右手、左右肩。')
        self.assertEqual(codes(run(build(global_rules=glob)), 'W46'), [])


class DeliveryTests(unittest.TestCase):
    def test_speed_word_in_bracket(self):
        shot = SHOT2.replace('英语，随口）', '英语，随口，语速快）')
        hits = codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W47')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('语速快', hits[0])

    def test_covering_the_mic_in_bracket(self):
        shot = SHOT2.replace('英语，随口）', '英语，捂着话筒压低声音，飞快）')
        hits = codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W47')
        self.assertTrue(hits and '飞快' in hits[0] and '捂着话筒' in hits[0], hits)

    def test_negated_speed_is_fine_and_soft_words_are_info(self):
        shot = SHOT2.replace('英语，随口）', '英语，随口，语速自然，不赶）')
        result = run(build(shots=(SHOT1, shot, SHOT3)))
        self.assertEqual(codes(result, 'W47'), [])
        self.assertTrue(any(i.startswith('台词括号里的语速') for i in result['info']), result['info'])

    def test_fast_voice_line(self):
        glob = GLOBAL.replace('B 是 25 岁女声，干脆。', 'B 是 25 岁女声，干脆、快。')
        hits = codes(run(build(global_rules=glob)), 'W47')
        self.assertTrue(hits and '女声' in hits[0], hits)

    def test_light_timbre_is_not_speed(self):
        glob = GLOBAL.replace('B 是 25 岁女声，干脆。', 'B 是 25 岁女声，轻快。')
        self.assertEqual(codes(run(build(global_rules=glob)), 'W47'), [])


class HandTests(unittest.TestCase):
    def test_held_phone_without_grip(self):
        shot = SHOT2.replace('停在 A 前方。', '停在 A 前方，拿着手机。')
        hits = codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W48')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('手机', hits[0])

    def test_grip_in_shot_or_hand_line_is_fine(self):
        shot = SHOT2.replace('停在 A 前方。', '停在 A 前方，右手拿着手机，正常握法：四指托在背面。')
        self.assertEqual(codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W48'), [])
        loose = SHOT2.replace('停在 A 前方。', '停在 A 前方，拿着手机。')
        glob = GLOBAL + '手：B 从头到尾只用右手拿手机，四指托在背面，拇指在屏幕一侧。\n'
        self.assertEqual(codes(run(build(shots=(SHOT1, loose, SHOT3), global_rules=glob)), 'W48'), [])

    def test_covering_the_mouthpiece(self):
        shot = SHOT2.replace('停在 A 前方。', '停在 A 前方，右手正常握着手机，一只手捂住手机话筒。')
        hits = codes(run(build(shots=(SHOT1, shot, SHOT3))), 'W48')
        self.assertTrue(hits and '捂嘴' in hits[0], hits)


class ActingTests(unittest.TestCase):
    def test_flustered_words_in_a_light_clip(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '他慌慌张张往后退，牙关一咬。')
        hits = codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W49')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('慌慌张张', hits[0])

    def test_comedy_declared_is_info(self):
        overview = OVERVIEW.replace('整条轻松、生活化。', '整条是喜剧。')
        shot = SHOT1.replace('他抬眼看着画左的门。', '他瞪大眼睛。')
        result = run(build(overview=overview, shots=(shot, SHOT2, SHOT3)))
        self.assertEqual(codes(result, 'W49'), [])
        self.assertTrue(any(i.startswith('表演幅度词') for i in result['info']), result['info'])

    def test_negated_is_fine(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '他只是一愣，不瞪眼、不张大嘴。')
        self.assertEqual(codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W49'), [])


class ContinuityTests(unittest.TestCase):
    E_CHAIN = E + '| 上游 clip | clip01 尾帧接首帧（clip01 成片末帧） |\n'

    def test_first_shot_replays_the_previous_beat(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '0-1s 他还看着镜头右侧的远处，没人答。')
        hits = codes(run(build(shots=(shot, SHOT2, SHOT3), e=self.E_CHAIN)), 'W51')
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('没人答', hits[0])

    def test_continuing_motion_is_fine(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '他没等到回答，闭上嘴，拽平西装，转身朝向画左的门。')
        self.assertEqual(codes(run(build(shots=(shot, SHOT2, SHOT3), e=self.E_CHAIN)), 'W51'), [])

    def test_no_upstream_no_check(self):
        shot = SHOT1.replace('他抬眼看着画左的门。', '他还看着远处，没人答。')
        self.assertEqual(codes(run(build(shots=(shot, SHOT2, SHOT3))), 'W51'), [])


class ViewpointTests(unittest.TestCase):
    ROOM = '@01_room：化妆间的材质与光色参考，只用在镜头3：胡桃木墙板、暖色柔光。不参考这张图的视角和构图。\n'
    REVERSE = ('镜头3（6-9s）：【中近景，机位在屋里正对门，焦点在 A】机位在屋里朝门拍，灯泡镜台在镜头身后。门被推开，A 站在门口，'
               '镜头身后灯泡镜的暖色柔光照亮他的脸。他进门，从画左出画。\n')

    def test_behind_camera_object_mentioned_repeatedly(self):
        hits = codes(run(build(shots=(SHOT1, SHOT2, self.REVERSE))), 'W52')
        self.assertTrue(any('镜台' in h and '本镜提了 2 次' in h for h in hits), hits)

    def test_single_direction_sentence_is_fine(self):
        shot = self.REVERSE.replace('镜头身后灯泡镜的暖色柔光照亮他的脸', '屋里的暖色柔光从镜头这边照亮他的脸')
        self.assertEqual(codes(run(build(shots=(SHOT1, SHOT2, shot))), 'W52'), [])

    def test_global_sentence_naming_the_shot_counts(self):
        shot = self.REVERSE.replace('镜头身后灯泡镜的暖色柔光照亮他的脸', '屋里的暖色柔光照亮他的脸')
        glob = GLOBAL + '画面基调贯穿：镜头3 机位在屋里，镜台在镜头身后，灯泡镜的暖色光从镜头身后照来。\n'
        hits = codes(run(build(shots=(SHOT1, SHOT2, shot), global_rules=glob)), 'W52')
        self.assertTrue(any('全局句里 2 次' in h for h in hits), hits)

    def test_single_shot_opposite_view_image(self):
        shot = self.REVERSE.replace('镜头身后灯泡镜的暖色柔光照亮他的脸', '屋里的暖色柔光照亮他的脸')
        e = E.replace('@01_hall |', '@01_hall、@01_room |')
        hits = codes(run(build(refs=REFS + self.ROOM, shots=(SHOT1, SHOT2, shot), e=e)), 'W52')
        self.assertTrue(any('@01_room' in h and '只服务镜头3' in h for h in hits), hits)
        self.assertTrue(all('不要求补图' in h for h in hits if '@01_room' in h), hits)

    def test_e23_landmark_and_direction_sentence_are_not_counted(self):
        """E23 wants the door anchored in every unit that moves toward it, and a 方向： sentence in 【贯穿要求】."""
        walk = ('镜头3（6-9s）：【中近景，后退跟拍，焦点在 A】A 朝镜头走来，门在镜头身后；他看着镜头后方的门，'
                '越走越近，镜头身后的门开着一条缝。\n')
        glob = GLOBAL + '方向：镜头3 机位背对门，门在镜头身后，A 朝镜头走来，走向门。\n'
        self.assertEqual(codes(run(build(shots=(SHOT1, SHOT2, walk), global_rules=glob)), 'W52'), [])

    def test_reviewed_choice_is_info(self):
        shot = self.REVERSE.replace('镜头身后灯泡镜的暖色柔光照亮他的脸', '屋里的暖色柔光照亮他的脸')
        e = E.replace('@01_hall |', '@01_hall、@01_room |') + '| 视角说明 | 用户 10-19 定先用文字测 5 s 验证条 |\n'
        result = run(build(refs=REFS + self.ROOM, shots=(SHOT1, SHOT2, shot), e=e))
        self.assertFalse(any('@01_room' in h for h in codes(result, 'W52')))
        self.assertTrue(any(i.startswith('反视角参考图') for i in result['info']), result['info'])


class WarnClassTests(unittest.TestCase):
    def test_render_lesson_codes_are_named(self):
        shot = SHOT2.replace('英语，随口）', '英语，随口，语速快）')
        result = run(build(shots=(SHOT1, shot, SHOT3)))
        line = [i for i in result['info'] if i.startswith('成片教训类提醒')]
        self.assertEqual(len(line), 1, result['info'])
        self.assertIn('W47', line[0])
        self.assertIn('默认改', line[0])

    def test_clean_prompt_has_no_class_line(self):
        result = run(build())
        self.assertFalse(any(i.startswith('成片教训类提醒') for i in result['info']), result['info'])


if __name__ == '__main__':
    unittest.main()
