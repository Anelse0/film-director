"""1.11.0 stage_check.py (S5 §5.11): the shot card closes with a filled 执行卡 and a 镜头纵览; the script checks presence,
referenced sections, and the E-layer longest-silence figure. Pattern: the 1.8.0 camera plan (必做段 + 模板表 + 脚本查有没有)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import stage_check as sc  # noqa: E402

SHOTS = ''.join(f'## 镜头 {n}（0-2s）\n\n**C**：……\n\n' for n in (1, 2, 3))
OVERVIEW = ('## 镜头纵览\n| 镜 | 时间 | 景别 | 机位 / 运镜 | 焦点与虚实 | 台词（句 · 画内 / 画外整句） | 无台词秒 | 脸对镜头角度 | 手法 |\n'
            '|---|---|---|---|---|---|---|---|---|\n'
            '| 1 | 0-2s | 近景 | 手持 | A 眼睛 | A 1 句画内 | 0 | 3/4 | 手持 |\n'
            '| 2 | 2-4s | 近景 | 手持 | B 眼睛 | B 1 句画内 | 1 | 3/4 | 手持 |\n'
            '| 3 | 4-6s | 中景 | 横移 | A | 无 | 2 | 侧面 | 横移 |\n\n')
E_LAYER = '## E 层\n| 项 | 值 |\n|---|---|\n| 峰值镜 | 3 |\n| 最长无台词 | 2 s（镜 3） |\n| 反应镜 | 镜 2 |\n\n'
SECTIONS = ('## 走位表\n…\n\n## 机位设计\n\n### 空间锚点\n…\n\n### 机位表\n…\n\n### 核对\n…\n\n'
            '## clip 起始状态\n…\n\n## clip 结束状态\n…\n\n## 贯穿要求\n…\n\n')


def card_rows(override=None):
    rows = {n: f'见 §{name}' for n, name in sc.CARD_ROWS.items()}
    rows.update({5: '## 走位表', 6: '### 空间锚点', 7: '### 机位表', 8: '### 核对；无上一条', 9: '## 镜头纵览',
                 11: 'E 层 最长无台词 2 s', 12: 'E 层 反应镜 镜 2', 16: '## 贯穿要求 表演约束', 20: '## clip 起始状态 / ## clip 结束状态',
                 21: '无', 22: '无', 23: '无', 25: 'camera_plan_check 0 / stage_check 0'})
    for n in (1, 2, 3, 4, 10, 13, 14, 15, 17, 18, 19, 24):
        rows[n] = '卡头 / 各镜 C 层'
    rows.update(override or {})
    return rows


def card(rows=None, overview=OVERVIEW, e_layer=E_LAYER, with_card=True):
    text = '# 卡\n\n' + SECTIONS + overview + SHOTS + e_layer
    if with_card:
        rows = rows if rows is not None else card_rows()
        table = '## 执行卡\n| # | 项 | 证据 |\n|---|---|---|\n' + ''.join(
            f'| {n} | {sc.CARD_ROWS[n]} | {rows[n]} |\n' for n in sorted(rows))
        text += table
    return text


def run(text, stage='s5'):
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(text)
    return sc.check(f.name, stage)


class StageCheckTests(unittest.TestCase):
    def test_filled_card_passes(self):
        errors, warns = run(card())
        self.assertEqual(errors, [], errors)
        self.assertEqual(warns, [], warns)

    def test_missing_card_is_s01(self):
        errors, _ = run(card(with_card=False))
        self.assertTrue(any(e.startswith('S01') for e in errors), errors)

    def test_missing_row_and_placeholder_are_s02(self):
        rows = card_rows()
        del rows[12]
        rows[11] = '__'
        errors, _ = run(card(rows=rows))
        self.assertTrue(any(e.startswith('S02') and '12 反应镜清单' in e for e in errors), errors)
        self.assertTrue(any(e.startswith('S02') and '第 11 行' in e for e in errors), errors)

    def test_reference_to_missing_section_is_s03(self):
        errors, _ = run(card(rows=card_rows({5: '## 走位与机位表'})))
        self.assertTrue(any(e.startswith('S03') and '走位与机位表' in e for e in errors), errors)

    def test_overview_missing_or_short_is_c11(self):
        errors, _ = run(card(overview=''))
        self.assertTrue(any(e.startswith('C11') for e in errors), errors)
        short = OVERVIEW.replace('| 3 | 4-6s | 中景 | 横移 | A | 无 | 2 | 侧面 | 横移 |\n', '')
        errors, _ = run(card(overview=short))
        self.assertTrue(any(e.startswith('C11') and '2 行' in e for e in errors), errors)

    def test_overview_missing_column_is_c11(self):
        errors, _ = run(card(overview=OVERVIEW.replace('| 脸对镜头角度 ', '| 脸 ')))
        self.assertTrue(any(e.startswith('C11') and '角度' in e for e in errors), errors)

    def test_e_layer_rows_missing_is_w_c6(self):
        _, warns = run(card(e_layer='## E 层\n| 项 | 值 |\n|---|---|\n| 峰值镜 | 3 |\n\n'))
        self.assertTrue(any(w.startswith('W-C6') and '最长无台词' in w and '反应镜' in w for w in warns), warns)

    def test_longest_silence_over_three_seconds_is_w_c7_and_tunable(self):
        over = E_LAYER.replace('| 最长无台词 | 2 s（镜 3） |', '| 最长无台词 | 4 s（镜 3） |')
        _, warns = run(card(e_layer=over))
        self.assertTrue(any(w.startswith('W-C7') for w in warns), warns)
        _, warns = run(card(e_layer=over + '| 最长无台词上限 | 4 |\n'))
        self.assertFalse(any(w.startswith('W-C7') for w in warns), warns)

    def test_off_screen_without_whole_line_is_w_c8(self):
        _, warns = run(card(overview=OVERVIEW.replace('| B 1 句画内 |', '| A 后半句画外 |')))
        self.assertTrue(any(w.startswith('W-C8') for w in warns), warns)
        _, warns = run(card(overview=OVERVIEW.replace('| B 1 句画内 |', '| A 1 句画外整句 |')))
        self.assertFalse(any(w.startswith('W-C8') for w in warns), warns)

    def test_template_card_has_all_rows(self):
        template = (ROOT / 'templates' / 'shot-card.md').read_text(encoding='utf-8')
        for n, name in sc.CARD_ROWS.items():
            self.assertIn(f'| {n} | {name} |', template)
        self.assertIn('## 镜头纵览', template)


if __name__ == '__main__':
    unittest.main()
