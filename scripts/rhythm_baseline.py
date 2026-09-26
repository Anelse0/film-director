"""User rhythm baseline for dialogue-led clips: R01-R04 (errors) and W38 (notices). stdlib only.

1.12.0 (2026-09-26). The user's clip-rhythm baseline was set on 2026-09-19 (THE ORDER, D07b as the sample) and
restated after Offset EP01 s04: duration follows the content (dialogue scenes 15-20 s), shots run 2-4 s, opening and
ending silence at most 2 s each and with a function, lines follow each other without gaps, long lines split across
two shots with the second half off-screen. Until 1.11.0 it lived only in memory and in one project's
production-profile.md. validate_prompt fell back to the Skill's looser defaults -- one shot may hold several lines
for 5-8 s (duration-rhythm §四), W23 only above 5 s without speech and camera move, W28 only for exactly one line,
W24 kept with a written reason -- and Offset s04 v4 (2/2/2/6/2/6 s, 3 s silent head, 3 s silent tail) passed with
0 errors and 4 warnings.

This module makes the baseline the default for dialogue-led clips (节奏档 对话) and reports a violation as an ERROR,
so QA cannot keep it by writing a reason:

  R01  a shot longer than 镜长上限 (4 s). Exempt only through the E-layer row
       | 长镜理由 | 镜N 类型：理由 | with a type the script can verify on that shot, up to 持续镜阈值 (8 s):
         持续动作  the shot's 【变化】 amplitude ends at 2 or 3 (a head / hand / body action, or movement);
         运镜      the shot tag carries a camera move (the move needs the time to reach its end);
         长句      the shot holds one line of one sentence whose estimate alone exceeds 镜长上限, and the
                   shot is at most one second longer than that estimate.
       Several lines in one shot are not a type: split at the information change (duration-rhythm §九).
  R02  opening or ending silence longer than 首尾无声上限 (2 s).
  R03  silence between two lines longer than 无声段上限 (2 s).
  R04  E-layer 节奏档 | 表演 on a clip whose speech share makes it dialogue-led (it would skip R01-R03).
       R02-R04 are exempt only through | 基准豁免 | … （用户指定 …） |, the user's own decision.
  W38  notices: gaps between lines of 1-2 s (句间不留空); opening / ending silence of 1 s or more whose
       function is not named in 无声段理由; 语速词每秒 below 语速下限 without 语速理由 (a slow rate makes the
       chained estimate cover gaps the render will have); an E-layer or profile row that loosens the baseline
       without the user; an item in 长镜理由 / 基准豁免 that cannot be read or does not hold.

Silence is measured on the chained dialogue track, the same model as W29: each explicit line starts at
max(its window start, the previous line's finish) and lasts words / rate. A window wider than its line does not
hide silence here (W22 still reviews the window itself).

Precedence, highest first:
  1. 基准豁免 items that say 用户指定, per target (开头 / 结尾 / 镜N / 节奏档 / 全部);
  2. 长镜理由 (R01 only, verified per type);
  3. E-layer threshold rows (镜长上限 / 首尾无声上限 / 无声段上限 / 句间空档提示 / 语速下限) -- tighten only;
  4. the nearest project profile: rhythm-profile.md or production-profile.md in the prompt's folder or any parent,
     holding a table whose first header cell is 节奏基准项. It may switch the baseline off (基准 | 关) or loosen
     a value only when its 来源 row names the user;
  5. BASELINE below.
W22-W37 run unchanged beside these checks; under 节奏档 表演 the baseline reports INFO only (held performance,
duration-rhythm §四), and R04 stops a dialogue-led clip from getting there by declaration.
"""
import math
import re
from pathlib import Path

from rhythm_checks import CAMERA_MOVES, scene_mode, sentence_count, settings as rhythm_settings, tag_of
from variation_checks import parse_field

BASELINE = {
    "镜长上限": 4.0,       # seconds per shot (dialogue-led clips)
    "首尾无声上限": 2.0,   # opening / ending silence
    "无声段上限": 2.0,     # silence between two lines
    "句间空档提示": 1.0,   # a gap of at least this much between lines is listed (W38); also the head/tail function floor
    "语速下限": 3.5,       # English words per second the design may assume without a stated delivery (语速理由)
}
LOWER_IS_LOOSER = {"语速下限"}
BASELINE_SOURCE = "内置用户基准：2026-09-19 THE ORDER 定，2026-09-26 Offset s04 后写进 skill"
PROFILE_NAMES = ("rhythm-profile.md", "production-profile.md")
PROFILE_HEADER = "节奏基准项"
OFF_WORDS = ("关", "off", "否")
LONG_TYPES = ("持续动作", "运镜", "长句")
LONG_RE = re.compile(r"镜(?:头)?\s*(\d+)\s*[（(]?\s*(持续动作|运镜|长句)\s*[)）]?\s*[：:]\s*(\S.*)$")
EPS = 1e-9


def number(value):
    m = re.match(r"\s*(\d+(?:\.\d+)?)", value or "")
    if not m:
        return None
    v = float(m.group(1))
    return v if math.isfinite(v) else None


def looser(key, new, base):
    return new < base - EPS if key in LOWER_IS_LOOSER else new > base + EPS


def read_profile_table(text):
    """Rows of the first markdown table whose first header cell is 节奏基准项, or None."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == PROFILE_HEADER:
            rows = {}
            for row in lines[i + 1:]:
                if not row.strip().startswith("|"):
                    break
                c = [x.strip() for x in row.strip().strip("|").split("|")]
                if len(c) < 2 or not c[0] or set(c[0]) <= set("-: "):
                    continue
                rows[c[0]] = c[1]
            return rows
    return None


def load_profile(prompt_path):
    """Nearest profile (prompt folder, then each parent) with a 节奏基准项 table; None when there is none."""
    if prompt_path is None:
        return None
    here = Path(prompt_path).resolve().parent
    for folder in (here, *here.parents):
        for name in PROFILE_NAMES:
            candidate = folder / name
            if not candidate.is_file():
                continue
            try:
                rows = read_profile_table(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                rows = None
            if rows is not None:
                return {"path": str(candidate), "rows": rows}
    return None


def resolve(profile, metadata_text):
    """(on, values, sources, notices, e_layer_notices) after profile and E-layer rows.

    E-layer notices are reported only where the baseline runs (dialogue-led): a 表演档 clip may legitimately
    carry 首尾无声上限 for the legacy W24 performance form."""
    values, on, sources, notes, layer_notes = dict(BASELINE), True, [BASELINE_SOURCE], [], []
    if profile:
        rows = profile["rows"]
        by_user = "用户" in rows.get("来源", "")
        sources.append(f"项目档案 {profile['path']}" + ("（来源：用户）" if by_user else ""))
        state = rows.get("基准", "").strip().lower()
        if state.startswith(OFF_WORDS):
            if by_user:
                on = False
            else:
                notes.append(f"W38 基准：项目档案 {profile['path']} 写了「基准 | 关」，但「来源」没写用户决定，不生效")
        for key in BASELINE:
            if key not in rows:
                continue
            v = number(rows[key])
            if v is None:
                notes.append(f"W38 基准：项目档案「{key} | {rows[key]}」读不出数值，沿用 {values[key]:g}")
            elif looser(key, v, values[key]) and not by_user:
                notes.append(f"W38 基准：项目档案把「{key}」放宽到 {v:g}，但「来源」没写用户决定，沿用 {values[key]:g}")
            else:
                values[key] = v
    for key in BASELINE:
        m = re.search(r"\|\s*" + key + r"\s*\|\s*([^|\n]+)\|", metadata_text)
        if not m:
            continue
        v = number(m.group(1))
        if v is None:
            layer_notes.append(f"W38 基准：E 层「{key} | {m.group(1).strip()}」读不出数值，沿用 {values[key]:g}")
        elif looser(key, v, values[key]):
            layer_notes.append(f"W38 基准：E 层「{key} | {v:g}」比基准 {values[key]:g} 宽，不生效（E 层只能收紧；放宽要用户指定，"
                         f"写进「基准豁免」或项目档案并注明来源）")
        else:
            values[key] = v
    return on, values, sources, notes, layer_notes


def user_overrides(metadata_text):
    """基准豁免 items that carry 用户指定; others become notices."""
    items, notes = [], []
    for m in re.finditer(r"\|\s*基准豁免\s*\|\s*([^|\n]+)\|", metadata_text):
        for item in re.split(r"[；;]", m.group(1)):
            item = item.strip()
            if not item:
                continue
            if "用户指定" in item:
                items.append(item)
            else:
                notes.append(f"W38 基准：「基准豁免」项「{item[:40]}」没写「用户指定」，不生效（豁免只来自用户在对话里的决定，写日期）")
    return items, notes


def override_for(items, target, shot=None):
    for item in items:
        if target == "全部" and re.search(r"全部|基准\s*关", item):
            return item
        if target in ("开头", "结尾", "节奏档") and target in item:
            return item
        if target == "镜" and shot is not None and re.search(r"镜(?:头)?\s*" + str(shot) + r"(?!\d)", item):
            return item
    return None


def long_reasons(metadata_text):
    """{shot: (type, reason, raw)} from 长镜理由 rows, plus notices for unreadable items."""
    found, notes = {}, []
    for m in re.finditer(r"\|\s*长镜理由\s*\|\s*([^|\n]+)\|", metadata_text):
        for item in re.split(r"[；;]", m.group(1)):
            item = item.strip()
            if not item:
                continue
            lm = LONG_RE.match(item)
            if not lm:
                notes.append(f"W38 基准：「长镜理由」项「{item[:40]}」读不出（格式：镜N 类型：理由；类型 = 持续动作 / 运镜 / 长句）")
                continue
            found[int(lm.group(1))] = (lm.group(2), lm.group(3).strip(), item)
    return found, notes


def verify_long(kind, shot, lines, limit, sustained):
    """(holds, why) for one 长镜理由 item on shot (no, s, e, body)."""
    no, s, e, body = shot
    length = e - s
    if length > sustained + EPS:
        return False, f"镜{no} {length:g}s 超过持续镜阈值 {sustained:g}s，长镜理由不适用（同时见 W23）"
    if kind == "运镜":
        tag = tag_of(body)
        if any(w in tag for w in CAMERA_MOVES):
            return True, ""
        return False, f"镜{no} 标注【{tag[:24]}】里没有运镜"
    if kind == "持续动作":
        field = parse_field(body)
        amp = field.get("幅度") if field else None
        dst = amp[1] if amp else None
        if dst is None or not re.fullmatch(r"\d+", str(dst).strip()):
            return False, f"镜{no} 没有【变化】幅度，核对不了持续动作"
        if int(dst) < 2:
            return False, f"镜{no} 幅度 {dst}（持续动作要幅度 2–3：头 / 手 / 上身的一个动作或全身位移）"
        return True, ""
    if kind == "长句":
        if len(lines) != 1:
            return False, f"镜{no} 有 {len(lines)} 段台词（长句只适用于一镜一句；多句在信息变化处切）"
        line = lines[0]
        if sentence_count(line["text"]) > 1:
            return False, f"镜{no} 这段台词有 {sentence_count(line['text'])} 句（按句号拆成跨镜两段，后半句画外）"
        if line["estimate"] <= limit + EPS:
            return False, f"镜{no} 这句估时 {line['estimate']:.1f}s，{limit:g}s 的镜放得下"
        if length > math.ceil(line["estimate"] - EPS) + 1 + EPS:
            return False, f"镜{no} {length:g}s 比这句估时 {line['estimate']:.1f}s 长出 1s 以上"
        return True, ""
    return False, f"类型「{kind}」不在 持续动作 / 运镜 / 长句 之内"


def chain(explicit):
    """Chained speech: [(row, begin, finish)] in start order (same model as rhythm_checks.track_schedule)."""
    out, prev = [], 0.0
    for r in sorted(explicit, key=lambda x: (x["start"], x["end"])):
        begin = max(r["start"], prev)
        finish = begin + r["estimate"]
        out.append((r, begin, finish))
        prev = finish
    return out


def overlap(a, b, s, e):
    return max(0.0, min(b, e) - max(a, s))


def speech_rate(metadata_text):
    m = re.search(r"\|\s*语速词每秒\s*\|\s*([^|\n]+)\|", metadata_text)
    return number(m.group(1)) if m else None


def baseline_checks(shots, rows, duration, metadata_text, profile=None):
    """shots: [(no, start, end, body)]; rows: dialogue rows. Returns (errors, warns, infos, stats)."""
    errors, warns, infos = [], [], []
    stats = {"status": "not_applicable"}
    if not shots or duration is None or duration <= 0:
        return errors, warns, infos, stats
    on, values, sources, notes, layer_notes = resolve(profile, metadata_text)
    items, override_notes = user_overrides(metadata_text)
    notes += override_notes
    stats.update({"source": sources, "values": values})
    cfg = rhythm_settings(metadata_text)
    explicit = [r for r in rows if r["explicit"] and r["end"] > r["start"]]
    est_total = sum(r["estimate"] for r in explicit)
    auto = scene_mode("", est_total, duration, len(shots), cfg)
    declared = scene_mode(metadata_text, est_total, duration, len(shots), cfg)
    lengths = {no: e - s for no, s, e, _ in shots}
    limit = values["镜长上限"]
    head = (f"节奏基准（{'；'.join(sources)}）：镜长 ≤{limit:g}s · 开头 / 结尾无声 ≤{values['首尾无声上限']:g}s · "
            f"句间无声 ≤{values['无声段上限']:g}s（≥{values['句间空档提示']:g}s 列出）· 语速 ≥{values['语速下限']:g} 词/s")
    everything = override_for(items, "全部")
    if not on or everything:
        infos.append(head.replace("节奏基准（", "节奏基准 关（", 1) + f"；{'用户豁免：' + everything[:60] if everything else '项目档案关闭'}"
                     "；R01–R04 不查，W22–W37 照常")
        warns.extend(notes)
        stats["status"] = "off"
        return errors, warns, infos, stats

    mode = declared
    if declared == "表演" and auto == "对话":
        ok = override_for(items, "节奏档")
        share = est_total / duration
        if ok:
            infos.append(f"基准豁免（用户指定）：节奏档 表演（台词 {share:.0%}）——{ok[:60]}")
        else:
            errors.append(f"R04 E 层「节奏档 | 表演」，但台词净时长 {est_total:.1f}s / {duration:g}s = {share:.0%} ≥ "
                          f"{cfg['对话场判定占比']:.0%}，是对话场：表演档会跳过 R01–R03，这里按对话档查"
                          f"（只有用户指定才可在「基准豁免」写 节奏档）")
            mode = "对话"
    if mode != "对话":
        over = [f"镜{no} {L:g}s" for no, L in lengths.items() if L > limit + EPS]
        infos.append(head + f"；本条 节奏档 表演，基准只查对话档，R01–R03 不查"
                     + (f"（>{limit:g}s 的镜：{'、'.join(over)}）" if over else ""))
        warns.extend(notes)
        return errors, warns, infos, stats

    infos.append(head + "；只有用户指定可豁免（「基准豁免」），R01 另可按类型写「长镜理由」；不能在 QA 写理由保留")
    notes += layer_notes
    reasons, reason_notes = long_reasons(metadata_text)
    notes += reason_notes
    flags = {no: [] for no in lengths}

    # R01 shot length
    for shot in shots:
        no, s, e, body = shot
        L = e - s
        if L <= limit + EPS:
            continue
        lines = [r for r in explicit if r["shot"] == str(no)]
        ov = override_for(items, "镜", no)
        if ov:
            infos.append(f"基准豁免（用户指定）：镜头{no} {L:g}s——{ov[:60]}")
            flags[no].append("豁免")
            continue
        entry = reasons.get(no)
        if entry:
            holds, why = verify_long(entry[0], shot, lines, limit, cfg["持续镜阈值"])
            if holds:
                infos.append(f"长镜理由成立：镜头{no} {L:g}s {entry[0]}——{entry[1][:50]}")
                flags[no].append(entry[0])
                continue
            notes.append(f"W38 基准：长镜理由「{entry[2][:40]}」不成立：{why}")
        fixed = not any(w in tag_of(body) for w in CAMERA_MOVES)
        many = sum(sentence_count(r["text"]) for r in lines)
        detail = (f"固定机位 {len(lines)} 段台词 / {many} 句" if fixed and many >= 2 else
                  f"{len(lines)} 段台词" if lines else "无台词")
        errors.append(f"R01 镜头{no} {L:g}s > 基准镜长 {limit:g}s（{detail}）：在信息变化处切成两镜——前半句画内、后半句画外落在"
                      f"听者 / 插入 / 动作上，无台词的动作并进说话的镜；只有 持续动作 / 运镜 / 长句 可在 E 层「长镜理由 | 镜{no} 类型：…」登记，"
                      f"不能在 QA 写理由保留")
        flags[no].append("R01")

    # R02 / R03 silence on the chained track
    track = chain(explicit)
    silent = []
    if track:
        lead = track[0][1]
        last = min(max(f for _, _, f in track), duration)
        trail = max(0.0, duration - last)
        silent.append((0.0, lead, "开头"))
        for (r1, b1, f1), (r2, b2, f2) in zip(track, track[1:]):
            if r2["start"] > f1 + EPS:
                silent.append((f1, r2["start"], "句间"))
        silent.append((last, duration, "结尾"))
        why_row = re.search(r"\|\s*无声段理由\s*\|\s*([^|\n]+)\|", metadata_text)
        why_text = why_row.group(1) if why_row else ""
        cap_edge, cap_mid, hint = values["首尾无声上限"], values["无声段上限"], values["句间空档提示"]
        for a, b, where in silent:
            g = b - a
            if g <= EPS:
                continue
            covered = [no for no, s, e, _ in shots if overlap(a, b, s, e) > EPS]
            if where in ("开头", "结尾"):
                if g > cap_edge + EPS:
                    ov = override_for(items, where)
                    if ov:
                        infos.append(f"基准豁免（用户指定）：{where} {g:.1f}s 无台词——{ov[:60]}")
                    else:
                        fix = ("让第一句在 {0:g}s 内开口（台词可从画外先起），或把开头压成一个 ≤{0:g}s 的有功能的镜" if where == "开头"
                               else "事件完成即停：缩短末镜，或让最后一句 / 画外句落在末镜里").format(cap_edge)
                        errors.append(f"R02 {where} {g:.1f}s 无台词 > 基准 {cap_edge:g}s（{a:.1f}–{b:.1f}s，镜头 {covered}；同 W24，"
                                      f"基准下不能写理由保留）：{fix}；只有用户指定才可写进「基准豁免」")
                        for no in covered:
                            flags[no].append("R02")
                elif g >= hint - EPS:
                    named = where in why_text or any(re.search(r"镜(?:头)?\s*" + str(no) + r"(?!\d)", why_text) for no in covered)
                    if not named:
                        notes.append(f"W38 基准：{where} {g:.1f}s 无台词（镜头 {covered}），「无声段理由」没写这段的功能"
                                     f"（建立 / 揭示 / 反应 / 物件行动 / 出画停留，写镜号）")
            else:
                if g > cap_mid + EPS:
                    ov = next((override_for(items, "镜", no) for no in covered if override_for(items, "镜", no)), None)
                    if ov:
                        infos.append(f"基准豁免（用户指定）：{a:.1f}–{b:.1f}s 句间 {g:.1f}s——{ov[:60]}")
                    else:
                        errors.append(f"R03 {a:.1f}–{b:.1f}s 两句之间 {g:.1f}s 无台词 > 基准 {cap_mid:g}s（镜头 {covered}）："
                                      f"句间不留空——下一句在上一句说完时就起，动作并进说话的镜；只有用户指定才可写进「基准豁免」")
                        for no in covered:
                            flags[no].append("R03")
                elif g >= hint - EPS:
                    notes.append(f"W38 基准：{a:.1f}–{b:.1f}s 句间空 {g:.1f}s（镜头 {covered}；句间不留空，提前下一句起点或并掉这段动作）")
        stats.update({"lead": lead, "trail": trail,
                      "gaps": [(round(a, 2), round(b, 2)) for a, b, w in silent if w == "句间" and b - a >= hint - EPS]})

    # W38 speech-rate floor: a slow design rate makes the chain cover gaps the render will have (D05)
    rate = speech_rate(metadata_text)
    if rate is not None and rate < values["语速下限"] - EPS and not re.search(r"\|\s*语速理由\s*\|\s*[^|\n\s]", metadata_text):
        notes.append(f"W38 基准：语速词每秒 {rate:g} < 基准 {values['语速下限']:g}，没写「语速理由」（估时按慢语速算，"
                     f"句间空档与首尾无声会被算小；改回 {values['语速下限']:g}–4，或写明这场怎么说）")

    # per-shot table: the whole clip, so a "slow" note is answered shot by shot, not only for the shots named
    cells = []
    for no, s, e, _ in shots:
        quiet = sum(overlap(a, b, s, e) for a, b, _ in silent)
        mark = "、".join(dict.fromkeys(flags[no]))
        cells.append(f"镜{no} {e - s:g}s" + (f" 无声{quiet:.1f}" if quiet >= 0.05 else "") + (f" [{mark}]" if mark else ""))
    infos.append("节奏基准逐镜：" + " ｜ ".join(cells))
    warns.extend(notes)
    stats.update({"status": "failed" if errors else "passed",
                  "shots": [{"shot": no, "length": e - s, "flags": list(dict.fromkeys(flags[no]))} for no, s, e, _ in shots]})
    return errors, warns, infos, stats
