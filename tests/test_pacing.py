"""W22/W23 dialogue-pacing hints (1.3.0): presence-only WARNs, production only."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_prompt import validate  # noqa: E402

HEAD = ('【素材绑定】无参考素材。\n【总述】{dur}秒 9:16，室内，两人对话。\n【起始状态】A 在画左，B 在画右，机位中景。\n'
        '【整体情绪弧线】平静 → 紧。\n- A：平静（镜1，抬眼）→ 紧（镜末，抿嘴）\n【分镜时间线】\n')
TAIL = '【贯穿要求】A 外观锁；B 外观锁；无 bgm，只有环境音与台词；不要字幕。\n\n| 项 | 值 |\n|---|---|\n| duration | {dur} |\n'


def prompt(shots, dur):
    return HEAD.format(dur=dur) + '\n'.join(shots) + '\n' + TAIL.format(dur=dur)


def shot(no, a, b, tag='中景，正面，固定', lines=()):
    body = f'镜头{no}（{a}-{b}s）：【{tag}】〔A：平静〕A 抬眼看 B。'
    for i, line in enumerate(lines):
        body += f' 台词（A，{a}-{b}s，英语）："{line}"（说法：平）；B 闭着嘴。'
    return body


def run(text, artifact='production'):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'p.md'
        p.write_text(text, encoding='utf-8')
        return validate(p, artifact=artifact)


def codes(result, code):
    return [w for w in result['warnings'] if w.startswith(code)]


class PacingTests(unittest.TestCase):
    def test_single_line_seven_second_shot_warns(self):
        r = run(prompt([shot(1, 0, 3), shot(2, 3, 10, '近景，侧面，微推', ['Hello there.'])], 10))
        self.assertEqual(r['errors'], [])
        self.assertEqual(len(codes(r, 'W22')), 1)
        self.assertIn('镜头2(7s/1句)', codes(r, 'W22')[0])

    def test_two_line_seven_second_shot_is_a_beat_not_a_stretch(self):
        r = run(prompt([shot(1, 0, 3), shot(2, 3, 10, '近景，侧面，微推', ['Hi.', 'Hi back.'])], 10))
        self.assertEqual(codes(r, 'W22'), [])

    def test_nine_second_multi_line_shot_still_warns(self):
        r = run(prompt([shot(1, 0, 3), shot(2, 3, 12, '近景，侧面，微推', ['Hi.', 'Hi back.', 'Well.'])], 12))
        self.assertEqual(len(codes(r, 'W22')), 1)

    def test_voiceover_and_single_shot_clip_are_exempt(self):
        vo = '镜头2（3-11s）：【全景，俯拍，缓推】〔空镜〕校园。旁白（Lena，3-10s，英语）："This is the school."；画面无人说话。'
        r = run(prompt([shot(1, 0, 3), vo], 11))
        self.assertEqual(codes(r, 'W22'), [])
        one = prompt([shot(1, 0, 20, '中景，正面，固定', ['One long take.'])], 20)
        self.assertEqual(codes(run(one), 'W22'), [])

    def test_identical_tags_three_in_a_row_warn_but_variation_does_not(self):
        same = [shot(1, 0, 3), shot(2, 3, 6), shot(3, 6, 9), shot(4, 9, 12, '特写，正面，固定')]
        r = run(prompt(same, 12))
        self.assertEqual(len(codes(r, 'W23')), 1)
        self.assertIn('镜头1–3', codes(r, 'W23')[0])
        varied = [shot(1, 0, 3, '中景，正面，固定'), shot(2, 3, 6, '中景，侧面，固定'), shot(3, 6, 9, '中景，正面，微推')]
        self.assertEqual(codes(run(prompt(varied, 9)), 'W23'), [])

    def test_w04_follows_average_shot_length_not_shot_count(self):
        # Official 2.5 guide example: 9 shots / 30s, one line per 3-4s shot.
        nine = [shot(1, 0, 3, '全景，仰拍，固定'), shot(2, 3, 6, '中景，正面，手持'), shot(3, 6, 10, '特写，正面，固定'),
                shot(4, 10, 14, '全景，仰摇'), shot(5, 14, 18, '全景，正面，固定'), shot(6, 18, 22, '特写，正面，固定'),
                shot(7, 22, 25, '近景，正面，固定'), shot(8, 25, 28, '近景，仰拍，固定'), shot(9, 28, 30, '全景，背影，固定')]
        r = run(prompt(nine, 30))
        self.assertEqual(r['errors'], [])
        self.assertEqual(codes(r, 'W04'), [])
        dense = [shot(i + 1, int(i * 1.5), int((i + 1) * 1.5), f'{"中景" if i % 2 else "近景"}，正面，固定') for i in range(12)]
        r = run(prompt(dense, 18))
        self.assertTrue(any('平均镜长' in w for w in codes(r, 'W04')))
        self.assertTrue(any('< 1.5s' in w for w in codes(r, 'W04')))

    def test_performance_artifact_never_emits_pacing_codes(self):
        text = '【表演条件】12秒。\n【表演时间线】\n节拍 1（0-12s）：她说 "I am fine." 然后闭嘴。'
        r = run(text, artifact='performance')
        self.assertEqual(codes(r, 'W22') + codes(r, 'W23'), [])

    def test_pacing_codes_are_warnings_not_errors(self):
        r = run((ROOT / 'examples/bad-example-3-lazy-long-take.prompt.md').read_text(encoding='utf-8'))
        self.assertEqual(r['errors'], [])
        self.assertTrue(codes(r, 'W22') and codes(r, 'W23'))


if __name__ == '__main__':
    unittest.main()
