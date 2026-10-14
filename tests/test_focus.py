"""1.7.0 W43 焦点与虚实 (focus_checks.py): a focus statement in every on-screen character shot, a placement wherever an
over-shoulder or soft layer is named, and the default depth of field declared once in 【画面基调】.

Fixtures are placeholder bar-scene prompts (A / B, generic lines) in the clip03 shape: 8 shots / 25 s, one object
insert, two-line and three-line shots, off-screen lines. The document-wiring test lives in test_release_170.py."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from focus_checks import (depth_of_field, layer_without_placement, has_focus, is_character_shot, tag_of,  # noqa: E402
                          character_names, normalize_speaker)
from validate_prompt import validate  # noqa: E402

HEAD = '【素材绑定】图1 = A 外观，只参考面部与发型；图2 = B 外观，只参考面部与发型；图3 = 酒吧空镜，不参考人物。\n'
LOOK = '【画面基调】暖光，数字电影机实拍质感，长焦，深景深，人和身后的环境都清楚，机位平视。\n'
BODY = ('【总述】25秒3:4竖屏，酒吧（图3），A 坐下，B 过来招呼，两人闲聊；声音：无 bgm，只有环境音与台词。\n'
        '{look}'
        '【起始状态】图1的A 站在吧台外的高脚凳旁，在画面中间，面朝画右的吧台；图2的B 在画面深处的吧台里。\n'
        '【分镜时间线】\n'
        '镜头1（0-3s）：【中近景，平视，固定，A 居中{f1}】A 坐下，把外套搭在旁边的凳子上。视线：A 看着吧台里面。\n'
        '镜头2（3-6s）：【近景双人，平视，固定，A 画左、B 画右{f2}】B 走到 A 对面。'
        '台词（A，3-4s，英语，声音不高）："Hey."；此时 B 闭着嘴。台词（B，4-6s，英语，轻松）："Hey. Long time."；此时 A 闭着嘴。\n'
        '镜头3（6-9s）：【特写，固定，只拍台面上的杯子】一只矮杯放在台面上，杯壁上有水珠。\n'
        '镜头4（9-13s）：【中近景，平视，固定，B 居中{f4}】B 从吧台下取出一只杯子放到台面上。'
        '台词（B，9-11s，英语，轻松）："Been busy."；台词（B，11-12s，英语，随口）："Same as before?"；'
        '台词（A，画外，12-13s，英语，轻松）："Yeah."；此时 B 闭着嘴。\n'
        '镜头5（13-15s）：【中近景双人，{ots}平视，固定，A 画左、B 画右{f5}】B 转身去身后的酒柜取一瓶酒。{place}'
        '台词（A，14-15s，英语，轻松）："You ever act?"；此时 B 背对着他，闭着嘴。\n'
        '镜头6（15-18s）：【近景，平视，固定，B 居中{f6}】B 低头量酒，抬眼看了 A 一下。'
        '台词（B，15-16s，英语，随口）："No. Why?"；台词（A，画外，16-18s，英语，轻松）："I have a film."；此时 B 闭着嘴。\n'
        '镜头7（18-21s）：{tag7}A 的手指在台面上点了一下。'
        '台词（A，18-21s，英语，轻松）："There is a part for you."；此时 B 闭着嘴。\n'
        '镜头8（21-25s）：【近景，平视，固定，B 居中{f8}】B 抬眼看了 A 一下，笑了一下，又低头看杯子。'
        '台词（A，画外，22-23s，英语，轻松）："What?"；台词（B，23-25s，英语，轻松）："Nothing."；此时 A 闭着嘴。\n'
        '【贯穿要求】A 与 B 的脸和发型按各自素材；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n')
E = '\n| 项 | 值 |\n|---|---|\n| duration | 25 |\n| 节奏档 | 对话 |\n'


def prompt(focus=False, look=LOOK, ots=False, place=False, tag7=None):
    f = {f'f{n}': (f'，焦点在 {"B" if n in (4, 6, 8) else "A"} 眼睛' if focus else '') for n in (1, 2, 4, 5, 6, 8)}
    if tag7 is None:
        tag7 = '【近景，平视，固定，A 居中' + ('，焦点在 A 眼睛' if focus else '') + '】'
    return HEAD + BODY.format(look=look, ots='过肩，' if ots else '', tag7=tag7,
                              place='右下角是 B 虚化的肩膀，只占一小块，A 在画面中间清楚。' if place else '', **f) + E


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def w43(result):
    return [w for w in result['warnings'] if w.startswith('W43')]


def focus_info(result):
    return [i for i in result['info'] if i.startswith('焦点：')]


class MissingFocusTests(unittest.TestCase):
    def test_lists_exactly_the_on_screen_character_shots(self):
        result = run(prompt())
        self.assertEqual(result['errors'], [], result['errors'])
        hits = w43(result)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('镜头 [1, 2, 4, 5, 6, 7, 8] 有画内人物但没写焦点在谁', hits[0])   # shot 3 is the object insert
        self.assertIn('焦点在 X（部位）', hits[0])
        self.assertEqual(focus_info(result), ['焦点：0/7 个画内人物镜写了焦点；默认景深「深景深」（【画面基调】）'])

    def test_focus_in_every_tag_clears_it(self):
        result = run(prompt(focus=True))
        self.assertEqual(w43(result), [])
        self.assertEqual(focus_info(result), ['焦点：7/7 个画内人物镜写了焦点；默认景深「深景深」（【画面基调】）'])

    def test_partial_focus_counts_and_global_statement_is_acknowledged(self):
        text = prompt().replace('【近景，平视，固定，A 居中】A 的手指', '【近景，平视，固定，A 居中，焦点在 A 的眼睛】A 的手指')
        result = run(text)
        self.assertIn('镜头 [1, 2, 4, 5, 6, 8] 有画内人物', w43(result)[0])
        self.assertTrue(focus_info(result)[0].startswith('焦点：1/7 个画内人物镜写了焦点'))
        text = prompt().replace('【贯穿要求】', '【贯穿要求】画面的焦点始终在 A、B 身上；')
        self.assertIn('全局已写', w43(run(text))[0])

    def test_english_and_other_phrasings_count(self):
        text = prompt(tag7="[close-up, eye level, locked, focused on A's eyes]")
        self.assertIn('镜头 [1, 2, 4, 5, 6, 8] 有画内人物', w43(run(text))[0])
        for phrase in ('焦点里是 A', '焦点始终在 A 的眼睛', '焦点：A 的眼睛', '对焦在 A', '移焦，前景的手变模糊，脸由模糊变清晰'):
            self.assertTrue(has_focus('：【近景，固定】' + phrase + '。'), phrase)
        self.assertFalse(has_focus('：【近景，固定】镜头从前景的手移焦到脸。'))          # bare 移焦 needs its explanation
        self.assertFalse(has_focus('：【近景，固定】【变化：机位 移焦→固定】A 抬眼。'))   # legacy field, previous shot
        self.assertFalse(has_focus('：【近景，固定，A 居中】A 抬眼。'))

    def test_inserts_and_off_screen_only_lines_are_exempt(self):
        text = prompt(focus=True).replace('杯壁上有水珠。', '杯壁上有水珠，映出一点 A 的眼睛。')
        self.assertEqual(w43(run(text)), [])
        self.assertFalse(is_character_shot(3, '：【特写，固定，只拍台面上的杯子】杯壁映出 A 的眼睛。', [], {'A'}))
        self.assertTrue(is_character_shot(3, '：【特写，固定，只拍台面上的杯子】台词（A，6-7s，英语，轻）："Hm."', [], {'A'}))
        # A hand insert carrying only an off-screen line (the user's 贝壳 shot) is not an on-screen character.
        self.assertFalse(is_character_shot(5, '：【特写，A 的手，固定】手捡起贝壳。台词（A，画外，10-12s，英语，轻）："Hey."', [], {'A'}))
        # A footprint shot with off-screen laughter: 笑声 is not a face.
        self.assertFalse(is_character_shot(6, '：【特写，沙滩上的脚印，固定】浪漫过脚印。声音：画外两人的喘气和笑声。', [], {'A'}))
        self.assertTrue(is_character_shot(1, '：【中近景，平视，固定】A 坐下。视线：A 看着吧台里面。', [], {'A'}))
        self.assertFalse(is_character_shot(1, '：【中近景，平视，固定】A 坐下，把外套搭在凳子上。', [], {'A'}))
        # Two-shots and named-character tags count even without a line or a face word; 屏幕 does not exempt a named person.
        self.assertTrue(is_character_shot(4, '：【中近景双人，侧面，固定】两人走进电梯间。', [], set()))
        self.assertTrue(is_character_shot(8, '：【中近景，A 与前排椅背上的车载屏幕同框，平视，固定】屏幕熄灭。', [], {'A'}))
        self.assertFalse(is_character_shot(8, '：【特写，车载屏幕，固定】屏幕熄灭。', [], {'A'}))


class LayerTests(unittest.TestCase):
    def test_over_shoulder_without_placement_fires_per_shot(self):
        result = run(prompt(focus=True, ots=True))
        self.assertEqual(w43(result), ['W43 镜头 5 有过肩 / 虚化层，没写它在画面哪里、占多少（哪一层虚、在哪一侧或哪个角、占多少；主体在哪里清楚）'])

    def test_placement_sentence_clears_it_and_forms_are_independent(self):
        self.assertEqual(w43(run(prompt(focus=True, ots=True, place=True))), [])
        hits = w43(run(prompt(ots=True)))
        self.assertEqual(len(hits), 2, hits)
        self.assertTrue(hits[0].startswith('W43 镜头 [1, 2, 4, 5, 6, 7, 8]') and hits[1].startswith('W43 镜头 5 有过肩'))

    def test_phrasings_and_exclusions(self):
        self.assertTrue(layer_without_placement('：【中近景，越过 A 的肩拍 B，平视，固定】B 抬眼。'))
        self.assertTrue(layer_without_placement('：【近景，平视，固定】镜头越过 A 的肩拍 B 的正脸。'))
        self.assertTrue(layer_without_placement('：【中近景，越肩，平视，固定，长焦浅景深】B 抬眼。'))
        self.assertTrue(layer_without_placement('：[medium close-up, over-the-shoulder, locked] B looks up.'))
        self.assertTrue(layer_without_placement('：【中近景，越肩，固定】B 点出事实。台词（B，3-5s，英语，吐字清楚）："Yes."'))
        self.assertTrue(layer_without_placement('：【近景，固定】B 抬眼，身后的人虚化。'.replace('身后的人虚化', '客人虚化')))
        # Position words settle it: a corner, a side, a layer name.
        self.assertFalse(layer_without_placement('：【中近景，越肩，平视，固定】前景是 A 虚化的肩，只占画面右下角一小块。'))
        self.assertTrue(layer_without_placement('：【中近景，越过 A 的右肩拍 B，平视，固定】前景是 A 的右肩，虚化。'))   # which corner, how much?
        self.assertFalse(layer_without_placement('：【中近景，越过 A 的右肩拍 B，平视，固定】前景是 A 的右肩，虚化，只占画面右下角。'))
        self.assertFalse(layer_without_placement('：【中近景，固定，A 的肩在画右边缘虚焦】B 抬眼。'))
        self.assertFalse(layer_without_placement('：【近景，固定】B 抬眼，身后的客人轻微虚化、看得出人形。'))
        # Not a picture layer: the 声音 line's audio layering, a set piece in deep focus, a gaze over a shoulder, the legacy field.
        self.assertFalse(layer_without_placement('：【近景，平视，固定】B 抬眼。声音：前景=B 的台词；床=酒吧人声。'))
        self.assertFalse(layer_without_placement('：【中景，平视，固定】画左前景是床头柜，B 在床上。'))
        self.assertFalse(layer_without_placement('：【中近景，平视，固定】A 回头越过肩膀看 B 一眼；B 的目光越过 A 的肩膀落到门口。'))
        self.assertFalse(layer_without_placement('：【特写，台面上的调酒，俯拍，固定】【变化：景别 近→特写｜机位 越肩→台面俯拍｜光 =｜幅度 1】酒落进杯里。'))
        self.assertFalse(layer_without_placement('：【中景，平视，固定】两人并肩靠着栏杆。'))

    def test_keyframe_task_is_exempt_from_the_layer_form(self):
        text = '以图片1至图片2的顺序作为关键帧。\n' + prompt(focus=True, ots=True).replace('【素材绑定】', '【素材绑定】图4 = 镜头5关键帧；')
        self.assertEqual(w43(run(text)), [])


class OverrideInfoAndEdgeTests(unittest.TestCase):
    def test_focus_reason_row_keeps_the_design(self):
        result = run(prompt(ots=True) + '| 焦点理由 | 2D 手绘，无景深 |\n')
        self.assertEqual(w43(result), [])
        self.assertTrue(any('焦点理由 已写明' in i for i in focus_info(result)), result['info'])

    def test_depth_of_field_phrases(self):
        self.assertEqual(depth_of_field(LOOK), '深景深')
        self.assertEqual(depth_of_field('【画面基调】35mm 胶片质感，浅景深，背景虚化。'), '浅景深')
        self.assertEqual(depth_of_field('【画面基调】中等景深，桌面与母亲都清晰。'), '中等景深')
        self.assertEqual(depth_of_field('【画面基调】人物脸部清楚，背景适度虚化。'), '背景适度虚化')
        self.assertEqual(depth_of_field('LOOK: 35mm film, shallow depth of field.'), 'shallow depth of field')
        self.assertIsNone(depth_of_field('【画面基调】暖光，长焦。'))
        result = run(prompt(look='【画面基调】暖光，数字电影机实拍质感，长焦，机位平视。\n'))
        self.assertEqual(focus_info(result), ['焦点：0/7 个画内人物镜写了焦点；未声明默认景深（【画面基调】写一句景深：深 / 中等 / 浅）'])

    def test_no_character_shots_gives_no_w43_and_no_info(self):
        text = (HEAD + '【总述】6秒3:4竖屏，酒吧（图3）空镜；声音：无 bgm，只有环境音。\n' + LOOK +
                '【起始状态】吧台上放着一只杯子和一瓶酒。\n【分镜时间线】\n'
                '镜头1（0-3s）：【特写，固定，只拍台面上的杯子】杯壁上的水珠慢慢滑下来。\n'
                '镜头2（3-6s）：【空镜，平视，固定】酒柜的暖光照着一排酒瓶。\n'
                '【贯穿要求】无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音；不要字幕。\n'
                '\n| 项 | 值 |\n|---|---|\n| duration | 6 |\n')
        result = run(text)
        self.assertEqual(w43(result), [])
        self.assertEqual(focus_info(result), [])

    def test_helpers(self):
        long_tag = '：【' + '中近景，平视，过道这头往里拍，长焦，镜头随他坐下轻轻下移，' * 2 + 'A 居中，焦点在 A 的脸】A 坐下。'
        self.assertTrue(tag_of(long_tag).endswith('焦点在 A 的脸'))
        self.assertEqual(normalize_speaker('Theo演员@Theo '), 'Theo')
        self.assertEqual(normalize_speaker('女导演@01_Directer '), '女导演')
        self.assertEqual(normalize_speaker('Theo 内心独白画外'), 'Theo')
        names = character_names('【起始状态】Rhett（@Rhett-基础形象，穿 @05_Rhett_outfit）站着；图1的母亲在画左。\n【分镜时间线】\n',
                                [{'speaker': 'Theo演员@Theo '}])
        self.assertEqual(names, {'Rhett', 'Theo', '母亲'})


if __name__ == '__main__':
    unittest.main()
