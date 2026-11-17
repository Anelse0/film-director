"""Wording the model executes literally (W46-W49), stdlib only — 1.9.0.

Trigger case [实测] (`validation-log.md` evidence #8, 2026-10-18 / 19): the first render crushed the dialogue together,
gave the lead a wide-eyed open-mouth face, put the agent's phone flat in both palms, turned "捂住手机话筒" into a hand
over her mouth, and put the door on the wrong side of him. Every one of these came from a
phrase in the prompt, every one was already a written rule in the project's director guide, and none of them was
caught by the validator. The user named the cause of the first one directly: "不是 shot 时长的问题，是台词前面的描述的问题".
These are review hints (WARN): a reviewed design keeps them with a reason in QA.

  W46  方位词     (a) a character's own left / right used as a screen position: 右肩旁边 / 头的右边 / 他左手边 / 往左挪,
                  outside an over-the-shoulder construct and with no 画左 / 画右 in the same clause. A character facing the
                  camera has his right side on frame left, so the model can resolve either way (evidence #8: 门框在他
                  右肩旁边 next to 门左边那截窄墙).
                  (b) an over-the-shoulder shot whose shoulder side disagrees with the frame corner it is said to occupy
                  (过 X 右肩 … 画左下角是 X 的右肩: with the back to the camera the right shoulder is frame right).
                  (c) a landmark-relative side (门左侧 / 走廊左侧 / 桌子右边) that is neither defined in a 【素材绑定】 line
                  carrying a 画左 / 画右 translation nor anchored by 画左 / 画右 in the same clause. 走廊左侧 changes side
                  when the camera turns round.
                  A hand that holds something (右手拿着手机) is not a position and is not reported.
  W47  台词括号快慢  a speed word in the dialogue bracket (语速快 / 飞快 / 很快 / 急促 / 一口气说 / 抢着 / 赶着 / 捂着话筒),
                  or a fast voice in the 【贯穿要求】 voice line (女声，干脆、快). The model compresses the whole line. Negated
                  forms (不赶 / 不快) and 轻快 (a timbre) are not reported. INFO lists the softer words still in brackets
                  (语速 / 压低 / 压着声音 / 利落) so the reviewer sees them; the project decides whether they count.
  W48  手持道具    a held phone / cup / bottle / water / microphone with no grip phrase in the shot (正常握 / 握着 / 托在 /
                  捏着 / 拎着 / 夹着 …) and no 手： line in 【贯穿要求】 — once per prop per clip (rendered as both palms
                  cradling the phone); and 捂 … 话筒 / 听筒 / 麦克风 anywhere (rendered as a hand over the mouth).
  W49  表演幅度词   flustered / wide-eyed / gritted-teeth words (慌慌张张 / 慌着 / 瞪大 / 睁圆 / 张大嘴 / 牙关一咬 / 狼狈 /
                  抓了两下 …), negated forms excepted: WARN per unit when the prompt declares a light tone (轻松 / 日常 /
                  生活化 …), INFO when it declares comedy / suspense or nothing (those genres use big faces on purpose).
"""
import re

from guide_checks import section_text
from prompt_structure import SPEECH_RE
from tone_checks import GENRE_INTENDED, LIGHT_TONE

CLAUSE_SPLIT = re.compile(r"[，。；,;\n]")
FRAME_SIDE = re.compile(r"画左|画右|画面(?:中间)?偏?[左右]|画面[左右](?:侧|边|下角|上角)")

# W46
SHOULDER = re.compile(r"(?<![左右])([左右])肩(?:膀|头)?")
PERSON_SIDE = re.compile(r"(?:(?<!镜)头部?|身体|(?<![镜转])身|他|她)的?([左右])(?:边|侧|手边)")
STEP_SIDE = re.compile(r"往([左右])(?:挪|移|走|退|跨|迈|靠|让)")
LANDMARK_SIDE = re.compile(r"(?:门|窗|桌子?|镜台|吧台|走廊|墙|柜子?|沙发|床|电梯|楼梯|窗户)(?:的)?([左右])(?:边|侧)")
OTS = re.compile(r"过肩|越肩|(?:过|越过)[^，。；\n]{0,10}?肩")
CORNER = re.compile(r"画面?([左右])下角|([左右])下角")
RULE_SENTENCE = re.compile(r"不指|不写人物|一律指画")

# W47
SPEED = re.compile(r"(?<!不)(?:语速[^，、）)]{0,3}快|飞快|很快|快速|急促|一口气(?:说|念|讲|读)|连珠炮|抢着说?|赶着说?|捂着?(?:手机)?话筒|捂住(?:手机)?话筒)")
SOFT_SPEED = re.compile(r"语速|压低|压着声音|利落")
VOICE_FAST = re.compile(r"[男女]声[^；。\n]{0,12}?(?<!不)(?<!轻)快")

# W48
HELD = re.compile(r"(?:拿|握|捧|举|端|攥|托|贴到|贴在|递|接过|拎)(?:着|起|住|上)?[^，。；\n]{0,6}?(?P<p>手机|电话|杯子?|酒杯|瓶子?|瓶装水|一瓶水|水杯|话筒|麦克风)")
GRIP = re.compile(r"正常握|握着|握法|托在|捏着|拎着|夹着|握住(?:瓶|杯|手机)|握瓶|握杯|四指")
COVER = re.compile(r"捂(?:住|着)?[^，。；\n]{0,4}?(?:话筒|听筒|麦克风)")
HAND_LINE = re.compile(r"(?:^|[。\n])\s*手\s*[：:]")

# W49
EXAG = re.compile(r"(?<!不)(?<!不要)(?<!别)(?:慌慌张张|慌张|慌着|慌乱|手忙脚乱|吓了?一跳|瞪大|瞪眼|睁圆|睁大|张大嘴|嘴张成"
                  r"|牙关一咬|咬紧牙|咬牙|脸一垮|狼狈|大惊|惊得|猛地|手足无措|抓了?两下)")

UNIT_ORDER = ("起始状态", "贯穿要求")


def units(text, shots):
    """[(name, body)] — 起始状态, every shot, 贯穿要求. 【素材绑定】 is read separately (definitions)."""
    out = []
    opening = section_text(text, "起始状态")
    if opening:
        out.append(("起始状态", opening))
    out.extend((f"镜头{no}", body) for no, _, _, body in shots)
    glob = section_text(text, "贯穿要求")
    if glob:
        out.append(("贯穿要求", glob))
    return out


def defined_landmarks(text):
    refs = section_text(text, "素材绑定")
    found = set()
    for line in refs.splitlines():
        if FRAME_SIDE.search(line):
            found |= {m.group(0) for m in LANDMARK_SIDE.finditer(line)}
    return found


def side_words(name, body, defined):
    hits = []
    shoulders_ots = []
    is_ots = bool(OTS.search(body))
    for clause in CLAUSE_SPLIT.split(body):
        if not clause.strip() or RULE_SENTENCE.search(clause):
            continue
        anchored = bool(FRAME_SIDE.search(clause))
        for m in SHOULDER.finditer(clause):
            if is_ots:
                shoulders_ots.append(m.group(1))
            elif not anchored:
                hits.append(m.group(0))
        if not anchored:
            hits += [m.group(0) for m in PERSON_SIDE.finditer(clause)]
            hits += [m.group(0) for m in STEP_SIDE.finditer(clause)]
        for m in LANDMARK_SIDE.finditer(clause):
            if m.group(0) not in defined and not anchored:
                hits.append(m.group(0))
    msgs = []
    if hits:
        msgs.append(f"W46 {name} 方位用了人物自己或地标的左右 {sorted(set(hits))}：人面对镜头时他的右边在画左，"
                    "按镜头写画左 / 画右；指手写「靠门那只手（画左那只）」；地标的左右在【素材绑定】定义一次并写明画左 / 画右")
    if shoulders_ots:
        corners = {a or b for a, b in CORNER.findall(body)}
        sides = set(shoulders_ots)
        if corners and sides != corners:
            msgs.append(f"W46 {name} 过肩镜写了「{'、'.join(s + '肩' for s in sorted(sides))}」，前景却在画面"
                        f"{'、'.join(sorted(corners))}下角：背对镜头的人右肩在画右，两处要一致（直接写「画X下角是他虚化的肩」）")
    return msgs


def wording_checks(text, shots, metadata_text=""):
    warns, infos = [], []
    pool = section_text(text, "总述") + section_text(text, "贯穿要求") + section_text(text, "画面基调")
    genre, light = bool(GENRE_INTENDED.search(pool)), bool(LIGHT_TONE.search(pool))
    defined = defined_landmarks(text)
    glob = section_text(text, "贯穿要求")
    has_hand_line = bool(HAND_LINE.search(glob))
    held_seen, soft = set(), []
    exag_info = []
    for name, body in units(text, shots):
        warns.extend(side_words(name, body, defined))
        for m in SPEECH_RE.finditer(body):
            bracket = m.group("cn") or m.group("en") or ""
            fast = SPEED.findall(bracket)
            if fast:
                warns.append(f"W47 {name} 台词括号里有快慢词 {fast}：模型会把整句挤着说；括号只写语言、情绪 / 口气、音量和距离，"
                             "节奏交给【贯穿要求】的全局语速句；先删这些词，不先改时长")
            elif SOFT_SPEED.search(bracket):
                soft.append(f"{name}：{'、'.join(sorted(set(SOFT_SPEED.findall(bracket))))}")
        cover = COVER.findall(body)
        if cover:
            warns.append(f"W48 {name} 「{cover[0]}」会被生成成用手捂嘴：写成把手机从耳边拿下来，或不写这个动作")
        if name.startswith("镜头") and not has_hand_line and not GRIP.search(body):
            for m in HELD.finditer(body):
                prop = m.group("p")
                if prop not in held_seen:
                    held_seen.add(prop)
                    warns.append(f"W48 {name} 手里的「{prop}」没写哪只手、怎么握，【贯穿要求】也没有「手：」一行：会被生成成两手捧着、"
                                 "平放在掌心；写明哪只手、正常握法（四指托背面、拇指在屏幕一侧）、另一只手在干什么（每条每件道具报一次）")
        # W49 (表演幅度词) retired in 1.12.0: folded into W57 (layer_checks.py), dictionary = externalization lexicon.
    for m in VOICE_FAST.finditer(glob):
        warns.append(f"W47 【贯穿要求】声音行「{m.group(0)}」：音色里写快，模型会把这个人的每句都挤着说；只写年龄、音色和口气")
    if soft:
        infos.append("台词括号里的语速 / 音量词（待审）：" + "；".join(soft))
    return warns, infos
