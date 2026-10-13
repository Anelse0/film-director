"""Official-guide alignment checks (W36–W41 + INFO), from the 70-page edition of the Doubao Seedance 2.5
提示词指南 (2026-10, 常见问题 section) — references/seedance-2.5-capabilities.md §8.

Every item here is a review hint derived from an `[官方]` FAQ entry; none is a format fact, so none is an ERROR.

  W36  台词后语气括号 / 复述片段   FAQ 字幕约束不生效: tone / voice / action notes appended after a line, or
                                    fragments of the line quoted again after it, induce subtitles. Write the delivery
                                    note before the colon: 台词（角色，a-bs，语言，语气）："…".
  W37  声音策略位置与同义词         FAQ 背景音乐约束不生效: state the audio policy at the start and the end, and
                                    enumerate music synonyms (音乐、背景音乐、BGM、配乐、器乐、旋律、铺底音).
  W38  篇幅                         API doc recommends ≤500 Chinese characters / ≤1000 English words; the longest
                                    official example is about 1,300 characters. INFO always; WARN above the budget
                                    (default 3,000 CJK / 6,000 EN words, E-layer `字数上限` / `词数上限` override).
                                    The trim order never names performance; performance is translated, never cut.
  W39  素材顺序                     FAQ 角色对应错误: character assets in first-appearance order; the E-layer
                                    `上传与角色` row in the same order as 【素材绑定】.
  W40  强情绪词                     FAQ 情绪过度响应（眼睛发光）: 狂热 / 极度 … → ordinary descriptions; guard line
                                    人物为正常人眼，不发光 for strong beats (INFO when missing).
  W41  声明未引用                   An image / video asset or @名 declared in 【素材绑定】 but never referenced in the body.
  INFO 水 / 浪 / 回音               FAQ 音频出现水波纹噪声: water / wave / echo descriptions beside dialogue.
"""
import re

from prompt_structure import SPEECH_RE

CJK = re.compile(r"[一-鿿]")
EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
SECTION_LABELS = [
    ("素材绑定", ("【素材绑定】", "REFERENCES")), ("总述", ("【总述】", "OVERVIEW")), ("画面基调", ("【画面基调】", "LOOK")),
    ("严格排除", ("【严格排除】", "EXCLUDE")), ("起始状态", ("【起始状态】", "OPENING STATE")),
    ("分镜", ("【分镜时间线】", "TIMELINE")), ("贯穿要求", ("【贯穿要求】", "GLOBAL RULES")),
]
# User decisions 2026-10-13: first budget 2,000 / 4,000 (4× the official recommendation, the guide's own 500 字 : 1000 词
# ratio); raised to 3,000 / 6,000 the same day because the agent was still trimming performance to chase the number.
# The budget is a review threshold, never a target: the INFO line states it without the official figure.
CJK_LIMIT, EN_LIMIT = 3000, 6000
OFFICIAL_NOTE = "官方建议 ≤500 字 / ≤1000 词，官方最长范例约 1300 字"

POST_QUOTE_RE = re.compile(r"[\"”]\s*[（(]([^）)\n]{1,120})[）)]")
POST_QUOTE_OK = re.compile(r"^\s*(?:画外|off[- ]screen|V\.?O\.?|英语|中文(?:普通话)?|日语|韩语|English|Mandarin)\s*$", re.I)
QUOTED_TOKEN_RE = re.compile(r"[“\"「]([^”\"」\n]{1,40})[”\"」]")

POLICY_RE = re.compile(r"无\s*bgm|没有\s*bgm|不要\s*bgm|无背景音乐|不要背景音乐|不加背景音乐|不生成背景音乐|只生成环境音|只有环境音|只保留环境音"
                       r"|不要任何声音|不加音乐|无音乐|no (?:background )?music|no bgm|no score|only (?:room tone|ambien)", re.I)
MUSIC_SYNONYMS = ["背景音乐", "bgm", "配乐", "器乐", "旋律", "铺底", "合成器", "音乐", "music", "score", "soundtrack",
                  "instrumental", "melody", "pad", "drone"]

INTENSITY_RE = re.compile(r"极度|狂热|疯狂|歇斯底里|惊骇|崩溃|暴怒|狂怒|癫狂|狂喜|发狂|眼睛(?:发光|放光|冒光|发亮)|瞳孔(?:发光|冒光)"
                          r"|目光如炬|眼里(?:燃|烧|冒火)|眼神(?:炽热|灼人|如刀)|杀气|frenz|manic|hysteric|glowing eyes|eyes glow", re.I)
STRONG_BEAT_RE = re.compile(r"泪|哭|怒|惊|恐|吓|崩|吼|颤|震|tear|cry|rage|terror|shock|scream", re.I)
GUARD_RE = re.compile(r"不发光|正常人眼|不要发光|normal (?:human )?eyes|no glow", re.I)
WATER_RE = re.compile(r"海浪|浪声|浪花|水声|流水|瀑布|回音|回声|泉水|水花|溪流|雨声|浪涌|涌上来|\bwaves?\b|\becho\b|waterfall|\brain\b", re.I)

CHARACTER_WORDS = re.compile(r"人物|角色|外观|面部|发型|脸|character|face|appearance|actor", re.I)
NOT_CHARACTER_WORDS = re.compile(r"服装|服饰|衣着|outfit|wardrobe|场景|空间|空镜|scene|车|道具|prop|音色|voice|音频|audio|音乐|music|白模|关键帧|分镜|故事板|storyboard|keyframe", re.I)
UPLOAD_ROW_RE = re.compile(r"\|\s*(?:上传与角色|上传顺序|upload order)\s*\|\s*([^|\n]+)\|", re.I)
NAME_TOKEN_RE = re.compile(r"@(?P<name>[^\s：:=＝，。；、（）()【】\[\]\"“”→@,;!?<>|]+)")
NUMBERED_TOKEN_RE = re.compile(r"(?:@?\[?(?:图片?|视频|音频|image|img|video|vid|audio|aud)\s*(\d+)\]?)", re.I)
KIND_MAP = {"图片": "img", "图": "img", "image": "img", "img": "img", "视频": "vid", "video": "vid", "vid": "vid",
            "音频": "aud", "audio": "aud", "aud": "aud"}


def section_spans(text):
    """[(label, start, end)] for the sections present, in document order."""
    found = []
    for label, aliases in SECTION_LABELS:
        for alias in aliases:
            pos = text.find(alias)
            if pos >= 0:
                found.append((label, pos))
                break
    found.sort(key=lambda x: x[1])
    spans = []
    for i, (label, start) in enumerate(found):
        end = found[i + 1][1] if i + 1 < len(found) else len(text)
        spans.append((label, start, end))
    return spans


def section_text(text, label):
    for name, start, end in section_spans(text):
        if name == label:
            return text[start:end]
    return ""


def length_profile(text):
    cjk = len(CJK.findall(text))
    words = len(EN_WORD.findall(text))
    per = []
    for label, start, end in section_spans(text):
        chunk = text[start:end]
        per.append((label, len(CJK.findall(chunk)), len(EN_WORD.findall(chunk))))
    return cjk, words, per


def limits(metadata_text):
    cjk, words = CJK_LIMIT, EN_LIMIT
    m = re.search(r"\|\s*字数上限\s*\|\s*(\d+)\s*\|", metadata_text)
    if m:
        cjk = int(m.group(1))
    m = re.search(r"\|\s*词数上限\s*\|\s*(\d+)\s*\|", metadata_text)
    if m:
        words = int(m.group(1))
    return cjk, words


def upload_order(metadata_text):
    """Asset ids in the order the E-layer 上传与角色 row lists them ('@名' or 'img1').

    A row that maps numbers to names (`img1 = @A, img2 = @B`) yields the names only: the names are what a
    name-bound prompt declares, the numbers are the platform mapping."""
    m = UPLOAD_ROW_RE.search(metadata_text)
    if not m:
        return []
    names, numbers = [], []
    for token in re.finditer(rf"{NAME_TOKEN_RE.pattern}|{NUMBERED_TOKEN_RE.pattern}", m.group(1), re.I):
        if token.group("name"):
            name = token.group("name")
            if not re.fullmatch(r"(?:图片?|视频|音频|image|img|video|vid|audio|aud)\s*\d+", name, re.I):
                if "@" + name not in names:
                    names.append("@" + name)
                continue
            raw = name
        else:
            raw = token.group(0)
        kind = re.sub(r"[\d@\s\[\]]", "", raw).lower()
        number = re.search(r"\d+", raw).group(0)
        ident = f"{KIND_MAP.get(kind, kind)}{int(number)}"
        if ident not in numbers:
            numbers.append(ident)
    return names or numbers


def is_character(declaration):
    return bool(CHARACTER_WORDS.search(declaration)) and not NOT_CHARACTER_WORDS.search(
        re.sub(r"的衣着一律按[^。；\n]*", "", declaration))


# ---------- individual checks ----------

def post_quote_notes(text):
    hits = []
    for m in POST_QUOTE_RE.finditer(text):
        note = m.group(1).strip()
        if POST_QUOTE_OK.match(note):
            continue
        hits.append(note[:30])
    return hits


def requoted_fragments(text):
    hits = []
    for m in SPEECH_RE.finditer(text):
        line = m.group("line").strip()
        if len(line) < 2:
            continue
        window_end = text.find("\n", m.end())
        window = text[m.end(): window_end if window_end > 0 else m.end() + 200][:200]
        for q in QUOTED_TOKEN_RE.finditer(window):
            frag = q.group(1).strip()
            # The FAQ's own bad case re-quotes a single character ("像" 后短暂停顿); the window is the rest of the
            # same paragraph, which keeps unrelated quotations out.
            if frag and frag != line and frag in line and (CJK.search(frag) or len(frag) >= 3):
                hits.append(frag[:20])
    return hits


def audio_policy(text):
    """(front, end, synonyms) — policy before the timeline, policy in the closing section, synonym count there."""
    spans = {label: (s, e) for label, s, e in section_spans(text)}
    positions = [m.start() for m in POLICY_RE.finditer(text)]
    if not positions:
        return None
    timeline_start = spans.get("分镜", (len(text), len(text)))[0]
    closing = spans.get("贯穿要求")
    front = any(p < timeline_start for p in positions)
    end = bool(closing) and any(closing[0] <= p < closing[1] for p in positions)
    closing_text = text[closing[0]:closing[1]].lower() if closing else ""
    synonyms = sum(1 for s in MUSIC_SYNONYMS if s.lower() in closing_text)
    return front, end, synonyms


def intensity_words(text):
    excluded = section_text(text, "严格排除")
    body = text.replace(excluded, "") if excluded else text
    return list(dict.fromkeys(m.group(0) for m in INTENSITY_RE.finditer(body)))


def guide_checks(text, metadata_text, shots, dialogue, assets):
    """Return (warnings, infos).

    text: D-layer body (E table stripped); metadata_text: whole file; shots: validate_prompt.split_shots();
    dialogue: rows from dialogue_checks; assets: {"declared": [{"id", "kind", "line", "order"}], "used_outside": {id: pos},
    "opening_pos": int}.
    """
    warns, infos = [], []

    # W36 delivery notes after the quote / re-quoted fragments
    notes = post_quote_notes(text)
    if notes:
        warns.append(f"W36 台词引号后追加语气 / 音色 / 动作括号 {len(notes)} 处（如「{notes[0]}」）：官方 FAQ 字幕约束不生效——"
                     f"台词后复述词语并追加语气、表情、动作描述会诱发字幕；写到冒号前：台词（角色，a-bs，语言，语气 / 音量 / 语速）：\"…\"，"
                     f"引号后只接「；此时 B 闭着嘴」")
    frags = requoted_fragments(text)
    if frags:
        warns.append(f"W36 台词之后复述了台词片段「{frags[0]}」等 {len(frags)} 处：官方 FAQ 字幕约束不生效——"
                     f"不同片段的语气差异用「角色台词（情绪）：内容」分行写，不在台词后再引用词语")

    # W37 audio policy placement and synonyms
    policy = audio_policy(text)
    if policy is not None:
        front, end, synonyms = policy
        if not (front and end):
            where = "只写在结尾" if end else ("只写在开头" if front else "不在开头也不在【贯穿要求】")
            warns.append(f"W37 声音策略{where}：官方 FAQ 背景音乐约束不生效——音频约束在开头（【总述】末尾一句）与结尾（【贯穿要求】）各写一遍")
        if end and synonyms < 3:
            warns.append(f"W37 【贯穿要求】的声音策略只列了 {synonyms} 个音乐类词：官方 FAQ 要一次性穷举同义词"
                         f"（音乐、背景音乐、BGM、配乐、器乐、旋律、铺底音至少三种），避免模型换个说法绕过约束")

    # W38 length budget
    cjk, words, per = length_profile(text)
    cjk_limit, en_limit = limits(metadata_text)
    breakdown = " · ".join(f"{label} {c if c else w}{'字' if c else '词'}" for label, c, w in per)
    infos.append(f"篇幅：中文 {cjk} 字 / 英文 {words} 词（{breakdown}）；预算 {cjk_limit} 字 / {en_limit} 词（W38 阈值，不是目标；表演不为篇幅删）")
    over_cjk = cjk > cjk_limit and cjk >= words
    over_en = words > en_limit and words > cjk
    if over_cjk or over_en:
        measure = f"中文 {cjk} 字 > {cjk_limit}" if over_cjk else f"英文 {words} 词 > {en_limit}"
        warns.append(f"W38 篇幅 {measure}（{OFFICIAL_NOTE}）：先删 变化字段 → 引号后的语气括号 → 图里已有的外观复述 → 逐镜重复的光与机位；"
                     f"不删 人物一致性、表演约束、声音要求、画面基调，表演只翻译不删不缩写（S4 §4.4c）；写明理由可在 E 层 `字数上限` / `词数上限` 放宽")

    # W39 asset order: characters by first appearance; E-layer upload row = declaration order
    declared = assets.get("declared", [])
    used_outside = assets.get("used_outside", {})
    characters = [d for d in declared if d["kind"] in ("img", "name") and is_character(d["line"])]
    opening_pos = assets.get("opening_pos", 0)
    appearances = [(used_outside.get(d["id"], float("inf")), d["id"]) for d in characters if d["id"] in used_outside]
    appeared = [i for _, i in sorted(appearances)]
    declared_chars = [d["id"] for d in characters if d["id"] in used_outside]
    if len(appeared) >= 2 and appeared != declared_chars:
        warns.append(f"W39 角色素材顺序与首次出场顺序不一致：声明 {declared_chars}，出场 {appeared}"
                     f"（官方 FAQ 角色对应错误：按人物首次出场顺序上传并同步编号）")
    order = upload_order(metadata_text)
    if order:
        named = order[0].startswith("@")
        declared_ids = [d["id"] for d in declared if d["id"].startswith("@") == named]
        if declared_ids and order != declared_ids:
            warns.append(f"W39 E 层 上传与角色 顺序 {order} 与【素材绑定】顺序 {declared_ids} 不一致（编号 = 上传顺序）")

    # W40 intensity labels; INFO guard line
    labels = intensity_words(text)
    if labels:
        warns.append(f"W40 强情绪词 {labels}：官方 FAQ 情绪过度响应——强烈情绪词会把情绪渲染成眼睛发光等特效；"
                     f"改为常规描述（惊叹、看着不动、眼睛睁大一点），情绪写进眼神落点、部位先后与动作")
    if STRONG_BEAT_RE.search(section_text(text, "分镜")) and not GUARD_RE.search(text):
        infos.append("强情绪镜：官方 FAQ 建议在最高优先级写一句「人物为正常人眼，不发光」（放【总述】或【贯穿要求】）")

    # INFO water / echo beside dialogue
    if dialogue and WATER_RE.search(text):
        infos.append("官方 FAQ：水 / 浪 / 回音描述可能引入水波纹噪声（冒泡、回音、啸叫）；台词段里按需减少，或放到无台词段")

    # W41 declared but unused (images, videos, @名)
    unused = [d["id"] for d in declared if d["kind"] in ("img", "vid", "name") and d["id"] not in used_outside]
    if unused:
        warns.append(f"W41 素材 {unused} 已声明但正文未引用：写到该人物 / 场景的段落挂上它，或不上传")
    return warns, infos
