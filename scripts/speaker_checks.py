"""Speaker attribution of off-screen lines (1.11.0; S5 §5.2 第 6 步, S6 §6.2 台词条, duration-rhythm §九).

The official guide (Doubao Seedance 2.5 提示词指南) writes off-screen sound three ways: `角色（V.O.）说："…"` over the
character's own close-up with the lips written closed, `画外音："…"` in an advert shot, and a plain `台词 (角色): "…"`
on shots where the speaker is not in frame (the 30 s example's rocket wide shots); its four-person case excludes
"错误人物发声、多人同时说话" in the prompt itself. No official or platform guide shows a line carried across a cut onto
another character's face (checked 2026-11: Volcano guide and tutorial, Dreamina, Higgsfield, Runway, fal, WaveSpeed).
Both codes were render lessons through 1.15.x. 1.16.0 (user decision 2026-11-21, references/shot-requirements.md
R1): off-screen sound is an ordinary technique — 句中切听者 / 先闻其声 / 画外整句 / 旁白与 V.O. — and the evidence row that
banned it was withdrawn. W54 / W55 now check that an off-screen segment is written out in full (whose voice — the first
item of the 台词（…） bracket —, the visible listener's mouth closed, the line count and exclusion sentences in
【贯穿要求】); a complete one is an INFO. They are ordinary WARNs, no longer render lessons.

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
CLOSED_MOUTH_RE = re.compile(r"闭着嘴|合着嘴|抿着嘴|没有?出声|不出声|没有?说话|没开口|不开口|嘴闭着|嘴唇闭合|闭口|含着烟|咬着|mouth (?:closed|shut)|lips? closed", re.I)
LINE_COUNT_RE = re.compile(r"只有这?\s*[0-9一二两三四五六七八九十]+\s*句台词|此外没有人说话|除此之外没有人说话|nothing else (?:is )?spoken|only (?:these|the) \w+ (?:scripted )?lines?", re.I)
VO_RE = re.compile(r"V\.?O\.?|内心独白|心声", re.I)
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
    floor = min_shot(metadata_text)  # kept for callers that read the E-layer key; no longer a W55 condition (1.16.0)

    has_count = bool(LINE_COUNT_RE.search(global_text))

    def tag_details(body, text_start):
        for speaker, details, line in speech_tags(body):
            if line.strip() and line.strip()[:12] in text_start:
                return details
        return ""

    def missing(body, speaker):
        """What an off-screen segment written in this shot still lacks (R1)."""
        lacks = []
        face = other_face_in_frame(body, speaker, names)
        if face and not CLOSED_MOUTH_RE.search(picture_text(body)):
            lacks.append(f"没写{face}闭着嘴")
        if not has_exclusion:
            lacks.append("【贯穿要求】没有「排除错误人物发声、多人同时说话」")
        if not has_count:
            lacks.append("【贯穿要求】没有「全条只有这 N 句台词，此外没有人说话」")
        return lacks

    # W54: one line carried across two shots (句中切听者 / 先闻其声) — is the off-screen half written out in full?
    split_hits = {}
    rows = sorted([r for r in (dialogue or []) if r.get("explicit") and r.get("shot")], key=lambda r: (r["start"], r["end"]))
    for a, b in zip(rows, rows[1:]):
        if normalize_speaker(a["speaker"]) != normalize_speaker(b["speaker"]) or a["shot"] == b["shot"]:
            continue
        body_a, body_b = body_of.get(str(a["shot"]), ""), body_of.get(str(b["shot"]), "")
        off_a = bool(OFF_RE.search(tag_details(body_a, a["text"])))
        off_b = bool(OFF_RE.search(tag_details(body_b, b["text"])))
        # one sentence carried across the cut: the first half is not a finished sentence (no closing 。！？), or the
        # prose says so (接上 / 后半句 / 同一个声音). Two finished sentences in two shots are two lines, not a split —
        # the off-screen one is then a 画外整句 and W55 looks at it.
        unfinished = not re.search(r"[。！？.!?…]\s*$", a["text"].strip())
        if ((off_a or off_b) and unfinished) or SPLIT_WORDS_RE.search(body_b):
            off_shot = str(a["shot"]) if (off_a and not off_b) else str(b["shot"])
            split_hits[(str(a["shot"]), str(b["shot"]))] = (normalize_speaker(a["speaker"]), a["text"][:20], b["text"][:20],
                                                           off_shot, "先闻其声" if (off_a and not off_b) else "句中切听者")
    for no, s, e, body in shots:
        if re.search(r"溢出到(?:下一|镜头)|落在下一镜|最后几个词落在|这句的最后", body):
            lines = speech_tags(body)
            spk = lines[-1][0] if lines else "？"
            warns.append(f"W54 镜头{no}→镜头{no + 1} {spk} 的台词写成溢出到下一镜：一句要跨镜时分成两段、各写在各的镜里，"
                         f"画外那段写 台词（{spk}，画外音，…）并写全（shot-requirements R1；duration-rhythm §九）")
    if TRACK_SPLIT_RE.search(metadata_text or ""):
        infos.append("E 层「台词轨」写了跨镜 / 拆句：按 shot-requirements R1 分成两段、各写各的镜，台词轨仍写「连续」")
    for (shot_a, shot_b), (spk, ta, tb, off_shot, kind) in sorted(split_hits.items(), key=lambda x: int(re.sub(r"\D", "", x[0][0]) or 0)):
        lacks = missing(body_of.get(off_shot, ""), spk)
        if not OFF_RE.search(tag_details(body_of.get(off_shot, ""), tb if off_shot == shot_b else ta)):
            lacks.insert(0, f"镜头{off_shot} 那一段的括号没标「画外音」")
        if lacks:
            warns.append(f"W54 镜头{shot_a}→镜头{shot_b} {spk} 的一句分在两镜（{kind}：「{ta}」/「{tb}」），画外段还没写全："
                         f"{'；'.join(lacks)}（shot-requirements R1；duration-rhythm §九）")
        else:
            infos.append(f"画外段 镜头{shot_a}→镜头{shot_b}：{spk}（{kind}），写法齐——是谁的声音、画里的人闭着嘴、句数与排除句"
                         f"（R1；[未验证] 没有官方范例，成片回来记 validation-log，待验证 24）")
    carried = {v[3] for v in split_hits.values()}

    # W55: a whole off-screen line / V.O. over a visible face — is it written out in full?
    for no, s, e, body in shots:
        tag = tag_of(body)
        if WIDE_TAG_RE.search(tag) and not CLOSE_TAG_RE.search(tag):
            continue
        for speaker, details, line in speech_tags(body):
            if not OFF_RE.search(details) or str(no) in carried:
                continue
            where = f"镜头{no}（{s:g}-{e:g}s）"
            if NARRATION_RE.search(details):
                continue
            if VO_RE.search(details) and speaker in picture_text(body):
                if not CLOSED_MOUTH_RE.search(picture_text(body)):
                    warns.append(f"W55 {where} {speaker} 的 V.O.「{line[:20]}」：同镜没写 {speaker} 嘴唇闭合（shot-requirements R1；官方 V.O. 范例的写法）")
                continue
            face = other_face_in_frame(body, speaker, names)
            if not face:
                continue
            lacks = missing(body, speaker)
            if lacks:
                warns.append(f"W55 {where} {speaker} 的台词「{line[:20]}」是画外音，画里是 {face} 的脸，画外段还没写全："
                             f"{'；'.join(lacks)}（shot-requirements R1）")
            else:
                infos.append(f"画外整句 {where}：{speaker} 的声音在画外、{face} 闭着嘴、有句数与排除句，写法齐（R1；成片回来记账本，待验证 24）")
    return warns, infos
