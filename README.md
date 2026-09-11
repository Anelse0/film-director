# film-director

版本 **2.0.0**。Seedance 2.5 视频 Prompt 生产 Skill：表演外化与情绪提示词、导演与分镜、参考资产计划、Prompt 编译、连续性与质量检查。调用：`/film-director` 或在对话中描述任务（拆分镜、转 Prompt、表演测试、改成片）。

创意前端（概念、故事、剧本、台词创作与改写）由独立的 [film-creative](https://github.com/Anelse0/film-creative) Skill 承担。本 Skill 内容取自 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) **v2.3.1** 的生产后端（用户指定以 2.3.1 为生产基线）。

## 2.0.0 更新（表演语法 · 一手导演手法 · 官方指南复读）

- **表演语法** `references/performance-grammar.md`：把 25 条情绪原文从"单一情绪、单张脸"扩展成人物表演的组合方法——压缩留 hinge（Ekman 可靠信号）、可读性地板（景别决定哪个部位可读）、家族阶梯（19→6、18→3、17→4、25/21→1，铰链是先失控的部位）、跨情绪过渡铰链、面具与泄漏（双层表演）、听者与切点（Kuleshov / Murch）、相对时间、部署密度。全部是判断工具，不是配额或警告。
- **情绪索引增强** `references/emotion-index.json`：每条新增 `zh` 译写、`hinge`、`readability`、`wider_parts`、`onset`、`min_seconds`、`ladder`、`listener`、`mask`、`neighbors`（89 条带桥梁部位的衔接关系）。`scripts/emotion_library.py` 新增 `--zh` `--neighbors` `--ladder` `--readability` `--listener`；`--raw` 与原文保真检查不变。
- **导演手法一手提炼** `references/director-craft.md`：Hitchcock（影像尺寸随情绪重要性）、Kuleshov / Pudovkin、Murch（六律、切在眨眼）、Fincher / Kubrick / Lubezki（运动动机）、Lumet（镜头曲线）、Deakins、ASC Shot Craft（视线与机位高度）、Haneke、Tarkovsky、Weston / Caine（表演）、Jenkins / Sonnenfeld / Payne / Spielberg（DGA Shot to Remember）、Lanthimos / Coen、Nolan。按决策组织，每条带 `[一手·摘要]` 标签（一手来源，本次仅读到摘要）与 Seedance 写法；`director-lenses.md` 的 L1–L18 指向它。
- **官方指南复读**：`seedance-2.5-capabilities.md` 新增 §4.9 官方案例揭示的写法（9 镜 / 30s 每镜一句台词、情绪词与证据并写、渐变链、分段参考绑定、【严格排除】段、白模与表情参考）；S5 §5.10 加白模 / 表情参考锁调度，§5.11 镜头曲线与平行动作；S5b 资产表加表情参考视频与白模；S6 加相对时间、部署密度、分段绑定。
- **校验重校**：W04 不再以"30s 内 >8 镜"提示（官方案例本身 9 镜 / 30s），改为平均镜长 < 2s 或单镜 < 1.5s 才提示。无新增警告码。
- 示例：`examples/performance/07-mask-and-leak`（面具 + 泄漏，blend 25/19/6，保真 matched）、`examples/performance/08-listener-reaction-chain`（听者反应链 9→14→25 的 production 示例，0 警告）。

## 一句话

先做导演决策，再把决策翻译成模型能看见的东西，最后才写 Prompt。

## 流水线

```
S1 资源读取 → S2 任务识别 → S4 表演外化 → S5 分镜与参考资产 ▮ → S6 Prompt → S7 检查
```

输入是已成形的剧本场景（任何来源）、分镜或表演需求；剧本层缺口只登记不代写。纯表演测试走共用 S4 模块，不强制故事、参考图或停靠；可直接说"10秒，从愤怒到委屈，最后忍住眼泪"或"原文直出 Crying"。交付原则：对话是默认，落盘只在停靠确认后或用户明确要求时。

## 文件地图

| 文件 | 何时读 |
|---|---|
| `SKILL.md` | 入口：表演优先路由、运行模式、五层分离、硬规则、输出契约、输入契约 |
| `references/seedance-2.5-capabilities.md` | 写任何模型能力/参数前；事实分级表 |
| `references/stage-1-intake.md` | S1 / S2：资产登记、任务树（R2V 核心）、入口判定、clip 估算、画幅时长、项目目录 |
| `references/emotion-performance.md` | 原文/微调/重组，强度与克制独立，高光时间编排及保真 |
| `references/performance-grammar.md` | 把条目组成人物表演：hinge、可读性地板、阶梯、过渡铰链、面具与泄漏、听者与切点、相对时间 |
| `references/performance-record.md` | 可选编译前记录与自动检查接口 |
| `references/stage-4-performance.md` | S4 表演外化与台词的模型执行约束 |
| `references/stage-5-directing-storyboard.md` | S5 导演与分镜 |
| `references/director-lenses.md` | S5 透镜：按意图选择，不覆盖锁定表演 |
| `references/director-craft.md` | 导演 / 摄影 / 剪辑一手说法按决策整理（景别、并置、切点、运动动机、镜头曲线、画外、平行动作）及 Seedance 写法 |
| `references/camera-vocabulary.md` | 运镜词汇："术语 + 描述" |
| `references/stage-5b-reference-assets.md` | S5b 参考资产清单与图像简报（图 + 文核心） |
| `references/stage-6-prompt-compiler.md` | S6 编译规范 |
| `references/stage-7-qa-continuity.md` | S7 检查与成片反馈 |
| `references/production-workflow.md` | 完整生产包：素材绑定、参数、上游版本、审阅记录 |
| `references/handoff-contract.md` | 与 film-creative 的交接物、账本模式、正典变更协议、台词预算、交付默认 |
| `references/dialogue-pacing.md` | 对白场 / 宣布 / 亮相：一句一切、逐镜变化、hero beat、修订全文交付 |
| `references/production-profile.md` | 项目生产常量档案：字段、进入 Prompt 的位置、更新规则 |
| `references/validation-log.md` | 成片验证记录与标签变更登记 |
| `references/scene-parameters.md` | 场景参数卡：六参数在表演 / 分镜 / 模型执行中的取值 |
| `references/externalization-lexicon.md` | 外化词典（可选写法） |
| `references/anti-mechanical.md` | 机械感诊断 |
| `references/causal-chain.md` | 表演状态推进/持续与镜头链 |
| `references/genre-packs.md` | 基调为动作 / 悬疑恐怖 / UGC 广告 / 蒙太奇时叠加 |
| `references/source-analysis.md` | 审计 / 更新来源时 |
| `templates/*` | 分镜卡 / Prompt / 资产简报 / 登记表 / 生产记录骨架（`script-scene.md` 为输入格式参照） |
| `scripts/emotion_library.py` | 按编号或关键词读取完整条目，`--list` 查看索引；`--zh` 译写、`--neighbors ID` 过渡、`--ladder FAMILY` 阶梯、`--readability 景别`、`--listener` 反应镜候选 |
| `scripts/validate_prompt.py` | S6 之后必跑 |
| `scripts/ledger_check.py` | 分镜 / 台词表（xlsx）改动后：时间连续、长镜含台词、机位单调、台词窗口 |
| `examples/example-01-kitchen-keys*.md` | 完整走查 + 通过校验的 Prompt |
| `examples/example-02-one-scene-three-lenses.md` | 同一场戏三个透镜的对照，含一版通过校验的 Prompt |
| `examples/example-03-yogurt-comedy*.md` | 喜剧走查（三拍 + 反讽落差），通过校验 |
| `examples/example-04-parameters-fight*.md` | 同一套规则，参数卡不同：高强度外放吵架，与示例 01 对照 |
| `examples/bad-example-3-lazy-long-take.prompt.md` | 反例：一段发言装进 9s 长镜 + 三镜同机位（W22 / W23） |
| `examples/performance/acceptance.md` | 五组验收 Demo、取材/改动说明及成片观察点 |
| `examples/production/acceptance-2.3.1.md` | 生产侧验收与 30 秒对照 |

## 校验脚本

```bash
cd <实际安装的Skill目录>
python3 scripts/validate_prompt.py <prompt.md> [--duration N] [--json]
python3 scripts/validate_prompt.py <fragment.md> --artifact performance --duration 10
python3 scripts/validate_prompt.py <fragment.md> --artifact performance --record <record.json>
python3 scripts/validate_prompt.py <original.txt> --artifact raw --entry-id 6
```

退出码 0 只代表无确定性错误，不代表表演或视频质量通过。多文件默认按连续片段做提示，独立 A/B 对照加 `--batch independent`。Python 3.9+，基础脚本仅用标准库；真实媒体预检另需 PATH 中的 ffprobe（测试另用 ffmpeg）。

账本检查（项目主表为分镜 / 台词 xlsx 时）：

```bash
python3 scripts/ledger_check.py <分镜与台词.xlsx> [--sheet 分镜总表] [--lines-sheet 台词与表演] [--long 7] [--very-long 10] [--json]
```

完整生产预检：

```bash
python3 scripts/validate_prompt.py <prompt.md> --production-record <production.json> --require-ready --json
```

接口与参数适配见 `references/production-workflow.md`。生产侧验收和 30 秒对照见 `examples/production/acceptance-2.3.1.md`；可直接测试 `examples/production/30s-fight-t2v.prompt.md`。R2V 案例需补真实素材；不会把虚构图号当就绪。

## 项目目录约定

```
<workspace>/<ip-slug>/ip.md · assets/ · <story-slug>/{00_brief, 01_concept, 02_story, 03_script/, production-profile.md, 04_shots/, 05_assets/, 06_prompts/, 07_qa/}
```

00–03 层是创意侧输入（film-creative 或用户提供），本 Skill 只读不写。 项目主表是分镜 / 台词 xlsx 时按 `references/handoff-contract.md` §二 的账本模式工作。

## 事实来源

- `[官方]` 火山方舟《Doubao Seedance 2.5 提示词指南》（2026 版，38 页）
- `[一手·摘要]` 导演 / 摄影师 / 剪辑师本人著作与访谈，DGA · ASC · BFI · Criterion · Paul Ekman Group 等机构材料，本次调研只读到搜索摘要（清单见 `references/source-analysis.md` §2.0.0 调研）
- `[第三方]` Higgsfield、fal.ai、rundiffusion、runware、the-decoder、mindstudio 等（见 `references/source-analysis.md`）
- 分辨率各来源不一致（480p/720p/1080p/4K），Skill 内标为"以平台为准"。

## 版本管理

- 语义化版本，记录在 `VERSION` 与 `CHANGELOG.md`。
- 每次改动跑 `bash tests/run_tests.sh`；GitHub Actions 在 push 与 PR 时自动跑。
- 生产/表演核心文件由 `tests/test_protected_zone.py` 哈希锁定（1.0.0 基线取自 v2.3.1；1.1.0 为强制情绪层 W20 重算了 validate_prompt.py、stage-6、prompt-templates、shot-card 四个文件的基线；1.3.0 为 W22/W23 重算 validate_prompt.py；2.0.0 为表演语法与一手导演手法重算 emotion-index、emotion_library、stage-4/5/5b/6、capabilities、director-lenses、shot-card、validate_prompt，并新增 performance-grammar 与 director-craft 两个受保护文件）；有意变更属于独立的生产版本发布，需同步更新哈希并在 CHANGELOG 说明。

## 维护

- 模型能力更新 → 只改 `references/seedance-2.5-capabilities.md`，并保留事实标签。
- 新任务类型 → 更新对应模板与路由；脚本只增加可确定核对的契约，不通过累积情绪关键词或固定动作组合模拟语义判断。
- 校验脚本回归：`bash tests/run_tests.sh`。

## 安装

```bash
git clone https://github.com/Anelse0/film-director.git <skills目录>/film-director
```
