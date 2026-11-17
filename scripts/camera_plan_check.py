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
另给 WARN：机位表里用人物身体的左右（左肩 / 右肩 / 左手 / 右手 / 他的左边…）而没写画左 / 画右（W-C1）。

1.9.0 加一条"写得对不对"的检查（复盘提案 S1；1.8.0 的表在 D8 错误样例上 0 ERROR 通过）：
- 空间锚点给固定物件写绝对方位（`方位：门=北，西长墙=西，东窄墙=东北`，或 `| 物件 | 方位 |` 表），机位表"朝哪拍"写 朝北 / 朝东 …，
  "机位在哪"偏离中线时写 偏东 / 偏西 …。C09（ERROR）：画左 / 画右格里出现的锚点物件，按朝向换算不在那一侧
  （朝北：画左西、画右东；朝东：画左北、画右南；朝南：画左东、画右西；朝西：画左南、画右北）；正对镜头方向的物件
  只在写了"偏 X"时判（机位偏右，正前方的东西落在画左），正在镜头身后的物件填进画左 / 画右也报。
- W-C3：空间锚点没写方位，或某行"朝哪拍"没写绝对方位，C09 核不了；W-C4：机位表"动作做得出来吗"全是光秃秃的"能"、
  空间锚点也没有"可达"；W-C5：机位表用了随机位转向会换边的名字（走廊左墙 / 右侧的墙），改用锚点里的绝对名字。

1.10.0 加 `--prompt <prompt.md>`（只带一张分镜卡时）：C10（ERROR）——机位表第 N 行画左格里的物件，在 Prompt 镜头 N 里
出现在只写了画右的分句里（或反过来）。物件取空间锚点方位行里的名字，没写方位时取常见固定物件（门 / 名牌 / 窗 / 镜台 …）。
只报明确矛盾（同一分句只有一侧），不判遗漏。分镜卡和 Prompt 改了一边没改另一边（复盘 G3）就在这里拦。

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
BEARINGS = {'北': 0, '东北': 45, '东': 90, '东南': 135, '南': 180, '西南': 225, '西': 270, '西北': 315}
BEARING_WORD = r'东北|东南|西北|西南|北|南|东|西'
PAIR = re.compile(rf'([^\s=＝，、；：:|（）()]+?)\s*[=＝]\s*({BEARING_WORD})(?![\u4e00-\u9fff])')
FACING = re.compile(rf'朝(?:正)?({BEARING_WORD})')
OFFSET = re.compile(rf'偏({BEARING_WORD})')
RELATIVE_WALL = re.compile(r'(?:走廊|房间|屋子?|过道)(?:的)?[左右](?:墙|侧|边|长墙)|[左右](?:墙|长墙)|[左右]边(?:那|的)?面?墙')
BARE_YES = re.compile(r'^\s*(?:能|可以|做得到|可行|没问题)\s*[。.]?\s*$')
FRAME_LEFT, FRAME_RIGHT = '画左', '画右'
# C10
COMMON_OBJECTS = ('门框', '门', '名牌', '墙纸', '窗户', '窗', '镜台', '灯泡镜', '镜子', '吧台', '沙发', '扶手椅', '床', '桌子', '柜子', '壁灯')
PROMPT_SHOT = re.compile(r'^镜头\s*(\d+)（[^）]*）[：:](.*)$', re.M)
SAYS_LEFT = re.compile(r'画左|画面(?:中间)?偏左|画面(?:的)?左(?:侧|边|半)')
SAYS_RIGHT = re.compile(r'画右|画面(?:中间)?偏右|画面(?:的)?右(?:侧|边|半)')
CLAUSE = re.compile(r'[，。；;,\n]')


def prompt_shots(prompt_path):
    text = Path(prompt_path).read_text(encoding='utf-8')
    return {int(n): body for n, body in PROMPT_SHOT.findall(text)}


def cross_check(seen, idx, names, shots_text):
    """C10: an object the camera table puts on one side, named in a prompt clause that gives only the other side."""
    errors = []
    for n, r in sorted(seen.items()):
        body = shots_text.get(n)
        if body is None:
            continue
        clauses = [c for c in CLAUSE.split(re.sub(r'【[^】]*】', '', body)) if c.strip()]
        for col, want, other in (('画左', SAYS_LEFT, SAYS_RIGHT), ('画右', SAYS_RIGHT, SAYS_LEFT)):
            i = idx.get(col)
            cell = r[i] if i is not None and i < len(r) else ''
            for obj in objects_in(cell, names):
                for c in clauses:
                    hit = re.search(re.escape(obj), c)
                    if not hit or re.match(r'[左右](?:边|侧)', c[hit.end():hit.end() + 2]):
                        continue
                    if other.search(c) and not want.search(c):
                        errors.append(f'C10 镜{n} 机位表把「{obj}」填在{col}，Prompt 镜头{n}却写「{c.strip()[:30]}」：'
                                      '分镜卡和 Prompt 只改了一边，以机位设计为准对齐')
                        break
    return errors


def bearing_table(anchors):
    """{物件: 角度} from `方位：门=北，…` pairs or a `| 物件 | 方位 |` table inside the anchors."""
    found = {}
    for name, word in PAIR.findall(anchors):
        found[name.strip()] = BEARINGS[word]
    for line in anchors.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.strip().startswith('|') else []
        if len(cells) >= 2 and cells[1] in BEARINGS and cells[0] not in ('物件', '---'):
            found[cells[0]] = BEARINGS[cells[1]]
    return found


def objects_in(cell, table):
    """Anchor names in a cell, longest first; a name followed by 左边 / 右侧 is a reference point, not the thing placed."""
    hits, masked = [], cell
    for name in sorted(table, key=len, reverse=True):
        for m in re.finditer(re.escape(name), masked):
            if re.match(r'[左右](?:边|侧)', masked[m.end():m.end() + 2]):
                continue
            hits.append(name)
            masked = masked[:m.start()] + '＿' * len(name) + masked[m.end():]
            break
    return hits


def side_of(obj_angle, facing, offset):
    """'left' / 'right' / 'ahead' / 'behind' for an object seen from a camera facing `facing`, shifted toward `offset`."""
    r = (obj_angle - facing) % 360
    if r == 0:
        if offset is None:
            return 'ahead'
        ro = (offset - facing) % 360
        if 0 < ro < 180:
            return 'left'
        if 180 < ro < 360:
            return 'right'
        return 'ahead'
    if r == 180:
        return 'behind'
    return 'right' if r < 180 else 'left'


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


def check(path, stage='s6', prompt=None):
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
            table_bearings = bearing_table(anchors or '')
            if anchors and not table_bearings:
                warns.append('W-C3 空间锚点没给固定物件写绝对方位（方位：门=北，西长墙=西 …），机位表的画左 / 画右核不了（C09）')
            cell = lambda r, col: r[idx[col]] if idx.get(col) is not None and idx[col] < len(r) else ''
            bare = []
            for n, r in sorted(seen.items()):
                empty = [c for c, i in idx.items() if i is not None and (i >= len(r) or PLACEHOLDER.match(r[i]))]
                if empty:
                    errors.append(f'C06 镜{n} 机位表未填：' + '、'.join(empty))
                cells = ' '.join(r[1:])
                if BODY_SIDE.search(cells) and not re.search(r'画左|画右', cells):
                    warns.append(f'W-C1 镜{n} 用了人物身体的左右（{BODY_SIDE.search(cells).group()}），没写画左 / 画右')
                rel = RELATIVE_WALL.search(cell(r, '画左') + ' ' + cell(r, '画右'))
                if rel:
                    warns.append(f'W-C5 镜{n} 用了随机位转向会换边的名字「{rel.group()}」，改用空间锚点里的绝对名字')
                if BARE_YES.match(cell(r, '动作做得出来')):
                    bare.append(n)
                if not table_bearings:
                    continue
                facing = FACING.search(cell(r, '朝哪拍'))
                if not facing:
                    warns.append(f'W-C3 镜{n} 「朝哪拍」没写绝对方位（朝北 / 朝东 …），这一行的左右核不了')
                    continue
                f = BEARINGS[facing.group(1)]
                off = OFFSET.search(cell(r, '机位在哪'))
                o = BEARINGS[off.group(1)] if off else None
                for col, want in (('画左', 'left'), ('画右', 'right')):
                    for obj in objects_in(cell(r, col), table_bearings):
                        got = side_of(table_bearings[obj], f, o)
                        if got == 'ahead':
                            continue
                        if got != want:
                            where = {'left': '画左', 'right': '画右', 'behind': '镜头身后'}[got]
                            errors.append(f'C09 镜{n} 朝{facing.group(1)}拍时「{obj}」应在{where}，表里填在{col}'
                                          '（按朝向换算：朝北 画左西 / 画右东；朝东 画左北 / 画右南；朝南 画左东 / 画右西；朝西 画左南 / 画右北）')
            if prompt is not None:
                names = table_bearings or {o: 0 for o in COMMON_OBJECTS}
                errors.extend(cross_check(seen, idx, names, prompt_shots(prompt)))
            if seen and len(bare) == len(seen) and anchors and '可达' not in anchors:
                warns.append('W-C4 机位表「动作做得出来吗」全是"能"，空间锚点也没有「可达」：写每个站位用哪只手够得到什么、够不到什么')
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
    prompt = None
    if '--prompt' in args:
        i = args.index('--prompt')
        if i + 1 >= len(args):
            print('--prompt 后面要跟 Prompt 文件', file=sys.stderr)
            return 2
        prompt = args[i + 1]
        del args[i:i + 2]
    if not args:
        print('用法：camera_plan_check.py [--stage s5|s6] [--prompt <prompt.md>] <分镜卡.md> [更多分镜卡…]', file=sys.stderr)
        return 2
    if prompt is not None and len(args) != 1:
        print('--prompt 只能配一张分镜卡', file=sys.stderr)
        return 2
    worst = 0
    for path in args:
        errors, warns = check(path, stage, prompt)
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
