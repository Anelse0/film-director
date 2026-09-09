# Changelog

## 1.4.0 — 2026-09-09

参考素材绑定格式修正（面向 director 输出 Prompt 的两个实测问题：给人看的注释漏进 D 层、人物形象与服饰揉在一条）。依据官方 `seedance-2.5-capabilities.md` §4.1（素材指代=编号＋用途）、§4.2（每个素材一个职责、分工具体到"参考什么"），非自创格式。

- **【素材绑定】人物形象与服饰硬拆两条**：`图N = {角色} 人物形象，只参考面部、发型、体型，不参考服装/背景/姿势` ＋ `图M = {角色} {本场}服装造型，只参考服装与配饰，不参考面部/背景`；换装态各一条服饰参考。改 `stage-6-prompt-compiler.md` §6.2、`prompt-templates.md`（T2/T3/T4/T5＋英文 REFERENCES）、`stage-5b-reference-assets.md`（角色主体图拆成人物形象图/服饰图）、`reference-asset-brief.md`、`asset-registry.md` 示例行；硬规则 3 从"不为凑模板拆图"改为"形象与服饰分别供图、分别绑定，每个参考一个职责"；生产档案"每人每场一张造型图"改为"形象图＋服饰图"。图数上升：主体图数=角色数×2，官方 §3 >8 需抽卡，S7 登记。
- **【素材绑定】段禁止 E 层注释**：约定/数量小计/草稿/待回填/S5b/"用户提供"等规划与来源说明是 E 层，进文末 E 参数表或 `07_qa/`，不进 D 层 Prompt（五层分离）。新增校验 **W24**（production：扫【素材绑定】段的这类词，WARN 级）。§6.6 自检加两项。
- 受保护区同一提交重算 6 个文件哈希（stage-6、stage-5b、prompt-templates、reference-asset-brief、asset-registry、validate_prompt）。示例 Prompt（examples/01–04）保留 1.4.0 前合并式绑定，用作台词/情绪/参数示例，已在 §6.2 注明。
- 测试：`tests/test_binding.py`（5）＋ run_tests W24 断言；99 unittest ＋ shell 回归 ＋ CI 预检通过。

## 1.3.2 — 2026-09-08

容错修复（对两个 skill 的脚本、测试与文档做一次审查后发现的问题；无新功能、无新警告码）。

- `scripts/xlsx_lite.py`：`<row>` / `<c>` 缺 `r` 属性（OOXML 允许，部分生成器省略）时按隐式位置读，不再 `TypeError`；非 zip 或缺 `xl/workbook.xml` 的文件（如 Excel 打开主表时留下的 `~$…xlsx` 锁文件）抛 `ValueError` 并带文件名，不再是 `BadZipFile` 追溯。
- `scripts/ledger_view.py`：只有表头含 入点 / 出点 / 起 / 止 / 时间 / time / start / end 的列才把 0–1 之间的小数当 Excel 时间显示；其他列的小数（词/秒等）原样输出（此前 0.5 会显示成 `720:00`）。
- `scripts/ledger_check.py`：L03 与 validate_prompt W22 同口径——≥ `--long`（7s）且只有一句、或 ≥ `--long-dialogue`（9s，新参数）含对白才提示；两句以上的 7–8s 镜不再误报；台词格里数不出引号时仍按一句处理（保守）。
- `scripts/validate_prompt.py`（受保护文件，同一提交重算哈希）：W22 不再把带 重读 / 轻读 / 之后 / 停住 / 一词 / word 标注的引号当台词计数（与 W21 同一豁免）；W04 的"30s 内 > 8 镜"提示只在平均镜长 < 2s 时给出——此前它与 1.3.0 的"对白场一句一切、对白镜 2–4s"约定互相矛盾（30s 对白场按约定切出 9–12 镜必触发 W04，反过来引导把台词塞回长镜）；文档字符串改为 film-director。`references/dialogue-pacing.md` §6 同步口径。
- `tests/run_tests.sh`：W14/W18 断言此前误用账本夹具的输出变量（恒真），改回对 example-04 输出断言；账本夹具加"8s 两句不报 L03"。
- 新增 `tests/test_shared_files.py`：与 film-creative 同目录安装时，`handoff-contract.md` / `xlsx_lite.py` / `ledger_view.py` 三个同文文件逐字节一致（此前只有 film-creative 侧检查契约一份）。
- 测试：`test_ledger.py` +3、`test_pacing.py` +2、`test_shared_files.py` +1；shell 回归与 CI 预检通过。

## 1.3.1 — 2026-09-08

- `references/dialogue-pacing.md` §4b：台词设计表 → Prompt 的逐列映射（说法 → 〔说法〕；目的动词 + 递进 → 〔情绪〕；全场阶梯 → 【整体情绪弧线】；听者反应 → 句末嘴部状态与反应镜；目的动词 → S4 手 / 视线 / 距离；收尾标记 → 末镜停留或硬切）。台词逐字不动，只新增外化信息。
- `scripts/ledger_view.py` + `tests/test_ledger_view.py`（stdlib，与 film-creative 同文）。
- `tests/test_pacing.py`、`tests/test_ledger.py` 夹具人名改为 A / B。
- 受保护文件字节不变；89 个 unittest 与 shell 回归 + CI 预检通过。

## 1.3.0 — 2026-09-08

面向实际协作返工的版本：把两天生产里反复出现的四类返工（一段发言装进长镜、连续同机位、修订只给 diff、正典改了旧分镜还在表里）和一个断掉的接口（创作侧 1.2.0 起不再逐句给说法，生产侧 W20 却需要〔说法〕）收进规则与工具。

- **协作契约** `references/handoff-contract.md`（film-creative 仓库同文）：交接物表（场景页 / 账本行 · 台词设计表 · ip.md 含正典变更表 · 生产档案 · 台词预算回传 · 缺口请求）；账本模式的列所有权；正典变更五步协议；时长与台词预算口径；交付默认（修订给全文；〔说法〕〔情绪〕取自设计表）。
- **对白场节奏与亮相** `references/dialogue-pacing.md`：一句一切（对白镜 2–4s；≥7s 单句 / ≥9s 对白须写理由）、逐镜变化、台词预算先于分镜、hero beat 四节拍模板（介绍 → 他人反应赋予地位 → 特写作揭示 → 落定）、按场合区分人设与造型、修订全文交付。
- **校验** `scripts/validate_prompt.py`：新增 **W22**（production、≥2 镜的 clip：含台词单镜 ≥7s 且只有一句，或 ≥9s；旁白 / 画外音镜免检）与 **W23**（连续 3 镜【景别 / 角度 / 运镜】标注归一化后完全相同）。两者为 WARN 级本地约定 `[推论]`，不判质量；`checks.performance` 仍恒为 `needs_review`。对既有示例与生产 Prompt 逐一校准：接受过的一镜到底、6s 对白镜与变化的中近景序列均不触发。
- **生产档案** `references/production-profile.md` + `templates/production-profile.md`：把同一项目被反复重申的常量（画幅、Prompt / 台词语言、每人每场一张造型图、调色段、声音与旁白、一句一切、字幕、首帧、台词预算）固定为 S1 先读的文件。
- **账本模式与工具**：`scripts/xlsx_lite.py`（stdlib 读写 .xlsx）与 `scripts/ledger_check.py`（L01/L02/L06 为错误：入出点倒置、相邻镜不连续、台词窗口越界；L03/L04/L05/L08 为提示：长镜含对白、超长镜、三镜同景别运镜、语速 >3 词/s；L07 占位统计；旁白镜不计 L03）。
- `SKILL.md`：输入与交接加台词设计表；新增「项目常量与账本」节；S1 / S5 读取项加档案与节奏文件；硬规则 15；输出契约要求修订给全文并回显档案行；快速路由加宣布 / 亮相、账本检查、台词超长、节奏太慢四个入口。
- 示例与测试：`examples/bad-example-3-lazy-long-take.prompt.md`（触发 W22 + W23，0 error）；`tests/test_pacing.py`（7）与 `tests/test_ledger.py`（7）；`run_tests.sh` 加 bad-3 断言、"接受过的一镜到底与 6s 镜不触发"断言、账本夹具检查。
- 协议：按 `test_protected_zone.py` 约定，同一提交内重算 `scripts/validate_prompt.py` 基线哈希；其余受保护文件字节不变。stage-5 等受保护文档本次不改，新增指引放在非保护文件中。

## 1.2.0 — 2026-09-08

新增可复用导演法则**「引荐与亮相的顺序（介绍先行，特写作揭示）」**，把一次实战修正（E-1 宣布余波·上，Cole/Beckett 引荐从"先看脸再报名"翻转为"名字先行、特写作揭示落在头衔落点"）提炼为通用规则，防止人物引荐/亮相节拍反复出现反向节奏。

- `references/stage-5-directing-storyboard.md`：§5.1d 揭示模式下新增一段规则——引荐/亮相先给介绍（名字/画外报名/前情/头衔），特写作为揭示落在信息落点，reveal 引爆在名字或头衔那一刻；禁止"先看脸再报名"的反向节奏；受镜数/时长所限时可在同一特写内用揭示手法（前景遮挡＋焦点交接）把脸压到信息落点之后再露。§5.9 常见问题表新增一行"人物引荐先看脸才报名（反向节奏）"并回指 5.1d。
- 纯导演指引补充，**不改校验/代码**，无新警告码；`checks.performance` 仍恒为 `needs_review`。
- 按 `test_protected_zone.py` 约定，同一提交内重算受保护文件 `stage-5-directing-storyboard.md` 的基线哈希并更新其文档说明。

## 1.1.1 — 2026-09-08

标注澄清（无行为变化）：情绪三件套（【整体情绪弧线】/〔情绪〕/〔说法〕）**不是官方 Seedance Prompt 结构**——官方结构见 `seedance-2.5-capabilities.md` §4.1（素材指代 / 概述 / 情节 / 结尾，无情绪弧线字段）。它是本 skill 的 `[推论]`（本地写作约定），把 S4 表演层的情绪弧线上抬进编译后 Prompt，用于防"漏情绪"缺陷。

- `stage-6-prompt-compiler.md` §6.0、`prompt-templates.md` 头部、`SKILL.md` 输出契约：把"必备"改写为"本 skill 约定的必备产出 `[推论]`，非官方结构"，并说明 **W20 为 WARN 级本地审阅提示、只提示不拦**（呼应硬规则 1：写能力/结构须带事实标签，不冒充官方）。
- 按 `test_protected_zone.py` 约定，同一提交内重算 stage-6 与 prompt-templates 两个受保护文件的基线哈希。
- 校验逻辑、W20 行为与全部测试不变。

## 1.1.0 — 2026-09-08

情绪层从"隐含在表演正文里、时有时无"升级为 production **必备结构**，防止编译出的生产 Prompt 反复缺【整体情绪弧线】与逐镜/逐句情绪（须用户手动指出才补）。

**根因（多因）**：①模板 `prompt-templates.md`、编译顺序 `stage-6-prompt-compiler.md §6.1/6.2`、分镜卡 `shot-card.md` 都没有情绪弧线/逐镜情绪/逐句说法的槽位，编译作确定性翻译时天然不产出；②`validate_prompt.py` 不检查情绪层，缺了也不报，长期漏而不自知；③反机械化基调（"不把细节总结为情绪名"、硬规则 7"删空泛替代"）被过度执行成"干脆不写情绪标签"，只剩零星标签。

**改动（情绪三件套 = ①【整体情绪弧线】块 ②每镜段首〔情绪〕 ③每句台词〔说法〕，均为定位标签、与可见证据正文并存、绝不替代或省略表演正文——与硬规则 7 一致）**：
- `scripts/validate_prompt.py`：新增 **W20**（production 专用，WARN）——缺【整体情绪弧线】/EMOTION ARC 块，或有镜头段首未标〔情绪〕时提示。只查结构在场，不判情绪质量（`checks.performance` 仍恒为 `needs_review`）。
- `references/stage-6-prompt-compiler.md`：§6.0 增"情绪层是必备结构"与标签 vs 证据的边界；§6.1 编译顺序加【整体情绪弧线】；§6.2 逐镜格式加〔本镜情绪〕与台词〔说法〕并补规则；§6.6 自检加检查项。
- `templates/prompt-templates.md`：头部加情绪三件套契约；T1/T2/英文骨架加【整体情绪弧线】块、〔情绪〕与〔说法〕槽位。
- `templates/shot-card.md`：C 层加"本镜情绪〔情绪〕"与台词〔说法〕字段，新增"clip 整体情绪弧线"字段。
- `SKILL.md`：默认输出契约声明 production 必含情绪三件套。
- 示例：`example-01/02/03`、`example-04-parameters-fight`、`examples/performance/06-production-rage-hurt` 与 `examples/production/30s-fight-t2v` 全部补全情绪三件套并保持原有警告面（01/02/03/06 为 0 警告；04 与 30s-fight 保留既有 2×W05）。CI 的 `--require-ready` 预检直接跑 30s-fight 生产包，故同步在 `30s-fight-t2v.production.json` 重算 `prompt_sha256` 及 `example-04-parameters-fight.prompt.md` 的 upstream 哈希，使预检仍 `passed`（W20 已消除，仅余两条已登记的 W05）。
- 测试：`test_production.py` 加 `EmotionLayerTests`（W20 触发/清除、中英文、performance 不触发、W20 是 WARN 非 ERROR）；`run_tests.sh` 的 bad-1 断言加 W20；`prompt()` 夹具与 RealMedia 夹具补情绪层以通过 preflight。
- 协议：按 `test_protected_zone.py` 约定，同一提交内重算并更新四个受保护文件（validate_prompt.py、stage-6、prompt-templates、shot-card）的基线哈希。

## 1.0.0 — 2026-09-07

独立的 Seedance 2.5 生产后端 Skill，内容取自 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) **v2.3.1**（用户指定以 2.3.1 为生产基线；创意前端由 film-creative Skill 承担，其基线为 2.6.0-alpha.3）。

- 范围：S1 资源读取、S2 任务识别、S4 表演外化（含情绪表演库）、S5 导演与分镜、S5b 参考资产、S6 Prompt 编译、S7 检查；表演优先路由（performance / production / raw）完整保留；生产契约与 30 秒设计沿用 2.3.1。
- 移除创意侧文件：stage-3a/3b/3c、concept-generation、screenwriting-traditions、validate_concept、story 模板、概念示例与概念测试。
- 新增「输入与交接」契约：接受任何来源的剧本场景文本；剧本层缺口只登记不代写；已确认台词与场景为锁定输入。
- 共用文件（stage-1-intake、scene-parameters、causal-chain、anti-mechanical、genre-packs、stage-4、stage-5、director-lenses、script-scene 模板）中指向创意侧文件或概念模式的引用改为交接说明；其余生产核心文件与 v2.3.1 逐字节一致。
- `tests/test_protected_zone.py` 以 1.0.0 为基线哈希锁定生产/表演核心；对照 v2.3.1 的差异可在源仓库 tags 中核查。
- 历史版本记录（1.2.0–2.3.1 及其后的 2.4.0–2.6.0 开发线）见源仓库 Film-Seedance-Director 的 CHANGELOG 与 tags。
