#!/usr/bin/env python3
"""场面轨 / 事件轨：剧本的场地 / 场景清单作参考，分镜的场级合计与之对照；每条 clip 交付哪几次变化（film-director 1.6.0）。

用法:
  scene_track.py 03_script/scene-04.md                                   # 只列参考清单
  scene_track.py 03_script/scene-04.md --clips 04_shots/*-s04-clip*.md   # + 场级合计与比值
  scene_track.py 03_script/scene-04.md --clips … --plan 04_shots/*-s04-plan.md [--json]

剧本页正文前的轨表有两种格式，本脚本都读：film-creative 3.7+ 的"## 事件轨"（人物清单 + 一行一次变化：
# / 谁 → 对谁 / 变化：进 → 出（类别）/ 说出口 / 删掉损失 / 地点（子空间）/ 活动 / 时间 / 锚句 / 估时），
和 3.6 的"## 场面轨"（段 / 地点（子空间）/ 主要活动 / 时间 / 谁在画面里 / 观众这段新看见什么 / 锚句 / 估时）。
两种都只取 地点 / 活动 / 时间 / 锚句 / 估时 与行号；对本 skill 是**告知，不是锁定**：分镜可以重分段、换子空间、
换活动或地点，只要在场级方案里写一行"与场面轨的差异：…"（"与事件轨的差异：…"同样认；没改写"无"）。
台词仍是锁定输入。

- 参考清单：本场有哪些场地 / 场景、几段（行）、有几次时间跳、剧本总估时（轨表"总估时"或各行估时之和；
  两种轨表都没有的旧稿回退到节拍表"总窗口 ≈ N s"）。地点以"同上 / 同前 / 连续 / 接上 / 紧接"开头的行沿用
  上一行的场地（1.13.0：film-creative 4.0 模板"地点沿用上一行写'同上'"；"同上，沿通道往出口"仍是同一处），
  括号里的子空间照旧并到该场地下；第一行没有上一行可沿用，按原文列出。
- 设计卡（1.13.0）：film-creative 4.0+ 剧本页正文前的"## 设计"，只取"静音测试"一格列出——关掉声音也看得懂
  谁要、谁赢的那个动作，S5 定视觉重点与峰值事件时的候选（stage-5 §5.1b）。告知，不锁定：不报问题、不影响
  退出码；没有设计卡的旧稿、没填或写"本场不转"的卡照旧，只是不列。
- 场级合计：各分镜卡头部"clip 时长 N s"之和。合计 / 剧本估时 ≥ 1.2 → **提醒**（多出来的时间观众在看什么、
  是不是同一个画面拉长了），照常继续，不退回；回不回剧本层由用户定。1.2 按 THE ORDER 已出分镜的 5 场定：
  只有 EP03 场 4 的两版超出（1.28 / 1.30），其余 1.02–1.13（`[推论]`，见 references/duration-rhythm.md §十一）。
- 差异行：剧本有场面轨或事件轨、又给了 --plan 时，方案里必须有"与场面轨的差异"（或"与事件轨的差异"）一行。
- 交付变化（1.6.0）：场级方案的 clip 切分表（首列 clip）必须有"交付变化"一列，写本条交付事件轨哪几行
  （"第 3–6 行"）。剧本有事件轨时：每条 clip 至少交付一个变化行；余韵行（"无（余韵：…）"）可以写上但不计入交付，
  只交付余韵的 clip 报问题（余韵不单独成 clip）；同一变化行只能由一条 clip 交付；行号必须在事件轨里；
  没有 clip 交付的变化行只提醒（有意删掉写进差异行）。每条 clip 的"删掉损失"取自它交付那几行——
  回答"这 N 秒存在的意义是？"。规则本身不依赖 film-creative 的模板：没有事件轨的剧本（3.6 场面轨、无轨、
  任何来源的场景稿）由分镜自己写出这条 clip 交付的变化"谁：进 → 出"，脚本查有没有"→"、是不是"无"。
  这一列管"这条 clip 该不该存在"；峰值事件、变化轨四维字段（W30–W33）、无声段理由（W24）管"clip 里怎么拍"，
  照常填、照常校验，不被这一列取代，也不能代替它。

不改任何文件；零外部依赖。退出码：0 = 通过或只有提醒，1 = 方案缺差异行 / 交付变化不成立，2 = 输入无法解析。
"""
import argparse
import json
import re
import sys
from pathlib import Path

REMIND_RATIO = 1.2  # [推论]
TRACK_HEAD = re.compile(r'^##\s*(场面轨|事件轨)[^\n]*$', re.M)  # 3.6 场面轨 / 3.7+ 事件轨
COLS = (('seg', ('段', '#')), ('loc', ('地点',)), ('act', ('活动',)), ('time', ('时间',)), ('who', ('谁',)),
        ('new', ('新看见',)), ('anchor', ('锚句',)), ('est', ('估时',)), ('change', ('变化',)), ('loss', ('删掉损失',)))
EVENT_ONLY = ('change', 'loss')  # 3.6 场面轨"主要活动（类别；变化写括号）"也含"变化"，只在事件轨里读
EMPTY = {'', '—', '-', '无', '空', '__'}
CONTINUOUS = ('连续', '接上', '同上', '同前', '紧接')  # 地点 / 时间沿用上一行（与 film-creative review_script 同一组）
PARENS = re.compile(r'[（(][^)）]*[)）]')
DESIGN_HEAD = re.compile(r'^##\s*设计(?=[\s（(]|$)[^\n]*$', re.M)  # film-creative 4.0+ 设计卡；"## 设计原则"一类不算
SILENT_CELL = re.compile(r'静音测试[^：:\n]{0,8}[：:]\s*([^\n]*)')
CLIP_LEN = re.compile(r'clip\s*时长\s*(\d+(?:\.\d+)?)\s*s')
DIFF_LINE = re.compile(r'与(?:场面轨|事件轨)的差异\s*[:：]?\s*(.*)')
DELIVER_COL = '交付变化'
ROW_REFS = re.compile(r'第\s*([\d\s–—\-~～至到、，,和]+?)\s*行')
BARE_REFS = re.compile(r'[\d\s–—\-~～至到、，,和]+')
ARROW = re.compile(r'→|->|⟶')
RANGE = re.compile(r'(\d+)\s*(?:[–—\-~～至到]\s*(\d+))?')


def _cells(row):
    return [c.strip() for c in row.strip().strip('|').split('|')]


def _base(cell):
    return re.sub(r'\s+', ' ', PARENS.sub('', cell)).strip()


def read_track(text):
    """返回 {'rows', 'total', 'source', 'kind'}；两种轨表都没有时 rows 为空、kind 为 None、total 回退到节拍表总窗口。"""
    rows, total, source, kind = [], None, None, None
    m = TRACK_HEAD.search(text)
    if m:
        kind = m.group(1)
        sec = re.split(r'\n## ', text[m.end():], maxsplit=1)[0]
        table = [r for r in sec.splitlines() if r.strip().startswith('|')]
        if table:
            header = _cells(table[0])
            idx = {k: next((i for i, h in enumerate(header) if any(w in h for w in ws)), None) for k, ws in COLS}
            if kind != '事件轨':
                idx.update({k: None for k in EVENT_ONLY})
            for r in table[1:]:
                cells = _cells(r)
                if all(set(c) <= set('-: ') for c in cells):
                    continue
                get = lambda k: cells[idx[k]] if idx[k] is not None and idx[k] < len(cells) else ''
                if get('loc') and get('loc') not in EMPTY:
                    rows.append({k: get(k) for k, _ in COLS})
        tot = re.search(r'总估时\s*[≈约]?\s*(\d+(?:\.\d+)?)\s*s', sec)
        if tot:
            total, source = float(tot.group(1)), f'{kind}总估时'
        else:
            nums = [re.search(r'\d+(?:\.\d+)?', r['est']) for r in rows]
            if rows and all(nums):
                total, source = sum(float(n.group(0)) for n in nums), f'{kind}各段估时之和'
    if total is None:
        w = re.search(r'总窗口\s*[≈约]?\s*(\d+(?:\.\d+)?)\s*s', text)
        if w:
            total, source = float(w.group(1)), '节拍表总窗口（无场面轨）'
    return {'rows': rows, 'total': total, 'source': source, 'kind': kind}


def is_change(row):
    """事件轨的一行有没有变化：变化列非空且不以"无"开头（"无（余韵：…）"是余韵）。"""
    c = (row.get('change') or '').strip()
    return bool(c) and c not in EMPTY and not c.startswith('无')


def reference_list(track):
    """本场有哪些场地 / 场景（按出现顺序去重，括号里的子空间并到同一场地下）。
    地点以"同上 / 同前 / 连续 / 接上 / 紧接"开头的行沿用上一行的场地，括号里的子空间并到那个场地下。"""
    places, jumps, prev = {}, 0, None
    for k, r in enumerate(track['rows']):
        inherit = prev is not None and r['loc'].startswith(CONTINUOUS)
        base = prev if inherit else _base(r['loc'])
        prev = base
        sub = PARENS.findall(r['loc'])
        places.setdefault(base, [])
        for s in (x for grp in sub for x in re.split(r'[、，,]', grp.strip('（）()'))):
            s = s.strip()
            if s and s not in places[base]:
                places[base].append(s)
        t = r['time'].strip()
        if k and t and t not in EMPTY and not t.startswith(CONTINUOUS):
            jumps += 1
    return places, jumps


def read_design(text):
    """film-creative 4.0+ 正文前的"## 设计"：只取"静音测试"一格。没有这一节（旧稿）返回 None；
    有这一节但这一格没写、写"无"或还是模板占位（"__（靠哪个动作）"）时 silent_test 为 None。"""
    m = DESIGN_HEAD.search(text)
    if not m:
        return None
    sec = re.split(r'\n## ', text[m.end():], maxsplit=1)[0]
    cell = SILENT_CELL.search(sec)
    v = cell.group(1).strip() if cell else ''
    outside = PARENS.sub('', v).strip()
    if outside and (set(outside) <= set('_ ') or outside in EMPTY):
        v = ''
    return {'silent_test': v or None}


def clip_total(paths):
    out = []
    for p in paths:
        m = CLIP_LEN.search(Path(p).read_text(encoding='utf-8'))
        if not m:
            raise ValueError(f'{p}: 找不到"clip 时长 N s"')
        out.append((Path(p).name, float(m.group(1))))
    return out


def plan_diff(path):
    """方案里的"与场面轨 / 事件轨的差异"行内容；没有这一行返回 None。"""
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        m = DIFF_LINE.search(line)
        if m:
            return m.group(1).strip(' |*') or '（空）'
    return None


def parse_refs(cell):
    """"第 3–6 行（…）" / "第 1、2 行" / "7-9" → 行号列表；括号里的数字与叙述里的数字不算。"""
    s = PARENS.sub('', cell)
    groups = ROW_REFS.findall(s)
    if groups:
        src = ' '.join(groups)
    elif BARE_REFS.fullmatch(s.strip() or 'x'):
        src = s
    else:
        return []
    out = []
    for a, b in RANGE.findall(src):
        a, b = int(a), int(b or a)
        out.extend(range(a, b + 1) if b >= a else [a])
    return out


def plan_clips(text):
    """场级方案里首列为 clip 的表中带"交付变化"列的那张：[{clip, sec, cell}]。
    有 clip 表但都没有这一列返回 None；没有 clip 表返回 []。"""
    lines, found_clip_table = text.splitlines(), False
    for i, line in enumerate(lines):
        if not line.strip().startswith('|'):
            continue
        if i and lines[i - 1].strip().startswith('|'):
            continue  # 只看表头行
        header = _cells(line)
        if not header or 'clip' not in header[0].lower():
            continue
        found_clip_table = True
        col = next((k for k, h in enumerate(header) if DELIVER_COL in h), None)
        if col is None:
            continue
        sec_col = next((k for k, h in enumerate(header) if '时长' in h), None)
        out = []
        for r in lines[i + 1:]:
            if not r.strip().startswith('|'):
                break
            cells = _cells(r)
            if all(set(c) <= set('-: ') for c in cells):
                continue
            name = re.match(r'[\w.\-]+', cells[0])
            sec = re.search(r'\d+(?:\.\d+)?', cells[sec_col]) if sec_col is not None and sec_col < len(cells) else None
            out.append({'clip': name.group(0) if name else cells[0], 'sec': float(sec.group(0)) if sec else None,
                        'cell': cells[col] if col < len(cells) else ''})
        return out
    return None if found_clip_table else []


def check_delivery(track, clips):
    """每条 clip 交付事件轨至少一个变化行；同一变化行只交付一次；余韵不计入交付。返回 (交付表, 未交付行, 问题)。"""
    problems, table, owner = [], [], {}
    event = track['kind'] == '事件轨'
    by_n = {}
    for r in track['rows']:
        m = re.match(r'\d+', r['seg'] or '')
        if m:
            by_n[int(m.group(0))] = r
    for c in clips:
        refs = parse_refs(c['cell']) if event else []
        rows = []
        for n in refs:
            r = by_n.get(n)
            rows.append({'n': n, 'change': r['change'] if r else None, 'loss': r['loss'] if r else None,
                         'linger': bool(r) and not is_change(r), 'missing': r is None})
        table.append({**c, 'rows': rows})
        if not event:
            cell = c['cell'].strip()
            if cell in EMPTY or cell.startswith('无') or not ARROW.search(cell):
                problems.append(f"{c['clip']}：交付变化写的是\"{cell or '（空）'}\"——剧本没有事件轨时，写成\"谁：进 → 出\""
                                f"（删掉这条 clip 观众少知道什么）；写不出就是没有交付变化")
            continue
        for x in rows:
            if x['missing']:
                problems.append(f"{c['clip']}：交付变化写了第 {x['n']} 行，事件轨没有这一行")
        delivered = [x for x in rows if not x['missing'] and not x['linger']]
        if not delivered:
            lingers = [x['n'] for x in rows if x['linger']]
            why = (f"只列了余韵第 {'、'.join(map(str, lingers))} 行" if lingers
                   else f"交付变化写的是\"{c['cell'] or '（空）'}\"")
            problems.append(f"{c['clip']}：没有交付任何变化行（{why}）——余韵不单独成 clip：并进它前面那次变化所在的 clip 尾部，"
                            f"或删掉这条 clip、在差异行写\"第 N 行不拍\"并提醒用户。峰值事件、观众问题、无声段理由照常要写，但不能代替交付变化")
        for x in delivered:
            if x['n'] in owner and owner[x['n']] != c['clip']:
                problems.append(f"第 {x['n']} 行同时由 {owner[x['n']]} 和 {c['clip']} 交付：一次变化只交付一次"
                                f"（后一条在重演它，或行号写错）")
            owner.setdefault(x['n'], c['clip'])
    undelivered = [n for n, r in sorted(by_n.items()) if event and is_change(r) and n not in owner]
    return table, undelivered, problems


def run(script, clips=(), plan=None):
    text = Path(script).read_text(encoding='utf-8')
    track = read_track(text)
    places, jumps = reference_list(track)
    res = {'script': str(script), 'track_kind': track['kind'], 'segments': track['rows'], 'places': places, 'jumps': jumps,
           'script_total': track['total'], 'script_total_source': track['source'], 'design': read_design(text),
           'clips': [], 'production_total': None, 'ratio': None, 'reminder': None,
           'plan_diff': None, 'delivery': None, 'undelivered': [], 'delivery_reminder': None, 'problems': []}
    if clips:
        res['clips'] = clip_total(clips)
        res['production_total'] = sum(s for _, s in res['clips'])
        if track['total']:
            res['ratio'] = round(res['production_total'] / track['total'], 2)
            if res['ratio'] >= REMIND_RATIO:
                res['reminder'] = (f"分镜合计 {res['production_total']:g} s，比剧本估时 {track['total']:g} s 多 "
                                   f"{round((res['ratio'] - 1) * 100)}%（≥{round((REMIND_RATIO - 1) * 100)}%）："
                                   f"多出来的时间观众在看什么，是不是同一个画面拉长了。照常继续；回不回剧本层由用户定。")
    if plan:
        res['plan_diff'] = plan_diff(plan)
        if track['rows'] and res['plan_diff'] is None:
            res['problems'].append(f'剧本有{track["kind"]}，方案里没有"与{track["kind"]}的差异：…"一行（没改写"无"）')
        pc = plan_clips(Path(plan).read_text(encoding='utf-8'))
        if pc is None:
            res['problems'].append(f'方案的 clip 切分表缺"{DELIVER_COL}"列：每条 clip 写它交付事件轨哪几行（"第 3–6 行"）')
        elif not pc:
            if track['kind'] == '事件轨':
                res['problems'].append(f'方案里找不到 clip 切分表（首列 clip、带"{DELIVER_COL}"列）')
        else:
            res['delivery'], res['undelivered'], probs = check_delivery(track, pc)
            res['problems'].extend(probs)
            if res['undelivered']:
                by_n = {int(r['seg']): r for r in track['rows'] if r['seg'].isdigit()}
                rows = '；'.join(f"第 {n} 行 {by_n[n]['change']}" for n in res['undelivered'])
                res['delivery_reminder'] = (f"没有 clip 交付的变化行：{rows}。有意删掉就写进差异行，提醒用户；照常继续。")
    return res


def render(res):
    out = []
    name = Path(res['script']).name
    if res['segments']:
        places = '；'.join(p + (f"（{'、'.join(s)}）" if s else '') for p, s in res['places'].items())
        unit = '行' if res['track_kind'] == '事件轨' else '段'
        out.append(f"{name} {res['track_kind']}（参考，不锁定）：{len(res['segments'])} {unit}，场地 / 场景 {len(res['places'])} 处——{places}"
                   + (f"；时间跳 {res['jumps']} 次" if res['jumps'] else ''))
        for r in res['segments']:
            out.append(f"  {r['seg'] or '·'}. {r['loc']} · {r['act']}" + (f" · {r['time']}" if r['time'] not in EMPTY else '')
                       + (f" · 估 {r['est']} s" if r['est'] else ''))
    else:
        out.append(f'{name}：没有场面轨或事件轨（旧稿或非 film-creative 来源），按剧本正文与场景标题读场地。')
    if res['script_total'] is not None:
        out.append(f"剧本估时 {res['script_total']:g} s（{res['script_total_source']}）")
    if res['design'] and res['design']['silent_test']:
        out.append(f"设计卡·静音测试（告知，不锁定）：{res['design']['silent_test']}——关掉声音也看得懂谁要、谁赢的那个动作；"
                   f"S5 定视觉重点与峰值事件时的候选，用不用由分镜定")
    if res['production_total'] is not None:
        out.append(f"分镜合计 {res['production_total']:g} s = " + ' + '.join(f'{s:g}' for _, s in res['clips'])
                   + (f"；合计 / 剧本估时 = {res['ratio']}" if res['ratio'] is not None else '；剧本没有估时，无法对照'))
    if res['reminder']:
        out.append('提醒：' + res['reminder'])
    if res['plan_diff'] is not None:
        out.append(f"与{res['track_kind'] or '场面轨'}的差异：{res['plan_diff']}")
    if res['delivery']:
        out.append('交付变化（删掉这条 clip，观众少的就是这几行的"删掉损失"）：')
        for c in res['delivery']:
            head = f"  {c['clip']}" + (f" {c['sec']:g} s" if c['sec'] is not None else '')
            if not c['rows']:
                out.append(f"{head} ← {c['cell'] or '（空）'}")
            for k, x in enumerate(c['rows']):
                lead = head + ' ← ' if k == 0 else ' ' * len(head) + '   '
                if x['missing']:
                    out.append(f"{lead}第 {x['n']} 行（事件轨没有）")
                elif x['linger']:
                    out.append(f"{lead}第 {x['n']} 行 {x['change']}（余韵，不计入交付）")
                else:
                    out.append(f"{lead}第 {x['n']} 行 {x['change']}｜删掉损失：{x['loss'] or '（空）'}")
    if res['delivery_reminder']:
        out.append('提醒：' + res['delivery_reminder'])
    for p in res['problems']:
        out.append('问题：' + p)
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('script', help='剧本页（03_script/scene-XX.md）')
    ap.add_argument('--clips', nargs='*', default=[], help='本场分镜卡（读头部"clip 时长 N s"）')
    ap.add_argument('--plan', help='场级方案（核"与场面轨 / 事件轨的差异"一行与 clip 切分表的"交付变化"列）')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    try:
        res = run(args.script, args.clips, args.plan)
    except (OSError, ValueError) as e:
        print(f'无法解析：{e}', file=sys.stderr)
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2) if args.json else render(res))
    return 1 if res['problems'] else 0


if __name__ == '__main__':
    sys.exit(main())
