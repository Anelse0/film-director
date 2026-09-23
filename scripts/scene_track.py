#!/usr/bin/env python3
"""场面轨 / 事件轨：剧本的场地 / 场景清单作参考，分镜的场级合计与之对照（film-director 1.5.1）。

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
  两种轨表都没有的旧稿回退到节拍表"总窗口 ≈ N s"）。
- 场级合计：各分镜卡头部"clip 时长 N s"之和。合计 / 剧本估时 ≥ 1.2 → **提醒**（多出来的时间观众在看什么、
  是不是同一个画面拉长了），照常继续，不退回；回不回剧本层由用户定。1.2 按 THE ORDER 已出分镜的 5 场定：
  只有 EP03 场 4 的两版超出（1.28 / 1.30），其余 1.02–1.13（`[推论]`，见 references/duration-rhythm.md §十一）。
- 差异行：剧本有场面轨或事件轨、又给了 --plan 时，方案里必须有"与场面轨的差异"（或"与事件轨的差异"）一行。

不改任何文件；零外部依赖。退出码：0 = 通过或只有提醒，1 = 方案缺差异行，2 = 输入无法解析。
"""
import argparse
import json
import re
import sys
from pathlib import Path

REMIND_RATIO = 1.2  # [推论]
TRACK_HEAD = re.compile(r'^##\s*(场面轨|事件轨)[^\n]*$', re.M)  # 3.6 场面轨 / 3.7+ 事件轨
COLS = (('seg', ('段', '#')), ('loc', ('地点',)), ('act', ('活动',)), ('time', ('时间',)), ('who', ('谁',)),
        ('new', ('新看见',)), ('anchor', ('锚句',)), ('est', ('估时',)))
EMPTY = {'', '—', '-', '无', '空', '__'}
CONTINUOUS = ('连续', '接上', '同上', '紧接')
PARENS = re.compile(r'[（(][^)）]*[)）]')
CLIP_LEN = re.compile(r'clip\s*时长\s*(\d+(?:\.\d+)?)\s*s')
DIFF_LINE = re.compile(r'与(?:场面轨|事件轨)的差异\s*[:：]?\s*(.*)')


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


def reference_list(track):
    """本场有哪些场地 / 场景（按出现顺序去重，括号里的子空间并到同一场地下）。"""
    places, jumps = {}, 0
    for k, r in enumerate(track['rows']):
        base = _base(r['loc'])
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


def run(script, clips=(), plan=None):
    track = read_track(Path(script).read_text(encoding='utf-8'))
    places, jumps = reference_list(track)
    res = {'script': str(script), 'track_kind': track['kind'], 'segments': track['rows'], 'places': places, 'jumps': jumps,
           'script_total': track['total'], 'script_total_source': track['source'],
           'clips': [], 'production_total': None, 'ratio': None, 'reminder': None,
           'plan_diff': None, 'problems': []}
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
    if res['production_total'] is not None:
        out.append(f"分镜合计 {res['production_total']:g} s = " + ' + '.join(f'{s:g}' for _, s in res['clips'])
                   + (f"；合计 / 剧本估时 = {res['ratio']}" if res['ratio'] is not None else '；剧本没有估时，无法对照'))
    if res['reminder']:
        out.append('提醒：' + res['reminder'])
    if res['plan_diff'] is not None:
        out.append(f"与{res['track_kind'] or '场面轨'}的差异：{res['plan_diff']}")
    for p in res['problems']:
        out.append('问题：' + p)
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('script', help='剧本页（03_script/scene-XX.md）')
    ap.add_argument('--clips', nargs='*', default=[], help='本场分镜卡（读头部"clip 时长 N s"）')
    ap.add_argument('--plan', help='场级方案（核"与场面轨 / 事件轨的差异"一行）')
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
