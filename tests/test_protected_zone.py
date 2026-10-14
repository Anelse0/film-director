"""film-director protected zone: production/performance core hash-locked at the 1.7.0 baseline.

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
    'references/emotion-performance.md': '9b7a06b48c4885b07ea02d79da4f28fd1ec5f80f01f9b1a6f4e5f0be92cc7878',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': 'f32a6a6e907363ac20e26125277c096c823e460340c75fa352d8e88513e7e495',
    'references/stage-5-directing-storyboard.md': 'cabfa4689a438f74ec8ba9ef872c5d73d506707a48528f4114a18894bc9c26c1',
    'references/stage-5b-reference-assets.md': '38c893fcdfe03dbf2238cecdd7d5cc8559f4b2593a87e9b2cd87be493d3bc81e',
    'references/stage-6-prompt-compiler.md': '69b4c4372e40117ef45169422f4ba2ca1128e8f1ace8a4b3036e3a3f4f4efed6',
    'references/stage-7-qa-continuity.md': 'eb901b272544797804e8a202083ba1a133e0c177fa971d42466f9a67848a64e6',
    'references/production-workflow.md': '4ee084b36dc9a2ef1ddb0e9c46e1dd45727383b24385c40e7b03e34cb1f8840a',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'b1cf9cec6593a12c0a51ccb3f6d4818a2c90eda35de9e7a90a857e27563f92eb',
    'references/camera-vocabulary.md': '2910da6bcebe1d4603e712a30db195504edfbf0ddfc22aa823adbf996be4582c',
    'references/externalization-lexicon.md': 'd89d0cc4ea98e63c9673984c84abd4081729ddaff2057616af582f141891f9da',
    'references/genre-packs.md': 'e8bf4dd45abb22776ac4dec2490551e1a9aedddfd26cca459bc6557df3c95513',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '2433dc53d6c3e66adcfc82aaa879391b1451ca932627d5dd5b3934e29a7a9a38',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '96e7fcb783028d6c258005c962c18b9f2cdbd3bc36d52596bc7a5568900b838b',
    'templates/shot-card.md': '91655dd74fa05903db459ddddbf1c835af1f94ccffff365ea5f3a84ddeef8664',
    'templates/reference-asset-brief.md': '106e08747fd39ce900ca928afef2244ce8071c0ea43fec328581352ce552b441',
    'templates/asset-registry.md': '2b478992e56c0d08bd99e66b04aa3933f9bd6dc46b0ca2eb507ae68632df0bba',
    'scripts/rhythm_checks.py': '24f4836a1d98b46acfeb1cf95c2f50a5f89f633b2412dd4ffc5d9a10628e61be',
    'scripts/variation_checks.py': '11a116c63f7e32a988da9eedb465d89ad8a3d73b92d7ceeb804c3e487a74c19f',
    'scripts/direction_checks.py': 'fdbd694059a9ca156946345ef4ac29ae95ad10fa22aea5fe52be20969fbf55ea',
    'scripts/tone_checks.py': '565322afadb5a468b6ed86049058e56d49a883f9b437e92f0b1e771eda262482',
    'scripts/guide_checks.py': '7e6532c1235348714e9bf953067c45ac83bf9116d459e6e752c5107b2c533845',
    'scripts/focus_checks.py': '5b5d3110f22c58c272f3c24aa7533e75b9b91f46f951589a829c0eef25a6106c',
    'scripts/subtext_checks.py': '0b0c355961c2de5878a306aba1fc5c124e5be334a7182d0477d30a60782ecdca',
    'scripts/costume_checks.py': 'dd11f7a23d3a252378d6f415a7310e16d0bf0811b3f5df29629b6957c74955fc',
    'scripts/validate_prompt.py': '45e6bfaa222cf52576125790e424307b98f105350b777572073ae0932577722b',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': 'adb40d1e05ecb6d298e2bb295a8ef325941812f00a89f9000fe03477a58b780f',
    'scripts/production_preflight.py': 'aab550991f000dac727f744f1c603a5a1519f1adf44d2e288e11c9d3cc859c0d',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
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
