#!/usr/bin/env python3
"""Measure the actual rhythm and visual variation of a generated clip (needs ffmpeg/ffprobe on PATH).

Usage: measure_clip.py VIDEO... [--prompt PROMPT.md] [--scene 0.3] [--silence -30]
                       [--frames DIR | --no-frames] [--json]

Reports per video: duration, detected cuts (scene-change score above --scene),
average shot length, shot-length buckets, speech occupancy (non-silent audio
above --silence dB for >= 0.3 s), leading / trailing silence and the longest
silent stretch. With --prompt it also lists what the Prompt declared (shots,
dialogue windows) next to what was generated, so the review can say which
side is slow: the design or the render, and prints the calibrated speech
rate (words / voiced seconds) to feed back into the E layer 语速词每秒.

1.4.0 visual variation profile: one frame per shot (at the shot's midpoint; shots
from the Prompt's declared cuts when --prompt is given, else the detected cuts)
saved as jpg plus a contact sheet, and per shot three cheap proxies computed
from a 96x54 grayscale frame with no extra dependency: mean luminance, edge
density (share of pixels with a strong local gradient — high in wide / busy
frames, low in close-ups on smooth skin and backdrop) and a subject-share proxy
(share of pixels closer in luminance to the frame centre than to its border —
a coarse stand-in for how much of the frame the face / subject fills). The
histogram distance between adjacent shots (0 = identical, 1 = disjoint) and the
deltas of the two proxies decide whether the render actually changed at each
cut ("变") or stayed flat ("平"); side by side with the Prompt's declared
variation track (【变化：…】 fields, or the size / camera inferred from the shot
tags) the report says whether a flat cut is flat in the design or in the
render. A fourth proxy, intra-shot motion (mean pixel change between a frame near
the shot's start and one near its end), says whether anything moved inside the
shot at all — camera or subject — so a run of "静" shots with declared fixed
cameras and low 幅度 is flat in the design, and a declared push that measures
"静" is flat in the render. The clip-level line sums it up: measured
shot-length contrast, the spread of edge density (a clip whose shots are all
the same size has a small spread), the spread of subject share, and how many
shots have any motion. Thresholds are heuristics (histogram distance < 0.12,
edge delta < 0.04, subject delta < 0.10 = flat cut; motion < 0.08 = still
shot); treat them as ±1 shot and check the sheet by eye.

Scene detection is a heuristic: a slow pan across a bright opening can count as
a cut and a hard cut between two similar frames can be missed; treat counts as
±1 and check by eye when it matters. Speech occupancy counts any non-silent
audio, including footsteps and crowd, so it is an upper bound on speech.
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

GRAY_W, GRAY_H = 96, 54
FLAT_HIST, FLAT_EDGE, FLAT_SUBJECT = 0.12, 0.04, 0.10
MOTION_STILL = 0.08          # intra-shot mean pixel change below this = essentially still (AI renders carry ~0.03-0.05 of breathing / noise)


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


# ---------- visual variation profile ----------

def gray_frame(path, t, w=GRAY_W, h=GRAY_H):
    """One grayscale frame at t seconds as a flat list of 0-255 ints (w*h), or None."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(path),
                          "-frames:v", "1", "-vf", f"scale={w}:{h}", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=False)
    data = out.stdout
    if len(data) < w * h:
        return None
    return list(data[:w * h])


def frame_stats(px, w=GRAY_W, h=GRAY_H):
    n = w * h
    mean = sum(px) / n
    hist = [0] * 16
    for v in px:
        hist[v >> 4] += 1
    hist = [c / n for c in hist]
    strong = 0
    for y in range(h - 1):
        row = y * w
        for x in range(w - 1):
            i = row + x
            if abs(px[i] - px[i + 1]) + abs(px[i] - px[i + w]) > 24:
                strong += 1
    edge = strong / ((w - 1) * (h - 1))
    cx0, cx1, cy0, cy1 = int(w * 0.4), int(w * 0.6), int(h * 0.4), int(h * 0.6)
    centre = [px[y * w + x] for y in range(cy0, cy1) for x in range(cx0, cx1)]
    bx, by = max(1, w // 10), max(1, h // 10)
    border = [px[y * w + x] for y in range(h) for x in range(w) if x < bx or x >= w - bx or y < by or y >= h - by]
    c = sum(centre) / len(centre)
    b = sum(border) / len(border)
    if abs(c - b) < 8:
        subject = None   # centre and border alike: the proxy cannot separate subject from background
    else:
        subject = sum(1 for v in px if abs(v - c) < abs(v - b)) / n
    return {"mean": round(mean / 255, 3), "hist": hist, "edge": round(edge, 3),
            "subject": None if subject is None else round(subject, 3)}


def hist_distance(h1, h2):
    return round(0.5 * sum(abs(a - b) for a, b in zip(h1, h2)), 3)


def motion(path, a, b):
    """Mean absolute pixel change between a frame near the start and one near the end of a shot
    (0 = nothing moved, camera or subject; a push-in / walk / turn scores well above MOTION_STILL)."""
    if b - a < 0.6:
        return None
    first, last = gray_frame(path, a + 0.25), gray_frame(path, b - 0.25)
    if first is None or last is None:
        return None
    return round(sum(abs(x - y) for x, y in zip(first, last)) / (len(first) * 255), 3)


def visual_profile(path, edges):
    """edges: shot boundaries [0, t1, ..., dur]. One frame per shot at its midpoint."""
    rows = []
    prev = None
    dur = edges[-1]
    for i, (a, b) in enumerate(zip(edges, edges[1:]), start=1):
        mid = min((a + b) / 2, max(dur - 0.15, 0))
        px = gray_frame(path, mid)
        row = {"no": i, "start": round(a, 2), "end": round(b, 2), "mid": round(mid, 2)}
        if px is None:
            row.update({"mean": None, "edge": None, "subject": None, "d_hist": None, "flat": None})
            rows.append(row)
            prev = None
            continue
        st = frame_stats(px)
        row.update({"mean": st["mean"], "edge": st["edge"], "subject": st["subject"], "motion": motion(path, a, b)})
        if prev is not None:
            row["d_hist"] = hist_distance(prev["hist"], st["hist"])
            row["d_edge"] = round(st["edge"] - prev["edge"], 3)
            row["d_subject"] = (None if st["subject"] is None or prev["subject"] is None
                                else round(st["subject"] - prev["subject"], 3))
            row["flat"] = (row["d_hist"] < FLAT_HIST and abs(row["d_edge"]) < FLAT_EDGE
                           and (row["d_subject"] is None or abs(row["d_subject"]) < FLAT_SUBJECT))
        else:
            row.update({"d_hist": None, "d_edge": None, "d_subject": None, "flat": None})
        rows.append(row)
        prev = st
    return rows


def contact_sheet(path, edges, out_dir):
    """Save one jpg per shot (midpoint frame) and a tiled contact sheet; returns (frame paths, sheet path)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(path).stem
    dur = edges[-1]
    frames = []
    has_drawtext = "drawtext" in run(["ffmpeg", "-hide_banner", "-filters"]).stdout
    for i, (a, b) in enumerate(zip(edges, edges[1:]), start=1):
        mid = min((a + b) / 2, max(dur - 0.15, 0))
        target = out_dir / f"{stem}-shot{i:02d}.jpg"
        vf = "scale=320:-2"
        if has_drawtext:
            label = f"{i}  {a:.1f}-{b:.1f}s".replace(":", r"\:")
            vf += f",drawtext=text='{label}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.5"
        proc = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", str(path),
                    "-frames:v", "1", "-vf", vf, "-q:v", "4", str(target)])
        if proc.returncode != 0 and has_drawtext:   # font not found etc.: retry without the label
            run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", str(path),
                 "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "4", str(target)])
        if target.exists():
            frames.append(target)
    sheet = None
    if frames:
        cols = len(frames) if len(frames) <= 6 else math.ceil(len(frames) / 2)
        rows = math.ceil(len(frames) / cols)
        listing = out_dir / f"{stem}-frames.txt"
        listing.write_text("".join(f"file '{f.resolve()}'\n" for f in frames), encoding="utf-8")
        sheet = out_dir / f"{stem}-sheet.jpg"
        proc = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-vf", f"scale=320:180,tile={cols}x{rows}", "-frames:v", "1", "-q:v", "4", str(sheet)])
        listing.unlink(missing_ok=True)
        if proc.returncode != 0 or not sheet.exists():
            sheet = None
    return frames, sheet


# ---------- declared side ----------

def declared(prompt_path):
    from prompt_structure import Document, dialogue_checks
    from validate_prompt import speech_parameters
    from variation_checks import profile as variation_profile, peak_shot
    text = Path(prompt_path).read_text(encoding="utf-8")
    body = re.split(r"^\|\s*(?:项|参数项)\s*\|", text, maxsplit=1, flags=re.M)[0]
    doc = Document(body)
    shots = [(u.ident, u.start, u.end) for u in doc.shots]
    dur = shots[-1][2] if shots else None
    rates = speech_parameters(text)
    _, _, rows, total = dialogue_checks(doc, dur, rates)
    words = sum(len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", r["text"])) for r in rows)
    zh = sum(len(re.findall(r"[一-鿿]", r["text"])) for r in rows)
    variation = variation_profile([(u.ident, u.start, u.end, u.body) for u in doc.shots], text)
    return {"shots": len(shots), "duration": dur, "asl": round(dur / len(shots), 2) if shots else None,
            "shot_lengths": [e - s for _, s, e in shots], "edges": [0.0] + [e for _, _, e in shots] if shots else None,
            "dialogue_windows": [(r["start"], r["end"]) for r in rows if r["explicit"]],
            "words": words, "zh_chars": zh, "rates": rates, "variation": variation, "peak": peak_shot(text)}


def declared_change(row):
    """(any declared change?, label) for a variation-profile row (None when nothing is trackable)."""
    tracked = {d: v for d, v in row["changes"].items() if v is not None}
    if not tracked:
        return None, "无可检维度"
    label = "".join(f"{d[:2]}{'✓' if v else '—'}" for d, v in tracked.items()) + ("" if row["declared"] else "(推断)")
    return any(tracked.values()), label


def compare(profile_rows, declared_rows):
    """Adjacent-cut verdicts: 变化已执行 / 平在渲染 / 平在设计 / 渲染多出变化."""
    verdicts = []
    for m in profile_rows[1:]:
        d = next((r for r in declared_rows if int(r["no"]) == m["no"]), None)
        if d is None or m.get("flat") is None:
            continue
        dchange, label = declared_change(d)
        measured = "平" if m["flat"] else "变"
        if dchange is None:
            verdict = "设计未声明可检维度"
        elif dchange and not m["flat"]:
            verdict = "变化已执行"
        elif dchange and m["flat"]:
            verdict = "平在渲染（设计声明了变化，成片没变）"
        elif not dchange and m["flat"]:
            verdict = "平在设计（设计就没变）"
        else:
            verdict = "渲染多出变化（核对是否漂移）"
        verdicts.append({"cut": f"{m['no'] - 1}→{m['no']}", "declared": label, "measured": measured, "verdict": verdict})
    return verdicts


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--prompt")
    ap.add_argument("--scene", type=float, default=0.3)
    ap.add_argument("--silence", type=float, default=-30)
    ap.add_argument("--frames", help="directory for per-shot frames and the contact sheet (default: <video>_frames/ beside the video)")
    ap.add_argument("--no-frames", action="store_true", help="skip frame extraction and the contact sheet")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv[1:])
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        ap.error("ffmpeg and ffprobe must be on PATH")
    results = [measure(Path(v), args.scene, args.silence) for v in args.videos]
    decl = declared(args.prompt) if args.prompt else None
    for r in results:
        edges = None
        if decl and decl["edges"]:
            edges = [min(t, r["duration"]) for t in decl["edges"]]
            if edges[-1] < r["duration"] - 0.5:
                edges[-1] = r["duration"]
            r["profile_source"] = "prompt"
        else:
            edges = [0.0] + r["cuts"] + [r["duration"]]
            r["profile_source"] = "detected"
        r["profile"] = visual_profile(Path(r["file"]), edges)
        r["frames"], r["sheet"] = [], None
        if not args.no_frames:
            out_dir = Path(args.frames) if args.frames else Path(r["file"]).with_name(Path(r["file"]).stem + "_frames")
            frames, sheet = contact_sheet(Path(r["file"]), edges, out_dir)
            r["frames"], r["sheet"] = [str(f) for f in frames], (str(sheet) if sheet else None)
        r["verdicts"] = compare(r["profile"], decl["variation"]) if decl else []
        flat_runs = []
        run_ = []
        for m in r["profile"][1:]:
            if m.get("flat"):
                run_.append(m["no"])
            else:
                if len(run_) >= 2:
                    flat_runs.append(run_)
                run_ = []
        if len(run_) >= 2:
            flat_runs.append(run_)
        r["flat_runs"] = flat_runs
    if args.json:
        for r in results:
            for m in r["profile"]:
                m.pop("hist", None)
        print(json.dumps({"measured": results, "declared": decl}, ensure_ascii=False, indent=2, default=str))
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
                      f"词数 / 窗口合计 {win:g}s = {decl['words'] / win if win else 0:.2f} 词/秒（Prompt 假设）→ 可回填 E 层「语速词每秒」（当前 E 层 / 默认 {decl['rates'][1]:g}）")
            if decl["zh_chars"] and r["audio_active"] > 0:
                print(f"   校准：{decl['zh_chars']} 字 / 有声 {r['audio_active']}s ≈ {decl['zh_chars'] / r['audio_active']:.2f} 字/秒")
    for r in results:
        src = "按 Prompt 声明切点" if r["profile_source"] == "prompt" else "按检出切点"
        print(f"== 视觉变化谱（{Path(r['file']).name}，{src}，一镜一帧 @ 镜中点；亮 = 平均亮度，边缘 = 强梯度像素占比，主体 ≈ 中心色调占比代理）")
        for m in r["profile"]:
            if m.get("mean") is None:
                print(f"   镜{m['no']} {m['start']:g}-{m['end']:g}s  抽帧失败")
                continue
            subj = "?" if m["subject"] is None else f"{m['subject']:.0%}"
            if m.get("d_hist") is None:
                delta = "—"
            else:
                ds = "?" if m.get("d_subject") is None else f"{m['d_subject']:+.0%}"
                delta = f"Δ直方图 {m['d_hist']:.2f} Δ边缘 {m['d_edge']:+.3f} Δ主体 {ds} → {'平' if m['flat'] else '变'}"
            mo = "?" if m.get("motion") is None else f"{m['motion']:.3f}{'静' if m['motion'] < MOTION_STILL else '动'}"
            print(f"   镜{m['no']} {m['start']:g}-{m['end']:g}s  亮 {m['mean']:.2f} 边缘 {m['edge']:.3f} 主体≈{subj} 镜内运动 {mo}  {delta}")
        ok = [m for m in r["profile"] if m.get("mean") is not None]
        if len(ok) >= 2:
            lens = [m["end"] - m["start"] for m in ok]
            edges_ = [m["edge"] for m in ok]
            subj_ = [m["subject"] for m in ok if m["subject"] is not None]
            moving = [m["no"] for m in ok if m.get("motion") is not None and m["motion"] >= MOTION_STILL]
            print(f"   clip 级：镜长对比 最长/最短 = {max(lens):.2f}/{min(lens):.2f} = {max(lens) / max(min(lens), 0.01):.1f}×"
                  f"{'（<2×：无镜长对比）' if max(lens) < 2 * min(lens) else ''}；边缘密度极差 {max(edges_) - min(edges_):.3f}"
                  f"{'（<0.08：景别一路相近）' if max(edges_) - min(edges_) < 0.08 else ''}；主体占比极差 {(max(subj_) - min(subj_)) if subj_ else 0:.0%}；"
                  f"有镜内运动的镜 {moving or '无'}（{len(moving)}/{len(ok)}）")
        if r["flat_runs"]:
            print(f"   成片连续平的切点：{['→'.join(str(x - 1) + '→' + str(x) for x in [run_[0]]) + ' … ' + str(run_[-1]) for run_ in r['flat_runs']]}（连续 ≥2 个切点视觉变化小）")
        if r["frames"]:
            print(f"   抽帧 {len(r['frames'])} 张：{Path(r['frames'][0]).parent}/{Path(r['frames'][0]).name} …")
        if r["sheet"]:
            print(f"   拼图：{r['sheet']}")
        if r["verdicts"]:
            print("== 变化轨对照（Prompt 声明 vs 成片）")
            for v in r["verdicts"]:
                print(f"   镜{v['cut']}  声明 {v['declared']}  / 成片 {v['measured']}  → {v['verdict']}")
            design_flat = [v["cut"] for v in r["verdicts"] if v["verdict"].startswith("平在设计")]
            render_flat = [v["cut"] for v in r["verdicts"] if v["verdict"].startswith("平在渲染")]
            print(f"   结论：平在设计 {design_flat or '无'}；平在渲染 {render_flat or '无'}"
                  f"{'；峰值镜 ' + str(decl['peak']) if decl and decl.get('peak') else '；峰值镜 未声明'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
