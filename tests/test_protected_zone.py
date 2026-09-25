"""film-director protected zone: production/performance core hash-locked at the 1.4.0 baseline.

1.11.0 (2026-09-25): wardrobe default -- appearance and outfit images apart unless the user says so (W37 in
wardrobe_checks.py, E-layer 衣着来源 row read through validate_prompt.py); stage-5b §5b.1/§5b.3a, stage-6 §6.2/§6.5,
stage-7 §7.1, prompt-templates, shot-card, reference-asset-brief and asset-registry. In-line additions except the
three-source table labels; hashes re-set in the same commit with a CHANGELOG entry.

1.10.0 (2026-09-24): wardrobe per character, per shot (hard rule 21) -- scripts/wardrobe_checks.py (E23 / W36) joins
the zone and is wired into validate_prompt.py; stage-5 §5.0/§5.5/§5.6/§5.9/§5.10, stage-5b §5b.1/§5b.2/§5b.3a/§5b.5,
stage-6 §6.1/§6.2/§6.3/§6.6, stage-7 §7.1/§7.2/§7.3, production-workflow step 1, capabilities §4.2, prompt-templates
(T1-T8, English skeleton), shot-card, reference-asset-brief and asset-registry. In-line additions except the lines
that made an appearance image carry its clothes by default (T2 binding, stage-6 binding format, English REFERENCES,
asset-registry img1); hashes re-set in the same commit with a CHANGELOG entry.

1.9.0 (2026-09-23): camera presence / support / movement character (director-grammar §2.5) wired into stage-5
§5.1b/§5.4, shot-card, stage-6 §6.2, stage-7 §7.1/§7.2; camera-vocabulary dolly-zoom direction corrected
(dolly back + zoom in -> background grows, per Wikipedia's diagram caption); camera_library.py --slots prints
layer / support. In-line additions only; hashes re-set in the same commit with a CHANGELOG entry.

1.8.0 (2026-09-23): camera library -- assets/camera-library.json (byte-identical copy of the user's AI运镜提示词库,
SHA 0f3136a5...), scripts/camera_library.py and scripts/camera_checks.py (W34-W35) join the zone; validate_prompt.py,
stage-5 §5.1b/§5.4, stage-6 §6.2/§6.5/§6.6, stage-7 §7.1, prompt-templates, shot-card and camera-vocabulary hashes
re-set in the same commit with a CHANGELOG entry. references/camera-index.json (reading index) stays outside the
zone so its notes can be corrected.

1.7.0 (2026-09-23): English speech default 3.5 -> 4 words/s (user decision; 短促 4.5 [推论]) in
validate_prompt.py, capabilities §7.2-7.3, stage-4 §4.5, stage-6 and prompt-templates; hashes re-set in the
same commit with a CHANGELOG entry.

1.6.1 (2026-09-23): stage-4 §4.5 English speech default 2.5 -> 3.5 words/s, left stale by 1.4.0 (hard rule 17,
capabilities §7 and validate_prompt.py already used 3.5); stage-4 hash re-set in the same commit.

1.6.0 (2026-09-23): every clip delivers at least one change (hard rule 20) -- stage-5 §5.1 rule 6, §5.1f peak
event chosen from the delivered rows, §5.9 row; stage-7 §7.1 review row and §7.2 diagnosis row. Additions only:
no existing clause removed (variation track, W24/W30-W33 unchanged). stage-5 and stage-7 hashes re-set in the
same commit with a CHANGELOG entry.

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
    'references/emotion-performance.md': 'a150f6047b6a484a6ab858a93773d9c28fab022ac274bcc358dd20684468d8d0',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': 'b04d317cc1dd2ad609244acd6210c0d953e4c8df7484b13bc815bb76bb9c78b0',
    'references/stage-5-directing-storyboard.md': '86fce52587d9ceb3ebc58c64c7ee1694a7133ec4693258ef7e008abdb0ccde4b',
    'references/stage-5b-reference-assets.md': 'aa0bf1aead92c3e0e413e5ecfc9c0c6ad28feec33c7a6aba39ac564a174fcac6',
    'references/stage-6-prompt-compiler.md': '99d21be692487ee932c35f47f0f7a479fd78853b3b4007c04e9815dfb53dbde4',
    'references/stage-7-qa-continuity.md': '67d4b08f0c89087c554b88428c504c98ecfaa5f4f6fd92c8b1156562bf7e9cc9',
    'references/production-workflow.md': 'c7d74cf72b2c114aa94af102cd3dc962927bda75e268c3a1c964aba8b07df589',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': '17044a111383df9b067991115e7af249f4863ffa242a005e6ac0d47bdac26e52',
    'references/camera-vocabulary.md': 'e29356b0956d67e50658a49e13eb57bf7fa58a9e7f574ba19fd777e8df402f4c',
    'references/externalization-lexicon.md': '292b8363a566a18aae1eae2b3e2c085760930d2dfb608b2dc3040288cb03bbbb',
    'references/genre-packs.md': '998602b50c9773ebac196991dd52bee21352695e4e64507215c90df5b60f5d0d',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '252b7b42800a7b84d28e85615069b4df4562bc2a83a3a8e897e969feaa2bc635',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': 'ecc70d84cf92b2eb8b13bc9750822002f4b3a1aaf7e626e13a9b38cfd18e3b18',
    'templates/reference-asset-brief.md': '4a6857d28f67688921b4ed5c1c2746be1e65c7e3389d7629c9b20c39fe216882',
    'templates/asset-registry.md': '5455fd01c138723256c1f09eaf108d9372f2f8d8e6af01e6f08d7a93c1eb2dc9',
    'scripts/rhythm_checks.py': 'b1293f1d3f91eaad415e8a984abaf9fcc4344b4736351c6dba7fbf4fba3575f3',
    'scripts/variation_checks.py': 'c1a95f98ff786b8479ed7aa169e27a306d4d31d1c6feb28e6b2e9b031e350ef0',
    'scripts/validate_prompt.py': '5561e5d0804ca5c0952e95ff1de3594e9c13cfef85a703dd376a5d84f4a898df',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': '963653540c39519d99a731749736e96b39bed17005305af1082c857af5426bfa',
    'scripts/production_preflight.py': '80379ec01b3f952ee82cc1611e38b555ad41838bd0bb6f0ac52ddb5453605702',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'assets/camera-library.json': '0f3136a56e593db3f721db97358681d641e6c941a0840df4fa5ea2ac9f0e88ec',
    'scripts/camera_library.py': '21667cbb3a16819478febb318faf9e19554b6b97a29ce1a1f979af7f65a231e7',
    'scripts/camera_checks.py': 'ebea54738b44af35096316a3687c174a2245e8fadaad06521172da0683d724f3',
    'scripts/wardrobe_checks.py': '2517c427bda9fc8176ac43098b3725affeda6359259884a124a1ce2ea09ef655',
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
