"""1.4.1 spatial direction: E23 (direction_checks.py, an ERROR by decision) and the 方向句 INFO.

Fixtures mirror the shape of the triggering case (offset EP05 场01 clip01 v2 → v2.1, validation-log
2026-10-13) with placeholder content: the scene image is shot from the building doorway looking out
at the street, the camera backs away under the canopy with the doors behind it, and the character
walks toward the camera into the building. v2 wrote the door as ahead of the character (朝大门走 /
前面的大门 / 退向大门); v2.1 anchors it to the camera (门在镜头身后) and adds a 方向 line. The real
v2.1 run is recorded in CHANGELOG 1.4.1. E23 was first shipped as WARN W34 and promoted the same day."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from direction_checks import core_cn, toward_camera, unresolved, has_direction_statement  # noqa: E402
from validate_prompt import validate  # noqa: E402

HEAD = ('【素材绑定】无参考素材。\n【总述】8秒3:4竖屏，大楼门口。\n'
        '【起始状态】A 从车门里出来，脸朝镜头方向；机位在雨棚下，背对大门，正对车门。\n【分镜时间线】\n')
E = '\n\n| 项 | 值 |\n|---|---|\n| duration | 8 |\n| 峰值镜 | 2 |\n'

V2_SHOTS = [
    '镜头1（0-3s）：【中景，平视，雨棚下正面，手持后退，A 居中】【变化：景别 中｜机位 手持后退｜光 正｜幅度 3】'
    '镜头随他起步往后退。A 迈步朝大门走，边走边扣扣子。视线：看着前面的大门，不看镜头。',
    '镜头2（3-6s）：【近景，平视，正面平稳后退跟拍，A 居中】【变化：景别 中→近｜机位 =｜光 =｜幅度 3→3】'
    '镜头在他正前方以他的步速后退，退向大门。A 不回头。视线：回到前面的大门。',
    '镜头3（6-8s）：【特写，平视，固定，A 的脸居中】【变化：景别 近→特写｜机位 后退跟拍→固定｜光 =｜幅度 3→1】'
    'A 在门口站定，看着前面的大门。',
]
V21_SHOTS = [
    '镜头1（0-3s）：【中景，平视，雨棚下正面，手持后退，A 居中】【变化：景别 中｜机位 手持后退｜光 正｜幅度 3】'
    '镜头随他起步往后退。A 迈步朝镜头走来，边走边扣扣子。视线：看着他要去的方向（镜头后方的门），不看镜头。',
    '镜头2（3-6s）：【近景，平视，正面平稳后退跟拍，A 居中】【变化：景别 中→近｜机位 =｜光 =｜幅度 3→3】'
    '镜头在他正前方以他的步速后退，退回雨棚下的门口（门在镜头身后）。A 不回头。视线：看着他要去的方向（镜头后方）。',
    '镜头3（6-8s）：【特写，平视，固定，A 的脸居中】【变化：景别 近→特写｜机位 后退跟拍→固定｜光 =｜幅度 3→1】'
    'A 在门口站定。',
]
DIRECTION = '方向：机位在雨棚下背对大门朝街道拍，画面里是街道一侧，A 始终从街道那边朝镜头走来，越走越近，他是在走进大楼'
NO_DIRECTION = 'A 的外观与图一致；记者在他两侧'


def build(shots, global_rules):
    return HEAD + '\n'.join(shots) + '\n【贯穿要求】' + global_rules + '；无bgm，只有环境音；不要字幕。' + E


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def e23(result):
    return [e for e in result['errors'] if e.startswith('E23')]


def direction_info(result):
    return [line for line in result['info'] if line.startswith('方向句')]


class TriggerShapeTests(unittest.TestCase):
    def test_v2_wording_errors_on_each_toward_camera_shot_only(self):
        result = run(build(V2_SHOTS, NO_DIRECTION))
        hits = e23(result)
        self.assertEqual(len(hits), 2, result['errors'])
        self.assertTrue(hits[0].startswith('E23 镜头1') and '朝大门走' in hits[0] and '前面的大门' in hits[0])
        self.assertTrue(hits[1].startswith('E23 镜头2') and '退向大门' in hits[1])
        # Shot 3 is a fixed shot: its 【变化：机位 后退跟拍→固定】 names the previous move, not this one.
        self.assertFalse(any('镜头3' in h for h in hits))
        self.assertTrue(any('未见方向句' in line for line in direction_info(result)))

    def test_v2_1_wording_is_clean_and_direction_line_is_seen(self):
        result = run(build(V21_SHOTS, DIRECTION))
        self.assertEqual(e23(result), [], result['errors'])
        self.assertEqual(result['checks']['format'], 'passed')
        self.assertTrue(any('已写方向' in line for line in direction_info(result)), result['info'])

    def test_missing_direction_line_is_info_not_error_or_warn(self):
        result = run(build(V21_SHOTS, NO_DIRECTION))
        self.assertEqual(e23(result), [])
        self.assertFalse(any('方向' in w for w in result['warnings']))
        self.assertTrue(any('未见方向句' in line for line in direction_info(result)))

    def test_e23_is_an_error_that_fails_format_and_is_not_a_warning(self):
        result = run(build(V2_SHOTS, NO_DIRECTION))
        self.assertEqual(result['checks']['format'], 'failed')
        self.assertFalse(any(w.startswith('E23') or w.startswith('W34') for w in result['warnings']))


class FalsePositiveGuardTests(unittest.TestCase):
    def test_walking_away_toward_an_in_frame_door_does_not_error(self):
        shots = ['镜头1（0-4s）：【全景，平视，固定】【变化：景别 全｜机位 固定｜光 侧｜幅度 3】'
                 'A 背对镜头朝走廊尽头的门走去，门在画面深处。',
                 '镜头2（4-8s）：【中景，平视，固定】【变化：景别 全→中｜机位 =｜光 =｜幅度 3→2】A 走到门口，伸手推门。']
        result = run(build(shots, NO_DIRECTION))
        self.assertEqual(e23(result), [], result['errors'])
        # Movement exists, so the 方向 reminder still appears as INFO.
        self.assertTrue(direction_info(result))

    def test_static_dialogue_prompt_emits_nothing(self):
        shots = ['镜头1（0-4s）：【近景，平视，固定】A 抬眼。', '镜头2（4-8s）：【近景，平视，固定】B 闭着嘴看着 A。']
        result = run(build(shots, NO_DIRECTION))
        self.assertEqual(e23(result), [])
        self.assertEqual(direction_info(result), [])

    def test_change_field_previous_move_is_not_this_shot(self):
        # EP03 s02b-clip02 shot 7 shape: tracking sideways, the field says 后退跟拍→横移.
        shots = ['镜头1（0-4s）：【中近景，正面后退跟拍】【变化：景别 中近｜机位 后退跟拍｜光 正｜幅度 3】两人朝镜头走来。',
                 '镜头2（4-8s）：【近景双人，两人斜前方，随步子横移】【变化：景别 中近→近｜机位 后退跟拍→横移｜光 =｜幅度 3→2】'
                 '两人走到入口上方发光的顶棚下，跨进影院的门。']
        result = run(build(shots, NO_DIRECTION))
        self.assertEqual(e23(result), [], result['errors'])
        self.assertFalse(toward_camera(shots[1]))

    def test_global_landmark_phrase_errors_once_unless_a_toward_shot_anchors_it(self):
        shot = ('镜头1（0-8s）：【近景，正面平稳后退跟拍，A 居中】【变化：景别 近｜机位 后退跟拍｜光 正｜幅度 3】'
                '镜头在他正前方后退，A 朝镜头走来。')
        result = run(build([shot], '走位：A 从车门朝大门走，进大堂'))
        hits = e23(result)
        self.assertEqual(len(hits), 1, result['errors'])
        self.assertTrue(hits[0].startswith('E23 【贯穿要求】') and '朝大门走' in hits[0])
        # EP04 s03-clip01 shape: the global sentence repeats a move the toward-camera shot already anchored.
        anchored = shot.replace('A 朝镜头走来。', 'A 往画左的桌边走，朝镜头走来。')
        result = run(build([anchored], '位置与轴线：镜头1 两人朝画左走回桌边'))
        self.assertEqual(e23(result), [], result['errors'])

    def test_toward_camera_without_any_landmark_phrase_is_clean(self):
        shot = ('镜头1（0-8s）：【近景，正面平稳后退跟拍，A 居中】【变化：景别 近｜机位 后退跟拍｜光 正｜幅度 3】'
                '镜头在他正前方后退，A 朝镜头走来，边走边转头答记者的问题。')
        self.assertEqual(e23(run(build([shot], NO_DIRECTION))), [])


class EnglishTests(unittest.TestCase):
    def test_english_wording_errors_and_anchoring_clears_it(self):
        shot = ('Shot 1 (0-8s): [MS, eye level, camera tracks back ahead of him] He walks toward the door, '
                'buttoning his jacket. He looks at the door ahead.')
        result = run(build([shot], NO_DIRECTION))
        self.assertEqual(len(e23(result)), 1, result['errors'])
        anchored = shot + ' The door is behind the camera.'
        self.assertEqual(e23(run(build([anchored], NO_DIRECTION))), [])
        self.assertTrue(has_direction_statement('DIRECTION: the frame shows the street side; he walks toward the camera.'))


class HelperTests(unittest.TestCase):
    def test_core_noun_normalisation(self):
        self.assertEqual(core_cn('大门'), '门')
        self.assertEqual(core_cn('门口'), '门')
        self.assertEqual(core_cn('玻璃门'), '门')
        self.assertEqual(core_cn('入口'), '入口')
        self.assertEqual(core_cn('窗口'), '窗口')
        self.assertEqual(core_cn('车门'), '车门')

    def test_unresolved_uses_same_unit_anchoring(self):
        self.assertEqual([p for p, _ in unresolved('他朝大门走。')], ['朝大门走'])
        self.assertEqual(unresolved('他朝大门走，大门在镜头身后。'), [])
        self.assertEqual(unresolved('他退回雨棚下的门口（门在镜头身后）。'), [])
        self.assertEqual(unresolved('机位在大堂里正对玻璃门；他走到门口。'), [])
        self.assertEqual([p for p, _ in unresolved('看向前面的大门')], ['前面的大门'])


class WiringTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_documents_carry_the_rule_and_the_code(self):
        self.assertIn('### 3.7', self.read('references/director-grammar.md'))
        self.assertIn('E23', self.read('references/stage-6-prompt-compiler.md'))
        self.assertIn('E23', self.read('references/stage-5-directing-storyboard.md'))
        self.assertIn('| E23 |', self.read('references/checks.md'))
        self.assertIn('E23', self.read('SKILL.md'))
        self.assertIn('2026-10-13', self.read('references/validation-log.md'))
        self.assertIn('E23', self.read('scripts/validate_prompt.py').split('import argparse')[0])
        for name in ('SKILL.md', 'references/stage-6-prompt-compiler.md', 'references/duration-rhythm.md'):
            self.assertNotIn('W34', self.read(name), name)


if __name__ == '__main__':
    unittest.main()
