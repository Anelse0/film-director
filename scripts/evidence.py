#!/usr/bin/env python3
"""按编号读 validation-log.md 的证据行（1.13.0）。

规则文里的「证据 #n」指 `references/validation-log.md` 成片表的第 n 行。查一条不必读整张表（23 KB）：

  python3 scripts/evidence.py 8             一行
  python3 scripts/evidence.py 8 9 "#12"     多行（空格 / 逗号 / 顿号分隔都行）
  python3 scripts/evidence.py --grep 画左   关键词检索（任一格命中）
  python3 scripts/evidence.py --all         只列行号 · 日期 · 项目/clip/节拍

输出：每条先打 `#n · 日期 · 项目/clip/节拍`，再按表头逐格缩进打印，空格跳过。
退出码：0 找到；1 有编号没找到 / 检索无命中；2 用法错误。
"""
import re
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / 'references' / 'validation-log.md'


def tables(text):
    """Yield (header, rows) for each markdown table in the file."""
    header, rows = None, []
    for line in text.splitlines() + ['']:
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if header is None:
                header = cells
            elif cells and set(''.join(cells)) <= set('-: '):
                continue
            else:
                rows.append(cells)
        elif header is not None:
            yield header, rows
            header, rows = None, []


def load(path=LOG):
    text = Path(path).read_text(encoding='utf-8')
    for header, rows in tables(text):
        if header and header[0] in ('#', '编号') and any('观察' in h for h in header):
            out = {}
            for cells in rows:
                m = re.match(r'#?(\d+)$', cells[0]) if cells else None
                if m:
                    out[int(m.group(1))] = cells
            return header, out
    return None, {}


def fmt(header, cells):
    pad = lambda i: cells[i] if i < len(cells) else ''
    head = f"#{pad(0).lstrip('#')} · {pad(1)} · {pad(2)}"
    body = [f'  {header[i]}：{pad(i)}' for i in range(3, len(header)) if pad(i)]
    return '\n'.join([head] + body)


def parse_ids(args):
    ids = []
    for a in args:
        for part in re.split(r'[,，、\s]+', a):
            if not part:
                continue
            m = re.fullmatch(r'#?(\d+)', part)
            if not m:
                return None
            ids.append(int(m.group(1)))
    return ids


def main(argv):
    args = list(argv[1:])
    path = LOG
    if '--log' in args:
        i = args.index('--log')
        if i + 1 >= len(args):
            print('--log 后面要跟 validation-log.md 路径', file=sys.stderr)
            return 2
        path = Path(args[i + 1])
        del args[i:i + 2]
    header, rows = load(path)
    if header is None:
        print(f'{path} 里没有以「#」开头的成片表', file=sys.stderr)
        return 2
    if '--all' in args:
        for n in sorted(rows):
            c = rows[n]
            print(f"#{n} · {c[1] if len(c) > 1 else ''} · {c[2] if len(c) > 2 else ''}")
        return 0
    if '--grep' in args:
        i = args.index('--grep')
        if i + 1 >= len(args):
            print('--grep 后面要跟关键词', file=sys.stderr)
            return 2
        key = args[i + 1]
        hits = [n for n in sorted(rows) if any(key in c for c in rows[n])]
        for n in hits:
            print(fmt(header, rows[n]))
            print()
        if not hits:
            print(f'没有一行含「{key}」')
        return 0 if hits else 1
    ids = parse_ids(args)
    if not ids:
        print('用法：evidence.py <n> [<n>…] | --grep <关键词> | --all [--log <validation-log.md>]', file=sys.stderr)
        return 2
    missing = []
    for n in ids:
        if n in rows:
            print(fmt(header, rows[n]))
            print()
        else:
            missing.append(n)
    if missing:
        print('没有这些编号：' + '、'.join(f'#{n}' for n in missing) + f'（表里有 #{min(rows)}–#{max(rows)}）')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
