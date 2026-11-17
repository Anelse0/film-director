"""Focus and soft-layer placement per character shot (W43 + INFO), stdlib only — 1.7.0.

The tag format 【景别，机高/角度，运镜与终点，构图位置】 had no focus slot: S4 §4.4 lists 焦点 as a visibility condition and
camera-vocabulary.md has the words, but nothing asked for a per-shot statement. 1.7.0 (S5 §5.2 step 3; `[推论]` + the
user's practice 2026-10-13; the 移焦 / 主体清晰、背景虚化 wording is `[官方示例]`; render effect `[未验证]`): every shot with an
on-screen character says 焦点在谁（部位）; a shot with an over-shoulder or soft layer says where that layer sits and how much
of the frame it takes; the default depth of field is declared once in 【画面基调】. Every item here is a review hint
(WARN), never a format fact; the E-layer row `焦点理由` keeps a reviewed design.

  W43  焦点未写     on-screen character shots — an on-screen dialogue tag (no 画外 / 电话里 … channel word), a 视线 label,
                    face words, or a 双人 / named-character tag; object and body-part inserts (空镜 / 插入 / 只拍 / X 的手 …)
                    with no on-screen line are exempt — with no 焦点在 … / 对焦 / explained 移焦 / focus on … statement in the
                    tag or the body: one warning listing the shots.
  W43  虚实未定位   a shot whose tag or camera prose names an over-shoulder layer (过肩 / 越肩 / 越过 X 的肩 / over-the-shoulder)
                    or whose prose names a soft layer (虚化 / 虚焦 / 模糊 / 光斑 …) and that says nowhere which side, corner or
                    layer it occupies (左下角 / 一小块 / 边缘 / 身后 / 前景 …): one warning per shot. Keyframe tasks are exempt
                    (the placement lives in the image).
  INFO 焦点         n/m on-screen character shots state a focus; the default depth-of-field phrase quoted from 【画面基调】, or
                    its absence; the `焦点理由` row when present.
"""
import re

from guide_checks import section_text, NAME_TOKEN_RE
from prompt_structure import SPEECH_RE

# rhythm_checks.tag_of stops at 80 characters; a tag that carries 焦点在 X is read with a wider allowance here.
TAG_RE = re.compile(r"【([^】]{2,120})】|\[([^\]]{2,160})\]")
CHANNEL_RE = re.compile(r"画外|旁白|电话里|屏幕里|手机里|车载|内心独白|免提|听筒|扬声器|音响|广播|off[- ]screen|\bV\.?O\.?|\bphone\b", re.I)
GAZE_LABEL_RE = re.compile(r"视线(?:落点)?\s*[:：]")
FACE_RE = re.compile(r"脸|(?<!刺)眼(?!镜)|眉|嘴|表情|(?<!说)(?<!玩)笑(?!声|话)|下巴|下颌|\b(?:face|eyes|gaze|smile|brow|mouth)\b", re.I)
PEOPLE_TAG_RE = re.compile(r"双人|[两三四五六]人|\d\s*人|two[- ]shot", re.I)
# Body-part / object inserts (X 的手, 脚印, 按钮, 道具, 空镜, 只拍 …) are exempt whenever no on-screen line is spoken, even when
# the tag names whose hand it is; a 屏幕 tag is exempt only when it names nobody (X 与屏幕同框 is a character shot).
INSERT_RE = re.compile(r"(?:的|只|双|两只)手(?!持)|手部|手腕|脚印|按钮|物件|道具|空镜|插入|只拍|\b(?:insert|object|prop|hand)\b", re.I)
SCREEN_RE = re.compile(r"屏幕|screen", re.I)
FOCUS_RE = re.compile(r"焦点[^，。；：:【】\n]{0,4}(?:在|落|从|转|跟|移|锁|给|里|回|始终|一直|保持|切|换|是|为|和|随|[：:])"
                      r"|聚焦|合焦|对焦|变焦点|移焦[^。；\n]{0,30}(?:变|转|清晰|模糊|清楚)"
                      r"|focus(?:ed|es|ing)?\s+(?:on|pull|rack|stay|shift|remain|hold|move|is|sits)|in focus|sharp on", re.I)
# Over-shoulder named in the tag, or in the camera prose before the first 台词 / 视线 / 声音 label. Not a character looking
# over a shoulder (目光 / 回头 越过 X 的肩膀), not 并肩 / 肩上.
OTS_TAG_RE = re.compile(r"(?<!越)过肩|越肩|越过[^，。；：【】\n]{0,12}肩|肩头|肩后|over[- ]the[- ]shoulder|\bOTS\b", re.I)
OTS_PROSE_RE = re.compile(r"(?<!目光)(?<!视线)(?<!回头)(?<!抬头)(?<!转头)(?<!侧头)(?<!眼)(?:(?<!越)过肩|越肩|越过[^，。；：【】\n]{0,12}肩)"
                          r"|over[- ]the[- ]shoulder", re.I)
SOFT_RE = re.compile(r"虚化|虚焦|虚着|虚在|虚成|略虚|都虚|柔焦|模糊|光斑|\b(?:blur|bokeh)|soft focus", re.I)
# An over-shoulder layer needs a corner / side / amount (the user's practice: a lower corner, a small patch); a soft background
# is placed by naming the layer (身后的客人轻微虚化 / 背景虚化).
PLACE_RE = re.compile(r"左下|右下|下角|上角|一角|角落|一小块|只占|占画面|占[一两三半]|三分之一|边缘|\b(?:corner|third|edge)\b", re.I)
LAYER_RE = re.compile(r"身后|背景|后景|远处|深处|前景(?!\s*[=＝])|\b(?:background|foreground|behind)\b", re.I)
DOF_RE = re.compile(r"[深浅中]等?景深|适中景深|深焦|全景深|景深(?:自然|较深|较浅|深|浅)|背景(?:适度|轻微|柔和|都|自然)?虚化?|都清楚|同时清晰|光斑"
                    r"|deep focus|shallow(?: depth of field| focus)?|depth of field", re.I)
# The legacy inline 【变化：景别 A→B｜机位 A→B…】 field names the previous shot's position (越肩→正面, 移焦→固定); it is not
# this shot's focus or layer statement. Dialogue brackets hold voice words (吐字清楚); 声音 clauses hold the audio layering (前景=).
VARIATION_FIELD_RE = re.compile(r"[【\[]\s*变化\s*[:：][^】\]]*[】\]]")
BRACKET_RE = re.compile(r"台词\s*[（(][^)）\n]*[)）]")
SOUND_CLAUSE_RE = re.compile(r"声音\s*[:：][^。\n]*。?")
LABEL_RE = re.compile(r"台词\s*[（(]|视线(?:落点)?\s*[:：]|声音\s*[:：]|表演\s*[:：]|表情\s*[:：]|结束时|\b(?:says|speaks|Eyeline|Face|Sound)\b", re.I)
FOCUS_REASON_RE = re.compile(r"\|\s*焦点理由\s*[|｜]\s*([^|\n]+)\|")
NUMBERED_RE = re.compile(r"(?:图片?|视频|音频|image|img|video|vid|audio|aud)\s*\d+$", re.I)


def tag_of(body):
    tag = TAG_RE.search(body[:200])
    return (tag.group(1) or tag.group(2)) if tag else ""


def prose_of(body):
    """The shot text without the legacy inline 【变化：…】 field."""
    return VARIATION_FIELD_RE.sub("", body)


def picture_prose(body):
    """Shot text that describes the picture: no 【变化】 field, no dialogue brackets, no 声音 clauses."""
    return SOUND_CLAUSE_RE.sub("", BRACKET_RE.sub("台词（）", prose_of(body)))


def normalize_speaker(raw):
    """`Theo演员@Theo ` → Theo; `女导演@01_Directer ` → 女导演; `Theo 内心独白画外` → Theo."""
    s = re.sub(r"@\S+", "", raw or "")
    s = CHANNEL_RE.sub("", s)
    s = re.sub(r"演员|\s+", "", s)
    return s.strip("，,、 ")


def character_names(text, dialogue):
    """Names the prompt uses for people: dialogue speakers, `@名` stems (@Theo-基础形象 → Theo) and the names that
    【起始状态】 introduces with a reference in brackets (`Rhett（@Rhett-基础形象…` / `图1的母亲`)."""
    names = set()
    for row in dialogue or []:
        name = normalize_speaker(row.get("speaker", ""))
        if name:
            names.add(name)
    for m in NAME_TOKEN_RE.finditer(text):
        stem = re.split(r"[-_]", m.group("name"))[0]
        if stem and not re.match(r"\d", stem) and not NUMBERED_RE.match(stem):
            names.add(stem)
    opening = section_text(text, "起始状态")
    for m in re.finditer(r"(?<![A-Za-z])([A-Za-z][A-Za-z]{0,15}|[一-鿿]{1,4})\s*[（(]\s*(?:@|图)", opening):
        names.add(m.group(1))
    for m in re.finditer(r"图\s*\d+\s*的\s*([一-鿿]{1,4}?|[A-Za-z]{1,16})(?=[（(在站坐走从把看刚正已穿躺靠回抬低向朝\s，,、]|$)", opening):
        names.add(m.group(1))
    return {n for n in names if n not in {"图", "图片", "画面"}}


def name_in(text, names):
    for name in names:
        if re.search(r"[A-Za-z]", name):
            if re.search(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text):
                return True
        elif name in text:
            return True
    return False


def onscreen_dialogue(body):
    """A dialogue tag whose bracket carries no channel word (画外 / 电话里 / 内心独白 …)."""
    for m in SPEECH_RE.finditer(body):
        details = m.group("cn") or m.group("en") or ""
        if not CHANNEL_RE.search(details):
            return True
    return False


def has_dialogue(no, body, dialogue):
    if SPEECH_RE.search(body):
        return onscreen_dialogue(body)
    return any(row.get("shot") == str(no) for row in dialogue or [])


def is_character_shot(no, body, dialogue, names=()):
    """An on-screen character: on-screen dialogue, a 视线 label, face words, or a 双人 / named-character tag — unless the
    tag marks an object or body-part insert and the shot has no on-screen line and names nobody."""
    tag = tag_of(body)
    spoken = has_dialogue(no, body, dialogue)
    if not spoken and INSERT_RE.search(tag):
        return False
    in_tag = bool(PEOPLE_TAG_RE.search(tag)) or name_in(tag, names)
    if not spoken and not in_tag and SCREEN_RE.search(tag):
        return False
    prose = picture_prose(body)
    return bool(spoken or in_tag or GAZE_LABEL_RE.search(prose) or FACE_RE.search(prose))


def has_focus(body):
    return bool(FOCUS_RE.search(prose_of(body)))


def layer_without_placement(body):
    """An over-shoulder or soft layer is named but nothing says where it sits or how much of the frame it takes."""
    prose = picture_prose(body)
    camera = LABEL_RE.split(prose, 1)[0]
    if OTS_TAG_RE.search(tag_of(body)) or OTS_PROSE_RE.search(camera):
        return not PLACE_RE.search(prose)
    if SOFT_RE.search(prose):
        return not (PLACE_RE.search(prose) or LAYER_RE.search(prose))
    return False


def depth_of_field(text):
    """The default depth-of-field phrase declared in 【画面基调】 / LOOK, or None."""
    m = DOF_RE.search(section_text(text, "画面基调"))
    return m.group(0).strip() if m else None


def keyframe_task(text):
    head = text.strip().splitlines()[0] if text.strip() else ""
    return bool(re.search(r"以图片\s*\d+.{0,40}作为关键帧", head)) or "关键帧" in section_text(text, "素材绑定")


def global_focus(text):
    for label in ("画面基调", "贯穿要求"):
        m = FOCUS_RE.search(section_text(text, label))
        if m:
            start = max(0, m.start() - 6)
            return section_text(text, label)[start:m.end() + 14].strip()
    return None


def focus_checks(text, shots, dialogue, metadata_text=""):
    """Return (warnings, infos).

    text: D-layer body (E table stripped); shots: validate_prompt.split_shots(); dialogue: rows from dialogue_checks;
    metadata_text: whole file (E-layer `焦点理由`)."""
    warns, infos = [], []
    if not shots:
        return warns, infos
    names = character_names(text, dialogue)
    keyframe = keyframe_task(text)
    character, focused, missing, layered = [], [], [], []
    for no, _, _, body in shots:
        if is_character_shot(no, body, dialogue, names):
            character.append(no)
            (focused if has_focus(body) else missing).append(no)
        if not keyframe and layer_without_placement(body):
            layered.append(no)
    reason = FOCUS_REASON_RE.search(metadata_text or "")
    if reason:
        if missing or layered:
            infos.append(f"焦点：E 层 焦点理由 已写明（{reason.group(1).strip()[:40]}），W43 不报；"
                         f"{len(focused)}/{len(character)} 个画内人物镜写了焦点")
        missing, layered = [], []
    if missing:
        global_line = global_focus(text)
        extra = f"；全局已写「{global_line[:30]}」，逐镜仍要写" if global_line else ""
        warns.append(f"W43 镜头 {missing} 有画内人物但没写焦点在谁：标注末尾加「焦点在 X（部位）」（深景深的双人镜写这一镜为谁的反应而拍的人）；"
                     f"默认景深在【画面基调】声明一次（S5 §5.2 第 3 步）；E 层 焦点理由 可保留{extra}")
    for no in layered:
        warns.append(f"W43 镜头 {no} 有过肩 / 虚化层，没写它在画面哪里、占多少（哪一层虚、在哪一侧或哪个角、占多少；主体在哪里清楚）")
    if character and not reason:
        dof = depth_of_field(text)
        if dof:
            infos.append(f"焦点：{len(focused)}/{len(character)} 个画内人物镜写了焦点；默认景深「{dof}」（【画面基调】）")
        else:
            infos.append(f"焦点：{len(focused)}/{len(character)} 个画内人物镜写了焦点；未声明默认景深（【画面基调】写一句景深：深 / 中等 / 浅）")
    return warns, infos
