"""film-director 1.0.0 protected zone: production/performance core hash-locked at the 1.0.0 split baseline.

Baseline: Film-Seedance-Director 2.6.0-alpha.3 (commit 0436abd), itself unchanged since v2.5.0 except
templates/asset-registry.md (2.6.0 P1 registry metadata, user-authorized). At the split, three files
(stage-4-performance, stage-7-qa-continuity, director-lenses) had their references to files now living in
film-creative rewritten as hand-off notes (1-3 lines each); every other protected file is byte-identical
to the source repo. A deliberate change to any of these belongs to a production/performance release with
its own review, and must update this baseline in the same commit with a CHANGELOG entry."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    'assets/emotion-library.json': 'ef22ac8bfec33567344e13a927d47f7b577c3c6f07b110cc5a2e316523599977',
    'references/emotion-performance.md': 'a150f6047b6a484a6ab858a93773d9c28fab022ac274bcc358dd20684468d8d0',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': '9ccd98a9945e759a5c7a11a2de26ccec5cd2794d17714d14e1dce6eb39773a2f',
    'references/stage-5b-reference-assets.md': '167fee36b688f32f5a8796be58098e043eb3ae0d27af3624ce7ed75ff7adc2d0',
    'references/stage-6-prompt-compiler.md': '18f28369d44ef06adbc756d64000b4eebe051386925cb14894ff786b2afda424',
    'references/stage-7-qa-continuity.md': '76fb51bea742a76a2642029d587472fcbe99ada63ecc066a33ea8a44a7b4ec6d',
    'references/production-workflow.md': '68d30274c6a375371cd9dfb6837958fea3f409da45d431df0debe99fd69f5961',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'cee3b580a447f686b4fc62723438c39dbd8f8233f01c8550e3b1086878bf7a7b',
    'references/camera-vocabulary.md': 'de1cd86da8fbf17c778038a565d57a425218636c8a148abfec476aead1007bd8',
    'references/externalization-lexicon.md': '7a79bf1bf42805f185441a7767c95dd900dc390503674b286807df68eb709ce6',
    'references/genre-packs.md': '59e0d3858456582ec779a438ad96380afe3158e46c1fdff37f085cbdd7a9d742',
    'references/director-lenses.md': '5d76b7b5f1f2908ea732eab1bb69dee8f9c81297bc5203e1a788d274d5b8c36a',
    'templates/prompt-templates.md': '4f37de4d413ca36d042473b855b8ad4396802a1ea951787f9ddd5f680defa512',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': '6b8b783d20af949afa15c3543192c0458a4a32811b0ca8031066cc86941671b0',
    'templates/reference-asset-brief.md': 'adc6b7c7c52c169d31ee7ba83111293496e7133572a7bedc08bf4a08d251df0b',
    'templates/asset-registry.md': '9e393bd1ff8e12a61bb95e4e9aaed758a4bcc6e4b567bf6945369e39de63c2d7',
    'scripts/validate_prompt.py': '8f33f8373ebc092445540814cb669b6c3716f41c4a10b5002eba94a0f8244bd6',
    'scripts/prompt_structure.py': 'd9f73020e41eec19edee56b7ad8a45f9b973c28db9c93e451274ab6d1a0b60bf',
    'scripts/production_contract.py': '963653540c39519d99a731749736e96b39bed17005305af1082c857af5426bfa',
    'scripts/production_preflight.py': '80379ec01b3f952ee82cc1611e38b555ad41838bd0bb6f0ac52ddb5453605702',
    'scripts/emotion_library.py': '11b1257528d00edbf66a9637a9508966f26d23d1db97917b609127858ac0cc6d',
    'scripts/performance_checks.py': '5a54ee7c0cb77b67466ee6f7102ded648220cf8b922fea7da186f68ccd869ae0',
    'scripts/prose_hints.py': '22a5425c7cba5e01a9ea1608045192eb0c63cd5a9d48894ea43c9f8c9b035f5f',
}


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


class ProtectedZoneTests(unittest.TestCase):
    def test_production_and_performance_core_unchanged_since_1_0_0(self):
        for name, expected in PROTECTED.items():
            with self.subTest(file=name):
                self.assertEqual(sha(name), expected)


class SkillWiringTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_route_check_is_wired_into_skill(self):
        self.assertTrue((ROOT / 'scripts/route_check.py').exists())
        self.assertIn('scripts/route_check.py', self.read('SKILL.md'))


if __name__ == '__main__':
    unittest.main()
