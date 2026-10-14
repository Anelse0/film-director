"""Tone-cue review (W35): staging cues that read as suspense in a scene that is not one.

Trigger case [实测] (validation-log.md 2026-10-13, offset EP05 场03 clip02 v1): a light, warm
bar scene — two coworkers bantering, a regular walking in. The ending rendered "like a thriller".
The prompt text had four pieces of suspense grammar: a hand holding a fry stops halfway (freeze);
a hard cut to a fixed frontal close-up in which the character slowly turns his head toward an
off-screen person who is approaching (slow turn); the coworker stares in one direction and lowers
her voice (stare + whisper); the regular walks straight toward the camera on a long lens with no
state written (stateless approach). The accepted fix wrote the light reading into the cues:
he keeps chewing, no head turn, she holds back a smile and gossips, he walks in looking at his
phone with a hand in a pocket and loose shoulders, ambient chatter continues, plus one tone line.
A follow-up risk for the end shot: head lowered with eyes raised to the lens reads as a menacing
stare, eyes-only sideways glances with a frozen head read as suspicion; fix = chin level, eyeline
in the partner's screen direction, a small continuous action.

The tone word does not set the tone; the cues do. The model follows "手停在半路 / 慢慢转头 / 盯着 +
压低声音 / 朝镜头走来" and ignores "轻松". Freeze and deadpan are legitimate devices in comedy (G5)
and suspense (G2), so a declared 喜剧 / 悬疑 / 惊悚 turns the warning into INFO.

W35 (WARN, review item): per shot, collect cue types A–E below from the shot's own prose (the
【变化：…】 field is the previous shot). A / B / E are dropped when the same shot carries a light
cue (笑 / 嚼 / 聊 / 眨 / 继续 / 边…边 …); C (stare + whisper) and D (approach without any state
word) are not softened by a smile elsewhere in the shot. Then:
  - genre declared (悬疑 / 惊悚 / 恐怖 / 喜剧 / 冷面 / thriller / comedy …) → INFO only;
  - light tone declared (轻松 / 温暖 / 日常 / 玩笑 / 八卦 …) → W35 on every shot with ≥1 cue type;
  - no tone declared → W35 on a shot with ≥2 cue types, or on cue shots that are adjacent.
Regex over the documented local format; semantic acting quality is still needs_review.
"""
import re

OWN_TEXT = re.compile(r"【变化[：:][^】]*】|\[CHANGE[：:][^\]]*\]", re.I)

# ---------- declared tone ----------
GENRE_INTENDED = re.compile(r"悬疑|惊悚|恐怖|惊吓|鬼|阴森|诡异|喜剧|冷面|搞笑|滑稽|荒诞"
                            r"|thriller|suspense|horror|creepy|menac|ominous|comed|deadpan|farce|slapstick", re.I)
# Tone words only: 暖 alone would match 暖光 in every 【画面基调】, 放松 matches 肩膀放松 in blocking.
LIGHT_TONE = re.compile(r"轻松|温暖|温馨|日常|玩笑|八卦|打趣|打闹|闺蜜|轻快|愉快|欢快|惬意"
                        r"|light-?hearted|lighthearted|warm|casual|playful|banter|everyday|easygoing", re.I)

# ---------- cues (per shot) ----------
FREEZE = re.compile(r"停在半路|停在半空|僵住|僵在|定住|顿住|停在原地|(?:手|胳膊|手臂|动作|脚步|身体|勺子|杯子|筷子)[^。；，\n]{0,6}?停住"
                    r"|freez(?:e|es)|stops? (?:mid|half)|hands? stops?|goes still", re.I)
SLOW_TURN = re.compile(r"(?:缓缓|慢慢|缓慢|一点点)(?:地)?(?:转头|转过头|回过头|回头|转过脸|扭头|转向|抬头|抬起头)"
                       r"|slowly turns? (?:his |her |their )?(?:head|face)|turns? (?:his |her |their )?head slowly", re.I)
TURN = re.compile(r"转头|转过头|回过头|转过脸|扭头|turns? (?:his |her |their )?head", re.I)
OFFSCREEN_ARRIVAL = re.compile(r"走过来|走来|走近|过来|过道|门口|画外|身后|off[- ]screen|approach|coming|walks in", re.I)
FIXED_FRONTAL_CU = re.compile(r"固定|fixed|static|locked", re.I)
FRONTAL = re.compile(r"正面|正对|frontal|facing camera|head-on", re.I)
CLOSE = re.compile(r"特写|近景|close-?up|CU\b|MCU\b", re.I)
STARE = re.compile(r"盯着|盯住|定定地|直直地|直视|不眨眼|一眨不眨|死死地|stares?|fixed gaze|unblinking", re.I)
WHISPER = re.compile(r"压低声音|声音压低|压低了声音|低声|声音放低|放低声音|轻声说|小声|whisper|lowers? (?:his |her |their )?voice|under (?:his |her |their )breath", re.I)
APPROACH = re.compile(r"朝镜头(?:这边|这里|方向)?走|向镜头走|走向镜头|朝(?:着)?镜头(?:这边)?(?:走|过)来|逼近镜头|走近镜头|迎着镜头"
                      r"|从[^。；，\n]{0,12}?(?:走过来|走来)|walks? (?:straight )?toward(?:s)? (?:the )?camera|approach(?:es|ing)? (?:the )?camera", re.I)
# A gaze target alone (看着吧台的方向) is not a state; the trigger case had exactly that and read as stalking.
STATE_WORDS = re.compile(r"手机|口袋|裤袋|插在|肩膀|步子|神情|表情|笑|聊|说着|边走边|手里|拿着|提着|端着|拎着|扶着|挥手|打招呼|哼|放松|随意|不紧不慢|晃|摆"
                         r"|phone|pocket|shoulders|smil|grin|chat|wav|hands?|carr|holding|relaxed|casual|stroll|nod", re.I)
KUBRICK = re.compile(r"低着头[^。；\n]{0,10}(?:抬眼|抬起眼|眼睛(?:抬|往上|向上)|眼珠)|低头抬眼|头(?:低着|垂着)[^。；\n]{0,10}眼睛(?:抬|往上|向上)|从眉毛下(?:面)?看|眼睛(?:从下往上|向上)(?:看|瞟)"
                     r"|head (?:down|lowered)[^.;\n]{0,30}eyes (?:up|raised)|looks? up from under", re.I)
SIDE_EYE = re.compile(r"只动眼珠|只有眼珠|眼珠(?:转|斜|瞟)|斜眼|斜着眼|眼睛斜|余光(?:看|瞥|扫|瞄)|头不(?:动|转)[^。；，\n]{0,8}(?:眼|视线)"
                      r"|side-?eye|eyes only|without turning (?:his |her |their )?head", re.I)
LIGHT_CUE = re.compile(r"笑|嚼|吃着|哼|聊|打趣|挑眉|眉毛[^。；，\n]{0,3}挑|眨|眼睛亮|轻快|随意|放松|继续|不停|没停|手上的活|边(?:走|说|吃|嚼)边|乐|逗|哈"
                       r"|smil|grin|laugh|chew|chat|shrug|wink|keeps? (?:working|stirring|eating)", re.I)

SECTION_ALIASES = {
    "overview": ("【总述】", "OVERVIEW"),
    "look": ("【画面基调】", "LOOK"),
    "global": ("【贯穿要求】", "GLOBAL RULES"),
}


def section(text, aliases):
    for alias in aliases:
        start = text.find(alias)
        if start >= 0:
            rest = text[start + len(alias):]
            stop = re.search(r"^\s*(?:【[^】]+】|(?:REFERENCES|OVERVIEW|LOOK|EXCLUDE|OPENING STATE|TIMELINE|GLOBAL RULES"
                             r"|AUDIO)\s*:|\|)", rest, re.M | re.I)
            return rest[:stop.start()] if stop else rest
    return ""


def own_text(unit):
    return OWN_TEXT.sub("", unit)


def shot_tag(unit):
    m = re.search(r"【([^】]{2,80})】|\[([^\]]{2,100})\]", unit[:120])
    return (m.group(1) or m.group(2)) if m else ""


def shot_cues(body):
    """Return {cue_type: phrase} for one shot's own prose."""
    body = own_text(body)
    tag = shot_tag(body)
    found = {}
    light = bool(LIGHT_CUE.search(body))
    if not light:
        m = FREEZE.search(body)
        if m:
            found["停住"] = m.group(0)
        m = SLOW_TURN.search(body)
        if m:
            found["慢转头"] = m.group(0)
        elif FIXED_FRONTAL_CU.search(tag) and FRONTAL.search(tag) and CLOSE.search(tag) \
                and TURN.search(body) and OFFSCREEN_ARRIVAL.search(body):
            found["固定正面近景里转头朝画外来人"] = TURN.search(body).group(0)
        m = KUBRICK.search(body) or SIDE_EYE.search(body)
        if m:
            found["低头抬眼 / 只动眼珠"] = m.group(0)
    s, w = STARE.search(body), WHISPER.search(body)
    if s and w:
        found["盯住 + 压低声音"] = f"{s.group(0)} … {w.group(0)}"
    a = APPROACH.search(body)
    if a and not STATE_WORDS.search(body):
        found["无状态的朝镜头走来"] = a.group(0)
    return found


def declared_tone(text, metadata_text):
    """'genre' when suspense / comedy is declared, 'light' when a light everyday tone is, else None."""
    fields = re.findall(r"^\|\s*(?:基调|类型|题材|genre|tone)\s*\|\s*([^|\n]*)\|", metadata_text, re.M | re.I)
    pool = " ".join([section(text, SECTION_ALIASES["overview"]), section(text, SECTION_ALIASES["look"]),
                     section(text, SECTION_ALIASES["global"]), *fields])
    if GENRE_INTENDED.search(pool):
        return "genre"
    if LIGHT_TONE.search(pool):
        return "light"
    return None


def tone_checks(text, shots, metadata_text):
    """Return (warnings, infos). text = Prompt body (E table stripped); shots as validate_prompt.split_shots."""
    warns, infos = [], []
    per_shot = [(no, shot_cues(body)) for no, _, _, body in shots]
    hits = [(no, cues) for no, cues in per_shot if cues]
    if not hits:
        return warns, infos
    tone = declared_tone(text, metadata_text)

    def describe(no, cues):
        return f"镜头{no}「" + "；".join(f"{k}：{v}" for k, v in cues.items()) + "」"

    if tone == "genre":
        infos.append("基调线索：已声明悬疑 / 喜剧类基调，" + "、".join(describe(n, c) for n, c in hits) +
                     " 按类型语法保留（S4 §4.4b）")
        return warns, infos
    if tone == "light":
        flagged = hits
        reason = "基调写了轻松 / 温暖 / 日常"
    else:
        order = [no for no, _ in per_shot]
        cue_shots = {no for no, _ in hits}
        flagged = []
        for no, cues in hits:
            i = order.index(no)
            neighbours = {order[j] for j in (i - 1, i + 1) if 0 <= j < len(order)}
            if len(cues) >= 2 or (neighbours & cue_shots):
                flagged.append((no, cues))
        reason = "基调未声明"
    for no, cues in flagged:
        warns.append(f"W35 {describe(no, cues)}：{reason}——停住 / 慢转头 / 盯住加压低声音 / 无状态的逼近 / 低头抬眼是悬疑语法，成片会读成惊悚 [实测]；"
                     f"轻松场写继续做的事（嚼、手上的活不停）、下巴放平顺着对方的方向看一眼、压着笑、来人写手里 / 步子 / 肩膀，环境声照常；"
                     f"真要悬疑 / 喜剧就在【总述】或【贯穿要求】声明基调（S4 §4.4b）")
    return warns, infos
