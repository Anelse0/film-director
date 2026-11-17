"""Spatial-direction review: landmark position and character movement, both relative to the CAMERA.

E23 (an ERROR: the validator exits 1 and production preflight blocks) and one INFO line, wired into
validate_prompt.py after the variation track. Regex over the documented local Prompt format; this
is not a scene-geometry solver and it does not judge whether the geometry is right, only whether
the wording leaves it open to two readings.

E23 is the one ERROR in this validator that is a wording heuristic rather than a format / contract
fact (first shipped as WARN W34 on 2026-10-13, promoted the same day): anchoring the landmark to
the camera never makes a prompt worse, a false stop costs a few characters, a false pass costs a
render, and WARNs in this workflow are routinely kept with a written reason. E22 was already taken
by the parameter contract, hence E23.

Trigger case [实测] (validation-log.md evidence #6): the scene image
was shot from inside the building doorway looking out at the street — camera under the canopy,
back to the doors. The character gets out of a car at the curb and walks TOWARD the camera, into
the building. The v2 prompt wrote 朝大门走 / 视线回到前面的大门 / 退向大门, which put the door in
FRONT of the character while the image and the camera put it BEHIND the camera. Seedance resolved
the conflict by walking him away from the camera toward the street, so he looked like he was
leaving. v2.1 fixed it by writing the door as 在镜头身后 every time, the gaze as
看着他要去的方向（镜头后方）, one explicit 方向 sentence in 【贯穿要求】, and the lobby shot as
从门外推门走进来，朝镜头走.

Heuristic A → E23: a shot has a toward-camera / backward-tracking move (后退跟拍 / 朝镜头走 /
走近镜头 / 镜头…后退) AND the same shot, or 【贯穿要求】, names a landmark as ahead of the character
(朝X走 / 走向X / 退向X / 前面的X / 面前的X …) without anchoring X to the camera inside that same text
unit (X在镜头身后 / 镜头后方的X / 镜头前的X / 画面深处 / 画左 / 画右 / 机位正对X / 机位背对X). A shot in
which the character walks away from the camera toward a landmark that is in frame has no
toward-camera move and does not match. Anchoring is checked per text unit, not per prompt: in
the trigger case the opening state already said 机位背对大门 and the shot-level 朝大门走 still won.

Heuristic B → INFO: the prompt has camera-relative or landmark-directed movement but 【贯穿要求】
has no 方向 statement (which side the frame shows, which way the character travels in frame).
INFO rather than WARN: a missing sentence is a reminder, not a detected conflict, and every
walking prompt would otherwise warn.
"""
import re

GLOBAL_ALIASES = ("【贯穿要求】", "GLOBAL RULES")

# ---------- 中文 ----------
LANDMARK_CN = (r"(?:(?:大|玻璃|房|铜框|旋转|侧滑|正)?门口?|车门|车|吧台|柜台|前台|接待台|窗(?:口|户)?|电梯|楼梯"
               r"|出口|入口|桌子?|沙发|大楼|楼|房子|屋子|街道?|马路|人行道|舞台|床|墙|柱子|花槽)")
TOWARD_CAMERA_CN = re.compile(
    r"后退跟拍|倒退跟拍|后退[^。；，\n]{0,4}跟拍|跟拍[^。；，\n]{0,4}后退|镜头[^。；\n]{0,24}?(?:往|向|朝)?后退"
    r"|(?:朝|向|往|迎着|面朝|面向)(?:着)?镜头(?:的)?(?:方向)?[^。；，\n]{0,8}?(?:走|跑|来|移动|挪|过来|逼近|靠近|冲)"
    r"|走近镜头|走向镜头|接近镜头|靠近镜头|逼近镜头|追上镜头")
AWAY_CAMERA_CN = re.compile(r"背对镜头[^。；，\n]{0,8}?(?:走|跑|去|远|移动)|背向镜头|远离镜头|离镜头越来越远|走远")
AHEAD_CN = [
    re.compile(rf"(?:朝|向|往)(?:着)?(?P<x>{LANDMARK_CN})(?:的方向)?(?:走|跑|退|移动|挪|去|过去|冲)"),
    re.compile(rf"(?:走|跑|冲|奔)(?:向|到|回)(?:[^，。；\n]{{0,6}}?的)?(?P<x>{LANDMARK_CN})"),
    re.compile(rf"退(?:向|到|回)(?:[^，。；\n]{{0,6}}?的)?(?P<x>{LANDMARK_CN})"),
    re.compile(rf"(?:前面|前方|面前)的(?:那|这)?(?:扇|张|个|道|排|座|栋|辆)?(?P<x>{LANDMARK_CN})"),
]
MARKER_CN = (r"(?:镜头|机位|摄影机|相机)(?:的)?(?:正)?(?:身后|后方|背后|后面|前|前方|正前方)"
             r"|画面深处|景深处|画(?:面)?(?:左|右)(?:侧|边)?|前景|后景")
DIRECTION_CN = re.compile(r"方向[：:]")
DIRECTION_CN_TRAVEL = re.compile(r"(?:朝|向|走近|走向|背对|面向|迎着)镜头")
DIRECTION_CN_SIDE = re.compile(r"画面(?:里|中)?是|画面深处|镜头身后|镜头后方|背对[^，。；\n]{0,10}(?:拍|朝)|朝[^，。；\n]{0,10}拍"
                               r"|机位[^，。；\n]{0,10}(?:背对|正对)")

# ---------- English ----------
LANDMARK_EN = (r"(?:doors?|doorway|entrance|exit|gate|car|bar|counter|desk|windows?|elevator|lift|stairs|staircase"
               r"|table|stage|building|street|curb|sidewalk)")
TOWARD_CAMERA_EN = re.compile(
    r"toward(?:s)?\s+(?:the\s+)?(?:camera|lens)\b|(?:dolly|dollies|dollying|track|tracks|tracking|pull|pulls|pulling"
    r"|back|backs|backing|retreat|retreats|retreating)\s+(?:back|backward|backwards|away|out)\b"
    r"|walks?\s+(?:up\s+)?(?:in)?to\s+(?:the\s+)?camera|approach(?:es|ing)?\s+(?:the\s+)?camera|reverse\s+track", re.I)
AWAY_CAMERA_EN = re.compile(r"away\s+from\s+(?:the\s+)?camera|back\s+to\s+(?:the\s+)?camera,?\s+walk", re.I)
AHEAD_EN = [
    re.compile(r"(?:walk|walks|walking|head|heads|heading|move|moves|moving|step|steps|stepping|go|goes|going|run|runs"
               r"|running|back|backs|backing|retreat|retreats|retreating)\s+(?:back\s+|away\s+|on\s+|off\s+)?"
               rf"(?:toward|towards|to|into|for)\s+(?:the|a|an|his|her|their)\s+(?:\w+\s+){{0,2}}?(?P<x>{LANDMARK_EN})\b", re.I),
    re.compile(rf"(?:the|his|her|their)\s+(?P<x>{LANDMARK_EN})\s+(?:ahead|in\s+front\s+of\s+(?:him|her|them))\b", re.I),
    re.compile(rf"(?:in\s+front\s+of|ahead\s+of)\s+(?:him|her|them)[,:]?\s+the\s+(?P<x>{LANDMARK_EN})\b", re.I),
]
MARKER_EN = (r"behind\s+(?:the\s+)?(?:camera|lens)|off[- ]screen\s+behind|(?:camera|frame|screen)[- ](?:left|right)"
             r"|(?:in|at)\s+the\s+back\s+of\s+the\s+frame|deep\s+in\s+the\s+frame|in\s+the\s+(?:background|foreground)")
DIRECTION_EN = re.compile(r"\bdirection\s*:", re.I)
DIRECTION_EN_TRAVEL = re.compile(r"toward(?:s)?\s+the\s+camera|away\s+from\s+the\s+camera", re.I)
DIRECTION_EN_SIDE = re.compile(r"frame\s+shows|behind\s+the\s+camera|in\s+the\s+background|frame[- ](?:left|right)"
                               r"|camera\s+(?:faces|facing|has\s+its\s+back)", re.I)


def section(text, aliases):
    """Body of the first section whose alias appears, up to the next section header or table."""
    for alias in aliases:
        start = text.find(alias)
        if start >= 0:
            rest = text[start + len(alias):]
            stop = re.search(r"^\s*(?:【[^】]+】|(?:REFERENCES|OVERVIEW|LOOK|EXCLUDE|OPENING STATE|TIMELINE|GLOBAL RULES"
                             r"|AUDIO)\s*:|\|)", rest, re.M | re.I)
            return rest[:stop.start()] if stop else rest
    return ""


def core_cn(x):
    """Canonical landmark noun: 大门 / 玻璃门 / 门口 → 门; 入口 / 出口 / 窗口 keep their own noun."""
    x = re.sub(r"^(?:大|玻璃|房|铜框|旋转|侧滑|正)", "", x)
    return re.sub(r"(?<=门)口$", "", x)


def core_en(x):
    x = x.lower()
    return x[:-1] if x.endswith("s") and x not in ("stairs",) else x


def anchored_cn(unit, core):
    c = re.escape(core)
    patterns = [
        rf"{c}[^。；\n]{{0,6}}?在?(?:{MARKER_CN})",                               # 门在镜头身后 · 门就在镜头后方
        rf"(?:{MARKER_CN})(?:的)?(?:[^，。；\n]{{0,4}}的)?{c}",                      # 镜头后方的门 · 镜头前的门口
        rf"(?:镜头|机位|摄影机)[^。；\n]{{0,12}}?(?:正对|背对|面向|朝着|对着)(?:[^，。；\n]{{0,4}}?的)?[^，。；\n]{{0,4}}?{c}",  # 机位背对大门
    ]
    return any(re.search(p, unit) for p in patterns)


def anchored_en(unit, core):
    c = rf"\b{re.escape(core)}s?\b"
    patterns = [
        rf"{c}[^.;\n]{{0,30}}?(?:{MARKER_EN})",
        rf"(?:{MARKER_EN})[^.;\n]{{0,20}}?{c}",
        rf"camera[^.;\n]{{0,20}}?(?:faces|facing|back\s+to|back\s+toward(?:s)?)[^.;\n]{{0,12}}?{c}",
    ]
    return any(re.search(p, unit, re.I) for p in patterns)


CHANGE_FIELD = re.compile(r"【变化[：:][^】]*】|\[CHANGE[：:][^\]]*\]", re.I)


def own_text(unit):
    """A shot's own prose: the 【变化：…】 field names the previous shot's move (后退跟拍→横移) and is not this shot."""
    return CHANGE_FIELD.sub("", unit)


def toward_camera(unit):
    unit = own_text(unit)
    return bool(TOWARD_CAMERA_CN.search(unit) or TOWARD_CAMERA_EN.search(unit))


def away_camera(unit):
    unit = own_text(unit)
    return bool(AWAY_CAMERA_CN.search(unit) or AWAY_CAMERA_EN.search(unit))


def anchored(unit, core):
    return anchored_cn(unit, core) or anchored_en(unit, core)


def landmark_phrases(unit, anchors=()):
    """All landmark-ahead phrases in a unit as (phrase, core, resolved).

    A phrase is resolved when the landmark is anchored to the camera in the same unit, or in any of
    the extra `anchors` units (used for 【贯穿要求】, which has no shot of its own: its landmark counts
    as anchored when a toward-camera shot anchors it)."""
    unit = own_text(unit)
    found = []
    for pattern in AHEAD_CN:
        for m in pattern.finditer(unit):
            core = core_cn(m.group("x"))
            found.append((m.group(0), core, any(anchored(u, core) for u in (unit, *anchors))))
    for pattern in AHEAD_EN:
        for m in pattern.finditer(unit):
            core = core_en(m.group("x"))
            found.append((m.group(0), core, any(anchored(u, core) for u in (unit, *anchors))))
    return found


def unresolved(unit, anchors=()):
    seen, out = set(), []
    for phrase, core, resolved in landmark_phrases(unit, anchors):
        if not resolved and phrase not in seen:
            seen.add(phrase)
            out.append((phrase, core))
    return out


def has_direction_statement(global_unit):
    if DIRECTION_CN.search(global_unit) or DIRECTION_EN.search(global_unit):
        return True
    if DIRECTION_CN_TRAVEL.search(global_unit) and DIRECTION_CN_SIDE.search(global_unit):
        return True
    return bool(DIRECTION_EN_TRAVEL.search(global_unit) and DIRECTION_EN_SIDE.search(global_unit))


def quote(items):
    return "、".join(f"「{p}」" for p, _ in items)


def direction_checks(text, shots):
    """Return (errors, infos). text is the Prompt body (E-layer table stripped); shots as validate_prompt.split_shots."""
    errors, infos = [], []
    global_unit = section(text, GLOBAL_ALIASES)
    toward_shots = [no for no, _, _, body in shots if toward_camera(body)]
    global_hits = unresolved(global_unit, anchors=[body for no, _, _, body in shots if no in toward_shots])
    for no, _, _, body in shots:
        if no not in toward_shots:
            continue
        hits = unresolved(body)
        if hits:
            cores = "、".join(dict.fromkeys(c for _, c in hits))
            errors.append(f"E23 镜头{no} 后退跟拍 / 朝镜头走，同镜又写 {quote(hits)}：{cores}没有标相对镜头的位置"
                          f"（镜头身后 / 画面深处 / 画左右）——地标在人物前方与人物朝镜头走冲突，模型会让人物背对镜头走远；"
                          f"改写为「镜头身后的{cores}」或「朝镜头走来（{cores}在镜头身后）」再生成 [实测]")
    if global_hits and toward_shots:
        cores = "、".join(dict.fromkeys(c for _, c in global_hits))
        errors.append(f"E23 【贯穿要求】写 {quote(global_hits)}，而镜头 {toward_shots} 后退跟拍 / 朝镜头走：{cores}没有标相对镜头的位置"
                      f"（镜头身后 / 画面深处 / 画左右）——与朝镜头的运动冲突；改写为「{cores}在镜头身后」并在每镜重复 [实测]")
    moving = bool(toward_shots) or any(away_camera(b) or landmark_phrases(b) for _, _, _, b in shots) \
        or away_camera(global_unit) or bool(landmark_phrases(global_unit))
    if moving:
        if has_direction_statement(global_unit):
            infos.append("方向句：【贯穿要求】已写方向（画面是哪一侧 / 人物在画内朝哪走）")
        else:
            infos.append("方向句：正文有朝镜头 / 背对镜头或朝地标的走位，【贯穿要求】未见方向句（画面是哪一侧、人物在画内朝哪走）；"
                         "场景图定了机位朝向时写一句（S6 §6.2 贯穿要求）")
    return errors, infos
