"""1.11.0 stage_check.py (S5 §5.11): the shot card closes with a 镜头纵览 and the script checks presence and the E-layer
longest-silence figure. Pattern: the 1.8.0 camera plan (必做段 + 模板表 + 脚本查有没有).
1.15.0: the 25-row 执行卡 is no longer copied onto the card; S01–S03 check the card's own slots (mandatory sections, head
items, the 贯穿要求 buckets). Cards that still carry a 执行卡 are legacy: their S01–S03 findings become NOTEs."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import stage_check as sc  # noqa: E402

TRANSLATION = '- 表演翻译：被逗到 → 外化词典「被逗到 / 认了（轻松）」→ 可见：合着嘴笑，嘴角一边先挑起来，摇一下头；声音：鼻子里轻轻出一口气，不出声\n'
SHOTS = ''.join(f'## 镜头 {n}（0-2s）\n\n**C**：\n{TRANSLATION}- 有序表演块：0–1 s 嘴角一边先挑起来。\n\n' for n in (1, 2, 3))
OVERVIEW = ('## 镜头纵览\n| 镜 | 时间 | 景别 | 机位 / 运镜 | 焦点与虚实 | 台词（句 · 画内 / 画外整句） | 无台词秒 | 脸对镜头角度 | 手法 |\n'
            '|---|---|---|---|---|---|---|---|---|\n'
            '| 1 | 0-2s | 近景 | 手持 | A 眼睛 | A 1 句画内 | 0 | 3/4 | 手持 |\n'
            '| 2 | 2-4s | 近景 | 手持 | B 眼睛 | B 1 句画内 | 1 | 3/4 | 手持 |\n'
            '| 3 | 4-6s | 中景 | 横移 | A | 无 | 2 | 侧面 | 横移 |\n\n')
E_LAYER = '## E 层\n| 项 | 值 |\n|---|---|\n| 峰值镜 | 3 |\n| 最长无台词 | 2 s（镜 3） |\n| 反应镜 | 镜 2 |\n\n'
# 1.15.0 card head: the items S02 reads, the template's inline line, and the three hand-off lines
HEAD_BLOCK = ('场景参数卡：强度低 · 方向外放 · 信息对称 · 权力平 · 进场温度暖 · 密度中\n\n'
              '视觉方案：只推近一次 · 观众问题：她会不会笑出来 · **峰值事件**：她笑出声（镜 3） · 决策载体：文字\n\n'
              '方向句：机位朝北，门在镜头身后，人物朝镜头走来\n\n'
              '交接：\n- 偏好与 skill 冲突：无\n- 剧本回写待办：无\n- 用户已点名：见 QA 现行状态与 ## 历史\n\n')
HEAD = '# 卡\n\n**版本：v1 · 2026-10-27** · 状态：待确认 · film-director 1.15.0\n\n' + HEAD_BLOCK
THROUGH = ('## 贯穿要求\n- 保持一致：人物按各自素材\n- 空间与机位：轴线；方向句；拍人角度一句\n'
           '- 表演约束：站姿、基调句\n- 画面基调贯穿：主光一句\n- 声音：环境声\n\n')
SECTIONS = ('## 走位表\n…\n\n## 机位设计\n\n### 空间锚点\n…\n\n### 机位表\n…\n\n### 核对\n…\n\n'
            '## clip 起始状态\n…\n\n## clip 结束状态\n…\n\n' + THROUGH)
# the 1.11.0–1.14.2 execution card, kept only to build legacy fixtures
LEGACY_ROWS = {
    1: '场景参数卡', 2: '视觉方案与观众问题', 3: '峰值事件与峰值镜', 4: '决策载体', 5: '走位表', 6: '空间锚点',
    7: '机位表', 8: '核对与复核', 9: '镜头纵览', 10: '每句台词的镜头', 11: '无台词段预算', 12: '反应镜清单',
    13: '变化轨', 14: '焦点与虚实', 15: '表演翻译', 16: '表演基线', 17: '拍人角度与摄影', 18: '穿着状态',
    19: '方向句', 20: '衔接', 21: '偏好与 skill 冲突', 22: '用户已点名', 23: '剧本回写待办', 24: '风险登记', 25: '脚本',
}
LEGACY_SECTIONS = SECTIONS.replace(THROUGH, '## 贯穿要求\n…\n\n')


def card_rows(override=None):
    rows = {n: f'见 §{name}' for n, name in LEGACY_ROWS.items()}
    rows.update({5: '## 走位表', 6: '### 空间锚点', 7: '### 机位表', 8: '### 核对；无上一条', 9: '## 镜头纵览',
                 11: 'E 层 最长无台词 2 s', 12: 'E 层 反应镜 镜 2', 16: '## 贯穿要求 表演约束', 20: '## clip 起始状态 / ## clip 结束状态',
                 21: '无', 22: '无', 23: '无', 25: 'camera_plan_check 0 / stage_check 0'})
    for n in (1, 2, 3, 4, 10, 13, 14, 15, 17, 18, 19, 24):
        rows[n] = '卡头 / 各镜 C 层'
    rows.update(override or {})
    return rows


def legacy_table(rows=None):
    rows = rows if rows is not None else card_rows()
    return '## 执行卡\n| # | 项 | 证据 |\n|---|---|---|\n' + ''.join(
        f'| {n} | {LEGACY_ROWS[n]} | {rows[n]} |\n' for n in sorted(rows))


def card(overview=OVERVIEW, e_layer=E_LAYER, shots=SHOTS, head=HEAD, sections=SECTIONS):
    return head + sections + overview + shots + e_layer


def legacy_card(rows=None):
    """A card written before 1.15.0: no head items, no 贯穿要求 buckets, the 25-row table at the end."""
    return '# 卡\n\n' + LEGACY_SECTIONS + OVERVIEW + SHOTS + E_LAYER + legacy_table(rows)


def write(text):
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(text)
    return f.name


def run(text, stage='s5'):
    return sc.check(write(text), stage)


class StageCheckTests(unittest.TestCase):
    def test_filled_card_passes(self):
        path = write(card())
        errors, warns = sc.check(path, 's5')
        self.assertEqual(errors, [], errors)
        self.assertEqual(warns, [], warns)
        self.assertEqual(sc.notes(path), [])

    def test_missing_mandatory_section_is_s01(self):
        errors, _ = run(card(sections=SECTIONS.replace('## 走位表\n…\n\n', '')))
        self.assertTrue(any(e.startswith('S01') and '走位表' in e for e in errors), errors)
        errors, _ = run(card(sections=SECTIONS.replace('## clip 结束状态\n…\n\n', '')))
        self.assertTrue(any(e.startswith('S01') and 'clip 结束状态' in e for e in errors), errors)

    def test_missing_or_placeholder_head_item_is_s02(self):
        errors, _ = run(card(head=HEAD.replace('场景参数卡：强度低 · 方向外放 · 信息对称 · 权力平 · 进场温度暖 · 密度中\n\n', '')))
        self.assertTrue(any(e.startswith('S02') and '场景参数卡' in e for e in errors), errors)
        errors, _ = run(card(head=HEAD.replace('**峰值事件**：她笑出声（镜 3）', '**峰值事件**（落在镜 N）：__（镜 __）')))
        self.assertTrue(any(e.startswith('S02') and '峰值事件' in e and '占位' in e for e in errors), errors)
        errors, _ = run(card(head=HEAD.replace('- 用户已点名：见 QA 现行状态与 ## 历史\n', '')))
        self.assertTrue(any(e.startswith('S02') and '用户已点名' in e for e in errors), errors)

    def test_hand_off_lines_may_say_none(self):
        errors, _ = run(card())
        self.assertFalse(any(e.startswith('S02') for e in errors), errors)
        errors, _ = run(card(head=HEAD.replace('- 剧本回写待办：无', '- 剧本回写待办：__')))
        self.assertTrue(any(e.startswith('S02') and '剧本回写待办' in e for e in errors), errors)

    def test_old_direction_label_counts_only_at_line_start(self):
        old = HEAD.replace('方向句：机位朝北，门在镜头身后，人物朝镜头走来', '- **方向**：坡上 = 北，坡下 = 南')
        errors, _ = run(card(head=old))
        self.assertFalse(any(e.startswith('S02') and '方向句' in e for e in errors), errors)
        # 场景参数卡 里的「方向外放」/「· 方向：外放」不是方向句
        inline = HEAD.replace('方向句：机位朝北，门在镜头身后，人物朝镜头走来\n\n', '').replace('方向外放', '方向：外放')
        errors, _ = run(card(head=inline))
        self.assertTrue(any(e.startswith('S02') and '方向句' in e for e in errors), errors)

    def test_missing_through_bucket_is_s03(self):
        errors, _ = run(card(sections=SECTIONS.replace('- 表演约束：站姿、基调句\n', '')))
        self.assertTrue(any(e.startswith('S03') and '表演约束' in e and '站姿' in e for e in errors), errors)
        # a bucket is a bullet that starts with its name; the word inside another bullet does not count
        inside = SECTIONS.replace('- 表演约束：站姿、基调句\n', '').replace('- 声音：环境声', '- 声音：环境声，表演约束见上')
        errors, _ = run(card(sections=inside))
        self.assertTrue(any(e.startswith('S03') and '表演约束' in e for e in errors), errors)

    def test_short_bucket_names_count(self):
        short = SECTIONS.replace('- 表演约束：站姿、基调句', '- **表演**：站姿挺直').replace('- 空间与机位：', '- **摄影**：')
        errors, _ = run(card(sections=short))
        self.assertFalse(any(e.startswith('S03') for e in errors), errors)

    def test_legacy_card_downgrades_to_notes(self):
        path = write(legacy_card())
        errors, warns = sc.check(path, 's5')
        self.assertEqual(errors, [], errors)
        self.assertEqual(warns, [], warns)
        notes = sc.notes(path)
        self.assertTrue(notes and notes[0].startswith('旧卡还有「## 执行卡」'), notes)
        self.assertTrue(any('旧卡（不报错）S02' in n and '场景参数卡' in n for n in notes), notes)
        self.assertTrue(any('旧卡（不报错）S03' in n for n in notes), notes)
        # rows 21–23 count as the three hand-off lines
        findings = [n for n in notes if n.startswith('旧卡（不报错）')]
        self.assertFalse(any(k in n for n in findings for k in ('偏好与 skill 冲突', '剧本回写待办', '用户已点名')), findings)

    def test_new_card_that_copied_the_old_table_stays_strict(self):
        text = card(head=HEAD.replace('场景参数卡：强度低 · 方向外放 · 信息对称 · 权力平 · 进场温度暖 · 密度中\n\n', '')) + legacy_table()
        path = write(text)
        errors, _ = sc.check(path, 's5')
        self.assertTrue(any(e.startswith('S02') and '场景参数卡' in e for e in errors), errors)
        self.assertTrue(any(n.startswith('卡里还抄着「## 执行卡」') for n in sc.notes(path)), sc.notes(path))
        self.assertFalse(sc.is_legacy(text))
        self.assertTrue(sc.is_legacy(legacy_card()))
        self.assertTrue(sc.is_legacy(legacy_card().replace('# 卡\n\n', '# 卡\n\n**版本：v2 · 10-26**（film-director 1.14.2）\n\n')))

    def test_not_applicable_slots_are_listed(self):
        head = HEAD.replace('方向句：机位朝北，门在镜头身后，人物朝镜头走来', '方向句：不适用：全程固定，没有走位')
        e_layer = E_LAYER.replace('| 反应镜 | 镜 2 |', '| 反应镜 | 不适用：单人戏 |')
        path = write(card(head=head, e_layer=e_layer))
        self.assertEqual(sc.check(path, 's5')[0], [])
        notes = sc.notes(path)
        self.assertTrue(any(n.startswith('写了「不适用」的格子') and '方向句' in n and '反应镜' in n for n in notes), notes)
        # the hand-off lines saying 无 are a normal answer, not listed
        self.assertFalse(any('偏好与 skill 冲突' in n for n in notes), notes)

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

    def test_missing_translation_line_is_s04(self):
        shots = SHOTS.replace(TRANSLATION, '', 1)
        errors, _ = run(card(shots=shots))
        self.assertTrue(any(e.startswith('S04') and '镜头1' in e for e in errors), errors)

    def test_two_segment_translation_is_s04(self):
        shots = SHOTS.replace(TRANSLATION, '- 表演翻译：不可思议 → 皱眉、括号口气\n')
        errors, _ = run(card(shots=shots))
        self.assertTrue(any(e.startswith('S04') and '不是三段' in e for e in errors), errors)

    def test_middle_segment_must_be_a_lexicon_row_or_library_entry(self):
        bad = SHOTS.replace(TRANSLATION, '- 表演翻译：不可思议 → 皱眉 → 眉头一皱\n')
        errors, _ = run(card(shots=bad))
        self.assertTrue(any(e.startswith('S05') for e in errors), errors)
        lib = SHOTS.replace(TRANSLATION, '- 表演翻译：被拆穿 → 情绪库 13 → 可见：眉毛一抬，鼻子里笑出一口气；声音："啊？"的口气\n')
        errors, _ = run(card(shots=lib))
        self.assertFalse(any(e.startswith('S05') for e in errors), errors)
        none = SHOTS.replace(TRANSLATION, '- 表演翻译：无（物件插入）\n')
        errors, _ = run(card(shots=none))
        self.assertFalse(any(e.startswith(('S04', 'S05')) for e in errors), errors)

    def test_third_segment_without_voice_half_is_w_c10(self):
        shots = SHOTS.replace(TRANSLATION, '- 表演翻译：被逗到 → 外化词典「被逗到 / 认了（轻松）」→ 合着嘴笑，摇一下头\n')
        _, warns = run(card(shots=shots))
        self.assertTrue(any(w.startswith('W-C10') for w in warns), warns)
        _, warns = run(card())
        self.assertFalse(any(w.startswith('W-C10') for w in warns), warns)

    def test_a_layer_word_in_c_layer_line_is_w_c9(self):
        shots = SHOTS.replace('- 有序表演块：0–1 s 嘴角一边先挑起来。', '- 有序表演块：0–1 s 一脸不信，觉得不可思议。')
        _, warns = run(card(shots=shots))
        self.assertTrue(any(w.startswith('W-C9') and '不信' in w for w in warns), warns)

    def test_template_card_has_every_slot_the_checks_read(self):
        template = (ROOT / 'templates' / 'shot-card.md').read_text(encoding='utf-8')
        self.assertNotIn('## 执行卡', template)
        head = sc.head_region(template)
        for names in sc.HEAD_ITEMS:
            self.assertIsNotNone(sc.head_value(head, names), names[0])
        for name in sc.REQUIRED_SECTIONS:
            self.assertIn(f'## {name}', template)
        through = sc.section(template, '贯穿要求')
        for bucket in sc.THROUGH_BUCKETS:
            self.assertIn(bucket, through)
        self.assertIn('## 镜头纵览', template)


if __name__ == '__main__':
    unittest.main()
