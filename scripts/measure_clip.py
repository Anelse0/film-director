#!/usr/bin/env python3
"""Measure the actual rhythm of a generated clip (needs ffmpeg/ffprobe on PATH).

Usage: measure_clip.py VIDEO... [--prompt PROMPT.md] [--scene 0.3] [--silence -30] [--json]

Reports per video: duration, detected cuts (scene-change score above --scene),
average shot length, shot-length buckets, speech occupancy (non-silent audio
above --silence dB for >= 0.3 s), leading / trailing silence and the longest
silent stretch. With --prompt it also lists what the Prompt declared (shots,
dialogue windows) next to what was generated, so the review can say which
side is slow: the design or the render, and prints the calibrated speech
rate (words / voiced seconds) to feed back into the E layer 语速词每秒. Scene detection is a heuristic: a
slow pan across a bright opening can count as a cut and a hard cut between two
similar frames can be missed; treat counts as ±1 and check by eye when it
matters. Speech occupancy counts any non-silent audio, including footsteps
and crowd, so it is an upper bound on speech.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.stdout.strip())


def cuts(path, threshold):
    out = run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo",
               "-an", "-f", "null", "-"])
    times = [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", out.stderr)]
    return [round(t, 2) for t in times if t > 0.2]


def silences(path, db, min_len=0.3):
    out = run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"silencedetect=n={db}dB:d={min_len}",
               "-vn", "-f", "null", "-"])
    starts = [float(m) for m in re.findall(r"silence_start:\s*([0-9.]+)", out.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([0-9.]+)", out.stderr)]
    pairs = list(zip(starts, ends))
    if len(starts) > len(ends):
        pairs.append((starts[-1], None))
    return pairs


def buckets(lengths):
    b = {"<2s": 0, "2-4s": 0, "4-5s": 0, ">5s": 0}
    for L in lengths:
        b["<2s" if L < 2 else "2-4s" if L <= 4 else "4-5s" if L <= 5 else ">5s"] += 1
    return b


def measure(path, scene, db):
    dur = duration(path)
    cut_times = cuts(path, scene)
    edges = [0.0] + cut_times + [dur]
    lengths = [round(b - a, 2) for a, b in zip(edges, edges[1:])]
    sil = [(s, e if e is not None else dur) for s, e in silences(path, db)]
    silent_total = sum(e - s for s, e in sil)
    lead = sil[0][1] if sil and sil[0][0] <= 0.05 else 0.0
    trail = dur - sil[-1][0] if sil and sil[-1][1] >= dur - 0.05 else 0.0
    longest = max(((e - s), s) for s, e in sil) if sil else (0.0, 0.0)
    return {
        "file": str(path), "duration": round(dur, 2), "cuts": cut_times, "shots": len(lengths),
        "asl": round(sum(lengths) / len(lengths), 2), "shot_lengths": lengths, "buckets": buckets(lengths),
        "audio_active": round(dur - silent_total, 2), "audio_active_share": round((dur - silent_total) / dur, 3),
        "lead_silence": round(lead, 2), "trail_silence": round(trail, 2),
        "longest_silence": {"length": round(longest[0], 2), "at": round(longest[1], 2)},
        "silences": [(round(s, 2), round(e, 2)) for s, e in sil],
    }


def declared(prompt_path):
    from prompt_structure import Document, dialogue_checks
    text = Path(prompt_path).read_text(encoding="utf-8")
    body = re.split(r"^\|\s*(?:项|参数项)\s*\|", text, maxsplit=1, flags=re.M)[0]
    doc = Document(body)
    shots = [(u.ident, u.start, u.end) for u in doc.shots]
    dur = shots[-1][2] if shots else None
    _, _, rows, total = dialogue_checks(doc, dur, (4.0, 2.5, 2 / 3))
    words = sum(len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", r["text"])) for r in rows)
    zh = sum(len(re.findall(r"[\u4e00-\u9fff]", r["text"])) for r in rows)
    return {"shots": len(shots), "duration": dur, "asl": round(dur / len(shots), 2) if shots else None,
            "shot_lengths": [e - s for _, s, e in shots],
            "dialogue_windows": [(r["start"], r["end"]) for r in rows if r["explicit"]],
            "words": words, "zh_chars": zh}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--prompt")
    ap.add_argument("--scene", type=float, default=0.3)
    ap.add_argument("--silence", type=float, default=-30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv[1:])
    results = [measure(Path(v), args.scene, args.silence) for v in args.videos]
    decl = declared(args.prompt) if args.prompt else None
    if args.json:
        print(json.dumps({"measured": results, "declared": decl}, ensure_ascii=False, indent=2))
        return 0
    for r in results:
        print(f"== {Path(r['file']).name}: {r['duration']}s, 检出切点 {len(r['cuts'])} → {r['shots']} 镜, 平均镜长 {r['asl']}s")
        print(f"   镜长 {r['shot_lengths']}  分布 {r['buckets']}")
        print(f"   切点 {r['cuts']}")
        print(f"   有声占比 {r['audio_active_share']:.0%}（{r['audio_active']}s）；开头静音 {r['lead_silence']}s，结尾静音 {r['trail_silence']}s，"
              f"最长静音 {r['longest_silence']['length']}s @ {r['longest_silence']['at']}s")
        print(f"   静音段 {r['silences']}")
    if decl:
        print(f"== Prompt 声明: {decl['shots']} 镜 / {decl['duration']}s, 平均镜长 {decl['asl']}s, 镜长 {decl['shot_lengths']}")
        print(f"   台词窗口 {decl['dialogue_windows']}")
        for r in results:
            if decl["words"] and r["audio_active"] > 0:
                rate = decl["words"] / r["audio_active"]
                win = sum(e - s for s, e in decl["dialogue_windows"])
                print(f"   校准：{decl['words']} 词 / 有声 {r['audio_active']}s ≈ {rate:.2f} 词/秒（有声含非台词声，是语速下限）；"
                      f"词数 / 窗口合计 {win:g}s = {decl['words'] / win if win else 0:.2f} 词/秒（Prompt 假设）→ 可回填 E 层「语速词每秒」")
            if decl["zh_chars"] and r["audio_active"] > 0:
                print(f"   校准：{decl['zh_chars']} 字 / 有声 {r['audio_active']}s ≈ {decl['zh_chars'] / r['audio_active']:.2f} 字/秒")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
