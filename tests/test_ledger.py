"""ledger_check: timing/pacing checks on a shared storyboard spreadsheet (stdlib xlsx)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from xlsx_lite import read_workbook, write_workbook  # noqa: E402
from ledger_check import check, parse_time  # noqa: E402

HEADER = ['镜号', '故事段', '入点', '出点', '时长/秒', '场景／角色', '景别与运镜', '画面与有序表演', '英语台词／全片时间窗', '光源与声音', '连续性', '情绪']
LHEADER = ['台词号', '镜号', '角色／类型', '入点', '出点', '英语原句', '中文对照', '说法与重音', '词数', '窗口/秒', '词/秒']


def shot(no, start, end, camera='中景，固定', lines='A 00:00–00:03\n“Fine.”', scene='厨房 A/B'):
    return [no, '01', start, end, '=ROUND((D9-C9)*86400,0)', scene, camera, '动作。', lines, '声音', '', '']


def book(shots, lines=None):
    sheets = {'分镜总表': [['标题'], [], [], [], HEADER] + shots}
    if lines is not None:
        sheets['台词与表演'] = [['标题'], [], [], [], LHEADER] + lines
    return sheets


class LedgerTests(unittest.TestCase):
    def run_check(self, sheets, **kw):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'ledger.xlsx'
            write_workbook(path, sheets)
            self.assertEqual(list(read_workbook(path)), list(sheets))
            return check(path, **kw)

    def test_time_formats(self):
        self.assertEqual(parse_time('00:02:40'), 160)
        self.assertEqual(parse_time('2:40'), 160)
        self.assertAlmostEqual(parse_time(8 / 86400), 8)
        self.assertEqual(parse_time(12), 12)
        self.assertIsNone(parse_time('=ROUND(1)'))

    def test_clean_ledger_has_no_errors(self):
        r = self.run_check(book([shot('01', '00:00:00', '00:00:03'), shot('02', '00:00:03', '00:00:06', '近景，微推')]))
        self.assertEqual(r['errors'], [])
        self.assertEqual(r['warnings'], [])
        self.assertEqual(len(r['shots']), 2)

    def test_gap_overlap_and_inverted(self):
        r = self.run_check(book([shot('01', '00:00:00', '00:00:03'), shot('02', '00:00:04', '00:00:06'),
                                 shot('03', '00:00:05', '00:00:08'), shot('04', '00:00:09', '00:00:08')]))
        codes = [e[:3] for e in r['errors']]
        self.assertIn('L02', codes)
        self.assertIn('L01', codes)
        self.assertTrue(any('缝隙' in e for e in r['errors']))
        self.assertTrue(any('重叠' in e for e in r['errors']))

    def test_long_dialogue_shot_flags_but_voiceover_and_placeholder_do_not(self):
        r = self.run_check(book([
            shot('01', '00:00:00', '00:00:08', lines='A（旁白） 00:02–00:08\n“This is…”'),
            shot('02', '00:00:08', '00:00:16', '中景，固定', lines='B 00:08–00:15\n“Welcome.”'),
            shot('03', '00:00:16', '00:00:40', '〔待定〕', lines='〔待定〕', scene='【待重写·留空】'),
            shot('04', '00:00:40', '00:00:51', '全景，固定', lines='无台词'),
        ]))
        self.assertEqual(r['errors'], [])
        self.assertTrue(any(w.startswith('L03 镜02') for w in r['warnings']))
        self.assertFalse(any('镜01' in w for w in r['warnings']))
        self.assertFalse(any('镜03' in w for w in r['warnings']))
        self.assertTrue(any(w.startswith('L04 镜04') for w in r['warnings']))
        self.assertEqual(r['placeholders'], ['03'])
        self.assertTrue(any(i.startswith('L07') for i in r['info']))

    def test_camera_monotony(self):
        r = self.run_check(book([shot('01', '00:00:00', '00:00:02'), shot('02', '00:00:02', '00:00:04'),
                                 shot('03', '00:00:04', '00:00:06'), shot('04', '00:00:06', '00:00:08', '特写，固定')]))
        self.assertTrue(any(w.startswith('L05 镜03') for w in r['warnings']))
        self.assertEqual(sum(w.startswith('L05') for w in r['warnings']), 1)

    def test_lines_sheet_windows_and_rate(self):
        shots = [shot('01', '00:00:00', '00:00:04'), shot('02', '00:00:04', '00:00:08')]
        lines = [
            ['D01', '01', 'A／对白', '00:00:00', '00:00:03', 'One two three four five six.', '', '', 6, '', ''],
            ['D02', '02', 'B／对白', '00:00:03', '00:00:07', 'Late start.', '', '', 2, '', ''],
            ['D03', '02', 'B／对白', '00:00:05', '00:00:06', 'Seven eight nine ten.', '', '', None, '', ''],
            ['D04', '09', 'B／对白', '00:00:05', '00:00:06', 'x', '', '', 1, '', ''],
        ]
        r = self.run_check(book(shots, lines))
        self.assertTrue(any(e.startswith('L06 台词D02') and '越出' in e for e in r['errors']))
        self.assertTrue(any(e.startswith('L06 台词D04') and '不存在' in e for e in r['errors']))
        self.assertTrue(any(w.startswith('L08 台词D03') for w in r['warnings']))
        self.assertFalse(any('D01' in w for w in r['warnings']))
        self.assertEqual(len(r['lines']), 4)

    def test_missing_header_is_reported(self):
        r = self.run_check({'Sheet1': [['a', 'b'], [1, 2]]})
        self.assertTrue(r['errors'][0].startswith('L00'))


if __name__ == '__main__':
    unittest.main()
