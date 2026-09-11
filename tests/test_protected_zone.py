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
W20 stays a WARN-level review hint). See CHANGELOG 1.1.1.

1.2.0 rebaselines stage-5-directing-storyboard.md: adds the reusable directing rule "引荐与亮相
的顺序（介绍先行，特写作揭示）" under 5.1d plus a matching 5.9 troubleshooting row. Guidance only —
no validation/code change. See CHANGELOG 1.2.0.

1.3.0 rebaselines validate_prompt.py: adds W22 (dialogue-carrying long shot) and W23 (three
consecutive identical shot tags), WARN-level pacing hints for dialogue scenes. See CHANGELOG 1.3.0.
2.0.0 rebaselines the performance/directing core for the performance grammar and the
first-hand director craft: emotion-index.json (zh / hinge / readability / neighbors …),
emotion_library.py (composition lookups), stage-4, stage-5, stage-5b, stage-6,
seedance-2.5-capabilities.md (§4.9), director-lenses.md, shot-card.md and
validate_prompt.py (W04 recalibrated to average shot length); adds
performance-grammar.md and director-craft.md to the protected set. emotion-library.json
is byte-identical. See CHANGELOG 2.0.0."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    'assets/emotion-library.json': 'ef22ac8bfec33567344e13a927d47f7b577c3c6f07b110cc5a2e316523599977',
    'references/emotion-performance.md': 'a150f6047b6a484a6ab858a93773d9c28fab022ac274bcc358dd20684468d8d0',
    'references/emotion-index.json': '9e4498b7d81993e1cffe99f065e3acd15c9fa0cbc52539932a6853f2affe5738',
    'references/stage-4-performance.md': '187b0e100283af1d28baa2ae3ede1fb36157f50e8165d0787da52ca46354195a',
    'references/stage-5-directing-storyboard.md': 'be820f1522ef193872d4eb2d5552ba7f42d72ef66229d087d7b8bacbb8969233',
    'references/stage-5b-reference-assets.md': 'e43931abe812c41ada21b63136f2d05cf779f3d87c576b1185a8848cabd8a0e6',
    'references/stage-6-prompt-compiler.md': '6ccd657acea3a8695c432e6f53784d3b768fb6daf8d3faf08ba8aeb5c076ebc6',
    'references/stage-7-qa-continuity.md': '7957aca66d6cda61e4c2de9a69464b61f96abdd0e1a595fe36ff82d37e9e2f68',
    'references/production-workflow.md': 'db8cc8de428952283a2cda4d7d23e0b1b0f4784ab18c54b57f674ca93eac6cfd',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'e600c6e31f4d182cde3991bfe602b4c55e16896863e0510f956e6ddd30d036bd',
    'references/camera-vocabulary.md': 'de1cd86da8fbf17c778038a565d57a425218636c8a148abfec476aead1007bd8',
    'references/externalization-lexicon.md': '7a79bf1bf42805f185441a7767c95dd900dc390503674b286807df68eb709ce6',
    'references/genre-packs.md': '8e7334eaa40d40f07278bf0493bfe9315c515f203cf9876acfca7e6fccd4dd40',
    'references/director-lenses.md': '2cebe94a7c494d800f14a53fb1ee971f1f7a1b7acf2293019d0611e3367d0813',
    'references/performance-grammar.md': 'b3e96e0765e9aa24d013e30b2e80945c4213b08a93b4a98ec64c0c1572ebbb95',
    'references/director-craft.md': '21dd4b28abd9a8ec9a0e4521386eac3ff2709e9801b740a2a70abb441e569eb5',
    'templates/prompt-templates.md': 'c1f83c00453494b185b2bd1c1a7baf247157e6348288021275332ce74eee9006',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': 'fb5e4e276dca0f73bfaca110f1fe14fff2f428dec625558019da966c0c0cdc79',
    'templates/reference-asset-brief.md': 'adc6b7c7c52c169d31ee7ba83111293496e7133572a7bedc08bf4a08d251df0b',
    'templates/asset-registry.md': '996818cda8aa55796820ae96c808c56459198f8f465b4e4924196d7ed8cc2943',
    'scripts/validate_prompt.py': '588a6e8180491b5440150bb8c87995fa6b43c5bbe9fdb7a42f3b38fea648616f',
    'scripts/prompt_structure.py': 'd9f73020e41eec19edee56b7ad8a45f9b973c28db9c93e451274ab6d1a0b60bf',
    'scripts/production_contract.py': '963653540c39519d99a731749736e96b39bed17005305af1082c857af5426bfa',
    'scripts/production_preflight.py': '80379ec01b3f952ee82cc1611e38b555ad41838bd0bb6f0ac52ddb5453605702',
    'scripts/emotion_library.py': 'c017e8c0b0d6328ecacc2a25282b239fdc2438b7634c55d870c717bd2f27668a',
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
