"""Duration and rhythm review hints (stdlib only).

W05 only guards the upper side of a dialogue window (speech must fit). These
checks guard the lower side of time use: windows much wider than the speech,
silent stretches without a declared function, long shots that carry neither
speech nor a camera move, and a clip-level average shot length. Every result
is a review hint (WARN/INFO), never a quota: the E-layer can retune each
threshold, and a reviewed reason keeps the design. Thresholds are the Skill's
own inference from the official 30 s example (9 shots, 3.3 s average, one 3 s
shot without speech = 10 % silent) and editing literature; see
references/duration-rhythm.md.
"""
import math
import re

CAMERA_MOVES = [
    "推", "拉", "摇", "横移", "跟拍", "跟随", "跟进", "跟下", "环绕", "升", "降", "俯冲", "后拉", "手持", "随",
    "push", "pull", "pan", "tilt", "truck", "track", "orbit", "crane", "dolly", "handheld", "zoom",
]

DEFAULTS = {
    "台词填充率": 0.9,       # window = estimate / fill, rounded up to 0.5 s
    "窗口松弛上限": 1.0,     # seconds a window may exceed the recommended one
    "无声段占比上限": 0.2,   # share of the clip outside every dialogue window
    "首尾无声上限": 2.0,     # leading / trailing seconds without dialogue
    "长镜阈值": 5.0,         # shot longer than this with no speech and no move
    "持续镜阈值": 8.0,       # any shot longer than this needs a stated reason
    "对话场平均镜长上限": 4.5,
    "时长冗余阈值": 4.0,     # declared − derived reference
    "对话场判定占比": 0.25,  # speech estimate / duration at or above this = dialogue-led clip
    "动作节拍秒数": 0.0,     # declared seconds of physical beats inside dialogue shots (adds to the derived reference)
    "整句一镜阈值": 4.0,     # fixed shot holding exactly one whole line for at least this long -> W28
    "台词轨溢出容差": 1.0,   # continuous track: a line may run past its window / into the next shot by this much
}
TRACK_MODES = ("窗口", "连续")


def track_mode(metadata_text, scene="对话"):
    """E-layer 台词轨 wins; otherwise a dialogue-led clip uses 连续 (lines chain across cuts) and a
    performance-led clip uses 窗口 (each line fits its own window)."""
    m = re.search(r"\|\s*台词轨\s*\|\s*([^|\n]+)\|", metadata_text)
    if not m:
        return "连续" if scene == "对话" else "窗口"
    value = m.group(1).strip()
    if value not in TRACK_MODES:
        raise ValueError("台词轨 must be 窗口 or 连续")
    return value


def track_schedule(rows, duration, tolerance):
    """Chain explicit lines in start order: each begins at max(its window start, previous finish).

    Returns (warnings, finish_times, slack). A warning fires only when the chained speech would
    still be running past the next line's start by more than tolerance, or past the clip end."""
    warns, finishes = [], []
    ordered = sorted(rows, key=lambda r: (r["start"], r["end"]))
    prev_finish = 0.0
    for i, r in enumerate(ordered):
        begin = max(r["start"], prev_finish)
        finish = begin + r["estimate"]
        finishes.append(finish)
        nxt = ordered[i + 1]["start"] if i + 1 < len(ordered) else None
        if nxt is not None and finish > nxt + tolerance + 1e-9:
            warns.append(f"W29 台词轨：{r['speaker']}「{r['text'][:24]}」按 {r['start']:g}s 起说到 {finish:.1f}s，"
                         f"压过下一句起点 {nxt:g}s 超过 {tolerance:g}s（后移下一句或拆句）")
        elif duration is not None and nxt is None and finish > duration + 1e-9:
            warns.append(f"W29 台词轨：末句按 {r['start']:g}s 起说到 {finish:.1f}s > 片长 {duration:g}s")
        prev_finish = finish
    slack = None
    if ordered:
        slack = (ordered[-1]["end"] - finishes[-1]) if finishes else None
    return warns, finishes, slack

MODES = ("对话", "表演")
# Tempo cues in the observable prose. Slow cues are legitimate directing; the
# count only tells the reviewer where the "air" in a slow render was written.
SLOW_CUES = ["不急", "放慢", "慢慢", "缓慢", "缓缓", "缓推", "缓拉", "缓摇", "停住", "停在", "停顿", "停留", "定格",
             "留白", "静止", "不动", "沉默", "等他", "等她", "等着", "犹豫", "迟疑", "顿了", "顿一下", "停一拍",
             "slowly", "pause", "hold", "beat", "linger", "still"]
FAST_CUES = ["紧接", "紧贴", "抢话", "抢在", "连读", "不停顿", "不留停顿", "立刻", "随即", "马上", "说完即",
             "利落", "快速", "干脆", "immediately", "hard cut", "overlap", "no pause"]


def scene_mode(metadata_text, est_total, duration, shot_count, cfg):
    """E-layer 节奏档 wins; otherwise a clip whose speech fills >= 25 % is dialogue-led."""
    m = re.search(r"\|\s*节奏档\s*\|\s*([^|\n]+)\|", metadata_text)
    if m:
        value = m.group(1).strip()
        if value not in MODES:
            raise ValueError("节奏档 must be 对话 or 表演")
        return value
    if duration and shot_count >= 2 and est_total / duration >= cfg["对话场判定占比"]:
        return "对话"
    return "表演"


def settings(metadata_text):
    values = dict(DEFAULTS)
    for key in DEFAULTS:
        m = re.search(r"\|\s*" + key + r"\s*\|\s*([^|\n]+)\|", metadata_text)
        if m:
            try:
                v = float(m.group(1).strip())
            except ValueError:
                raise ValueError(f"{key} invalid")
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{key} invalid")
            values[key] = v
    return values


def ceil_half(x):
    return math.ceil(x * 2 - 1e-9) / 2


def recommended_window(estimate, fill):
    """estimate / fill rounded up to 0.5 s; a single word still needs 1 s."""
    return max(1.0, ceil_half(estimate / fill)) if estimate > 0 else 0.0


def union_length(intervals):
    total, cur = 0.0, None
    for s, e in sorted(intervals):
        if cur is None or s > cur[1]:
            if cur:
                total += cur[1] - cur[0]
            cur = [s, e]
        else:
            cur[1] = max(cur[1], e)
    if cur:
        total += cur[1] - cur[0]
    return total


def tag_of(body):
    tag = re.search(r"【([^】]{2,60})】|\[([^\]]{2,80})\]", body[:80])
    return (tag.group(1) or tag.group(2)) if tag else ""


def rhythm_checks(shots, rows, duration, metadata_text):
    """shots: [(no, start, end, body)]; rows: dialogue rows from dialogue_checks."""
    cfg = settings(metadata_text)
    warns, infos = [], []
    if not shots or duration is None or duration <= 0:
        return warns, infos, {}
    explicit = [r for r in rows if r["explicit"] and r["end"] > r["start"]]
    est_total = sum(r["estimate"] for r in explicit)
    mode = scene_mode(metadata_text, est_total, duration, len(shots), cfg)
    dialogue_led = mode == "对话"
    infos.append(f"节奏档 {mode}（台词净时长 {est_total:.1f}s / {duration:g}s；≥{cfg['对话场判定占比']:.0%} 判为对话场，可用 E 层「节奏档」覆盖；对话场默认 台词轨=连续）")

    # W22 dialogue window much wider than the speech it holds
    rec_total = 0.0
    for r in explicit:
        rec = recommended_window(r["estimate"], cfg["台词填充率"])
        rec_total += rec
        window = r["end"] - r["start"]
        if window > rec + cfg["窗口松弛上限"] + 1e-9:
            warns.append(
                f"W22 {r['speaker']} 台词窗口 {window:g}s 比建议 {rec:g}s 宽 {window - rec:.1f}s"
                f"（估时 {r['estimate']:.1f}s ÷ {cfg['台词填充率']:g} 向上取 0.5s；反应放在窗口外的镜内余量或反应镜）")

    # W23 long shots (dialogue-led clips): no speech and no camera move, or beyond the sustained limit
    for no, s, e, body in shots if dialogue_led else []:
        length = e - s
        lines = [r for r in rows if r["shot"] == str(no)]
        tag = tag_of(body)
        moving = any(w in tag for w in CAMERA_MOVES)
        if length > cfg["持续镜阈值"]:
            warns.append(f"W23 镜头{no} 长 {length:g}s > {cfg['持续镜阈值']:g}s（持续表演镜须在 QA 写不可切断的理由）")
        elif length > cfg["长镜阈值"] and not lines and not moving:
            warns.append(f"W23 镜头{no} 长 {length:g}s 且无台词、标注无运镜（写明观众这几秒在看什么，或缩短 / 拆镜）")

    # W28 one whole line held in one fixed shot for >= 4 s: the cut is waiting for the sentence
    if dialogue_led:
        for no, s, e, body in shots:
            length = e - s
            lines = [r for r in rows if r["shot"] == str(no)]
            tag = tag_of(body)
            if length >= cfg["整句一镜阈值"] and len(lines) == 1 and not any(w in tag for w in CAMERA_MOVES) \
                    and (lines[0]["end"] - lines[0]["start"]) >= length - 1e-9:
                warns.append(f"W28 镜头{no} {length:g}s 固定机位只承载一整句（{lines[0]['speaker']}）：在信息变化处切——前半句画内、后半句画外落在听者 / 插入 / 视线对象，或换景别（duration-rhythm §九）")

    # W24 silence outside dialogue windows (only for clips that have dialogue)
    stats = {}
    if dialogue_led and explicit:
        occupied = union_length([(r["start"], r["end"]) for r in explicit])
        silent = duration - occupied
        lead = min(r["start"] for r in explicit)
        trail = duration - max(r["end"] for r in explicit)
        gaps = []
        prev_end = None
        for r in sorted(explicit, key=lambda x: x["start"]):
            if prev_end is not None and r["start"] - prev_end >= 1.0:
                gaps.append(f"{prev_end:g}-{r['start']:g}s")
            prev_end = max(prev_end or 0, r["end"])
        share = silent / duration
        if share > cfg["无声段占比上限"] + 1e-9:
            warns.append(
                f"W24 台词窗口外 {silent:g}s（{share:.0%} > {cfg['无声段占比上限']:.0%}）：开头 {lead:g}s，结尾 {trail:g}s"
                f"{'，句间 ' + '、'.join(gaps) if gaps else ''}（每段无声须有可写出的叙事功能，否则收紧）")
        if lead > cfg["首尾无声上限"] + 1e-9:
            warns.append(f"W24 开头 {lead:g}s 无台词 > {cfg['首尾无声上限']:g}s（迟进：从事件已在进行的一刻开始，或写明这几秒的信息功能）")
        if trail > cfg["首尾无声上限"] + 1e-9:
            warns.append(f"W24 结尾 {trail:g}s 无台词 > {cfg['首尾无声上限']:g}s（早出：事件完成即停，或写明停留的功能）")
        stats.update({"silent": silent, "silent_share": share, "lead": lead, "trail": trail, "gaps": gaps})

    # W25 / INFO average shot length and distribution
    lengths = [e - s for _, s, e, _ in shots]
    asl = sum(lengths) / len(lengths)
    buckets = {"<2s": 0, "2-4s": 0, "4-5s": 0, ">5s": 0}
    for L in lengths:
        buckets["<2s" if L < 2 else "2-4s" if L <= 4 else "4-5s" if L <= 5 else ">5s"] += 1
    longest = max(shots, key=lambda x: x[2] - x[1])
    infos.append(
        f"平均镜长 {asl:.1f}s（{len(shots)} 镜 / {duration:g}s）；分布 " +
        "，".join(f"{k} {v}" for k, v in buckets.items()) +
        f"；最长镜头{longest[0]} {longest[2] - longest[1]:g}s")
    if dialogue_led and asl > cfg["对话场平均镜长上限"] + 1e-9:
        warns.append(f"W25 对话场平均镜长 {asl:.1f}s > {cfg['对话场平均镜长上限']:g}s（对白镜 2-4s 为目标；持续镜需理由）")

    # W29 continuous dialogue track (E-layer 台词轨 | 连续): lines chain across cuts
    mode_track = track_mode(metadata_text, mode)
    if explicit:
        tw, finishes, slack = track_schedule(explicit, duration, cfg["台词轨溢出容差"])
        if mode_track == "连续":
            warns.extend(tw)
        infos.append(f"台词轨 {mode_track}：{len(explicit)} 句连续说完约在 {finishes[-1]:.1f}s"
                     f"（末句窗口止于 {max(r['end'] for r in explicit):g}s，余量 {slack:+.1f}s）")
        stats.update({"track_finish": finishes[-1], "track_slack": slack, "track_mode": mode_track})

    # W27 tempo cues: where a slow render was written (dialogue-led clips)
    if dialogue_led:
        prose = re.sub(r"[“\"][^”\"\n]*[”\"]", "", "\n".join(body for _, _, _, body in shots))  # not the lines themselves
        slow = [c for c in SLOW_CUES if c in prose]
        fast = [c for c in FAST_CUES if c in prose]
        n_slow = sum(prose.count(c) for c in SLOW_CUES)
        n_fast = sum(prose.count(c) for c in FAST_CUES)
        infos.append(f"减速词 {n_slow}（{'、'.join(slow) if slow else '无'}）/ 提速词 {n_fast}（{'、'.join(fast) if fast else '无'}）")
        if n_slow >= 4 and n_slow >= 2 * n_fast:
            warns.append(f"W27 分镜正文减速词 {n_slow} 处、提速词 {n_fast} 处（每个「停 / 慢 / 不动」都会被执行成时长；保留有戏的，其余删）")
        stats.update({"slow_cues": n_slow, "fast_cues": n_fast})

    # INFO time budget and derived duration reference
    if explicit:
        win_total = sum(r["end"] - r["start"] for r in explicit)
        silent_shots = sum(e - s for no, s, e, _ in shots if not any(r["shot"] == str(no) for r in rows))
        beats = cfg["动作节拍秒数"]
        track_total = est_total / cfg["台词填充率"]   # one rounding for the whole track, not per line
        derived = math.ceil(track_total + silent_shots + beats - 1e-9)
        infos.append(
            f"台词净时长 {est_total:.1f}s；建议窗口合计 {rec_total:g}s；实际窗口合计 {win_total:g}s（松弛 {win_total - rec_total:.1f}s）；"
            f"窗口外 {duration - union_length([(r['start'], r['end']) for r in explicit]):g}s")
        infos.append(
            f"按台词量推导的时长参考 ≈ 台词轨 {track_total:.1f}s（净 {est_total:.1f}s ÷ {cfg['台词填充率']:g}）+ 无台词镜 {silent_shots:g}s + 动作节拍 {beats:g}s = {derived}s（声明 {duration:g}s；逐句取整的窗口合计 {rec_total:g}s 只作参考）")
        if dialogue_led and duration - derived >= cfg["时长冗余阈值"] - 1e-9:
            warns.append(
                f"W26 声明时长 {duration:g}s 比推导参考 {derived}s 多 {duration - derived:g}s ≥ {cfg['时长冗余阈值']:g}s"
                f"（30s 不是默认值：多出的秒数要能指到具体的反应 / 动作节拍——在 E 层「动作节拍秒数」登记——否则缩短 clip）")
        stats.update({"asl": asl, "estimate_total": est_total, "window_total": win_total,
                      "recommended_total": rec_total, "derived": derived})
    return warns, infos, stats
