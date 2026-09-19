# Changelog

## 1.3.1 — 2026-09-19

把 1.3.0 的"连续台词轨"从可选字段变成模型本身（自查：1.3.0 文档前后打架、连续轨靠 E 层字段记得写，属补丁痕迹）。

### Changed
- `duration-rhythm.md` §二、§三 重写为两条轨：台词轨（校准语速、整条一次取整、句句相接）与画面轨（切在信息上、整数秒、≥2 s、能并进台词镜的动作不单独成镜），再对齐（窗口 = 起点 + 所属镜，可溢出 ≤1 s）；D10a 例：15.2 s 轨 + 4 s 无声 = 20 s。§九 补连续轨下的 D05 例。
- 对话场（台词净时长 ≥25%）**默认 台词轨 = 连续**，无需 E 层字段；`台词轨 | 窗口` 才退回逐窗口 W05（表演档默认窗口）。`validate_prompt.py` 与 `rhythm_checks.py` 同步。
- `stage-5` §5.2 第 7 步、`stage-6` 台词规则改为两轨表述。
- 测试：example-04（对话场）的"长句保留时间审阅"改为接受 W05 / W29 / 台词轨 INFO；保护区哈希重设。

## 1.3.0 — 2026-09-19

连续台词轨与语速校准。触发：用户把 1.2.0 规则产出的 D10a/b/c（25 / 19 / 18 s）手改到 21 / 15 / 14 s 后出片可用——说明 1.2.0 的时长模型比模型实际说话慢一档：逐句整数取整（7 句吃掉 3 s）、逐窗口 W05 逼人撑窗口、语速 3 词/秒低于实测 3.36。**工程完成：测试通过。效果提升：用户反馈手改版出片可用（未量成片）。**

### Added
- E 层 `台词轨 | 连续`：台词按连续轨排，窗口只标起点与所属镜，一句可溢出到下一镜 ≤1 s（`台词轨溢出容差`）；`rhythm_checks.track_schedule` 链式检查 → **W29**（压过下一句起点 >1 s 或超过片长才报），取代逐窗口 / 逐镜的 W05（总占比 W05 保留）。用户手改 D10a 在此模式 @3.3 词/秒下从 10 个 WARN 降到 2 个（仅开头 4 s 无台词的 W24）。
- `measure_clip.py --prompt` 输出校准行：词数 / 有声秒 = 实测词/秒（下限），回填 E 层 `语速词每秒`；D05 成片 3.36 词/秒。
- `duration-rhythm.md` §十 校准流程；§二 改为台词轨一次取整；§三 连续轨行；§一 校准依据行。
- `tests/test_rhythm.py` +2（连续轨溢出 / 堆积 / 片长；轨模式与轨和推导）。

### Changed
- 时长推导参考 = ceil(净时长 ÷ 填充率 + 无台词镜 + 动作节拍)，不再逐句取整求和（逐句合计只作参考显示）。
- `SKILL.md` 硬规则 18、`stage-6` 台词规则、`prompt-templates.md` E 层字段说明。

## 1.2.0 — 2026-09-19

时长与节奏版本（生产 / 导演核心的有意变更；保护区哈希在本提交重设）。触发：sable-point-college EP01 D05–D07 被用户反复批评"时间设计和利用不充分、节奏慢"，且 2.5 成片实测确认节奏来自 Prompt 的时间设计。**工程完成：测试通过。效果提升未验证**——尚未用收紧后的 Prompt 重新生成并对照。

### 调研
- 官方：《Seedance 2.5 提示词指南》在线版（2026-09-18）时间戳段与 30 秒范例逐镜秒数（3/3/4/4/4/4/3/3/2，8/9 镜有台词）。
- 实测：EP01 D05 成片切点与 Prompt 逐一对应（误差 ≤0.3 s），有声占比 59%，窗口内静音空档 22 段 → 记入 `validation-log.md`。
- 剪辑与镜长：Murch（眨眼即剪、六准则）、Lumet（节奏变化 / 过长）、Bordwell 2007（对话场 ASL 2–4 s）、Cutting et al.（当代 ASL 4.3 s；特写更短）、竖屏短剧实测 2.5 s（第三方搜索摘要，原页下架）。

### Added
- `references/duration-rhythm.md`：§九 一句不等于一镜（视觉单元分镜法：拆分句 → 每分句一个视觉事件 → 一句可跨两镜、尾段画外 → 相邻镜至少换一项）；clip 时长从内容推导（不默认 30 s）、台词窗口 = 估时 ÷ 0.9 向上取 0.5 s（写进 Prompt 取整数秒、松弛 ≤1 s）、镜长分布目标（对话 2–4 / 蒙太奇 2–3 / 持续 5–8 需理由）、无声段功能表与 ≤20% 阈值、Prompt 提速写法七条、检查项对照。
- `scripts/rhythm_checks.py` + `validate_prompt.py` 接线：W22 窗口过宽、W23 长镜（>5 s 无台词无运镜；>8 s 任何镜）、W24 无声段（窗口外 >20%、首尾 >2 s）、W25 对话场平均镜长 >4.5 s、W26 声明时长比推导参考多 ≥4 s、W27 减速词、W28 固定机位整句一镜 ≥4 s；INFO 节奏档 / 平均镜长与分布 / 台词净时长·建议窗口·松弛 / 推导参考。对话场判定：台词净时长 ≥25% clip，E 层 `节奏档` 可覆盖；其余阈值均可在 E 层覆盖（`动作节拍秒数` 登记与台词同镜的实体动作）。
- `scripts/measure_clip.py`：用 ffmpeg 量成片的切点、平均镜长、有声占比、首尾与最长静音，`--prompt` 并列 Prompt 声明。
- `tests/test_rhythm.py`（7 项）。
- `prompt_structure.dialogue_checks(..., fill=0.9)`：W05 的 90% 阈值改为读 E 层 `台词填充率`（与 W22 的建议窗口同一旋钮）；项目写 `台词填充率 | 1.0` 即"窗口 = 词数 ÷ 语速向上取整秒"的口径，只在台词放不下时报 W05。

### Changed
- `SKILL.md`：硬规则 18（对话场一句不等于一镜、时长从内容推导）；S5 读 `duration-rhythm.md`；S7 有成片时用 `measure_clip.py`；硬规则 12 提及 W22–W27；快速路由加"成片节奏慢"。
- `stage-5` §5.2 第 5 步切点跟信息走（§九）、第 7 步 clip 总长从内容推导；`stage-6` 一句分两段引号跨镜的写法；`prompt-templates.md` E 层节奏字段说明；`stage-6` §6.2 台词窗口规则与【贯穿要求】节奏指令；`prompt-templates.md` T2 贯穿要求加节奏指令占位；`stage-7` 诊断表加"节奏慢 / 拖"一行；能力表 §4.3 加官方范例逐镜秒数与实测注记；`validation-log.md` 首条记录。

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
