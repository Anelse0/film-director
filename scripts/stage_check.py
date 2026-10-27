#!/usr/bin/env python3
"""S5 分镜卡结构检查（1.11.0 起；1.15.0 改为直接查格子，S5 §5.11；模板 `templates/shot-card.md`）。

机位设计（1.8.0）执行住了，因为它是"必做段 + 模板里的固定表 + 脚本查有没有"。场 02 复盘里八条没执行的规则
（动作叠进台词、反应镜、拍人角度、站姿、纵览表、偏好冲突上报 …）共同点是：规则在参考文里是一句散文，分镜卡上没有一个必须填的
格子。1.11.0 把每阶段要回答的问题做成一张执行卡抄在卡末；1.15.0 起问题清单留在 S5 §5.11 对照表，卡上不再抄这张表，
脚本直接查格子本身——只查"有没有、填没填、数字过不过线"，不判设计好坏。

读分镜卡（04_shots/*.md）：
  S01 (ERROR)  1.15.0 缺必做段：`## 走位表`、`## clip 起始状态`、`## clip 结束状态`、`## 贯穿要求`（`## 机位设计` 归
               camera_plan_check，`## 镜头纵览` 归 C11）。
  S02 (ERROR)  1.15.0 卡头必填项缺，或还留着占位（__ / 待定 / TODO）：场景参数卡、视觉方案、观众问题、峰值事件、决策载体、
               方向句、交接三行「偏好与 skill 冲突」「剧本回写待办」「用户已点名」（可写"无"）。旧写法「方向」「偏好冲突」
               「剧本层的改动」只认行首。卡头 = 第一个 `## 走位表` / `## 机位设计` / `## 镜头纵览` / `## 镜头 N` /
               `## clip 起始状态` 之前，按标签找。
  S03 (ERROR)  1.15.0 `## 贯穿要求` 缺「保持一致」「空间与机位」「表演约束」任一桶（顶替执行卡第 16–18 行）；桶 = 以桶名开头的
               条目，「表演」「空间」「机位」「摄影」开头也认。
  旧卡         还有 `## 执行卡`、卡头的 film-director 版本低于 1.15（或没写）的卡：S01–S03 的发现不报错，由 `notes()` 给
               NOTE；执行卡第 21–23 行当作交接三行读。版本写到 1.15 以上就按新卡严查（照抄了旧表也一样）。
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

`notes(path)`（1.15.0）：旧卡的兼容 NOTE，加上卡头 / 表格里写了「不适用」的格子（停靠 B 回显单列）；不是校验码，不改退出码。

退出码：0 = 做了（可有 WARN / NOTE）；1 = 缺项（ERROR）；2 = 用法错误。
S5 停靠前：`python3 scripts/stage_check.py --stage s5 <分镜卡>`；S6 入口再跑一次。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layer_checks import LEXICON, load_vocabulary, scan_text  # noqa: E402

LIBRARY = Path(__file__).resolve().parents[1] / 'assets' / 'emotion-library.json'

REQUIRED_SECTIONS = ('走位表', 'clip 起始状态', 'clip 结束状态', '贯穿要求')
# 卡头必填项：第一个名字是模板写法，其余是旧写法（只认行首）；前六项写「无」也列进不适用清单
HEAD_ITEMS = (('场景参数卡',), ('视觉方案',), ('观众问题',), ('峰值事件',), ('决策载体',), ('方向句', '方向'),
              ('偏好与 skill 冲突', '偏好冲突'), ('剧本回写待办', '剧本层的改动'), ('用户已点名',))
LEGACY_HANDOFF = {21: '偏好与 skill 冲突', 22: '用户已点名', 23: '剧本回写待办'}  # 1.14.2 及以前执行卡里交接三行的行号
# 贯穿要求的桶：桶名 → (行首认的写法, 顶替执行卡哪一行的内容)
THROUGH_BUCKETS = {'保持一致': (('保持一致',), '穿着的分段状态'),
                   '空间与机位': (('空间与机位', '空间', '机位', '摄影'), '轴线、方向句、拍人角度一句'),
                   '表演约束': (('表演约束', '表演'), '站姿 / 基调句')}
E_ROWS = ('峰值镜', '最长无台词', '反应镜', '无声段理由', '已知风险')
HEAD_END = re.compile(r'^## (?:走位表|机位设计|镜头纵览|镜头\s*\d+|clip 起始状态)', re.M)
SKILL_VERSION = re.compile(r'film-director\s*v?(\d+)\.(\d+)')
OVERVIEW_COLUMNS = ('镜', '时间', '景别', '台词', '无台词', '角度')
PLACEHOLDER = re.compile(r'^\s*(?:_+|—|-|待定|TODO|TBD|？|\?)?\s*$', re.I)
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


def head_region(text):
    """The card head: everything before the first 走位表 / 机位设计 / 镜头纵览 / 镜头 N / clip 起始状态 section."""
    m = HEAD_END.search(text)
    return text[:m.start()] if m else text


def head_value(head, names):
    """Value after 「名字：」 in the head; the first name may sit inline after ' · ', older aliases only at line start."""
    for i, name in enumerate(names):
        lead = r'^[ \t]*(?:[-*][ \t]*)?' if i else r'(?:^|·)[ \t]*(?:[-*][ \t]*)?'
        m = re.search(lead + r'(?:\*\*)?' + re.escape(name)
                      + r'(?:\*\*)?[ \t]*(?:[（(][^）)\n]*[）)])?[ \t]*(?:\*\*)?[ \t]*[：:][ \t]*([^·\n]*)', head, flags=re.M)
        if m:
            return m.group(1)
    return None


def unfilled(value):
    """Empty, a bare placeholder, or anything still carrying a template blank 「__」 (「强度 __」「__（镜 __）」)."""
    return bool(PLACEHOLDER.match(value)) or '__' in value or value.strip().startswith('_')


def is_legacy(text):
    """A card written before 1.15.0: it still has `## 执行卡`, and its head names no film-director version ≥ 1.15.
    A new card that copied an old table is not legacy — its version line says 1.15+, so the checks stay strict."""
    if section(text, '执行卡') is None:
        return False
    m = SKILL_VERSION.search(head_region(text))
    return m is None or (int(m.group(1)), int(m.group(2))) < (1, 15)


def bucket_present(block, names):
    """A 贯穿要求 bucket is a bullet that starts with one of its names: 「- 表演约束：」「- **表演**：」."""
    alternatives = '|'.join(re.escape(n) for n in names)
    return re.search(rf'^[ \t]*[-*][ \t]*(?:\*\*)?[ \t]*(?:{alternatives})', block, flags=re.M) is not None


def legacy_handoff(text):
    """Rows 21–23 of a pre-1.15.0 `## 执行卡` table, filled ones only, keyed by their head-item names."""
    card = section(text, '执行卡')
    if card is None:
        return {}
    _, rows = table_rows(card)
    found = {}
    for r in rows:
        m = re.match(r'\d+', r[0]) if r else None
        if m and int(m.group()) in LEGACY_HANDOFF and len(r) >= 3 and not unfilled(r[2]):
            found[LEGACY_HANDOFF[int(m.group())]] = r[2]
    return found


def structure_checks(text):
    """S01–S03 over the card's own slots (1.15.0). Returns (findings, legacy) — legacy cards still carry `## 执行卡`."""
    findings = []
    heads = headings(text)
    for name in REQUIRED_SECTIONS:
        if not any(h.startswith(name) for h in heads):
            findings.append(f'S01 缺必做段「## {name}」（模板 templates/shot-card.md；S5 §5.11 对照表）')
    legacy = is_legacy(text)
    carried = legacy_handoff(text) if legacy else {}
    head = head_region(text)
    for names in HEAD_ITEMS:
        if names[0] in carried:
            continue
        value = head_value(head, names)
        if value is None:
            findings.append(f'S02 卡头缺「{names[0]}」（模板卡头；S5 §5.11 对照表）')
        elif unfilled(value):
            findings.append(f'S02 卡头「{names[0]}」只有占位：{value.strip()[:30]}')
    through = section(text, '贯穿要求')
    if through is not None:
        for bucket, (names, why) in THROUGH_BUCKETS.items():
            if not bucket_present(through, names):
                findings.append(f'S03 「## 贯穿要求」缺「{bucket}」一桶（{why}；S5 §5.11 对照表）')
    return findings, legacy


def not_applicable(text):
    """Head items written as 「不适用…」（前六项写「无」也算）and E rows written as 无 / 不适用, for the dock-B echo."""
    head = head_region(text)
    items = []
    for i, names in enumerate(HEAD_ITEMS):
        value = (head_value(head, names) or '').strip()
        if value.startswith('不适用') or (i < 6 and value.startswith('无')):
            items.append(f'{names[0]}（{value[:40]}）')
    layer = section(text, 'E 层') or section(text, 'E层') or text
    for key in E_ROWS:
        value = (e_value(layer, key) or '').strip()
        if value.startswith(('不适用', '无')):
            items.append(f'{key}（{value[:40]}）')
    return items


def notes(path):
    """NOTE lines (1.15.0, not codes): the legacy-card notice with its downgraded S01–S03, and the 不适用 list."""
    text = Path(path).read_text(encoding='utf-8')
    out = []
    findings, legacy = structure_checks(text)
    if legacy:
        out.append('旧卡还有「## 执行卡」：1.15.0 起不再抄这张表——下次改这条时把第 21 / 23 行挪进卡头交接三行、'
                   '「用户已点名」写一行指针到 QA，再删掉执行卡（S5 §5.11）')
        out += [f'旧卡（不报错）{f}' for f in findings]
    elif section(text, '执行卡') is not None:
        out.append('卡里还抄着「## 执行卡」：1.15.0 起答案写在各自的格子里，删掉这张表（S5 §5.11）')
    na = not_applicable(text)
    if na:
        out.append('写了「不适用」的格子（停靠 B 回显单列）：' + '；'.join(na))
    return out


def check(path, stage='s5'):
    text = Path(path).read_text(encoding='utf-8')
    errors, warns = [], []
    te, tw = translation_checks(text)
    errors.extend(te)
    warns.extend(tw)
    shots = re.findall(r'^## 镜头\s*(\d+)', text, flags=re.M)

    findings, legacy = structure_checks(text)
    if not legacy:
        errors.extend(findings)

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
        for n in notes(path):
            print('NOTE ', n)
        print(f'== {len(errors)} error(s), {len(warns)} warning(s)')
        worst = max(worst, 1 if errors else 0)
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
