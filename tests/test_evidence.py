"""1.13.0 evidence.py: a rule text's 「证据 #n」 resolves to one row of references/validation-log.md without reading
the whole table (review proposal 2026-10-20 M4)."""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import evidence  # noqa: E402

LOG = ('# 验证账本\n\n## 表\n\n'
       '| # | 日期 | 项目/clip/节拍 | 平台/模型/参考条件 | 测试写法与版本/变量 | 对应规则（文件 §） | 执行状态 | 观察证据 | 下一步 |\n'
       '|---|---|---|---|---|---|---|---|---|\n'
       '| | | | | | 可见 / 部分 / 未执行 / 不可观察 | | |\n'
       '| 1 | 2026-09-19 | EP01 D05 | 方舟 | v1 | duration §二 | 可见 | 切点对上 | 无 |\n'
       '| 8 | 2026-10-19 | EP06 s01 clip02 v1 | 方舟 | 右肩旁边 | S5 §5.1g | 未执行 | 人物右肩被放到画右 | 写画左 / 画右 |\n'
       '\n## 待验证\n\n| # | 项 | 状态 |\n|---|---|---|\n| 1 | 画外整句镜 | 待 |\n| 8 | 另一项 | 待 |\n')


def run(*args):
    out = io.StringIO()
    with redirect_stdout(out):
        code = evidence.main(['evidence.py', *args])
    return code, out.getvalue()


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8')
        self.temp.write(LOG)
        self.temp.close()

    def test_row_by_number_reads_the_render_table_not_the_pending_table(self):
        code, out = run('8', '--log', self.temp.name)
        self.assertEqual(code, 0)
        self.assertIn('#8 · 2026-10-19 · EP06 s01 clip02 v1', out)
        self.assertIn('观察证据：人物右肩被放到画右', out)
        self.assertNotIn('另一项', out)

    def test_hash_prefix_and_separators(self):
        code, out = run('#1，8', '--log', self.temp.name)
        self.assertEqual(code, 0)
        self.assertIn('#1 ·', out)
        self.assertIn('#8 ·', out)

    def test_missing_number_exits_1(self):
        code, out = run('3', '--log', self.temp.name)
        self.assertEqual(code, 1)
        self.assertIn('#3', out)

    def test_grep_and_all(self):
        code, out = run('--grep', '画右', '--log', self.temp.name)
        self.assertEqual(code, 0)
        self.assertIn('#8', out)
        code, out = run('--all', '--log', self.temp.name)
        self.assertEqual(code, 0)
        self.assertEqual(out.count('\n'), 2)

    def test_real_log_resolves_cited_evidence(self):
        """Every 「证据 #n」 cited by SKILL.md and the stage rule files is a row of the real table."""
        import re
        header, rows = evidence.load()
        cited = set()
        for f in ['SKILL.md', 'references/stage-5-directing-storyboard.md', 'references/stage-6-prompt-compiler.md',
                  'references/stage-7-qa-continuity.md', 'references/stage-4-performance.md', 'references/duration-rhythm.md']:
            text = (ROOT / f).read_text(encoding='utf-8')
            for m in re.finditer(r'证据 #(\d+)((?:、#\d+)*)', text):
                cited.add(int(m.group(1)))
                cited.update(int(x) for x in re.findall(r'#(\d+)', m.group(2)))
        self.assertTrue(cited)
        self.assertEqual(sorted(cited - set(rows)), [], f'rule files cite evidence rows the table lacks: {sorted(cited - set(rows))}')


if __name__ == '__main__':
    unittest.main()
