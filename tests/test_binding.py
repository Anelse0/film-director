"""W24: no E-layer planning/provenance/draft notes in the 素材绑定 section (1.4.0)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_prompt import validate  # noqa: E402

BIND_CLEAN = ('图1 = A 人物形象，只参考面部、发型、体型，不参考服装、背景与姿势；'
              '图2 = A 本场服装造型（礼服），只参考服装与配饰，不参考面部、背景与姿势；'
              '图3 = 大厅 布局与光，不参考人物。')
BODY = ('\n【总述】10秒 9:16，室内。\n【起始状态】图1 的 A 在画左，机位中景。\n'
        '【整体情绪弧线】平静。\n- A：平静（镜1，抬眼）\n【分镜时间线】\n'
        '镜头1（0-10s）：【中景，正面，固定】〔A：平静〕A 抬眼看向画右。\n'
        '【贯穿要求】A 外观锁；无 bgm，只有环境音；不要字幕。\n')

def run(binding):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'p.md'
        p.write_text('【素材绑定】' + binding + BODY, encoding='utf-8')
        return validate(p)

def w24(r):
    return [w for w in r['warnings'] if w.startswith('W24')]


class BindingNoteTests(unittest.TestCase):
    def test_clean_binding_has_no_w24(self):
        r = run(BIND_CLEAN)
        self.assertEqual(r['errors'], [])
        self.assertEqual(w24(r), [])

    def test_convention_note_leaks_w24(self):
        r = run(BIND_CLEAN + '（约定：每人两图，共 3 张 ≤6。本条为草稿 Prompt。）')
        self.assertEqual(len(w24(r)), 1)
        self.assertIn('约定', w24(r)[0])

    def test_provenance_note_leaks_w24(self):
        r = run('图1 = A 人物形象（用户提供·含面部与身形），不参考背景。')
        self.assertEqual(len(w24(r)), 1)
        self.assertIn('用户提供', w24(r)[0])

    def test_s5b_backfill_note_leaks_w24(self):
        r = run(BIND_CLEAN + '（说明：参考图尚未上传，需 S5b 回填。）')
        self.assertTrue(w24(r))

    def test_w24_is_production_only_and_warn_not_error(self):
        # A note-like word in a performance fragment must not raise W24 (no refs section).
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'f.md'
            p.write_text('【表演条件】10秒。\n【表演时间线】\n节拍 1（0-10s）：她说明来意后闭嘴。', encoding='utf-8')
            r = validate(p, artifact='performance')
        self.assertEqual(w24(r), [])


if __name__ == '__main__':
    unittest.main()
