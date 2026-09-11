"""2.0.0 performance-grammar contracts: index composition fields, lookups, examples.

These test data shape and tool behaviour only; readability / min_seconds are
[推论] estimates and never a quality judgement.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from emotion_library import load_library, load_index, select, neighbors, ladder, by_readability, listeners  # noqa: E402
from validate_prompt import validate  # noqa: E402

SCALE = ["特写", "近景", "中近景", "中景"]
FIELDS = ("zh", "hinge", "readability", "wider_parts", "onset", "min_seconds", "ladder", "listener", "mask", "neighbors")


class IndexShapeTests(unittest.TestCase):
    def setUp(self):
        self.entries = load_library()
        self.index = load_index()

    def test_every_entry_has_composition_fields_in_range(self):
        for eid in self.entries:
            row = self.index[eid]
            with self.subTest(entry=eid):
                for key in FIELDS:
                    self.assertIn(key, row)
                for key in ("zh", "hinge", "onset", "ladder", "mask"):
                    self.assertTrue(isinstance(row[key], str) and row[key].strip())
                self.assertIn(row["readability"], SCALE)
                self.assertIsInstance(row["wider_parts"], list)
                self.assertTrue(type(row["min_seconds"]) is int and 1 <= row["min_seconds"] <= 10)
                self.assertIsInstance(row["listener"], bool)
                # original reading fields survive
                for key in ("terms", "cues", "relations"):
                    self.assertTrue(row[key])

    def test_neighbors_are_valid_distinct_and_bridged(self):
        for eid in self.entries:
            links = self.index[eid]["neighbors"]
            with self.subTest(entry=eid):
                self.assertTrue(2 <= len(links) <= 5)
                ids = [l["id"] for l in links]
                self.assertEqual(len(ids), len(set(ids)))
                for link in links:
                    self.assertIn(link["id"], self.entries)
                    self.assertNotEqual(link["id"], eid)
                    self.assertTrue(link["bridge"].strip())

    def test_zh_is_a_rendering_not_the_original(self):
        for eid, entry in self.entries.items():
            zh = self.index[eid]["zh"]
            self.assertNotEqual(zh, entry["prompt"])
            self.assertNotIn("https://", zh)
            # A rendering keeps the library's sentence count within one.
            en_sentences = entry["prompt"].count(". ") + 1
            zh_sentences = zh.count("。")
            self.assertLessEqual(abs(en_sentences - zh_sentences), 1, (eid, en_sentences, zh_sentences))

    def test_duchenne_pair_is_encoded(self):
        self.assertIn("笑纹", self.index[1]["hinge"])
        self.assertIn("无眼角笑纹", self.index[25]["hinge"])
        self.assertIn("内眉角", self.index[19]["hinge"])


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.entries = load_library()
        self.index = load_index()

    def test_query_searches_own_notes_not_neighbor_bridges(self):
        hits = [e["id"] for e in select(self.entries, self.index, query="害羞")]
        self.assertIn(21, hits)
        self.assertNotIn(1, hits)  # 1's neighbour bridge mentions 害羞→笑, that is not a hit
        self.assertEqual(select(self.entries, self.index, query="nonexistent-emotion"), [])

    def test_neighbors_ladder_readability_listener(self):
        rage = neighbors(self.entries, self.index, 4)
        self.assertIn(19, [r["id"] for r in rage])
        self.assertTrue(all(r["bridge"] and r["hinge"] for r in rage))
        with self.assertRaises(ValueError):
            neighbors(self.entries, self.index, 999)
        sad = ladder(self.entries, self.index, "sadness")
        self.assertEqual([r["id"] for r in sad][0], 19)
        self.assertEqual([r["id"] for r in sad][-1], 6)
        with self.assertRaises(ValueError):
            ladder(self.entries, self.index, "NoSuchFamily")
        cu = {r["id"] for r in by_readability(self.entries, self.index, "特写")}
        ms = {r["id"] for r in by_readability(self.entries, self.index, "中景")}
        self.assertTrue(cu < ms)
        self.assertIn(9, cu)
        self.assertNotIn(24, cu)
        with self.assertRaises(ValueError):
            by_readability(self.entries, self.index, "大远景")
        self.assertIn(14, [r["id"] for r in listeners(self.entries, self.index)])

    def test_cli_flags(self):
        script = ROOT / "scripts/emotion_library.py"
        def run(*args):
            out = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            return out.stdout
        self.assertIn("\"bridge\"", run("--neighbors", "25"))
        self.assertIn("Crying", run("--ladder", "Sadness"))
        self.assertIn("\"readability\"", run("--readability", "近景"))
        self.assertIn("Realization", run("--listener"))
        with_zh = json.loads(run("--id", "23", "--zh"))[0]
        self.assertTrue(with_zh["zh"].startswith("一口大而可见的呼气"))
        self.assertEqual(with_zh["composition"]["readability"], "中近景")
        self.assertEqual(run("--id", "6", "--raw").strip(), self.entries[6]["prompt"])
        # --list is unchanged in shape apart from the readability hint
        listing = json.loads(run("--list"))
        self.assertEqual(len(listing), 25)
        self.assertIn("terms", listing[0])


class ExampleTests(unittest.TestCase):
    def test_mask_and_leak_record_matches(self):
        record = json.loads((ROOT / "examples/performance/07-mask-and-leak.performance.json").read_text(encoding="utf-8"))
        result = validate(ROOT / "examples/performance/07-mask-and-leak.prompt.md", artifact="performance", record=record)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["checks"]["fidelity"], "matched")
        self.assertEqual(record["mode"], "blend")
        self.assertEqual({eid for b in record["beats"] for eid in b["entry_ids"]}, {25, 19, 6})

    def test_listener_chain_is_clean_production(self):
        result = validate(ROOT / "examples/performance/08-listener-reaction-chain.prompt.md")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["checks"]["performance"], "needs_review")


if __name__ == "__main__":
    unittest.main()
