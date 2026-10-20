"""1.7.0 W44 (subtext_checks.py), relaxed in 1.7.1: actions written into the dialogue bracket, and intent words in the
bracket of a close shot with no executable beat of ANY kind for that speaker in the shot line (eye / face, hand / head /
body, voice or pause, an action toward the other character) and no delivery word in the bracket. Manner words (轻松 /
随口 / 带笑) are 口气 and never fire; 1.7.0 required an eye beat, 1.7.1 lets the director choose the carrier.

Fixtures are placeholder bar-scene prompts (A / B) shaped like offset EP05 s03 clip03 (shots 2 / 4 / 7 / 8). The
document-wiring tests live in test_release_170.py and test_release_171.py."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from subtext_checks import classify, bracket_delivery, clauses, carriers, beat_kinds  # noqa: E402
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


def attitude_info(result):
    return [i for i in result['info'] if i.startswith('态度拍子')]


SHOT2 = ('镜头1（0-4s）：【近景双人，平视，固定，A 画左、B 画右，焦点在 B】B 走到 A 对面，顺手把吧巾搭到肩上。'
         '台词（A，0-1s，英语，抬眼，笑一下，声音不高）："Hey."；此时 B 闭着嘴。'
         '台词（B，1-4s，英语，认出熟客，语气轻松，21岁年轻男声，偏低）："Hey. Long time."；此时 A 闭着嘴，嘴角带着笑。视线：两人隔着吧台看着对方。')
SHOT7 = ('镜头2（4-8s）：【近景，平视，固定，A 居中，焦点在 A 眼睛】A 的手指在台面上轻轻点了一下。'
         '台词（A，4-8s，英语，轻松，真诚，不推销）："There is a part you should read for."；此时画外的 B 闭着嘴。视线：看着镜头右边一点的 B，不看镜头。')
BARE7 = SHOT7.replace('A 的手指在台面上轻轻点了一下。', 'A 坐在吧台外。')      # placement only: no beat of any kind
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
        # A platform handle with nothing else keeps its stem as the speaker (ep02 s04: @01_host).
        self.assertEqual(classify('@01_host，10-11s，英语，清晰的成年男声、中音，好奇')[0::3], ('01_host', ['好奇']))

    def test_delivery_words_in_the_bracket_are_a_voice_carrier_but_manner_words_are_not(self):
        self.assertEqual(bracket_delivery('A，4-8s，英语，轻松，真诚，不推销'), [])
        self.assertEqual(bracket_delivery('B，1-4s，英语，认出熟客，语气轻松，21岁年轻男声，偏低'), [])
        self.assertEqual(bracket_delivery('A，4-8s，英语，真诚，轻声'), ['轻声'])
        self.assertEqual(bracket_delivery('A，0-1s，英语，声音不高'), ['声音不高'])
        self.assertEqual(bracket_delivery('Theo，17-18s，英语，偏低、带笑的挑衅'), ['带笑的挑衅'])
        self.assertEqual(bracket_delivery('A，4-8s，英语，真诚，放慢，句尾顿一拍'), ['放慢', '句尾顿一拍'])
        self.assertEqual(bracket_delivery('A，14-16s，English，quiet，sincere'), ['quiet'])


class CarrierTests(unittest.TestCase):
    def test_clauses_are_attributed_by_leading_name_and_pronoun(self):
        body = ('：【近景，固定】B 把酒倒进杯里，抬眼看了 A 一下，意外地笑了一下。A 在画外问他，B 嘴角浮起一点笑。'
                '台词（A，画外，0-1s，英语）："Hi."；此时 B 闭着嘴，嘴角带着笑。视线：杯子，再看回 A。声音：杯子轻响，A 笑声。')
        parts = clauses(body, {'A', 'B'})
        self.assertEqual([(s, g) for s, _, g in parts][:5], [('B', False), ('A', False), ('B', False), ('B', False), (None, True)])
        found = carriers(body, {'A', 'B'})
        self.assertEqual(found['B'], {'眼神', '身体'})
        self.assertNotIn('A', found)          # A's only clause is 问他; the 笑声 sits in the stripped 声音 clause
        self.assertEqual(found[None], {'眼神'})   # the 视线 line changes (再 / 看回) and names nobody
        # The listener's closed-mouth clause is not a beat; a framing or lighting clause is not a beat either.
        self.assertEqual(carriers('：【近景，固定】A 说话。台词（A，0-2s，英语）："Hi."；此时 B 闭着嘴。', {'A', 'B'}), {})
        self.assertEqual(carriers('：【近景，固定】镜头推到 A 的脸，止于看清他的眼睛。暖光照亮 A 的脸。', {'A', 'B'}), {})
        self.assertEqual(carriers('：【近景，固定】画外满桌笑出声，几个人轻快地笑。', {'A', 'B'}), {})
        # 1.7.1: a finger tap is a body carrier; a static placement is not.
        self.assertEqual(carriers('：【近景，固定】A 的手指在台面上点了一下。视线：看着 B，不看镜头。', {'A', 'B'}), {'A': {'身体'}})
        self.assertEqual(carriers('：【近景，固定】A 坐在吧台外，面朝画右。视线：看着 B，不看镜头。', {'A', 'B'}), {})

    def test_pronoun_sentences_inherit_the_last_named_subject(self):
        # ep04 s01 镜7: the camera sentence in between does not break the chain, 他 is still Theo.
        body = '：【近景】Theo 直起身，甩了甩湿头发。镜头随他后退的步子一起后退。他冲 Rhett 勾了勾手指，带着笑挑衅。'
        self.assertEqual([s for s, _, _ in clauses(body, {'Theo', 'Rhett'})], ['Theo', None, 'Theo'])
        self.assertEqual(carriers(body, {'Theo', 'Rhett'})['Theo'], {'眼神', '身体', '互动'})
        # ep03 s02 clip02 镜3: a dialogue bracket names its speaker, so 他说完 is Marcus; 两人 resets the subject; the
        # colon starts a new piece so Rhett's reaction is Rhett's.
        body = ('：【中近景双人】Rhett 和 Theo 并排坐着。台词（Marcus，画右后景，4-5s，轻松，像在逗他们）："Honestly?"；'
                '此时 Rhett 和 Theo 闭着嘴。他说完，两人都没接：Rhett 低头笑了一下。')
        parts = clauses(body, {'Rhett', 'Theo', 'Marcus'})
        self.assertEqual([(s, t) for s, t, _ in parts][-3:], [('Marcus', '他说完'), (None, '两人都没接'), ('Rhett', 'Rhett 低头笑了一下')])
        found = carriers(body, {'Rhett', 'Theo', 'Marcus'})
        self.assertNotIn('Marcus', found)
        self.assertEqual(found['Rhett'], {'眼神', '身体'})

    def test_beat_kinds(self):
        self.assertEqual(beat_kinds('手指在台面上轻轻点了一下'), {'身体'})
        self.assertEqual(beat_kinds('说这句时声音放低了半度，句尾没有上扬'), {'声音'})
        self.assertEqual(beat_kinds('说完停了一拍，没有接着推荐'), {'声音'})
        self.assertEqual(beat_kinds('把酒单朝 B 推过去一点', ['B']), {'身体', '互动'})
        self.assertEqual(beat_kinds('开口时眼睛留在 B 脸上，嘴角带着笑', ['B']), {'眼神'})
        self.assertEqual(beat_kinds('偏过头，朝着茶几上的手机答应'), {'身体'})
        self.assertEqual(beat_kinds('靠进沙发背里，原本还端着的肩膀彻底松下来'), {'身体'})
        self.assertEqual(beat_kinds('胸口随呼吸轻轻起伏'), {'身体'})
        self.assertEqual(beat_kinds('坐在吧台外，面朝画右'), set())
        self.assertEqual(beat_kinds('吧台在画右往画面深处延伸'), set())
        self.assertEqual(beat_kinds('镜头推到 A 的脸，止于看清他的眼睛', ['A']), set())


class ShotTests(unittest.TestCase):
    def test_clip03_shapes(self):
        result = run(build(SHOT2, SHOT7, SHOT8))
        self.assertEqual(result['errors'], [], result['errors'])
        hits = w44(result)
        self.assertEqual(len(hits), 2, hits)
        self.assertIn('镜头1 台词括号里 1 处动作「抬眼，笑一下」（A）：动作写进镜头行（开口前或开口时，由导演定）', hits[0])
        self.assertNotIn('态度', hits[0])      # B's 认出熟客 is carried by 顺手把吧巾搭到肩上
        self.assertIn('情绪 / 判断词移到分镜卡 A 层', hits[0])
        self.assertIn('镜头3 台词括号里 1 处动作「看回他」（B）', hits[1])
        self.assertIn('写进去后它就是同一括号里态度词的拍子', hits[1])   # B's bracket also carries 笑着解释 / 没有要拒绝的意思
        self.assertFalse(any(h.startswith('W44 镜头2') for h in hits), hits)   # the finger tap carries 真诚 / 不推销
        self.assertEqual(attitude_info(result), ['态度拍子：6/6 处意图词有可执行拍子（身体 5 · 听者或下一镜 1）'])

    def test_intent_with_no_carrier_of_any_kind_fires(self):
        result = run(build(BARE7))
        hits = w44(result)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('镜头2 台词括号里 1 处态度「真诚，不推销」（A）同镜没有这个人的可执行拍子', hits[0])
        self.assertIn('不限于眼神', hits[0])
        self.assertIn('情绪 / 判断词移到分镜卡 A 层', hits[0])
        self.assertNotIn('眼神拍子', hits[0])
        self.assertEqual(attitude_info(result), ['态度拍子：0/2 处意图词有可执行拍子'])

    def test_any_carrier_clears_the_intent(self):
        carriers_ = {
            '眼神': 'A 坐在吧台外，开口时眼睛留在 B 脸上，嘴角带着笑。',
            '身体': 'A 的手指在台面上轻轻点了一下。',
            '声音': 'A 说这句时声音放低了半度，句尾没有上扬。',
            '停顿': 'A 坐在吧台外。说完 A 停了一拍，没有接着推荐。',
            '互动': 'A 把酒单朝 B 推过去一点。',
        }
        for kind, prose in carriers_.items():
            result = run(build(BARE7.replace('A 坐在吧台外。', prose)))
            self.assertEqual(w44(result), [], kind)
            self.assertTrue(attitude_info(result)[0].startswith('态度拍子：2/2'), (kind, attitude_info(result)))
        # A delivery word in the bracket is the voice carrier; a manner word alone is not (BARE7 itself fires).
        result = run(build(BARE7.replace('轻松，真诚，不推销', '轻声，真诚，不推销')))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), ['态度拍子：2/2 处意图词有可执行拍子（声音 2）'])
        # 1.7.0 fixture still passes: a 视线 line that changes counts for the on-screen speakers.
        fixed2 = SHOT2.replace('B 走到 A 对面，顺手把吧巾搭到肩上。', 'B 站在 A 对面。').replace('视线：两人隔着吧台看着对方。', '视线：B 先看手里的吧巾，再看回 A。')
        hits = w44(run(build(fixed2)))
        self.assertEqual(len(hits), 1, hits)
        self.assertNotIn('态度', hits[0])

    def test_listener_beat_does_not_clear_the_speaker_and_off_screen_gets_info(self):
        # B's intent with only A's listener beat in the shot: still uncovered for B (站在 is placement, not a beat).
        shot = ('镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 站在吧台里。'
                '台词（B，0-3s，英语，认出熟客）："Hey. Long time."；此时 A 闭着嘴，嘴角带着笑。')
        self.assertIn('「认出熟客」（B）', w44(run(build(shot)))[0])
        # An off-screen speaker's intent with no beat anywhere: INFO, not WARN.
        shot = ('镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 站在吧台里。'
                '台词（A，画外，0-3s，英语，是真想知道）："What?"；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertTrue(any('画外 / 背对 / 后景' in i for i in attitude_info(result)), result['info'])
        # With the listener's reaction in the shot the intent has landed: no INFO about it, counted as covered.
        shot = ('镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 低头量酒。'
                '台词（A，画外，0-3s，英语，是真想知道）："What?"；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), ['态度拍子：1/1 处意图词有可执行拍子（听者或下一镜 1）'])
        # 1.7.1: a back-turned / background speaker is treated like an off-screen one (ep03 s02 clip02 镜3).
        shot = ('镜头1（0-4s）：【中近景双人，平视，固定，A 画左、B 画右，焦点在 A】A 和 B 并排坐着；画右后景是站在桌头的 C，人小、虚着。'
                '台词（C，画右后景，1-2s，英语，轻松，像在逗他们）："Honestly?"；此时 A 和 B 闭着嘴。他说完，两人都没接：A 低头笑了一下。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), ['态度拍子：1/1 处意图词有可执行拍子（听者或下一镜 1）'])
        result = run(build(shot.replace('他说完，两人都没接：A 低头笑了一下。', '')))
        self.assertEqual(w44(result), [])
        self.assertTrue(any('画外 / 背对 / 后景' in i and '「像在逗他们」（C）' in i for i in attitude_info(result)), result['info'])
        # 内心独白 / 旁白 lines are never judged.
        shot = '镜头1（0-4s）：【近景，平视，固定，B 居中，焦点在 B】B 低头量酒。台词（A，内心独白画外，0-3s，英语，是真想知道）："What?"'
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), [])

    def test_wide_shot_intent_is_info_unless_carried(self):
        shot = ('镜头1（0-4s）：【中景双人，平视，固定，A 画左、B 画右，焦点在两人】两人隔着吧台。'
                '台词（A，0-3s，英语，真诚，不推销）："There is a part for you."；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertTrue(any(i.startswith('态度拍子：中景以上 镜头1「真诚，不推销」（A）') for i in attitude_info(result)), result['info'])
        # A body / interaction beat carries it in the wide shot: no INFO.
        result = run(build(shot.replace('两人隔着吧台。', '两人隔着吧台，A 把酒单朝 B 推过去一点。')))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), ['态度拍子：2/2 处意图词有可执行拍子（身体 2）'])
        # An action in the bracket still warns, and it is named as the beat of the intent words beside it.
        result = run(build(shot.replace('真诚，不推销）', '真诚，不推销，抬眼）')))
        hits = w44(result)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('1 处动作「抬眼」（A）', hits[0])
        self.assertIn('写进去后它就是同一括号里态度词的拍子', hits[0])
        self.assertFalse(any('中景以上' in i for i in attitude_info(result)), result['info'])

    def test_voice_only_brackets_never_fire(self):
        shot = ('镜头1（0-4s）：【近景，平视，固定，A 居中，焦点在 A】A 看着 B。'
                '台词（A，0-3s，中文普通话，正常音量，语速慢，句尾停 1 秒）："面刚好。"；此时 B 闭着嘴。')
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), [])

    def test_prompt_without_dialogue_is_silent(self):
        shot = '镜头1（0-4s）：【近景，平视，固定，A 居中，焦点在 A】A 看着杯子。'
        result = run(build(shot))
        self.assertEqual(w44(result), [])
        self.assertEqual(attitude_info(result), [])


if __name__ == '__main__':
    unittest.main()
