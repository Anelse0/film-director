"""film-director protected zone: production/performance core hash-locked at the 1.16.0 baseline.
1.16.0 (2026-11-21): one table for writing and checking the shot deliverables — references/shot-requirements.md R1–R5
(dialogue shape and off-screen sound; the speaker is doing something taken from the story; what is deep in each frame;
deliverables carry only what is in the shot; no light in the eyes). Evidence #10 withdrawn by the user and the ban built
on it lifted: W54 / W55 / W-C8 keep their codes and now check that an off-screen segment is written out in full (no
longer render lessons). W57 gains a non-waivable eye-light group (ERROR, form check over the whole Prompt body); the
「正常人眼，不发光」 reminder is retired. W52 gains the per-shot 画面深处 slot, W13 / W-C9 the method / source marks,
S01 / C11 / W-C3 / W-C6 the new card slots (cards older than 1.16 get NOTEs). check.py prints the dock echo block.
No new code. Hashes for stage-4 / 5 / 6 / 7, emotion-performance, capabilities, genre-packs, the lexicon, the three
templates, and speaker / layer / viewpoint / guide / tone / rhythm / stage / camera-plan / qa checks, validate_prompt and
check.py re-set in the same change with a CHANGELOG entry; shot-requirements.md joins the zone.
1.16.0 previous baseline: 1.15.1.

1.15.1 (2026-11-05): `## 表演设计稿` gets a slot of its own (stage_check S01 checks presence, rows and blanks, never the
content; check.py plan gives the same finding as a note; 表演翻译's first segment comes from the draft; dock A echoes it)
and W38's budget becomes 15,000 characters of Prompt body (E-layer 字符上限; 字数上限 / 词数上限 no longer read). No new
code, no other threshold or class change. Hashes for stage-4, stage-5, stage-6, shot-card, prompt-templates,
stage_check.py, check.py and guide_checks.py re-set in the same change with a CHANGELOG entry.
1.15.1 previous baseline: 1.15.0.

1.15.0 (2026-10-27): the 25-row 执行卡 is no longer copied onto each shot card — its questions live on as the stage-5
§5.11 收口对照表 and the card answers them in its own slots (head items, 走位表, the three hand-off lines, 贯穿要求
buckets, E-layer 已知风险); stage_check.py S01–S03 check those slots directly (same codes, still ERROR; legacy cards — a
执行卡 and a skill version below 1.15 — get NOTEs) and gain notes(); check.py renames the QA machine line to 分镜检查
(`--sync` renames the legacy 执行卡 line in place) and adds three record NOTEs to `qa` (history entry > 300, 用户已点名
> 200, a repeated ## section). Records are written once: the user's words only in QA ## 历史, old review rounds are
rewritten in place, QA opens at dock A (stage-6 §6.5, stage-7, both templates). rhythm_checks.py: comment only. No new
W code, no threshold or class change; qa_check.py untouched. Hashes for stage-5, stage-6, stage-7, shot-card, qa.md,
stage_check.py, check.py and rhythm_checks.py re-set in the same change with a CHANGELOG entry.
1.15.0 previous baseline: 1.14.2.

1.14.2 (2026-10-26): project references removed from the zone — docstrings, comments and one lexicon row no longer name
the author's projects, episodes, clips or render files; they point to validation-log evidence #n instead. No rule, threshold,
code or message semantics changed (one checker message swaps a clip id for an evidence id). Hashes for those files re-set in
the same change with a CHANGELOG entry. No new W code.
1.14.2 previous baseline: 1.14.1.

1.14.1 (2026-10-21): 版本行一行制 — the shot card's head version line keeps only version · date · status · skill version · Prompt
version (plus a pointer 「改动见 QA 历史」), the Prompt E-table 版本 row only version and date; what changed per version goes to
QA `## 历史` one entry per version (the revision loop's change summary), the user's words to execution-card row 22, the script
source to a new 「剧本」 item on the card head; check.py gives a NOTE (not a code) when either line runs past 200 characters.
Wording in SKILL 交付原则, stage-5 §5.6, stage-6 §6.5, stage-7 §7.4, shot-card and qa templates, every earlier sentence kept;
hashes for those files and check.py re-set in the same change with a CHANGELOG entry. No new W code.
1.14.1 previous baseline: 1.14.0.

1.14.0 (2026-10-20): upstream docks and the revision loop (flow, not rules) — dock A 「方案」 after stage-5 §5.2 step 8
(camera table + shot overview, `check.py plan` = camera_plan_check --stage s5 + overview arithmetic, notes not codes),
dock B = the existing S5 stop (echo is the change summary + card path, the card is written as a 待确认 draft), dock C = the
existing S6 → S7 → delivery step written as a stop (the eight passes still run before the user sees the Prompt; C-point
feedback edits only the affected QA rows, design-level feedback goes back to the card); SKILL.md, stage-5 §5.2, stage-7 §7.1,
the shot-card template version line and README carry the wording, every earlier sentence kept (sentence-level diff 0 lost);
hashes for stage-5, stage-7, shot-card and check.py re-set in the same change with a CHANGELOG entry. No new W code.
1.14.0 previous baseline: 1.13.0.


1.13.0 (2026-10-20): execution mechanism only (1.12.1 cost-review proposal M1–M4) — scripts/check.py (new to the zone):
one entry point whose three sub-commands (s5 / s6 / qa [--sync]) import the four checkers' check() / validate() and merge
their output (ERROR → render-lesson WARN → other WARN → the QA number block → INFO → input sha256); `qa --sync` writes the
machine lines of the QA 现行状态 back and re-runs qa_check; scripts/evidence.py (new to the zone) prints one row of
validation-log.md by number so a rule's 「证据 #n」 is read without the whole table; SKILL.md gains five sentences (read
once, edit by section, session boundary, 续接 route, evidence pointer) and templates/qa.md title one clause. No new codes
(the new-code freeze holds), no threshold or class change; camera_plan_check / stage_check / validate_prompt / qa_check
and every rule doc keep their 1.12.1 hashes. Hashes for check.py and templates/qa.md set in the same change with a
CHANGELOG entry.

1.12.1 previous baseline. 1.12.1 (2026-10-19): content layering (review proposal §14.2) — version markers, case stories, user quotes and project
paths moved out of the rule docs into CHANGELOG / validation-log (#n rows) / the new references/checks.md code table
(not in the zone: generated from §七 + script messages); the bracket rule reworded as the voice half of the emotion's
translation (stage-4 §4.4c, stage-5 §5.2, stage-6 §6.2, lexicon, shot-card template; stage_check.py W-C10); W57 and
other script messages point to evidence ids. Rule semantics unchanged except the bracket clause. Hashes re-set in the
same change with a CHANGELOG entry.

1.12.0 previous baseline. 1.12.0 (2026-10-19): generation side of the EP06 s02 review proposal (§12) — three-segment 表演翻译 on the shot card
(stage_check.py S04 / S05 / W-C9), the dialogue bracket carries voice parameters only, A-layer words stay out of C / D
(layer_checks.py W57, new to the zone; W40 / W49 folded in, no longer emitted by guide_checks.py / wording_checks.py),
tone as a parameter (stage-4 §4.4b, scene-parameters), six light-variant rows and the "A 层词" section in the
externalization lexicon, W44 message tail (subtext_checks.py), SKILL hard rules 6 / 7 / 12 and the new-code freeze;
hashes re-set in the same change with a CHANGELOG entry. User decision: no more word-list patches; the lexicon is the
single vocabulary the agent writes from and the boundary check reads.

1.11.0 previous baseline. 1.11.0 (2026-10-19): offset EP06 s02 review proposal items 0-5 + the S5 checklist (M1) — one line does not cross a cut
(speaker_checks.py W54 / W55, new to the zone, wired into validate_prompt.py as render lessons), the W24 longest-silence
sub-item as a render lesson (rhythm_checks.py, RENDER_LESSON_PREFIXES), W28 for any camera, stage_check.py (S5 执行卡 +
镜头纵览, new to the zone), qa_check.py Q04 (user-named categories), stage-4 / 5 / 6 / 7, the shot-card and QA templates
carry the rules; hashes re-set in the same change with a CHANGELOG entry. User decision: the 1.4.0 J/L-cut default is
withdrawn after the v1.6 render gave the off-screen tail to the listener; the whole-line off-screen shot stays as a
project exception with conditions.

1.10.0 previous baseline. 1.10.0 (2026-10-19): the rest of the EP06 review proposal (W50 per-shot action load paused by the user, not in the release) —
C10 card-vs-prompt cross-check (camera_plan_check.py --prompt), the closing render-lesson INFO in validate_prompt.py,
qa_check.py and templates/qa.md (QA current state, new to the zone), seven review passes (stage-7 §7.1 / §7.4), C10 in
stage-6 §6.6, the platform-difference note (capabilities §2, stage-5 §5.1 hand-off row); hashes re-set in the same
change with a CHANGELOG entry.

1.9.0 previous baseline. 1.9.0 (2026-10-19): render lessons from offset EP06 s01 clip01 / clip02 — C09 bearing check plus W-C3 / W-C4 / W-C5 in
camera_plan_check.py; wording_checks.py (W46-W49), continuity_checks.py (W51) and viewpoint_checks.py (W52) added to the
zone and wired into validate_prompt.py; stage-5 (§5.1 hand-off, §5.1c, §5.1g bearings / reach / existing reference
images only), stage-5b (scene-image viewpoint), stage-6 (bracket without speed, five wording rules, self-check),
stage-7 (review row, six diagnosis rows, §7.3 header), shot-card and prompt-templates carry the rules; hashes re-set in
the same change with a CHANGELOG entry. User decision: camera design starts from the reference images the user already
provided; nothing asks for a new or regenerated image.

Previous baseline: 1.8.0.

1.8.0 (2026-10-19): mandatory camera-position plan in S5 (§5.1g), shot-card template section, stage-7 review row;
camera_plan_check.py added to the zone; per-clip recheck after the previous clip's render (--stage s5 / s6, C08, W-C2);
hashes for stage-5, stage-7, the shot-card template and camera_plan_check.py re-set in the same commit.

1.8.0 previous baseline: 1.7.1.

1.7.1 (2026-10-13): W44 relaxed by the user's decision - the intent word in the dialogue bracket needs one executable
beat of any kind for the speaker (eye / face, hand / head / body, voice or pause, an action toward the other character,
or a delivery word in the bracket), chosen by the director; background / back-turned speakers follow the off-screen
rule; coverage INFO added (subtext_checks.py). Stage-4 / 5 / 6 / 7, emotion-performance, duration-rhythm, the two
templates and the W36 message (guide_checks.py) carry the wording; validate_prompt docstring updated. W45 unchanged.
Hashes re-set in the same change with a CHANGELOG entry.

1.7.0 (2026-10-13): three review codes from the offset EP05 s03 clip03 review — W43 focus / soft-layer placement per
on-screen character shot (focus_checks.py, new to the zone), W44 intent in the dialogue bracket without an eye beat and
actions written into the bracket (subtext_checks.py, new), W45 sustained wearing-state deviation while the character's
binding lines use the image-equals-state wording (costume_checks.py, new); shot tags may run to 80 characters
(validate_prompt / rhythm_checks / variation_checks / tone_checks), 过肩 added to the OTS regex, W36 / W38 messages
extended (guide_checks). The fourth planned item (借秒 / W42) was paused by the user and is not in the release. Stage-4 /
5 / 5b / 6 / 7, emotion-performance, camera-vocabulary, templates and the examples carry the rules; hashes re-set in
the same change with a CHANGELOG entry.

1.6.2 (2026-10-13): wording that read as "trim performance" removed from stage-4 §4.4 / §4.4c, stage-5 §5.6,
stage-6 §6.2 and the T1 template (brevity applies to camera prose and background activity only; several beats per
shot are written in full). Hashes re-set with a CHANGELOG entry.

1.6.1 (2026-10-13): W38 length budget raised to 3,000 CJK / 6,000 EN words (user: the agent was still trimming
performance); INFO line no longer quotes the official 500-character figure. Hashes for guide_checks.py, stage-6 and
prompt-templates re-set with a CHANGELOG entry.

1.6.0 (2026-10-13): official-guide (2026-10 edition, 70 pages) alignment — variation fields move to the E-layer 变化轨 row
(variation_checks.py reads it first; size_rank fixed for 中近), W36–W41 + INFO in the new guide_checks.py (added to the zone),
@名 asset binding in validate_prompt / production_contract / production_preflight (record assets may carry `name`),
S4 §4.4a / §4.4c performance development → translation, 【贯穿要求】 five buckets, capabilities §8 FAQ; hashes for the
touched files re-set in the same change with a CHANGELOG entry. Decided by the user on 2026-10-13 (version 1.6.0).

1.4.2 (2026-10-13): tone-cue rule (S4 §4.4b: freeze / slow turn / stare + whisper / stateless approach / head-down-
eyes-up read as suspense whatever the tone word says; lexicon 发现（轻松） row; genre-packs G2/G5 notes; stage-5 §5.1e/§5.9;
stage-7 §7.2) and W35 in the new tone_checks.py (added to the zone) wired into validate_prompt.py; hashes re-set in the
same change with a CHANGELOG entry. Trigger: offset EP05 s03-clip02 v1 ending rendered "like a thriller".

1.4.1 (2026-10-13): spatial-direction rule (landmark position and character movement both relative to the camera;
stage-5 §5.2/§5.5/§5.9, stage-6 §6.2/§6.6, stage-7 §7.2, prompt-templates T1) and E23 + 方向句 INFO in the new
direction_checks.py (added to the zone) wired into validate_prompt.py; hashes for those files re-set in the same
change with a CHANGELOG entry. Trigger: offset EP05 clip01 v2 rendered the character walking away from the camera.

1.4.0 (2026-09-20): variation track (S5 §5.1f, director-grammar §4.1), W30-W33 (variation_checks.py), 节奏档 as a
check set, English speech default 3.5 words/s, measure_clip visual variation profile; hashes for validate_prompt.py,
rhythm_checks.py (new to the zone), variation_checks.py (new), stage-5, stage-6, stage-7, capabilities, genre-packs,
prompt-templates and shot-card re-set in the same commit with a CHANGELOG entry.

1.3.0 (2026-09-19): continuous dialogue track (W29), track-sum duration derivation, speech-rate calibration;
validate_prompt.py, stage-5, stage-6 and prompt-templates hashes re-set in the same commit
(1.3.1: continuous track is the dialogue-scene default; two-track model in duration-rhythm §2-3).

1.2.0 (2026-09-19) is a deliberate directing-core release (duration/rhythm rules W22-W27, measure_clip,
pace directives in stage-6/templates, capability §4.3 measured note); hashes for validate_prompt.py, prompt_structure.py (W05 threshold reads 台词填充率),
stage-5, stage-6, stage-7, capabilities and prompt-templates were re-set in the same commit with a CHANGELOG entry.


1.1.0 (2026-09-17) is a deliberate directing-core release (official-doc alignment, director grammar, carriers,
dialogue budget, validator W04/W19); the baseline was re-set in the same commit with a CHANGELOG entry, as this
docstring requires. Files not touched by 1.1.0 keep their 1.0.0 hashes (emotion library, emotion-performance,
performance-record, production-workflow, record templates, prompt_structure, production_contract,
production_preflight, emotion_library, performance_checks).

1.0.0 baseline history: production back end of Film-Seedance-Director v2.3.1.

Baseline content: Film-Seedance-Director v2.3.1 production back end (the user chose 2.3.1 as the
production baseline). At the split, references to files now living in film-creative (and to the
retired concept mode) were rewritten as hand-off notes in stage-1-intake, stage-4, stage-5,
director-lenses, scene-parameters, causal-chain, anti-mechanical, genre-packs and the script-scene
template; every other protected file is byte-identical to v2.3.1 (verifiable in the source repo's
tags). A deliberate change to any of these belongs to a production/performance release with its own
review, and must update this baseline in the same commit with a CHANGELOG entry."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    'assets/emotion-library.json': 'ef22ac8bfec33567344e13a927d47f7b577c3c6f07b110cc5a2e316523599977',
    'references/emotion-performance.md': 'dafd8c46170a540dc50e3ac080818cadb1292bd256f4e6b0ce5277ea6d059940',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': '0316675133ce6796e736a1b0f9e36738aad720ae0f9ea912a6b18dcd63e16860',
    'references/stage-5-directing-storyboard.md': '2d91cf78ecccc73ce3ee5567fc6122e7d481a6a49517741bdf88624f21719151',
    'references/stage-5b-reference-assets.md': '1474f46720197c575ff10b56a355a1a56d83daf3eae389f8d5eb592f86939964',
    'references/stage-6-prompt-compiler.md': '24b8ea8651f84db04402c31169e6d5b80adf79762626f8fb635eba0ef2ba0928',
    'references/stage-7-qa-continuity.md': 'f962c32c84ec2c2b7dc58af63605806ad39c8a908faab4bd0b8f65eecbc70b83',
    'references/production-workflow.md': '4ee084b36dc9a2ef1ddb0e9c46e1dd45727383b24385c40e7b03e34cb1f8840a',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'c303fba78790dec9f06d4daf8355e6750f475cfc571c3357066cfa8d06e0bcad',
    'references/camera-vocabulary.md': '27975701c3e1c6e34995418b96a6b66a90e78b4538994dc98c39db108d830b67',
    'references/externalization-lexicon.md': '3982b9cdd021d6647897266021259aff7cf1d84e80829527c5d630c3e6c8d8a3',
    'references/genre-packs.md': '27a3ad4ad2428479c21164aa7097b1b92341958aaa0e44fbfa5d8d442f3569df',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '7eaa17089b501e36ee500847e62d0befd2ebfd6d81ee0316861b2c3c626eb8b6',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '96e7fcb783028d6c258005c962c18b9f2cdbd3bc36d52596bc7a5568900b838b',
    'templates/shot-card.md': '9183f0c92f05ec50d5404913c900b393ea85e113c1dee627d0d4d492afe2a33a',
    'templates/reference-asset-brief.md': '106e08747fd39ce900ca928afef2244ce8071c0ea43fec328581352ce552b441',
    'templates/asset-registry.md': '2b478992e56c0d08bd99e66b04aa3933f9bd6dc46b0ca2eb507ae68632df0bba',
    'scripts/rhythm_checks.py': '54945abfb4e3849cbe82a8e481bd5420a12d52dfbdadaee4f542051b4f0eb1db',
    'scripts/variation_checks.py': '11a116c63f7e32a988da9eedb465d89ad8a3d73b92d7ceeb804c3e487a74c19f',
    'scripts/direction_checks.py': '54a7597032ffacbd05a689cd7e3ad0e5c8fb3ba2379f251d2b213839fb4fd992',
    'scripts/tone_checks.py': '1d836d6366587ebb763693eebc61b7aaa9a51158cd29d6d3f6bdde44f0063c1c',
    'scripts/guide_checks.py': 'cb2bc889727724e227025d2c6e7ba7b10e20ed80847b41d293171de78eaff7ef',
    'scripts/focus_checks.py': '5b5d3110f22c58c272f3c24aa7533e75b9b91f46f951589a829c0eef25a6106c',
    'scripts/subtext_checks.py': '84ba710d324ed2102701ae0ee2866a205f2c9160527af52b4b6f1cc647408f10',
    'scripts/costume_checks.py': '9f65d3b4fcdac75a5d61a07ccfbe6e63a0cd7a5c11ffd262ac9428d23f44ca59',
    'scripts/validate_prompt.py': '511f5db52dfbb8c9d6d376fa687584a4b882e263b13c4caabb2cb3520a4174ad',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': 'adb40d1e05ecb6d298e2bb295a8ef325941812f00a89f9000fe03477a58b780f',
    'scripts/production_preflight.py': 'aab550991f000dac727f744f1c603a5a1519f1adf44d2e288e11c9d3cc859c0d',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'scripts/camera_plan_check.py': '45138f69a861210ea967c7d0fe36b4c20dded64a2c76fa2666ef3715a695d1d9',
    'scripts/wording_checks.py': 'a12700904926ac4329b375c14873f25cb869dd8f337c61a9a50f97427c9702dd',
    'scripts/continuity_checks.py': '208cf0e08a652f086f5960999c1475c1785facfdadd2db44a25eba234e08ad74',
    'scripts/viewpoint_checks.py': '4216537edadbb2fcfdbe7c05aa5d621ff6cb88b39f6b5b453638e5d62e92903a',
    'scripts/layer_checks.py': '590dca196be1a40a7e5156539a72e6da7947bd5ebbef09adbde815c0bddfc8c8',
    'scripts/speaker_checks.py': '9c46c728b84531249499ce3cadc87280cb064cf3a9ef66f3ac961b40484bfb5a',
    'scripts/stage_check.py': '598a8a40154b41e7a2cc1ad51697d0b4f3545e236e4210d6351863a1096438e9',
    'scripts/check.py': '92748f197e14861dcb3354ade1fc7528e7d0929e4306f3c41821f494d349335b',
    'scripts/evidence.py': 'c28d4eaf39dcfff1f0e72f26f20eba8ed1410af4128766c82b1373474d4f8071',
    'scripts/qa_check.py': 'c44df6dfe0993f2e6917bd9f3eff4446d3fcaead27780e8282f3e38cbaaab62f',
    'templates/qa.md': '6f2e31f563155b4ef8c1d653e37e9c5b2bb8050f8ac3ecfd8cdae8dcf8e785b6',
    'references/shot-requirements.md': '727bb12c8108ee8e4fcb281c769f08773e118d73861fcee7f0f10fef4479b2a6',
    'scripts/performance_checks.py': '5a54ee7c0cb77b67466ee6f7102ded648220cf8b922fea7da186f68ccd869ae0',
}


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


class ProtectedZoneTests(unittest.TestCase):
    def test_production_and_performance_core_unchanged_since_1_1_0(self):
        for name, expected in PROTECTED.items():
            with self.subTest(file=name):
                self.assertEqual(sha(name), expected)


class SkillLinkTests(unittest.TestCase):
    def test_skill_links_resolve(self):
        import re
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        for ref in set(re.findall(r'`((?:references|templates|scripts|examples)/[^`]+)`', text)):
            self.assertTrue((ROOT / ref).exists(), ref)


if __name__ == '__main__':
    unittest.main()
