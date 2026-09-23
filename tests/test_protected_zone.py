"""film-director protected zone: production/performance core hash-locked at the 1.4.0 baseline.

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
    'references/stage-5-directing-storyboard.md': '301cd44278eb2c4a26ea48eb85de3f595cfe1a089a06987aa7ec225148a18157',
    'references/stage-5b-reference-assets.md': 'ee87fc676e3128def78a2aaa220688fe68b472768e669934ff52e5b4c01e7a77',
    'references/stage-6-prompt-compiler.md': 'da51a360c5111c85211526cced1aca6e245d20601e1cc5126e7631eae29b8fc8',
    'references/stage-7-qa-continuity.md': '442b7553d6945fcb5069714d38e12d14c579575c694cd2538a1554c1fa22c562',
    'references/production-workflow.md': 'db8cc8de428952283a2cda4d7d23e0b1b0f4784ab18c54b57f674ca93eac6cfd',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'a95da7455c8cc3b5c9706380e4e8082cf29c4e73a7f753b24324b138f8080e26',
    'references/camera-vocabulary.md': '06a5c14733a3c2cffb5c8dcaa02d107e6ab9f57982dfae0708b06b1583a3b93e',
    'references/externalization-lexicon.md': '292b8363a566a18aae1eae2b3e2c085760930d2dfb608b2dc3040288cb03bbbb',
    'references/genre-packs.md': '998602b50c9773ebac196991dd52bee21352695e4e64507215c90df5b60f5d0d',
    'references/director-lenses.md': '8964042aed92fb30c6daaba7ed66e891274cb96bbdbaa3a0514037c29f4aa894',
    'templates/prompt-templates.md': '502af938d3bb774e054467f27d5057840fea248a375fe4f79c620a1dc474773e',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': '76c6e2a7fc622140a90a2de5ede90ec143324322295dae6711fdd9bbe3ac2d1b',
    'templates/reference-asset-brief.md': 'adc6b7c7c52c169d31ee7ba83111293496e7133572a7bedc08bf4a08d251df0b',
    'templates/asset-registry.md': '996818cda8aa55796820ae96c808c56459198f8f465b4e4924196d7ed8cc2943',
    'scripts/rhythm_checks.py': 'b1293f1d3f91eaad415e8a984abaf9fcc4344b4736351c6dba7fbf4fba3575f3',
    'scripts/variation_checks.py': 'c1a95f98ff786b8479ed7aa169e27a306d4d31d1c6feb28e6b2e9b031e350ef0',
    'scripts/validate_prompt.py': '952fe9726e97469bf8755ec41e2a68f2f29ca8c4137f9bf8b2d5bbeb9a60d8a2',
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
