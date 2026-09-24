"""1.10.0 wardrobe per character, per shot (hard rule 21; E23 / W36 in wardrobe_checks.py).

Trigger: 2026-09-24 set scene (r2v, 20 s, 8 shots). Rhett's appearance image wears a white polo and Theo's a black
sweater; the binding said only "不参考…图中白色 polo / 黑色毛衣", Theo's outfit image sat inside a bracket on his
binding line, and no shot restated anyone's wardrobe. The Prompt passed the 1.9.0 validator with 0 errors; in the
render Rhett wore a top and Theo followed his appearance image (user's judgement of the render, not a measured
run). Same failure 2026-09-23 on THE ORDER EP03 s04 ("@01_Sharks_outfit = 所有男生球员都穿这一套").
Fixtures: set-scene-v4 (the failing Prompt) and set-scene-v5 (the fix delivered to the user), both unchanged."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from wardrobe_checks import wardrobe_checks  # noqa: E402
from validate_prompt import validate  # noqa: E402

FIX = ROOT / 'tests' / 'fixtures' / 'wardrobe'


def prompt(refs, opening, shots, global_rules):
    body = ''.join(f'镜头{i}（{2 * (i - 1)}-{2 * i}s）：【中景，固定】{s}\n' for i, s in enumerate(shots, 1))
    return (f'【素材绑定】{refs}\n【总述】{2 * len(shots)}秒16:9，室内。\n【起始状态】{opening}\n【分镜时间线】\n{body}'
            f'【贯穿要求】{global_rules}；无bgm，只有环境音；不要字幕。\n')


def check(text):
    errors, warnings, infos, summary = wardrobe_checks(text)
    return errors, warnings


def w36(warnings, unit=None):
    return [w for w in warnings if w.startswith('W36') and (unit is None or w.startswith(f'W36 {unit} '))]


# Three sources for one character's wardrobe (hard rule 21).
OUTFIT_IMAGE = ('@Rhett = Rhett 人物形象，只参考面部与发型；本条衣着一律按@R_outfit ；\n'
                '@R_outfit = 本条 Rhett 身上唯一的服装：深灰毛巾浴袍 -- 服装参考；\n')
IMAGE_CLOTHES = '@Theo = Theo 的外观与服饰参考：参考面部、发型与图中衣服——黑色粗针织毛衣；不参考背景与姿势；\n'
TEXT_ONLY = '@Rhett = Rhett 人物形象，只参考面部与发型；本条衣着一律按每一镜的文字：赤裸上身、腰间围白浴巾；\n'
TOWEL = 'Rhett（@Rhett ，赤裸上身、腰间只围一条白浴巾）'


class BindingSourceTests(unittest.TestCase):
    """E23: an appearance-image line states the wardrobe source in positive words."""

    def test_three_positive_sources_pass(self):
        for refs in (OUTFIT_IMAGE, IMAGE_CLOTHES, TEXT_ONLY,
                     '图1 = 母亲外观，只参考面部、发型与米色针织开衫，不参考背景与姿势；',
                     '@Beckett Hale = Beckett人物形象，只参考面部与发型，不参考图中的服装（本条服装一律按对应服饰图）；'):
            with self.subTest(refs=refs[:24]):
                errors, _ = check(prompt(refs, '有人。', ['有人。'], '有人'))
                self.assertEqual(errors, [])

    def test_negative_only_or_silent_binding_is_e23(self):
        negative = '@Rhett = 饰演 Rhett 的男演员外观（棕色碎发），只参考面部、发型，不参考背景、姿势与图中白色 polo；'
        errors, _ = check(prompt(negative, '有人。', ['有人。'], '有人'))
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith('E23 @Rhett') and '只写了不参考图中衣服' in errors[0], errors)
        errors, _ = check(prompt('图1 = 人物外观。', '有人。', ['有人。'], '有人'))
        self.assertTrue(errors and errors[0].startswith('E23 图1'), errors)

    def test_outfit_ref_inside_a_negative_bracket_is_not_a_source(self):
        # v4 Theo: the outfit image only inside "不参考…黑色毛衣（身穿戏服@01_Theo_outfit ）".
        refs = ('@Theo = Theo 的外观，只参考面部、发型，不参考背景、姿势与图中黑色毛衣（身穿戏服@01_Theo_outfit ）；\n'
                '@01_Theo_outfit = 戏服参考：奶白针织 polo -- 服饰参考；')
        errors, _ = check(prompt(refs, '有人。', ['有人。'], '有人'))
        self.assertTrue(any(e.startswith('E23 @Theo') for e in errors), errors)
        # the outfit line naming him ("Theo 演员的戏服") states the source on its own line: not E23
        named = refs.replace('= 戏服参考', '= Theo 演员的戏服唯一参考')
        self.assertEqual(check(prompt(named, '有人。', ['有人。'], '有人'))[0], [])
        # "Isa身穿@01_Sharks_outfit" before the 不参考 clause is a source (THE ORDER EP04 binding style)
        isa = ('@Isaiah Marsh = Isa人物形象，只参考面部与发型；Isa身穿@01_Sharks_outfit，不参考图中的服装、姿势与背景。\n'
               '@01_Sharks_outfit = Sharks队员服装，只参考服装款式与颜色。')
        self.assertEqual(check(prompt(isa, '有人。', ['有人。'], '有人'))[0], [])

    def test_two_sources_in_one_line_is_e23(self):
        refs = ('@Theo = Theo 外观，参考面部、发型与图中衣服；衣着一律按@T_outfit ；\n'
                '@T_outfit = Theo 的服装参考；')
        errors, _ = check(prompt(refs, '有人。', ['有人。'], '有人'))
        self.assertTrue(any('两个衣着来源' in e for e in errors), errors)

    def test_scene_prop_keyframe_voice_and_outfit_lines_are_not_characters(self):
        refs = ('图1 = 客厅布局与夜间光线，不参考图中人物；图2 = 镜头1关键帧（A 中景）；图3 = 钥匙道具外观；'
                '图4 = A 的戏服，服装参考；音频1 = A 音色，不参考内容。')
        errors, warnings, infos, summary = wardrobe_checks(prompt(refs, 'A 画左。', ['A 抬头。'], 'A 不变'))
        self.assertEqual(errors, [])
        self.assertEqual(summary['characters'], [])
        self.assertEqual(summary['outfits'], ['图4'])

    def test_edit_binding_can_follow_the_source_video(self):
        refs = '视频1 = 待编辑原视频；图1 = 替换人物的外观，只参考面部与发型，衣着按@视频1 里原人物的衣服。'
        errors, _ = check('【素材绑定】' + refs + '\n编辑视频：把 @视频1 中的人物替换为图1。\n')
        self.assertEqual(errors, [])


    def test_calibration_boundaries_from_existing_prompts(self):
        """Shapes met in the user's 77 earlier Prompts (THE ORDER, reckless-rivals, offset) that are not E23."""
        cases = {
            'vehicle': '@01_Mason_car = Mason 的车：哑光黑轿跑三视图；车身外观唯一参考。 --车辆参考；',
            'place 外观': '图12 = 场内采访席，只参考棚架、采访桌椅、围栏及区域外观与材质；',
            'scene note naming 人物': '图5 = 球员休息区，只参考长凳与护网，不参考图中人物；人物位置按文字。',
            'styling image': '图1 = Isaiah 出场态造型参考（含面部与身形；湿发贴额、上身赤裸、白毛巾裹腰）；',
            '本条换上 in a bracket': '@Isaiah Marsh = Isaiah人物形象，只参考面部与发型，不参考服装与背景（本条换上干的白色T恤，按文字）。',
            'outfit named on its own line': ('图1 = Noah 人物形象，只参考面部与发型，不参考背景与姿势；图2 = Noah 礼服，只参考服装；'),
            'several assets on one line': ('@Noah = 男主 Noah 外观，只参考面部、发型；\n@Noah球服 = Noah 的全套队服，服饰唯一参考；\n'
                                           '@set01 @set02 = 影棚的布局与光线，不参考图中人物。 --场景参考；'),
            'numbered token': '@02_Noah = 男主 Noah 外观，只参考面部、发型；\n@Noah_outfit = Noah 本场便装：黑色连帽衫 --服饰参考；',
            'wears the outfit image in a bracket': ('@Noah = 新人 Noah 外观，只参考面部、发型（身穿常服@Noah outfit），不参考背景；\n'
                                                    '@Noah outfit = 新人 Noah 服饰唯一参考 -- 服饰参考；'),
        }
        for label, refs in cases.items():
            with self.subTest(label):
                self.assertEqual(check(prompt(refs, '有人。', ['有人。'], '有人'))[0], [])
        # the true positives that remain in that corpus: "不参考服装" and nothing else
        for refs in ('@Isaiah Marsh = Isaiah人物形象，只参考面部、发型与体态，不参考服装、姿势与背景（本条头发半干）。',
                     '@Priya-制片 = 女制片 Priya 外观，只参考面部、发型，不参考背景、姿势与服饰；'):
            with self.subTest(refs[:14]):
                self.assertTrue(check(prompt(refs, '有人。', ['有人。'], '有人'))[0])


class PerShotTests(unittest.TestCase):
    """W36: every checked character's first appearance in each unit carries its wardrobe."""

    def test_separate_outfit_image_restated_every_shot_is_clean(self):
        worn = 'Rhett（@Rhett 身穿@R_outfit ）'
        errors, warnings = check(prompt(OUTFIT_IMAGE, worn + '在画左。', [worn + '转身。', worn + '坐下。'],
                                        'Rhett 面部与发型依@Rhett ，衣着只穿@R_outfit '))
        self.assertEqual((errors, warnings), ([], []))

    def test_binding_only_is_not_enough(self):
        errors, warnings = check(prompt(OUTFIT_IMAGE, 'Rhett（@Rhett 身穿@R_outfit ）在画左。',
                                        ['Rhett（@Rhett 身穿@R_outfit ）转身。', 'Rhett演员@Rhett 坐下。'],
                                        'Rhett 衣着只穿@R_outfit '))
        self.assertEqual(errors, [])
        self.assertEqual(len(w36(warnings)), 1)
        self.assertTrue(w36(warnings, '镜头2'), warnings)

    def test_image_clothes_restated_and_conflict(self):
        worn = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        _, warnings = check(prompt(IMAGE_CLOTHES, worn + '在画右。', [worn + '抬头。'], worn + '全程不变'))
        self.assertEqual(warnings, [])
        refs = IMAGE_CLOTHES + '@T_outfit = 本条的服装参考：奶白 polo；\n'
        _, warnings = check(prompt(refs, worn + '在画右。', ['Theo（@Theo 身穿@T_outfit ）抬头。'], worn + '不变'))
        self.assertTrue(any('镜头1' in w and '来源只留一个' in w for w in warnings), warnings)

    def test_text_only_wardrobe_and_change_of_clothes(self):
        robe = 'Rhett（@Rhett ，深灰浴袍套在白浴巾外）'
        clean = prompt(TEXT_ONLY, TOWEL + '在画左。', [TOWEL + '接过浴袍。', robe + '系带子。'],
                       'Rhett 衣着按每一镜的文字：镜1 赤裸上身围白浴巾，镜2 起浴袍套在外面')
        self.assertEqual(check(clean), ([], []))
        # the robe shot forgets to restate: the change of clothes is exactly where it drifts
        drift = prompt(TEXT_ONLY, TOWEL + '在画左。', [TOWEL + '接过浴袍。', 'Rhett演员@Rhett 系带子。'],
                       'Rhett 衣着按每一镜的文字')
        self.assertTrue(w36(check(drift)[1], '镜头2'))

    def test_several_characters_in_one_frame_are_judged_separately(self):
        refs = TEXT_ONLY + IMAGE_CLOTHES
        theo = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        _, warnings = check(prompt(refs, TOWEL + '画左、' + theo + '画右。',
                                   ['Rhett演员@Rhett 画左、' + theo + '画右。',   # Theo's sweater is not Rhett's
                                    TOWEL + '画左、Theo演员@Theo 画右。'],       # Rhett's towel is not Theo's
                                   TOWEL + '；' + theo))
        self.assertTrue(any('@Rhett' in w and '@Theo' not in w for w in w36(warnings, '镜头1')), warnings)
        self.assertTrue(any('@Theo' in w and '@Rhett' not in w for w in w36(warnings, '镜头2')), warnings)

    def test_monitor_and_picture_in_picture_count(self):
        refs = TEXT_ONLY + IMAGE_CLOTHES
        theo = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        bare = '监视器屏幕里是Rhett演员@Rhett 与Theo演员@Theo 四目相对的画面。'
        _, warnings = check(prompt(refs, TOWEL + '、' + theo + '。', [bare], TOWEL + '；' + theo))
        self.assertTrue(any('@Rhett' in w and '@Theo' in w for w in w36(warnings, '镜头1')), warnings)
        dressed = f'监视器屏幕里是{TOWEL}与{theo}四目相对的画面。'
        self.assertEqual(check(prompt(refs, TOWEL + '、' + theo + '。', [dressed], TOWEL + '；' + theo))[1], [])

    def test_extras_may_be_collective_but_characters_may_not(self):
        refs = ('@Beckett = Beckett人物形象，只参考面部与发型，衣着一律按@team ；\n@Isa = Isa人物形象，只参考面部与发型，'
                '衣着一律按@team ；\n@team = 本条 Beckett、Isa 与队友身上唯一的服装：Sharks 队服 -- 服装参考；\n')
        b, i = 'Beckett（@Beckett 身穿@team ）', 'Isa（@Isa 身穿@team ）'
        extras = f'全队十几人穿@team 的队服慢跑；{b}领跑，{i}在他身后。'
        self.assertEqual(check(prompt(refs, extras, [f'机位在两人身后；{b}在画右、{i}在画左。'], f'{b}；{i}'))[1], [])
        # "两人 / 两位" standing in for a character never named in the shot
        _, warnings = check(prompt(refs, extras, [f'{b}回头；两人并肩跑过。'], f'{b}；{i}'))
        self.assertTrue(any('集体指代' in w and '@Isa' in w for w in w36(warnings, '镜头1')), warnings)

    def test_offscreen_speaker_gaze_target_and_annotation_are_not_appearances(self):
        refs = TEXT_ONLY + IMAGE_CLOTHES
        theo = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        shot = (f'【Theo 近景，固定】{theo}笑出来，眼睛看向画左的Rhett。'
                '台词（Rhett演员@Rhett ，画外，1-2s，English）："Hi."')
        _, warnings = check(prompt(refs, TOWEL + '、' + theo + '。', [shot], TOWEL + '；' + theo))
        self.assertEqual(warnings, [])
        on_screen = f'{theo}笑出来。台词（Rhett演员@Rhett ，1-2s，English）："Hi."'
        _, warnings = check(prompt(refs, TOWEL + '、' + theo + '。', [on_screen], TOWEL + '；' + theo))
        self.assertTrue(any('只在台词标签里出现' in w for w in w36(warnings, '镜头1')), warnings)

    def test_quotes_acting_labels_and_name_with_its_reference_offscreen(self):
        refs = TEXT_ONLY + IMAGE_CLOTHES
        theo = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        shot = (f'〔Rhett·逗他〕{theo}举起写着"RHETT"的牌子。台词（Theo演员@Theo ，1-2s，English）："Rhett, look."'
                '；Rhett演员@Rhett 画外闭着嘴。')
        self.assertEqual(check(prompt(refs, TOWEL + '、' + theo + '。', [shot], TOWEL + '；' + theo))[1], [])

    def test_global_rules_need_every_character(self):
        refs = TEXT_ONLY + IMAGE_CLOTHES
        theo = 'Theo（@Theo 身穿图中的黑色粗针织毛衣）'
        _, warnings = check(prompt(refs, TOWEL + '、' + theo + '。', [TOWEL + '、' + theo], theo + '全程不变'))
        self.assertTrue(any('@Rhett（没有逐人写）' in w for w in w36(warnings, '贯穿要求')), warnings)

    def test_text_to_video_characters_come_from_their_locks(self):
        lock = '阿伟：三十岁左右男性，短发，浅蓝色衬衫，工牌；小雨：二十七岁左右女性，白色衬衫'
        errors, warnings = check(prompt('无参考素材。', '阿伟（浅蓝色衬衫）在画左。', ['阿伟低头。'], lock))
        self.assertEqual(errors, [])   # no image, no E23
        self.assertTrue(w36(warnings, '镜头1'), warnings)
        self.assertEqual(check(prompt('无参考素材。', '阿伟（浅蓝色衬衫）在画左。', ['阿伟（浅蓝色衬衫）低头。'], lock)), ([], []))
        # lock labels such as 节奏 / 声音 are not characters
        _, _, infos, summary = wardrobe_checks(prompt('无参考素材。', '空房间。', ['空房间。'], '节奏：每句即开口；声音：只有雨声'))
        self.assertEqual(summary['characters'], [])
        self.assertTrue(any('脚本不查' in i for i in infos))

    def test_english_prompt(self):
        refs = ('Image1 = Rhett\'s appearance: face and hair only; Rhett\'s wardrobe in this clip is Image2. '
                'Image2 = Rhett\'s outfit: grey bathrobe (wardrobe reference).')
        def en(shot):
            return (f'REFERENCES: {refs}\nOVERVIEW: 4-second 16:9 scene.\nOPENING STATE: Rhett (Image1, wearing Image2) '
                    f'stands frame-left.\nTIMELINE:\nShot 1 (0-4s): [medium, fixed] {shot}\n'
                    'GLOBAL RULES: Rhett keeps the face of Image1 and wears only Image2; no music; no subtitles.\n')
        self.assertEqual(check(en('Rhett (Image1, wearing Image2) turns.')), ([], []))
        self.assertTrue(w36(check(en('Rhett turns and sits.'))[1], '镜头1'))
        errors, _ = check(en('x').replace(refs, 'Image1 = Rhett appearance (face and hair only; ignore the white polo).'))
        self.assertTrue(errors and errors[0].startswith('E23 Image1'), errors)


class IncidentRegressionTests(unittest.TestCase):
    def test_v4_failing_prompt_now_errors_and_warns_per_shot(self):
        result = validate(FIX / 'set-scene-v4.prompt.md')
        e23 = [e for e in result['errors'] if e.startswith('E23')]
        # Rhett: only "不参考…图中白色 polo", no source anywhere. Theo's source is named on the outfit line
        # ("@01_Theo_outfit = Theo 演员的戏服唯一参考"), so his failure is per shot (W36), not E23.
        self.assertEqual([e.split()[1] for e in e23], ['@Rhett'])
        self.assertIn('只写了不参考图中衣服', e23[0])
        units = {w.split()[1] for w in result['warnings'] if w.startswith('W36')}
        for unit in ('镜头1', '镜头2', '镜头4', '镜头5', '镜头6', '镜头8'):
            self.assertIn(unit, units)
        self.assertTrue(any('镜头1' in w and '@Rhett' in w and '@Theo' in w for w in result['warnings']))  # monitor
        self.assertTrue(any('镜头8' in w and '集体指代' in w and '@Rhett' in w for w in result['warnings']))
        self.assertEqual(result['checks']['format'], 'failed')

    def test_v5_fix_passes_the_binding_and_every_shot(self):
        result = validate(FIX / 'set-scene-v5.prompt.md')
        self.assertFalse([e for e in result['errors'] if e.startswith('E23')], result['errors'])
        w = [x for x in result['warnings'] if x.startswith('W36')]
        # the one remaining hint is real: 【起始状态】 introduces the director without her wardrobe
        self.assertEqual(len(w), 1, w)
        self.assertTrue(w[0].startswith('W36 起始状态') and '@01_Directer' in w[0])
        self.assertEqual(result['wardrobe']['characters'], ['@Rhett', '@Theo', '@01_Directer'])
        self.assertEqual(result['wardrobe']['outfits'], ['@01_Theo_outfit'])

    def test_performance_and_raw_artifacts_are_out_of_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.prompt.md'
            path.write_text('【表演条件】4秒；近景。\n【表演时间线】\n节拍 b1（0-4s）：她抬眼。\n', encoding='utf-8')
            result = validate(path, artifact='performance')
            self.assertFalse(any(x.startswith(('E23', 'W36')) for x in result['errors'] + result['warnings']))


class WiringTests(unittest.TestCase):
    """The wardrobe rule is added on top; earlier rules and review rows are all still there."""

    def read(self, name):
        return (ROOT / name).read_text(encoding='utf-8')

    def test_rule_is_wired_through_every_stage(self):
        skill = self.read('SKILL.md')
        self.assertIn('21. **衣着逐镜逐人，来源唯一，写法正向。**', skill)
        self.assertIn('E23', skill)
        self.assertIn('W36', skill)
        tpl = self.read('templates/prompt-templates.md')
        self.assertNotIn('只参考面部、发型与服装，不参考背景与姿势', tpl)   # the old default that let clothes follow the image
        self.assertIn('衣着一律按', tpl)
        self.assertIn("wardrobe in this clip", tpl)
        s5 = self.read('references/stage-5-directing-storyboard.md')
        self.assertIn('衣着状态逐镜', s5)
        self.assertIn('群演可以集体写', s5)
        s5b = self.read('references/stage-5b-reference-assets.md')
        self.assertIn('## 5b.3a 形象图与服装图的分工', s5b)
        s6 = self.read('references/stage-6-prompt-compiler.md')
        self.assertIn('每镜每个角色第一次出现', s6)
        self.assertNotIn('`图1 = 角色A外观（只参考面部、发型与服装；不参考背景与姿势）`', s6)
        s7 = self.read('references/stage-7-qa-continuity.md')
        self.assertIn('| 衣着 |', s7)
        self.assertIn('衣服跟了形象图', s7)
        self.assertIn('| A 衣着 |', s7)
        card = self.read('templates/shot-card.md')
        self.assertIn('衣着来源', card)
        self.assertIn('- 衣着（', card)
        self.assertIn('服装图', self.read('templates/asset-registry.md'))
        self.assertIn('服装图', self.read('templates/reference-asset-brief.md'))
        caps = self.read('references/seedance-2.5-capabilities.md')
        self.assertIn('形象图里的衣服会被带进成片', caps)
        log = self.read('references/validation-log.md')
        self.assertIn('2026-09-24', log)
        self.assertIn('set-scene v4', log)

    def test_earlier_rules_and_review_rows_are_kept(self):
        skill = self.read('SKILL.md')
        for clause in ('19. **镜与镜之间必须有变化（变化轨', '20. **每条 clip 至少交付一次变化。**',
                       '9. **每个 clip 的 Prompt 自足。** 外观锁、空间、光源、声音在每个 clip 重写。',
                       'W30–W33 是变化轨的下限审阅', 'W22–W29 是时间利用的下限审阅', '与场面轨的差异'):
            self.assertIn(clause, skill)
        s7 = self.read('references/stage-7-qa-continuity.md')
        for row in ('| 交付变化 |', '| 导演语法 |', '| 运镜库 |', '| 摄影机身份与支撑 |', '| 外观锁 |', '| 起止状态 |',
                    '| 表演与时间 |', '| 人物换脸 / 换衣 |', '画面始终没有变化的感觉', '"这 N 秒存在的意义是？"'):
            self.assertIn(row, s7)
        s5 = self.read('references/stage-5-directing-storyboard.md')
        for clause in ('## 5.1f 变化轨', '6. **每条 clip 至少交付一次变化**', '- 角色外观锁（S1 提炼的一行）',
                       '- 服装、发型、道具颜色'):
            self.assertIn(clause, s5)
        tpl = self.read('templates/prompt-templates.md')
        for clause in ('`峰值镜 | N`', '【变化：景别 全→近｜机位 固定→推｜光 正→侧｜幅度 1→3】', '`运镜来源`'):
            self.assertIn(clause, tpl)
        validator = self.read('scripts/validate_prompt.py')
        for name in ('variation_checks(shots, metadata_text)', 'camera_checks(shots, metadata_text)',
                     'rhythm_checks(shots, dialogue'):
            self.assertIn(name, validator)


if __name__ == '__main__':
    unittest.main()
