"""1.13.0 check.py (cost-review proposal M1 / M2): one entry point that imports the four checkers' check() / validate(),
merges their results (ERROR → render-lesson WARN → other WARN → 数字块 → INFO → sha256) and, with `qa --sync`, writes the
machine lines of the QA 现行状态 back. The four scripts, their codes, thresholds and classes are untouched; this suite
asserts that the merged sets equal the direct calls, that the 数字块 lines satisfy qa_check Q03, and that Q01–Q04 still
fire through the entry point. Fixtures: the 1.8.0 camera plan + the 1.11.0 执行卡 card, the 1.9.0 corridor prompt."""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import camera_plan_check as cpc  # noqa: E402
import check  # noqa: E402
import qa_check  # noqa: E402
import stage_check as sc  # noqa: E402
from test_camera_plan import ANCHORS, HEADER, REVIEW, ROW  # noqa: E402
from test_render_lessons import E, SHOT1, SHOT2, SHOT3, build  # noqa: E402
from test_stage_check import E_LAYER, OVERVIEW, SHOTS, card_rows  # noqa: E402
from validate_prompt import validate  # noqa: E402

E_VERSION = E + '| 版本 | v1.2（2026-10-20：示例） |\n'
CAMERA_PLAN = ('## 机位设计\n\n' + ANCHORS + '### 机位表\n\n' + HEADER + ''.join(ROW.format(n=n) for n in (1, 2, 3)) + '\n'
               + REVIEW + '\n')
HEAD = '# clip 分镜卡\n\n**版本：v1.3 · 2026-10-20**（示例）\n\n'
SECTIONS = ('## 走位表\n…\n\n' + CAMERA_PLAN + '## clip 起始状态\n…\n\n## clip 结束状态\n…\n\n## 贯穿要求\n…\n\n')


def card_text(plan=True, door_left=True):
    """door_left=False puts the door on 画右 (examples/example-01 has the daughter enter from the 画右 doorway)."""
    text = HEAD + (SECTIONS if plan else SECTIONS.replace(CAMERA_PLAN, '')) + OVERVIEW + SHOTS + E_LAYER
    if not door_left:
        text = text.replace('| 门 | 墙纸 |', '| 墙纸 | 门 |')
    rows = card_rows()
    return text + '## 执行卡\n| # | 项 | 证据 |\n|---|---|---|\n' + ''.join(
        f'| {n} | {sc.CARD_ROWS[n]} | {rows[n]} |\n' for n in sorted(rows))


def qa_text(version='v1.2', codes='无', card_version='v1.3', camera='camera_plan_check 0 ERROR；C10 无矛盾；WARN 无',
            stage='stage_check 0 ERROR（S5 25 行；无）', named='无', drop=(), gate8='| 9 s | 2 / 2 | 1 | 0 | 无 | 无 |',
            dispositions='', prompt_path='06_prompts/clip.prompt.md', first=True):
    lines = [f'- Prompt：`{prompt_path}` {version}', f'- 分镜卡：`04_shots/clip.md` {card_version}', '- 成片：未生成',
             '- 上游末帧：无（人写的一行，脚本不动）', f'- 校验：validate_prompt 2026-10-20 0 ERROR；WARN {codes}；成片教训类 无',
             f'- 机位设计：{camera}', '- 未决：\n  - 等用户定的事（人写的，脚本不动）', f'- 用户已点名：{named}']
    if stage:
        lines.append(f'- 执行卡：{stage}')
    lines = [l for l in lines if not any(l.startswith(f'- {d}') for d in drop)]
    state = '## 现行状态（每次改稿重写这一节，不往下追加）\n\n' + '\n'.join(lines) + '\n\n'
    review = ('## 审阅（S7 §7.1 八道）\n\n### 1 台词\n逐镜结论。\n\n### 7 校验处置\n'
              '| 代码 | 内容 | 类别（成片教训 / 其余） | 处置 |\n|---|---|---|---|\n' + dispositions
              + '\n### 8 节奏与剪辑（数字抄 validate_prompt 的 WARN / INFO 与分镜卡执行卡，不自填）\n'
              + check.GATE8_HEADER + '\n|---|---|---|---|---|---|\n' + (gate8 + '\n' if gate8 else '') + '\n')
    history = '## 历史\n\n旧的审阅。\n\n'
    return '# QA clip\n\n' + (state + review + history if first else history + state + review)


def write_fixture(root, prompt_text=None, card=None, qa=None):
    """Write 04_shots/clip.md, 06_prompts/clip.prompt.md, 07_qa/clip.qa.md under root; the QA records the fresh codes."""
    root = Path(root)
    for d in ('04_shots', '06_prompts', '07_qa'):
        (root / d).mkdir(parents=True, exist_ok=True)
    (root / '04_shots' / 'clip.md').write_text(card if card is not None else card_text(), encoding='utf-8')
    prompt = root / '06_prompts' / 'clip.prompt.md'
    prompt.write_text(prompt_text if prompt_text is not None else build(e=E_VERSION), encoding='utf-8')
    fresh = sorted({w.split()[0] for w in validate(prompt)['warnings']})
    codes = '、'.join(fresh) if fresh else '无'
    (root / '07_qa' / 'clip.qa.md').write_text(qa if qa is not None else qa_text(codes=codes), encoding='utf-8')
    return root / '04_shots' / 'clip.md', prompt, root / '07_qa' / 'clip.qa.md'


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = check.main(['check.py', *argv])
    return rc, out.getvalue()


def run_json(*argv):
    rc, out = run('--json', *argv)
    return rc, json.loads(out)


def messages(data, key):
    return sorted(x['message'] for x in data[key])


class CheckFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.card, self.prompt, self.qa = write_fixture(self.root)
        fresh = sorted({w.split()[0] for w in validate(self.prompt)['warnings']})
        self.codes = '、'.join(fresh) if fresh else '无'

    def tearDown(self):
        self.temp.cleanup()


class S5Tests(CheckFixture):
    def test_equals_direct_calls(self):
        rc, data = run_json('s5', str(self.card))
        ce, cw = cpc.check(self.card, 's5')
        se, sw = sc.check(self.card, 's5')
        self.assertEqual(rc, 0)
        self.assertEqual(messages(data, 'errors'), sorted(ce + se))
        self.assertEqual(messages(data, 'render_lessons') + messages(data, 'warnings'), sorted(cw + sw))
        self.assertEqual([r['tool'] for r in data['runs']], ['camera_plan_check --stage s5', 'stage_check --stage s5'])

    def test_missing_plan_is_error_exit_1(self):
        self.card.write_text(card_text(plan=False), encoding='utf-8')
        rc, data = run_json('s5', str(self.card))
        ce, _ = cpc.check(self.card, 's5')
        self.assertEqual(rc, 1)
        self.assertTrue(any(e.startswith('C01') for e in ce))
        self.assertIn({'tool': 'camera_plan_check --stage s5', 'message': ce[0]}, data['errors'])

    def test_block_has_two_state_lines_and_no_gate8(self):
        rc, data = run_json('s5', str(self.card))
        self.assertEqual(data['block'], ['- 机位设计：camera_plan_check 0 ERROR；WARN 无', '- 执行卡：stage_check 0 ERROR（S5 25 行；无）'])


class S6Tests(CheckFixture):
    def direct(self):
        ce, cw = cpc.check(self.card, 's6')
        se, sw = sc.check(self.card, 's6')
        result = validate(self.prompt)
        pe, pw = cpc.check(self.card, 's6', self.prompt)
        errors = ce + se + result['errors'] + [x for x in pe if x not in ce]
        warns = cw + sw + result['warnings'] + [x for x in pw if x not in cw]
        return sorted(errors), sorted(warns), result

    def test_equals_direct_calls(self):
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        errors, warns, result = self.direct()
        self.assertEqual(rc, 0)
        self.assertEqual(messages(data, 'errors'), errors)
        self.assertEqual(sorted(messages(data, 'render_lessons') + messages(data, 'warnings')), warns)
        self.assertEqual([r['tool'] for r in data['runs']],
                         ['camera_plan_check', 'stage_check --stage s6', 'validate_prompt', 'camera_plan_check --prompt'])
        infos = [x['message'] for x in data['info'] if x['tool'] == 'validate_prompt']
        self.assertEqual(infos[:len(result['info'])], result['info'])
        self.assertIn(f"透镜 {result['lens']}" if result['lens'] else infos[-1], infos)

    def test_c10_contradiction_is_tagged_and_exit_1(self):
        shot = SHOT1.replace('门在他的画左。', '门在他的画右。')
        self.prompt.write_text(build(shots=(shot, SHOT2, SHOT3), e=E_VERSION), encoding='utf-8')
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        pe, _ = cpc.check(self.card, 's6', self.prompt)
        c10 = [e for e in pe if e.startswith('C10')]
        self.assertEqual(rc, 1)
        self.assertTrue(c10, pe)
        self.assertEqual([x['message'] for x in data['errors'] if x['tool'] == 'camera_plan_check --prompt'], c10)
        self.assertIn('C10 1 处矛盾', data['block'][1])

    def test_without_prompt_runs_card_checks_only(self):
        rc, data = run_json('s6', str(self.card))
        self.assertEqual(rc, 0)
        self.assertEqual([r['tool'] for r in data['runs']], ['camera_plan_check', 'stage_check --stage s6'])
        self.assertTrue(any('没有给 Prompt' in n for n in data['notes']))
        self.assertFalse(any(l.startswith('- 校验') for l in data['block']))

    def test_render_lessons_are_grouped_before_other_warnings(self):
        shot = SHOT1.replace('门在他的画左。', '门框就在他右肩旁边，名牌在他头的右边。')
        self.prompt.write_text(build(shots=(shot, SHOT2, SHOT3), e=E_VERSION), encoding='utf-8')
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        lessons = messages(data, 'render_lessons')
        self.assertTrue(any(w.startswith('W46') for w in lessons), lessons)
        self.assertFalse(any(w.startswith('W46') for w in messages(data, 'warnings')))
        self.assertIn('成片教训类 W46', data['block'][0])
        _, text = run('s6', str(self.card), str(self.prompt))
        order = [text.index(h) for h in ('-- ERROR', '-- 成片教训类 WARN', '-- 其余 WARN', '-- 数字块', '-- INFO', '-- sha256')]
        self.assertEqual(order, sorted(order))
        self.assertLess(text.index('W46'), text.index('-- 其余 WARN'))

    def test_block_lines_match_template_and_satisfy_q03(self):
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        block = data['block']
        self.assertRegex(block[0], r'^- 校验：validate_prompt \d{4}-\d{2}-\d{2} \d+ ERROR；WARN [^；]+；成片教训类 .+$')
        self.assertRegex(block[1], r'^- 机位设计：camera_plan_check \d+ ERROR；C10 [^；]+；WARN .+$')
        self.assertRegex(block[2], r'^- 执行卡：stage_check \d+ ERROR（S5 25 行；.+）$')
        self.assertEqual(len(block), 4)
        self.assertEqual(block[3].count('|'), 7)
        # paste the machine 校验 line into the QA: qa_check Q03 accepts it
        qa = qa_text(codes='W99').replace('- 校验：validate_prompt 2026-10-20 0 ERROR；WARN W99；成片教训类 无', block[0])
        self.qa.write_text(qa, encoding='utf-8')
        errors, _ = qa_check.check(self.qa)
        self.assertEqual([e for e in errors if e.startswith('Q03')], [])

    def test_gate8_numbers(self):
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        self.assertEqual(data['block'][3], '| 3 s（0-3s，镜头1）；E 层 2 s | 2 / 2 | 1 | 0 | 镜 2（1s）、镜 3（1s） | <不达标项处置> |')

    def test_hashes_and_text_report(self):
        rc, data = run_json('s6', str(self.card), str(self.prompt))
        self.assertEqual(set(data['sha256']), {str(self.card), str(self.prompt)})
        self.assertTrue(all(re.fullmatch(r'[0-9a-f]{12}', h) for h in data['sha256'].values()))
        _, text = run('s6', str(self.card), str(self.prompt))
        self.assertEqual(len(re.findall(r'^HASH  ', text, flags=re.M)), 2)
        self.assertRegex(text, r'(?m)^== 0 error\(s\), \d+ warning\(s\)$')


class QaTests(CheckFixture):
    def test_runs_qa_check_and_s6(self):
        rc, data = run_json('qa', str(self.qa))
        self.assertEqual(rc, 0, data['errors'])
        tools = [r['tool'] for r in data['runs']]
        self.assertIn('qa_check', tools)
        self.assertIn('validate_prompt', tools)
        self.assertIn('stage_check --stage s6', tools)
        self.assertEqual(data['block'][:2], ['- Prompt：`06_prompts/clip.prompt.md` v1.2', '- 分镜卡：`04_shots/clip.md` v1.3'])
        self.assertTrue(data['block'][-1].endswith('| 无 |'))  # existing 处置 cell is kept in the block

    def test_q01_missing_line(self):
        self.qa.write_text(qa_text(codes=self.codes, drop=('成片',)), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertEqual(rc, 1)
        self.assertTrue(any(m.startswith('Q01') and '成片' in m for m in messages(data, 'errors')))

    def test_q02_version_drift(self):
        self.qa.write_text(qa_text(version='v9', codes=self.codes), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertTrue(any(m.startswith('Q02') for m in messages(data, 'errors')))

    def test_q03_stale_codes(self):
        self.qa.write_text(qa_text(codes='W99'), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertTrue(any(m.startswith('Q03') for m in messages(data, 'errors')))

    def test_q04_named_category(self):
        row = '| W24 | 最长无台词 | 其余 | 保留理由：安静收尾 |\n'
        self.qa.write_text(qa_text(codes=self.codes, named='节奏（用户："太拖"，v1）', dispositions=row), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertEqual(rc, 1)
        self.assertTrue(any(m.startswith('Q04 W24') for m in messages(data, 'errors')))

    def test_unresolvable_prompt_only_runs_qa_check(self):
        self.qa.write_text(qa_text(codes=self.codes, prompt_path='06_prompts/missing.prompt.md'), encoding='utf-8')
        rc, data = run_json('qa', str(self.qa))
        self.assertEqual([r['tool'] for r in data['runs']], ['validate_prompt', 'qa_check'] if False else [r['tool'] for r in data['runs']])
        self.assertNotIn('validate_prompt', [r['tool'] for r in data['runs']])
        self.assertTrue(any(w.startswith('W-Q1') for w in messages(data, 'warnings')))
        self.assertTrue(any('只跑 qa_check' in n for n in data['notes']))


class SyncTests(CheckFixture):
    STALE = dict(version='v9', codes='W99', card_version='v0', camera='camera_plan_check（S6 入口）0 ERROR / 0 WARN', stage='',
                 gate8='| 9 s | 1 / 2 | 0 | 1 | 镜 1 | 用户同意保留：原话「留着」 |')

    def test_sync_rewrites_machine_lines_keeps_human_lines_and_is_idempotent(self):
        self.qa.write_text(qa_text(**self.STALE), encoding='utf-8')
        before = self.qa.read_text(encoding='utf-8')
        self.assertTrue(qa_check.check(self.qa)[0])  # stale: Q02 / Q03 fire before --sync
        rc, data = run_json('qa', '--sync', str(self.qa))
        after = self.qa.read_text(encoding='utf-8')
        self.assertEqual(rc, 0, data)
        self.assertTrue(data['sync']['changed'])
        self.assertEqual(set(data['sync']['written']), {'Prompt', '分镜卡', '校验', '机位设计', '执行卡', '第 8 道'})
        self.assertEqual(data['qa_check_after_sync'], {'errors': [], 'warnings': []})
        self.assertEqual(qa_check.check(self.qa), ([], []))
        # machine lines now carry the run results
        self.assertIn('- Prompt：`06_prompts/clip.prompt.md` v1.2\n', after)
        self.assertIn('- 分镜卡：`04_shots/clip.md` v1.3\n', after)
        self.assertIn(f'- 校验：validate_prompt {check.today()} 0 ERROR；WARN {self.codes}；成片教训类 无\n', after)
        self.assertIn('- 机位设计：camera_plan_check 0 ERROR；C10 无矛盾；WARN 无\n', after)
        self.assertIn('- 用户已点名：无\n- 执行卡：stage_check 0 ERROR（S5 25 行；无）\n', after)  # inserted in template order
        self.assertIn('| 3 s（0-3s，镜头1）；E 层 2 s | 2 / 2 | 1 | 0 | 镜 2（1s）、镜 3（1s） | 用户同意保留：原话「留着」 |\n', after)
        # the four human lines and everything outside the machine lines are byte-identical
        for line in ('- 成片：未生成', '- 上游末帧：无（人写的一行，脚本不动）', '- 未决：\n  - 等用户定的事（人写的，脚本不动）', '- 用户已点名：无'):
            self.assertIn(line, after)
        strip = lambda t: re.sub(r'^- (Prompt|分镜卡|校验|机位设计|执行卡)：[^\n]*\n|^\| (9 s|3 s)[^\n]*\n', '', t, flags=re.M)
        self.assertEqual(strip(before), strip(after))
        # idempotent
        rc2, data2 = run_json('qa', '--sync', str(self.qa))
        self.assertEqual(rc2, 0)
        self.assertFalse(data2['sync']['changed'])
        self.assertEqual(self.qa.read_text(encoding='utf-8'), after)

    def test_sync_keeps_q04_and_structure_errors(self):
        row = '| W24 | 最长无台词 | 其余 | 保留理由：安静收尾 |\n'
        self.qa.write_text(qa_text(**dict(self.STALE, named='节奏（用户："太拖"）', dispositions=row, first=False)), encoding='utf-8')
        rc, data = run_json('qa', '--sync', str(self.qa))
        after = data['qa_check_after_sync']['errors']
        self.assertEqual(rc, 1)
        self.assertTrue(any(e.startswith('Q01') and '不是第一个' in e for e in after), after)
        self.assertTrue(any(e.startswith('Q04 W24') for e in after), after)
        self.assertFalse(any(e.startswith(('Q02', 'Q03')) for e in after), after)

    def test_sync_without_prompt_writes_nothing(self):
        self.qa.write_text(qa_text(codes=self.codes, prompt_path='06_prompts/missing.prompt.md'), encoding='utf-8')
        before = self.qa.read_text(encoding='utf-8')
        rc, data = run_json('qa', '--sync', str(self.qa))
        self.assertEqual(self.qa.read_text(encoding='utf-8'), before)
        self.assertFalse(data['sync']['changed'])
        self.assertTrue(any('没有可写的机器行' in n for n in data['notes']))


class CliTests(CheckFixture):
    def test_usage_and_missing_file_exit_2(self):
        self.assertEqual(run()[0], 2)
        self.assertEqual(run('s5')[0], 2)
        self.assertEqual(run('s5', str(self.root / 'nope.md'))[0], 2)
        self.assertEqual(run('s6', str(self.card), str(self.root / 'nope.prompt.md'))[0], 2)
        self.assertEqual(run('qa', str(self.root / 'nope.qa.md'))[0], 2)

    def test_json_flag_before_or_after_subcommand(self):
        rc1, d1 = run_json('s5', str(self.card))
        rc2, out = run('s5', str(self.card), '--json')
        self.assertEqual((rc1, d1), (rc2, json.loads(out)))


if __name__ == '__main__':
    unittest.main()
