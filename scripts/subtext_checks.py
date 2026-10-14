"""Intent in the dialogue bracket without an executable beat (W44 + INFO), stdlib only — 1.7.0, relaxed in 1.7.1.

The official format `角色台词（情绪）：内容` `[官方]` lets the bracket carry an emotion or manner word. After 1.6.0 moved every
delivery note before the colon, shot cards began to park subtext there ("真诚放在台词语气里") and even actions ("抬眼，笑一下").
The bracket is the voice slot: an intent written only there has no visible destination `[推论]`, and an action written there is
performance with no shot-line home (whether the model renders bracketed actions is `[未验证]`, validation-log 待验证 19).
Rule (S4 §4.4c 第 7 条): manner / emotion words (轻松 / 随口 / 带笑 / 语气平常) may stay in the bracket — they are 口气; an intent
word (what the line does to the other person: 真诚 / 不推销 / 认出熟客 / 是真想知道 / 没有要拒绝的意思) needs one executable beat
for the speaker in the same close shot. 1.7.1 (user decision): the carrier is the director's choice, not an eye beat — an eye /
face beat or a changing 视线 line, a hand / head / body action, a voice or pause description, an action toward the other
character, or an executable delivery word in the bracket itself (轻声 / 放慢 / 顿一拍; manner words are colour, not a carrier).
Actions go into the shot line (before or while speaking — the director decides) and once there they are the beat. Nothing in
the bracket is deleted. One W44 per shot.

  W44  括号里的动作      抬眼 / 看向 / 笑一下 / 抬杯 / 点了头 … in the bracket → written into the shot line.
  W44  态度无可执行拍子  an intent token in the bracket of an on-screen line in a close shot (特写 / 近景 / 中近景) and no beat of
                        any kind attributed to that speaker in the shot line, nor a delivery word in the bracket.
  INFO 画外 / 后景 / 中景 an off-screen, back-turned or background speaker's intent lands on the listener's reaction or the next
                        shot (reported only when the shot and the next shot's opening show no beat at all); a wide shot (中景
                        and wider) with no carrier for the speaker — body / interaction / pause can carry it there, eye-level
                        beats go to the next closer shot. A coverage line counts the intent words that found a carrier, by kind.
"""
import re

from prompt_structure import SPEECH_RE
from focus_checks import tag_of, normalize_speaker, character_names, CHANNEL_RE, VARIATION_FIELD_RE, SOUND_CLAUSE_RE

TOKEN_SPLIT_RE = re.compile(r"[，,、/／；;]")
WINDOW_RE = re.compile(r"^-?\d+(?:\.\d+)?\s*(?:s|秒)?\s*[-–—~]\s*-?\d+(?:\.\d+)?\s*(?:s|秒)?$")
LANG_RE = re.compile(r"中文|普通话|粤语|英语|英文|日语|韩语|法语|德语|方言|口音$|^(?:English|Mandarin|Cantonese|Japanese|Korean|French|German)$", re.I)
POSITION_RE = re.compile(r"画[左右]|前景|后景|背对|片中|传出|电话|屏幕|车载|免提|听筒|扬声器|音响|广播|对讲|画外|旁白|内心独白|off[- ]screen|\bV\.?O\.?|\bphone\b", re.I)
BACKGROUND_RE = re.compile(r"后景|背对|背影|背身|远处|人小|虚着|画面深处|背景里|in the background|back (?:is )?turned", re.I)
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
VOICE_RE = re.compile(r"声|音|语速|吐字|连读|拖音|沙哑|清亮|低沉|洪亮|压低|放低|不高|偏低|偏高|\d+\s*岁|男|女|年轻|口音|匀速|停顿|停\s*\d|顿|含糊|闷|收音"
                      r"|利落|干脆|平稳|咬字|吞字|吞音|放慢|放缓|加快|提速|气声|清楚|清晰|轻松|随意|随口|随性|松弛|懒洋洋|不急|温和|轻快|平平|认真"
                      r"|带笑|带着笑|笑着|笑意|含笑|语气|口气|口吻|腔|调|^轻$|^快$|^慢$|^轻声$|^小声$|^大声$|轻一点|慢一点|快一点", re.I)
# Bracket words that are themselves an executable delivery (volume / pace / pause / breath / smile in the voice) — a carrier
# for an intent word in the same bracket. Manner colour (轻松 / 随口 / 认真 / 温和) and timbre (沙哑 / 偏低 / 年轻男声) are not.
DELIVERY_RE = re.compile(r"轻声|小声|大声|低声|压低|放低|放轻|提高|不高|音量|语速|放慢|放缓|慢一点|说得慢|加快|提速|快一点|匀速|拖音|拖长|短促|停顿|停\s*\d|顿"
                         r"|气声|咬字|吐字|吞字|吞音|含糊|利落|干脆|连读|带笑|带着笑|笑着|含笑|笑意|^轻$|^快$|^慢$|轻一点"
                         r"|whisper|quiet|soft|slow|fast|\blow\b|loud|pause|clipped|breathy|murmur|smil", re.I)
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
# 1.7.1 carriers besides the eye / face beat. Body: head, hands, shoulders, torso, breath and the small actions S4 §4.4a asks
# for; static placement (坐在 / 站在 / 面朝) is not a beat. Voice: how the line is said, or a pause / holding back. Interaction:
# a verb aimed at the other character (朝 / 向 / 对着 / 给 … + name or pronoun, or a verb that implies the other).
BODY_BEAT_RE = re.compile(
    r"点(?:了)?(?:点|一下|下)?头|摇(?:了)?(?:摇|一下)?头|偏(?:过|了一下|一下|了)?头|歪头|仰(?:起)?头|低(?:下|着)?头|抬(?:起|着)?头|转(?:过|回)?头|回(?:过|了)?头|侧头|扭头"
    r"|手[^，。；]{0,8}(?:动|点|压|按|放|搭|抬|垂|伸|收|握|松|停|拢|摊|撑|敲|抠|搓|翻|掏|捏|抓|扶|擦|推|拉|递|拍|摆|挥|指|摸|端|捧|举|揉|勾|甩|顿|插|揣|撑|托)"
    r"|手指|指尖|指了指|比了|递(?:给|还|过|到|上)?|拿(?:起|着|过|出|回)|放(?:下|回|到|进)|握(?:住|着|紧)|攥|抓|捏|摸|擦|抹|敲|(?<![一半两几])拍(?!子|摄)|碰|扶|搭|撑|掏|摆手|挥|勾(?:了)?(?:勾)?|搓|揉|甩"
    r"|举(?:起|杯|手)?|端(?:起|在|着)|捧|推(?!到|荐|销|测|理|断)|拉(?:住|开|过|了)|(?<!延)伸|收(?!音)(?:起|回|到|拾)?|接过|塞|递|倒(?:进|了|酒|水)|搅|舀|滤|切|拧|系(?:上|好|着)|解开|松开|松下|松了"
    r"|靠(?:进|过去|回|近|在|着|上)|前倾|后仰|耸|挪|退(?:了)?(?:一|半|两)?步|后退|退开|转身|侧身|起身|坐下|坐直|坐回|站起|站直|直起|弯下|躬|蹲|踮|停下|顿住|停住"
    r"|肩(?:膀)?[^，。；]{0,4}(?:松|沉|塌|耸|绷|垂|落|动|晃)|身子[^，。；]{0,4}(?:前|后|侧|靠|直|沉|松|转|往)|身体[^，。；]{0,4}(?:前|后|侧|靠|直|沉|松|转|往)"
    r"|吸(?:了)?(?:一)?口气|吐(?:了)?(?:一)?口气|深吸|呼吸|叹(?:了)?(?:口)?气|喘|呼出|喝|嚼|咬|吞|舔|垂下|缩|绷|僵|抖|颤|晃|踱"
    r"|\b(?:nod|nods|nodding|shrug|shrugs|lean|leans|leaning|hand|hands|finger|fingers|shoulder|shoulders|reach|reaches|taps?|grips?|breath|breathes|sigh|sighs|sips?|steps? back|turns?|pushes|slides|hands over|passes)\b",
    re.I)
VOICE_PROSE_RE = re.compile(
    r"声音(?!\s*[:：])|嗓音|语气|口气|语速|语调|音量|放慢|说得慢|说得轻|说得快|说得很|放轻|压低|压着声|轻声|低声|小声|提高|拖长|尾音|句尾|停顿|顿了|顿一|顿住|停了一|停一|停了半|停半"
    r"|等了|等一|半拍|一拍|沉默|不说话|没说话|不出声|没出声|没(?:有)?(?:马上|立刻|急着|接着|再)?(?:接话|接茬|接|答|回答|回|说|催|问|推|劝|推荐)|不接话|才开口|才说|才答|先不"
    r"|咬字|气声|笑着说|话音|慢半拍|慢了半拍|轻轻地说|说完[^，。；]{0,4}(?:停|顿|等|没)"
    r"|\b(?:pause|pauses|beat|quiet|quietly|soft|softly|low|lower|slower|slowly|faster|whisper|whispers|murmur|murmurs|silence|says nothing|doesn't answer|waits)\b", re.I)
TOWARD_RE = r"(?:朝|向|对着|冲着|冲|给|跟着|跟|替|帮)(?:着)?\s*(?:他|她|对方|两人|俩|他们|她们|%s)"
INTERACT_VERB_RE = re.compile(r"递给|递还|递过|递到|碰杯|举杯|敬酒|拍了拍|握住|搂住|扶住|碰了碰|凑近|凑过去|靠过去|挨着|贴着|搀|推过去|推给|塞给|拉住|牵|搂"
                              r"|\b(?:hands? (?:him|her|it) |passes|toward (?:him|her)|to (?:him|her)|nudges|touches|clinks)", re.I)
GAZE_LABEL_RE = re.compile(r"^\s*视线(?:落点)?\s*[:：]\s*")
GAZE_CHANGE_RE = re.compile(r"先|再|回到|看回|看一眼|转|落到|移|抬|又|然后|→|从|回")
FRAMING_RE = re.compile(r"止于|推到|居中|看得清|占画面|镜头|机位|画面是|构图|景别|焦点")
LIGHT_RE = re.compile(r"光|照亮|在暗里|暗部|勾边|勾出|阴影|剪影")
CROWD_RE = re.compile(r"满桌|客人|几个人|台下|众人|群演|服务生|路人|记者们|人群")
PRONOUN_RE = re.compile(r"^(?:他|她|两人|二人|俩|他们|她们)")
SINGULAR_RE = re.compile(r"^(?:他|她)(?!们)")
ASIDE_RE = re.compile(r"^(?:此时|同时|同一时间|同一秒|这时)")
LEAD_RE = re.compile(r"^(?:此时|然后|随即|接着|同时|说完|开口前|开口时|画外的|画外|同一时间|这时|接下来|最后|结束时|同一秒)\s*[，,]?\s*")
BRACKET_RE = re.compile(r"台词\s*[（(]([^)）\n]*)[)）]\s*[:：]?")
QUOTE_RE = re.compile(r"[“\"][^”\"\n]*[”\"]")
SAID = "‹说›"
KINDS = ("眼神", "身体", "声音", "互动")


def speaker_of(details):
    """The first bracket token as a name; a platform handle (`@01_host`) keeps its stem when nothing else is left."""
    tokens = [t.strip() for t in TOKEN_SPLIT_RE.split(details or "") if t.strip()]
    if not tokens:
        return ""
    name = normalize_speaker(tokens[0])
    if name:
        return name
    handle = re.sub(r"演员|\s+", "", CHANNEL_RE.sub("", tokens[0]))
    return handle.lstrip("@").strip("，,、 ")


def classify(details):
    """Split the bracket content; return (speaker, channel, actions, intents)."""
    tokens = [t.strip() for t in TOKEN_SPLIT_RE.split(details or "") if t.strip()]
    speaker = speaker_of(details)
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


def bracket_delivery(details):
    """Executable delivery words in the bracket (轻声 / 放慢 / 顿一拍 / 带笑 …) — a voice carrier for the intent words beside them."""
    tokens = [t.strip() for t in TOKEN_SPLIT_RE.split(details or "") if t.strip()]
    found = []
    for token in tokens[1:]:
        if WINDOW_RE.match(token) or LANG_RE.search(token) or POSITION_RE.search(token):
            continue
        m = DELIVERY_RE.search(token)
        if m:
            found.append(token)
    return found


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
    clause starts where a name or a pronoun leads; a clause with neither inherits the sentence's current subject. 1.7.1: 他 /
    她 with no subject yet inherits the last named subject (a dialogue bracket counts as naming its speaker); 两人 / 他们
    resets it; a colon inside a sentence starts a new piece."""
    prose = VARIATION_FIELD_RE.sub("", body)
    tag = tag_of(body)
    if tag:
        prose = prose.replace("【" + tag + "】", "", 1).replace("[" + tag + "]", "", 1)
    prose = BRACKET_RE.sub(lambda m: "。" + speaker_of(m.group(1)) + SAID + "。", prose)
    prose = SOUND_CLAUSE_RE.sub("", QUOTE_RE.sub("", prose))
    out = []
    last_named = None
    for sentence in re.split(r"[。；;\n]", prose):
        sentence = sentence.strip(" \t：:，,、")
        if not sentence:
            continue
        if sentence.endswith(SAID):
            last_named = sentence[:-len(SAID)] or last_named
            continue
        gaze = GAZE_LABEL_RE.match(sentence)
        if gaze:
            text = sentence[gaze.end():]
            owner = leading_name(text, names)
            out.append((owner.lstrip("@") or owner if owner else owner, text, True))
            continue
        subject, current = None, []
        for piece in re.split(r"[，,：:]", sentence):
            piece = piece.strip()
            if not piece:
                continue
            name = leading_name(piece, names)
            stripped = LEAD_RE.sub("", piece)
            if name or PRONOUN_RE.match(stripped):
                if current:
                    out.append((subject, "，".join(current), False))
                    current = []
                if name:
                    subject = name.lstrip("@") or name
                elif not SINGULAR_RE.match(stripped):
                    subject = None            # 两人 / 他们: nobody in particular
                elif subject is None:
                    subject = last_named
            current.append(piece)
        if current:
            out.append((subject, "，".join(current), False))
        if subject and not ASIDE_RE.match(sentence):
            last_named = subject          # a 此时 / 同时 aside (the listener's mouth) does not take over 他 / 她
    return out


def beat_kinds(text, others=()):
    """The carrier kinds a clause shows: 眼神 (eye / face beat), 身体 (head / hand / body action, breath), 声音 (how the line
    is said, a pause or holding back), 互动 (a verb aimed at the other character). Pieces that describe framing, light, a
    crowd or the listener's closed mouth never count."""
    kinds = set()
    toward = re.compile(TOWARD_RE % "|".join(re.escape(n) for n in sorted(others, key=len, reverse=True)) if others else TOWARD_RE % "对方")
    for piece in re.split(r"[，,]", text):
        if MOUTH_CLOSED_RE.search(piece) or FRAMING_RE.search(piece) or LIGHT_RE.search(piece) or CROWD_RE.search(piece):
            continue
        if FACE_BEAT_RE.search(piece):
            kinds.add("眼神")
        if BODY_BEAT_RE.search(piece):
            kinds.add("身体")
        if VOICE_PROSE_RE.search(piece):
            kinds.add("声音")
        if INTERACT_VERB_RE.search(piece) or toward.search(piece):
            kinds.add("互动")
    return kinds


def is_face_beat(text):
    return "眼神" in beat_kinds(text)


def is_beat(text, others=()):
    return bool(beat_kinds(text, others))


UNATTRIBUTED = ""


def carriers(body, names):
    """{subject: {kinds}} for every subject with a beat of any kind, or a changing 视线 line (kind 眼神). Key None = an
    unnamed 视线 line (counts for the on-screen speakers); key UNATTRIBUTED = a beat whose subject could not be resolved
    (counts only as 'some beat exists', for the off-screen rule)."""
    found = {}
    for subject, text, gaze in clauses(body, names):
        if gaze:
            if GAZE_CHANGE_RE.search(text):
                found.setdefault(subject, set()).add("眼神")
            continue
        kinds = beat_kinds(text, [n for n in names if n != subject])
        if kinds:
            found.setdefault(subject if subject is not None else UNATTRIBUTED, set()).update(kinds)
    return found


def opening_beat(body, names):
    """A beat in the first two clauses of a shot (the 去处 of an off-screen speaker's intent)."""
    for subject, text, gaze in clauses(body, names)[:2]:
        if (gaze and GAZE_CHANGE_RE.search(text)) or (not gaze and is_beat(text, names)):
            return True
    return False


def subtext_checks(text, shots, dialogue):
    """Return (warnings, infos). text: D-layer body; shots: validate_prompt.split_shots(); dialogue: rows."""
    warns, infos = [], []
    if not shots:
        return warns, infos
    names = set(character_names(text, dialogue))
    for m in SPEECH_RE.finditer(text):
        details = m.group("cn") or m.group("en") or (m.group("speaker") or m.group("zh") or "")
        first = (TOKEN_SPLIT_RE.split(details) or [""])[0].strip()
        if first.startswith("@"):
            names.update({first, first.lstrip("@"), speaker_of(details)})
    names.discard("")
    off_screen_pending, wide_pending = [], []
    total, covered = 0, {k: 0 for k in KINDS + ("听者或下一镜",)}
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
                actions.append((speaker, acts, intents))
            if not intents:
                continue
            total += len(intents)
            if acts:                      # moved into the shot line, the action is the beat
                covered["身体"] += len(intents)
                continue
            if channel or BACKGROUND_RE.search(details):
                if not found and not opening_beat(next_body, names):
                    off_screen_pending.append((no, speaker, intents))
                else:
                    covered["听者或下一镜"] += len(intents)
                continue
            kinds = set(found.get(speaker, ())) | set(found.get(None, ()))
            if bracket_delivery(details):
                kinds.add("声音")
            if kinds:
                covered[next(k for k in KINDS if k in kinds)] += len(intents)
                continue
            if wide:
                wide_pending.append((no, speaker, intents))
                continue
            uncovered.append((speaker, intents))
        if not actions and not uncovered:
            continue
        parts, advice = [], []
        if actions:
            parts.append(f"{len(actions)} 处动作" + "".join(f"「{'，'.join(a)}」（{s}）" for s, a, _ in actions))
            advice.append("动作写进镜头行（开口前或开口时，由导演定）"
                          + ("，写进去后它就是同一括号里态度词的拍子" if any(i for _, _, i in actions) else ""))
        if uncovered:
            parts.append(f"{len(uncovered)} 处态度" + "".join(f"「{'，'.join(i)}」（{s}）" for s, i in uncovered) + "同镜没有这个人的可执行拍子")
            advice.append("把 S4 为这句定的载体写进镜头行——眼神 / 脸、手与身体、声音与停顿（括号里写 轻声 / 放慢 / 顿一拍 也算）、对对方的动作，"
                          "任一种，由导演设计定，不限于眼神；在台词窗口内、不另占秒数")
        warns.append(f"W44 镜头{no} 台词括号里 " + "，".join(parts) + "：" + "；".join(advice) + "；括号里的词不删（S4 §4.4c 第 7 条）")
    if off_screen_pending:
        listed = "、".join(f"镜头{no}「{'，'.join(i)}」（{s}）" for no, s, i in off_screen_pending)
        infos.append(f"态度拍子：画外 / 背对 / 后景句的态度 {listed} 落在听者反应或下一镜第一拍，本镜与下一镜开头都未见——补一句听者的反应（眼神 / 动作 / 停顿）")
    if wide_pending:
        listed = "、".join(f"镜头{no}「{'，'.join(i)}」（{s}）" for no, s, i in wide_pending)
        infos.append(f"态度拍子：中景以上 {listed} 同镜没有这个人的拍子——身体动作 / 互动 / 停顿可以写在本镜，眼神留给下一个近景")
    if total:
        hit = sum(covered.values())
        kinds = " · ".join(f"{k} {n}" for k, n in covered.items() if n)
        infos.append(f"态度拍子：{hit}/{total} 处意图词有可执行拍子" + (f"（{kinds}）" if kinds else ""))
    return warns, infos
