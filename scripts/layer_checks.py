"""A-layer vocabulary leaking into the C / D layer (W57), stdlib only — 1.12.0.

The five-layer rule says only the C layer (observable quantities) enters the Prompt; emotion labels locate intent but
cannot stand in for performance evidence. Evidence #12 (2026-10-19) showed what happens when an A-layer
word slips through: the script's "一脸'你认真的？'" became the card's "不可思议 → 皱眉、括号口气" and the Prompt's
bracket "觉得不可思议" + "一脸不信"; the render read as suspense. W40 (intensity labels) and W49 (flustered /
wide-eyed words) were two word lists for the same leak; 1.12.0 folds them into this one check whose dictionary is the
externalization lexicon itself (`references/externalization-lexicon.md`: the first column of the table plus the
"## A 层词" section). The lexicon is the vocabulary the agent writes from; the check only confirms the boundary.

  W57  镜头 N 的 C / D 层出现 A 层词 [...]：emotion / judgment / intent words (or the shapes 一脸X / 觉得X / 显得X /
       看起来X) in a shot body or a dialogue bracket. Negated uses (不 / 没 / 别 / 排除 …) are skipped. One per shot.
       Fix: keep the word in the card's A layer and the first segment of 表演翻译; translate it through a lexicon row
       (the （轻松） variants for a light scene) into parts, order and sound.
Only the 【分镜时间线】 shots are scanned: 【总述】 and 【贯穿要求】 may name the tone (轻松 / 愉快) — W35 reads those.
"""
import re
from pathlib import Path

LEXICON = Path(__file__).resolve().parents[1] / "references" / "externalization-lexicon.md"
NEGATION = re.compile(r"(?:不|没有?|别|不要|不是|不做|不会|排除|无|并非|非)\s*$")
SHAPES = re.compile(r"(?:一脸|满脸|显得|看起来|看上去|觉得|感到|感觉)(?!色|上)([^，。；：:、\s（）()“”\"]{1,6})")
VARIATION_FIELD_RE = re.compile(r"【\s*变化\s*[:：][^】]*】")
SOUND_CLAUSE_RE = re.compile(r"声音\s*[:：][^。\n]*。?")
QUOTE_RE = re.compile(r"[“\"][^”\"\n]*[”\"]")
VOICE_WORDS = {"随口", "懒洋洋", "轻描淡写", "平平的", "干脆", "带笑", "轻快", "轻声", "放慢", "顿一拍", "声音不高", "带一点笑",
               "笑着", "小声", "轻轻", "不当回事", "发现", "被提醒看", "等对方", "出去", "回答"}


def load_vocabulary(path=LEXICON):
    """A-layer words: lexicon table first column (full cell and its base before （) + every 、-separated item in the
    `## A 层词` section's `- 类名：w1、w2` lines. Returns a list sorted longest first."""
    words = set()
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        if line.startswith("|") and not line.startswith("|---") and "抽象词" not in line:
            cell = line.strip().strip("|").split("|")[0].strip()
            if cell:
                words.add(cell)
                base = re.sub(r"[（(].*$", "", cell).strip()
                for part in re.split(r"\s*/\s*", base):
                    if part:
                        words.add(part)
    section = re.search(r"^## A 层词[^\n]*\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    if section:
        for line in section.group(1).splitlines():
            m = re.match(r"\s*-\s*[^：:]+[：:]\s*(.+)$", line)
            if m:
                for w in re.split(r"[、，,]\s*", m.group(1)):
                    w = w.strip().strip("。")
                    if w and not w.startswith("（") and len(w) <= 12:
                        words.add(w)
    # Delivery / voice words are voice parameters and may stay in the bracket (lexicon "A 层词" note); they can appear in
    # a lexicon row title ("随口 / 不当回事（轻松）") without being A-layer words themselves.
    skip = {"抽象词", "类名", "示例", "例"} | VOICE_WORDS
    return sorted((w for w in words if w not in skip), key=len, reverse=True)


def scan_text(prose, vocabulary):
    """Words / shapes found in prose, negated uses skipped; in order of appearance, no duplicates."""
    found = []
    masked = prose
    for w in vocabulary:
        for m in re.finditer(re.escape(w), masked):
            if NEGATION.search(masked[max(0, m.start() - 4):m.start()]):
                continue
            if w not in found:
                found.append(w)
        masked = masked.replace(w, "＿" * len(w))
    for m in SHAPES.finditer(prose):
        if NEGATION.search(prose[max(0, m.start() - 4):m.start()]):
            continue
        hit = m.group(0)
        if hit not in found:
            found.append(hit)
    return found


BEAT_LINE_RE = re.compile(r"^\s*(?:节拍|beat)\s*[A-Za-z]?\d+[^\n]*$", re.M | re.I)


def shot_prose(body):
    """Shot text minus the legacy 【变化】 field, the dialogue quotes themselves, 声音 clauses (the bracket stays) and
    S4 beat lines (`节拍 bN（a-bs）：…` — performance original text is not rewritten, SKILL 表演任务优先路由 / 硬规则 7)."""
    text = BEAT_LINE_RE.sub("", body)
    text = VARIATION_FIELD_RE.sub("", text)
    text = QUOTE_RE.sub("“…”", text)
    return SOUND_CLAUSE_RE.sub("", text)


def layer_checks(text, shots, metadata_text="", vocabulary=None):
    """shots: [(no, start, end, body)]. Returns (warnings, infos)."""
    warns, infos = [], []
    vocab = vocabulary if vocabulary is not None else load_vocabulary()
    if not shots or not vocab:
        return warns, infos
    total = 0
    for no, _, _, body in shots:
        found = scan_text(shot_prose(body), vocab)
        if not found:
            continue
        total += len(found)
        in_bracket = [w for w in found if re.search(r"台词\s*[（(][^)）\n]*" + re.escape(w), body)]
        where = f"（台词括号里：{'、'.join(in_bracket)}）" if in_bracket else ""
        warns.append(f"W57 镜头{no} C / D 层出现 A 层词 {found}{where}：情绪 / 判断 / 意图词只在分镜卡 A 层和「表演翻译」第一段；"
                     f"按外化词典的行（轻松场用「X（轻松）」变体）翻成两半：脸和手的一半进镜头行（部位 · 先后），声音的一半进括号（口气 / 音量 / 停顿，"
                     f"例：不可思议 → 眉毛一抬、鼻子里笑出一口气 + 括号「声音不高，'啊？'的口气」）——是翻译，不是删词"
                     f"（S4 §4.4c 第 7 条，S5 §5.2 第 1 步；证据 validation-log #12）")
    infos.append(f"A 层词边界：词典 {len(vocab)} 词，分镜正文命中 {total} 处")
    return warns, infos
