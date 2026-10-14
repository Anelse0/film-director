"""Intent in the dialogue bracket without an eye beat (W44 + INFO), stdlib only — 1.7.0.

The official format `角色台词（情绪）：内容` `[官方]` lets the bracket carry an emotion or manner word. After 1.6.0 moved every
delivery note before the colon, shot cards began to park subtext there ("真诚放在台词语气里") and even actions ("抬眼，笑一下").
The bracket is the voice slot: an intent written only there has no visible destination `[推论]`, and an action written there is
performance with no shot-line home (whether the model renders bracketed actions is `[未验证]`, validation-log 待验证 19).
Rule (S4 §4.4c 第 7 条): manner / emotion words (轻松 / 随口 / 带笑 / 语气平常) may stay in the bracket — they are 口气; an intent
word (what the line does to the other person: 真诚 / 不推销 / 认出熟客 / 是真想知道 / 没有要拒绝的意思) needs an eye beat for the
speaker somewhere in the shot line of a close shot (眼睛先亮一下 / 眼睛留在对方脸上，嘴角带着笑, or a 视线 line that changes); a
hand action alone does not replace it; actions go into the shot line as the beat before the line. Nothing in the bracket is
deleted. One W44 per shot.

  W44  括号里的动作      抬眼 / 看向 / 笑一下 / 抬杯 / 点了头 … in the bracket → written into the shot line as the beat before the line.
  W44  态度无眼神拍子    an intent token in the bracket of an on-screen line in a close shot (特写 / 近景 / 中近景) and no eye /
                        face beat or changing 视线 line attributed to that speaker anywhere in the shot line.
  INFO 画外 / 中景       an off-screen speaker's intent lands on the listener's reaction or the next shot (reported only when the
                        shot and the next shot's opening show neither); a wide shot (中景 and wider) does not carry part-level
                        expression, the intent lands in the next closer shot — both are reminders.
"""
import re

from prompt_structure import SPEECH_RE
from focus_checks import tag_of, normalize_speaker, character_names, CHANNEL_RE, VARIATION_FIELD_RE, SOUND_CLAUSE_RE

TOKEN_SPLIT_RE = re.compile(r"[，,、/／；;]")
WINDOW_RE = re.compile(r"^-?\d+(?:\.\d+)?\s*(?:s|秒)?\s*[-–—~]\s*-?\d+(?:\.\d+)?\s*(?:s|秒)?$")
LANG_RE = re.compile(r"中文|普通话|粤语|英语|英文|日语|韩语|法语|德语|方言|口音$|^(?:English|Mandarin|Cantonese|Japanese|Korean|French|German)$", re.I)
POSITION_RE = re.compile(r"画[左右]|前景|后景|背对|片中|传出|电话|屏幕|车载|免提|听筒|扬声器|音响|广播|对讲|画外|旁白|内心独白|off[- ]screen|\bV\.?O\.?|\bphone\b", re.I)
TIMING_RE = re.compile(r"同时说|的同时|边\S{1,3}边|一说完|接着说|接着刚才|补一句|补完|说时|说到|戛然|盖过|跑着喊|边走边|就接|断开|起音|重读|轻读|跨镜"
                       r"|延续到|句尾|句子延续|同时|顺手补|紧接|抢在|接上|接下去|说完即|说着")
ACTION_RE = re.compile(r"抬(?:了)?(?:一下)?眼|看向|看着|看回|看了|瞥|望向|望着|点(?:了)?(?:一下)?头|摇(?:了)?头|抬手|抬杯|抬一下|抬起|举(?:起|杯|手)|低(?:下)?头"
                       r"|转头|回头|皱眉|挑眉|眨(?:了)?眼|耸肩|前倾|靠(?:近|回|在|过去)|伸手|放下|手指|笑(?:了)?一下|一笑|笑了|咬(?:着|住|唇)|吞(?:咽|了)|舔"
                       r"|板着脸|板起|脸.{0,2}板|压着笑|憋着笑|走近|走过来|推了|搭在|捏|扶住|拍(?:了)?一?下"
                       r"|\bglance|\bnods?\b|shakes (?:his|her) head|looks (?:at|up|away|back)|raises|lowers", re.I)
INTENT_RE = re.compile(r"真诚|真心|真想|真高兴|实话|实在|不推销|不是玩笑|没有要|没要|认出|这次|顺着|像在|像是在|说得|故意|半开玩笑|开玩笑|挑衅|打趣|试探"
                       r"|服软|松口|抱怨|撒娇|讨好|示好|认输|否认|敷衍|应付|客气|逗|堵|催|让他|让她|让对方|招呼|提醒|劝|哄|安抚|拒绝|解释|回应|回答|接话"
                       r"|安慰|认真了|藏着|不说破|不想|想让|想知道|好奇|试着|恳求|命令|威胁|警告|嘲|讽|怼|噎|服气|不服|意外|委屈|心虚|撒谎|隐瞒"
                       r"|sincere|genuine|teasing|meaning it|not selling|half[- ]joking|as if|testing|coaxing|pleading|deflect|earnest", re.I)
VOICE_RE = re.compile(r"声|音|语速|吐字|连读|拖音|沙哑|清亮|低沉|洪亮|压低|放低|不高|偏低|偏高|\d+\s*岁|男|女|年轻|口音|匀速|停顿|停\s*\d|含糊|闷|收音"
                      r"|利落|干脆|平稳|咬字|吞字|吞音|放慢|放缓|加快|提速|气声|清楚|清晰|轻松|随意|随口|随性|松弛|懒洋洋|不急|温和|轻快|平平|认真"
                      r"|带笑|带着笑|笑着|笑意|含笑|语气|口气|口吻|腔|调|^轻$|^快$|^慢$|^轻声$|^小声$|^大声$|轻一点|慢一点|快一点", re.I)
EN_VOICE = {"quiet", "quietly", "soft", "softly", "low", "loud", "loudly", "fast", "slow", "slowly", "whisper", "whispering", "hoarse",
            "flat", "even", "clipped", "murmur", "murmuring", "breathy", "raspy", "volume", "pace", "voice", "calm", "calmly", "gentle",
            "gently", "light", "lightly", "warm", "warmly", "normal", "and", "but", "a", "the", "with", "very", "slightly", "bit", "tone"}
EN_WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
CJK_RE = re.compile(r"[一-鿿]")

CLOSE_TAG_RE = re.compile(r"近景|特写|中近|close|medium[- ]close", re.I)
WIDE_TAG_RE = re.compile(r"中景|中全景|全景|远景|大全景|wide|full shot|long shot", re.I)
MONOLOGUE_RE = re.compile(r"内心独白|旁白|voice[- ]?over|narrat", re.I)
MOUTH_CLOSED_RE = re.compile(r"闭着嘴|抿着?嘴|不出声|嘴[^，。]{0,4}闭|嘴唇合着|合着嘴|闭唇|嘴唇闭合|mouth (?:stays )?closed|lips (?:pressed|closed)", re.I)
FACE_BEAT_RE = re.compile(r"(?<!刺)眼(?!镜)|眉|嘴角|嘴唇|下巴|下颌|脸|(?<!说)(?<!玩)笑(?!声|话|容)|眨|瞳|目光|神情|表情"
                          r"|\b(?:eye|eyes|brow|lip|lips|jaw|smile|smiles|face)\b", re.I)
GAZE_LABEL_RE = re.compile(r"^\s*视线(?:落点)?\s*[:：]\s*")
GAZE_CHANGE_RE = re.compile(r"先|再|回到|看回|看一眼|转|落到|移|抬|又|然后|→|从|回")
FRAMING_RE = re.compile(r"止于|推到|居中|看得清|占画面|镜头|机位|画面是|构图|景别|焦点")
LIGHT_RE = re.compile(r"光|照亮|在暗里|暗部|勾边|勾出|阴影|剪影")
CROWD_RE = re.compile(r"满桌|客人|几个人|台下|众人|群演|服务生|路人|记者们|人群")
PRONOUN_RE = re.compile(r"^(?:他|她|两人|二人|俩|他们|她们)")
LEAD_RE = re.compile(r"^(?:此时|然后|随即|接着|同时|说完|开口前|开口时|画外的|画外|同一时间|这时|接下来|最后|结束时|同一秒)\s*[，,]?\s*")
BRACKET_RE = re.compile(r"台词\s*[（(][^)）\n]*[)）]\s*[:：]?")
QUOTE_RE = re.compile(r"[“\"][^”\"\n]*[”\"]")


def classify(details):
    """Split the bracket content; return (speaker, channel, actions, intents)."""
    tokens = [t.strip() for t in TOKEN_SPLIT_RE.split(details or "") if t.strip()]
    speaker = normalize_speaker(tokens[0]) if tokens else ""
    channel = bool(CHANNEL_RE.search(details or ""))
    actions, intents = [], []
    for token in tokens[1:]:
        if WINDOW_RE.match(token) or LANG_RE.search(token) or POSITION_RE.search(token) or TIMING_RE.search(token):
            continue
        if CJK_RE.search(token):
            if ACTION_RE.search(token):
                actions.append(token)
            elif INTENT_RE.search(token):
                intents.append(token)
            elif VOICE_RE.search(token):
                continue
            elif len(CJK_RE.findall(token)) >= 5:
                intents.append(token)
            continue
        words = [w.lower() for w in EN_WORD_RE.findall(token)]
        if not words:
            continue
        if ACTION_RE.search(token):
            actions.append(token)
        elif INTENT_RE.search(token) or any(w not in EN_VOICE for w in words):
            intents.append(token)
    return speaker, channel, actions, intents


def leading_name(piece, names):
    piece = LEAD_RE.sub("", piece.strip())
    for name in sorted(names, key=len, reverse=True):
        if piece.startswith(name):
            rest = piece[len(name):len(name) + 1]
            if re.search(r"[A-Za-z]$", name) and re.match(r"[A-Za-z]", rest or ""):
                continue
            return name
    return None


def clauses(body, names):
    """[(subject, text, is_gaze)] for the shot line with the tag, brackets, quotes, 【变化】 and 声音 clauses removed. A
    clause starts where a name or a pronoun leads; a clause with neither inherits the sentence's current subject."""
    prose = VARIATION_FIELD_RE.sub("", body)
    tag = tag_of(body)
    if tag:
        prose = prose.replace("【" + tag + "】", "", 1).replace("[" + tag + "]", "", 1)
    prose = SOUND_CLAUSE_RE.sub("", QUOTE_RE.sub("", BRACKET_RE.sub("。", prose)))
    out = []
    for sentence in re.split(r"[。；;\n]", prose):
        sentence = sentence.strip(" \t：:，,、")
        if not sentence:
            continue
        gaze = GAZE_LABEL_RE.match(sentence)
        if gaze:
            text = sentence[gaze.end():]
            out.append((leading_name(text, names), text, True))
            continue
        subject, current = None, []
        for piece in re.split(r"[，,]", sentence):
            piece = piece.strip()
            if not piece:
                continue
            name = leading_name(piece, names)
            if name or PRONOUN_RE.match(LEAD_RE.sub("", piece)):
                if current:
                    out.append((subject, "，".join(current), False))
                    current = []
                subject = name or subject
            current.append(piece)
        if current:
            out.append((subject, "，".join(current), False))
    return out


def is_face_beat(text):
    pieces = [p for p in re.split(r"[，,]", text) if not MOUTH_CLOSED_RE.search(p)]
    return any(FACE_BEAT_RE.search(p) and not FRAMING_RE.search(p) and not LIGHT_RE.search(p) and not CROWD_RE.search(p)
               for p in pieces)


UNATTRIBUTED = ""


def carriers(body, names):
    """{subject: True} for every subject with an eye / face beat or a changing 视线 line. Key None = an unnamed 视线 line
    (counts for the on-screen speakers); key UNATTRIBUTED = a beat whose subject could not be resolved (counts only as
    'some beat exists', for the off-screen rule)."""
    found = {}
    for subject, text, gaze in clauses(body, names):
        if gaze:
            if GAZE_CHANGE_RE.search(text):
                found[subject] = True
        elif is_face_beat(text):
            found[subject if subject is not None else UNATTRIBUTED] = True
    return found


def opening_beat(body, names):
    """A beat in the first two clauses of a shot (the 去处 of an off-screen speaker's intent)."""
    for subject, text, gaze in clauses(body, names)[:2]:
        if (gaze and GAZE_CHANGE_RE.search(text)) or (not gaze and is_face_beat(text)):
            return True
    return False


def subtext_checks(text, shots, dialogue):
    """Return (warnings, infos). text: D-layer body; shots: validate_prompt.split_shots(); dialogue: rows."""
    warns, infos = [], []
    if not shots:
        return warns, infos
    names = character_names(text, dialogue)
    off_screen_pending, wide_pending = [], []
    for index, (no, _, _, body) in enumerate(shots):
        tag = tag_of(body)
        wide = bool(WIDE_TAG_RE.search(tag)) and not CLOSE_TAG_RE.search(tag)
        found = carriers(body, names)
        next_body = shots[index + 1][3] if index + 1 < len(shots) else ""
        actions, uncovered = [], []
        for m in SPEECH_RE.finditer(body):
            details = m.group("cn") or m.group("en") or (m.group("speaker") or m.group("zh") or "")
            if MONOLOGUE_RE.search(details):
                continue
            speaker, channel, acts, intents = classify(details)
            if acts:
                actions.append((speaker, acts))
            if not intents:
                continue
            if channel:
                if not found and not opening_beat(next_body, names):
                    off_screen_pending.append((no, speaker, intents))
                continue
            if wide:
                wide_pending.append((no, speaker, intents))
                continue
            if not (found.get(speaker) or None in found):
                uncovered.append((speaker, intents))
        if not actions and not uncovered:
            continue
        parts, advice = [], []
        if actions:
            parts.append(f"{len(actions)} 处动作" + "".join(f"「{'，'.join(a)}」（{s}）" for s, a in actions))
            advice.append("动作写进镜头行作开口前一拍")
        if uncovered:
            parts.append(f"{len(uncovered)} 处态度" + "".join(f"「{'，'.join(i)}」（{s}）" for s, i in uncovered) + "同镜没有这个人的眼神拍子")
            advice.append("态度翻成台词窗口内的一句眼神（开口前眼睛先亮一下 / 开口时眼睛留在对方脸上，嘴角带着笑——眼神为主、幅度小，"
                          "不设计表情转折；手上的动作保留）")
        warns.append(f"W44 镜头{no} 台词括号里 " + "，".join(parts) + "：" + "；".join(advice) + "；括号里的词不删（S4 §4.4c 第 7 条）")
    if off_screen_pending:
        listed = "、".join(f"镜头{no}「{'，'.join(i)}」（{s}）" for no, s, i in off_screen_pending)
        infos.append(f"态度拍子：画外句的态度 {listed} 落在听者反应或下一镜第一拍，本镜与下一镜开头都未见——补一句听者的眼神")
    if wide_pending:
        listed = "、".join(f"镜头{no}「{'，'.join(i)}」（{s}）" for no, s, i in wide_pending)
        infos.append(f"态度拍子：中景以上不写部位级表情，{listed} 的态度留给视线行或下一个近景")
    return warns, infos
