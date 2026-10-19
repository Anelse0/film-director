"""1.10.0 qa_check.py (S7 §7.4): the QA file opens with 现行状态 and it matches the prompt — version (Q02) and a fresh
validate_prompt run (Q03). Trigger: offset EP06 QA files that only ever grew (proposal G3)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import qa_check  # noqa: E402
from test_render_lessons import build, E, SHOT1, SHOT2, SHOT3  # noqa: E402
from validate_prompt import validate  # noqa: E402

E_VERSION = E + '| 版本 | v1.2（2026-10-19：示例） |\n'


def current(version='v1.2', codes=None, errors=0, first=True, drop=None):
    lines = [f'- Prompt：`06_prompts/clip.prompt.md` {version}', '- 分镜卡：`04_shots/clip.md` v1', '- 成片：未生成',
             '- 上游末帧：无', f'- 校验：validate_prompt 2026-10-19 {errors} ERROR；WARN {codes}；成片教训类 无', '- 未决：无']
    if drop:
        lines = [l for l in lines if not l.startswith(f'- {drop}')]
    block = '## 现行状态\n\n' + '\n'.join(lines) + '\n\n'
    history = '## 历史\n\n旧的审阅。\n\n'
    return '# QA clip\n\n' + (block + history if first else history + block)


class QaCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / '06_prompts').mkdir()
        (root / '07_qa').mkdir()
        self.prompt = root / '06_prompts' / 'clip.prompt.md'
        self.prompt.write_text(build(e=E_VERSION), encoding='utf-8')
        self.qa = root / '07_qa' / 'clip.qa.md'
        fresh = sorted({w.split()[0] for w in validate(self.prompt)['warnings']})
        self.codes = '、'.join(fresh) if fresh else '无'

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self, text, prompt=None):
        self.qa.write_text(text, encoding='utf-8')
        return qa_check.check(self.qa, prompt)

    def test_current_state_matches(self):
        errors, warns = self.run_check(current(codes=self.codes))
        self.assertEqual(errors, [])
        self.assertEqual(warns, [])

    def test_missing_section(self):
        errors, _ = self.run_check('# QA clip\n\n## 脚本校验\n\nW17。\n')
        self.assertTrue(errors and errors[0].startswith('Q01'), errors)

    def test_section_not_first(self):
        errors, _ = self.run_check(current(codes=self.codes, first=False))
        self.assertTrue(any('不是第一个' in e for e in errors), errors)

    def test_missing_line(self):
        errors, _ = self.run_check(current(codes=self.codes, drop='成片'))
        self.assertTrue(any('Q01' in e and '成片' in e for e in errors), errors)

    def test_version_drift(self):
        """clip02 stayed v1 through six changes: the QA said one version, the prompt another."""
        errors, _ = self.run_check(current(version='v1.1', codes=self.codes))
        self.assertTrue(any(e.startswith('Q02') and 'v1.1' in e and 'v1.2' in e for e in errors), errors)

    def test_stale_validator_codes(self):
        """clip01 QA listed W27 (no longer fired) and missed W33 (fired)."""
        stale = 'W27' if self.codes == '无' else self.codes + '、W27'
        errors, _ = self.run_check(current(codes=stale))
        self.assertTrue(any(e.startswith('Q03') and 'W27' in e for e in errors), errors)
        shot = SHOT2.replace('英语，随口）', '英语，随口，语速快）')
        self.prompt.write_text(build(shots=(SHOT1, shot, SHOT3), e=E_VERSION), encoding='utf-8')
        errors, _ = self.run_check(current(codes=self.codes))
        self.assertTrue(any(e.startswith('Q03') and 'W47' in e for e in errors), errors)

    def test_error_count_drift(self):
        errors, _ = self.run_check(current(codes=self.codes, errors=2))
        self.assertTrue(any('2 个 ERROR' in e for e in errors), errors)

    def test_unresolvable_path_warns(self):
        text = current(codes=self.codes).replace('06_prompts/clip.prompt.md', '06_prompts/missing.prompt.md')
        errors, warns = self.run_check(text)
        self.assertEqual(errors, [])
        self.assertTrue(any(w.startswith('W-Q1') for w in warns), warns)
        errors, warns = self.run_check(text, prompt=str(self.prompt))
        self.assertEqual(warns, [])

    def test_cli(self):
        self.qa.write_text(current(version='v9', codes=self.codes), encoding='utf-8')
        self.assertEqual(qa_check.main(['x', str(self.qa)]), 1)
        self.assertEqual(qa_check.main(['x']), 2)
        self.assertEqual(qa_check.main(['x', '--prompt']), 2)

    def test_template_has_the_section(self):
        template = (ROOT / 'templates' / 'qa.md').read_text(encoding='utf-8')
        block, first = qa_check.current_section(template)
        self.assertTrue(first)
        for label in ('Prompt', '成片', '校验'):
            self.assertIsNotNone(qa_check.line(block, label), label)


if __name__ == '__main__':
    unittest.main()
