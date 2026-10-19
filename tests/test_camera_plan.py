"""1.8.0 camera-position plan (S5 §5.1g): camera_plan_check.py checks that the plan was done —
section present, anchors give the reference view and frame sides, one filled row per shot, five review items answered.
1.9.0: with absolute bearings in the anchors and the row's facing, C09 checks that the frame sides are right
(W-C3 when bearings are missing, W-C4 bare "能" with no reach line, W-C5 corridor-relative wall names).
1.10.0: --prompt cross-checks each row against the same prompt shot (C10, explicit contradictions only)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import camera_plan_check as cpc  # noqa: E402

HEADER = '| 镜 | 机位在哪 | 朝哪拍 | 画左有什么 | 画右有什么 | 人物在画面哪里、脸朝哪 | 动作做得出来吗 | 和参考图视角 |\n|---|---|---|---|---|---|---|---|\n'
ROW = '| {n} | 走廊里正对门 | 朝北，朝门 | 门 | 墙纸 | 中间，正面 | 能 | 一致 |\n'
REVIEW = ('### 核对\n\n1. 左右：一律画左 / 画右。\n2. 换边：无反打。\n3. 动作可行：都做得到。\n'
          '4. 参考图视角：和场景图一致。\n5. 上一条成片：首帧对上了。\n')
BEARING = '方位：门=北，西长墙=西，东长墙=东，东窄墙=东北，走廊另一头=南\n可达：站在东窄墙前，画左那只手够得到门板铰链一侧，够不到门把手。\n'
ANCHORS = '### 空间锚点\n\n场景图视角：从走廊看门。门在画面中间，Theo 站的窄墙在画右。上一条成片末帧：无。\n' + BEARING + '\n'
PRESENCE_ONLY = '### 空间锚点\n\n场景图视角：从走廊看门。门在画面中间，Theo 站的窄墙在画右。上一条成片末帧：无。\n\n'
UPSTREAM = '### 空间锚点\n\n场景图视角：从走廊看门。门在画面中间，Theo 站的窄墙在画右。上一条成片末帧：clip01 成片末帧，门在 Theo 画左。\n' + BEARING + '\n'
RECHECK = ('### 复核\n\n上一条成片：clip01.mp4（Prompt v1.4）\n末帧：门和名牌在 Theo 画左，墙纸在画右。\n'
           '对照：和起草时相反。\n改动：镜 1–8 镜像。\n\n')


def card(shots=(1, 2), rows=None, review=REVIEW, anchors=ANCHORS, plan=True, recheck=''):
    rows = rows if rows is not None else shots
    body = ''.join(f'## 镜头 {n}（0-2s）\n\n**C**：……\n\n' for n in shots)
    if not plan:
        return body
    table = '### 机位表\n\n' + HEADER + ''.join(ROW.format(n=n) for n in rows) + '\n'
    return '# 卡\n\n## 机位设计\n\n' + anchors + table + review + '\n' + recheck + '---\n\n' + body


def run(text, stage='s6'):
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(text)
    return cpc.check(f.name, stage)


class CameraPlanTests(unittest.TestCase):
    def test_complete_plan_passes(self):
        errors, warns = run(card())
        self.assertEqual(errors, [])
        self.assertEqual(warns, [])

    def test_missing_section_is_error(self):
        errors, _ = run(card(plan=False))
        self.assertTrue(any(e.startswith('C01') for e in errors))

    def test_missing_shot_row(self):
        errors, _ = run(card(shots=(1, 2, 3), rows=(1, 2)))
        self.assertTrue(any('C05' in e and '镜3' in e for e in errors))

    def test_placeholder_cell(self):
        text = card().replace('| 2 | 走廊里正对门 |', '| 2 | __ |')
        errors, _ = run(text)
        self.assertTrue(any('C06' in e and '镜2' in e for e in errors))

    def test_review_item_without_conclusion(self):
        errors, _ = run(card(review=REVIEW.replace('都做得到。', '')))
        self.assertTrue(any('C07' in e and '动作可行' in e for e in errors))

    def test_anchor_needs_view_and_frame_side(self):
        errors, _ = run(card(anchors='### 空间锚点\n\n门在中间。\n\n'))
        self.assertTrue(any('视角' in e for e in errors))
        self.assertTrue(any('画左 / 画右' in e for e in errors))

    def test_body_side_words_without_frame_side(self):
        row = '| 1 | 走廊里正对门 | 朝门 | 门在他右肩旁 | 墙纸 | 中间 | 能 | 一致 |\n'
        text = card(shots=(1,), rows=()).replace(HEADER, HEADER + row)
        _, warns = run(text)
        self.assertTrue(any('W-C1' in w for w in warns))

    def test_upstream_field_required(self):
        errors, _ = run(card(anchors=ANCHORS.replace('上一条成片末帧：无。', '')))
        self.assertTrue(any('C03' in e and '上一条成片末帧' in e for e in errors))

    def test_no_upstream_needs_no_recheck(self):
        errors, warns = run(card())
        self.assertFalse(any('C08' in e for e in errors))
        self.assertFalse(any('W-C2' in w for w in warns))

    def test_upstream_without_recheck_blocks_s6_and_warns_at_s5(self):
        errors, _ = run(card(anchors=UPSTREAM))
        self.assertTrue(any(e.startswith('C08') for e in errors))
        errors, warns = run(card(anchors=UPSTREAM), stage='s5')
        self.assertFalse(any(e.startswith('C08') for e in errors))
        self.assertTrue(any(w.startswith('W-C2') for w in warns))

    def test_recheck_with_placeholder_field(self):
        errors, _ = run(card(anchors=UPSTREAM, recheck=RECHECK.replace('镜 1–8 镜像。', '__')))
        self.assertTrue(any('C08' in e and '改动' in e for e in errors))

    def test_upstream_with_recheck_passes(self):
        errors, warns = run(card(anchors=UPSTREAM, recheck=RECHECK))
        self.assertEqual(errors, [])
        self.assertEqual(warns, [])

    def test_wrong_case_d8_passes_presence_check(self):
        """Known gap, kept on purpose (user 2026-10-19): offset EP06 clip02 shot 2 writes the camera shifted to the
        corridor's left while the door sits left of centre. Facing the door, a camera shifted left sees the door right
        of centre, so the row is wrong. Written the 1.8.0 way (no bearings) the checker only checks that the row is
        filled, so it still passes; 1.9.0 adds W-C3 to say the sides could not be checked."""
        row = '| 1 | 走廊里正对门，略偏走廊左侧 | 朝门 | 门（中间偏左） | Theo 中间偏右 | 两人对着 | 能 | 一致 |\n'
        errors, warns = run(card(shots=(1,), rows=(), anchors=PRESENCE_ONLY).replace(HEADER, HEADER + row))
        self.assertEqual(errors, [])
        self.assertTrue(any(w.startswith('W-C3') for w in warns), warns)

    def test_wrong_case_d8_with_bearings_fails_c09(self):
        """The same wrong case with bearings (1.9.0, proposal S1): shifted west while facing north, the door straight
        ahead lands right of centre, so 门 in the 画左 column is a C09 error. Shifted east it is correct."""
        row = '| 1 | 走廊里，偏西 | 朝北 | 门（中间偏左） | 东窄墙 | 两人对着 | 能 | 一致 |\n'
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertTrue(any(e.startswith('C09') and '门' in e for e in errors), errors)
        fixed = row.replace('偏西', '偏东')
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + fixed))
        self.assertEqual(errors, [])

    def test_c09_reverse_along_the_end_wall(self):
        """dddc014 shot 8: camera by the west narrow wall facing east; the end wall and door are on the north side,
        which is frame left when facing east. The review wrote the door on frame right."""
        row = '| 1 | 西窄墙前，贴尽头墙 | 朝东 | 走廊另一头 | 门 | 中间，3/4 正脸 | 能 | 相反 |\n'
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertTrue(any('C09' in e and '「门」应在画左' in e for e in errors), errors)
        self.assertTrue(any('C09' in e and '「走廊另一头」应在画右' in e for e in errors), errors)

    def test_c09_back_to_the_door(self):
        """clip01 shot 1 with absolute names: facing south, the west wall is frame right."""
        row = '| 1 | 走廊里，随 Theo 后退 | 朝南，背对门 | 西长墙 | 东长墙 | 中间，正面 | 能 | 一致 |\n'
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertTrue(any('C09' in e and '西长墙' in e for e in errors), errors)
        swapped = row.replace('| 西长墙 | 东长墙 |', '| 东长墙 | 西长墙 |')
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + swapped))
        self.assertEqual(errors, [])

    def test_c09_object_behind_the_camera(self):
        row = '| 1 | 走廊中段 | 朝北 | 走廊另一头 | 东长墙 | 中间 | 能 | 一致 |\n'
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertTrue(any('C09' in e and '镜头身后' in e for e in errors), errors)

    def test_landmark_used_as_reference_point_is_skipped(self):
        row = '| 1 | 走廊里正对门 | 朝北 | 门右边那截窄墙的影子 | 东长墙 | 中间 | 能 | 一致 |\n'
        errors, _ = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertEqual(errors, [])

    def test_row_without_bearing_facing_warns(self):
        row = '| 1 | 走廊里正对门 | 朝门 | 门 | 墙纸 | 中间 | 能 | 一致 |\n'
        errors, warns = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertEqual(errors, [])
        self.assertTrue(any(w.startswith('W-C3 镜1') for w in warns), warns)

    def test_bare_yes_without_reach_line(self):
        anchors = ANCHORS.replace('可达：站在东窄墙前，画左那只手够得到门板铰链一侧，够不到门把手。\n', '')
        _, warns = run(card(anchors=anchors))
        self.assertTrue(any(w.startswith('W-C4') for w in warns), warns)
        _, warns = run(card())
        self.assertFalse(any(w.startswith('W-C4') for w in warns), warns)

    def test_corridor_relative_wall_name(self):
        row = '| 1 | 走廊里正对门 | 朝北 | 走廊左墙 | 东长墙 | 中间 | 能 | 一致 |\n'
        _, warns = run(card(shots=(1,), rows=()).replace(HEADER, HEADER + row))
        self.assertTrue(any(w.startswith('W-C5 镜1') and '走廊左墙' in w for w in warns), warns)

    def test_cli_stage_flag(self):
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(card(anchors=UPSTREAM))
        self.assertEqual(cpc.main(['x', f.name]), 1)
        self.assertEqual(cpc.main(['x', '--stage', 's5', f.name]), 0)
        self.assertEqual(cpc.main(['x', '--stage', 'bad', f.name]), 2)

    def test_cli_exit_codes(self):
        self.assertEqual(cpc.main(['x']), 2)
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(card(plan=False))
        self.assertEqual(cpc.main(['x', f.name]), 1)


def prompt_file(lines):
    with tempfile.NamedTemporaryFile('w', suffix='.prompt.md', delete=False, encoding='utf-8') as f:
        f.write('【分镜时间线】\n' + ''.join(lines))
    return f.name


class CrossCheckTests(unittest.TestCase):
    ROW = '| 1 | 走廊里，偏东 | 朝北 | 门（中间偏左） | 东窄墙 | Theo 中间偏右 | 能 | 一致 |\n'

    def card_path(self):
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(card(shots=(1,), rows=()).replace(HEADER, HEADER + self.ROW))
        return f.name

    def test_contradiction_is_c10(self):
        """offset EP06: the clip02 card was mirrored (door frame left) while an older prompt still said frame right."""
        prompt = prompt_file(['镜头1（0-3s）：【中景，正对门，焦点在 Theo】门在画面中间偏右；Theo 在画面中间偏左。\n'])
        errors, _ = cpc.check(self.card_path(), 's6', prompt)
        self.assertTrue(any(e.startswith('C10 镜1') and '「门」' in e for e in errors), errors)

    def test_agreement_passes(self):
        prompt = prompt_file(['镜头1（0-3s）：【中景，正对门，焦点在 Theo】门在画面中间偏左；Theo 在画面中间偏右。\n'])
        errors, _ = cpc.check(self.card_path(), 's6', prompt)
        self.assertEqual(errors, [])

    def test_clause_with_both_sides_or_reference_point_is_skipped(self):
        prompt = prompt_file(['镜头1（0-3s）：【中景，正对门，焦点在 Theo】门从画左看过去在画右的反光里，门右边那截窄墙在画右。\n'])
        errors, _ = cpc.check(self.card_path(), 's6', prompt)
        self.assertEqual(errors, [])

    def test_common_objects_without_bearings(self):
        row = '| 1 | 走廊里正对门 | 朝门 | 门框和铜名牌 | 墙纸 | Theo 中间 | 能 | 一致 |\n'
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(card(shots=(1,), rows=(), anchors=PRESENCE_ONLY).replace(HEADER, HEADER + row))
        prompt = prompt_file(['镜头1（0-2s）：【近景，正对门，焦点在 Theo】门框和铜名牌在他头部的画右一侧，画左是墙纸。\n'])
        errors, _ = cpc.check(f.name, 's6', prompt)
        self.assertTrue(any('C10' in e and '「门框」' in e for e in errors), errors)

    def test_cli_prompt_flag(self):
        prompt = prompt_file(['镜头1（0-3s）：【中景】门在画面中间偏右。\n'])
        self.assertEqual(cpc.main(['x', '--prompt', prompt, self.card_path()]), 1)
        self.assertEqual(cpc.main(['x', '--prompt']), 2)
        self.assertEqual(cpc.main(['x', '--prompt', prompt, self.card_path(), self.card_path()]), 2)


if __name__ == '__main__':
    unittest.main()
