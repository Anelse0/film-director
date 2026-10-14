"""Costume reference vs in-scene wearing state (W45 + INFO), stdlib only — 1.7.0.

An outfit image shows the garment as photographed (the full tuxedo, jacket on); the scene often wears it differently (jacket
off on the stool, sleeves pushed up, coat open, shirt soaked). The binding grammar has two variants: the image-equals-state
one (人物行「X 的衣着一律按 @服装名」, 服装行「X 身上唯一的服装」) and the state-writing one (「X 的衣着一律按每一镜的文字：上身 … 的衬衫，
外套落座时脱下搭在凳上…」, 「X 身上的衬衫与长裤；外套只在开场穿着、之后搭在凳上」). When the wearing state deviates and stays deviated,
the pair of lines for that character should use the second variant, the opening state sits in 【起始状态】 and the 分段状态 in
【贯穿要求】 (S5b §5b.3). That the first variant brings the jacket back is `[推论]`, not a measured mechanism (offset EP05 s03
clip03 r1 rendered the jacket off with the first variant plus a 分段状态; validation-log 待验证 20), so W45 is a risk reminder.
「不参考 X」 is never suggested for a garment that is still on screen.

  W45  服装参考与穿着状态   one per character: a sustained deviation (a state sentence in 【起始状态】 or 【贯穿要求】, or in two or
                            more shots, or a garment removed / absent: 脱下 / 换上 / 只穿 / 尚未穿) attributed to a character whose
                            character line and outfit line(s) both use the image-equals-state wording and none writes a state.
                            Donning / fastening actions (穿上 / 扣上 / 系上) are timeline actions, not deviations.
  INFO 穿着状态              per character: how many transitions, whether 【起始状态】 states the opening state and 【贯穿要求】 the
                            分段状态; state sentences that resolve to nobody; the E-layer `穿着状态说明` row when present.
"""
import re

from guide_checks import section_spans, section_text, is_character
from prompt_structure import SHOT_RE

CJK_NAME = r"[一-鿿]{1,4}"
LATIN_NAME = r"[A-Za-z][A-Za-z0-9'’-]*"

GARMENT_RE = re.compile(
    r"外套|衬衫|领结|领带|袖口|袖子|扣子|纽扣|围裙|帽子|鞋|衣服|上衣|外衣|大衣|衣裙|裙|裤|西装|礼服|毛衣|围巾|手套|夹克|背心|马甲|腰封|浴袍|浴巾|卫衣|T恤"
    r"|\b(?:jacket|shirt|coat|tie|sleeves?|apron|hat|dress|suit|sweater|scarf|gloves?|vest|robe|towel|hoodie)\b", re.I)
DEVIATION_RE = re.compile(
    r"脱下|脱掉|脱了|脱去|脱到|搭在|披在|敞开|敞着|解开|解下|卷起|卷到|挽起|挽到|推上去|往上推|推了一点|换上|换下|摘下|摘掉|湿透|淋湿|弄脏|(?<![一两几])只穿|只剩"
    r"|尚未穿|还没穿|没穿|未穿|不穿|\b(?:takes? off|took off|unbuttons?|unbuttoned|rolls? up|rolled up|drapes?|draped|sleeves (?:pushed|rolled))\b", re.I)
SLEEVE_VERBS = ("卷起", "卷到", "挽起", "挽到", "推上去", "往上推", "推了一点")
ABSENT_RE = re.compile(r"脱|换上|换下|只穿|只剩|尚未穿|还没穿|没穿|未穿|不穿|takes? off|took off", re.I)
# 只穿 / 只剩 followed by the whole outfit (只穿他自己那套 @outfit) restates the image.
WHOLE_OUTFIT_RE = re.compile(r"^[^，。；;\n]{0,12}?(?:@\S|[那这一整全]套|此图|图中|图里)")
PROP_RE = re.compile(r"衣架|挂满|挂着|挂在")
PAIR_DISTANCE = 14
SENTENCE_RE = re.compile(r"[^。；;\n]+")
BRACKET_RE = re.compile(r"台词\s*[（(][^)）\n]*[)）]")
SOUND_CLAUSE_RE = re.compile(r"声音\s*[:：][^。\n]*。?")

ABSOLUTE_RE = re.compile(r"(?:身上)?唯一的?服装|唯一的?服饰|一律按\s*@[^\s，。；、）)]+|全[场程]锁定|完整穿着|全套|整套|按图穿|only outfit|exactly as (?:the )?image", re.I)
GARMENT_RUN_RE = re.compile(r"(?:%s)+" % GARMENT_RE.pattern, re.I)
SCOPED_RE = re.compile(r"只参考|不参考|只穿|本条|从镜|镜(?:头)?\s*\d|开场|起始|尚未|未穿|没穿|脱|敞|解开|解下|卷|挽|换|状态|除了|不含|不包括|每一镜|各镜"
                       r"|按文字|的文字|搭在|披|湿|脏|only the|except|without|ignore", re.I)
CLOTHING_RE = re.compile(r"服装|服饰|衣着|衣服|outfit|wardrobe|clothes", re.I)
SEGMENT_MARK_RE = re.compile(r"镜(?:头)?\s*\d+\s*起|之后|一直|从头到尾|不穿回|全程不|搭在|始终")
OPENING_MARK_RE = re.compile(r"穿在身上|还穿|已经?脱|脱下|敞开|卷|挽|尚未|没穿|未穿|只穿|搭在|披")
STATE_NOTE_RE = re.compile(r"\|\s*穿着状态说明\s*[|｜]\s*([^|\n]+)\|")

NAME_BEFORE_RE = re.compile(
    rf"(?<![A-Za-z0-9_一-鿿])(?P<name>{LATIN_NAME}|{CJK_NAME})\s*(?:（[^）]*）|\([^)]*\))?\s*"
    r"(?:的人物参考|的人物|的外观|外观|的衣着|的服装|的服饰|的形象|身上)")
NAME_PREFIX_RE = re.compile(r"@(?P<name>[^\s：:=＝，。；、（）()【】\[\]\"“”→@,;!?<>|-]+)-基础形象")
PLAIN_ID_RE = re.compile(r"^[A-Za-z][A-Za-z'’-]{0,19}$")
NOT_NAMES = {"他", "她", "它", "人物", "角色", "图", "图片", "两人", "此人", "本人", "各自", "其中", "该", "此图", "图中", "的", "人"}
NEXT_DECL_RE = re.compile(r"[；;。]\s*(?:@?图片?|@?视频|@?音频|image|img|video|vid|audio|aud)\s*\d+(?:\s*[-–至到]\s*\d+)?\s*(?:=|＝|:|：|为)", re.I)
STATE_SECTIONS = ("起始状态", "分镜", "贯穿要求")


# ---------- names and binding lines ----------

def declared_names(declared):
    names = []
    for d in declared:
        line = d.get("line", "")
        found = [m.group("name") for m in NAME_BEFORE_RE.finditer(line)] + [m.group("name") for m in NAME_PREFIX_RE.finditer(line)]
        ident = d.get("id", "")
        if ident.startswith("@") and PLAIN_ID_RE.match(ident[1:]):
            found.append(ident[1:])
        for name in found:
            name = name.lstrip("的").strip()
            if name and name not in NOT_NAMES and not re.fullmatch(r"\d+", name) and name not in names:
                names.append(name)
    return names


def name_pattern(name):
    if re.match(r"[A-Za-z]", name):
        return re.compile(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])")
    return re.compile(re.escape(name))


def declaration_segment(line):
    """A numbered declaration line holds every later declaration too (图1 = …；图2 = …); keep this entry's own part."""
    line = line.strip()
    m = NEXT_DECL_RE.search(line, 1)
    return line[:m.start()] if m else line


def bound_names(ident, segment, names):
    """The characters a binding line is about: names in the line (an identity prefix such as 「Theo 的经纪人 Jo」 binds Jo,
    the name right before 的人物参考 / 身上), and the id stem (@05_Rhett_outfit → Rhett)."""
    found = []
    for m in NAME_BEFORE_RE.finditer(segment):
        if m.group("name") in names and m.group("name") not in found:
            found.append(m.group("name"))
    if not found:
        for name in names:
            if name_pattern(name).search(segment) and name not in found:
                found.append(name)
    stem = re.sub(r"^@\d+_", "@", ident)
    stem = re.split(r"[-_]", stem.lstrip("@"))[0]
    if stem in names and stem not in found:
        found.append(stem)
    return found


def clothing_clauses(segment):
    return [s for s in SENTENCE_RE.findall(segment) if CLOTHING_RE.search(s) or GARMENT_RE.search(s)]


def line_variant(segment):
    """'scoped' when a clothing clause writes a state or a scope; 'absolute' when one matches the image-equals-state wording;
    otherwise None (the line says nothing about clothing)."""
    clothes = clothing_clauses(segment)
    if not clothes:
        return None, None
    if any(SCOPED_RE.search(s) for s in clothes):
        return "scoped", None
    for s in clothes:
        m = ABSOLUTE_RE.search(s)
        if m:
            return "absolute", m.group(0).strip()
    return None, None


def pairs(declared, names):
    """{name: {"absolute": [(id, phrase)], "scoped": [id]}} over character and outfit lines."""
    table = {n: {"absolute": [], "scoped": []} for n in names}
    for d in declared:
        segment = declaration_segment(d.get("line", ""))
        if not (is_character(segment) or CLOTHING_RE.search(segment) or GARMENT_RE.search(segment)):
            continue
        variant, phrase = line_variant(segment)
        if not variant:
            continue
        for name in bound_names(d.get("id", ""), segment, names):
            table[name][variant].append((d.get("id", ""), phrase) if variant == "absolute" else d.get("id", ""))
    return table


# ---------- wearing-state sentences ----------

def state_pair(sentence):
    """(verb_match, garment_match) for the first deviation verb within PAIR_DISTANCE of a garment noun, else None."""
    garments = list(GARMENT_RE.finditer(sentence))
    if not garments:
        return None
    for v in sorted(DEVIATION_RE.finditer(sentence), key=lambda m: m.start()):
        verb = v.group(0)
        if verb in ("只穿", "只剩") and WHOLE_OUTFIT_RE.match(sentence[v.end():]):
            continue
        if verb in SLEEVE_VERBS and not re.search(r"袖", sentence[max(0, v.start() - 6):v.end() + 6]):
            continue
        nearest = None
        for g in garments:
            gap = max(g.start() - v.end(), v.start() - g.end(), 0)
            if gap <= PAIR_DISTANCE and (nearest is None or gap < nearest[0]):
                nearest = (gap, g)
        if nearest:
            return v, nearest[1]
    return None


def state_sentences(text, shots, names):
    """[{"where", "phrase", "subject", "section", "shot", "verb"}] in document order."""
    headers = [(int(m.group(1)), m.start()) for m in SHOT_RE.finditer(text)]
    known = {no for no, _, _, _ in shots}
    found = []
    for label, start, end in section_spans(text):
        if label not in STATE_SECTIONS:
            continue
        chunk = text[start:end]
        for s in SENTENCE_RE.finditer(chunk):
            sentence = SOUND_CLAUSE_RE.sub("", BRACKET_RE.sub("", s.group(0)))
            if PROP_RE.search(sentence):          # a garment on a rack is a prop, not a wearing state
                continue
            pair = state_pair(sentence)
            if not pair:
                continue
            verb, garment = pair
            lo, hi = min(verb.start(), garment.start()), max(verb.end(), garment.end())
            garments = list(GARMENT_RE.finditer(sentence))
            for g in garments:                          # 礼服外套 / 礼服衬衫: take the whole run of garment nouns
                if g.start() == hi:
                    hi = g.end()
            for g in reversed(garments):
                if g.end() == lo:
                    lo = g.start()
            phrase = sentence[lo:hi].strip()[:24]
            abs_start = start + s.start()
            shot = None
            if label == "分镜":
                for no, pos in headers:
                    if pos <= abs_start and no in known:
                        shot = no
            where = f"镜头{shot}" if shot is not None else {"起始状态": "【起始状态】", "贯穿要求": "【贯穿要求】"}.get(label, label)
            best = None
            for name in names:
                m = name_pattern(name).search(sentence)
                if m and (best is None or m.start() < best[0]):
                    best = (m.start(), name)
            subject = best[1] if best else None
            if subject is None:
                paragraph = text[text.rfind("\n", 0, abs_start) + 1:abs_start]
                last = None
                for name in names:
                    for m in name_pattern(name).finditer(paragraph):
                        if last is None or m.start() > last[0]:
                            last = (m.start(), name)
                subject = last[1] if last else None
            found.append({"where": where, "phrase": phrase, "subject": subject, "section": label, "shot": shot, "verb": verb.group(0)})
    return found


def sustained(states):
    shots = {s["shot"] for s in states if s["shot"] is not None}
    return any(s["section"] in ("起始状态", "贯穿要求") or ABSENT_RE.search(s["verb"]) for s in states) or len(shots) >= 2


def opening_state_written(text):
    for sentence in SENTENCE_RE.findall(section_text(text, "起始状态")):
        if GARMENT_RE.search(sentence) and OPENING_MARK_RE.search(sentence):
            return True
    return False


def segmented_state_written(text):
    for sentence in SENTENCE_RE.findall(section_text(text, "贯穿要求")):
        garments = list(GARMENT_RE.finditer(sentence))
        if not garments or not (DEVIATION_RE.search(sentence) or "搭在" in sentence):
            continue
        for m in SEGMENT_MARK_RE.finditer(sentence):
            if any(max(g.start() - m.end(), m.start() - g.end(), 0) <= PAIR_DISTANCE * 2 for g in garments):
                return True
    return False


# ---------- entry ----------

def costume_checks(text, shots, assets, metadata_text=""):
    """Return (warnings, infos).

    text: D-layer body (E table stripped); shots: validate_prompt.split_shots(); assets: {"declared": [{"id", "kind", "line",
    "order"}], …}; metadata_text: whole file (E-layer `穿着状态说明`)."""
    warns, infos = [], []
    declared = assets.get("declared", []) if assets else []
    names = declared_names(declared)
    states = state_sentences(text, shots, names)
    if not states:
        return warns, infos
    note = STATE_NOTE_RE.search(metadata_text or "")
    table = pairs(declared, names)
    opening, segmented = opening_state_written(text), segmented_state_written(text)
    by_subject = {}
    for s in states:
        by_subject.setdefault(s["subject"], []).append(s)
    for subject, rows in by_subject.items():
        unique, seen = [], set()
        for s in rows:                       # one transition per garment + verb (镜头1 脱下礼服外套 = 【贯穿要求】 礼服外套脱下)
            run = GARMENT_RUN_RE.search(s["phrase"])
            key = (run.group(0) if run else s["phrase"][:8], s["verb"])
            if key not in seen:
                seen.add(key)
                unique.append(s)
        listed = "、".join(f"{u['where']}「{u['phrase']}」" for u in unique[:3]) + ("…" if len(unique) > 3 else "")
        if subject is None:
            infos.append(f"穿着状态：{len(unique)} 处状态句归不到人物（{listed}）——句子里写明是谁的衣服")
            continue
        pair = table.get(subject, {"absolute": [], "scoped": []})
        infos.append(f"穿着状态：{subject} {len(unique)} 处变化（{listed}）；【起始状态】{'已' if opening else '未'}写开场状态；"
                     f"【贯穿要求】{'已' if segmented else '未'}写分段状态")
        if note or not pair["absolute"] or pair["scoped"] or not sustained(rows):
            continue
        lines = "、".join(f"{ident}「{phrase}」" for ident, phrase in pair["absolute"])
        garment = GARMENT_RUN_RE.search(unique[0]["phrase"])
        garment = garment.group(0) if garment else "外套"
        warns.append(f"W45 {subject} 的穿着状态与服装图不同（{listed}），而绑定行是图 = 状态的写法（{lines}）：改用写状态的写法——"
                     f"人物行「{subject} 的衣着一律按每一镜的文字：上身 @服装名 的衬衫，{garment}{unique[0]['verb']}…，下身 @服装名 的长裤」，"
                     f"服装行「@服装名：{subject} 身上的衬衫与长裤；{garment} 只在开场穿着、之后搭在一旁」；【起始状态】写开场状态，"
                     f"【贯穿要求】写分段状态（镜 N 起 …，不穿回）；「不参考 X」只用于本条从不出现的衣物；可选另出一张该状态的服装图"
                     f"（S5b §5b.3）；E 层 穿着状态说明 写明理由可保留")
    if note:
        infos.append(f"穿着状态：E 层 穿着状态说明 已写明（{note.group(1).strip()[:40]}），W45 不报")
    return warns, infos
