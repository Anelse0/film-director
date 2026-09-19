"""film-director protected zone: production/performance core hash-locked at the 1.3.0 baseline.

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
    'references/stage-4-performance.md': 'df8bc48db59bc120f728d8ad1901048332c890819324512d721fc0b4886795de',
    'references/stage-5-directing-storyboard.md': 'd9342edfd09d351c09ff656bd03cd4205658944153e14bb580bc1c9dcada2071',
    'references/stage-5b-reference-assets.md': 'ee87fc676e3128def78a2aaa220688fe68b472768e669934ff52e5b4c01e7a77',
    'references/stage-6-prompt-compiler.md': '7e566f7c0e38afe6259cea2ae41cd1dbb0a901502781942c7530fa1b9df3184a',
    'references/stage-7-qa-continuity.md': '45af4617f62108b03b15d8c373a973a4511d53e0ae7ddea6ce63cfd54965b98d',
    'references/production-workflow.md': 'db8cc8de428952283a2cda4d7d23e0b1b0f4784ab18c54b57f674ca93eac6cfd',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': '1ea545f25935b5a256f14061a0e8ba8ca5dd95535074547bf4d335a9353399fd',
    'references/camera-vocabulary.md': '06a5c14733a3c2cffb5c8dcaa02d107e6ab9f57982dfae0708b06b1583a3b93e',
    'references/externalization-lexicon.md': '292b8363a566a18aae1eae2b3e2c085760930d2dfb608b2dc3040288cb03bbbb',
    'references/genre-packs.md': '9b12fbcc6ce13d60d086021b981274f1a24e89f9091d34e3b734f31b8dd4e231',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '335f6ec400294447c77d623a74b16c72d9cf6744bcb62d3207ebd2189a79707d',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': '53c840ba177e68edc9f80d5d994a0e0520fbeba9b1c0bf46954167d76d3394e8',
    'templates/reference-asset-brief.md': 'adc6b7c7c52c169d31ee7ba83111293496e7133572a7bedc08bf4a08d251df0b',
    'templates/asset-registry.md': '996818cda8aa55796820ae96c808c56459198f8f465b4e4924196d7ed8cc2943',
    'scripts/validate_prompt.py': '8ee40e55ac9b2399a81804782f744fefa6f3771f5f34202de233fc334ac7706f',
    'scripts/prompt_structure.py': 'efbd86c1eb8fb7a7a451e291e2b0e58d2e7220e97a8fae3d0c1bd37a2307fc7d',
    'scripts/production_contract.py': '963653540c39519d99a731749736e96b39bed17005305af1082c857af5426bfa',
    'scripts/production_preflight.py': '80379ec01b3f952ee82cc1611e38b555ad41838bd0bb6f0ac52ddb5453605702',
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
