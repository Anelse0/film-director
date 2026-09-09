# film-director

版本 **1.3.2**。Seedance 2.5 视频 Prompt 生产 Skill：表演外化与情绪提示词、导演与分镜、参考资产计划、Prompt 编译、连续性与质量检查。调用：`/film-director` 或在对话中描述任务（拆分镜、转 Prompt、表演测试、改成片）。

创意前端（概念、故事、剧本、台词创作与改写）由独立的 [film-creative](https://github.com/Anelse0/film-creative) Skill 承担。本 Skill 内容取自 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) **v2.3.1** 的生产后端（用户指定以 2.3.1 为生产基线）。

## 1.3.2 更新（容错修复）

- xlsx 读取：缺 `r` 属性的行 / 单元格按位置读；Excel 锁文件与损坏文件报 `ValueError` 而非追溯。`ledger_view` 只把时间列的小数显示为 mm:ss。
- `ledger_check` L03 与 `validate_prompt` W22 同口径（单句 ≥7s 或多句 ≥9s，新参数 `--long-dialogue`）。
- `validate_prompt`：W22 不把"重读 / 一词"标注的引号当台词；W04 的 >8 镜提示只在平均镜长 <2s 时给出，不再与一句一切约定冲突。
- 新增与 film-creative 同文文件的一致性测试；修正 run_tests 里一条恒真断言。

## 1.4.0 更新（参考素材绑定格式）

- 【素材绑定】人物形象（面部/发型/体型）与服饰（本场服装/配饰）**硬拆两条**，换装态各一条服饰参考（官方 §4.2 一图一职责）；改 stage-6/prompt-templates/stage-5b 及两个模板、硬规则 3、生产档案。主体图数=角色数×2，>8 抽卡。
- 【素材绑定】段**禁止 E 层注释**（约定/数量/草稿/待回填/用户提供）：这些进文末 E 参数表或 QA，不进 D 层。新增校验 **W24**。
- 受保护区重算 6 文件哈希；示例 01–04 保留旧式绑定作示例。

## 1.3.1 更新
## 1.3.1 更新

- `references/dialogue-pacing.md` 新增 §4b：台词设计表各列 → 〔说法〕/〔情绪〕/【整体情绪弧线】/ 反应镜 / S4 表演块 / 末镜收尾 的映射表；有表时不重推情绪层。
- `scripts/ledger_view.py`：账本模式下按镜号范围把 xlsx 读成 Markdown（与 film-creative 同文）。
- 测试夹具中的人名改为泛称。

## 1.3.0 更新（对白节奏 · 亮相 · 与 film-creative 的协作契约 · 账本模式）

- **协作契约** `references/handoff-contract.md`（与 film-creative 同文）：台词设计表作为交接物直接映射为〔说法〕〔情绪〕与【整体情绪弧线】；正典变更协议（登记 → 扫描 → 处理，不 patch 旧镜头）；台词预算反向回传；每次修订交付完整 Prompt 全文。
- **对白场节奏与亮相** `references/dialogue-pacing.md`：一句一切、对白镜 2–4s、逐镜换景别 / 角度 / 运镜、hero beat 模板（介绍 → 他人反应 → 特写揭示 → 落定）。新增校验 **W22**（含台词长镜：≥7s 单句或 ≥9s 对白，旁白与单镜 clip 免检）与 **W23**（三镜标注完全相同），均为 WARN 级本地约定 `[推论]`。
- **生产档案** `references/production-profile.md` + `templates/production-profile.md`：画幅、语言、素材绑定约定、调色段、声音 / 旁白、节奏约定、字幕、首帧策略、台词预算口径——一个项目只说一次，S1 先读。
- **账本模式**：项目主表是分镜 / 台词表（xlsx）时的读写规则；新增 `scripts/ledger_check.py`（stdlib 读 xlsx：时间连续 L02、长镜含台词 L03、机位单调 L05、台词窗口 L06、语速 L08、占位统计 L07）与 `scripts/xlsx_lite.py`。
- 硬规则 15 与快速路由新增对应入口；反例 `examples/bad-example-3-lazy-long-take.prompt.md`。

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
| `references/performance-record.md` | 可选编译前记录与自动检查接口 |
| `references/stage-4-performance.md` | S4 表演外化与台词的模型执行约束 |
| `references/stage-5-directing-storyboard.md` | S5 导演与分镜 |
| `references/director-lenses.md` | S5 透镜：按意图选择，不覆盖锁定表演 |
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
| `scripts/emotion_library.py` | 按编号或关键词读取完整条目，`--list` 查看索引 |
| `scripts/validate_prompt.py` | S6 之后必跑 |
| `scripts/ledger_check.py` | 分镜 / 台词表（xlsx）改动后：时间连续、长镜含台词、机位单调、台词窗口 |
| `scripts/ledger_view.py` | 账本模式开工前：按镜号范围把表读成 Markdown |
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
python3 scripts/ledger_check.py <分镜与台词.xlsx> [--sheet 分镜总表] [--lines-sheet 台词与表演] [--long 7] [--long-dialogue 9] [--very-long 10] [--json]
python3 scripts/ledger_view.py <分镜与台词.xlsx> --from 30 --to 40 [--cols 镜号,入点,出点,景别,台词]
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
- `[第三方]` Higgsfield、fal.ai、rundiffusion、runware、the-decoder、mindstudio 等（见 `references/source-analysis.md`）
- 分辨率各来源不一致（480p/720p/1080p/4K），Skill 内标为"以平台为准"。

## 版本管理

- 语义化版本，记录在 `VERSION` 与 `CHANGELOG.md`。
- 每次改动跑 `bash tests/run_tests.sh`；GitHub Actions 在 push 与 PR 时自动跑。
- 生产/表演核心文件由 `tests/test_protected_zone.py` 哈希锁定（1.0.0 基线取自 v2.3.1；1.1.0 为强制情绪层 W20 重算了 validate_prompt.py、stage-6、prompt-templates、shot-card 四个文件的基线；1.3.0 为 W22/W23 重算 validate_prompt.py）；有意变更属于独立的生产版本发布，需同步更新哈希并在 CHANGELOG 说明。

## 维护

- 模型能力更新 → 只改 `references/seedance-2.5-capabilities.md`，并保留事实标签。
- 新任务类型 → 更新对应模板与路由；脚本只增加可确定核对的契约，不通过累积情绪关键词或固定动作组合模拟语义判断。
- 校验脚本回归：`bash tests/run_tests.sh`。

## 安装

```bash
git clone https://github.com/Anelse0/film-director.git <skills目录>/film-director
```
