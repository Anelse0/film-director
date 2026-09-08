#!/usr/bin/env python3
"""Storyboard-ledger checks for a shared 分镜/台词 spreadsheet (.xlsx, stdlib only).

Usage: ledger_check.py LEDGER.xlsx [--sheet NAME] [--lines-sheet NAME]
                       [--long 7] [--long-dialogue 9] [--very-long 10] [--json]

The ledger is the table both skills write into when a project keeps its master
storyboard in a spreadsheet instead of 03_script/04_shots files. The sheet is
located by a header row containing 「镜号」 plus 「入点」/「出点」 (or 起/止);
the optional lines sheet by 「台词号」. Times may be Excel day fractions,
seconds, or HH:MM:SS / MM:SS strings.

Codes — L01/L02/L06 are deterministic ERRORs (exit 1); L03–L05, L08 are WARNs
for review; L07 is information. None of them judges story or acting quality.
  L01 出点 ≤ 入点
  L02 相邻镜头时间不连续（缝隙/重叠，按表内顺序）
  L03 单镜 ≥ --long 秒且只承载一句对白，或 ≥ --long-dialogue 秒含对白（与 validate_prompt W22
      同口径的“一句一切”约定 [推论]，审阅是否偷懒长镜；旁白/画外音不计；台词格里数不出引号时按一句处理）
  L04 单镜 ≥ --very-long 秒（任何内容）
  L05 连续 ≥3 镜「景别与运镜」原文相同（机位/景别/运镜一成不变）
  L06 台词窗口越出所属镜头或无效
  L07 占位/待定行统计（〔待定〕/待重写/未出/留空）
  L08 台词词数/窗口 > 3.0 词/s（英语口语可说上限的保守估计 [推论]；validate_prompt W05 另按 2.5 词/s 估时）
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlsx_lite import read_workbook  # noqa: E402

SHOT_HEADERS = {
    "id": ("镜号", "镜头号", "shot"),
    "start": ("入点", "起", "start", "开始"),
    "end": ("出点", "止", "end", "结束"),
    "camera": ("景别", "运镜", "camera"),
    "lines": ("台词", "dialogue", "line"),
    "picture": ("画面", "表演", "action"),
    "scene": ("场景", "scene"),
}
LINE_HEADERS = {
    "id": ("台词号", "line id"),
    "shot": ("镜号", "shot"),
    "start": ("入点", "start"),
    "end": ("出点", "end"),
    "text": ("英语原句", "原句", "台词", "line"),
    "words": ("词数", "words"),
}
PLACEHOLDER_RE = re.compile(r"〔待定〕|待定|待重写|未出|留空|TBD", re.I)
NO_LINE_RE = re.compile(r"^\s*(无台词|无|—|-|none|n/a)?\s*$", re.I)
VO_RE = re.compile(r"旁白|画外|V\.?O\.?|voice.?over|narrat", re.I)
QUOTE_RE = re.compile(r"[“\"][^”\"\n]{1,400}[”\"]")


def parse_time(value):
    """Return seconds (float) or None."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        return v * 86400 if 0 <= v < 1 else v
    text = str(value).strip()
    if text.startswith("="):
        return None
    m = re.fullmatch(r"(?:(\d+):)?(\d{1,2}):(\d{1,2}(?:\.\d+)?)", text)
    if m:
        h = int(m.group(1) or 0)
        return h * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*s?", text)
    if m:
        return float(m.group(1))
    return None


def fmt(seconds):
    if seconds is None:
        return "?"
    seconds = int(round(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def find_header(rows, must):
    for i, row in enumerate(rows[:15]):
        cells = [str(c) if c is not None else "" for c in row]
        if all(any(k in c for c in cells) for k in must):
            return i, cells
    return None, None


def map_columns(header_cells, spec):
    """Needle priority: the first needle that matches any header wins, so
    「英语原句」 beats 「台词」 and 「台词号」 never doubles as the text column."""
    mapping, taken = {}, set()
    for key, needles in spec.items():
        for needle in needles:
            hit = next((idx for idx, cell in enumerate(header_cells)
                        if idx not in taken and needle.lower() in cell.lower()
                        and not (needle == "台词" and "台词号" in cell)), None)
            if hit is not None:
                mapping[key] = hit
                taken.add(hit)
                break
    return mapping


def cell(row, idx):
    if idx is None or idx >= len(row):
        return None
    return row[idx]


def text_of(value):
    return "" if value is None else str(value).strip()


def pick_sheets(book, sheet, lines_sheet):
    shots = lines = None
    if sheet:
        shots = (sheet, book[sheet])
    if lines_sheet:
        lines = (lines_sheet, book[lines_sheet])
    for name, rows in book.items():
        if shots is None and find_header(rows, ("镜号", "入点" if any("入点" in text_of(c) for r in rows[:15] for c in r) else "起"))[0] is not None \
                and find_header(rows, ("台词号",))[0] is None:
            shots = (name, rows)
        elif lines is None and find_header(rows, ("台词号",))[0] is not None:
            lines = (name, rows)
    return shots, lines


def check(path, sheet=None, lines_sheet=None, long=7.0, very_long=10.0, long_dialogue=9.0):
    book = read_workbook(path)
    errors, warnings, infos = [], [], []
    shots_sheet, lines_sheet_data = pick_sheets(book, sheet, lines_sheet)
    if shots_sheet is None:
        return {"file": str(path), "errors": ["L00 未找到含「镜号」与「入点/出点」表头的分镜表"], "warnings": [], "info": [], "shots": []}
    name, rows = shots_sheet
    hdr_idx, header = find_header(rows, ("镜号",))
    cols = map_columns(header, SHOT_HEADERS)
    shots = []
    for r in range(hdr_idx + 1, len(rows)):
        row = rows[r]
        sid = text_of(cell(row, cols.get("id")))
        if not sid:
            continue
        start, end = parse_time(cell(row, cols.get("start"))), parse_time(cell(row, cols.get("end")))
        shots.append({
            "row": r + 1, "id": sid, "start": start, "end": end,
            "camera": text_of(cell(row, cols.get("camera"))),
            "lines": text_of(cell(row, cols.get("lines"))),
            "picture": text_of(cell(row, cols.get("picture"))),
            "scene": text_of(cell(row, cols.get("scene"))),
        })
    infos.append(f"分镜表「{name}」表头行 {hdr_idx + 1}，识别 {len(shots)} 镜")

    placeholders = []
    for s in shots:
        if s["start"] is None or s["end"] is None:
            errors.append(f"L01 镜{s['id']}（行{s['row']}）入点/出点无法解析")
            continue
        if s["end"] <= s["start"]:
            errors.append(f"L01 镜{s['id']}（行{s['row']}）出点 {fmt(s['end'])} ≤ 入点 {fmt(s['start'])}")
        dur = s["end"] - s["start"]
        s["duration"] = dur
        blob = " ".join((s["scene"], s["camera"], s["lines"], s["picture"]))
        if PLACEHOLDER_RE.search(blob):
            placeholders.append(s["id"])
            continue  # placeholder rows are reserved time, not designed shots
        has_lines = not NO_LINE_RE.match(s["lines"]) and not VO_RE.search(s["lines"])
        n_quotes = len(QUOTE_RE.findall(s["lines"]))
        if dur >= very_long:
            warnings.append(f"L04 镜{s['id']} 时长 {dur:.0f}s ≥ {very_long:g}s（{fmt(s['start'])}–{fmt(s['end'])}）")
        elif has_lines and dur >= long and (n_quotes <= 1 or dur >= long_dialogue):
            count = f" {n_quotes} 句台词" if n_quotes else "台词"
            warnings.append(f"L03 镜{s['id']} 时长 {dur:.0f}s 且含{count}（{fmt(s['start'])}–{fmt(s['end'])}）：对白场默认一句一切，审阅是否拆镜")
    for a, b in zip(shots, shots[1:]):
        if a.get("end") is None or b.get("start") is None:
            continue
        if abs(b["start"] - a["end"]) > 0.5:
            kind = "缝隙" if b["start"] > a["end"] else "重叠"
            errors.append(f"L02 镜{a['id']}→镜{b['id']} 时间{kind}：{fmt(a['end'])} → {fmt(b['start'])}")
    run, prev = 1, None
    for s in shots:
        cam = re.sub(r"\s+", "", s["camera"])
        if cam and cam == prev and s["id"] not in placeholders:
            run += 1
            if run == 3:
                warnings.append(f"L05 镜{s['id']} 起连续 3 镜「景别与运镜」相同：{s['camera'][:30]}")
        else:
            run = 1
        prev = cam
    if placeholders:
        infos.append(f"L07 占位/待定 {len(placeholders)} 镜：{placeholders[0]}–{placeholders[-1]}")
    timed = [s for s in shots if s.get("duration") is not None]
    if timed:
        infos.append(f"总时长 {fmt(timed[-1]['end'])}（{timed[-1]['end']:.0f}s），首镜 {fmt(timed[0]['start'])}")

    line_rows = []
    if lines_sheet_data is not None:
        lname, lrows = lines_sheet_data
        lh, lheader = find_header(lrows, ("台词号",))
        lcols = map_columns(lheader, LINE_HEADERS)
        by_id = {s["id"]: s for s in shots}
        for r in range(lh + 1, len(lrows)):
            row = lrows[r]
            lid = text_of(cell(row, lcols.get("id")))
            if not lid:
                continue
            shot_id = text_of(cell(row, lcols.get("shot")))
            start, end = parse_time(cell(row, lcols.get("start"))), parse_time(cell(row, lcols.get("end")))
            text = text_of(cell(row, lcols.get("text")))
            words_cell = cell(row, lcols.get("words"))
            words = int(words_cell) if isinstance(words_cell, (int, float)) else len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", text))
            line_rows.append({"id": lid, "shot": shot_id, "start": start, "end": end, "words": words})
            if start is None or end is None or end <= start:
                errors.append(f"L06 台词{lid}（行{r + 1}）窗口无效：{fmt(start)}–{fmt(end)}")
                continue
            shot = by_id.get(shot_id)
            if shot and shot.get("start") is not None and shot.get("end") is not None:
                if start < shot["start"] - 0.5 or end > shot["end"] + 0.5:
                    errors.append(f"L06 台词{lid} 窗口 {fmt(start)}–{fmt(end)} 越出镜{shot_id} {fmt(shot['start'])}–{fmt(shot['end'])}")
            elif shot_id and shot is None:
                errors.append(f"L06 台词{lid} 指向不存在的镜{shot_id}")
            if words and words / (end - start) > 3.0:
                warnings.append(f"L08 台词{lid} {words} 词 / {end - start:.0f}s（>3.0 词/s，英语偏快，核对窗口）")
        infos.append(f"台词表「{lname}」识别 {len(line_rows)} 句")
    return {"file": str(path), "sheet": name, "errors": errors, "warnings": warnings, "info": infos,
            "shots": [{k: v for k, v in s.items() if k in ("id", "start", "end", "duration")} for s in shots],
            "lines": line_rows, "placeholders": placeholders}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ledger")
    parser.add_argument("--sheet")
    parser.add_argument("--lines-sheet")
    parser.add_argument("--long", type=float, default=7.0, help="单句对白镜的长镜阈值（秒）")
    parser.add_argument("--long-dialogue", type=float, default=9.0, help="多句对白镜的长镜阈值（秒）")
    parser.add_argument("--very-long", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv[1:])
    try:
        result = check(args.ledger, args.sheet, args.lines_sheet, args.long, args.very_long, args.long_dialogue)
    except (OSError, KeyError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"== ledger_check: {result['file']}")
        for e in result["errors"]:
            print(f"ERROR {e}")
        for w in result["warnings"]:
            print(f"WARN  {w}")
        for i in result["info"]:
            print(f"INFO  {i}")
        print(f"== {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
