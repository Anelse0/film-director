"""Wardrobe per character, per shot (film-director 1.10.0, hard rule 21). Presence checks, not a costume judge.

Who is checked
  (a) characters bound to an appearance image in 【素材绑定】/REFERENCES — `图N` / `@名字` / `ImageN` lines that
      say 外观 / 形象 / 面部 / 人物参考 / appearance / face (scene, prop, keyframe and outfit lines are not);
  (b) characters with their own appearance lock in 【贯穿要求】/GLOBAL RULES ("名字：三十岁左右男性，…"), which is
      how a text-only (T1) Prompt names them.
  Extras without an appearance image or lock (群演) may be written collectively and are not checked.

E23  an appearance-image line does not state, in positive words, where this clip's wardrobe comes from. One of:
       衣着一律按 @服装图 · 参考面部、发型与图中衣服：{衣物} · 衣着一律按每一镜的文字：{衣物}
     (also accepted: "A身穿@服装图" outside a 不参考 clause, or an outfit line that names A: "图2 = A 的礼服").
     "不参考图中白色 polo" alone, or nothing at all, leaves the image's clothes in play (2026-09-23 THE ORDER EP03
     s04; 2026-09-24 set scene v4: both rendered in the image's clothes). Also E23: one line gives two sources
     (image clothes and an outfit image).
W36  in 【起始状态】, a shot, or 【贯穿要求】, a checked character's first appearance carries no wardrobe (an outfit
     image reference, "身穿图中的…", or garment / wearing words in the same clause) — monitor and
     picture-in-picture appearances included; a numeric collective ("两人 / 两位演员 / 三人") stands in for more
     checked characters than the unit names individually; a shot dresses a character in an outfit image while
     the binding says the image's own clothes; 【贯穿要求】 omits a checked character's wardrobe.
     Not counted as an appearance: 【…】/【变化…】 annotations, 〔…〕 acting labels, quoted text (dialogue, signs),
     台词（…画外…） labels, a name followed by 在画外 /
     出画 / 的声音, a name that is only a gaze target (看向画左的 X / 抬眼看 X).
     Known misses: a garment that is a prop in the same clause (接过浴袍); a collective whose number happens to
     match the characters named; a character with neither an appearance image nor an appearance lock.
W37  (1.11.0, user decision 2026-09-25) default: the appearance image gives face and hair only; wardrobe follows the
     outfit image, or per-shot text when there is none. A character whose binding keeps the appearance image's own
     clothes ("参考面部、发型与图中衣服" / "造型参考（含衣物）") needs the user's say-so recorded in the E-layer row
     `| 衣着来源 | Theo：形象图中的衣服（用户指定） |` (the row stays out of the model's prompt). Missing → W37.
Whether the wardrobe is the right one, and whether a change of clothes is continuous, is S7 review.
"""
import re

from prompt_structure import Document

SECTION_RE = re.compile(r"^\s*(?:【[^】]+】|(?:REFERENCES|OVERVIEW|LOOK|EXCLUDE|OPENING STATE|TIMELINE|GLOBAL RULES|AUDIO)\s*[:：])",
                        re.M | re.I)
SECTIONS = {
    "refs": ("【素材绑定】", "REFERENCES:", "REFERENCES："),
    "opening": ("【起始状态】", "OPENING STATE:", "OPENING STATE："),
    "global": ("【贯穿要求】", "GLOBAL RULES:", "GLOBAL RULES："),
}
# A declaration starts a line or follows ；。; — never inside an entry's prose.
# Several assets may share one line: "@A_front @A_side = …", "图1-2 = …", "img1-2 是人物 1" (official example).
_ONE = r"(?:@?图片?\s*\d+|@?视频\s*\d+|@?音频\s*\d+|Image\s*\d+|Video\s*\d+|Audio\s*\d+|img\s*\d+|@[^\s=＝:：@；;。\n][^=＝:：@；;。\n]*?)"
DECL_RE = re.compile(
    r"(?:^|(?<=[；;。.]))[ \t]*(?P<tok>" + _ONE + r"(?:\s*[-–至到、,，]\s*(?:图片?|img|Image)?\s*\d+|[ \t、，,]+" + _ONE + r")*)"
    r"\s*(?:[=＝:：]|为|是)", re.M | re.I)
NOT_REFERENCED = re.compile(r"(?:不参考|不采用|不要参考|ignore|do not use|not referenc\w*)[^；;。\n]*", re.I)
FACE = re.compile(r"形象|面部|长相|发型|appearance|\bface\b", re.I)
CHARACTER = re.compile(r"人物|角色|主体参考|演员", re.I)
# "外观" alone also describes places and objects ("采访席区域外观"); it marks a character only next to a person word.
LOOKS_OF_PERSON = re.compile(r"外观.{0,20}?(?:人|男|女|演员|主角|母|父|妻|夫|儿|哥|姐|弟|妹|爷|奶|岁|发|脸|体态|身形)|"
                             r"(?:人|男|女|演员|主角|母|父|妻|夫|儿|哥|姐|弟|妹|爷|奶|[A-Za-z]{2,})\s*的?\s*外观")
NOT_CHARACTER = re.compile(r"场景|空镜|布景|布局|地点|房间|街道|建筑|道具|车身|车辆|关键帧|首帧|尾帧|故事板|分镜|白模|宫格|"
                           r"\bscene\b|\blocation\b|\bprop\b|\bvehicle\b|\bcar\b|keyframe|storyboard|first frame|last frame",
                           re.I)
OUTFIT = re.compile(r"服装|服饰|戏服|衣着|队服|校服|制服|球衣|球服|礼服|便装|常服|outfit|wardrobe|costume|clothing", re.I)
MEDIA = re.compile(r"^@?(?:视频|音频|video|audio)", re.I)
GARMENT = (r"(?:衣|衫|裤|裙|袍|褂|外套|夹克|西装|制服|队服|校服|球服|礼服|便服|常服|工服|浴巾|背心|T\s*恤|polo|毛衣|卫衣|"
           r"大衣|风衣|戏服|帽|头盔|护胸|护腿|护具|鞋|靴|围巾|领带|"
           r"服装(?!助理|师|组|间)|服饰|衣着|\bshirt|\bjacket|\bcoat\b|sweater|hoodie|\bdress\b|uniform|\brobe\b|towel|"
           r"jeans|trousers|\bpants\b|skirt|\bsuit\b|jersey|t-shirt|outfit|wardrobe|clothes|clothing)")
WEARING = re.compile(r"身穿|穿着|穿上|穿了|穿一|穿的|换上|赤裸|裸着|裸露|光着|赤膊|只围|围着|套着|披着|"
                     r"shirtless|bare-chested|topless|wearing|wears|dressed|" + GARMENT, re.I)
# Positive statements of where the wardrobe comes from.
SOURCE = [
    re.compile(r"(?:衣着|服装|服饰|着装|衣服|穿着)[^；;。\n]{0,8}?(?:按|依|以|穿|用|为|见|跟|照)", re.I),
    re.compile(r"(?:衣着|着装|服装)\s*[:：]"),
    re.compile(r"(?<!不)参考(?:(?!不参考|不采用)[^；;。\n])*?" + GARMENT, re.I),
    re.compile(r"(?:本条|全程|这一条)[^；;。\n]{0,10}?(?:身穿|穿着|穿|换上|裹着|套着|披着|围着|赤裸|光着)"),
    re.compile(r"(?:造型|穿搭|装扮|着装)(?:唯一)?参考"),                 # "出场态造型参考（…白毛巾裹腰）"
    re.compile(r"(?:wardrobe|outfit|clothing|clothes)\b[^;.\n]{0,20}?\b(?:is|are|follows?|comes? from|per|as)\b", re.I),
    re.compile(r"(?<!ignore )\b(?:face|hair)\b(?:(?!ignore)[^;.\n])*?\b(?:wardrobe|outfit|clothing|clothes)\b", re.I),
]
IMAGE_CLOTHES = SOURCE[2]
STYLING = SOURCE[4]
SOURCE_ROW = re.compile(r"^\|\s*衣着来源\s*\|\s*([^|\n]*)\|", re.M)
# "Isa身穿@01_Sharks_outfit" / "wears Image2" count only outside a 不参考 / ignore clause
# (v4 Theo: "不参考…图中黑色毛衣（身穿戏服@01_Theo_outfit）" is not a source).
WEARS_SOURCE = re.compile(r"(?:身穿|穿着|穿上|换上|wears|wearing|dressed in)[^，。；,;\n]{0,6}?(?:@|图片?\s*\d|Image\s*\d|"
                          + GARMENT + ")", re.I)
GENERIC_NAMES = re.compile(r"^(?:\d+|人物|角色|主体|人|演员|男演员|女演员|character|person)$", re.I)
LOCK_LABELS = re.compile(r"节奏|声音|轴线|光|空间|字幕|物件|道具|屏幕|方向|服装|衣着|外观|镜头|机位|注意|节拍|台词|音色|"
                         r"rhythm|sound|axis|light|subtitle|camera|note", re.I)
PERSON = re.compile(r"岁|男性|女性|男人|女人|男孩|女孩|少年|少女|老人|头发|发型|短发|长发|卷发|马尾|光头|寸头|"
                    r"\bman\b|\bwoman\b|\bboy\b|\bgirl\b|\bhair\b", re.I)
COLLECTIVE = re.compile(r"两位|两人|二人|俩人|两名|三人|三位|三名|四人|四位|both of them|the two of them|the pair|"
                        r"all three(?: of them)?", re.I)
COUNT = (("两", 2), ("二", 2), ("俩", 2), ("三", 3), ("四", 4), ("both", 2), ("the two", 2), ("the pair", 2),
         ("all three", 3))
GAZE = re.compile(r"(?:看向|望向|看着|盯着|瞄向|瞥向|看了一眼|看|朝着?|冲着?|对着|转向|面向|落在|落到|停在|移到|扫过|"
                  r"looks? at|glances? at|towards?)\s*"
                  r"(?:画[左右中]|frame-(?:left|right))?的?\s*$", re.I)
OFFSCREEN = re.compile(r"[^，。；,;]{0,4}?(?:在画外|画外|出画|的声音|的画外音|声音|看不见|不入画|off-screen|offscreen|out of frame|"
                       r"\(O\.S\.\)|\(V\.O\.\))",
                       re.I)
SPEECH_LABEL = re.compile(r"台词\s*[（(][^)）\n]*[)）]")
EN_SPEECH = re.compile(r"\s+says\s*\(([^)\n]*)\)", re.I)
# Shot annotations, acting labels 〔Noah·不忍〕 and quoted text (dialogue, signs: "BECKETT HALE") are not appearances.
ANNOTATION = re.compile(r'【[^】\n]*】|〔[^〕\n]*〕|“[^”\n]*”|「[^」\n]*」|"[^"\n]*"')
UNIT_LEAD = re.compile(r"^[\s：:]*")


def section(text, key):
    for alias in SECTIONS[key]:
        start = text.find(alias)
        if start >= 0:
            start += len(alias)
            stop = SECTION_RE.search(text, start)
            return text[start: stop.start() if stop else len(text)]
    return None


def bindings(text):
    body = section(text, "refs") or ""
    matches = list(DECL_RE.finditer(body))
    out = []
    for i, m in enumerate(matches):
        entry = body[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(body)]
        out.append((m.group("tok").strip(), entry.strip()))
    return out


def kind_of(token, entry):
    if MEDIA.match(token):
        return None
    kept = NOT_REFERENCED.sub("", entry)
    if NOT_CHARACTER.search(kept):
        return None
    face = FACE.search(kept) or LOOKS_OF_PERSON.search(kept)
    # "@01_Theo_outfit = 本条 Theo演员身上唯一的服装" defines clothes; it names a person without showing one.
    if OUTFIT.search(kept) and not face:
        return "outfit"
    # 人物 / 角色 / 演员 alone mark a character only in the line's own head ("图1 = 人物外观"), not in a scene
    # line's later note ("球员休息区，…；人物位置按文字").
    if face or CHARACTER.search(re.split(r"[，,；;。（(]", kept, maxsplit=1)[0]):
        return "character"
    return None


def token_pattern(token):
    """A declaration head may carry several assets ("@A_front @A_side", "图1-2"); any of them refers to it."""
    parts = []
    for one in re.split(r"[ \t、，,]+(?=@)", token.strip()):
        bare = one.lstrip("@").strip()
        numbers = re.findall(r"\d+", bare)
        if re.match(r"图", bare) and numbers:
            if len(numbers) == 2 and re.search(r"[-–至到]", bare):
                numbers = [str(n) for n in range(int(numbers[0]), int(numbers[1]) + 1)]
            parts += [r"@?图片?\s*" + n + r"(?!\d)" for n in numbers]
        elif re.match(r"image|img", bare, re.I) and numbers:
            if len(numbers) == 2 and re.search(r"[-–]", bare):
                numbers = [str(n) for n in range(int(numbers[0]), int(numbers[1]) + 1)]
            parts += [r"@?(?:Image|img)\s*" + n + r"(?!\d)" for n in numbers]
        else:
            parts.append(re.escape("@" + bare))
    return "|".join(parts)


def names_from(token, entry):
    names = set()
    for one in re.split(r"[ \t、，,]+(?=@)", token.strip()):
        if one.startswith("@") and not re.match(r"@?图", one):
            names.add(one[1:].strip())
            names.add(re.sub(r"^[\d_\-]+", "", one[1:].strip()))        # @02_Noah is Noah
    m = re.search(r"饰演\s*([^\s的，,（(]+)\s*的", entry)
    if m:
        names.add(m.group(1))
    else:
        m = re.match(r"\s*([A-Za-z][A-Za-z.'’-]*(?: [A-Za-z][A-Za-z.'’-]*){0,2}|[^\s，,（(：:=；;{}]{1,12}?)\s*(?:的)?(?:人物)?(?:外观|形象)",
                     entry)
        if m:
            names.add(m.group(1))
        m = re.search(r"([A-Za-z][A-Za-z.'’-]*(?: [A-Za-z][A-Za-z.'’-]*){0,2})\s*(?:的)?(?:人物)?(?:外观|形象)", entry.split("，")[0])
        if m:                                                              # "男主 Noah 外观"
            names.add(m.group(1))
        m = re.match(r"\s*\{?([^{}\n(]+?)\}?(?:'s)?\s+appearance", entry, re.I)
        if m:
            names.add(m.group(1).strip())
    # "Isaiah Marsh" is also written "Isaiah" in shots.
    names |= {n.split()[0] for n in names if re.fullmatch(r"[A-Za-z][A-Za-z.'’-]+(?: [A-Za-z.'’-]+)+", n)}
    return {n for n in names if n and not GENERIC_NAMES.match(n)}


def name_pattern(name):
    if re.search(r"[A-Za-z]", name):
        return r"(?<![A-Za-z0-9_@])" + re.escape(name) + r"(?![A-Za-z0-9_])"
    return re.escape(name)


def lock_characters(text, known):
    """Characters named by their own appearance lock in 【贯穿要求】 ("名字：…岁…")."""
    body = section(text, "global") or ""
    found = []
    for segment in re.split(r"[；;。\n]", body):
        m = re.match(r"\s*([^\s：:；;，,（(【】]{1,12})\s*[：:]\s*(.+)", segment)
        if not m or LOCK_LABELS.search(m.group(1)) or GENERIC_NAMES.match(m.group(1)):
            continue
        if PERSON.search(m.group(2)) and not known.search(m.group(1)):
            found.append(m.group(1))
    return list(dict.fromkeys(found))


def clause(body, start, others):
    """From a first appearance to the end of its clause (；。 or newline outside brackets) or the next character."""
    depth, i = 0, start
    while i < len(body):
        c = body[i]
        if c in "（(":
            depth += 1
        elif c in "）)":
            depth = max(0, depth - 1)
        elif depth == 0 and c in "；;。.\n" and not (c == "." and i + 1 < len(body) and body[i + 1].isdigit()):
            break
        if i > start and depth == 0 and others and others.match(body, i):
            break
        i += 1
    return body[start:i]


def sentence_end(body, start):
    m = re.search(r"[；;。\n]", body[start:])
    return start + m.start() if m else len(body)


def blank(match):
    return " " * len(match.group(0))


def appearances(body, pattern):
    """(position, kind) of each appearance; kind 'prose' or 'speech' (on-screen speaker label)."""
    labels = [(m.start(), m.end(), m.group(0)) for m in SPEECH_LABEL.finditer(body)]
    own_reference = re.compile(r"[^，。；,;（(\n]{0,3}?(?:" + pattern.pattern + ")", re.I)
    found = []
    for m in pattern.finditer(body):
        label = next((l for l in labels if l[0] <= m.start() < l[1]), None)
        if label:
            if not re.search(r"画外|off-screen|O\.S\.|V\.O\.", label[2], re.I):
                found.append((m.start(), "speech"))
            continue
        en = EN_SPEECH.match(body, m.end())
        if en:
            if not re.search(r"off-screen|offscreen|O\.S\.|V\.O\.|画外", en.group(1), re.I):
                found.append((m.start(), "speech"))
            continue
        end = m.end()
        while True:                        # "Rhett演员@Rhett 画外闭嘴": name and its own reference are one appearance
            follow = own_reference.match(body, end)
            if not follow or follow.end() <= end:
                break
            end = follow.end()
        if OFFSCREEN.match(body, end) or re.match(r"[^，。；,;]{0,6}?(?:在门外|在墙后)[^，。；]{0,4}看不见", body[end:]):
            continue
        is_token = m.group(0).startswith("@") or re.match(r"图|image|img", m.group(0), re.I)
        if not is_token and GAZE.search(body[max(0, m.start() - 12): m.start()]):
            continue
        found.append((m.start(), "prose"))
    return found


def wardrobe_checks(text, metadata_text=""):
    """→ (errors, warnings, infos, summary). `text` is the Prompt body without the E-layer table; `metadata_text`
    is the whole file, read only for the E-layer 衣着来源 row (W37)."""
    row = SOURCE_ROW.search(metadata_text or "")
    specified = [seg for seg in re.split(r"[；;]", row.group(1)) if "用户指定" in seg] if row else []
    errors, warnings = [], []
    characters, outfits, outfit_entries = [], [], []
    for token, entry in bindings(text):
        kind = kind_of(token, entry)
        if kind == "character":
            characters.append({"token": token, "entry": entry, "names": names_from(token, entry)})
        elif kind == "outfit":
            outfits.append(token)
            outfit_entries.append(entry)
    outfit_re = re.compile("|".join(token_pattern(t) for t in outfits), re.I) if outfits else None
    for c in characters:
        c["pattern"] = re.compile("|".join([token_pattern(c["token"])] + [name_pattern(n) for n in
                                                                            sorted(c["names"], key=len, reverse=True)]), re.I)
        entry = c["entry"]
        positive = NOT_REFERENCED.sub("", entry)
        # "参考面部、发型（身穿常服@Noah outfit）" names the outfit image, not the image's own clothes.
        own = WEARS_SOURCE.sub(" ", outfit_re.sub(" ", entry) if outfit_re else entry)
        c["image_clothes"] = bool(IMAGE_CLOTHES.search(own))
        c["bound_outfit"] = bool(outfit_re and outfit_re.search(positive))
        # An outfit line that names this character ("图2 = Noah 礼服") states the source too.
        named_by_outfit = any(c["pattern"].search(o) for o in outfit_entries)
        if not (any(p.search(entry) for p in SOURCE) or WEARS_SOURCE.search(positive) or named_by_outfit):
            only_negative = re.search(r"(?:不参考|ignore)[^；;。\n]*" + GARMENT, entry, re.I)
            errors.append(f"E23 {c['token']} 是人物形象图，【素材绑定】没有正向写本条衣着来源"
                          + ("（只写了不参考图中衣服，压不住形象图里的衣服）" if only_negative else "") +
                          "：默认写「衣着一律按 @服装图」，没有服装图写「衣着一律按每一镜的文字：{衣物}」；"
                          "用户指定沿用形象图时才写「参考面部、发型与图中衣服：{衣物}」")
        elif c["image_clothes"] and c["bound_outfit"]:
            errors.append(f"E23 {c['token']} 的绑定同时给了两个衣着来源（图中衣服 + 服装图），只留一个")
        elif (c["image_clothes"] or STYLING.search(own)) and not c["bound_outfit"] and \
                not any(c["pattern"].search(seg) for seg in specified):
            warnings.append(f"W37 {c['token']} 的衣着沿用形象图里的衣服，E 层没有登记用户指定——默认形象图与服装图分开"
                            "（衣着按服装图，没有服装图按逐镜文字）；是用户定的，E 层写「| 衣着来源 | 名字：形象图中的衣服（用户指定） |」")
    known = re.compile("|".join(c["pattern"].pattern for c in characters), re.I) if characters else re.compile(r"(?!)")
    for name in lock_characters(text, known):
        characters.append({"token": name, "entry": "", "names": {name}, "pattern": re.compile(name_pattern(name), re.I),
                           "image_clothes": False, "bound_outfit": False})
    summary = {"characters": [c["token"] for c in characters], "outfits": outfits, "units": 0}
    if not characters:
        return errors, warnings, ["衣着（W36）：未识别到有形象图或单列外观锁的角色，脚本不查；逐镜衣着按硬规则 21 人工核对"], summary

    units = []
    opening = section(text, "opening")
    if opening is not None:
        units.append(("起始状态", opening))
    for shot in Document(text).shots:
        units.append((f"镜头{shot.ident}", shot.body))
    global_body = section(text, "global")
    summary["units"] = len(units)
    for label, raw in units + ([("贯穿要求", global_body)] if global_body is not None else []):
        body = ANNOTATION.sub(blank, UNIT_LEAD.sub(blank, raw))
        present, missing, conflict = [], [], []
        for c in characters:
            found = appearances(body, c["pattern"])
            if not found:
                if label == "贯穿要求":
                    missing.append(f"{c['token']}（没有逐人写）")
                continue
            present.append((c["token"], found[0][0]))
            prose = [p for p, k in found if k == "prose"]
            if not prose:
                missing.append(f"{c['token']}（只在台词标签里出现，画内说话却没写衣着）")
                continue
            others = [o["pattern"].pattern for o in characters if o is not c]
            span = clause(body, prose[0], re.compile("|".join(others), re.I) if others else None)
            if not (WEARING.search(span) or (outfit_re and outfit_re.search(span))):
                missing.append(f"{c['token']}（「{span.strip()[:30]}」）")
            elif c["image_clothes"] and not c["bound_outfit"] and outfit_re and outfit_re.search(span):
                conflict.append(c["token"])
        if missing:
            warnings.append(f"W36 {label} 角色第一次出现没写衣着：{'、'.join(missing)}")
        if conflict:
            warnings.append(f"W36 {label} {'、'.join(conflict)} 的绑定写的是图中衣服，这里却穿服装图——衣着来源只留一个")
        # A numeric collective stands in for checked characters only when one of them is never named in this
        # unit and fewer than N were named before it (or in its own sentence, "两位演员此刻在门口：A（…）、B（…）").
        absent = [c["token"] for c in characters if c["token"] not in {t for t, _ in present}]
        for m in COLLECTIVE.finditer(body) if absent and label != "贯穿要求" else ():
            word = m.group(0)
            n = next(v for k, v in COUNT if word.lower().startswith(k))
            named = [t for t, pos in present if pos < m.start() or m.end() <= pos < sentence_end(body, m.end())]
            if len(named) < n:
                warnings.append(f"W36 {label} 用「{word}」集体指代，这里没逐人写：{'、'.join(absent)}")
                break
    infos = [f"衣着（W36 / E23）：角色 {len(characters)} 个（{'、'.join(summary['characters'])}），服装图 "
             f"{len(outfits)} 个{('（' + '、'.join(outfits) + '）') if outfits else ''}；查【起始状态】、每镜、【贯穿要求】；"
             "群演与没有形象图、没单列外观锁的角色不在脚本范围"]
    if any(w.startswith("W36") for w in warnings):
        infos.append("W36 写法：每个在画面里的角色（含监视器、画中画里的）第一次出现写「名字（@形象 身穿 @服装图：衣物）」"
                     "「名字（@形象 身穿图中的…）」或「名字（@形象，衣物文字）」；换装后逐镜写新状态")
    return errors, warnings, infos, summary
