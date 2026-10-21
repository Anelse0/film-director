#!/usr/bin/env python3
"""一键检查入口（1.13.0，复盘提案 M1 / M2）。

四个校验脚本没变、校验码没变、阈值与 ERROR / WARN 分类没变：本脚本只 import `camera_plan_check.check()`、
`stage_check.check()`、`validate_prompt.validate()`、`qa_check.check()`，不复制任何检查逻辑，把 1.12.1 脚本表里的
7 个时机合成 3 个子命令，输出一份合并报告：

  ERROR → 成片教训类 WARN（validate_prompt 的 RENDER_LESSON_CODES / RENDER_LESSON_PREFIXES）→ 其余 WARN
  → 数字块（templates/qa.md 现行状态的「校验 / 机位设计 / 执行卡」三行 + 第 8 道那一行，格式一致，可直接粘贴）
  → 原有全部 INFO 行 → 每个输入文件的 sha256 前 12 位（文件没变就不必再跑）。

  check.py plan <分镜卡>             = 1.14.0 停靠 A（方案）：camera_plan_check --stage s5 + 镜头纵览的算术
                                      （行数、时间是否从 0 连续、台词行数、无台词秒、表下的最长连续无台词 >3 s 提示）；
                                      逐镜小节与执行卡还没写，不跑 stage_check；提示是 NOTE，不是校验码
  所有子命令：分镜卡版本行 / Prompt E 表「版本」行超过 200 字给 NOTE（1.14.1 版本行一行制，不是校验码）
  check.py s5 <分镜卡>               = camera_plan_check --stage s5 + stage_check --stage s5
  check.py s6 <分镜卡> [<prompt.md>] = camera_plan_check（不带 --stage，C08）+ stage_check --stage s6
                                      + validate_prompt + camera_plan_check --prompt（C10）
                                      S6 入口还没有 Prompt 时只给分镜卡，后两步跳过
  check.py qa [--sync] [--prompt <prompt.md>] <qa.md>
                                    = qa_check；现行状态里能解析出 Prompt / 分镜卡路径时顺带跑一遍 s6
    --sync                            把现行状态里机器能定的五行（Prompt 版本、分镜卡版本、校验、机位设计、执行卡）
                                      和第 8 道的数字行按实际运行结果写回 qa.md；成片 / 上游末帧 / 未决 / 用户已点名
                                      四行不动；写完再独立跑一遍 qa_check 并打印结果
  --json                              机器可读输出

第 8 道数字行的来源：最长连续无台词 = Prompt 台词窗口之间最长的空档（和 W24 最长连续无台词用同一定义），括号里附
分镜卡 E 层「最长无台词」；一句一镜 / 总句 = 总句数 − W54 报的跨镜句；反应镜数 = E 层「反应镜」行里「同镜」之前的镜号数；
画外句数 = 括号里写了画外 / off-screen 的台词数；句尾后停留 ≥1 s 的镜 = 镜尾比该镜最后一句窗口尾晚 ≥1 s 的镜
（和 rhythm_checks 的 INFO 同一定义）；最后一格「不达标项处置」留给人，--sync 原样保留。

退出码：0 = 没有 ERROR（可有 WARN）；1 = 有 ERROR；2 = 用法 / 文件错误。
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import camera_plan_check  # noqa: E402
import qa_check  # noqa: E402
import speaker_checks  # noqa: E402
import stage_check  # noqa: E402
import validate_prompt  # noqa: E402

STATE_ORDER = ('Prompt', '分镜卡', '成片', '上游末帧', '校验', '机位设计', '未决', '用户已点名', '执行卡')
HUMAN_LINES = ('成片', '上游末帧', '未决', '用户已点名')
MACHINE_LINES = tuple(l for l in STATE_ORDER if l not in HUMAN_LINES)
GATE8_HEADER = '| 最长连续无台词 | 一句一镜 / 总句 | 反应镜数 | 画外句数 | 句尾后停留 ≥1 s 的镜 | 不达标项处置 |'
GATE8_PLACEHOLDER = '<不达标项处置>'
VERSION_RE = re.compile(r'\bv\d+(?:\.\d+)*\b')
MD_PATH_RE = re.compile(r'`([^`]+\.md)`')


# ---------- helpers ----------
def sha12(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def code_of(message):
    return message.split()[0] if message.split() else message


def codes(messages):
    return sorted({code_of(m) for m in messages})


def joined(items, empty='无'):
    return '、'.join(items) if items else empty


def today():
    return datetime.date.today().isoformat()


def card_version(text):
    head = text[:4000]
    m = re.search(r'版本[：:]?\s*\**\s*(v\d+(?:\.\d+)*)', head)
    if m:
        return m.group(1)
    m = VERSION_RE.search(head)
    return m.group(0) if m else None


VERSION_LINE_MAX = 200  # 1.14.1 版本行一行制：超过给 NOTE，不是校验码


def version_line_notes(card_text=None, prompt_text=None):
    """分镜卡卡头的版本行 / Prompt E 表的「版本」行超过 VERSION_LINE_MAX 字时各给一条 NOTE（1.14.1）。"""
    notes = []
    if card_text:
        m = re.search(r'^\W*版本[：:].*$', card_text[:6000], re.M)
        if m and len(m.group(0)) > VERSION_LINE_MAX:
            notes.append(f'分镜卡版本行 {len(m.group(0))} 字（>{VERSION_LINE_MAX}）：版本行一行制——只留版本 · 日期 · 状态 · skill 版本 · Prompt 版本，'
                         '改了什么写 QA ## 历史 一版一条，用户原话进执行卡第 22 行（1.14.1）')
    if prompt_text:
        m = re.search(r'^\|\s*版本\s*\|[^\n]*$', prompt_text, re.M)
        if m and len(m.group(0)) > VERSION_LINE_MAX:
            notes.append(f'Prompt E 表「版本」行 {len(m.group(0))} 字（>{VERSION_LINE_MAX}）：只写版本号和日期，'
                         '改了什么写 QA ## 历史 一版一条（1.14.1）')
    return notes


def e_row(text, key):
    """A row of the shot card's `## E 层` table (the 手法分布 table may carry a row of the same name)."""
    layer = stage_check.section(text, 'E 层')
    return stage_check.e_value(layer if layer is not None else text, key)


def display(path):
    try:
        return Path(path).resolve().relative_to(Path.cwd())
    except ValueError:
        return Path(path)


def state_block(text):
    """(start, end) of the `## 现行状态` body in a QA file, or None."""
    heads = list(re.finditer(r'^## (.+)$', text, flags=re.M))
    for i, m in enumerate(heads):
        if m.group(1).startswith('现行状态'):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return m.end(), end
    return None


def state_line(block, label):
    pat = re.compile(rf'^[ \t]*-[ \t]*{re.escape(label)}[^：:\n]*[：:][^\n]*$', re.M)
    return pat.search(block)


def resolve_from_state(qa_path, block, label):
    m = MD_PATH_RE.search(state_line(block, label).group(0) if state_line(block, label) else '')
    if not m:
        return None, None
    for base in (qa_path.parent.parent, qa_path.parent, Path.cwd()):
        candidate = base / m.group(1)
        if candidate.exists():
            return candidate, m.group(1)
    return None, m.group(1)


# ---------- the merged report ----------
class Report:
    def __init__(self, command, inputs):
        self.command = command
        self.inputs = [Path(p) for p in inputs]
        self.runs = []      # (tool label, errors, warnings, infos)
        self.block = []     # 数字块 lines
        self.notes = []     # one-line remarks (missing files, skipped steps)
        self.sync = None    # --sync summary
        self.after = None   # qa_check after --sync: (errors, warnings)

    def add(self, tool, errors, warnings, infos=()):
        self.runs.append((tool, list(errors), list(warnings), list(infos)))

    def tagged(self, index):
        return [(tool, m) for tool, *rest in self.runs for m in rest[index]]

    def errors(self):
        out = self.tagged(0)
        if self.after and self.after[0]:
            out += [('qa_check（写回后）', e) for e in self.after[0]]
        return out

    def warnings(self):
        return self.tagged(1)

    def render_lessons(self):
        return [(t, w) for t, w in self.warnings() if t.startswith('validate_prompt') and validate_prompt.is_render_lesson(w)]

    def other_warnings(self):
        lessons = set(self.render_lessons())
        return [(t, w) for t, w in self.warnings() if (t, w) not in lessons]

    def infos(self):
        return self.tagged(2)

    def hashes(self):
        return {str(p): sha12(p) for p in self.inputs if p.exists()}

    def exit_code(self):
        return 1 if self.errors() else 0

    def render(self):
        lines = [f"== check.py {self.command}: " + ' + '.join(str(p) for p in self.inputs)]
        for note in self.notes:
            lines.append(f'NOTE  {note}')
        errors, lessons, others = self.errors(), self.render_lessons(), self.other_warnings()
        lines.append(f'-- ERROR {len(errors)}')
        lines += [f'ERROR [{t}] {m}' for t, m in errors]
        lines.append(f'-- 成片教训类 WARN {len(lessons)}（默认改，保留要用户点头并在 QA 记原话）')
        lines += [f'WARN  [{t}] {m}' for t, m in lessons]
        lines.append(f'-- 其余 WARN {len(others)}')
        lines += [f'WARN  [{t}] {m}' for t, m in others]
        if self.block:
            lines.append('-- 数字块（现行状态机器行 + 第 8 道数字行，格式同 templates/qa.md，可直接粘贴）')
            lines += self.block
        infos = self.infos()
        lines.append(f'-- INFO {len(infos)}')
        lines += [f'INFO  [{t}] {m}' if not m.startswith('CHECK ') else f'CHECK [{t}] {m[6:]}' for t, m in infos]
        lines.append('-- sha256 前 12 位（文件没变就不必再跑）')
        lines += [f'HASH  {p} {h}' for p, h in self.hashes().items()]
        if self.sync is not None:
            lines.append(f"-- --sync 写回 {self.sync['file']}")
            lines.append(self.sync['summary'])
        if self.after is not None:
            e, w = self.after
            lines.append(f'== qa_check（写回后独立跑）: {self.sync["file"]}')
            lines += [f'ERROR {x}' for x in e] + [f'WARN  {x}' for x in w]
            lines.append(f'== {len(e)} error(s), {len(w)} warning(s)')
        lines.append(f"== {len(errors)} error(s), {len(self.warnings())} warning(s)")
        return '\n'.join(lines)

    def to_json(self):
        return {
            'command': self.command,
            'inputs': [str(p) for p in self.inputs],
            'notes': self.notes,
            'runs': [{'tool': t, 'errors': e, 'warnings': w, 'info': i} for t, e, w, i in self.runs],
            'errors': [{'tool': t, 'message': m} for t, m in self.errors()],
            'render_lessons': [{'tool': t, 'message': m} for t, m in self.render_lessons()],
            'warnings': [{'tool': t, 'message': m} for t, m in self.other_warnings()],
            'block': self.block,
            'info': [{'tool': t, 'message': m} for t, m in self.infos()],
            'sha256': self.hashes(),
            'sync': self.sync,
            'qa_check_after_sync': None if self.after is None else {'errors': self.after[0], 'warnings': self.after[1]},
            'exit': self.exit_code(),
        }


# ---------- facts behind the 数字块 ----------
def facts_from(card=None, prompt=None, result=None, camera=None, c10_checked=False, stage=None):
    """Machine-determined values. camera / stage: (errors, warnings) of the fullest run of that script."""
    f = {}
    card_text = Path(card).read_text(encoding='utf-8') if card else ''
    prompt_text = Path(prompt).read_text(encoding='utf-8') if prompt else ''
    if card_text:
        f['分镜卡 版本'] = card_version(card_text)
    if prompt_text:
        f['Prompt 版本'] = qa_check.prompt_version(prompt_text)
    if result is not None:
        lessons = list(dict.fromkeys((code_of(w) if code_of(w) != 'W24' else 'W24（最长连续无台词）')
                                     for w in result['warnings'] if validate_prompt.is_render_lesson(w)))
        f['校验'] = (f"- 校验：validate_prompt {today()} {len(result['errors'])} ERROR；"
                   f"WARN {joined(codes(result['warnings']))}；成片教训类 {joined(lessons)}")
    if camera is not None:
        errors, warnings = camera
        parts = []
        if c10_checked:
            c10 = [e for e in errors if e.startswith('C10')]
            parts.append('C10 无矛盾' if not c10 else f'C10 {len(c10)} 处矛盾')
        parts.append('WARN ' + joined(codes(warnings)))
        f['机位设计'] = f"- 机位设计：camera_plan_check {len(errors)} ERROR；{'；'.join(parts)}"
    if stage is not None:
        errors, warnings = stage
        rows = 'S5 25 行' if not any(e.startswith(('S01', 'S02')) for e in errors) else 'S5 执行卡缺行'
        f['执行卡'] = f"- 执行卡：stage_check {len(errors)} ERROR（{rows}；{joined(codes(warnings))}）"
    f['第 8 道'] = gate8_cells(card_text, prompt_text, result)
    return f


def gate8_cells(card_text, prompt_text, result):
    cells = ['—'] * 5
    if result is None or not prompt_text:
        if card_text:
            cells[2] = reaction_count(card_text)
        return cells
    shots = validate_prompt.split_shots(prompt_text)
    duration = validate_prompt.declared_duration(prompt_text, None)
    if duration is None and shots:
        duration = shots[-1][2]
    rows = result.get('dialogue') or []
    explicit = sorted([r for r in rows if r['explicit'] and r['end'] > r['start']], key=lambda r: (r['start'], r['end']))
    # 1 最长连续无台词（台词窗口之间最长的空档；与 W24 最长连续无台词同一定义）
    if duration:
        stretches, prev_end = [], 0.0
        for r in explicit:
            if r['start'] > prev_end:
                stretches.append((prev_end, r['start']))
            prev_end = max(prev_end, r['end'])
        if duration > prev_end:
            stretches.append((prev_end, duration))
        if stretches:
            a, b = max(stretches, key=lambda x: x[1] - x[0])
            inside = [str(no) for no, s0, e0, _ in shots if s0 < b and e0 > a]
            cells[0] = f"{b - a:g} s（{a:g}-{b:g}s" + (f"，镜头{'、'.join(inside)}" if inside else '') + '）'
        else:
            cells[0] = '0 s'
        e_value = e_row(card_text, '最长无台词') if card_text else None
        number = re.search(r'\d+(?:\.\d+)?', e_value or '')
        if number:
            cells[0] = cells[0] + f'；E 层 {number.group(0)} s'
    # 2 一句一镜 / 总句（总句数 − W54 跨镜句）
    split = sum(1 for w in result['warnings'] if re.match(r'W54 镜头\d+→镜头', w))
    cells[1] = f'{len(rows) - split} / {len(rows)}'
    # 3 反应镜数（分镜卡 E 层）
    cells[2] = reaction_count(card_text) if card_text else '—'
    # 4 画外句数
    cells[3] = str(sum(1 for _, _, _, body in shots for _, details, _ in speaker_checks.speech_tags(body)
                       if speaker_checks.OFF_RE.search(details)))
    # 5 句尾后停留 ≥1 s 的镜（镜尾 − 该镜最后一句窗口尾；与 rhythm_checks 的 INFO 同一定义）
    holds = []
    for no, s, e, _ in shots:
        lines = [r for r in explicit if r['shot'] == str(no)]
        if lines:
            hold = e - max(r['end'] for r in lines)
            if hold >= 1.0 - 1e-9:
                holds.append(f'镜 {no}（{hold:g}s）')
    cells[4] = joined(holds)
    return cells


def reaction_count(card_text):
    value = e_row(card_text, '反应镜')
    if value is None:
        return '—'
    if value.strip().startswith('无'):
        return '0'
    counted = value.split('同镜')[0]
    return str(len(set(re.findall(r'镜\s*(\d+)', counted))))


def gate8_row(cells, last=GATE8_PLACEHOLDER):
    return '| ' + ' | '.join(list(cells) + [last]) + ' |'


# ---------- 停靠 A：镜头纵览算术（1.14.0） ----------
OVERVIEW_TIME = re.compile(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*s')
UNFILLED = re.compile(r'^\s*(?:_+|待定|TODO|TBD|？|\?)\s*$', re.I)
NO_LINE = {'—', '-', '无', '─', '——'}


def overview_facts(card_text):
    """`## 镜头纵览` 的算术：行数、时间是否连续、台词行数、无台词秒、表下的最长连续无台词。没有表返回 None。"""
    block = stage_check.section(card_text, '镜头纵览')
    if block is None:
        return None
    header, rows = stage_check.table_rows(block)
    facts = {'rows': 0, 'gaps': [], 'lines': 0, 'silent_sum': 0.0, 'silent_max': 0.0, 'end': None, 'unfilled': [],
             'longest': None, 'shots': len(re.findall(r'^## 镜头\s*(\d+)', card_text, flags=re.M))}
    m = re.search(r'最长连续无台词\s*\|\s*(\d+(?:\.\d+)?)\s*s', card_text)
    if m:
        facts['longest'] = float(m.group(1))
    if header is None:
        return facts
    idx = lambda name: next((i for i, h in enumerate(header) if name in h), None)
    i_time, i_line, i_silent = idx('时间'), idx('台词'), idx('无台词')
    prev_end = 0.0
    for r in rows:
        if not r or not re.match(r'\d+', r[0]):
            continue
        facts['rows'] += 1
        cell = lambda i: r[i] if i is not None and i < len(r) else ''
        t = OVERVIEW_TIME.search(cell(i_time))
        if t:
            s, e = float(t.group(1)), float(t.group(2))
            if abs(s - prev_end) > 1e-9:
                facts['gaps'].append(f'镜 {r[0]} 从 {s:g}s 起，上一镜止于 {prev_end:g}s')
            prev_end = e
            facts['end'] = e
        if cell(i_line).strip() and cell(i_line).strip() not in NO_LINE:
            facts['lines'] += 1
        sec = re.search(r'\d+(?:\.\d+)?', cell(i_silent))
        if sec:
            v = float(sec.group(0))
            facts['silent_sum'] += v
            facts['silent_max'] = max(facts['silent_max'], v)
        for i, c in enumerate(r[1:], start=2):
            if UNFILLED.match(c):
                facts['unfilled'].append(f'镜 {r[0]} 第 {i} 列')
                break
    return facts


def pipeline_plan(card, report):
    ce, cw = camera_plan_check.check(card, 's5')
    report.add('camera_plan_check --stage s5', ce, cw)
    text = Path(card).read_text(encoding='utf-8')
    f = overview_facts(text)
    infos, notes = [], []
    if f is None:
        notes.append('没有「## 镜头纵览」表：停靠 A 要先有每镜一行的纵览（S5 §5.2 第 8 步后、§5.6 前）')
    else:
        infos.append(f"镜头纵览 {f['rows']} 行"
                     + (f"，分镜卡已有「## 镜头 N」{f['shots']} 个" if f['shots'] else '，逐镜小节还没写（停靠 A 正常）')
                     + (f"；时间止于 {f['end']:g}s" if f['end'] is not None else ''))
        infos.append(f"台词行 {f['lines']}；无台词秒 合计 {f['silent_sum']:g}s / 单镜最大 {f['silent_max']:g}s"
                     + (f"；表下最长连续无台词 {f['longest']:g}s" if f['longest'] is not None else '；表下没写「最长连续无台词 | N s」'))
        notes += ['纵览时间不连续：' + g for g in f['gaps']]
        if f['shots'] and f['rows'] != f['shots']:
            notes.append(f"纵览 {f['rows']} 行 ≠ 「## 镜头 N」{f['shots']} 个（停靠 B 时 stage_check C11 会报）")
        if f['longest'] is not None and f['longest'] > stage_check.DEFAULT_MAX_SILENT + 1e-9:
            notes.append(f"表下最长连续无台词 {f['longest']:g}s > {stage_check.DEFAULT_MAX_SILENT:g} s：停靠 A 就要用户点头"
                         '（停靠 B 由 stage_check W-C7 按 E 层查；这里是提示，不是校验码）')
        if f['unfilled']:
            notes.append('纵览未填格：' + '、'.join(f['unfilled'][:6]))
    report.add('镜头纵览算术', [], [], infos)
    report.notes.extend(notes + version_line_notes(card_text=text))
    return facts_from(card=card, camera=(ce, cw))


# ---------- pipelines ----------
def pipeline_s5(card, report):
    ce, cw = camera_plan_check.check(card, 's5')
    report.add('camera_plan_check --stage s5', ce, cw)
    se, sw = stage_check.check(card, 's5')
    report.add('stage_check --stage s5', se, sw)
    report.notes.extend(version_line_notes(card_text=Path(card).read_text(encoding='utf-8')))
    return facts_from(card=card, camera=(ce, cw), stage=(se, sw))


def pipeline_s6(card, prompt, report):
    ce, cw = camera_plan_check.check(card, 's6')
    report.add('camera_plan_check', ce, cw)
    se, sw = stage_check.check(card, 's6')
    report.add('stage_check --stage s6', se, sw)
    result, camera = None, (ce, cw)
    if prompt:
        result = validate_prompt.validate(prompt)
        infos = list(result['info']) + ([f"透镜 {result['lens']}"] if result['lens'] else []) \
            + ['CHECK ' + json.dumps(result['checks'], ensure_ascii=False)]
        report.add('validate_prompt', result['errors'], result['warnings'], infos)
        pe, pw = camera_plan_check.check(card, 's6', prompt)
        report.add('camera_plan_check --prompt', [x for x in pe if x not in ce], [x for x in pw if x not in cw])
        camera = (pe, pw)
    else:
        report.notes.append('没有给 Prompt：validate_prompt 与 camera_plan_check --prompt（C10）没跑（S6 入口可以这样；S6 后要带 Prompt 再跑）')
    report.notes.extend(version_line_notes(card_text=Path(card).read_text(encoding='utf-8'),
                                           prompt_text=Path(prompt).read_text(encoding='utf-8') if prompt else None))
    return facts_from(card=card, prompt=prompt, result=result, camera=camera, c10_checked=bool(prompt), stage=(se, sw))


def block_lines(facts, labels, gate8=True):
    lines = [facts[l] for l in labels if facts.get(l)]
    if gate8:
        lines.append(gate8_row(facts['第 8 道'], facts.get('第 8 道处置') or GATE8_PLACEHOLDER))
    return lines


def existing_gate8_last(text):
    section = gate8_section(text)
    if not section:
        return None
    _, _, data = gate8_rows(section[2])
    if data is None:
        return None
    cells = [c.strip() for c in data.strip().strip('|').split('|')]
    return cells[-1] if len(cells) >= 6 and cells[-1] else None


def gate8_section(text):
    m = re.search(r'^###\s*8\b[^\n]*\n', text, flags=re.M)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r'^#{2,3} ', rest, flags=re.M)
    end = m.end() + (nxt.start() if nxt else len(rest))
    return m.end(), end, text[m.end():end]


def gate8_rows(section):
    """(header line index, separator index, first data row text or None) inside the section's lines."""
    lines = section.split('\n')
    for i, l in enumerate(lines[:-1]):
        if l.strip().startswith('|') and re.match(r'^\s*\|\s*:?-', lines[i + 1]):
            data = lines[i + 2] if i + 2 < len(lines) and lines[i + 2].strip().startswith('|') else None
            return i, i + 1, data
    return None, None, None


# ---------- --sync ----------
def sync_state(text, facts, state_paths):
    """Rewrite the machine lines of 现行状态 and the gate-8 data row. Returns (new_text, written labels, skipped notes)."""
    written, skipped = [], []
    span = state_block(text)
    if span is None:
        return text, written, ['没有「## 现行状态」节，机器行没写（Q01 会报）']
    start, end = span
    block = text[start:end]
    new_lines = {}
    for label in ('Prompt', '分镜卡'):
        version = facts.get(f'{label} 版本')
        path_text = state_paths.get(label)
        if version and path_text:
            new_lines[label] = f'- {label}：`{path_text}` {version}'
        else:
            skipped.append(f'{label} 行：' + ('文件没找到' if not path_text else '版本号没解析出来') + '，没动')
    for label in ('校验', '机位设计', '执行卡'):
        if facts.get(label):
            new_lines[label] = facts[label]
        else:
            skipped.append(f'{label} 行：对应脚本没跑，没动')
    for label in MACHINE_LINES:
        if label not in new_lines:
            continue
        m = state_line(block, label)
        if m:
            if m.group(0) != new_lines[label]:
                written.append(label)
            block = block[:m.start()] + new_lines[label] + block[m.end():]
        else:
            block = insert_line(block, label, new_lines[label])
            written.append(label)
    text = text[:start] + block + text[end:]
    # 第 8 道
    section = gate8_section(text)
    if section is None:
        skipped.append('第 8 道：没有「### 8」节，数字行没写')
        return text, written, skipped
    s_start, s_end, body = section
    h, sep, data = gate8_rows(body)
    lines = body.split('\n')
    if h is None:
        lines = [GATE8_HEADER, '|---|---|---|---|---|---|', gate8_row(facts['第 8 道'])] + lines
        written.append('第 8 道')
    else:
        last = GATE8_PLACEHOLDER
        if data is not None:
            cells = [c.strip() for c in data.strip().strip('|').split('|')]
            if len(cells) >= 6 and cells[-1]:
                last = cells[-1]
        row = gate8_row(facts['第 8 道'], last)
        if data is None:
            lines.insert(sep + 1, row)
            written.append('第 8 道')
        elif lines[sep + 1] != row:
            lines[sep + 1] = row
            written.append('第 8 道')
    text = text[:s_start] + '\n'.join(lines) + text[s_end:]
    return text, written, skipped


def insert_line(block, label, line):
    """Put a missing machine line where the template has it: after the nearest preceding label that exists."""
    before = STATE_ORDER[:STATE_ORDER.index(label)]
    for prev in reversed(before):
        m = state_line(block, prev)
        if m:
            # skip the sub-bullets that belong to a human line (e.g. 未决 的子项)
            tail = block[m.end():]
            sub = re.match(r'(?:\n[ \t]+-[^\n]*)*', tail)
            cut = m.end() + (sub.end() if sub else 0)
            return block[:cut] + '\n' + line + block[cut:]
    first = re.search(r'^[ \t]*-[ \t]*', block, flags=re.M)
    if first:
        return block[:first.start()] + line + '\n' + block[first.start():]
    return block.rstrip('\n') + '\n\n' + line + '\n\n'


# ---------- commands ----------
def cmd_plan(args):
    card = Path(args.card)
    if not card.is_file():
        print(f'分镜卡不存在：{card}', file=sys.stderr)
        return None
    report = Report('plan', [card])
    facts = pipeline_plan(str(card), report)
    report.block = block_lines(facts, ('机位设计',), gate8=False)
    return report


def cmd_s5(args):
    card = Path(args.card)
    if not card.is_file():
        print(f'分镜卡不存在：{card}', file=sys.stderr)
        return None
    report = Report('s5', [card])
    facts = pipeline_s5(str(card), report)
    report.block = block_lines(facts, ('机位设计', '执行卡'), gate8=False)
    return report


def cmd_s6(args):
    card, prompt = Path(args.card), (Path(args.prompt) if args.prompt else None)
    for p in (card, prompt):
        if p is not None and not p.is_file():
            print(f'文件不存在：{p}', file=sys.stderr)
            return None
    report = Report('s6', [card] + ([prompt] if prompt else []))
    facts = pipeline_s6(str(card), str(prompt) if prompt else None, report)
    report.block = block_lines(facts, ('校验', '机位设计', '执行卡'))
    return report


def cmd_qa(args):
    qa = Path(args.qa)
    if not qa.is_file():
        print(f'QA 文件不存在：{qa}', file=sys.stderr)
        return None
    qa = qa.resolve()
    text = qa.read_text(encoding='utf-8')
    span = state_block(text)
    block = text[span[0]:span[1]] if span else ''
    prompt, prompt_text_path = resolve_from_state(qa, block, 'Prompt')
    if args.prompt:
        prompt = Path(args.prompt)
        prompt_text_path = prompt_text_path or str(prompt)
    card, card_text_path = resolve_from_state(qa, block, '分镜卡')
    inputs = [display(qa)] + [display(p) for p in (card, prompt) if p]
    report = Report('qa', inputs)
    facts = {}
    if card and prompt:
        facts = pipeline_s6(str(card), str(prompt), report)
    elif prompt:
        report.notes.append('现行状态里没有能找到的分镜卡：只跑 validate_prompt，camera_plan_check / stage_check 没跑')
        result = validate_prompt.validate(prompt)
        infos = list(result['info']) + ([f"透镜 {result['lens']}"] if result['lens'] else []) \
            + ['CHECK ' + json.dumps(result['checks'], ensure_ascii=False)]
        report.add('validate_prompt', result['errors'], result['warnings'], infos)
        facts = facts_from(prompt=str(prompt), result=result)
    else:
        report.notes.append('现行状态里没有能找到的 Prompt / 分镜卡：只跑 qa_check（用 --prompt 指定 Prompt）')
    if facts:
        facts['第 8 道处置'] = existing_gate8_last(text)
        report.block = block_lines(facts, ('校验', '机位设计', '执行卡'))
        for label, key in (('Prompt', 'Prompt 版本'), ('分镜卡', '分镜卡 版本')):
            path_text = {'Prompt': prompt_text_path, '分镜卡': card_text_path}[label]
            if facts.get(key) and path_text:
                report.block.insert(0 if label == 'Prompt' else 1, f'- {label}：`{path_text}` {facts[key]}')
    if args.sync:
        if not facts:
            report.notes.append('--sync：没有可写的机器行（Prompt / 分镜卡都没找到）')
        else:
            new_text, written, skipped = sync_state(text, facts, {'Prompt': prompt_text_path, '分镜卡': card_text_path})
            if new_text != text:
                qa.write_text(new_text, encoding='utf-8')
            summary = ('写入：' + '、'.join(written) if written else '无变化：机器行已是现行结果') \
                + '（成片 / 上游末帧 / 未决 / 用户已点名 不动）' + ('；' + '；'.join(skipped) if skipped else '')
            report.sync = {'file': str(qa), 'written': written, 'skipped': skipped, 'changed': new_text != text, 'summary': summary}
        e, w = qa_check.check(qa, str(prompt) if prompt else None)
        report.after = (e, w)
        if report.sync is None:
            report.sync = {'file': str(qa), 'written': [], 'skipped': [], 'changed': False, 'summary': '没有写回'}
    else:
        e, w = qa_check.check(qa, str(prompt) if prompt else None)
        report.add('qa_check', e, w)
    return report


def build_parser():
    parser = argparse.ArgumentParser(prog='check.py', description='一键检查入口：合并四个校验脚本的结果，不改任何检查')
    parser.add_argument('--json', action='store_true', help='机器可读输出')
    sub = parser.add_subparsers(dest='command', required=True)
    pp = sub.add_parser('plan', help='S5 停靠 A 前（1.14.0）：camera_plan_check --stage s5 + 镜头纵览算术，不跑 stage_check')
    pp.add_argument('card', metavar='<分镜卡>')
    p5 = sub.add_parser('s5', help='S5 停靠前（停靠 B）：camera_plan_check --stage s5 + stage_check --stage s5')
    p5.add_argument('card', metavar='<分镜卡>')
    p6 = sub.add_parser('s6', help='S6 入口与 S6 后：camera_plan_check + stage_check --stage s6 + validate_prompt + camera_plan_check --prompt')
    p6.add_argument('card', metavar='<分镜卡>')
    p6.add_argument('prompt', nargs='?', metavar='<prompt.md>')
    pq = sub.add_parser('qa', help='QA 改完：qa_check（+ 现行状态能解析出路径时跑 s6）；--sync 写回机器行')
    pq.add_argument('qa', metavar='<qa.md>')
    pq.add_argument('--sync', action='store_true', help='把机器行按实际运行结果写回 qa.md，再独立跑一遍 qa_check')
    pq.add_argument('--prompt', metavar='<prompt.md>', help='现行状态里的 Prompt 路径找不到时指定')
    for p in (p5, p6, pq):  # --json 也可以写在子命令后面；SUPPRESS 让子命令不覆盖主解析器上的值
        p.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
    return parser


def main(argv):
    parser = build_parser()
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit as exc:
        return 2 if exc.code else 0
    report = {'plan': cmd_plan, 's5': cmd_s5, 's6': cmd_s6, 'qa': cmd_qa}[args.command](args)
    if report is None:
        return 2
    if getattr(args, 'json', False):
        print(json.dumps(report.to_json(), ensure_ascii=False, indent=2))
    else:
        print(report.render())
    return report.exit_code()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
