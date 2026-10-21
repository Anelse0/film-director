"""film-director protected zone: production/performance core hash-locked at the 1.13.0 baseline.

1.13.0 (2026-10-20): execution mechanism only (1.12.1 cost-review proposal M1 / M2) — scripts/check.py (new to the zone):
one entry point whose three sub-commands (s5 / s6 / qa [--sync]) import the four checkers' check() / validate() and merge
their output (ERROR → render-lesson WARN → other WARN → the QA number block → INFO → input sha256); `qa --sync` writes the
machine lines of the QA 现行状态 back and re-runs qa_check. templates/qa.md title carries one added clause. No new codes
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
    'references/emotion-performance.md': 'b928678bee8bfc1a6d68953b83f5bc9a86dff022e0a41667b38f8f5e4e8a084e',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': '12eb294f022c8d39350bbb6f5af44af06d972e037cd7483f5f07f3b486155ad7',
    'references/stage-5-directing-storyboard.md': '7b47bc606585c5e7eb61d5d737e202305c0e414b0326c4e195c7ffbf03646cf5',
    'references/stage-5b-reference-assets.md': 'a002a1b033dee2f4e0471c118b7d592e2cb8db4171ff4a95b3c3d6d06306aa09',
    'references/stage-6-prompt-compiler.md': 'a74fe556a9b4c2dd0fb2854d46ba1ddbfaab5f2d9cd58544c92d7ed1863a8773',
    'references/stage-7-qa-continuity.md': '4751e2bdb612257af9805e82f005e83b129f8966d943d072e5e79d5bcc8da3bd',
    'references/production-workflow.md': '4ee084b36dc9a2ef1ddb0e9c46e1dd45727383b24385c40e7b03e34cb1f8840a',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'be04dcd09e62d3df98a4f8d5ed95d4f79a58272838a35d777c8e509bcc79fad6',
    'references/camera-vocabulary.md': '27975701c3e1c6e34995418b96a6b66a90e78b4538994dc98c39db108d830b67',
    'references/externalization-lexicon.md': '047776e5594b68f31ba53ac43893a834d8b3caca25b03bf03e6b8558d1df4965',
    'references/genre-packs.md': 'e8bf4dd45abb22776ac4dec2490551e1a9aedddfd26cca459bc6557df3c95513',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '4582e1eeb68d6b11940ddc699052bafcccc36bb5222aabd080ca8736f187f548',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '96e7fcb783028d6c258005c962c18b9f2cdbd3bc36d52596bc7a5568900b838b',
    'templates/shot-card.md': '40bc9c292c94fdf1f20a7e1ce64765b264cb88cee44d68318bfbd09a5c8f342c',
    'templates/reference-asset-brief.md': '106e08747fd39ce900ca928afef2244ce8071c0ea43fec328581352ce552b441',
    'templates/asset-registry.md': '2b478992e56c0d08bd99e66b04aa3933f9bd6dc46b0ca2eb507ae68632df0bba',
    'scripts/rhythm_checks.py': '5157f9c0a72c119b99f8d09d54756aeb9699f3af947a9df7b84a3a0c10de983f',
    'scripts/variation_checks.py': '11a116c63f7e32a988da9eedb465d89ad8a3d73b92d7ceeb804c3e487a74c19f',
    'scripts/direction_checks.py': 'fdbd694059a9ca156946345ef4ac29ae95ad10fa22aea5fe52be20969fbf55ea',
    'scripts/tone_checks.py': '565322afadb5a468b6ed86049058e56d49a883f9b437e92f0b1e771eda262482',
    'scripts/guide_checks.py': '3c08ca954d0f787bab215a1b5d0181c74b0de4cf6f23fac57ad517ad70da906b',
    'scripts/focus_checks.py': '5b5d3110f22c58c272f3c24aa7533e75b9b91f46f951589a829c0eef25a6106c',
    'scripts/subtext_checks.py': '84ba710d324ed2102701ae0ee2866a205f2c9160527af52b4b6f1cc647408f10',
    'scripts/costume_checks.py': 'dd11f7a23d3a252378d6f415a7310e16d0bf0811b3f5df29629b6957c74955fc',
    'scripts/validate_prompt.py': '8ab9299b7a3ce0cf73cb0783714a91c4d63ac037e1c7f312878565c42c5efb7c',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': 'adb40d1e05ecb6d298e2bb295a8ef325941812f00a89f9000fe03477a58b780f',
    'scripts/production_preflight.py': 'aab550991f000dac727f744f1c603a5a1519f1adf44d2e288e11c9d3cc859c0d',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'scripts/camera_plan_check.py': '97e1e20dda466748e7d0f9aa5c46859674fd635234506f54f05a9cc9453c9655',
    'scripts/wording_checks.py': 'ae8411eb2e8687d73c5e00d15935deeccc26b1af5360f8d92cd68429e80dac08',
    'scripts/continuity_checks.py': 'b93b1349b682829892f7e7df7b8459aa0ae953266da017683cd80c1ccebc2c96',
    'scripts/viewpoint_checks.py': 'ef4fec0091e3b99587dfe399e7e4b91e20ca0467030ea6f593cf5eb75b18bda2',
    'scripts/layer_checks.py': '0f6ef4f6b5c267bed9d069b27da5308138be99789468dac1851774e3bf1f74ef',
    'scripts/speaker_checks.py': '583c01941542037e7b97b793a4f90aa58c5aca6979c881f05f899d5ebdc9fa9a',
    'scripts/stage_check.py': '2f837d8d6823aecb76f945b1805b525d378a35a7428d4d265398fa217f61c0b8',
    'scripts/check.py': 'aefa743a3fbb0db058ea6c2d5c96cb667f814b662431a260858faa048ce708c3',
    'scripts/qa_check.py': '5815f9e068b958c3bf7297b110488dcdc1a1f0950f56b5761d671548b03a34da',
    'templates/qa.md': '477c64f7b43a2a0469272741a2099e8fa6acaf09ae7c521600e2acf5d9448346',
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
