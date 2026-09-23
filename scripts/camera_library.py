#!/usr/bin/env python3
"""Read-only camera-movement library lookup (film-director 1.8.0).

The library (assets/camera-library.json, a byte-identical copy of the user's AI运镜提示词库) is execution
grammar: each entry says how the machine moves in five parts — Camera / Movement / Speed / Framing / End.
It does not say when or why to move; that stays with director-grammar §二 and hard rule 8. The Chinese
reading index (references/camera-index.json) adds function, when not to use, subject motion, carrier and
the official-term status for each entry. Default use is to fill the five parts with this shot's content
(填写); verbatim use (原文) only when the user asks for it. See references/camera-library.md.

  camera_library.py --list
  camera_library.py --id shot-19 shot-08
  camera_library.py --query 侧跟
  camera_library.py --slots shot-19      # five-part fill template for a shot card
  camera_library.py --raw shot-19        # verbatim library prompt (原文 only)
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ("camera", "movement", "speed", "framing", "end")
SLOT_HINT = {
    "camera": "运镜名（中文术语，进标注）",
    "movement": "方向与机位侧：按走位表写画左 / 画右、从哪里到哪里",
    "speed": "跟人物速度走，或写秒数",
    "framing": "谁在画面哪里、运动中什么保持不变",
    "end": "本镜终点构图（止于……），不用库里的通用句",
}


def load_library(path=None):
    data = json.loads(Path(path or ROOT / "assets/camera-library.json").read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("camera library needs a nonempty items list")
    result = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] in result:
            raise ValueError("each item needs a unique string id")
        comps = item.get("components")
        if not isinstance(comps, dict) or any(not isinstance(comps.get(k), str) or not comps[k].strip() for k in PARTS):
            raise ValueError(f"{item['id']}: components need camera/movement/speed/framing/end")
        if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
            raise ValueError(f"{item['id']}: prompt must be a nonempty string")
        result[item["id"]] = item
    return result


def load_index(path=None):
    rows = json.loads(Path(path or ROOT / "references/camera-index.json").read_text(encoding="utf-8"))
    return {r["id"]: r for r in rows}


def select(entries, index, ids=None, query=None):
    if ids:
        missing = [i for i in ids if i not in entries]
        if missing:
            raise ValueError(f"unknown camera ids: {missing}")
        return [entries[i] for i in ids]
    if query:
        needle = query.casefold()
        return [e for i, e in entries.items()
                if needle in json.dumps([e, index.get(i, {})], ensure_ascii=False).casefold()]
    return list(entries.values())


def norm(text):
    return re.sub(r"\s+", " ", text).strip().rstrip(".").casefold()


def library_phrases(entries=None, min_words=5):
    """Generic component sentences long enough to identify a verbatim copy: [(phrase, id, part)]."""
    entries = entries or load_library()
    out = []
    for i, e in entries.items():
        for part in PARTS[1:]:
            sentence = e["components"][part]
            if len(sentence.split()) >= min_words:
                out.append((norm(sentence), i, part))
    return out


def slots(entry, note):
    lines = [f"{entry['id']} {note.get('zh', '')}（{entry['name']}）",
             f"动机（A 层，库里没有）：__　职能参考：{note.get('function', '—')}（{note.get('grammar', '—')}）",
             f"什么时候不用：{note.get('avoid', '—')}　人物：{note.get('subject', '—')}　载体：{note.get('carrier', '—')}"]
    for part in PARTS:
        lines.append(f"{part.capitalize()} → {SLOT_HINT[part]}：__　（库：{entry['components'][part]}）")
    lines.append(f"写法：{note.get('official', '—')}；词表：{note.get('vocab', '—')}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--id", nargs="+")
    group.add_argument("--query")
    group.add_argument("--list", action="store_true")
    group.add_argument("--slots")
    group.add_argument("--raw")
    args = parser.parse_args()
    try:
        entries, index = load_library(), load_index()
        if args.raw:
            print(select(entries, index, [args.raw])[0]["prompt"])
        elif args.slots:
            e = select(entries, index, [args.slots])[0]
            print(slots(e, index.get(e["id"], {})))
        elif args.list or (args.id is None and args.query is None):
            print(json.dumps([{"id": e["id"], "name": e["name"], "zh": index.get(e["id"], {}).get("zh"),
                               "category_zh": e.get("category_zh")} for e in select(entries, index)],
                             ensure_ascii=False, indent=2))
        else:
            print(json.dumps([e | {"reading_notes": index.get(e["id"], {})}
                              for e in select(entries, index, args.id, args.query)], ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
