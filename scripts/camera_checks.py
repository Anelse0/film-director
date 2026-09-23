"""Camera-library use in a compiled Prompt (film-director 1.8.0). Review hints, not a style scorer.

E-layer row (optional):  | 运镜来源 | 镜1 shot-19 原文；镜3 shot-08 填写；镜4 库外 |
  填写 (default) = the entry's five parts filled with this shot's content; 原文 = verbatim, only when the user
  asked for it; 库外 = not from the library.

W34  a shot copies the library's generic sentences (Movement / Speed / Framing / End, >= 5 words) or carries
     the English five-part skeleton (Camera: … Movement: … End:) inside a Chinese Prompt, and the shot is
     not declared 原文 — fill the parts with this shot's subject, side, pace, what stays constant, and end frame.
W35  the 运镜来源 row does not hold: unknown entry id, unknown shot number, 原文 without an entry id, or an
     unreadable mode.
Only verbatim English copies are detectable; a word-for-word Chinese translation of the generic sentence is not.
"""
import re

from camera_library import PARTS, library_phrases, load_library, norm

MODES = ("填写", "原文", "库外")
SKELETON = re.compile(r"\b(Camera|Movement|Speed|Framing|End)\s*:", re.I)
CJK = re.compile(r"[一-鿿]")
QUOTED = re.compile(r"[\"“][^\"”]*[\"”]")


def sources(metadata_text):
    """Parse the 运镜来源 row → ({shot: (id or None, mode)}, problems)."""
    m = re.search(r"^\|\s*运镜来源\s*\|\s*([^|\n]*)\|", metadata_text, re.M)
    if not m:
        return {}, []
    out, problems = {}, []
    for part in re.split(r"[；;，,]", m.group(1)):
        part = part.strip()
        if not part or part in ("无", "—", "-"):
            continue
        sm = re.match(r"镜头?\s*(\d+)\s*(shot-[0-9a-z]+)?\s*(\S+)?$", part, re.I)
        if not sm:
            problems.append(f"运镜来源「{part}」读不出：写成「镜N shot-XX 填写 / 原文」或「镜N 库外」")
            continue
        shot, eid, mode = int(sm.group(1)), sm.group(2), sm.group(3) or ("填写" if sm.group(2) else None)
        if mode not in MODES:
            problems.append(f"运镜来源「{part}」的方式应为 {' / '.join(MODES)}")
            continue
        if mode != "库外" and not eid:
            problems.append(f"运镜来源「{part}」写了{mode}却没有条目编号")
            continue
        out[shot] = (eid.lower() if eid else None, mode)
    return out, problems


def camera_checks(shots, metadata_text, entries=None):
    """shots: [(no, start, end, body)] → (warnings, infos, declared)."""
    entries = entries or load_library()
    phrases = library_phrases(entries)
    declared, problems = sources(metadata_text)
    warns, infos = [], []
    numbers = {int(no) for no, *_ in shots}
    for shot, (eid, mode) in sorted(declared.items()):
        if shot not in numbers:
            problems.append(f"运镜来源写了镜{shot}，Prompt 里没有这一镜")
        if eid and eid not in entries:
            problems.append(f"运镜来源镜{shot} 的 {eid} 不在运镜库里（camera_library.py --list）")
    for p in problems:
        warns.append(f"W35 {p}")
    for no, _s, _e, body in shots:
        no = int(no)
        eid, mode = declared.get(no, (None, None))
        if mode == "原文":
            infos.append(f"运镜：镜{no} {eid} 原文（用户指定）")
            continue
        text = norm(QUOTED.sub(" ", body))
        hits = sorted({f"{i} {part}" for phrase, i, part in phrases if phrase in text})
        labels = {m.group(1).lower() for m in SKELETON.finditer(body)}
        prose = QUOTED.sub("", body)
        chinese = len(CJK.findall(prose)) > len(re.findall(r"[A-Za-z]+", prose))
        if hits:
            warns.append(f"W34 镜头{no} 照抄运镜库通用句（{', '.join(hits)}）：按本镜填写——谁在画面哪里、"
                         f"什么保持不变、止于什么构图；确要原文，在 E 层运镜来源写「镜{no} shot-XX 原文」")
        elif chinese and len(labels) >= 3:
            warns.append(f"W34 镜头{no} 中文 Prompt 里夹着英文运镜五段骨架（{'/'.join(sorted(labels))}）："
                         f"译成本镜的中文运镜句；确要原文，在 E 层运镜来源写「镜{no} shot-XX 原文」")
        if eid:
            infos.append(f"运镜：镜{no} {eid} {mode}")
    return warns, infos, {k: {"id": v[0], "mode": v[1]} for k, v in declared.items()}
