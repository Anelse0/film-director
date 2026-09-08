"""Files kept byte-identical with the sibling film-creative checkout (skipped when it is absent).

The two skills each carry a copy of the collaboration contract and of the stdlib xlsx helpers;
a change on one side without the other silently desynchronises the pair."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent / 'film-creative'
SHARED = ['references/handoff-contract.md', 'scripts/xlsx_lite.py', 'scripts/ledger_view.py']


@unittest.skipUnless(SIBLING.is_dir(), 'sibling film-creative checkout not present')
class SharedFilesTests(unittest.TestCase):
    def test_shared_files_identical_to_film_creative(self):
        for name in SHARED:
            with self.subTest(file=name):
                self.assertEqual((ROOT / name).read_bytes(), (SIBLING / name).read_bytes(),
                                 f'{name} differs from the film-creative copy; update both in the same change')


if __name__ == '__main__':
    unittest.main()
