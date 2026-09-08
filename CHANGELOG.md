# Changelog

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
