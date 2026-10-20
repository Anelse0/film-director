"""Speaker attribution of off-screen lines (1.11.0; S5 §5.2 第 6 步, S6 §6.2 台词条, duration-rhythm §九).

Trigger case `[实测]` offset EP06 s02 clip01 v1.6 (2026-10-19): three L-cuts put the tail of a line "画外，同一个声音接上"
on the listener's shot, each with "此时 X 闭着嘴". The render gave "The black one." to Theo, the listener whose face
filled the frame. The official guide (Doubao Seedance 2.5 提示词指南) has no off-screen-dialogue format: its only
"画外音" is an advert voice-over with nobody to mis-attribute it to, its 30 s example puts the grandmother's lines on
rocket wide shots with no other face in frame, and its four-person case excludes "错误人物发声、多人同时说话" in the
prompt itself. The evidence covers "a line is spoken while the speaker is not in frame", not "whose mouth moves when
another face is in close-up". Both codes are render lessons (fixed by default; keeping one needs the user's words).

  W54  one line split across two shots: the same speaker's consecutive lines sit in different shots and the second is
       marked 画外 / 接上 / 后半句, or the shot prose says the line spills into the next shot (溢出 / 落在下一镜), or the
       E-layer 台词轨 says 跨镜.  → merge the line back into the shot where the speaker is on screen.
  W55  an off-screen line (bracket 画外 / off-screen) lands in a shot at 中景 or closer whose picture prose gives another
       named character's face.  → put the speaker on screen, or make it a reaction shot without the line, or write the
       project's whole-line off-screen shot: shot ≥ `画外整句镜最短秒数` (3 s), the whole line inside this shot, the
       listener's mouth written closed, and the official exclusion sentence in 【贯穿要求】 — then INFO with the risk noted.
"""
import re

from focus_checks import (BRACKET_RE, FACE_RE, SPEECH_RE, SOUND_CLAUSE_RE, VARIATION_FIELD_RE, character_names,
                          normalize_speaker, tag_of)

OFF_RE = re.compile(r"画外|off[- ]screen|\bO\.?S\.?\b|\bV\.?O\.?\b", re.I)
NARRATION_RE = re.compile(r"旁白|内心独白|narrat|voice[- ]over", re.I)
SPLIT_WORDS_RE = re.compile(r"接上|后半句|后半截|接着说|同一个声音|续上|这句的最后|最后几个词|溢出到|落在下一镜|还在画外|没说完")
TRACK_SPLIT_RE = re.compile(r"\|\s*台词轨\s*\|[^|\n]*(?:跨镜|拆句)[^|\n]*\|")
WIDE_TAG_RE = re.compile(r"全景|远景|大全景|wide|establishing", re.I)
CLOSE_TAG_RE = re.compile(r"特写|近景|中近|中景|双人|过肩|越肩|close|medium", re.I)
CLOSED_MOUTH_RE = re.compile(r"闭着嘴|合着嘴|抿着嘴|没有?出声|不出声|没有?说话|没开口|不开口|嘴闭着|含着烟|咬着|mouth (?:closed|shut)", re.I)
EXCLUSION_RE = re.compile(r"错误人物发声|错人发声|多人同时说话|只有\S{1,6}(?:在)?说话时\S{0,6}动嘴")
CLAUSE_RE = re.compile(r"[。；;\n]")
MIN_SHOT_KEY = "画外整句镜最短秒数"
MIN_SHOT_DEFAULT = 3.0


def picture_text(body):
    """Shot prose without the tag, dialogue brackets and sound clauses."""
    text = VARIATION_FIELD_RE.sub("", body)
    text = re.sub(r"【[^】]*】", "", text, count=1)
    text = BRACKET_RE.sub("台词（）", text)
    return SOUND_CLAUSE_RE.sub("", text)


def speech_tags(body):
    """[(speaker, details, line)] for every dialogue tag in the shot, in order."""
    out = []
    for m in SPEECH_RE.finditer(body):
        raw = m.group("cn") or m.group("speaker") or m.group("zh") or ""
        details = m.group("cn") or m.group("en") or ""
        speaker = normalize_speaker(raw.split("，")[0].split(",")[0])
        out.append((speaker, details, m.group("line") or ""))
    return out


def other_face_in_frame(body, speaker, names):
    """Another named character's face in the picture prose: a clause naming them that also carries a face word (or
    the clause right after it, for pronouns). Back-turned / 背影-only mentions do not count."""
    prose = picture_text(body)
    clauses = [c for c in CLAUSE_RE.split(prose) if c.strip()]
    others = [n for n in names if n != speaker]
    for i, clause in enumerate(clauses):
        for name in others:
            if name not in clause:
                continue
            window = clause + (clauses[i + 1] if i + 1 < len(clauses) else "")
            if re.search(r"背影|背对|后脑|后背|背朝", clause) and not FACE_RE.search(clause):
                continue
            if FACE_RE.search(window):
                return name
    return None


def min_shot(metadata_text):
    m = re.search(r"\|\s*" + MIN_SHOT_KEY + r"\s*\|\s*([^|\n]+)\|", metadata_text or "")
    if m:
        try:
            return float(m.group(1).strip())
        except ValueError:
            pass
    return MIN_SHOT_DEFAULT


def speaker_checks(text, shots, dialogue, metadata_text=""):
    """shots: [(no, start, end, body)]; dialogue: rows from dialogue_checks. Returns (warnings, infos)."""
    warns, infos = [], []
    if not shots:
        return warns, infos
    names = character_names(text, dialogue)
    body_of = {str(no): body for no, _, _, body in shots}
    span_of = {str(no): (s, e) for no, s, e, _ in shots}
    global_text = text.split("【贯穿要求】", 1)[1] if "【贯穿要求】" in text else ""
    has_exclusion = bool(EXCLUSION_RE.search(global_text))
    floor = min_shot(metadata_text)

    # W54: one line split across two shots
    split_hits = set()
    rows = sorted([r for r in (dialogue or []) if r.get("explicit") and r.get("shot")], key=lambda r: (r["start"], r["end"]))
    for a, b in zip(rows, rows[1:]):
        if normalize_speaker(a["speaker"]) != normalize_speaker(b["speaker"]) or a["shot"] == b["shot"]:
            continue
        body_b = body_of.get(str(b["shot"]), "")
        details_b = ""
        for speaker, details, line in speech_tags(body_b):
            if line.strip() and line.strip()[:12] in b["text"]:
                details_b = details
                break
        marked = bool(OFF_RE.search(details_b)) or bool(SPLIT_WORDS_RE.search(body_b))
        if marked:
            split_hits.add((a["shot"], b["shot"], normalize_speaker(a["speaker"]), a["text"][:20], b["text"][:20]))
    for no, s, e, body in shots:
        if re.search(r"溢出到(?:下一|镜头)|落在下一镜|最后几个词落在|这句的最后", body):
            lines = speech_tags(body)
            spk = lines[-1][0] if lines else "？"
            split_hits.add((str(no), str(no + 1), spk, lines[-1][2][:20] if lines else "", ""))
    if TRACK_SPLIT_RE.search(metadata_text or ""):
        warns.append("W54 E 层「台词轨」写了跨镜 / 拆句：一句不跨镜，台词轨写「连续」（S5 §5.2 第 6 步）")
    for shot_a, shot_b, spk, ta, tb in sorted(split_hits, key=lambda x: (int(re.sub(r"\D", "", x[0]) or 0))):
        how = f"「{ta}」/「{tb}」后半句画外" if tb else f"「{ta}」句尾溢出到镜头{shot_b}"
        warns.append(f"W54 镜头{shot_a}→镜头{shot_b} {spk} 的一句拆成两段跨镜（{how}）："
                     f"一句不跨镜，合回说话人出镜的那一镜；要让听者的脸承担反应，用无台词的反应镜或双人镜"
                     f"（S5 §5.2 第 6 步；duration-rhythm §九；[实测] offset EP06 s02 clip01 v1.6 听者替说话人开了口）")

    # W55: off-screen line on another character's face
    for no, s, e, body in shots:
        tag = tag_of(body)
        if WIDE_TAG_RE.search(tag) and not CLOSE_TAG_RE.search(tag):
            continue
        for speaker, details, line in speech_tags(body):
            if not OFF_RE.search(details) or NARRATION_RE.search(details):
                continue
            face = other_face_in_frame(body, speaker, names)
            if not face:
                continue
            conditions = []
            if e - s < floor - 1e-9:
                conditions.append(f"镜长 {e - s:g}s < {floor:g}s")
            if SPLIT_WORDS_RE.search(body) or any(h[1] == str(no) for h in split_hits):
                conditions.append("不是整句（接上 / 后半句）")
            if not CLOSED_MOUTH_RE.search(picture_text(body)):
                conditions.append(f"没写{face}闭着嘴")
            if not has_exclusion:
                conditions.append("【贯穿要求】没有「排除错误人物发声、多人同时说话」")
            where = f"镜头{no}（{s:g}-{e:g}s）"
            if conditions:
                warns.append(f"W55 {where} {speaker} 的台词「{line[:20]}」画外，画里是 {face} 的脸：模型会把这句给画里那张脸"
                             f"（[实测] offset EP06 s02 clip01 v1.6）。改成 {speaker} 出镜说，或改成无台词的反应镜；"
                             f"按项目的画外整句镜写时还缺：{'；'.join(conditions)}（阈值 E 层「{MIN_SHOT_KEY}」可覆盖）")
            else:
                infos.append(f"画外整句镜 {where}：{speaker} 整句画外、{face} 闭着嘴、有排除句、镜长 ≥{floor:g}s——仍登记风险"
                             f"（[未验证] 听者近景 + 他人整句画外是否仍开口，validation-log 待验证 23）")
    return warns, infos
