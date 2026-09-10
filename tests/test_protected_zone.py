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

1.3.2 rebaselines validate_prompt.py: W22 no longer counts quoted acting annotations
(重读/轻读/一词/word …) as lines; W04's ">8 shots in 30s" hint applies only when the average
shot is under 2s (it contradicted the 1.3.0 one-line-per-cut convention); docstring names
film-director. No new codes. See CHANGELOG 1.3.2.

1.4.0 rebaselines six files for the reference-binding format change (identity vs
wardrobe split into two entries; no E-layer notes in 素材绑定; new WARN W24):
stage-6-prompt-compiler.md (§6.2 binding format + §6.6 self-check),
stage-5b-reference-assets.md (identity/wardrobe asset rows), prompt-templates.md
(T2/T3/T4/T5 + English REFERENCES), reference-asset-brief.md and asset-registry.md
(example rows), validate_prompt.py (W24). See CHANGELOG 1.4.0.

1.4.1 rebaselines stage-6-prompt-compiler.md (§6.2 图数) and stage-5b-reference-assets.md
(wardrobe row): the stability limit is by SUBJECT (character) count, not image count —
the identity/wardrobe split adds images (multi-view), not subjects, so it never triggers
抽卡 for <=8 characters; only the 30-image cap limits image count. Wording only.

1.4.2 rebaselines stage-6-prompt-compiler.md (6.2) and prompt-templates.md: each binding line
ends with the official 4.1 role tag (-形象参考/-服饰参考/-场景参考/-音色参考/-动作参考); a
character identity/wardrobe ref is tagged 唯一参考 and 全程锁定 (local [推论]); the body refers
to a split character as {name}(@图片{id} wearing @图{wardrobe}) using official @ syntax. Wording only.

1.5.0 rebaselines stage-5-directing-storyboard.md (§5.1c 节奏曲线 expanded into a shot-duration
rhythm method: vary shot length against the beat, accelerate into peaks, long shots must earn
their length, avoid a uniform/over-wide grid — fix a flat timeline by re-timing cuts, never by
trimming dialogue) and validate_prompt.py (new WARN W25: three or more consecutive shots of equal
duration read as a flat meter). W25 is a presence-only review hint like W23. See CHANGELOG 1.5.0."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    'assets/emotion-library.json': 'ef22ac8bfec33567344e13a927d47f7b577c3c6f07b110cc5a2e316523599977',
    'references/emotion-performance.md': 'a150f6047b6a484a6ab858a93773d9c28fab022ac274bcc358dd20684468d8d0',
    'references/emotion-index.json': '3fe3f2946669c2e649f79bdc82917dfa8bc528220d992f7166350623ee03e3d5',
    'references/stage-4-performance.md': 'ade55ddb33655042f6360bdde1bd5a0d4e149a479b1b407f142d510b696338a0',
    'references/stage-5-directing-storyboard.md': '1e6f3e4633479a2a83645f69ab513362c3d28f854855680983c157aee861a599',
    'references/stage-5b-reference-assets.md': 'ecd595f1b39d6a7396968562febf185533536a95b4f83719c61954b0c446b72f',
    'references/stage-6-prompt-compiler.md': '1ca4dd6d518540f099595c50daded02c3b5fb1b4eda4dd2b2d0a768fd0ad7ff4',
    'references/stage-7-qa-continuity.md': '7957aca66d6cda61e4c2de9a69464b61f96abdd0e1a595fe36ff82d37e9e2f68',
    'references/production-workflow.md': 'db8cc8de428952283a2cda4d7d23e0b1b0f4784ab18c54b57f674ca93eac6cfd',
    'references/performance-record.md': '1c970fd3dc7db2d45706361e8f283ae2f2d6d70c00e55f3f369e0f1bb8bcd4eb',
    'references/seedance-2.5-capabilities.md': 'cee3b580a447f686b4fc62723438c39dbd8f8233f01c8550e3b1086878bf7a7b',
    'references/camera-vocabulary.md': 'de1cd86da8fbf17c778038a565d57a425218636c8a148abfec476aead1007bd8',
    'references/externalization-lexicon.md': '7a79bf1bf42805f185441a7767c95dd900dc390503674b286807df68eb709ce6',
    'references/genre-packs.md': '8e7334eaa40d40f07278bf0493bfe9315c515f203cf9876acfca7e6fccd4dd40',
    'references/director-lenses.md': '5d76b7b5f1f2908ea732eab1bb69dee8f9c81297bc5203e1a788d274d5b8c36a',
    'templates/prompt-templates.md': '9a540c25e0ee9b19666a26f6c77bf76b5a592e0b5e7339510507057308fa9b11',
    'templates/performance-record.json': 'aced33a04bd1e72fe33e6e78ca64e4a938402654cdb3028ee4139d75ae64d159',
    'templates/production-record.json': '7adc7226bf0b7648ecc2f2320db3edefe317297bf7486645271d9f87d8bb56fd',
    'templates/shot-card.md': '2c59e1022197bc88fa3539cbe7dcc2c61ee4bd60c1586c380995ef9623005f30',
    'templates/reference-asset-brief.md': 'ed6e9e6f5c2b66ad29cf5ddb73b3ee7a1280c56e470a4ac5dc2937c2cfffc58d',
    'templates/asset-registry.md': '0628db7bc42ff34d8b2043f0a8f43f89edefd546d5bfc1eb940ba00858f4673e',
    'scripts/validate_prompt.py': 'dd498406c4362bb05e17768f8d3d231c7ec35a230dd2ad7a57332cffe4e75ba9',
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
