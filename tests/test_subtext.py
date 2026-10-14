"""1.7.0 W44 (subtext_checks.py): actions written into the dialogue bracket, and intent words in the bracket of a close
shot with no eye / face beat for that speaker in the shot line. Manner words (轻松 / 随口 / 带笑) are 口气 and never fire.

Fixtures are placeholder bar-scene prompts (A / B) shaped like offset EP05 s03 clip03 (shots 2 / 4 / 7 / 8). The
document-wiring test lives in test_release_170.py."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from subtext_checks import classify, clauses, carriers  # noqa: E402
from validate_prompt import validate  # noqa: E402

HEAD = ('【素材绑定】图1 = A 外观，只参考面部与发型；图2 = B 外观，只参考面部与发型；图3 = 酒吧空镜，不参考人物。\n'
        '【总述】12秒3:4竖屏，酒吧（图3），A 坐在吧台外，B 在吧台里；声音：无 bgm，只有环境音与台词。\n'
        '【画面基调】暖光，深景深。\n【起始状态】图1的A 坐在吧台外，在画面中间，面朝画右；图2的B 在吧台里。\n【分镜时间线】\n')
TAIL = ('【贯穿要求】A 与 B 的脸和发型按各自素材；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n'
        '\n| 项 | 值 |\n|---|---|\n| duration | 12 |\n| 节奏档 | 对话 |\n')


def build(*shots):
    return HEAD + '\n'.join(shots) + '\n' + TAIL


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def w44(result):
    return [w for w in result['warnings'] if w.startswith('W44')]


SHOT2 = ('镜头1（0-4s）：【近景双人，平视，固定，A 画左、B 画右，焦点在 B】B 走到 A 对面，顺手把吧巾搭到肩上。'
         '台词（A，0-1s，英语，抬眼，笑一下，声音不高）："Hey."；此时 B 闭着嘴。'
         '台词（B，1-4s，英语，认出熟客，语气轻松，21岁年轻男声，偏低）："Hey. Long time."；此时 A 闭着嘴，嘴角带着笑。视线：两人隔着吧台看着对方。')
SHOT7 = ('镜头2（4-8s）：【近景，平视，固定，A 居中，焦点在 A 眼睛】A 的手指在台面上轻轻点了一下。'
         '台词（A，4-8s，英语，轻松，真诚，不推销）："There is a part you should read for."；此时画外的 B 闭着嘴。视线：看着镜头右边一点的 B，不看镜头。')
SHOT8 = ('镜头3（8-12s）：【近景，平视，固定，B 居中，焦点在 B 眼睛】B 把酒倒进杯里，抬眼看了 A 一下，意外地笑了一下，又低头看向杯子。'
         '台词（A，画外，8-9s，英语，带一点笑意，是真想知道）："What?"；'
         '台词（B，9-12s，英语，看回他，笑着解释，没有要拒绝的意思）："Nothing. Just wasn\'t expecting that."。视线：杯子，再看回镜头左边一点的 A。')


class ClassifierTests(unittest.TestCase):
    def test_tokens_are_sorted_into_action_intent_and_skipped_manner(self):
        speaker, channel, actions, intents = classify('A，0-1s，英语，抬眼，笑一下，声音不高')
        self.assertEqual((speaker, channel, actions, intents), ('A', False, ['抬眼', '笑一下'], []))
        _, _, actions, intents = classify('B，1-4s，英语，认出熟客，语气轻松，21岁年轻男声，偏低')
        self.assertEqual((actions, intents), ([], ['认出熟客']))
        _, _, actions, intents = classify('A，4-8s，英语，轻松，真诚，不推销')
        self.assertEqual((actions, intents), ([], ['真诚', '不推销']))
        _, _, actions, intents = classify('B，9-12s，英语，看回他，笑着解释，没有要拒绝的意思')
        self.assertEqual((actions, intents), (['看回他'], ['笑着解释', '没有要拒绝的意思']))
        _, _, actions, intents = classify('B，12-14s，英语，这次点了头，语气平常')
        self.assertEqual((actions, intents), (['这次点了头'], []))
        # Manner, voice, timing, position and language tokens never count.
        for details in ('A，9-11s，英语，边忙边回，轻松', 'A，画外，12-13s，英语，轻松', 'A，14-15s，英语，像接着刚才的闲聊',
                        'A，6-9s，英语，随意，带一点笑意', '母亲，6-8s，中文普通话，正常音量，语速慢，句尾停 1 秒',
                        '女儿，9-10s，中文普通话，音量轻，语速快，拿起钥匙的同时说', 'Margaux，女声，免提，14-16s，英语，带笑',
                        'A，3-5s，英语，笑意收了、放慢', 'A，画右后景，4-5s，轻松', 'A，0-2s，英语，咬字清楚'):
            _, _, actions, intents = classify(details)
            self.assertEqual((actions, intents), ([], []), details)
        self.assertEqual(classify('A，15-16s，英语，顺着他的迟疑，把邀请放轻一点')[3], ['顺着他的迟疑'])
        self.assertEqual(classify('A，19-21s，英语，说得实在，比刚才的答应更具体')[3], ['说得实在', '比刚才的答应更具体'])
        # English brackets: voice words skip, anything else is intent; the channel flag reads 画外 / off-screen.
        self.assertEqual(classify('A，14-16s，English，quiet，sincere')[2:], ([], ['sincere']))
        self.assertEqual(classify('A，14-16s，English，soft voice')[2:], ([], []))
        self.assertTrue(classify('A，画外，8-9s，英语，是真想知道')[1])
        self.assertEqual(classify('Theo演员@Theo ，9-10s，English')[0], 'Theo')


class CarrierTests(unittest.TestCase):
    def test_clauses_are_attributed_by_leading_name_and_pronoun(self):
        body = ('：【近景，固定】B 把酒倒进杯里，抬眼看了 A 一下，意外地笑了一下。A 在画外问他，B 嘴角浮起一点笑。'
                '台词（A，画外，0-1s，英语）："Hi."；此时 B 闭着嘴，嘴角带着笑。视线：杯子，再看回 A。声音：杯子轻响，A 笑声。')
        parts = clauses(body, {'A', 'B'})
        self.assertEqual([(s, g) for s, _, g in parts][:5], [('B', False), ('A', False), ('B', False), ('B', False), (None, True)])
        found = carriers(body, {'A', 'B'})
        self.assertIn('B', found)
        self.assertNotIn('A', found)          # A's only clause is 问他; the 笑声 sits in the stripped 声音 clause
        self.assertIn(None, found)            # the 视线 line changes (再 / 看回) and names nobody
        # The listener's closed-mouth clause is not a beat; a framing or lighting clause is not a beat either.
        self.assertEqual(carriers('：【近景，固定】A 说话。台词（A，0-2s，英语）："Hi."；此时 B 闭着嘴。', {'A', 'B'}), {})
        self.assertEqual(carriers('：【近景，固定】镜头推到 A 的脸，止于看清他的眼睛。暖光照亮 A 的脸。', {'A', 'B'}), {})
        self.assertEqual(carriers('：【近景，固定】画外满桌笑出声，几个人轻快地笑。', {'A', 'B'}), {})
        self.assertEqual(carriers('：【近景，固定】A 的手指在台面上点了一下。视线：看着 B，不看镜头。', {'A', 'B'}), {})


class ShotTests(unittest.TestCase):
    def test_clip03_shapes(self):
        result = run(build(SHOT2, SHOT7, SHOT8))
        self.assertEqual(result['errors'], [], result['errors'])
        hits = w44(result)
        self.assertEqual(len(hits), 3, hits)
        self.assertIn('镜头1 台词括号里 1 处动作「抬眼，笑一下」（A），1 处态度「认出熟客」（B）同镜没有这个人的眼神拍子', hits[0])
        self.assertIn('括号里的词不删', hits[0])
        self.assertIn('镜头2 台词括号里 1 处态度「真诚，不推销」（A）同镜没有这个人的眼神拍子', hits[1])   # a finger tap is not an eye beat
        self.assertIn('镜头3 台词括号里 1 处动作「看回他」（B）', hits[2])
        self.assertNotIn('态度', hits[2])      # B's intent is carried by 抬眼看了 A 一下，意外地笑了一下; A 画外 lands on that beat
        self.assertFalse(any(i.startswith('态度拍子') for i in result['info']), result['info'])

    def test_eye_beat_clears_the_intent_form(self):
        fixed7 = SHOT7.replace('A 的手指在台面上轻轻点了一下。', 'A 的手指在台面上轻轻点了一下，开口时眼睛留在 B 脸上，嘴角带着笑。')
        hits = w44(run(build(SHOT2, fixed7, SHOT8)))
        self.assertFalse(any(h.startswith('W44 镜头2') for h in hits), hits)
        fixed2 = SHOT2.replace('视线：两人隔着吧台看着对方。', '视线：B 先看手里的吧巾，再看回 A。')
        hits = w44(run(build(fixed2, SHOT7, SHOT8)))
        self.assertIn('镜头1 台词括号里 1 处动作「抬眼，笑一下」（A）：', hits[0])
        self.assertNotIn('态度', hits[0])

    def test_listener_beat_does_not_clear_the_speaker_and_off_screen_gets_info(self):
        # B's intent with only A's listener beat in the shot: still uncovered for B.
        shot = ('镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 站在吧台里。'
                '台词（B，0-3s，英语，认出熟客）："Hey. Long time."；此时 A 闭着嘴，嘴角带着笑。')
        self.assertIn('「认出熟客」（B）', w44(run(build(shot)))[0])
        # An off-screen speaker's intent with no beat anywhere: INFO, not WARN.
        shot = ('镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 低头量酒。'
                '台词（A，画外，0-3s，英语，是真想知道）："What?"；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertTrue(any(i.startswith('态度拍子') and '画外' in i for i in result['info']), result['info'])
        # 内心独白 / 旁白 lines are never judged.
        shot = '镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 低头量酒。台词（A，内心独白画外，0-3s，英语，是真想知道）："What?"'
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertFalse(any(i.startswith('态度拍子') for i in result['info']))

    def test_wide_shot_intent_is_info_and_actions_still_warn(self):
        shot = ('镜头1（0-4s）：【中景双人，平视，固定，A 画左、B 画右，焦点在两人】两人隔着吧台。'
                '台词（A，0-3s，英语，真诚，不推销，抬眼）："There is a part for you."；此时 B 闭着嘴。')
        result = run(build(shot))
        hits = w44(result)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('1 处动作「抬眼」（A）', hits[0])
        self.assertNotIn('态度', hits[0])
        self.assertTrue(any(i.startswith('态度拍子') and '中景以上' in i for i in result['info']), result['info'])

    def test_voice_only_brackets_never_fire(self):
        shot = ('镜头1（0-4s）：【近景，平视，固定，A 居中，焦点在 A】A 看着 B。'
                '台词（A，0-3s，中文普通话，正常音量，语速慢，句尾停 1 秒）："面刚好。"；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertFalse(any(i.startswith('态度拍子') for i in result['info']))

    def test_prompt_without_dialogue_is_silent(self):
        shot = '镜头1（0-4s）：【近景，平视，固定，A 居中，焦点在 A】A 看着杯子。'
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertFalse(any(i.startswith('态度拍子') for i in result['info']))


if __name__ == '__main__':
    unittest.main()
