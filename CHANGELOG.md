# Changelog

## 1.1.0 — 2026-09-17

导演语法与官方对齐版本（生产 / 导演核心的有意变更；保护区哈希在本提交公开重设，见 `tests/test_protected_zone.py` 与 `tests/acceptance-1.1.0/protocol.md`）。**工程完成：测试通过；效果提升未验证**——没有生成对照成片，也没有用户盲选。

### 调研（`tests/acceptance-1.1.0/`）
- 官方：火山方舟《Seedance 2.5 提示词指南》PDF 通读 41 页；在线教程、《创建视频生成任务 API》、《2.0 系列提示词指南》FAQ、Seed 博客复核，补齐 PDF 之外的参数与限制。
- 导演语法：Mackendrick、Mamet、Hitchcock/Truffaut、Lumet、Murch、Bordwell、Block、Katz、Proferes、Weston、Deakins、Fincher、Lubezki、Villeneuve、Spinotti/Mann、Richards/Zhao、Gerwig/Levy、Nolan 及 Every Frame a Painting 等；每条标注已读原页 / 搜索摘要。
- 台词速率：NCVS、Tauroza & Allison 1990、Yuan/Liberman/Cieri 2006、Netflix TTSG、Banse & Scherer 1996、中文配音行业数值；官方无每秒字数规则。
- 暧昧 / 爱情：Sciamma（BFI）、Lachman（Film Stage）已读原文；Wong/Doyle、Linklater、Guadagnino/Mukdeeprom、Wright、Coppola、Jenkins、Haigh、Lubitsch/Wilder 经搜索摘要。

### Added
- `references/director-grammar.md`：三个元问题、景别、运镜（动机 → 动作 → 终点）、动线与调度（走位表、平面 / 纵深、动线语法、轴线与合法越轴、三种对话图形）、覆盖与剪辑（Murch 六准则、眨眼即剪、POV 三联、迟进早出）、构图与镜头（对比 / 亲和、焦距即心理、机高）、光与色、决策载体、类型语法（悬念 / 视觉喜剧 / 动作 / 封闭空间 / 暧昧爱情）、十条推导规则、来源与核实状态。
- S5 §5.0 决策载体（文字 / 关键帧 / 白模 / 动作视频 / 宫格）、§5.1c 走位表、§5.1b 景别序列；S5b §5b.0 从载体推资产；T3b 白模模板；【严格排除】可选段位（官方范例）。
- 能力表 §7 台词每秒预算（英文 2.5 词/s、中文 4 字/s、占比 2/3 的一手依据与预算表）。
- `genre-packs.md` G5 视觉喜剧、G6 暧昧 / 爱情（难题 → 机制 → 选择 → 风险）；`director-lenses.md` L19 凝视与克制，每条透镜补"作用机制"与"语法依据"。
- 示例 05〈楼梯间的信〉（信息差、有动机的推近与反向跟拍、关键帧载体）、示例 06〈阳台的烟〉（错位注视、身体先于头脑、无 bgm），均通过校验。
- `tests/test_directing_release.py`：W04 阈值对齐官方范例、W19 退役、示例 05 / 06 清洁、语法与载体接线、无固定意图映射、词典不再规定运镜、台词预算有一手来源。
- 硬规则 15（每镜负载）、16（决策载体）、17（台词预算）。

### Changed
- `seedance-2.5-capabilities.md`：按官方在线文档重写——Model ID、duration [4, 30] / -1、resolution 480p / 720p / 1080p（无 4k）、ratio 取值与锁定任务只允许 adaptive、输入规格、真人人脸限制、仅音频输入、11 种语言、mov 编码、水印、omni_reference_task_type、不支持的参数、提示词长度建议、声音符号规范、分段绑定参考的官方写法、2.0 FAQ、官方 `sd25-pe` Skill 与模板文档的存在；分辨率与发布时间由 `[第三方]` 改为 `[官方]`。
- `validate_prompt.py`：W04 改为 <2 s 与 >10 镜 / 30 s 的审阅提示（官方 30 秒范例 9 镜、最短 2 s）；W19 标点推意图退役。
- `stage-4-performance.md`：删除"每个动词配一个身体证据（恳求 = 前倾 + 手伸出）"的固定映射与"反讽 = 台词与动作相反"的规则化；人物语言开发交回创意侧，S4 只取执行需要的语音信息；多人同框由"默认拆单人"改为风险登记与可协商方案；台词长度按预算；官方符号规范可选。
- `stage-5-directing-storyboard.md`：重写。5.4 推近的动机由"靠近情绪"改为"人物内部变化"（消除与 W15 的自相矛盾）；5.2 加入"机器要不要动""每镜负载"；5.6 复合运镜写同步 / 先后；5.9 诊断表改为按顺序排查而非单因单解；5.1 允许有意的时空省略；5.1b 无主控句时用观众问题替代。
- `stage-6-prompt-compiler.md` / `prompt-templates.md`：每镜负载规则；镜头段首标注 ≤40 字、运镜动机展开写在标注后；台词不为每句新编听者反应；T8 延长不再复述原视频末态，直接指代、可换景别与速度、可引用其他视频；T3b 白模。
- `stage-7-qa-continuity.md`：加导演语法检查行；口型 / 动作被赶 / 机器乱动 / 长镜头崩的诊断改为多因排查。
- `camera-vocabulary.md`：按官方"景别 + 机位 + 运镜 + 速度 + 质感"五要素重组；加焦距与景深写法、机高、运镜终点示例、反向跟拍、急推变焦、匹配转场、光的动机、声音符号。
- `externalization-lexicon.md`：最后一列由"摄影 / 声音"改为"声音 / 可见性条件"，去掉情绪 → 运镜的固定伴随。
- `templates/shot-card.md`：加观众问题、轴线、决策载体、焦距感、运镜动机 → 终点、每镜主要事件与记忆点；`templates/script-scene.md`：策略列与距离曲线改为按需。
- `SKILL.md`：S5 读取项加 grammar；硬规则 8 加动机与终点；硬规则 10 指明导演逻辑的存放处；工作边界补"不开发人物语言"；运行模式表的"触发词"改为"典型说法（示例）"；类型叠加加视觉喜剧 / 暧昧爱情；示例列表加 05 / 06。
- `source-analysis.md`、`validation-log.md`：登记新来源与标签变更；待验证队列加 9–12 项。

### Retired
- W19（标点推意图）；"抗拒快切"作为 W04 的依据；`stage-4` 角色声音表；"两人对视不动 → 回 S3""长 clip 后半崩 → 切成两个 15 s""口型对不上 → 换中文 / 英文"的单因单解。

### 未改动（保护区哈希保持 1.0.0）
- `assets/emotion-library.json`、`references/emotion-performance.md`、`references/emotion-index.json`、`references/performance-record.md`、`references/production-workflow.md`、`templates/performance-record.json`、`templates/production-record.json`、`templates/reference-asset-brief.md`、`templates/asset-registry.md`、`scripts/prompt_structure.py`、`scripts/production_contract.py`、`scripts/production_preflight.py`、`scripts/emotion_library.py`、`scripts/performance_checks.py`。

## 1.0.0 — 2026-09-07

独立的 Seedance 2.5 生产后端 Skill，内容取自 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) **v2.3.1**（用户指定以 2.3.1 为生产基线；创意前端由 film-creative Skill 承担，其基线为 2.6.0-alpha.3）。

- 范围：S1 资源读取、S2 任务识别、S4 表演外化（含情绪表演库）、S5 导演与分镜、S5b 参考资产、S6 Prompt 编译、S7 检查；表演优先路由（performance / production / raw）完整保留；生产契约与 30 秒设计沿用 2.3.1。
- 移除创意侧文件：stage-3a/3b/3c、concept-generation、screenwriting-traditions、validate_concept、story 模板、概念示例与概念测试。
- 新增「输入与交接」契约：接受任何来源的剧本场景文本；剧本层缺口只登记不代写；已确认台词与场景为锁定输入。
- 共用文件（stage-1-intake、scene-parameters、causal-chain、anti-mechanical、genre-packs、stage-4、stage-5、director-lenses、script-scene 模板）中指向创意侧文件或概念模式的引用改为交接说明；其余生产核心文件与 v2.3.1 逐字节一致。
- `tests/test_protected_zone.py` 以 1.0.0 为基线哈希锁定生产/表演核心；对照 v2.3.1 的差异可在源仓库 tags 中核查。
- 历史版本记录（1.2.0–2.3.1 及其后的 2.4.0–2.6.0 开发线）见源仓库 Film-Seedance-Director 的 CHANGELOG 与 tags。
