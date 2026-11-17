"""Clip hand-off: the first shot of a first-frame continuation keeps moving (W51), stdlib only — 1.9.0.

Trigger case [实测] (evidence #9's scene, 2026-10-19): the previous clip ended on a character calling after someone with
no answer. The next clip was cut from that last frame, and its first shot replayed the beat — "0–1s 他还看着镜头右侧的远处，
没人答，嘴角往下撇" — so the cut read as a freeze. The user asked for continuous motion: the next clip starts on the next
step of whatever was happening in the last frame (he straightens his jacket and reaches for the door). The first rewrite,
"手停在半空", tripped W35 (a freeze reads as suspense).

  W51  首镜停顿   the E-layer `上游 clip` row says this clip continues from the previous clip's last frame (尾帧 / 首帧 / 末帧),
                  and the first 120 characters of shot 1 hold the previous beat (还看着 / 没人答 / 愣 / 停住 / 停在 / 定住 /
                  不动 / 沉默 / 等着 / 半空). Write the next step of the motion in the last frame instead.
"""
import re

UPSTREAM = re.compile(r"\|\s*上游\s*clip\s*\|[^\n]*?(?:尾帧|首帧|末帧|last frame|first frame)", re.I)
HOLD = re.compile(r"还(?:在)?看着|没人答|没有人答|愣(?:住|了|在)?|停住|停在|定住|不动|沉默|等着|半空|还在等|freez|holds? still", re.I)
HEAD = 120


def continuity_checks(text, shots, metadata_text=""):
    warns = []
    if not shots or not UPSTREAM.search(metadata_text):
        return warns, []
    no, _, _, body = shots[0]
    body = re.sub(r"^【[^】]*】", "", body.strip())
    head = body[:HEAD]
    holds = sorted(set(m.group(0) for m in HOLD.finditer(head)))
    if holds:
        warns.append(f"W51 镜头{no} 接上一条末帧，开头却停在上一拍 {holds}：下一条从末帧那一刻正在做的事的下一步开始，"
                     "不把上一条最后一拍再演一遍（证据 #9）")
    return warns, []
