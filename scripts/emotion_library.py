#!/usr/bin/env python3
"""Read-only emotion catalogue lookup. No fixed emotion-to-intensity presets.

The library (assets/emotion-library.json) holds the 25 verbatim English entries;
the reading index (references/emotion-index.json) adds per-entry composition
notes: zh (Chinese rendering, an adapt), hinge (identifying signal to keep when
compressing), readability (smallest shot size at which the hinge reads),
wider_parts, onset, min_seconds ([推论] estimate), ladder, listener, mask and
neighbors (adjacent entries with the body-part bridge). See
references/performance-grammar.md. Lookups return candidates only; none of the
index fields is a limit or a quality judgement.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_FIELDS = ("zh", "hinge", "readability", "wider_parts", "onset", "min_seconds",
                "ladder", "listener", "mask", "neighbors")


def load_library(path=None):
    entries = json.loads(Path(path or ROOT / "assets/emotion-library.json").read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("emotion library must be a nonempty list")
    result = {}
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("id")) is not int:
            raise ValueError("each entry needs an integer id")
        if entry["id"] in result:
            raise ValueError("duplicate entry id")
        if any(not isinstance(entry.get(key), str) or not entry[key].strip()
               for key in ("name", "family", "intensity", "direction", "prompt")):
            raise ValueError("entry text fields must be nonempty strings")
        result[entry["id"]] = entry
    return result


def load_index(path=None):
    rows = json.loads(Path(path or ROOT / "references/emotion-index.json").read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("emotion index must be a list")
    return {r["id"]: r for r in rows if isinstance(r, dict) and type(r.get("id")) is int}


def select(entries, index, ids=None, query=None):
    if ids is not None:
        missing = [i for i in ids if i not in entries]
        if missing:
            raise ValueError(f"unknown entry ids: {missing}")
        return [entries[i] for i in ids]
    if query:
        needle = query.casefold()
        # Search the entry plus its own index notes; neighbour bridges name other
        # emotions and would make every query match half the library.
        return [e for i, e in entries.items()
                if needle in json.dumps([e, {k: v for k, v in index.get(i, {}).items()
                                              if k not in ("neighbors", "ladder")}],
                                        ensure_ascii=False).casefold()]
    return list(entries.values())


def neighbors(entries, index, eid):
    """Adjacent entries and the bridge (which body part changes first)."""
    if eid not in entries:
        raise ValueError(f"unknown entry ids: [{eid}]")
    rows = []
    for link in index.get(eid, {}).get("neighbors", []):
        target = entries.get(link.get("id"))
        if target is None:
            raise ValueError(f"index neighbor {link.get('id')} of entry {eid} is not in the library")
        rows.append({"id": target["id"], "name": target["name"], "family": target["family"],
                     "intensity": target["intensity"], "bridge": link.get("bridge", ""),
                     "hinge": index.get(target["id"], {}).get("hinge", "")})
    return rows


def ladder(entries, index, family):
    """Entries of one family ordered subtle → medium → explosive, with the ladder note."""
    order = {"Subtle": 0, "Medium": 1, "Explosive": 2}
    needle = family.casefold()
    rows = [e for e in entries.values() if e["family"].casefold() == needle]
    if not rows:
        raise ValueError(f"unknown family: {family}")
    rows.sort(key=lambda e: (order.get(e["intensity"], 9), e["id"]))
    return [{"id": e["id"], "name": e["name"], "intensity": e["intensity"],
             "hinge": index.get(e["id"], {}).get("hinge", ""),
             "ladder": index.get(e["id"], {}).get("ladder", "")} for e in rows]


def by_readability(entries, index, shot_size):
    """Entries whose hinge reads at the given shot size (特写 < 近景 < 中近景 < 中景)."""
    scale = ["特写", "近景", "中近景", "中景"]
    if shot_size not in scale:
        raise ValueError(f"shot size must be one of {scale}")
    limit = scale.index(shot_size)
    rows = []
    for eid, e in entries.items():
        floor = index.get(eid, {}).get("readability")
        if floor in scale and scale.index(floor) <= limit:
            rows.append({"id": eid, "name": e["name"], "readability": floor,
                         "wider_parts": index.get(eid, {}).get("wider_parts", [])})
    return rows


def listeners(entries, index):
    return [{"id": eid, "name": e["name"], "intensity": e["intensity"],
             "hinge": index.get(eid, {}).get("hinge", "")}
            for eid, e in entries.items() if index.get(eid, {}).get("listener")]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--id", nargs="+", type=int)
    group.add_argument("--query")
    group.add_argument("--list", action="store_true")
    group.add_argument("--neighbors", type=int, metavar="ID", help="adjacent entries and body-part bridges")
    group.add_argument("--ladder", metavar="FAMILY", help="one family ordered by intensity")
    group.add_argument("--readability", metavar="SHOT", help="entries whose hinge reads at 特写/近景/中近景/中景")
    group.add_argument("--listener", action="store_true", help="entries suited to reaction shots")
    parser.add_argument("--raw", action="store_true", help="one complete English body only")
    parser.add_argument("--zh", action="store_true", help="with --id/--query: also print the Chinese rendering (adapt)")
    args = parser.parse_args()
    try:
        entries = load_library()
        index = load_index()
        if args.neighbors is not None:
            print(json.dumps(neighbors(entries, index, args.neighbors), ensure_ascii=False, indent=2))
            return
        if args.ladder:
            print(json.dumps(ladder(entries, index, args.ladder), ensure_ascii=False, indent=2))
            return
        if args.readability:
            print(json.dumps(by_readability(entries, index, args.readability), ensure_ascii=False, indent=2))
            return
        if args.listener:
            print(json.dumps(listeners(entries, index), ensure_ascii=False, indent=2))
            return
        selected = select(entries, index, args.id, args.query)
        if args.raw:
            if len(selected) != 1:
                parser.error("--raw requires exactly one matching entry")
            print(selected[0]["prompt"])
        elif args.list or (args.id is None and args.query is None):
            print(json.dumps([{k: e[k] for k in ("id", "name", "family", "intensity")}
                              | {"terms": index.get(e["id"], {}).get("terms", []),
                                 "readability": index.get(e["id"], {}).get("readability")}
                              for e in selected], ensure_ascii=False, indent=2))
        else:
            rows = []
            for e in selected:
                note = index.get(e["id"], {})
                row = e | {"reading_notes": {k: v for k, v in note.items() if k not in INDEX_FIELDS}}
                if args.zh:
                    row["zh"] = note.get("zh")
                row["composition"] = {k: note.get(k) for k in INDEX_FIELDS if k != "zh"}
                rows.append(row)
            print(json.dumps(rows, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
