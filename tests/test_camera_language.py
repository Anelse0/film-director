"""1.9.0 camera language: presence / support / movement / character as four separate decisions
(director-grammar §2.5, from a user-supplied note without sources), a Seedance risk table built only from the
capabilities doc and this project's renders, and the dolly-zoom direction fix (the note and the skill both had
"dolly back + zoom in -> background stretched away"; Wikipedia's diagram caption: background grows bigger)."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import camera_library as cl  # noqa: E402


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def section(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]


def table_rows(block, header_start):
    lines = block[block.index(header_start):].splitlines()
    rows = []
    for line in lines[2:]:
        if not line.startswith('|'):
            break
        rows.append([c.strip() for c in line.strip('|').split('|')])
    return rows


class DollyZoomTests(unittest.TestCase):
    def test_direction_is_corrected_in_both_docs(self):
        grammar, vocab = read('references/director-grammar.md'), read('references/camera-vocabulary.md')
        for text in (grammar, vocab):
            row = next(l for l in text.splitlines() if l.startswith('| 希区柯克变焦'))
            self.assertIn('机器后拉同时变焦推近，人物大小不变、背景变大压向人物', row)
            self.assertIn('背景变小退远', row)
            self.assertNotIn('变焦推近，人物大小不变、背景被拉远', row)   # 旧的错误示例
            self.assertNotIn('| "人物大小不变、背景被拉远" |', row)
        self.assertIn('the teapots in the background grow bigger', grammar)


class SectionTests(unittest.TestCase):
    def setUp(self):
        self.g = read('references/director-grammar.md')
        self.s25 = section(self.g, '### 2.5 摄影机身份、支撑与运动质感', '## 三、')

    def test_order_and_originals_kept(self):
        heads = ['### 2.1 动机原则', '### 2.2 各运动的叙事职能与终点', '### 2.3 长镜头的理由',
                 '### 2.4 运镜库：执行语法', '### 2.5 摄影机身份、支撑与运动质感', '## 三、人物动线与调度']
        pos = [self.g.index(h) for h in heads]
        self.assertEqual(pos, sorted(pos))
        self.assertIn("it's got to be for a reason within the story", self.g)  # §2.1 Deakins 原文仍在
        self.assertIn('用户提供资料《摄影机运动与支撑语言》（2026-09-23，未注出处）', self.s25)
        self.assertIn('`[第三方·未注出处]`', self.s25)

    def test_four_layers_presence_support_character(self):
        layers = [r[0] for r in table_rows(self.s25, '| 层 | 回答 | 写在哪 |')]
        self.assertEqual(layers, ['摄影机身份', '支撑', '运动', '质感'])
        presence = [r[0] for r in table_rows(self.s25, '| 身份 | 观众的位置 | 常见搭配 |')]
        self.assertEqual(presence, ['旁观', '亲密观察', '参与', '陪伴', '引导', '追随', '全知', '角色主观', '显性摄影机'])
        self.assertIn('只是候选，不是映射', self.s25)
        self.assertIn('身份和"视点"是两件事', self.s25)
        support = table_rows(self.s25, '| 支撑 | 运动质感 |')
        self.assertEqual(len(support), 11)
        for name, _q, _fit, risk, how in support:
            self.assertTrue(risk and how, name)
            if name in ('肩扛', '稳定器', '车载', '身体固定（Snorricam）'):
                self.assertIn('非官方术语', how, name)  # 不单写器材名
        chars = [r[0] for r in table_rows(self.s25, '| 质感 | 写进 Prompt |')]
        self.assertEqual(chars, ['几乎无感', '克制', '精确', '漂浮', '有机', '紧张 / 攻击性'])

    def test_risk_table_every_row_has_evidence_and_a_handling(self):
        rows = table_rows(self.s25, '| # | 情形 | 资料里说适合的例子 | 依据 | 处理 |')
        self.assertEqual([r[0] for r in rows], list('①②③④⑤⑥⑦'))
        for num, case, fit, basis, handling in rows:
            self.assertRegex(basis, r'`\[(官方|第三方|实测·单样本|未验证)\]`|本 skill', num)
            self.assertTrue(fit and handling, num)
        self.assertIn('不是禁用', self.s25)
        self.assertIn('只有四人', rows[0][3])              # THE ORDER EP03 s04 clip01 实测
        self.assertIn('弧移和环绕不用于两人对白', rows[2][4])


class WiringTests(unittest.TestCase):
    def test_s5_card_s6_s7_skill(self):
        s5 = read('references/stage-5-directing-storyboard.md')
        self.assertIn('本场运动逻辑', s5)
        self.assertIn('同一行先写**摄影机身份**', s5)
        for row in ('| 靠近人物、和他一起承受（1.9.0） | 克制手持 |', '| 跟人物进入新空间（1.9.0） |',
                    '| 强化两人关系（1.9.0） |', '| 审判 / 无处可逃 / 对比基础 | 固定 |', '| 揭示信息 | 摇 / 横移 / 后拉 |'):
            self.assertIn(row, s5)
        self.assertIn('先过它的风险表 ①–⑦', s5)
        card = read('templates/shot-card.md')
        self.assertIn('摄影机身份（按场；本 clip 有变化时写理由', card)
        self.assertIn('- 支撑 / 质感（可选', card)
        s6 = read('references/stage-6-prompt-compiler.md')
        self.assertIn('**支撑与质感**（1.9.0', s6)
        self.assertIn('摄影机身份属 A 层，不进 Prompt', s6)
        s7 = read('references/stage-7-qa-continuity.md')
        self.assertIn('| 摄影机身份与支撑 |', s7)
        self.assertIn('| 运动质感不对（', s7)
        for row in ('| 运镜库 |', '| 导演语法 |', '| 起止状态 |', '画面始终没有变化的感觉'):
            self.assertIn(row, s7)   # 原有审阅行保留
        skill = read('SKILL.md')
        self.assertIn('"摄影机该站在哪 / 用手持还是稳定器 / 这个镜头什么质感"', skill)
        self.assertIn('摄影机身份（观众站在哪里）按场定，换身份要有理由', skill)
        self.assertIn('支撑（手持 / 克制手持', read('references/camera-vocabulary.md'))

    def test_validation_log_records_renders_and_queue(self):
        log = read('references/validation-log.md')
        self.assertIn('| 2026-09-23 | THE ORDER EP03 场 4 clip01–03', log)
        self.assertRegex(log, r'\n15\. 运动质感能否被区分')
        self.assertRegex(log, r'\n16\. 侧跟拍 / 弧移配 ≥8 词的台词')

    def test_index_layer_and_support(self):
        index = cl.load_index()
        for i, row in index.items():
            self.assertIn(row['layer'], ('运动', '支撑', '特效'), i)
            self.assertTrue(row['support'], i)
        self.assertEqual(sorted(i for i, r in index.items() if r['layer'] == '支撑'), ['shot-21', 'shot-23', 'shot-24'])
        text = cl.slots(cl.load_library()['shot-23'], index['shot-23'])
        self.assertIn('层：支撑　默认支撑：手持', text)


if __name__ == '__main__':
    unittest.main()
