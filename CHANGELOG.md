# Changelog

## 2.0.0 — 2026-09-11

把 25 条情绪原文从"可调用的资源"升级为"可组合的表演语法"，把导演手法从二手归纳换成一手来源的决策规则，并逐页复读官方 2.5 指南补齐写法依据。全部改动是判断工具与依据，不新增警告码；1.3.1–1.5.1 被回退的内容（绑定拆条、W24、W25、账本视图）不恢复。

**根因**：①原文库只支持 raw / adapt / blend 三种调用，没有回答"同一情绪更强怎么写、从 A 到 B 怎么过渡、表面一层心里一层怎么写、听者怎么演、这个景别读不读得出"——于是组合表演靠每次临场发挥，示例 02–05 里做对的方法没有沉淀；②`director-lenses.md` 的来源多为 nofilmschool / studiobinder 等二手拆解，`source-analysis.md` 已自认"不是逐条第一手核实"；③W04 的"30s 内 >8 镜"与官方案例（9 镜 / 30s）直接冲突。

- **`references/performance-grammar.md`（新，受保护）**：§1 官方依据（描述性语句 / 只在有记忆点处写细节 / 案例的情绪词 + 证据并写与渐变链）；§2 压缩留 hinge（Ekman reliable facial expressions、Duchenne 眼轮匝肌 `[一手·摘要]`）；§3 可读性地板（Hitchcock 影像尺寸随情绪重要性、Bergman、Villeneuve；反例 Sonnenfeld）；§4 时间包络与相对时间（Ekman 微 / 宏表情时长；官方相对时间控制）；§5 家族阶梯与失控铰链；§6 过渡铰链三检查；§7 面具与泄漏（Ekman leakage；Caine 不眨眼）；§8 听者与切点（Kuleshov / Pudovkin、Hitchcock 1964、Jenkins、Murch 六律与眨眼切点）；§9–12 多人、语言、检索、误用信号。
- **`references/emotion-index.json`（受保护，重算哈希）**：25 条各加 `zh`（译写，标 adapt）、`hinge`、`readability`、`wider_parts`、`onset`、`min_seconds`（`[推论]`）、`ladder`、`listener`、`mask`、`neighbors`（共 89 条，每条带桥梁部位）；条目 17 末句歧义记在 `notes`。原有 terms / cues / relations 不变；`assets/emotion-library.json` 字节不变，raw 保真检查不变。
- **`scripts/emotion_library.py`（受保护，重算哈希）**：新增 `--zh`、`--neighbors ID`、`--ladder FAMILY`、`--readability 景别`、`--listener`；`--query` 只搜条目与其自身索引注记，不搜 neighbors / ladder（否则"害羞"会命中半个库）；`--raw`、`--id`、`--list` 行为不变。
- **`references/director-craft.md`（新，受保护）**：按决策组织 A–M 十三节，每节 = 一手说法 `[一手·摘要]` + 决策 + Seedance 写法 `[推论]` + 误用；末表对应 L1–L18。来源：Hitchcock / Truffaut 与 1964 CBC 访谈、Pudovkin 记述的 Kuleshov 实验、Lumet《Making Movies》、Murch《In the Blink of an Eye》、Ekman、Caine BBC 表演课、Weston《Directing Actors》、Bergman、Deakins、ASC Shot Craft、Fincher / Messerschmidt、Kubrick / Ciment、Cuarón / Lubezki（ASC）、Villeneuve（DGA）、Haneke、Nolan（DGA Quarterly）、Lanthimos（BFI / ASC）、Coen（ASC）、Tarkovsky、DGA Shot to Remember（Jenkins / Sonnenfeld / Payne / Spielberg）。按用户约定只用搜索不抓全文，故一律标"仅读摘要"，不做推演式归因；Edgar Wright 的视频论文（第三方）与 Spielberg 纵深调度（摘要无具体说法）未采纳。
- **`references/director-lenses.md`（受保护，重算哈希）**："从已核实资料到本地决策"改为指向 `director-craft.md`，保留 Lumet / ASC / Gerwig 三条已核实链接。
- **`references/seedance-2.5-capabilities.md`（受保护，重算哈希）**：§2 补编辑时长差异说明与时间戳编辑 / 音频编辑；新增 §4.9 官方案例揭示的写法（切镜密度、情绪词与证据并写、渐变链、段首标注、分段参考绑定、参考只做指代、【严格排除】段、一键成片与转场、音频编辑、总体介绍、官方 sd25-pe skill、2.0 附录缺口）；复核日期 2026-09-11。
- **`references/stage-4-performance.md`（受保护，重算哈希）**：4.4 听与回应加"先写他看见了什么"；新增 4.4b 组合语法七条；4.5 表加相对时间行 `[官方]`。
- **`references/stage-5-directing-storyboard.md`（受保护，重算哈希）**：§5.1c 加 Murch 权重顺序与眨眼切点、Tarkovsky 时间压力；§5.2 景别一步改为"影像尺寸随情绪重要性 + 可读性地板"；§5.4 运动三种合法动机；§5.9 加两行（反应镜空、景别与地板不符）；§5.10 加白模参考与表情参考锁调度 `[官方]`；新增 §5.11 镜头曲线（Lumet）与平行动作（Nolan）。
- **`references/stage-5b-reference-assets.md`（受保护，重算哈希）**：资产表加"表情 / 表演参考视频（运动参考）"与"白模视频（粗粒度）" `[官方]`。
- **`references/stage-6-prompt-compiler.md`（受保护，重算哈希）**：§6.0 压缩回 S4 留 hinge；§6.2 加相对时间与时间点、部署密度、分段绑定参考三条规则。
- **`templates/shot-card.md`（受保护，重算哈希）**：头部加镜头曲线字段；C 层表演块行记 hinge 与可读性地板。
- **`scripts/validate_prompt.py`（受保护，重算哈希）**：W04 镜数条件由"30s 内 >8 镜"改为"≥3 镜且平均镜长 < 2s"，提示文案引用官方案例；单镜 < 1.5s 不变；文档字符串更新。`references/dialogue-pacing.md` §6 与 `validation-log.md` 待验证队列（+5 项）同步。
- **`references/source-analysis.md`**：新增 §2.0.0 调研表（20 行来源、采纳要点、去处、未采纳说明）。
- `SKILL.md`：表演优先路由加组合语法与新检索项；流水线表 S4 / S5 读取项；硬规则 4（相对时间）、7（压缩留 hinge、部署密度）、8（景别服从情绪重要性、运动动机）；快速路由加七个入口。README 同步。
- 示例：`examples/performance/07-mask-and-leak.prompt.md` + `.performance.json`（blend 25 / 19 / 6，`--record` 保真 matched）、`examples/performance/08-listener-reaction-chain.prompt.md`（production，B 走 9 → 14 → 25，切点落在眨眼 / 凝视 / 闭嘴之后，0 error 0 warning）；`examples/performance/acceptance.md` 补两组说明。
- 测试：新增 `tests/test_grammar.py`（索引字段完整性与取值域、neighbors 有效且不自指、译写无来源元数据、`--query` 范围、四个新检索函数与 CLI、示例 07 / 08 断言）；`test_pacing.py` 加 W04 重校（9 镜 / 30s 不提示、平均 < 2s 提示）；`run_tests.sh` 加 07 / 08 断言；`test_protected_zone.py` 重算 12 个受保护文件哈希并新增 2 个受保护文件。
- 未做与边界：`min_seconds`、`readability`、hinge 部位对应均为本 skill 估算 `[推论]`，成片验证后按 `validation-log.md` 修订；未读取官方 `sd25-pe` skill 内容；2.0 指南附录的 R2V 基础案例未收录。远端 tags v1.3.1–v1.5.1 保留（2.0.0 > 1.5.1，无冲突，未删除）。

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
