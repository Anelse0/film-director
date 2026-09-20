"""Variation track: what changes between one shot and the next (stdlib only).

The two time tracks (picture track = where the cuts fall, dialogue track = when
lines are spoken) say nothing about whether the picture after a cut differs from
the picture before it. This module reads the third design track that S5 declares
per shot — 【变化：景别 全→近｜机位 固定→推｜光 正→侧｜幅度 1→3】 — plus the
E-layer 峰值镜 (peak shot), and reviews four lower bounds (W30-W33):

  W30  three consecutive shots with zero change on every declared dimension;
       fewer than two dimensions change anywhere in the clip; a G6 (romance)
       repeated composition without a declared new element (新增).
  W31  no shot-length contrast: longest < 2 x shortest with >= 4 shots.
  W32  variation track not declared: no 峰值镜 row, or shots without the field.
  W33  the peak shot sits in the least visible size (wide / extreme wide) or an
       over-the-shoulder, or is a fixed shot while the clip's motivated camera
       move went to another shot.

When a shot has no 【变化】 field the size and camera dimensions are inferred from
its 【景别，角度，运镜】 tag and marked 推断 (inferred); light and amplitude cannot
be inferred. Every result is a review hint, never a quota (references/duration-rhythm.md §二,
references/stage-5-directing-storyboard.md §5.1f).

Field grammar (stable, regex-parsed; keep it on the same line as the shot tag,
never at the start of a line):
  【变化：<dim> <from>→<to>｜<dim> <value>｜…】   or   [CHANGE: size W→CU | camera static→push | …]
  dims: 景别/size · 机位/运镜/camera · 光/light · 幅度/amp (integer 0-3) · 新增/new (free text)
  "<value>" without an arrow, "=", "同" or "不变" means unchanged; the first shot is the baseline.
"""
import re

DIM_ALIASES = {
    "景别": "景别", "size": "景别", "shot": "景别",
    "机位": "机位", "运镜": "机位", "机位或运镜": "机位", "camera": "机位", "move": "机位",
    "光": "光", "光线": "光", "light": "光",
    "幅度": "幅度", "动作幅度": "幅度", "amp": "幅度", "amplitude": "幅度", "action": "幅度",
    "新增": "新增", "new": "新增", "added": "新增",
}
DIMS = ("景别", "机位", "光", "幅度")
DIM_LABELS = {"景别": "景别", "机位": "机位或运镜", "光": "光", "幅度": "动作幅度"}

FIELD_RE = re.compile(r"【\s*变化\s*[：:]\s*([^】]+)】|\[\s*CHANGE\s*[：:]\s*([^\]]+)\]", re.I)
ARROW_RE = re.compile(r"\s*(?:→|->|=>|＞|>)\s*")
UNCHANGED = {"", "=", "同", "不变", "same", "-", "—", "－"}

# Longest key first; rank = visibility of the face / part (0 least, 6 most).
SIZE_RANK = [
    ("大远景", 0), ("大远", 0), ("远景", 0), ("远", 0), ("大全景", 1), ("大全", 1), ("全景", 1), ("全", 1),
    ("中近景", 3), ("中近", 3), ("中景", 2), ("中", 2), ("近景", 4), ("近", 4),
    ("大特写", 6), ("大特", 6), ("特写", 5), ("特", 5), ("插入", 5), ("微距", 6),
    ("extreme wide", 0), ("ews", 0), ("extreme long", 0), ("wide", 1), ("full", 1), ("long shot", 1), ("ws", 1),
    ("medium close", 3), ("mcu", 3), ("medium", 2), ("ms", 2),
    ("extreme close", 6), ("ecu", 6), ("close", 4), ("cu", 4), ("insert", 5), ("macro", 6),
]
SIZE_NAMES = {0: "远景", 1: "全景", 2: "中景", 3: "中近景", 4: "近景", 5: "特写", 6: "大特写"}
LEAST_VISIBLE = 1

CAMERA_MOVES = [
    "推", "拉", "摇", "横移", "跟拍", "跟随", "跟进", "跟下", "跟", "环绕", "升", "降", "俯冲", "后拉", "手持", "甩", "随",
    "push", "pull", "pan", "tilt", "truck", "track", "orbit", "crane", "dolly", "handheld", "zoom", "whip", "arc",
]
FIXED_WORDS = ["固定", "locked", "static", "fixed"]
OTS_RE = re.compile(r"越[^，,。；;】｜|\n]{0,10}肩|over[- ]the[- ]shoulder|\bOTS\b", re.I)
PEAK_RE = re.compile(r"\|\s*峰值镜\s*\|\s*([^|\n]+)\|")
REPEAT_RE = re.compile(
    r"(?:构图)?与镜头\s*(\d+)\s*(?:同构图|相同|一致|同一构图)|同镜头?\s*(\d+)\s*(?:的)?构图|镜头\s*(\d+)\s*同构图"
    r"|same (?:framing|composition) as shot\s*(\d+)", re.I)
G6_RE = re.compile(r"\|\s*透镜\s*\|[^|\n]*\bL19\b|\|\s*(?:类型|类型包|基调|语域|类型叠加)\s*\|[^|\n]*(?:暧昧|爱情|G6)")


def size_rank(value):
    """Visibility rank of a size word (last size word wins: '全景缓推到中景' ends in 中景)."""
    if not value:
        return None
    low = value.lower()
    best = None
    for key, rank in SIZE_RANK:
        pos = low.rfind(key)
        if pos >= 0 and (best is None or pos > best[0] or (pos == best[0] and len(key) > best[2])):
            best = (pos, rank, len(key))
    return best[1] if best else None


def camera_of(text):
    if not text:
        return None
    low = text.lower()
    if any(w in low for w in FIXED_WORDS):
        return "固定"
    for w in CAMERA_MOVES:
        if w in low:
            return w
    return None


def tag_of(body):
    tag = re.search(r"【([^】]{2,60})】|\[([^\]]{2,80})\]", body[:80])
    return (tag.group(1) or tag.group(2)) if tag else ""


def parse_field(body):
    """Return {dim: (from, to, changed)} plus '新增' and 'raw', or None when the shot has no field."""
    m = FIELD_RE.search(body)
    if not m:
        return None
    raw = m.group(1) or m.group(2)
    parsed = {"raw": raw.strip(), "新增": None}
    for item in re.split(r"[｜|；;]", raw):
        item = item.strip()
        if not item:
            continue
        key_match = re.match(r"([A-Za-z一-鿿]+)\s*[：:]?\s*(.*)$", item)
        if not key_match:
            continue
        dim = DIM_ALIASES.get(key_match.group(1).strip().lower()) or DIM_ALIASES.get(key_match.group(1).strip())
        value = key_match.group(2).strip()
        if dim is None:
            continue
        if dim == "新增":
            parsed["新增"] = value or ""
            continue
        parts = ARROW_RE.split(value, maxsplit=1)
        if len(parts) == 2:
            src, dst = parts[0].strip(), parts[1].strip()
            if dst in UNCHANGED:
                changed = False
            elif dim == "景别" and size_rank(src) is not None and size_rank(dst) is not None:
                changed = size_rank(src) != size_rank(dst)      # 中→中（双人同框） is the same size
            elif dim == "幅度" and re.fullmatch(r"\d+", src) and re.fullmatch(r"\d+", dst):
                changed = int(src) != int(dst)
            else:
                changed = src != dst
        else:
            src, dst = None, value.strip()
            changed = False
        parsed[dim] = (src, dst if dst not in UNCHANGED else src, changed)
    return parsed


def profile(shots, metadata_text):
    """Per-shot variation profile: declared or inferred dimensions, change flags, size rank, camera, OTS."""
    rows = []
    prev = None
    for no, s, e, body in shots:
        tag = tag_of(body)
        field = parse_field(body)
        row = {"no": int(no), "start": s, "end": e, "declared": field is not None, "changes": {}, "新增": None,
               "repeat_of": None}
        repeat = REPEAT_RE.search(body)
        if repeat:
            row["repeat_of"] = int(next(g for g in repeat.groups() if g))
        if field:
            row["新增"] = field.get("新增")
            size_to = field.get("景别", (None, None, False))[1]
            cam_to = field.get("机位", (None, None, False))[1]
            row["size"] = size_to or None
            row["size_rank"] = size_rank(size_to) if size_to else size_rank(tag)
            row["camera"] = (camera_of(cam_to) if cam_to else None) or camera_of(tag)   # 平视→略俯 is an angle, not a move
            row["camera_text"] = cam_to or camera_of(tag)
            row["ots"] = bool(OTS_RE.search(tag) or (cam_to and OTS_RE.search(cam_to)))
            for dim in DIMS:
                if dim in field:
                    row["changes"][dim] = field[dim][2]
                else:
                    row["changes"][dim] = None   # dimension not written
        else:
            row["size_rank"] = size_rank(tag)
            row["size"] = SIZE_NAMES.get(row["size_rank"]) if row["size_rank"] is not None else None
            row["camera"] = camera_of(tag)
            row["camera_text"] = row["camera"]
            row["ots"] = bool(OTS_RE.search(tag))
            if prev is not None:
                if row["size_rank"] is None or prev.get("size_rank") is None:
                    row["changes"]["景别"] = None
                else:
                    row["changes"]["景别"] = row["size_rank"] != prev["size_rank"]
                if row["camera"] is None and prev.get("camera") is None:
                    row["changes"]["机位"] = None
                else:
                    row["changes"]["机位"] = row["camera"] != prev.get("camera")
            row["changes"]["光"] = None
            row["changes"]["幅度"] = None
        if prev is None:
            row["changes"] = {dim: None for dim in DIMS}   # first shot is the baseline
        rows.append(row)
        prev = row
    return rows


def peak_shot(metadata_text):
    m = PEAK_RE.search(metadata_text)
    if not m:
        return None
    n = re.search(r"\d+", m.group(1))
    return int(n.group(0)) if n else None


def is_g6(metadata_text):
    return bool(G6_RE.search(metadata_text))


def change_marks(row):
    return "".join(f"{d}{'✓' if row['changes'].get(d) else ('—' if row['changes'].get(d) is False else '?')}"
                   for d in DIMS)


def variation_checks(shots, metadata_text):
    """shots: [(no, start, end, body)]. Returns (warnings, infos, profile_rows)."""
    warns, infos = [], []
    if not shots:
        return warns, infos, []
    rows = profile(shots, metadata_text)
    if len(rows) < 2:
        # The variation track is about what changes between shots; inside one shot the
        # change is carried by the acting beats and the blocking (S4 / S5 §5.1c).
        infos.append("变化轨：单镜 clip，不查 W30–W33（镜内变化由表演节拍与走位承担）")
        return warns, infos, rows
    n = len(rows)
    peak = peak_shot(metadata_text)
    g6 = is_g6(metadata_text)

    # W32 declaration missing
    undeclared = [r["no"] for r in rows if not r["declared"]]
    if peak is None:
        warns.append("W32 未声明峰值镜（E 层「峰值镜 | N」：全 clip 最大物理动作或最大信息变化所在的镜；峰值镜拿最可见景别与本 clip 首要的有动机运镜）")
    elif peak not in {r["no"] for r in rows}:
        warns.append(f"W32 峰值镜 {peak} 不在分镜时间线里（镜头 {[r['no'] for r in rows]}）")
    if undeclared:
        warns.append(f"W32 镜头 {undeclared} 缺【变化：景别 a→b｜机位 a→b｜光 a→b｜幅度 n→m】字段"
                     f"（S5 变化轨；缺字段时只能按标注推断景别 / 机位两维，光与幅度不可检）")

    # W30 zero-change runs (from the second shot on)
    run, run_start = 0, None
    reported = set()
    for r in rows[1:]:
        tracked = [d for d in DIMS if r["changes"].get(d) is not None]
        zero = bool(tracked) and not any(r["changes"][d] for d in tracked)
        if zero:
            run += 1
            run_start = r["no"] if run == 1 else run_start
            if run == 3 and run_start not in reported:
                reported.add(run_start)
                inferred = any(not x["declared"] for x in rows if run_start <= x["no"] <= r["no"])
                warns.append(f"W30 镜头 {run_start}–{r['no']} 连续 3 镜零变化"
                             f"（{'按标注推断，只查景别 / 机位两维' if inferred else '景别 / 机位或运镜 / 光 / 动作幅度都没变'}）："
                             f"相邻镜至少换一维，或在 A 层写明有意单调")
        else:
            run, run_start = 0, None
    # W30 clip-level: fewer than two dimensions ever change
    if n >= 3:
        changed_dims = [d for d in DIMS if any(r["changes"].get(d) for r in rows[1:])]
        trackable = [d for d in DIMS if any(r["changes"].get(d) is not None for r in rows[1:])]
        if len(changed_dims) < 2 and trackable:
            warns.append(f"W30 全 clip 只有 {len(changed_dims)} 个维度变化过（{'、'.join(DIM_LABELS[d] for d in changed_dims) or '无'}；"
                         f"可检维度 {'、'.join(DIM_LABELS[d] for d in trackable)}）：至少两个维度在 clip 内各变一次")
    # W30 / INFO repeated composition
    for r in rows:
        if r["repeat_of"] is None:
            continue
        added = r.get("新增")
        if g6 and not added:
            warns.append(f"W30 镜头{r['no']} 与镜头{r['repeat_of']} 同构图但未声明新增元素"
                         f"（G6：重复第二次必须多一样东西，写进【变化】的「新增」）")
        else:
            infos.append(f"重复构图：镜头{r['no']} ← 镜头{r['repeat_of']}（新增：{added or '未声明'}）")

    # W31 shot-length contrast
    lengths = [r["end"] - r["start"] for r in rows]
    if n >= 4:
        longest, shortest = max(lengths), min(lengths)
        if shortest > 0 and longest < 2 * shortest - 1e-9:
            warns.append(f"W31 镜长 {[f'{L:g}' for L in lengths]} 无对比：最长 {longest:g}s < 2 × 最短 {shortest:g}s"
                         f"（Lumet：感到的是节奏的变化；30 s 内至少一次镜长对比，有意单调在 A 层写明）")

    # W33 peak shot placement
    if peak is not None:
        pr = next((r for r in rows if r["no"] == peak), None)
        if pr is not None:
            if pr["size_rank"] is not None and pr["size_rank"] <= LEAST_VISIBLE:
                warns.append(f"W33 峰值镜 {peak} 是{SIZE_NAMES.get(pr['size_rank'], '全景')}（最小可见景别）："
                             f"最大动作 / 最大信息变化要拿最可见景别，全景留给建立或收束")
            if pr["ots"]:
                warns.append(f"W33 峰值镜 {peak} 是越肩镜：峰值事件不放在越肩里（前景的肩会吃掉动作幅度），换正面近景 / 双人正面")
            movers = [r["no"] for r in rows if r["no"] != peak and r["camera"] not in (None, "固定")]
            if pr["camera"] == "固定" and movers:
                warns.append(f"W33 峰值镜 {peak} 固定机位，而运镜给了镜头 {movers}："
                             f"本 clip 首要的有动机运镜应落在峰值事件上（或把峰值改到运镜所在的镜）")

    # INFO profile
    counts = {d: sum(1 for r in rows[1:] if r["changes"].get(d)) for d in DIMS}
    marks = " · ".join(f"镜{r['no']} {change_marks(r)}{'' if r['declared'] else '(推断)'}" for r in rows[1:])
    if peak is None:
        peak_txt = "未声明"
    else:
        pr = next((r for r in rows if r["no"] == peak), None)
        peak_txt = "不存在" if pr is None else (
            f"{peak}（{pr.get('size') or SIZE_NAMES.get(pr['size_rank'], '?')}，{pr['camera_text'] or '?'}）")
    infos.append(f"变化轨：{marks or '单镜'}；维度变化次数 景别 {counts['景别']} / 机位 {counts['机位']} / 光 {counts['光']} / 幅度 {counts['幅度']}；"
                 f"峰值镜 {peak_txt}；镜长 {[f'{L:g}' for L in lengths]}")
    return warns, infos, rows
