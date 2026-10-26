#!/usr/bin/env python3
"""QA current-state check (1.10.0, S7 §7.4; template `templates/qa.md`).

Trigger case [实测] (2026-10-19 review, proposal G3): the QA files only ever grew. The clip02 QA still
described the corridor before the mirror ("门在画右"), the clip01 QA's validator table listed a warning that no longer
fired and missed one that did, and the clip02 prompt stayed "v1" through six changes. The next session reads the stale
left / right first. This checker reads the `## 现行状态` section a QA file opens with and compares it with the files.

  Q01 (ERROR)  no `## 现行状态` section, it is not the first `##` section, or a required line is missing / a placeholder
               (Prompt / 成片 / 校验).
  Q02 (ERROR)  the Prompt version in 现行状态 differs from the first version in the prompt's E-layer 版本 row.
  Q03 (ERROR)  the WARN codes in the 校验 line differ from a fresh `validate_prompt.py` run on that prompt (ERROR count too).
  W-Q1 (WARN)  the prompt path in 现行状态 cannot be resolved; pass --prompt.
  Q04 (ERROR)  1.11.0 — 现行状态 names a category the user has already called out on this clip (`用户已点名：节奏（原话）、空间`)
               and the 校验处置 table keeps a WARN of that category with a written reason instead of 改了 / 用户同意保留.
               Trigger `[实测]` evidence #10: the user said 节奏太拖 at v1.3; v1.4 / v1.5 still kept W24 with a
               reason; the user asked at v1.6 whether anyone had reviewed it. Categories → codes: 节奏 W22–W29, 剪辑 W28 W54 W55,
               空间 W46 C09 C10 E23, 表演 W35 W49 W40, 台词 W47 W36 W44, 衣着 W45, 道具 W48, 衔接 W51, 视角 W52.

Exit codes: 0 = current (warnings allowed); 1 = drift (ERROR); 2 = usage error.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REQUIRED = ('Prompt', '成片', '校验')
CATEGORY_CODES = {
    '节奏': {'W22', 'W23', 'W24', 'W25', 'W26', 'W27', 'W28', 'W29'},
    '剪辑': {'W28', 'W54', 'W55'},
    '空间': {'W46', 'C09', 'C10', 'E23'},
    '表演': {'W35', 'W49', 'W40'},
    '台词': {'W47', 'W36', 'W44'},
    '衣着': {'W45'},
    '道具': {'W48'},
    '衔接': {'W51'},
    '视角': {'W52'},
}
KEPT_OK = re.compile(r'改了|已改|用户同意保留|用户原话|用户[：:]|用户点头|用户说')
PLACEHOLDER = re.compile(r'^\s*(?:<[^>]*>|_+|—|-|待定|TODO|TBD)?\s*$', re.I)
VERSION = re.compile(r'\bv\d+(?:\.\d+)*\b')
CODE = re.compile(r'\bW\d{2}\b')
PATH = re.compile(r'`([^`]+\.prompt\.md)`')


def current_section(text):
    heads = list(re.finditer(r'^## (.+)$', text, flags=re.M))
    if not heads:
        return None, False
    for i, m in enumerate(heads):
        if m.group(1).startswith('现行状态'):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return text[m.end():end], i == 0
    return None, False


def line(block, label):
    m = re.search(rf'^\s*-\s*{re.escape(label)}[^：:\n]*[：:][ \t]*([^\n]*)', block, flags=re.M)
    return m.group(1) if m else None


def resolve_prompt(qa_path, block, override):
    if override:
        return Path(override)
    m = PATH.search(line(block, 'Prompt') or '')
    if not m:
        return None
    for base in (qa_path.parent.parent, qa_path.parent, Path.cwd()):
        candidate = base / m.group(1)
        if candidate.exists():
            return candidate
    return None


def prompt_version(prompt_text):
    m = re.search(r'\|\s*版本\s*\|\s*([^|\n]+)\|', prompt_text)
    v = VERSION.search(m.group(1)) if m else None
    return v.group(0) if v else None


def check(qa_path, prompt=None):
    qa_path = Path(qa_path).resolve()
    text = qa_path.read_text(encoding='utf-8')
    errors, warns = [], []
    block, first = current_section(text)
    if block is None:
        return ['Q01 没有「## 现行状态」节（S7 §7.4，模板 templates/qa.md）'], warns
    if not first:
        errors.append('Q01 「## 现行状态」不是第一个 ## 节：现状要放在最前面，历史放后面')
    for label in REQUIRED:
        value = line(block, label)
        if value is None or PLACEHOLDER.match(value):
            errors.append(f'Q01 现行状态缺「{label}：」一行或没填')
    path = resolve_prompt(qa_path, block, prompt)
    if path is None:
        warns.append('W-Q1 现行状态里的 Prompt 路径找不到，用 --prompt 指定，Q02 / Q03 没核')
        return errors, warns
    prompt_text = path.read_text(encoding='utf-8')
    recorded = VERSION.search(line(block, 'Prompt') or '')
    actual = prompt_version(prompt_text)
    if recorded and actual and recorded.group(0) != actual:
        errors.append(f'Q02 现行状态写 Prompt {recorded.group(0)}，Prompt E 表版本是 {actual}：改稿后没重写现行状态，或版本号没升')
    check_line = line(block, '校验') or ''
    from validate_prompt import validate
    result = validate(path)
    fresh = sorted({w.split()[0] for w in result['warnings'] if CODE.match(w.split()[0])})
    noted_part = re.split(r'成片教训', check_line)[0]
    noted = sorted(set(CODE.findall(noted_part)))
    if fresh != noted:
        missing = [c for c in fresh if c not in noted]
        extra = [c for c in noted if c not in fresh]
        detail = '；'.join(x for x in (f"现在会报、没记：{'、'.join(missing)}" if missing else '',
                                      f"记了、现在不报：{'、'.join(extra)}" if extra else '') if x)
        errors.append(f'Q03 现行状态的校验结果过期（{detail}）：重跑 validate_prompt，替换「校验」一行')
    m = re.search(r'(\d+)\s*(?:个)?\s*ERROR', check_line, flags=re.I)
    if m and int(m.group(1)) != len(result['errors']):
        errors.append(f"Q03 现行状态写 {m.group(1)} 个 ERROR，现在是 {len(result['errors'])} 个")
    errors.extend(named_category_check(block, text))
    return errors, warns


def named_category_check(block, text):
    """Q04: categories the user already called out on this clip may not keep a matching WARN with a written reason."""
    named = line(block, '用户已点名')
    if not named or PLACEHOLDER.match(named) or named.strip().startswith('无'):
        return []
    codes = set()
    hit = []
    for cat, cs in CATEGORY_CODES.items():
        if cat in named:
            codes |= cs
            hit.append(cat)
    if not codes:
        return []
    errors = []
    table = re.search(r'###\s*7\s*校验处置(.*?)(?=^##|\Z)', text, flags=re.M | re.S)
    if not table:
        return errors
    for row in table.group(1).splitlines():
        cells = [c.strip() for c in row.strip().strip('|').split('|')] if row.strip().startswith('|') else []
        if len(cells) < 4:
            continue
        code = re.match(r'[WCE]\d{2}', cells[0])
        if not code or code.group(0) not in codes:
            continue
        verdict = cells[-1]
        if not KEPT_OK.search(verdict):
            errors.append(f"Q04 {code.group(0)} 属于用户已点名的类别（{'、'.join(hit)}），处置却是写理由保留：「{verdict[:40]}」——"
                          f"只能「改了」或「用户同意保留：原话」（S7 §7.1）")
    return errors


def main(argv):
    args = list(argv[1:])
    prompt = None
    if '--prompt' in args:
        i = args.index('--prompt')
        if i + 1 >= len(args):
            print('--prompt 后面要跟 Prompt 文件', file=sys.stderr)
            return 2
        prompt = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print('用法：qa_check.py [--prompt <prompt.md>] <qa.md>', file=sys.stderr)
        return 2
    errors, warns = check(args[0], prompt)
    print(f'== qa_check: {args[0]}')
    for e in errors:
        print('ERROR', e)
    for w in warns:
        print('WARN ', w)
    print(f'== {len(errors)} error(s), {len(warns)} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
