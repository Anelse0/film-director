"""film-director protected zone: production/performance core hash-locked at the 1.10.0 baseline.

1.10.0 (2026-10-19): the rest of the EP06 review proposal (W50 per-shot action load paused by the user, not in the release) —
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
    'references/emotion-performance.md': 'f2c7aa0b1beb72781117abd310cab2431c703af909e5aa2918946a2f40ae5a5a',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': '8fbfdb57213b17e6d1ce6b2ef0fc55e49d81b517d57a880143bfe1486cbc56c5',
    'references/stage-5-directing-storyboard.md': '7356bbbd5ba12262d11a4794c3cb5f4050974c6398500ebaad6aac7945cfb46f',
    'references/stage-5b-reference-assets.md': '0ca1e45deee8a4dd5aa97022eed99c47284ca83018d5805aebfe254e9a1af18c',
    'references/stage-6-prompt-compiler.md': '5c992be1631a2b7ed8e4c13c4ecd1663b9dbfea2eb595810df81ba9720720f18',
    'references/stage-7-qa-continuity.md': 'c7faae3c63a9363f8fbc035df0654344e789c93ba02b4b0a5d2f63aa507b5b2f',
    'references/production-workflow.md': '4ee084b36dc9a2ef1ddb0e9c46e1dd45727383b24385c40e7b03e34cb1f8840a',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'fc3d1a1b4edf12b08cc333a655067433b8dd2bb12c85d1834cbf1c9a565c113d',
    'references/camera-vocabulary.md': '2910da6bcebe1d4603e712a30db195504edfbf0ddfc22aa823adbf996be4582c',
    'references/externalization-lexicon.md': 'd89d0cc4ea98e63c9673984c84abd4081729ddaff2057616af582f141891f9da',
    'references/genre-packs.md': 'e8bf4dd45abb22776ac4dec2490551e1a9aedddfd26cca459bc6557df3c95513',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': 'eb5732cb7d1e660522ad9d1e5543859b46124a4c62c9afcd8ed1d7c0b1e8b36b',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '96e7fcb783028d6c258005c962c18b9f2cdbd3bc36d52596bc7a5568900b838b',
    'templates/shot-card.md': 'd6b81744c21e5316aa712693481f8697d87ae40d9d1e28c8a57edaf1424a2631',
    'templates/reference-asset-brief.md': '106e08747fd39ce900ca928afef2244ce8071c0ea43fec328581352ce552b441',
    'templates/asset-registry.md': '2b478992e56c0d08bd99e66b04aa3933f9bd6dc46b0ca2eb507ae68632df0bba',
    'scripts/rhythm_checks.py': '24f4836a1d98b46acfeb1cf95c2f50a5f89f633b2412dd4ffc5d9a10628e61be',
    'scripts/variation_checks.py': '11a116c63f7e32a988da9eedb465d89ad8a3d73b92d7ceeb804c3e487a74c19f',
    'scripts/direction_checks.py': 'fdbd694059a9ca156946345ef4ac29ae95ad10fa22aea5fe52be20969fbf55ea',
    'scripts/tone_checks.py': '565322afadb5a468b6ed86049058e56d49a883f9b437e92f0b1e771eda262482',
    'scripts/guide_checks.py': 'f593bbd8e2b21dfc69dbbcaacb8d73c1a885b0cc24d9cc6e3e49da2f84d9825d',
    'scripts/focus_checks.py': '5b5d3110f22c58c272f3c24aa7533e75b9b91f46f951589a829c0eef25a6106c',
    'scripts/subtext_checks.py': 'c060f2bc9c7faf731e4ef8da3230319cdbf5c9916107de6ac1f37f019323a7ed',
    'scripts/costume_checks.py': 'dd11f7a23d3a252378d6f415a7310e16d0bf0811b3f5df29629b6957c74955fc',
    'scripts/validate_prompt.py': 'e515dfd023eb214fb083504fafbf6e2d752b46c8693b6362a232a56147c6d55b',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': 'adb40d1e05ecb6d298e2bb295a8ef325941812f00a89f9000fe03477a58b780f',
    'scripts/production_preflight.py': 'aab550991f000dac727f744f1c603a5a1519f1adf44d2e288e11c9d3cc859c0d',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'scripts/camera_plan_check.py': '97e1e20dda466748e7d0f9aa5c46859674fd635234506f54f05a9cc9453c9655',
    'scripts/wording_checks.py': 'b4e01868ffe7778b7ce45d90abe36b90fb1a25889a4f9c667ee3afe280a69417',
    'scripts/continuity_checks.py': 'b93b1349b682829892f7e7df7b8459aa0ae953266da017683cd80c1ccebc2c96',
    'scripts/viewpoint_checks.py': 'ef4fec0091e3b99587dfe399e7e4b91e20ca0467030ea6f593cf5eb75b18bda2',
    'scripts/qa_check.py': '25b2b1e2577aa76b80b5bcab5ff4d90fd0b79308b612c1f001c459e61bc8e8ff',
    'templates/qa.md': '2dbc43d0153d65fc94349c96d4067494c826ba4fd866db3051bb885393b1e102',
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
