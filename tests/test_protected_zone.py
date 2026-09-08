"""film-director 1.0.0 protected zone: production/performance core hash-locked at the 1.0.0 baseline.

Baseline content: Film-Seedance-Director v2.3.1 production back end (the user chose 2.3.1 as the
production baseline). At the split, references to files now living in film-creative (and to the
retired concept mode) were rewritten as hand-off notes in stage-1-intake, stage-4, stage-5,
director-lenses, scene-parameters, causal-chain, anti-mechanical, genre-packs and the script-scene
template; every other protected file is byte-identical to v2.3.1 (verifiable in the source repo's
tags). A deliberate change to any of these belongs to a production/performance release with its own
review, and must update this baseline in the same commit with a CHANGELOG entry.

1.1.0 deliberately rebaselines four files for the mandatory emotion layer (W20): the overall
emotion arc, per-shot emotion tags and per-line delivery notes — validate_prompt.py (W20 check),
stage-6-prompt-compiler.md (§6.0/6.1/6.2/6.6), prompt-templates.md and shot-card.md (new slots).
See CHANGELOG 1.1.0.

1.1.1 rebaselines stage-6-prompt-compiler.md and prompt-templates.md again: the mandatory
emotion layer is labelled `[推论]` (a local skill convention, not official Seedance structure;
W20 stays a WARN-level review hint). See CHANGELOG 1.1.1."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    'assets/emotion-library.json': 'ef22ac8bfec33567344e13a927d47f7b577c3c6f07b110cc5a2e316523599977',
    'references/emotion-performance.md': 'a150f6047b6a484a6ab858a93773d9c28fab022ac274bcc358dd20684468d8d0',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': 'ade55ddb33655042f6360bdde1bd5a0d4e149a479b1b407f142d510b696338a0',
    'references/stage-5-directing-storyboard.md': '49980af3b95bdd4e2eca0288a915293c7dada4ddfb4c45ef54fc7daf23aec16d',
    'references/stage-5b-reference-assets.md': '167fee36b688f32f5a8796be58098e043eb3ae0d27af3624ce7ed75ff7adc2d0',
    'references/stage-6-prompt-compiler.md': '012c548ef99538c283ec05fd2d8c58782058f4f2723cbf4346bc9315572de707',
    'references/stage-7-qa-continuity.md': '7957aca66d6cda61e4c2de9a69464b61f96abdd0e1a595fe36ff82d37e9e2f68',
    'references/production-workflow.md': 'db8cc8de428952283a2cda4d7d23e0b1b0f4784ab18c54b57f674ca93eac6cfd',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'cee3b580a447f686b4fc62723438c39dbd8f8233f01c8550e3b1086878bf7a7b',
    'references/camera-vocabulary.md': 'de1cd86da8fbf17c778038a565d57a425218636c8a148abfec476aead1007bd8',
    'references/externalization-lexicon.md': '7a79bf1bf42805f185441a7767c95dd900dc390503674b286807df68eb709ce6',
    'references/genre-packs.md': '8e7334eaa40d40f07278bf0493bfe9315c515f203cf9876acfca7e6fccd4dd40',
    'references/director-lenses.md': '5d76b7b5f1f2908ea732eab1bb69dee8f9c81297bc5203e1a788d274d5b8c36a',
    'templates/prompt-templates.md': 'c1f83c00453494b185b2bd1c1a7baf247157e6348288021275332ce74eee9006',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': '2c59e1022197bc88fa3539cbe7dcc2c61ee4bd60c1586c380995ef9623005f30',
    'templates/reference-asset-brief.md': 'adc6b7c7c52c169d31ee7ba83111293496e7133572a7bedc08bf4a08d251df0b',
    'templates/asset-registry.md': '996818cda8aa55796820ae96c808c56459198f8f465b4e4924196d7ed8cc2943',
    'scripts/validate_prompt.py': '068c21beb9955cc125b3465b1b6a56ed6f711ea109c2fb95152d8e0eff37842f',
    'scripts/prompt_structure.py': 'd9f73020e41eec19edee56b7ad8a45f9b973c28db9c93e451274ab6d1a0b60bf',
    'scripts/production_contract.py': '963653540c39519d99a731749736e96b39bed17005305af1082c857af5426bfa',
    'scripts/production_preflight.py': '80379ec01b3f952ee82cc1611e38b555ad41838bd0bb6f0ac52ddb5453605702',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'scripts/performance_checks.py': '5a54ee7c0cb77b67466ee6f7102ded648220cf8b922fea7da186f68ccd869ae0',
}


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


class ProtectedZoneTests(unittest.TestCase):
    def test_production_and_performance_core_unchanged_since_1_0_0(self):
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
