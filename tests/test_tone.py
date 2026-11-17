"""1.4.2 tone cues: W35 (tone_checks.py) and its INFO form.

Fixtures mirror the shape of the triggering case (offset EP05 场03 clip02 v1 → v1.6, validation-log
2026-10-13) with placeholder content: a light bar scene in which a regular walks in. v1 wrote the
reaction with suspense grammar (hand stops halfway, slow head turn in a fixed frontal close-up toward
the off-screen arrival, stare + lowered voice, stateless approach on a long lens) and rendered "like a
thriller"; v1.6 wrote the light reading into the cues. The real runs are recorded in CHANGELOG 1.4.2."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from tone_checks import shot_cues, declared_tone  # noqa: E402
from validate_prompt import validate  # noqa: E402

HEAD = ('【素材绑定】无参考素材。\n【总述】{overview}\n【画面基调】夜晚酒吧，暖光，深景深。\n'
        '【起始状态】A 在吧台里面画左搅酒，B 在画右。\n【分镜时间线】\n')
E = '\n\n| 项 | 值 |\n|---|---|\n| duration | 8 |\n| 峰值镜 | 1 |\n'

V1_SHOTS = [
    '镜头1（0-2s）：【近景，平视，过道里，长焦，C 居中】【变化：景别 近｜机位 长焦｜光 过道暖灯｜幅度 3】C 从画面深处的过道朝镜头这边走过来。视线：看着吧台的方向，不看镜头。',
    '镜头2（2-4s）：【中近景双人，平视，吧台外隔着台面，固定】【变化：景别 近→中近｜机位 长焦→固定｜光 =｜幅度 3→1】B 盯着画左过道那头，视线没离开，手背轻碰 A 的胳膊，压低声音。台词（B，2-4s，英语）："Look who\'s back."；此时 A 闭着嘴。',
    '镜头3（4-8s）：【近景，平视，吧台外正对 A，固定，A 正面居中】【变化：景别 中近→近｜机位 =｜光 =｜幅度 1→2】硬切到他的正面近景。A 抬眼，拿着薯条的手停在半路，顺着她的视线慢慢转头看向画左过道那头走过来的 C。',
]
V16_SHOTS = [
    '镜头1（0-2s）：【近景，平视，过道里，长焦，C 居中】【变化：景别 近｜机位 长焦｜光 过道暖灯｜幅度 3】C 在过道里朝镜头这边走，边走边低头看手机，另一只手插在裤袋里，步子随意，肩膀放松。',
    '镜头2（2-4s）：【中近景双人，平视，吧台外隔着台面，固定】【变化：景别 近→中近｜机位 长焦→固定｜光 =｜幅度 3→1】B 嘴角压着笑，眼睛亮起来，用手背轻碰一下 A 的胳膊。台词（B，2-4s，英语）："Look who\'s back."（声音放低，轻快，带着笑意）；此时 A 闭着嘴，正把一根薯条送进嘴里。视线：B 朝画左过道那头扬了扬下巴。',
    '镜头3（4-8s）：【近景，平视，吧台外正对 A，镜头稳定，A 正面居中】【变化：景别 中近→近｜机位 =｜光 =｜幅度 1→2】A 嚼着薯条抬起头，下巴放平，顺着 B 的方向朝画左看过去，看了一会儿；然后转头朝画右瞥了 B 一眼，嘴角的笑意深了一点。',
]
LIGHT = '8秒3:4竖屏，酒吧。轻松、温暖的上班日常：同事提醒 A 看常客走进来。'
NEUTRAL = '8秒3:4竖屏，酒吧。同事提醒 A 看常客走进来。'
SUSPENSE = '8秒3:4竖屏，悬疑片段：酒吧里 A 发现跟踪他的人走进来。'
COMEDY = '8秒3:4竖屏，办公室喜剧片段。'
GLOBAL = '【贯穿要求】A 与 B 外观与图一致；无bgm，只有环境音；不要字幕。'


def build(shots, overview):
    return HEAD.format(overview=overview) + '\n'.join(shots) + '\n' + GLOBAL + E


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def w35(result):
    return [w for w in result['warnings'] if w.startswith('W35')]


def tone_info(result):
    return [line for line in result['info'] if line.startswith('基调线索')]


class TriggerShapeTests(unittest.TestCase):
    def test_v1_wording_in_a_declared_light_scene_warns_on_every_cue_shot(self):
        result = run(build(V1_SHOTS, LIGHT))
        hits = w35(result)
        self.assertEqual([h.split('「')[0] for h in hits], ['W35 镜头1', 'W35 镜头2', 'W35 镜头3'], hits)
        self.assertIn('无状态的朝镜头走来', hits[0])
        self.assertIn('盯住 + 压低声音', hits[1])
        self.assertIn('停住', hits[2])
        self.assertIn('慢转头', hits[2])
        self.assertFalse(any(e.startswith('W35') for e in result['errors']))

    def test_v1_wording_with_no_tone_declared_still_warns_as_a_cluster(self):
        result = run(build(V1_SHOTS, NEUTRAL))
        self.assertEqual(len(w35(result)), 3, result['warnings'])
        self.assertTrue(all('基调未声明' in h for h in w35(result)))

    def test_v1_6_wording_is_clean(self):
        for overview in (LIGHT, NEUTRAL):
            result = run(build(V16_SHOTS, overview))
            self.assertEqual(w35(result), [], result['warnings'])
            self.assertEqual(tone_info(result), [])

    def test_declared_suspense_or_comedy_turns_the_same_cues_into_info(self):
        for overview in (SUSPENSE, COMEDY):
            result = run(build(V1_SHOTS, overview))
            self.assertEqual(w35(result), [], (overview, result['warnings']))
            self.assertEqual(len(tone_info(result)), 1, result['info'])
            self.assertIn('按类型语法保留', tone_info(result)[0])


class CueTests(unittest.TestCase):
    def test_light_cue_in_the_same_shot_drops_freeze_turn_and_eye_cues(self):
        self.assertIn('停住', shot_cues('A 拿着薯条的手停在半路。'))
        self.assertEqual(shot_cues('A 嚼着薯条，手停在半路又接着送进嘴里，笑了。'), {})
        self.assertIn('慢转头', shot_cues('A 慢慢转头看向门口。'))
        self.assertEqual(shot_cues('A 慢慢转头看向门口，眼神里是控诉，笑意压在嘴角。'), {})
        self.assertIn('低头抬眼 / 只动眼珠', shot_cues('A 低着头，眼睛抬起来看镜头。'))
        self.assertIn('低头抬眼 / 只动眼珠', shot_cues('A 头不动，只有眼珠转过去看她。'))

    def test_stare_plus_whisper_and_stateless_approach_are_not_softened_by_a_smile(self):
        self.assertIn('盯住 + 压低声音', shot_cues('B 盯着过道那头，压低声音，带一点笑。'))
        self.assertEqual(shot_cues('B 压低声音，带一点笑。'), {})          # whisper alone is not a cue
        self.assertEqual(shot_cues('B 盯着屏幕，嘴角压不住地笑。'), {})     # stare alone is not a cue
        self.assertIn('无状态的朝镜头走来', shot_cues('C 从过道朝镜头这边走过来，看着吧台的方向。'))
        self.assertEqual(shot_cues('C 朝镜头走来，边走边看手机，一手插在裤袋里。'), {})
        self.assertEqual(shot_cues('C 不紧不慢地朝镜头走过来，把吧巾往肩上一搭。'), {})

    def test_fixed_frontal_close_up_turn_toward_arrival_counts_without_the_word_slowly(self):
        body = '【近景，平视，正对 A，固定，A 正面居中】A 抬眼，转头看向画左过道那头走过来的 C。'
        self.assertIn('固定正面近景里转头朝画外来人', shot_cues(body))
        steady = body.replace('固定', '镜头稳定')
        self.assertEqual(shot_cues(steady), {})

    def test_change_field_is_not_this_shot(self):
        self.assertEqual(shot_cues('【中景，横移】【变化：机位 固定→横移｜幅度 停住→2】两人走到门口。'), {})

    def test_stage_spill_light_is_not_a_glance(self):
        self.assertEqual(shot_cues('舞台照下来的余光从画左打到脸上，右半边脸在暗里。'), {})


class ToneDeclarationTests(unittest.TestCase):
    def test_warm_light_and_relaxed_shoulders_do_not_declare_a_light_tone(self):
        text = '【总述】夜晚酒吧。\n【画面基调】暖光，暖色筒灯。\n【贯穿要求】肩膀放松，步子自然。'
        self.assertIsNone(declared_tone(text, ''))
        self.assertEqual(declared_tone('【总述】轻松的上班日常。', ''), 'light')
        self.assertEqual(declared_tone('【总述】夜晚酒吧。', '| 基调 | 喜剧 |'), 'genre')
        self.assertEqual(declared_tone('【总述】真人实拍悬疑片段。', ''), 'genre')


class WiringTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_documents_carry_the_rule_and_the_code(self):
        self.assertIn('## 4.4b', self.read('references/stage-4-performance.md'))
        self.assertIn('发现 / 被提醒看（轻松）', self.read('references/externalization-lexicon.md'))
        self.assertIn('| W35 |', self.read('references/checks.md'))
        self.assertIn('W35', self.read('SKILL.md'))
        self.assertIn('W35', self.read('references/stage-5-directing-storyboard.md'))
        self.assertIn('W35', self.read('references/genre-packs.md'))
        self.assertIn('像惊悚', self.read('references/validation-log.md'))
        self.assertIn('W35', self.read('scripts/validate_prompt.py').split('import argparse')[0])


if __name__ == '__main__':
    unittest.main()
