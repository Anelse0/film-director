"""1.16.0 — references/shot-requirements.md: one table (R1–R5) used both to write and to check the shot deliverables.

R1 dialogue shape and off-screen sound · R2 the speaker is doing something, taken from the story · R3 what is deep in
each frame · R4 shot deliverables carry only what is in the shot · R5 no light in the eyes. This file pins the wiring:
the same row ids appear where the rules are written, where they are checked and in the dock echo; nothing that 1.15.1
had was dropped except what the user withdrew (evidence #10 and the ban built on it).
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
BASELINE = '3bf2e20'  # film-director 1.15.1
ROWS = ('R1', 'R2', 'R3', 'R4', 'R5')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def baseline(rel):
    out = git('show', f'{BASELINE}:{rel}')
    return out.stdout if out.returncode == 0 else None


HAS_BASELINE = git('cat-file', '-e', f'{BASELINE}^{{commit}}').returncode == 0


class OneTableTests(unittest.TestCase):
    def test_version_and_changelog(self):
        self.assertEqual(read('VERSION').strip(), '1.16.0')
        self.assertTrue(read('CHANGELOG.md').startswith('# Changelog\n\n## 1.16.0 — '))

    def test_every_row_is_named_where_it_is_written_and_where_it_is_checked(self):
        table = read('references/shot-requirements.md')
        writing = {'SKILL.md': read('SKILL.md'), 'stage-5': read('references/stage-5-directing-storyboard.md'),
                   'stage-6': read('references/stage-6-prompt-compiler.md')}
        checking = {'stage-7': read('references/stage-7-qa-continuity.md'), 'checks.md': read('references/checks.md')}
        scripts = ''.join(read(f'scripts/{n}') for n in ('speaker_checks.py', 'validate_prompt.py', 'viewpoint_checks.py',
                                                         'layer_checks.py', 'stage_check.py', 'camera_plan_check.py', 'check.py'))
        for row in ROWS:
            self.assertIn(f'| {row} |', table, row)
            for name, text in {**writing, **checking}.items():
                self.assertRegex(text, rf'(?<![A-Za-z0-9]){row}(?![0-9])', f'{row} missing in {name}')
            self.assertRegex(scripts, rf'(?<![A-Za-z0-9]){row}(?![0-9])', f'{row} missing in the scripts')

    def test_codes_named_in_the_table_exist_in_the_code_table(self):
        named = set(re.findall(r'(?<![A-Za-z0-9])(W-C\d+|[WCS]\d{2})(?![0-9])', read('references/shot-requirements.md')))
        codes = read('references/checks.md')
        self.assertTrue({'W-C8', 'W54', 'W55', 'S01', 'W-C6', 'W-C3', 'C11', 'W52', 'W13', 'W-C9', 'W57'} <= named, named)
        for code in named:
            self.assertIn(code, codes, code)

    def test_no_new_code_was_opened(self):
        if not HAS_BASELINE:
            self.skipTest('baseline commit not in this checkout')
        pat = r'(?<![A-Za-z0-9])(?:W-[CQ]\d+|[WECSQP]\d{2})(?![0-9])'
        old = set(re.findall(pat, baseline('references/checks.md')))
        new = set(re.findall(pat, read('references/checks.md')))
        self.assertEqual(new - old, set(), 'SKILL 规则维护：新 W 码冻结')
        self.assertEqual(old - new, set(), 'no code was removed')

    def test_templates_carry_the_slots(self):
        card = read('templates/shot-card.md')
        for needle in ('## 台词动作表', '| 可见画面 | 画面深处 | 人物动作 |', '| 画面深处有什么 |', '`手法分布`', 'film-director 1.16'):
            self.assertIn(needle, card, needle)
        self.assertNotIn('| 手法 |', card)
        prompt = read('templates/prompt-templates.md')
        self.assertIn('可见画面：', prompt)
        self.assertIn('画面深处是', prompt)
        self.assertNotIn('不发光', prompt)
        self.assertIn('镜头要求核对', read('templates/qa.md'))

    def test_dialogue_keeps_the_quote_format(self):
        """Checked against the guides 2026-11-21; the user kept quotes (the official tutorial's {} is recorded, not adopted)."""
        self.assertIn('台词（{角色}，{台词起}-{台词止}s，{语言}，', read('templates/prompt-templates.md'))
        self.assertIn('）："{逐字}"', read('templates/prompt-templates.md'))
        self.assertIn('保留引号写法', read('references/seedance-2.5-capabilities.md'))
        self.assertIn('台词（A，画外音，b-cs，和镜头 N 同一个声音）："后半句"', read('references/shot-requirements.md'))


class WithdrawnEvidenceTests(unittest.TestCase):
    def test_evidence_10_is_gone_and_nothing_points_to_it(self):
        log = read('references/validation-log.md')
        self.assertIsNone(re.search(r'^\| 10 \|', log, flags=re.M))
        self.assertIsNotNone(re.search(r'^\| 37 \|', log, flags=re.M), 'the clothing half of the old row lives on as #37')
        files = ['SKILL.md', 'README.md'] + [str(p.relative_to(ROOT)) for d in ('references', 'templates', 'scripts')
                                              for p in sorted((ROOT / d).glob('*')) if p.suffix in ('.md', '.py')]
        for rel in files:
            self.assertIsNone(re.search(r'(?:证据|evidence|validation-log) ?#10(?![0-9])', read(rel)), rel)

    def test_other_rows_survive(self):
        log = read('references/validation-log.md')
        for n in (1, 5, 6, 8, 9, 12, 25, 26, 30, 32, 33, 36):
            self.assertIsNotNone(re.search(rf'^\| {n} \|', log, flags=re.M), n)


class NothingElseDroppedTests(unittest.TestCase):
    """「不删规则，不删内容」: against the 1.15.1 commit, headings, hard rules and the §5.11 rows are all still there."""

    def setUp(self):
        if not HAS_BASELINE:
            self.skipTest('baseline commit not in this checkout')

    def test_headings_survive(self):
        stem = lambda line: re.split(r'[（(]', line.strip(), maxsplit=1)[0].strip()
        files = ['SKILL.md'] + [f'references/{p.name}' for p in sorted((ROOT / 'references').glob('*.md'))] \
            + [f'templates/{p.name}' for p in sorted((ROOT / 'templates').glob('*.md'))]
        for rel in files:
            old = baseline(rel)
            if old is None:
                continue  # new in 1.16.0
            now = {stem(l) for l in read(rel).splitlines() if re.match(r'#{1,4} ', l)}
            for line in old.splitlines():
                if re.match(r'#{1,4} ', line):
                    self.assertIn(stem(line), now, f'{rel}: {line}')

    def test_hard_rules_and_closing_table_rows_survive(self):
        skill = read('SKILL.md')
        for n in range(1, 22):
            self.assertRegex(skill, rf'(?m)^{n}\. \*\*', n)
        old = baseline('references/stage-5-directing-storyboard.md')
        now = read('references/stage-5-directing-storyboard.md')
        rows = re.findall(r'(?m)^\| (\d+) \| ([^|]+) \|', old)
        self.assertEqual(len([r for r in rows if int(r[0]) <= 25]), 25)
        for n, name in rows:
            self.assertIn(f'| {n} | {name.strip()} |', now, f'§5.11 第 {n} 行')

    def test_no_reference_file_was_removed(self):
        tracked = git('ls-tree', '-r', '--name-only', BASELINE).stdout.split()
        for rel in tracked:
            if rel.startswith(('references/', 'templates/', 'scripts/', 'examples/', 'assets/')):
                self.assertTrue((ROOT / rel).exists(), rel)


class EchoBlockTests(unittest.TestCase):
    CARD, PROMPT = 'examples/example-07-noodle-shop.md', 'examples/example-07-noodle-shop.prompt.md'

    def report(self, *args):
        out = subprocess.run([sys.executable, 'scripts/check.py', '--json', *args], cwd=ROOT, capture_output=True, text=True)
        return json.loads(out.stdout)

    def test_plan_echo_is_the_shot_table_plus_five_requirement_lines(self):
        echo = self.report('plan', self.CARD)['echo']
        header = echo[0]
        for col in ('镜', '时间', '景别', '运镜', '可见画面', '画面深处', '人物动作', '台词'):
            self.assertIn(col, header)
        for col in ('焦点与虚实', '无台词秒', '角度'):
            self.assertNotIn(col, header)  # they stay on the card
        self.assertEqual(len([l for l in echo if re.match(r'\| \d+ \|', l)]), 4)
        lines = [l for l in echo if re.match(r'R[1-5] ', l)]
        self.assertEqual([l[:2] for l in lines], list(ROWS))
        self.assertTrue(all('：过' in l for l in lines), lines)

    def test_s6_echo_reads_the_prompt_side_too(self):
        data = self.report('s6', self.CARD, self.PROMPT)
        self.assertEqual(data['exit'], 0)
        self.assertEqual(data['errors'] + data['warnings'] + data['render_lessons'], [])
        self.assertTrue(any(l.startswith('R5 不写眼睛的光线：过') for l in data['echo']))
        self.assertTrue(any('画外段 镜头3→镜头4' in i['message'] and '句中切听者' in i['message'] for i in data['info']))

    def test_echo_reports_what_is_missing(self):
        import check
        card = read(self.CARD).replace('| 玻璃门，门外路灯下的电动车 |', '| __ |').replace('小北（画外音）："回老家。"', '画外音："回老家。"')
        echo = '\n'.join(check.echo_block(card))
        self.assertIn('R3 可见画面与画面深处：没过', echo)
        self.assertIn('镜 3', echo)
        self.assertIn('R1 对白形状与画外：没过', echo)


if __name__ == '__main__':
    unittest.main()
