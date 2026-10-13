"""1.6.0 official-guide alignment: W36–W41 + INFO (guide_checks.py), @名 asset binding (validate_prompt.py,
production_contract.py), and the E-layer 变化轨 row (variation_checks.py).

Fixtures are placeholder bar-scene prompts in both binding forms (numbered 图N and platform @名). The W36 / W37 /
W40 rules come from the 2026-10 edition of the official guide's 常见问题 (capabilities §8)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from guide_checks import length_profile, upload_order, is_character, post_quote_notes, requoted_fragments  # noqa: E402
from variation_checks import parse_track_row, profile  # noqa: E402
from production_contract import roles_from_fields  # noqa: E402
from validate_prompt import validate  # noqa: E402

HEAD_NUM = '【素材绑定】图1 = A 外观，只参考面部与发型；图2 = B 外观，只参考面部与发型；图3 = 酒吧空镜，不参考人物。\n'
HEAD_NAME = ('【素材绑定】\n@A-基础形象：A 的人物参考，只参考面部与发型。A 的衣着一律按 @A_outfit。\n'
             '@A_outfit：A 身上唯一的服装。\n@B-基础形象：B 的人物参考，只参考面部与发型。\n@01_bar：酒吧的空间、陈设与光色参考。\n')
BODY = ('【总述】8秒3:4竖屏，酒吧{scene}，A 和 B 聊天；声音：无 bgm，只有环境音与台词。\n【画面基调】暖光，深景深。\n'
        '【起始状态】{A} 在画左吧台里，面朝台面；{B} 在画右，看着 A；机位在吧台外。\n【分镜时间线】\n'
        '镜头1（0-4s）：【中近景双人，平视，固定】A 搅酒，B 看着他。台词（B，0-3s，英语，轻快）："Can you cover my shift?"；此时 A 闭着嘴。\n'
        '镜头2（4-8s）：【近景，平视，固定，A 正面】A 抬眼看向画右的 B，嘴角抬一点。台词（A，4-7s，英语，轻松）："You still owe me."；此时 B 闭着嘴。\n'
        '【贯穿要求】A 与 B 的脸和发型按各自素材；画面里只有两人；无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词；不要字幕。\n')
E = ('\n| 项 | 值 |\n|---|---|\n| duration | 8 |\n| 峰值镜 | 2 |\n'
     '| 变化轨 | 镜1：景别 中近｜机位 固定｜光 暖｜幅度 2；镜2：景别 中近→近｜机位 =｜光 =｜幅度 2→1 |\n')


def numbered():
    return HEAD_NUM + BODY.format(scene='（图3）', A='图1的A', B='图2的B') + E


def named():
    return (HEAD_NAME + BODY.format(scene='（@01_bar）', A='A（@A-基础形象，穿 @A_outfit）', B='B（@B-基础形象）') + E
            + '| 上传与角色 | @A-基础形象、@A_outfit、@B-基础形象、@01_bar |\n')


def run(text):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'clip.prompt.md'
        path.write_text(text, encoding='utf-8')
        return validate(path)


def codes(result):
    return {w.split()[0] for w in result['warnings']}


NEW_CODES = {'W36', 'W37', 'W38', 'W39', 'W40', 'W41'}


class BaselineTests(unittest.TestCase):
    def test_both_binding_forms_are_clean_and_read_the_e_row(self):
        for text in (numbered(), named()):
            result = run(text)
            self.assertEqual(result['errors'], [], result['errors'])
            self.assertFalse(codes(result) & NEW_CODES, result['warnings'])
            self.assertNotIn('W32', codes(result))
            self.assertTrue(any('声明来源 E 层' in i for i in result['info']), result['info'])
            self.assertTrue(any(i.startswith('篇幅') for i in result['info']))

    def test_named_assets_are_declared_and_referenced(self):
        result = run(named())
        self.assertEqual(result['assets']['declared'], sorted(['@A-基础形象', '@A_outfit', '@B-基础形象', '@01_bar']))
        self.assertTrue(any('@名 4' in i for i in result['info']), result['info'])


class W36Tests(unittest.TestCase):
    def test_delivery_note_after_the_quote_and_requoted_fragment(self):
        text = numbered().replace('"Can you cover my shift?"；', '"Can you cover my shift?"（轻快，带笑）；')
        hits = [w for w in run(text)['warnings'] if w.startswith('W36')]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('引号后追加', hits[0])
        text = numbered().replace('此时 A 闭着嘴。', '此时 A 闭着嘴。说到「cover」时她眨了一下眼。')
        hits = [w for w in run(text)['warnings'] if w.startswith('W36')]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('复述', hits[0])
        self.assertEqual(post_quote_notes('台词（A，0-2s，英语）："Hi."（画外）；'), [])
        self.assertEqual(requoted_fragments('台词（A，0-2s，英语）："Hi there."；她眨眼。'), [])


class W37Tests(unittest.TestCase):
    def test_policy_only_at_the_end_and_too_few_synonyms(self):
        end_only = numbered().replace('；声音：无 bgm，只有环境音与台词。', '。')
        hits = [w for w in run(end_only)['warnings'] if w.startswith('W37')]
        self.assertTrue(any('只写在结尾' in h for h in hits), hits)
        thin = numbered().replace('无 bgm：不要音乐、背景音乐、配乐、器乐、旋律与铺底音，只生成环境音、动作音与台词', '无 bgm，只生成环境音、动作音与台词')
        hits = [w for w in run(thin)['warnings'] if w.startswith('W37')]
        self.assertTrue(any('同义词' in h or '音乐类词' in h for h in hits), hits)


class W38Tests(unittest.TestCase):
    def test_info_always_warn_over_budget_and_override(self):
        base = run(numbered())
        self.assertTrue(any(i.startswith('篇幅') and '贯穿要求' in i for i in base['info']))
        self.assertNotIn('W38', codes(base))
        filler = '人物放在画面中间区域。' * 200   # ~2,200 CJK characters
        long = numbered().replace('不要字幕。\n', '不要字幕。' + filler + '\n')
        self.assertIn('W38', codes(run(long)))
        self.assertNotIn('W38', codes(run(long + '| 字数上限 | 3000 |\n')))
        cjk, words, per = length_profile('【总述】十个字十个字十个字十个\n【贯穿要求】五个字五个字')
        self.assertEqual((cjk, [p[0] for p in per]), (23, ['总述', '贯穿要求']))   # labels count: the model reads them too


class W39Tests(unittest.TestCase):
    def test_character_first_appearance_order_and_upload_row(self):
        swapped = named().replace('【起始状态】A（@A-基础形象，穿 @A_outfit） 在画左吧台里，面朝台面；B（@B-基础形象） 在画右，看着 A；',
                                  '【起始状态】B（@B-基础形象） 在画右，看着 A；A（@A-基础形象，穿 @A_outfit） 在画左吧台里，面朝台面；')
        hits = [w for w in run(swapped)['warnings'] if w.startswith('W39')]
        self.assertTrue(any('首次出场顺序' in h for h in hits), hits)
        row = named().replace('| 上传与角色 | @A-基础形象、@A_outfit、@B-基础形象、@01_bar |', '| 上传与角色 | @B-基础形象、@A-基础形象、@A_outfit、@01_bar |')
        hits = [w for w in run(row)['warnings'] if w.startswith('W39')]
        self.assertTrue(any('上传与角色' in h for h in hits), hits)
        self.assertEqual(upload_order('| 上传与角色 | img1 = @A, img2 = @B |'), ['@A', '@B'])   # mapping rows yield the names
        self.assertEqual(upload_order('| 上传与角色 | img1、aud1、img2 |'), ['img1', 'aud1', 'img2'])

    def test_character_detection_from_declaration_lines(self):
        self.assertTrue(is_character('@A-基础形象：A 的人物参考，只参考面部与发型。A 的衣着一律按 @A_outfit。'))
        self.assertFalse(is_character('@A_outfit：A 身上唯一的服装。'))
        self.assertFalse(is_character('@01_bar：酒吧的场景参考，不参考图中人物。'))
        self.assertTrue(is_character('图1 = 母亲外观，只参考面部、发型与米色针织开衫，不参考背景与姿势'))


class W40Tests(unittest.TestCase):
    def test_intensity_label_warns_and_guard_line_is_suggested(self):
        text = numbered().replace('A 抬眼看向画右的 B，嘴角抬一点。', 'A 极度惊骇地抬眼看向画右的 B。')
        result = run(text)
        self.assertIn('W40', codes(result))
        self.assertTrue(any('不发光' in i for i in result['info']), result['info'])
        guarded = text.replace('；声音：无 bgm', '；人物为正常人眼，不发光；声音：无 bgm')
        self.assertFalse(any('不发光' in i for i in run(guarded)['info']))


class W41AndE05Tests(unittest.TestCase):
    def test_declared_but_unreferenced_assets(self):
        text = named().replace('@01_bar：酒吧的空间、陈设与光色参考。\n', '@01_bar：酒吧的空间、陈设与光色参考。\n@02_bar：另一间酒吧的参考。\n')
        hits = [w for w in run(text)['warnings'] if w.startswith('W41')]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn('@02_bar', hits[0])
        text = numbered().replace('图3 = 酒吧空镜，不参考人物。', '图3 = 酒吧空镜，不参考人物；图4 = 道具杯子。')
        self.assertTrue(any('img4' in w for w in run(text)['warnings'] if w.startswith('W41')))

    def test_undeclared_name_is_e05_and_prefix_mentions_resolve(self):
        text = named().replace('A 搅酒，B 看着他。', 'A 搅酒，C（@C-基础形象）看着他。')
        self.assertTrue(any(e.startswith('E05') and '@C-基础形象' in e for e in run(text)['errors']))
        text = named().replace('A 搅酒，B 看着他。', '@A-基础形象的脸转向 B。')
        self.assertEqual(run(text)['errors'], [])

    def test_prose_declarations_in_the_binding_section_count(self):
        head = ('【素材绑定】\n@01_bar、@02_bar：酒吧的场景唯一参考，全场锁定。\n'
                '@A-基础形象：A 的形象唯一参考，人物五官参考此图；服饰以 @A_outfit 为准。\n@A_outfit：A 的服饰唯一参考。\n')
        body = BODY.format(scene='（@01_bar、@02_bar）', A='A（@A-基础形象，穿 @A_outfit）', B='B')
        result = run(head + body + E)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['assets']['declared'], sorted(['@01_bar', '@02_bar', '@A-基础形象', '@A_outfit']))


class VariationRowTests(unittest.TestCase):
    def test_e_row_grammar_precedence_and_missing_shot(self):
        row = parse_track_row(E)
        self.assertEqual(sorted(row), [1, 2])
        self.assertEqual(row[2]['景别'], ('中近', '近', True))
        self.assertFalse(row[2]['机位'][2])
        shots = [(1, 0, 4, '【中近景，固定】'), (2, 4, 8, '【近景，固定】【变化：景别 中近→近｜机位 固定→推｜光 =｜幅度 =】')]
        rows = profile(shots, E)
        self.assertEqual([r['source'] for r in rows], ['E 层', 'E 层'])
        self.assertFalse(rows[1]['changes']['机位'])          # the E row (=) wins over the legacy inline field (固定→推)
        self.assertEqual(profile(shots, '')[1]['source'], '行内')
        partial = numbered().replace('；镜2：景别 中近→近｜机位 =｜光 =｜幅度 2→1', '')
        self.assertTrue(any('缺镜头 [2]' in w for w in run(partial)['warnings']))


class ContractTests(unittest.TestCase):
    def test_role_map_accepts_names_and_numbers(self):
        roles = roles_from_fields({'content.role 映射': '@A-基础形象→reference_image, img3→reference_image'})
        self.assertEqual(roles, {'@A-基础形象': 'reference_image', 'img3': 'reference_image'})


class WiringTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_documents_carry_the_release(self):
        self.assertEqual(self.read('VERSION').strip(), '1.6.0')
        for code in NEW_CODES:
            self.assertIn(f'| {code} |', self.read('references/duration-rhythm.md'), code)
        self.assertIn('## 8.', self.read('references/seedance-2.5-capabilities.md'))
        self.assertIn('## 4.4a', self.read('references/stage-4-performance.md'))
        self.assertIn('## 4.4c', self.read('references/stage-4-performance.md'))
        self.assertIn('变化轨', self.read('templates/prompt-templates.md'))
        self.assertNotIn('【变化：', self.read('templates/prompt-templates.md').split('## P 表演片段')[1])
        self.assertIn('W36–W41', self.read('SKILL.md'))


if __name__ == '__main__':
    unittest.main()
