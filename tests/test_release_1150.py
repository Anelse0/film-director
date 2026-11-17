"""1.15.0 release wiring (user 2026-10-27): the 25-row 执行卡 is no longer copied onto each shot card — the questions live
on as the stage-5 §5.11 收口对照表, the card answers them in its own slots, and stage_check.py S01–S03 check those slots
directly (legacy cards: NOTE). Records are written once: the user's words only in QA ## 历史, old review rounds are
rewritten in place, QA opens at dock A; check.py qa gives three record NOTEs. No new W code (freeze)."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


OLD_ROWS = ('场景参数卡', '视觉方案与观众问题', '峰值事件与峰值镜', '决策载体', '走位表', '空间锚点', '机位表', '核对与复核',
            '镜头纵览', '每句台词的镜头', '无台词段预算', '反应镜清单', '变化轨', '焦点与虚实', '表演翻译', '表演基线',
            '拍人角度与摄影', '穿着状态', '方向句', '衔接', '偏好与 skill 冲突', '用户已点名', '剧本回写待办', '风险登记', '脚本')


class WiringTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.15.1')
        log = read('CHANGELOG.md')
        self.assertIn('## 1.15.0', log)
        self.assertLess(log.index('## 1.15.0'), log.index('## 1.14.2'))
        self.assertIn('1.15.0', read('tests/test_protected_zone.py'))

    def test_the_card_no_longer_carries_the_table_but_the_questions_survive(self):
        card = read('templates/shot-card.md')
        self.assertNotIn('## 执行卡', card)
        stage5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('## 5.11 分镜卡收口对照表', stage5)
        for n, name in enumerate(OLD_ROWS, 1):
            self.assertIn(f'| {n} | {name} |', stage5)

    def test_the_four_rule_phrases_have_a_slot_on_the_card(self):
        card = read('templates/shot-card.md')
        self.assertRegex(card, r'- 表演约束：[^\n]*站姿 / 基调句')
        self.assertRegex(card, r'- 空间与机位：[^\n]*拍人角度与摄影一句')
        self.assertRegex(card, r'`无声段理由`（[^）]*叠进相邻台词的动作')
        self.assertRegex(card, r'\*\*决策载体\*\*（[^\n]*为什么不用关键帧')
        self.assertIn('卡头「决策载体」一项要答"为什么不用关键帧"', read('SKILL.md'))

    def test_head_items_and_hand_off_lines(self):
        import stage_check as sc
        card = read('templates/shot-card.md')
        head = sc.head_region(card)
        for names in sc.HEAD_ITEMS:
            self.assertIsNotNone(sc.head_value(head, names), names[0])
        self.assertIn('**用户已点名**：见 QA 现行状态', card)
        self.assertNotIn('Prompt v__', card.split('\n## ')[0])  # version line: four items

    def test_no_pointer_to_old_rows_left_in_the_rules(self):
        for name in ('SKILL.md', 'references/stage-5-directing-storyboard.md', 'references/stage-7-qa-continuity.md',
                     'templates/shot-card.md', 'templates/qa.md'):
            text = read(name)
            self.assertIsNone(re.search(r'执行卡第\s*\d+\s*行', text), name)
            self.assertNotIn('25 行都有证据', text)

    def test_records_written_once(self):
        qa = read('templates/qa.md')
        self.assertIn('停靠 A 第一次把方案写进分镜卡时建这个文件', qa)
        self.assertIn('旧轮不留', qa)
        self.assertNotIn('被推翻的旧节不删', qa)
        self.assertIn('- 分镜检查：stage_check', qa)
        self.assertIn('用户同意保留（历史 vX）', qa)
        skill = read('SKILL.md')
        self.assertIn('记录只写一处（1.15.0）', skill)
        self.assertIn('规则有但没执行的，写它本该在卡上哪一格被拦住', skill)
        self.assertIn('| 抽卡记录 | 每次成片一行', read('references/stage-6-prompt-compiler.md'))

    def test_machine_line_label_and_record_notes(self):
        import check
        self.assertIn('分镜检查', check.STATE_ORDER)
        self.assertNotIn('执行卡', check.STATE_ORDER)
        self.assertEqual(check.LEGACY_LABELS, {'分镜检查': '执行卡'})
        self.assertEqual((check.HISTORY_ENTRY_MAX, check.NAMED_LINE_MAX), (300, 200))

    def test_no_new_w_code(self):
        codes = set()
        for path in (ROOT / 'scripts').glob('*.py'):
            codes |= {int(c) for c in re.findall(r'\bW(\d{2})\b', path.read_text(encoding='utf-8'))}
        self.assertLessEqual(max(codes), 57)


if __name__ == '__main__':
    unittest.main()
