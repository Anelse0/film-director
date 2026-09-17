"""1.1.0 directing-core release checks: validator thresholds follow the official 30s example,
the punctuation heuristic is retired, the new worked examples pass, and the grammar/carrier
documents are wired into the skill. No creative or render quality is graded here."""
import re
import unittest
from pathlib import Path

from test_production import run, ROOT
from validate_prompt import validate


def prompt_with_shots(shots):
    body = "\n".join(f"镜头{i+1}（{s}-{e}s）：【近景，固定】人物抬眼。" for i, (s, e) in enumerate(shots))
    return ("【素材绑定】无参考素材。\n【总述】30秒16:9，室内。\n【起始状态】A 居中。\n【分镜时间线】\n"
            + body + "\n【贯穿要求】无bgm，只有环境音；不要字幕。")


class ValidatorThresholdTests(unittest.TestCase):
    def test_official_density_nine_shots_two_second_minimum_is_not_flagged(self):
        # PDF p.20: 9 shots in 30s, shortest 2s.
        shots = [(0, 3), (3, 6), (6, 10), (10, 14), (14, 18), (18, 22), (22, 25), (25, 28), (28, 30)]
        result = run(prompt_with_shots(shots))
        self.assertFalse(any(w.startswith("W04") for w in result["warnings"]), result["warnings"])

    def test_sub_two_second_and_over_ten_shots_are_review_hints(self):
        shots = [(i, i + 1) for i in range(0, 12)] + [(12, 30)]
        result = run(prompt_with_shots(shots))
        hints = [w for w in result["warnings"] if w.startswith("W04")]
        self.assertEqual(len(hints), 2)
        self.assertTrue(any("< 2s" in w for w in hints))
        self.assertTrue(any("> 10" in w for w in hints))

    def test_punctuation_heuristic_w19_is_retired(self):
        body = '台词（A，0-8s，中文普通话）："走。别回头。我说真的！"'
        text = ("【素材绑定】无参考素材。\n【总述】10秒16:9，室内。\n【起始状态】A 居中。\n【分镜时间线】\n"
                "镜头1（0-10s）：【近景，固定】\n" + body + "\n【贯穿要求】无bgm，只有环境音；不要字幕。")
        result = run(text)
        self.assertFalse(any(w.startswith("W19") for w in result["warnings"]))


class WorkedExampleTests(unittest.TestCase):
    def test_example_05_keyframe_carrier_is_clean(self):
        result = validate(ROOT / "examples/example-05-stairwell-letter.prompt.md")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["task"], "keyframe")
        self.assertEqual([r["text"] for r in result["dialogue"]], ["你来得比我想的早。", "信呢？"])

    def test_example_06_romance_is_clean_and_turn_taking(self):
        result = validate(ROOT / "examples/example-06-balcony-cigarette.prompt.md")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])
        windows = [(r["start"], r["end"]) for r in result["dialogue"]]
        self.assertEqual(windows, [(6, 8), (14, 16)])


class WiringTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding="utf-8")

    def test_grammar_and_carrier_are_referenced(self):
        skill = self.read("SKILL.md")
        self.assertIn("references/director-grammar.md", skill)
        self.assertIn("决策载体", skill)
        stage5 = self.read("references/stage-5-directing-storyboard.md")
        self.assertIn("## 5.0 决策载体", stage5)
        self.assertIn("走位表", stage5)
        grammar = self.read("references/director-grammar.md")
        for phrase in ("Mackendrick", "动机", "终点", "关键帧", "白模", "§十"):
            self.assertIn(phrase, grammar)

    def test_no_fixed_intent_to_body_mapping_in_stage4(self):
        text = self.read("references/stage-4-performance.md")
        self.assertNotIn("每个动词配一个身体证据", text)
        self.assertNotIn("策略列只接受", text)
        self.assertIn("不建立", text)

    def test_lexicon_camera_column_no_longer_prescribes_moves(self):
        text = self.read("references/externalization-lexicon.md")
        for phrase in ("缓慢推近；环境音不变", "镜头缓慢后拉", "镜头略高俯视"):
            self.assertNotIn(phrase, text)

    def test_dialogue_budget_has_primary_sources(self):
        text = self.read("references/seedance-2.5-capabilities.md")
        for phrase in ("150 words per minute", "Tauroza", "Netflix", "2.5 词/s", "4 字/s"):
            self.assertIn(phrase, text)

    def test_all_skill_links_resolve(self):
        text = self.read("SKILL.md")
        for ref in set(re.findall(r"`((?:references|templates|scripts|examples)/[^`]+)`", text)):
            self.assertTrue((ROOT / ref).exists(), ref)


if __name__ == "__main__":
    unittest.main()
