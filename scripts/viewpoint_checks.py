"""Reference-image viewpoint against the camera (W52), stdlib only — 1.9.0.

Trigger case [实测] (offset EP06 场01 clip02 shot 8, 2026-10-19; `validation-log.md` 2026-10-19): the shot was designed
as a reverse — camera inside the dressing room facing the door, Theo walking in from the corridor. The scene image
@06_greenroom was bound for that one shot, and it looks the other way (from the doorway at the mirror wall). The
prompt said 灯泡镜台在镜头身后 and lit Theo with 灯泡镜的暖色光 in four places. The render put the camera in the
corridor with the mirrors behind Theo and had him walk out: the image's viewpoint beat the text, and every mention of
an object behind the camera pulled it into frame. 1.9.0 counts the mentions and flags the one risky binding. User decision
2026-10-19: camera and shot design start from the reference images the user already provided; the checker never asks
for a new or regenerated image.

  W52  镜头身后提及   a shot that places an object behind the camera (X 在镜头身后 / 镜头身后的 X / X 和 Y 都在镜头身后)
                     mentions X more than once in its own text, or more than once in the 【画面基调】 / 【贯穿要求】
                     sentences that name the shot (镜头N). One mention is the direction sentence E23 asks for; the rest
                     describe the thing the frame must not show. 灯泡镜 counts as 镜台, 水晶吊灯 as 吊灯. A landmark the
                     character walks toward or away from (门 / 车 / 床 … in a shot with a toward- or away-from-camera move)
                     is E23's business — E23 wants it anchored in every text unit that moves toward it — and is not counted.
  W52  反视角参考图   a scene reference whose binding line says not to follow its viewpoint (不参考 … 视角) and which serves
                     one shot only (named in the binding line or referenced in one shot's text). An image bound for a
                     single opposite-view shot is read as that shot's frame. S5 §5.1g: re-pick the camera among the views
                     the existing images cover (the image's own view, or the same side of the room), or keep the reverse
                     and drop that binding, writing the material and light in text. E-layer `视角说明` keeps a reviewed
                     choice (INFO).
"""
import re

from direction_checks import LANDMARK_CN, TOWARD_CAMERA_CN, AWAY_CAMERA_CN
from guide_checks import section_text

OBJ = r"灯泡镜台|镜台|灯泡镜|水晶吊灯|吊灯|梳妆台|镜子|窗户|窗|吧台|沙发|床|书架|柜台|门"
BEHIND = [re.compile(rf"(?P<o>{OBJ})[^，。；（(\n]{{0,8}}在镜头(?:身后|后方|背后)"),
          re.compile(rf"镜头(?:身后|后方|背后)(?:的)?(?P<o>{OBJ})"),
          re.compile(rf"(?P<o>{OBJ})(?:和|、|与)[^，。；\n]{{0,10}}都在镜头(?:身后|后方|背后)")]
CANON = {"灯泡镜台": "镜台", "灯泡镜": "镜台", "水晶吊灯": "吊灯", "窗户": "窗"}
COUNT_PATTERN = {"镜台": "镜台|灯泡镜", "吊灯": "吊灯", "窗": "(?<!车)窗", "门": "(?<![车柜橱快])门"}  # 车门 / 快门 are not the door behind the camera
SENTENCE = re.compile(r"[。；\n]")
NOT_VIEW = re.compile(r"不参考[^。；\n]{0,12}视角|视角[^。；\n]{0,6}不参考")
BIND_NAME = re.compile(r"^\s*@(?P<name>[^\s：:=＝，。；、（）()【】\[\]\"“”→@,;!?<>|]+)\s*[：:]", re.M)
SHOT_NO = re.compile(r"镜头\s*(\d+)")
SCENE_WORDS = re.compile(r"空间|陈设|材质|光色|场景|房间|化妆间|走廊|室内|街|scene|room|set", re.I)
OVERRIDE = re.compile(r"\|\s*视角说明\s*\|\s*([^|\n]+)\|")


def behind_objects(body):
    objs = set()
    for rx in BEHIND:
        for m in rx.finditer(body):
            objs.add(CANON.get(m.group("o"), m.group("o")))
    return objs


def viewpoint_checks(text, shots, metadata_text=""):
    warns, infos = [], []
    # E23's own 方向： sentence is required and is not counted.
    glob_sentences = [s for s in SENTENCE.split(section_text(text, "画面基调") + "。" + section_text(text, "贯穿要求"))
                      if s.strip() and not re.search(r"方向\s*[：:]", s)]
    landmark = re.compile(rf"^(?:{LANDMARK_CN})$")
    for no, _, _, body in shots:
        moving = bool(TOWARD_CAMERA_CN.search(body) or AWAY_CAMERA_CN.search(body))
        for obj in sorted(behind_objects(body)):
            if moving and landmark.match(obj):
                continue
            pat = COUNT_PATTERN.get(obj, re.escape(obj))
            visual = re.split(r"声音[：:]", body)[0]  # a sound (门被推开的声音) is not a picture of the thing
            own = len(re.findall(pat, visual))
            tag = re.compile(rf"镜头\s*{no}(?!\d)")
            glob = sum(len(re.findall(pat, s)) for s in glob_sentences if tag.search(s))
            if own > 1 or glob > 1:
                warns.append(f"W52 镜头{no} 镜头身后的「{obj}」本镜提了 {own} 次、提到镜头{no}的全局句里 {glob} 次（各留一句方向句）："
                             "多提一次就多一分被拉进画面的可能，写成光源（X 的暖光）也算；正文只写画面里有什么")
    refs = section_text(text, "素材绑定")
    override = OVERRIDE.search(metadata_text)
    for line in refs.splitlines():
        m = BIND_NAME.match(line)
        if not m or not NOT_VIEW.search(line) or not SCENE_WORDS.search(line):
            continue
        name = m.group("name")
        used = {int(n) for n in SHOT_NO.findall(line)}
        used |= {no for no, _, _, body in shots if f"@{name}" in body}
        if len(used) != 1:
            continue
        shot = next(iter(used))
        msg = (f"@{name} 绑定行写了不参考视角，且只服务镜头{shot}：只为一个反视角镜绑定的场景图会被当成这一镜的画面"
               "（offset EP06 clip02 镜 8）。按 S5 §5.1g 在现有参考图覆盖的视角里重选这一镜的机位（和图同视角或同一侧），"
               "或保留反打、这一镜不绑这张图，材质和光写进文字；不要求补图")
        if override:
            infos.append(f"反视角参考图（E 层 视角说明：{override.group(1).strip()}）：{msg}")
        else:
            warns.append("W52 " + msg)
    return warns, infos
