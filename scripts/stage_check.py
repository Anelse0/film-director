#!/usr/bin/env python3
"""S5 执行卡检查（1.11.0，S5 §5.11；模板 `templates/shot-card.md`）。

机位设计（1.8.0）执行住了，因为它是"必做段 + 模板里的固定表 + 脚本查有没有"。场 02 复盘里八条没执行的规则
（动作叠进台词、反应镜、拍人角度、站姿、纵览表、偏好冲突上报 …）共同点是：规则在参考文里是一句散文，分镜卡上没有一个必须填的
格子。执行卡把每阶段要回答的问题做成一张表，脚本只查"填没填、引的小节在不在、数字过不过线"，不判设计好坏。

读分镜卡（04_shots/*.md）：
  S01 (ERROR)  没有 `## 执行卡` 段，或表格缺 `#` / `项` / `证据` 列。
  S02 (ERROR)  执行卡缺行（模板 25 行按编号核）、证据格为空或占位（__ / 待定 / TODO）。
  S03 (ERROR)  证据格里引用的小节（`## X` / `### X` / §X）在卡里找不到。
  C11 (ERROR)  没有 `## 镜头纵览` 表，或表缺列（镜 / 时间 / 景别 / 台词 / 无台词 / 角度），或行数 ≠ `## 镜头 N` 的数量。
  W-C6 (WARN)  E 层缺 `最长无台词` 或 `反应镜` 行（S5 §5.2 第 6a / 8a 步）。
  W-C7 (WARN)  E 层 `最长无台词` 的秒数 > 3 s（默认；E 层 `最长无台词上限` 可覆盖）——保留要用户点头，QA 记原话。
  W-C8 (WARN)  镜头纵览"台词"列有「画外」而没有「整句」字样（可能是拆句；S5 §5.2 第 6 步）。
  S04 (ERROR)  1.12.0 某个 `## 镜头 N` 没有「表演翻译」行，或不是三段 `A 层词 → 词典行 / 情绪库条目 → 可见写法`（两个 →）；
               写 `表演翻译：无（原因）` 的插入镜跳过。
  S05 (ERROR)  1.12.0 表演翻译第二段没有引用外化词典的行（`references/externalization-lexicon.md` 第一列，含「（轻松）」变体）
               或情绪库条目（`情绪库 N` / 条目名）。
  W-C10 (WARN) 1.12.1 表演翻译第三段没写「声音：…」——情绪的声音翻译（口气 / 音量 / 停顿）就是括号里要放的内容。
  W-C9 (WARN)  1.12.0 C 层行（有序表演块 / 台词 / 结束状态 …）里出现 A 层词（词典「A 层词」一节 + 第一列）；只允许在 A 创作决策与表演翻译第一段。

退出码：0 = 做了（可有 WARN）；1 = 缺项（ERROR）；2 = 用法错误。
S5 停靠前：`python3 scripts/stage_check.py --stage s5 <分镜卡>`；S6 入口再跑一次。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layer_checks import LEXICON, load_vocabulary, scan_text  # noqa: E402

LIBRARY = Path(__file__).resolve().parents[1] / 'assets' / 'emotion-library.json'

CARD_ROWS = {
    1: '场景参数卡', 2: '视觉方案与观众问题', 3: '峰值事件与峰值镜', 4: '决策载体', 5: '走位表', 6: '空间锚点',
    7: '机位表', 8: '核对与复核', 9: '镜头纵览', 10: '每句台词的镜头', 11: '无台词段预算', 12: '反应镜清单',
    13: '变化轨', 14: '焦点与虚实', 15: '表演翻译', 16: '表演基线', 17: '拍人角度与摄影', 18: '穿着状态',
    19: '方向句', 20: '衔接', 21: '偏好与 skill 冲突', 22: '用户已点名', 23: '剧本回写待办', 24: '风险登记', 25: '脚本',
}
OVERVIEW_COLUMNS = ('镜', '时间', '景别', '台词', '无台词', '角度')
PLACEHOLDER = re.compile(r'^\s*(?:_+|—|-|待定|TODO|TBD|？|\?)?\s*$', re.I)
SECTION_REF = re.compile(r'(?:^|[\s（(；;，,])(?:##+\s*|§\s*)([^\s（）()；;，,。]+)')
DEFAULT_MAX_SILENT = 3.0


def section(text, title, level=2):
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
    return split(lines[0]), [split(l) for l in lines[2:]]


def headings(text):
    return {m.group(1).strip() for m in re.finditer(r'^#{2,3} ([^\n]+)', text, flags=re.M)}


def e_value(text, key):
    m = re.search(r'\|\s*' + re.escape(key) + r'\s*\|\s*([^|\n]+)\|', text)
    return m.group(1).strip() if m else None


def lexicon_rows(path=LEXICON):
    rows = set()
    try:
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            if line.startswith('|') and not line.startswith('|---') and '抽象词' not in line:
                cell = line.strip().strip('|').split('|')[0].strip()
                if cell:
                    rows.add(cell)
                    rows.add(re.sub(r'[（(].*$', '', cell).strip())
    except OSError:
        pass
    return rows


def library_names(path=LIBRARY):
    try:
        return {str(e.get('id')): e.get('name', '') for e in json.loads(Path(path).read_text(encoding='utf-8'))}
    except (OSError, ValueError):
        return {}


def translation_checks(text):
    """S04 / S05 / W-C9 over each `## 镜头 N` section of the card."""
    errors, warns = [], []
    rows = lexicon_rows()
    names = library_names()
    vocab = load_vocabulary()
    parts = re.split(r'^(?=## 镜头\s*\d+)', text, flags=re.M)
    for part in parts:
        m = re.match(r'## 镜头\s*(\d+)', part)
        if not m:
            continue
        no = m.group(1)
        body = re.split(r'^## (?!镜头)', part, maxsplit=1, flags=re.M)[0]
        line = re.search(r'^[^\n]*表演翻译[^\n]*$', body, flags=re.M)
        if not line:
            errors.append(f'S04 镜头{no} 没有「表演翻译」行（S5 §5.2 第 1 步：A 层词 → 词典行 → 可见写法）')
        else:
            content = re.sub(r'^.*?表演翻译[^：:]*[：:]\s*', '', line.group(0))
            if re.match(r'\s*无', content):
                pass
            else:
                segs = [x.strip() for x in re.split(r'→|->|=>', content) if x.strip()]
                if len(segs) < 3:
                    errors.append(f'S04 镜头{no} 表演翻译不是三段「A 层词 → 词典行 / 情绪库条目 → 可见写法」：{content[:50]}')
                else:
                    middle = segs[1]
                    ok = any(r and r in middle for r in rows) or re.search(r'情绪库\s*#?\d+', middle) \
                        or any(n and n.lower() in middle.lower() for n in names.values())
                    if not ok:
                        errors.append(f'S05 镜头{no} 表演翻译第二段「{middle[:40]}」不是外化词典的行或情绪库条目：从 externalization-lexicon.md 第一列挑一行（轻松场用「（轻松）」变体）')
                    third = '→'.join(segs[2:])
                    if not re.search(r'声音|口气|音量|语气|无声|不出声|不说话|无台词', third):
                        warns.append(f'W-C10 镜头{no} 表演翻译第三段没写声音那一半（情绪在声音里变成什么：口气 / 音量 / 停顿；没台词写「声音：无」）——括号里放的就是这一半，不写就会被删掉（S4 §4.4c 第 7 条）')
        c_lines = [l for l in body.splitlines() if re.match(r'\s*-\s*(?:有序表演块|表演(?!翻译)|台词|结束状态|起始状态|视线|主要事件|额外动作)', l)]
        found = scan_text('\n'.join(c_lines), vocab) if c_lines else []
        if found:
            warns.append(f'W-C9 镜头{no} C 层行出现 A 层词 {found}：只放在 A 创作决策和表演翻译第一段，C 层写部位 · 先后 · 声音')
    return errors, warns


def check(path, stage='s5'):
    text = Path(path).read_text(encoding='utf-8')
    errors, warns = [], []
    te, tw = translation_checks(text)
    errors.extend(te)
    warns.extend(tw)
    heads = headings(text)
    shots = re.findall(r'^## 镜头\s*(\d+)', text, flags=re.M)

    card = section(text, '执行卡')
    if card is None:
        errors.append('S01 缺少「## 执行卡」段（S5 §5.11 必做；模板 templates/shot-card.md）')
    else:
        header, rows = table_rows(card)
        if header is None or not all(any(c in h for h in header) for c in ('#', '项', '证据')):
            errors.append('S01 执行卡不是「# | 项 | 证据」表')
        else:
            seen = {}
            for r in rows:
                m = re.match(r'\d+', r[0]) if r else None
                if m and len(r) >= 3:
                    seen[int(m.group())] = r
            missing = [f'{n} {name}' for n, name in CARD_ROWS.items() if n not in seen]
            if missing:
                errors.append('S02 执行卡缺行：' + '、'.join(missing))
            for n, r in sorted(seen.items()):
                evidence = r[2]
                if PLACEHOLDER.match(evidence) or evidence.startswith('_'):
                    errors.append(f'S02 执行卡第 {n} 行（{CARD_ROWS.get(n, r[1])}）证据未填')
                    continue
                for ref in SECTION_REF.findall(evidence):
                    ref = ref.strip('`')
                    if ref and not any(ref in h for h in heads):
                        errors.append(f'S03 执行卡第 {n} 行引用「{ref}」，卡里没有这个小节')

    overview = section(text, '镜头纵览')
    if overview is None:
        errors.append('C11 缺少「## 镜头纵览」表（S5 停靠必交，导演偏好 §五 / S5 §5.6）')
    else:
        header, rows = table_rows(overview)
        if header is None:
            errors.append('C11 镜头纵览不是表格')
        else:
            missing = [c for c in OVERVIEW_COLUMNS if not any(c in h for h in header)]
            if missing:
                errors.append('C11 镜头纵览缺列：' + '、'.join(missing))
            data = [r for r in rows if r and re.match(r'\d+', r[0])]
            if shots and len(data) != len(shots):
                errors.append(f'C11 镜头纵览 {len(data)} 行，分镜卡有 {len(shots)} 个镜头')
            idx = next((i for i, h in enumerate(header) if '台词' in h), None)
            if idx is not None:
                for r in data:
                    cell = r[idx] if idx < len(r) else ''
                    if '画外' in cell and '整句' not in cell:
                        warns.append(f'W-C8 镜{r[0]} 纵览的台词列写了画外却没写「整句」：一句不跨镜，画外只用整句镜（S5 §5.2 第 6 步）')

    longest = e_value(text, '最长无台词')
    reactions = e_value(text, '反应镜')
    if longest is None or reactions is None:
        lack = [k for k, v in (('最长无台词', longest), ('反应镜', reactions)) if v is None]
        warns.append('W-C6 E 层缺 ' + '、'.join(f'`{k}`' for k in lack) + ' 行（S5 §5.2 第 6a / 8a 步）')
    if longest is not None:
        m = re.search(r'(\d+(?:\.\d+)?)\s*s', longest)
        cap = e_value(text, '最长无台词上限')
        try:
            cap = float(re.search(r'\d+(?:\.\d+)?', cap).group()) if cap else DEFAULT_MAX_SILENT
        except (AttributeError, ValueError):
            cap = DEFAULT_MAX_SILENT
        if m and float(m.group(1)) > cap + 1e-9:
            warns.append(f'W-C7 E 层最长无台词 {m.group(1)} s > {cap:g} s：叠进台词 / 合并同状态 / 反应镜 1 s / 收尾交下一条；保留要用户点头')
    return errors, warns


def main(argv):
    args = list(argv[1:])
    stage = 's5'
    if '--stage' in args:
        i = args.index('--stage')
        if i + 1 >= len(args) or args[i + 1] not in ('s5', 's6'):
            print('--stage 只接受 s5 或 s6', file=sys.stderr)
            return 2
        stage = args[i + 1]
        del args[i:i + 2]
    if not args:
        print('用法：stage_check.py [--stage s5|s6] <分镜卡.md> [更多分镜卡…]', file=sys.stderr)
        return 2
    worst = 0
    for path in args:
        errors, warns = check(path, stage)
        print(f'== stage_check ({stage}): {path}')
        for e in errors:
            print('ERROR', e)
        for w in warns:
            print('WARN ', w)
        print(f'== {len(errors)} error(s), {len(warns)} warning(s)')
        worst = max(worst, 1 if errors else 0)
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
