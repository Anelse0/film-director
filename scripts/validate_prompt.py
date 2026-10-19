#!/usr/bin/env python3
"""Prompt format/fidelity checks for film-seedance-director.
Usage: validate_prompt.py FILE... [--duration N] [--json]
       [--artifact production|performance|raw] [--record RECORD.json]
       [--entry-id N] [--batch sequence|independent]
Default production CLI remains compatible. ERROR is a format/contract issue,
not necessarily an official model limitation. WARN requires review.
F01-F06 concern record/schema/text fidelity; E20 concerns performance timing.
W14 reviews identical adjacent complete blocks; W18 and W19 are retired.
W04 thresholds follow the official 30s example (9 shots, 2s minimum): <2s and >10 shots per 30s are review hints.
W22-W29 (rhythm_checks.py) review the lower side of time use: wide dialogue windows, long silent
shots, silence share, dialogue-scene average shot length, declared-vs-derived duration, tempo cues,
whole-line-one-shot, and (E-layer 台词轨 | 连续) the chained dialogue track replacing per-window W05.
W30-W33 (variation_checks.py) review the variation track — what changes between shots: zero-change
runs / too few changing dimensions / G6 repeat without a new element (W30), no shot-length contrast
(W31), undeclared 峰值镜 or missing 【变化】 fields (W32), peak shot in a wide / OTS / fixed-while-
others-move shot (W33). 节奏档 selects a check set (对话: W22-W33; 表演: W24 + W30-W33), never INFO-only.
E23 (direction_checks.py) is the one heuristic ERROR, not a format fact: a toward-camera / backward-tracking
shot that also names a landmark as ahead of the character (朝X走 / 前面的X / 退向X) without anchoring X to the
camera (镜头身后 / 画面深处 / 画左右) in the same text unit — the model renders the character walking away, so
the wording is fixed before a render; INFO when movement exists but 【贯穿要求】 has no 方向 line.
W35 (tone_checks.py) reviews tone cues: freeze / slow head turn toward an off-screen arrival / stare + lowered
voice / approach toward camera with no state / head-down-eyes-up or eyes-only glance read as suspense whatever
the tone word says; WARN per shot when the prompt declares a light tone, or when such cues cluster with no tone
declared; INFO when 悬疑 / 喜剧 is declared (freeze and deadpan are those genres' own devices).
1.6.0 (guide_checks.py, official FAQ): W36 delivery notes after a quoted line / re-quoted fragments (subtitle trigger),
W37 audio policy at start and end with music synonyms enumerated, W38 length budget (INFO always; WARN > 1,500 CJK /
900 EN words, E-layer 字数上限 / 词数上限), W39 character assets in first-appearance order and E-layer 上传与角色 order,
W40 intensity labels (眼睛发光 trigger), W41 declared-but-unreferenced assets. Assets may be numbered (图1 / @图片1) or
named (`@Theo-基础形象：…` declaration lines, `@Theo-基础形象` references). The variation track is read from the E-layer
`变化轨` row first (inline 【变化：…】 fields are legacy).
1.7.0: W43 (focus_checks.py) every on-screen character shot states 焦点在 X and any over-shoulder / soft layer says where it
sits (E-layer 焦点理由 keeps a reviewed design); W44 (subtext_checks.py) actions written into the dialogue bracket, or an intent
word in the bracket of a close shot with no executable beat for that speaker in the shot line — 1.7.1: eye / face, hand /
body, voice or pause, an action toward the other character, or a delivery word in the bracket (口气 words stay; one line per shot);
W45 (costume_checks.py) a sustained wearing-state deviation while the character's binding lines use the image-equals-state
wording (唯一的服装 / 一律按 @图; E-layer 穿着状态说明 keeps a reviewed design). Shot tags may run to 80 characters.
1.9.0 (offset EP06 clip01 / clip02 renders): W46-W49 (wording_checks.py) wording the model executes literally — a character's
own left / right or an undefined landmark side used as a screen position, and an over-the-shoulder shoulder that disagrees
with its frame corner (W46); speed words in the dialogue bracket or a fast voice line (W47); a held phone / cup / bottle
with no grip, or 捂 … 话筒 (W48); flustered / wide-eyed acting words in a light-tone clip (W49). W51 (continuity_checks.py)
the first shot of a last-frame continuation replays the previous beat. W52 (viewpoint_checks.py) an object placed behind
the camera mentioned more than once per shot / per global sentence, and a scene image bound with 不参考视角 for one shot
only (E-layer 视角说明 keeps a reviewed choice). W50 is reserved for the per-shot load count (not in this release).
English speech estimate defaults to 3.5 words/s (1.4.0; 2.5 = American-English mean, a floor).
Semantic acting quality is always needs_review; render is always not_tested.
Exit 0 means no deterministic errors, 1 check failure, 2 invalid invocation/input.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

from performance_checks import split_beats, timing_errors, check_record, check_raw, repeated_blocks
from prompt_structure import Document, dialogue_checks
from production_contract import metadata, task_type, parameters, roles_from_fields, check_parameters, TASKS
from rhythm_checks import rhythm_checks, settings as rhythm_settings, track_mode, scene_mode
from variation_checks import variation_checks
from direction_checks import direction_checks
from tone_checks import tone_checks
from guide_checks import guide_checks
from focus_checks import focus_checks
from subtext_checks import subtext_checks
from costume_checks import costume_checks
from wording_checks import wording_checks
from continuity_checks import continuity_checks
from viewpoint_checks import viewpoint_checks

# ---------- 词表 ----------
VAGUE_WORDS = [
    "电影感", "唯美", "震撼", "史诗感", "高级感", "氛围感", "大片感", "大片",
    "cinematic", "stunning", "epic", "beautiful", "premium", "breathtaking",
]
CAMERA_MOVES = [
    "推", "拉", "摇", "横移", "跟拍", "跟随", "环绕", "升", "降", "俯冲", "后拉", "手持",
    "push", "pull", "pan", "tilt", "truck", "track", "orbit", "crane", "dolly", "handheld", "zoom",
]
SHOT_SIZE_WORDS = ["远景", "全景", "中景", "近景", "特写", "wide", "medium", "close-up", "close up", "extreme"]
NEG_ALLOWED = ["字幕", "bgm", "背景音乐", "对白", "人声", "音效", "声音", "音乐", "旁白", "配乐",
               "subtitle", "caption", "music", "dialogue", "narration", "voice", "sound", "score", "bgm"]
# Only explicit object-exclusion syntax; no blanket "no/without/无" scanning.
# Behavioral negation and ambiguous English phrases require semantic review.
NEG_PATTERNS = [r"不要出现[^，。；\n]{1,20}", r"不(?:能|准|得)?出现[^，。；\n]{1,20}",
                r"画面[里中内]没有[^，。；\n]{1,20}",
                r"\b(?:do not include|must not show|exclude)\s+[^.\n]{1,30}"]
DIRECTOR_NAMES = [
    "希区柯克", "斯皮尔伯格", "芬奇", "哈内克", "卡隆", "维伦纽瓦", "兰斯莫斯", "科恩", "埃德加", "吕美特",
    "马梅", "库布里克", "诺兰", "斯科塞斯", "伯格曼", "韦斯·安德森", "塔可夫斯基", "王家卫", "是枝裕和",
    "hitchcock", "spielberg", "fincher", "haneke", "cuar", "villeneuve", "lanthimos", "coen", "edgar wright",
    "lumet", "mamet", "kubrick", "nolan", "scorsese", "bergman", "wes anderson", "tarkovsky", "deakins",
    "wong kar", "malick", "tarantino", "anderson", "lynch", "ozu", "bresson",
]
CLICHE_PATTERNS = [
    (r"(缓慢?推近|缓推|push in|dolly in)[^。\n]{0,60}(泪|哭|悲伤|难过|tear|cry)", "悲伤脸缓推"),
    (r"(黄金时刻|golden hour|逆光[^。\n]{0,10}暖金|镜头光晕|lens flare)", "黄金时刻"),
    (r"(雨夜|rain)[^。\n]{0,30}(霓虹|neon)", "雨夜霓虹"),
    (r"(背影|背对镜头|from behind)[^。\n]{0,20}(望向远方|看向远处|远方|地平线|horizon|distance)", "背影望远"),
    (r"(慢动作|slow motion|slow-mo)[^。\n]{0,30}(泪|哭|拥抱|回头|tear|hug)", "慢动作情绪"),
]
EDIT_TRIGGERS = ["编辑视频", "增加", "加上", "删除", "去掉", "修改", "替换", "改成"]
EXTEND_TRIGGERS = ["向前延长", "向后延长", "延续", "续写", "延长"]
SPEECH_LEAK = [r"说了一句", r"说着[^“\"]*的话", r"低声说.{0,6}[^“\"]", r"says something", r"tells (him|her) that"]

SECTION_ALIASES = {
    "refs": ["【素材绑定】", "REFERENCES"],
    "overview": ["【总述】", "OVERVIEW"],
    "opening": ["【起始状态】", "OPENING STATE"],
    "timeline": ["【分镜时间线】", "TIMELINE"],
    "global": ["【贯穿要求】", "GLOBAL RULES"],
}

ASSET_REF_RE = re.compile(r"(?:@?\[?图片?|@?\[?视频|@?\[?音频|image|img|video|vid|audio|aud)\s*(\d+)\]?", re.I)
ASSET_DECL_RE = re.compile(r"(?:@?图片?|@?视频|@?音频|image|img|video|vid|audio|aud)\s*(\d+)(?:\s*[-–至到]\s*(?:图片?|image|img)?\s*(\d+))?(?=\s*(?:=|＝|:|：|为))", re.I)
# 1.6.0: platform asset names (`@Theo-基础形象：…` declaration lines, `@Theo-基础形象` references) beside the numbered form.
NAME_DECL_RE = re.compile(r"^\s*@(?P<name>[^\s：:=＝，。；、（）()【】\[\]\"“”→@,;!?<>|]+)\s*(?:：|:|=|＝)", re.M)
NAME_REF_RE = re.compile(r"@(?P<name>[^\s：:=＝，。；、（）()【】\[\]\"“”→@,;!?<>|]+)")
NUMBERED_NAME_RE = re.compile(r"^(?:图片?|视频|音频|image|img|video|vid|audio|aud)\s*\d+$", re.I)
KIND_MAP = {"图片": "img", "图": "img", "image": "img", "img": "img", "视频": "vid", "video": "vid",
            "vid": "vid", "音频": "aud", "audio": "aud", "aud": "aud"}
QUOTE_RE = re.compile(r"[“\"]([^”\"]{1,400})[”\"]")


def asset_kind(raw):
    return KIND_MAP.get(re.sub(r"[\d@\s\[\]]", "", raw).lower(), re.sub(r"[\d@\s\[\]]", "", raw).lower())


def resolve_name(name, declared_names):
    """Exact name, else the longest declared name that prefixes it (`@Theo-基础形象的脸` → `@Theo-基础形象`)."""
    if name in declared_names:
        return name
    candidates = [d for d in declared_names if name.startswith(d)]
    return max(candidates, key=len) if candidates else None


def find_section(text, key):
    for alias in SECTION_ALIASES[key]:
        if alias in text:
            return True
    return False


def split_shots(text):
    return [(int(u.ident), u.start, u.end, u.body) for u in Document(text).shots]


def declared_duration(text, override):
    if override is not None:
        value = float(override)
        if not math.isfinite(value):
            raise ValueError("duration must be finite")
        return value
    m = re.search(r"\|\s*duration\s*\|\s*(-?\d+(?:\.\d+)?)\s*\|", text, re.I)
    if m:
        return float(m.group(1))
    # Never take the first incidental reference-video/beat duration.
    m = re.search(r"(?:【总述】|【表演条件】|OVERVIEW[:：]?)\s*([^\n]+)", text, re.I)
    if m:
        number = re.search(r"(\d+(?:\.\d+)?)\s*(?:秒|s\b|-second|second)", m.group(1), re.I)
        if number:
            return float(number.group(1))
    return None


def speech_parameters(text):
    def field(key):
        match = re.search(r"\|\s*" + key + r"\s*\|\s*([^|\n]+)\|", text)
        return match.group(1).strip() if match else None
    density = field("台词密度")
    legacy = field("参数") or ""
    dense = density == "密" if density is not None else bool(
        re.search(r"(?:^|[·/；;、\s])(?:密度\s*)?密(?:$|[·/；;、\s])", legacy))
    # Density changes occupancy, not delivery speed. A dense scene can contain
    # slow lines. Slower or faster rates are explicit E-layer choices.
    # English 3.5 words/s = normal exchange (1.4.0; measured >= 3.6 / 4.1 usable in
    # validation-log D10a/b). 2.5 is the American-English mean [一手] and a floor, not the default.
    defaults = (4.0, 3.5, 0.75 if dense else 2 / 3)
    values = []
    for key, default in zip(("语速字每秒", "语速词每秒", "台词占比上限"), defaults):
        raw = field(key)
        value = float(raw) if raw is not None else default
        if not math.isfinite(value) or value <= 0 or (key == "台词占比上限" and value > 1):
            raise ValueError(f"{key} invalid")
        values.append(value)
    return tuple(values)


def validate(path, duration_override=None, artifact="production", record=None, entry_id=None):
    text = Path(path).read_text(encoding="utf-8")
    metadata_text = text
    if artifact not in {"production", "performance", "raw"}:
        raise ValueError("invalid artifact")
    errors, warns, infos = [], [], []

    def err(code, msg): errors.append(f"{code} {msg}")
    def warn(code, msg): warns.append(f"{code} {msg}")
    def info(msg): infos.append(msg)

    if artifact == "raw":
        raw_errors, fidelity = check_raw(text, entry_id)
        return {"file": str(path), "errors": raw_errors, "warnings": [], "info": [],
                "lens": None, "ext_phrases": {},
                "checks": {"format": "not_applicable", "fidelity": fidelity,
                           "performance": "needs_review", "render": "not_tested"}}
    # Keep E-layer metadata out of observable prose and last shot/beat.
    text = re.split(r"^\|\s*(?:项|参数项)\s*\|", text, maxsplit=1, flags=re.M)[0]
    fields = metadata(metadata_text)
    task = task_type(fields, text) if artifact == "production" else None
    is_edit = task == "edit"
    is_extend = task == "extend"
    is_keyframe = task == "keyframe" or (task is None and bool(re.search(r"关键帧|keyframe", text, re.I)))
    parameter_state = "not_applicable"
    if artifact == "production":
        pe, pw, parameter_state = check_parameters(task, parameters(fields), roles_from_fields(fields))
        errors.extend(pe)
        warns.extend(pw)

    # E01 / E12 / W07 structure
    if artifact == "production" and not find_section(text, "refs"):
        err("E01", "缺少【素材绑定】/REFERENCES 段（无素材也要写「无参考素材」）")
    if artifact == "production" and task not in {"edit", "extend", "transition", "keyframe", "first_last", "motion"} and not is_keyframe and not find_section(text, "opening"):
        err("E12", "缺少【起始状态】/OPENING STATE 段")
    if artifact == "production" and not is_edit and not find_section(text, "global"):
        warn("W07", "缺少【贯穿要求】/GLOBAL RULES 段")
    if artifact == "production" and not re.search(r"不要字幕|无字幕|不额外加入.{0,4}字幕|no subtitles|no captions", text, re.I):
        warn("W07", "未声明字幕负向（建议加「不要字幕」）")
    if artifact == "production" and not re.search(r"bgm|背景音乐|环境音|music|room tone|ambien", text, re.I):
        warn("W07", "未声明声音策略（无 bgm / 只生成环境音 / bgm 描述）")

    # E07 triggers
    if is_edit and not any(t in text for t in EDIT_TRIGGERS):
        err("E07", "编辑任务缺少触发关键词（编辑视频/增加/加上/删除/去掉/修改/替换/改成）")
    if is_extend and not any(t in text for t in EXTEND_TRIGGERS):
        err("E07", "延长任务缺少触发关键词（向前/向后延长、延续、续写）")

    # E08 keyframe first sentence
    if is_keyframe:
        first = text.strip().splitlines()[0] if text.strip() else ""
        if not re.search(r"以图片?\s*\d+(?:(?:\s*[至到\-–、,，]\s*图片?\s*\d+)+)?\s*的顺序作为关键帧", first):
            err("E08", "关键帧任务首句须明确图片编号与顺序（单图或有序多图）")

    # E05 asset refs — numbered (图1 / image1 / @图片1 / @[图片1]) and named (@Theo-基础形象) forms
    refs_block, refs_start, refs_end = "", 0, 0
    for alias in SECTION_ALIASES["refs"]:
        if alias in text:
            start = text.index(alias)
            # The binding section runs to the next section label; inside it every numbered declaration
            # (图1 = …) and every @名 mention counts as a declaration, whether one per line or in prose.
            stop = re.search(r"^\s*(?:【[^】]+】|(?:OVERVIEW|LOOK|EXCLUDE|OPENING STATE|TIMELINE|GLOBAL RULES|AUDIO)\s*:)",
                             text[start + len(alias):], re.M | re.I)
            refs_end = start + len(alias) + (stop.start() if stop else len(text) - start - len(alias))
            refs_block, refs_start = text[start:refs_end], start
            break
    declared_rows = []          # [{"id", "kind", "line", "order"}] in declaration order
    declared = set()            # (kind, n) for numbered assets; ("name", "@名") for named ones
    for m in ASSET_DECL_RE.finditer(refs_block):
        a, b = int(m.group(1)), m.group(2)
        kind = asset_kind(ASSET_REF_RE.match(m.group(0)).group(0))
        line_end = refs_block.find("\n", m.end())
        line = refs_block[m.start(): line_end if line_end > 0 else len(refs_block)]
        for n in (range(a, int(b) + 1) if b else [a]):
            if (kind, n) not in declared:
                declared.add((kind, n))
                declared_rows.append({"id": f"{kind}{n}", "kind": kind, "line": line, "order": m.start()})
    name_lines = {}
    for m in NAME_DECL_RE.finditer(refs_block):          # one declaration per line: `@名：…` / `@名 = …`
        name = m.group("name")
        if NUMBERED_NAME_RE.match(name) or name in name_lines:
            continue
        line_end = refs_block.find("\n", m.end())
        name_lines[name] = (m.start(), refs_block[m.start(): line_end if line_end > 0 else len(refs_block)])
    for m in NAME_REF_RE.finditer(refs_block):           # prose declarations: any other @名 mentioned in the section
        name = m.group("name")
        if NUMBERED_NAME_RE.match(name) or name in name_lines:
            continue
        line_start = refs_block.rfind("\n", 0, m.start()) + 1
        line_end = refs_block.find("\n", m.end())
        name_lines[name] = (m.start(), refs_block[line_start: line_end if line_end > 0 else len(refs_block)])
    for name, (pos, line) in name_lines.items():
        declared.add(("name", "@" + name))
        declared_rows.append({"id": "@" + name, "kind": "name", "order": pos, "line": line})
    declared_rows.sort(key=lambda d: d["order"])
    declared_names = {d["id"][1:] for d in declared_rows if d["kind"] == "name"}
    # The keyframe sentence expresses order, not an upload declaration.
    # Its references must still appear in REFERENCES like all other assets.
    # Cross-references inside the binding section also need declarations.
    used, used_outside, missing_names = set(), {}, []
    for m in ASSET_REF_RE.finditer(text):
        key = (asset_kind(m.group(0)), int(m.group(1)))
        used.add(key)
        if not refs_start <= m.start() < refs_end:
            used_outside.setdefault(f"{key[0]}{key[1]}", m.start())
    for m in NAME_REF_RE.finditer(text):
        name = m.group("name")
        if NUMBERED_NAME_RE.match(name):
            continue
        resolved = resolve_name(name, declared_names)
        if resolved is None:
            if "@" + name not in missing_names:
                missing_names.append("@" + name)
            continue
        used.add(("name", "@" + resolved))
        if not refs_start <= m.start() < refs_end:
            used_outside.setdefault("@" + resolved, m.start())
    missing = sorted(f"{k}{n}" for k, n in used - declared if k != "name") + missing_names
    if missing:
        err("E05", f"引用了未声明的素材：{', '.join(missing)}")
    n_named = sum(1 for d in declared_rows if d["kind"] == "name")
    info(f"素材声明 {len(declared)} 个（编号 {len(declared) - n_named} / @名 {n_named}），正文引用 {len(used_outside)} 个")
    opening_pos = next((text.index(a) for a in SECTION_ALIASES["opening"] if a in text), 0)
    assets_info = {"declared": declared_rows, "used_outside": used_outside, "opening_pos": opening_pos}

    # timestamps
    shots = split_shots(text)
    dur = declared_duration(metadata_text, duration_override)
    if dur is None and isinstance(record, dict) and type(record.get("duration")) in (int, float):
        dur = float(record["duration"])
    if dur is not None and (not math.isfinite(dur) or (not is_edit and (dur <= 0 or dur != int(dur)))):
        err("E04", "总时长必须为正整数秒")
    beats = split_beats(text)
    document = Document(text)
    errors.extend(document.ownership_errors())
    # All declarations refer to the same generated timeline (editing is locked
    # to the input instead). No precedence rule may silently hide a conflict.
    if not is_edit:
        overview_duration = declared_duration(text, None)
        if overview_duration is not None and dur is not None and overview_duration != dur:
            err("E04", "总述与参数/命令行声明的时长不一致")
        if duration_override is not None and fields.get("duration") is not None and float(fields["duration"]) != dur:
            err("E04", "参数表与命令行声明的时长不一致")
    if artifact == "performance" or beats or record is not None:
        errors.extend(timing_errors(beats, dur, shots, complete=artifact == "performance" or not shots))
    if artifact == "performance" and dur is not None and dur > 30:
        err("E06", "clip 总时长 > 30s")
    if shots:
        for no, s, e, _ in shots:
            if s != int(s) or e != int(e):
                err("E02", f"镜头{no} 时间戳非整数秒：{s}-{e}")
            if e <= s:
                err("E03", f"镜头{no} 结束 ≤ 开始：{s}-{e}")
        if shots[0][1] != 0:
            err("E03", f"首镜不从 0 开始（{shots[0][1]}）")
        for (n1, s1, e1, _), (n2, s2, e2, _) in zip(shots, shots[1:]):
            if s2 != e1:
                err("E03", f"镜头{n1}→镜头{n2} 时间不连续：{e1} → {s2}")
        end = shots[-1][2]
        if end > 30:
            err("E06", f"clip 总时长 {end}s > 30s")
        if dur is not None and not is_edit and end != dur:
            err("E04", f"末镜结束 {end}s != 声明时长 {dur}s")
        info(f"镜头数 {len(shots)}，总时长 {end}s")
        # W04 pacing
        short = [no for no, s, e, _ in shots if e - s < 2]
        if short:
            warn("W04", f"单镜 < 2s：镜头 {short}（官方范例最短 2s；审阅该镜是否只承载一个事件 [推论]）")
        if len(shots) > 10 and end <= 30:
            warn("W04", f"30s 内 {len(shots)} 镜 > 10（官方范例 9 镜/30s；审阅每镜是否有信息或节奏理由 [推论]）")
    elif task not in {"edit", "motion", "transition"} and artifact == "production":
        warn("W08", "未识别到「镜头N（a-bs）」格式的分镜段落")

    # Explicit dialogue settings only; emotional intensity is independent.
    ZH_RATE, EN_RATE, SPEECH_CAP = speech_parameters(metadata_text)
    info(f"台词估算 {ZH_RATE:g} 字/s，{EN_RATE:g} 词/s，占比 {SPEECH_CAP:g}（可覆盖的估时假设）")

    # Camera checks remain shot-level; dialogue below uses the smallest timed unit.
    for no, s, e, body in shots:
        head = body[:120]   # 1.7.0: the tag ends with 焦点在 X and may run to 80 characters
        if not re.search(r"【[^】]{2,80}】|\[[^\]]{2,100}\]", head):
            warn("W08", f"镜头{no} 段首缺少【景别，角度，运镜】标注")
        elif not any(w in head for w in SHOT_SIZE_WORDS):
            warn("W08", f"镜头{no} 标注里没有景别词")
        # 去掉与"推门""拉开"等动作误报：只在标注括号内统计
        tag = re.search(r"【([^】]{2,80})】|\[([^\]]{2,100})\]", head)
        tag_txt = (tag.group(1) or tag.group(2)) if tag else ""
        tag_moves = [w for w in CAMERA_MOVES if w in tag_txt]
        if len(tag_moves) > 2:
            warn("W10", f"镜头{no} 标注含多个运镜词 {tag_moves}（核对同步/先后关系与表演可见性，不自动删复合运镜）")
    de, dw, dialogue, total_speech = dialogue_checks(document, dur, (ZH_RATE, EN_RATE, SPEECH_CAP),
                                                    fill=rhythm_settings(metadata_text)["台词填充率"])
    errors.extend(de)
    _rs = rhythm_settings(metadata_text)
    _scene = scene_mode(metadata_text, sum(r["estimate"] for r in dialogue if r["explicit"]),
                        dur if dur is not None else (shots[-1][2] if shots else None), len(shots), _rs)
    if track_mode(metadata_text, _scene) == "连续":
        # A continuous track lets a line run past its window into the next shot; W29 checks the chain.
        dw = [w for w in dw if not (w.startswith("W05") and ("接近或超过窗口" in w or "单元" in w))]
    warns.extend(dw)
    info(f"台词估时 {total_speech:.1f}s")
    # W22-W26 duration / rhythm review hints (lower side of time use; W05 keeps the upper side).
    variation = []
    if artifact == "production" and shots and not is_edit:
        rw, ri, _ = rhythm_checks(shots, dialogue, dur if dur is not None else shots[-1][2], metadata_text)
        warns.extend(rw)
        for line in ri:
            info(line)
        # W30-W33 variation track (both 节奏档 sets): what changes from shot to shot.
        vw, vi, variation = variation_checks(shots, metadata_text)
        warns.extend(vw)
        for line in vi:
            info(line)
        # E23 spatial direction: landmark position and movement both relative to the camera (ERROR by decision).
        se, si = direction_checks(text, shots)
        errors.extend(se)
        for line in si:
            info(line)
        # W35 tone cues: suspense staging (freeze / slow turn / stare + whisper / stateless approach) in a non-suspense scene.
        tw, ti = tone_checks(text, shots, metadata_text)
        warns.extend(tw)
        for line in ti:
            info(line)
        # W36–W41 official-guide FAQ alignment (dialogue tag, audio policy placement, length, asset order, intensity words).
        gw, gi = guide_checks(text, metadata_text, shots, dialogue, assets_info)
        warns.extend(gw)
        for line in gi:
            info(line)
        # 1.7.0: W43 焦点与虚实 (focus_checks), W44 台词括号里的态度没有可执行拍子 (subtext_checks; 1.7.1 任一载体), W45 服装参考与穿着状态
        # (costume_checks). All review hints; E-layer overrides (焦点理由 / 穿着状态说明) documented in duration-rhythm §七.
        fw, fi = focus_checks(text, shots, dialogue, metadata_text)
        warns.extend(fw)
        for line in fi:
            info(line)
        sw, si = subtext_checks(text, shots, dialogue)
        warns.extend(sw)
        for line in si:
            info(line)
        cw, ci = costume_checks(text, shots, assets_info, metadata_text)
        warns.extend(cw)
        for line in ci:
            info(line)
        # 1.9.0: W46-W49 wording executed literally (wording_checks), W51 last-frame continuation replays the previous beat
        # (continuity_checks), W52 behind-camera mentions and single-shot opposite-view scene images (viewpoint_checks).
        for check in (wording_checks, continuity_checks, viewpoint_checks):
            xw, xi = check(text, shots, metadata_text)
            warns.extend(xw)
            for line in xi:
                info(line)
    # Ancillary prose hints inspect complete shots, including beat-external text.
    for no, s, e, body in shots or beats:
        if re.search(r"\d+\s*秒?内.{0,10}\d+\s*次|\d+\s*times? (?:per|in) \d+", body):
            warn("W09", f"镜头{no} 用时间戳控制频次（官方不建议）")
        # Acting quality is a semantic review, never a body-part keyword pass.
        # dialogue
        quotes = QUOTE_RE.findall(body)
        speakers = {row['speaker'] for row in dialogue if row['shot'] == str(no)}
        if quotes:
            if len(speakers) >= 2 and any(not row['explicit'] for row in dialogue if row['shot'] == str(no)):
                warn("W11", f"镜头{no} 有 {len(speakers)} 个说话人（{', '.join(speakers)}），确认不是同框同时说话")
            if not re.search(r"闭着嘴|抿嘴|不出声|嘴[^，。]{0,4}闭|mouth (?:stays )?closed|lips (?:pressed|closed)", body) and len(speakers) >= 1 and re.search(r"[两二]人|B|另一|对方|listener|the other", body):
                warn("W05", f"镜头{no} 有台词但未写非说话者嘴部状态")
        # W19 retired: punctuation cannot infer dramatic intention; W05 occupancy checks remain.
        for pat in SPEECH_LEAK:
            if re.search(pat, body):
                warn("W06", f"镜头{no} 疑似引号外的台词描述（明确逐字台词，避免仅给概述）")
                break

    prose_body = text
    warns.extend(repeated_blocks(beats or shots))

    # W17 同一运镜连续 ≥ 3 镜（只看段首标注）
    tag_moves_seq = []
    for no, s_, e_, body in shots:
        tag = re.search(r"【([^】]{2,80})】|\[([^\]]{2,100})\]", body[:120])
        tag_txt = (tag.group(1) or tag.group(2)) if tag else ""
        mv = next((w for w in ["固定", "locked", "static"] if w in tag_txt), None) or \
             next((w for w in CAMERA_MOVES if w in tag_txt), None)
        tag_moves_seq.append(mv)
    run = 1
    for i in range(1, len(tag_moves_seq)):
        if tag_moves_seq[i] and tag_moves_seq[i] == tag_moves_seq[i - 1]:
            run += 1
            if run == 3 and tag_moves_seq[i] not in ("固定", "locked", "static"):
                warn("W17", f"运镜「{tag_moves_seq[i]}」连续 {run} 镜（审阅是否有意持续；固定机位不计）")
        else:
            run = 1

    # W18 retired: reusable body actions are not prohibited quotations.

    # W13 导演名
    name_prose = re.sub(r'希区柯克变焦|Hitchcock\s+zoom', '', prose_body, flags=re.I)
    hits = [n for n in DIRECTOR_NAMES if re.search(re.escape(n), name_prose, re.I)]
    if hits:
        warn("W13", f"Prompt 正文出现导演/影片人名 {hits}（名字不是可观察量，改写为机位/光/运镜/部位）")

    # W15 反套路
    for pat, label in CLICHE_PATTERNS:
        if re.search(pat, prose_body, re.I):
            warn("W15", f"反套路组合「{label}」（允许，但 QA 里要写一行指回主控句的理由）")

    # W01 negatives（跳过参数表行，只扫 Prompt 正文）
    prose = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))
    seen = set()
    for pat in NEG_PATTERNS:
        for m in re.finditer(pat, prose, re.I):
            frag = m.group(0).strip("，。； \n")
            if not frag or frag in seen:
                continue
            if any(a in frag.lower() for a in NEG_ALLOWED):
                continue
            seen.add(frag)
            warn("W01", f"画面级负向描述「{frag}」（对象排除建议改为正向；行为保持不在此类）")

    # W02 vague
    found = [w for w in VAGUE_WORDS if re.search(re.escape(w), text, re.I)]
    if found:
        warn("W02", f"空泛风格词：{found}（改为可见量：媒介/光/色调/质地）")

    lens = None
    m = re.search(r"\|\s*透镜\s*\|\s*([^|\n]+)\|", metadata_text)
    if m:
        lm = re.search(r"L\d+", m.group(1))
        lens = lm.group(0) if lm else m.group(1).strip()
    fidelity = "not_checked"
    if record is not None:
        fidelity_errors, fidelity = check_record(record, beats, dur)
        errors.extend(fidelity_errors)
    return {"file": str(path), "errors": errors, "warnings": warns, "info": infos, "lens": lens,
            "task": task, "parameters": parameter_state, "dialogue": dialogue, "variation": variation,
            "assets": {"declared": sorted(d["id"] for d in declared_rows),
                       "used": sorted(f"{kind}{n}" if kind != "name" else n for kind, n in used)},
            "fidelity_scope": "original_exact" if record and record.get("mode") == "raw" else "beat_text_only; other prose and source semantics require review" if record else "not_checked",
            "ext_phrases": {},  # retained return key for 2.2 callers; no word-frequency judging
            "checks": {"format": "failed" if any(e.startswith("E") for e in errors) else "passed",
                       "fidelity": fidelity, "performance": "needs_review", "render": "not_tested"}}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--artifact", choices=("production", "performance", "raw"), default="production")
    parser.add_argument("--record", type=Path)
    parser.add_argument("--entry-id", type=int)
    parser.add_argument("--batch", choices=("sequence", "independent"), default="sequence")
    parser.add_argument("--production-record", type=Path, help="actual per-clip assets, parameters and review evidence")
    parser.add_argument("--require-ready", action="store_true", help="require production preflight, not a render-quality claim")
    args = parser.parse_args(argv[1:])
    if args.record and len(args.paths) != 1:
        parser.error("--record applies to exactly one prompt")
    if args.artifact == "raw" and (args.entry_id is None or args.record):
        parser.error("raw requires --entry-id and does not take --record")
    if args.entry_id is not None and args.artifact != "raw":
        parser.error("--entry-id requires --artifact raw")
    if (args.production_record or args.require_ready) and (args.artifact != "production" or len(args.paths) != 1):
        parser.error("production preflight applies to one production prompt")
    if args.require_ready and not args.production_record:
        parser.error("--require-ready requires --production-record")
    try:
        record = json.loads(args.record.read_text(encoding="utf-8")) if args.record else None
        if args.record and not isinstance(record, dict):
            raise ValueError("record must be an object")
        results = [validate(p, args.duration, args.artifact, record, args.entry_id) for p in args.paths]
        if args.production_record:
            from production_preflight import preflight
            results[0]["preflight"] = preflight(args.production_record, Path(args.paths[0]), results[0])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))
    as_json = args.json

    cross = []
    if len(results) > 1 and args.batch == "sequence":
        for a, b in zip(results, results[1:]):
            if a["lens"] and a["lens"] == b["lens"]:
                cross.append(f"W16 相邻 clip 同一主透镜 {a['lens']}：{Path(a['file']).name} → {Path(b['file']).name}")

    if as_json:
        print(json.dumps({"results": results, "cross": cross}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"== validate_prompt: {result['file']}")
            for e in result["errors"]:
                print(f"ERROR {e}")
            for w in result["warnings"]:
                print(f"WARN  {w}")
            for i in result["info"]:
                print(f"INFO  {i}")
            if result["lens"]:
                print(f"INFO  透镜 {result['lens']}")
            print("CHECK " + json.dumps(result["checks"], ensure_ascii=False))
            if "preflight" in result:
                print("PREFLIGHT " + json.dumps(result["preflight"], ensure_ascii=False))
            print(f"== {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)")
        if cross:
            print("== cross-clip")
            for c in cross:
                print(f"WARN  {c}")
    return 1 if any(r["errors"] or (args.require_ready and r.get("preflight", {}).get("status") != "passed") for r in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
