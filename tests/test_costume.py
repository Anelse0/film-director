"""1.7.0 W45 (costume_checks.py): a sustained wearing-state deviation while the character's binding lines use the
image-equals-state wording (唯一的服装 / 衣着一律按 @图 / 全场锁定). Fixtures are placeholder bar prompts (A / B) in the
offset EP05 s03 clip03 shape (jacket on at the start, off on the stool from shot 1). The document-wiring test lives in
test_release_170.py."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from costume_checks import declared_names, line_variant, state_pair, bound_names  # noqa: E402
from validate_prompt import validate  # noqa: E402

CHAR_ABS = '@A-基础形象：A 的人物参考，只参考面部与发型。A 的衣着一律按 @05_A_outfit。\n'
OUTFIT_ABS = '@05_A_outfit：A 身上唯一的服装。\n'
CHAR_STATE = '@A-基础形象：A 的人物参考，只参考面部与发型。A 的衣着一律按每一镜的文字：上身 @05_A_outfit 的白色礼服衬衫，礼服外套落座时脱下搭在凳上，下身 @05_A_outfit 的礼服长裤。\n'
OUTFIT_STATE = '@05_A_outfit：A 身上的衬衫与长裤；礼服外套只在开场穿着、之后搭在凳上，不穿回。\n'
OTHER = '@B-基础形象：B 的人物参考，只参考面部与发型。B 的衣着一律按 @01_B_outfit。\n@01_B_outfit：B 身上唯一的服装。\n@01_bar：酒吧的场景参考。\n'
OPENING = '【起始状态】A（@A-基础形象，穿 @05_A_outfit，礼服外套还穿在身上）站在吧台外的高脚凳旁，在画面中间；B（@B-基础形象，穿 @01_B_outfit）在吧台里。\n'
SHOTS = ('【分镜时间线】\n'
         '镜头1（0-3s）：【中近景，平视，固定，A 居中，焦点在 A】A 坐下，顺手脱下礼服外套，搭在旁边那张凳子上；他身上只剩白色礼服衬衫。视线：A 看着吧台里面。\n'
         '镜头2（3-6s）：【近景双人，平视，固定，A 画左、B 画右，焦点在 B】B 走到 A 对面。台词（B，3-6s，英语，轻松）："Hey. Long time."；此时 A 闭着嘴。\n'
         '镜头3（6-9s）：【近景，平视，固定，A 居中，焦点在 A 眼睛】A 顺手把衬衫袖口往上推了一点。台词（A，6-9s，英语，随意）："Been a while."；此时 B 闭着嘴。\n')
GLOBAL_SEG = ('【贯穿要求】保持一致：A 的脸和发型与 @A-基础形象 一致，衣着按 @05_A_outfit；镜头1 起他的礼服外套脱下，一直搭在旁边那张凳子上，不穿回。'
              'B 与 @B-基础形象、@01_B_outfit 一致。无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n')
GLOBAL_PLAIN = ('【贯穿要求】保持一致：A 的脸和发型与 @A-基础形象 一致，衣着按 @05_A_outfit；B 与 @B-基础形象、@01_B_outfit 一致。'
                '无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n')
E = '\n| 项 | 值 |\n|---|---|\n| duration | 9 |\n| 上传与角色 | @A-基础形象、@05_A_outfit、@B-基础形象、@01_B_outfit、@01_bar |\n'


def build(char=CHAR_ABS, outfit=OUTFIT_ABS, opening=OPENING, shots=SHOTS, global_rules=GLOBAL_SEG):
    return ('【素材绑定】\n' + char + outfit + OTHER + '【总述】9秒3:4竖屏，酒吧（@01_bar），A 坐下脱外套，B 过来招呼；声音：无 bgm，只有环境音与台词。\n'
            '【画面基调】暖光，深景深。\n' + opening + shots + global_rules + E)


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def w45(result):
    return [w for w in result['warnings'] if w.startswith('W45')]


def costume_info(result):
    return [i for i in result['info'] if i.startswith('穿着状态')]


class TriggerShapeTests(unittest.TestCase):
    def test_clip03_shape_fires_once_for_a_naming_both_lines(self):
        result = run(build())
        self.assertEqual(result['errors'], [], result['errors'])
        hits = w45(result)
        self.assertEqual(len(hits), 1, hits)
        self.assertTrue(hits[0].startswith('W45 A 的穿着状态与服装图不同（'), hits[0])
        self.assertIn('镜头1「脱下礼服外套」', hits[0])
        self.assertIn('@05_A_outfit「身上唯一的服装」', hits[0])
        self.assertIn('@A-基础形象「一律按 @', hits[0])
        self.assertIn('一律按每一镜的文字', hits[0])
        self.assertIn('「不参考 X」只用于本条从不出现的衣物', hits[0])
        self.assertFalse(any('B 的穿着状态' in h for h in hits))
        info = costume_info(result)
        self.assertEqual(len(info), 1, info)
        self.assertIn('A 3 处变化', info[0])            # 脱下礼服外套 / 只剩白色礼服衬衫 / 袖口往上推
        self.assertIn('【起始状态】已写开场状态', info[0])
        self.assertIn('【贯穿要求】已写分段状态', info[0])

    def test_state_writing_variant_is_clean(self):
        for char, outfit in ((CHAR_STATE, OUTFIT_STATE), (CHAR_STATE, OUTFIT_ABS), (CHAR_ABS, OUTFIT_STATE)):
            result = run(build(char=char, outfit=outfit))
            self.assertEqual(w45(result), [], (char, outfit, result['warnings']))
            self.assertEqual(len(costume_info(result)), 1)

    def test_override_row_keeps_the_design(self):
        result = run(build() + '| 穿着状态说明 | 用户定：仍用整套图，分段状态写在贯穿要求 |\n')
        self.assertEqual(w45(result), [])
        self.assertTrue(any('穿着状态说明 已写明' in i for i in costume_info(result)), result['info'])

    def test_info_reports_missing_opening_and_segment_states(self):
        opening = OPENING.replace('，礼服外套还穿在身上', '')
        result = run(build(opening=opening, global_rules=GLOBAL_PLAIN))
        self.assertIn('【起始状态】未写开场状态', costume_info(result)[0])
        self.assertIn('【贯穿要求】未写分段状态', costume_info(result)[0])
        self.assertEqual(len(w45(result)), 1)


class ScopeTests(unittest.TestCase):
    def test_no_deviation_means_no_w45_and_no_info(self):
        shots = SHOTS.replace('A 坐下，顺手脱下礼服外套，搭在旁边那张凳子上；他身上只剩白色礼服衬衫。', 'A 坐下，把手机放到台面上。') \
                     .replace('A 顺手把衬衫袖口往上推了一点。', 'A 把杯子推到一边。')
        result = run(build(opening=OPENING.replace('，礼服外套还穿在身上', ''), shots=shots, global_rules=GLOBAL_PLAIN))
        self.assertEqual(w45(result), [])
        self.assertEqual(costume_info(result), [])

    def test_donning_and_buttons_are_not_deviations(self):
        shots = SHOTS.replace('A 坐下，顺手脱下礼服外套，搭在旁边那张凳子上；他身上只剩白色礼服衬衫。', 'A 站起来，穿上礼服外套，扣上腰间那颗扣子。') \
                     .replace('A 顺手把衬衫袖口往上推了一点。', 'A 把袖扣扣好。')
        result = run(build(opening=OPENING.replace('，礼服外套还穿在身上', ''), shots=shots, global_rules=GLOBAL_PLAIN))
        self.assertEqual(w45(result), [])
        self.assertEqual(costume_info(result), [])

    def test_single_shot_minor_change_is_info_only(self):
        shots = SHOTS.replace('A 坐下，顺手脱下礼服外套，搭在旁边那张凳子上；他身上只剩白色礼服衬衫。', 'A 坐下，把外套敞开。') \
                     .replace('A 顺手把衬衫袖口往上推了一点。', 'A 把杯子推到一边。')
        result = run(build(opening=OPENING.replace('，礼服外套还穿在身上', ''), shots=shots, global_rules=GLOBAL_PLAIN))
        self.assertEqual(w45(result), [])
        self.assertIn('A 1 处变化', costume_info(result)[0])

    def test_other_characters_pair_and_props_do_not_fire(self):
        # B's line is absolute but the deviation belongs to A, whose pair is scoped: nothing fires.
        result = run(build(char=CHAR_STATE, outfit=OUTFIT_STATE))
        self.assertEqual(w45(result), [])
        # A garment on a rack is a prop, not a wearing state.
        shots = SHOTS.replace('A 坐下，顺手脱下礼服外套，搭在旁边那张凳子上；他身上只剩白色礼服衬衫。', '衣架上挂着他换下的礼服外套。') \
                     .replace('A 顺手把衬衫袖口往上推了一点。', 'A 把杯子推到一边。')
        result = run(build(opening=OPENING.replace('，礼服外套还穿在身上', ''), shots=shots, global_rules=GLOBAL_PLAIN))
        self.assertEqual(w45(result), [])

    def test_numbered_form_and_english_verbs(self):
        text = ('【素材绑定】图1 = A 外观，只参考面部与发型；图2 = A 的服装，全程锁定；图3 = 酒吧空镜，不参考人物。\n'
                '【总述】6秒3:4竖屏，酒吧（图3），A 脱外套；声音：无 bgm，只有环境音。\n【画面基调】暖光，深景深。\n'
                '【起始状态】图1的A 站在吧台边，礼服外套还穿在身上。\n【分镜时间线】\n'
                '镜头1（0-3s）：【中近景，平视，固定，A 居中，焦点在 A】A takes off his jacket and drapes it over the stool. 视线：A 看着吧台。\n'
                '镜头2（3-6s）：【近景，平视，固定，A 居中，焦点在 A 眼睛】A 把衬衫袖口往上推了一点。视线：A 看着杯子。\n'
                '【贯穿要求】A 的脸与图1一致，衣着按图2；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音；不要字幕。\n'
                '\n| 项 | 值 |\n|---|---|\n| duration | 6 |\n')
        hits = w45(run(text))
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('img2「全程锁定」', hits[0])

    def test_helpers(self):
        declared = [{'id': '@A-基础形象', 'line': CHAR_ABS.strip()}, {'id': '@05_A_outfit', 'line': OUTFIT_ABS.strip()},
                    {'id': '@Jo', 'line': '@Jo：Theo 的经纪人 Jo（年轻女性）的人物参考，只参考面部与发型。Jo 的衣着一律按 @02_Jo_outfit。'},
                    {'id': '@02_Jo_outfit', 'line': '@02_Jo_outfit：Jo 身上唯一的服装。'}]
        names = declared_names(declared)
        self.assertEqual(names, ['A', 'Jo'])           # the identity prefix 「Theo 的经纪人」 does not declare Theo
        self.assertEqual(bound_names('@Jo', declared[2]['line'], names), ['Jo'])
        self.assertEqual(bound_names('@02_Jo_outfit', declared[3]['line'], names), ['Jo'])
        self.assertEqual(bound_names('@05_A_outfit', OUTFIT_ABS, names), ['A'])
        self.assertEqual(line_variant(CHAR_ABS)[0], 'absolute')
        self.assertEqual(line_variant(OUTFIT_STATE)[0], 'scoped')
        self.assertEqual(line_variant('@05_A_outfit：A 唯一的服装参考：黑色礼服外套、白衬衫。镜头3才穿上外套。')[0], 'scoped')
        self.assertEqual(line_variant('@01_bar：酒吧的场景参考，全场锁定。'), (None, None))
        self.assertIsNotNone(state_pair('A 顺手脱下礼服外套，搭在凳子上'))
        self.assertIsNotNone(state_pair('A 把衬衫袖口往上推了一点'))
        self.assertIsNone(state_pair('她把头发挽起，米白衬衫'))          # 挽起 the hair, not a sleeve
        self.assertIsNone(state_pair('A 只穿他自己那套 @05_A_outfit'))   # the whole outfit = the image
        self.assertIsNone(state_pair('A 的衣着一律按 @05_A_outfit'))


if __name__ == '__main__':
    unittest.main()
