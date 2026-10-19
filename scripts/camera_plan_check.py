#!/usr/bin/env python3
"""机位设计必做检查（1.8.0，S5 §5.1g）。

读分镜卡（04_shots/*.md），只查"做没做"，不判设计好坏：
- 有 `## 机位设计` 段，段内有 `### 空间锚点`、`### 机位表`、`### 核对` 三个小节；
- 空间锚点写了参考图视角（"视角"）与门 / 窗 / 墙这类固定物件在画面里的左右（"画左" 或 "画右"）；
- 机位表的表头有必填列，分镜卡里每个 `## 镜头 N` 在表里都有一行，必填格不空、不是占位（__ / 待定 / TODO）；
- 核对小节五项都在，每项写了结论（冒号后不空、不是占位）；
- 空间锚点写了"上一条成片末帧"（没有写"无"）；不是"无"时要有 `### 复核` 小节，四行（上一条成片 / 末帧 / 对照 / 改动）都写了。
  复核在上一条成片回来后、编本条 Prompt 前做：S5 停靠时用 `--stage s5`，复核没做只给 WARN（W-C2）；
  编 Prompt 前（S6 入口）不带 --stage，复核没做是 ERROR（C08），不进 S6。
另给 WARN：机位表里用人物身体的左右（左肩 / 右肩 / 左手 / 右手 / 他的左边…）而没写画左 / 画右。

退出码：0 = 做了（可有 WARN）；1 = 缺项（ERROR）；2 = 用法错误。
"""
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = ('镜', '机位在哪', '朝哪拍', '画左', '画右', '人物在画面哪里', '动作做得出来', '参考图视角')
CHECK_ITEMS = ('左右', '换边', '动作可行', '参考图视角', '上一条成片')
RECHECK_FIELDS = ('上一条成片', '末帧', '对照', '改动')
PLACEHOLDER = re.compile(r'^\s*(?:_+|—|-|待定|TODO|TBD|？|\?)?\s*$', re.I)
BODY_SIDE = re.compile(r'(?:左|右)肩|(?:左|右)手|(?:他|她)的(?:左|右)边|(?:他|她)(?:左|右)侧')


def blank(value):
    return bool(PLACEHOLDER.match(value)) or value.strip().startswith('_')


def field(block, name):
    m = re.search(rf'^\s*(?:\d+\.\s*)?{re.escape(name)}[：:][ \t]*([^\n]*)', block, flags=re.M)
    return m.group(1) if m else None


def section(text, title, level):
    marks = '#' * level
    m = re.search(rf'^{marks} {re.escape(title)}[^\n]*\n', text, flags=re.M)
    if not m:
        return None
    rest = text[m.end():]
    stop = re.search(rf'^#{{1,{level}}} ', rest, flags=re.M)
    return rest[:stop.start()] if stop else rest


def table_rows(block):
    lines = [l.strip() for l in block.splitlines() if l.strip().startswith('|')]
    if len(lines) < 2:
        return None, []
    split = lambda l: [c.strip() for c in l.strip('|').split('|')]
    header = split(lines[0])
    rows = [split(l) for l in lines[2:]]
    return header, rows


def check(path, stage='s6'):
    text = Path(path).read_text(encoding='utf-8')
    errors, warns = [], []
    plan = section(text, '机位设计', 2)
    if plan is None:
        return ['C01 缺少「## 机位设计」段（S5 §5.1g 必做）'], warns
    anchors = section(plan, '空间锚点', 3)
    table = section(plan, '机位表', 3)
    review = section(plan, '核对', 3)
    for name, block in (('空间锚点', anchors), ('机位表', table), ('核对', review)):
        if block is None or not block.strip():
            errors.append(f'C02 「## 机位设计」缺少「### {name}」小节或内容为空')
    if anchors:
        if '视角' not in anchors:
            errors.append('C03 空间锚点没写参考图的视角（场景图是从哪往哪看）')
        if not re.search(r'画左|画右', anchors):
            errors.append('C03 空间锚点没写固定物件在画面里的画左 / 画右')
    shots = sorted({int(n) for n in re.findall(r'^## 镜头\s*(\d+)', text, flags=re.M)})
    if table:
        header, rows = table_rows(table)
        if header is None:
            errors.append('C04 机位表不是表格')
        else:
            missing = [c for c in REQUIRED_COLUMNS if not any(c in h for h in header)]
            if missing:
                errors.append('C04 机位表缺列：' + '、'.join(missing))
            idx = {c: next((i for i, h in enumerate(header) if c in h), None) for c in REQUIRED_COLUMNS}
            seen = {}
            for r in rows:
                m = re.search(r'\d+', r[0]) if r else None
                if m:
                    seen[int(m.group())] = r
            absent = [n for n in shots if n not in seen]
            if absent:
                errors.append('C05 机位表缺镜头：' + '、'.join(f'镜{n}' for n in absent))
            for n, r in sorted(seen.items()):
                empty = [c for c, i in idx.items() if i is not None and (i >= len(r) or PLACEHOLDER.match(r[i]))]
                if empty:
                    errors.append(f'C06 镜{n} 机位表未填：' + '、'.join(empty))
                cells = ' '.join(r[1:])
                if BODY_SIDE.search(cells) and not re.search(r'画左|画右', cells):
                    warns.append(f'W-C1 镜{n} 用了人物身体的左右（{BODY_SIDE.search(cells).group()}），没写画左 / 画右')
    if review:
        for item in CHECK_ITEMS:
            m = re.search(rf'{re.escape(item)}[^：:\n]*[：:][ \t]*([^\n]*)', review)
            if not m:
                errors.append(f'C07 核对缺一项：{item}')
            elif PLACEHOLDER.match(m.group(1)):
                errors.append(f'C07 核对「{item}」没写结论')
    if anchors:
        upstream = re.search(r'上一条成片末帧[：:][ \t]*([^\n]*)', anchors)
        if not upstream or blank(upstream.group(1)):
            errors.append('C03 空间锚点没写「上一条成片末帧」（没有上一条写"无"）')
        elif not upstream.group(1).strip().startswith('无'):
            recheck = section(plan, '复核', 3)
            todo = [f for f in RECHECK_FIELDS if recheck is None or field(recheck, f) is None or blank(field(recheck, f))]
            if todo:
                msg = '复核没做（上一条成片回来后、编本条 Prompt 前）：缺 ' + '、'.join(todo)
                if stage == 's5':
                    warns.append('W-C2 ' + msg)
                else:
                    errors.append('C08 ' + msg)
    return errors, warns


def main(argv):
    args = list(argv[1:])
    stage = 's6'
    if '--stage' in args:
        i = args.index('--stage')
        if i + 1 >= len(args) or args[i + 1] not in ('s5', 's6'):
            print('--stage 只接受 s5 或 s6', file=sys.stderr)
            return 2
        stage = args[i + 1]
        del args[i:i + 2]
    if not args:
        print('用法：camera_plan_check.py [--stage s5|s6] <分镜卡.md> [更多分镜卡…]', file=sys.stderr)
        return 2
    worst = 0
    for path in args:
        errors, warns = check(path, stage)
        print(f'== camera_plan_check: {path}')
        for e in errors:
            print('ERROR', e)
        for w in warns:
            print('WARN ', w)
        print(f'== {len(errors)} error(s), {len(warns)} warning(s)')
        worst = max(worst, 1 if errors else 0)
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
