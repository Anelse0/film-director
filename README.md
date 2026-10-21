# film-director

Seedance 2.5 视频 Prompt 生产 Skill：表演外化与情绪提示词、导演与分镜（导演语法、机位设计、变化轨、镜头纵览与执行卡）、时长与节奏、参考资产计划、Prompt 编译、连续性与质量检查、成片实测。调用：`/film-director` 或在对话中描述任务（拆分镜、转 Prompt、表演测试、改成片）。版本号在 `VERSION`，每一版改了什么、为什么、依据哪条成片见 `CHANGELOG.md`。创意前端（概念、故事、剧本、台词）由独立的 film-story Skill 承担，本 skill 不创作剧本。

## 一句话

先做导演决策，再把决策翻译成模型能看见的东西，最后才写 Prompt。

## 流水线

```
S1 资源读取 → S2 任务识别 → S4 表演外化 → S5 分镜与参考资产 ▮A ▮B → S6 Prompt → S7 检查 ▮C
```

输入是已成形的剧本场景（任何来源）、分镜或表演需求；剧本层缺口只登记不代写。纯表演测试走共用 S4 模块，不强制故事、参考图或停靠；可直接说"10秒，从愤怒到委屈，最后忍住眼泪"或"原文直出 Crying"。交付原则：对话是默认，落盘只在停靠确认后或用户明确要求时。停靠点三个：A 方案（机位表 + 镜头纵览，`check.py plan`）、B 分镜卡、C Prompt 交付（S7 八道做完后回显全文）；任何停靠点的反馈走改稿回路（定位 → 方案 → 只改受影响小节 → 变更摘要）。

## 文件地图

| 文件 | 何时读 |
|---|---|
| `SKILL.md` | 入口：表演优先路由、工作边界、流水线与脚本时机、运行模式、五层分离、硬规则、规则维护、输出契约 |
| `references/seedance-2.5-capabilities.md` | 写任何模型能力/参数前；事实分级表 |
| `references/checks.md` | 校验码总表：每个 ERROR / WARN / C / S / Q 码的触发条件、处置、分类（成片教训类 / 其余 / 并入 / 暂停）；规则文只写"校验 Wnn"，细节到这里查 |
| `references/stage-1-intake.md` | S1 / S2：资产登记、任务树（R2V 核心）、入口判定、clip 估算、画幅时长、项目目录 |
| `references/emotion-performance.md` | 原文/微调/重组，强度与克制独立，高光时间编排及保真 |
| `references/performance-record.md` | 可选：编译前记录与自动检查接口 |
| `references/stage-4-performance.md` | S4 表演外化：设计稿 → 翻译（三段：A 层词 → 词典行 → 可见 + 声音）、基调是参数（§4.4b）、台词括号 = 声音翻译（§4.4c 第 7 条） |
| `references/stage-5-directing-storyboard.md` | S5 导演与分镜：决策载体、走位表、机位设计（§5.1g）、变化轨（§5.1f）、镜头设计顺序（含 6a 反应镜、8a 无台词段预算）、每镜负载、镜头纵览与执行卡（§5.11） |
| `references/duration-rhythm.md` | 时长与节奏：clip 时长从内容推导、台词窗口 / 连续台词轨、镜长分布、无声段（最长连续无台词 ≤3 s）、变化轨、一句不跨镜（§九）、语速校准；阈值的来历与设计，码表在 `checks.md` |
| `references/director-grammar.md` | S5 主参考：景别 / 运镜 / 动线 / 剪辑 / 构图 / 光 / 载体 / 类型语法，每条附一手来源与核实状态 |
| `references/director-lenses.md` | S5 透镜：场景问题 → 作用机制 → 选择 → 边界 → 语法依据 |
| `references/camera-vocabulary.md` | 镜头语汇：景别 / 机高 / 焦距与景深 / 运镜与终点 / 构图 / 转场 / 光 / 声音符号 |
| `references/stage-5b-reference-assets.md` | S5b 参考资产清单与图像简报（图 + 文核心） |
| `references/stage-6-prompt-compiler.md` | S6 编译规范 |
| `references/stage-7-qa-continuity.md` | S7 检查与成片反馈：WARN 分类、八道审阅、成片问题定位表、QA 现行状态 |
| `references/production-workflow.md` | 可选：完整 API 生产包的素材绑定、参数、上游版本、审阅记录（手工上传平台的项目不需要） |
| `references/validation-log.md` | 成片验证账本：表的 `#n` 行号就是规则文里"证据 #n"的指代；待验证队列；标签变更登记 |
| `references/scene-parameters.md` | 场景参数卡：六参数在表演 / 分镜 / 模型执行中的取值 |
| `references/externalization-lexicon.md` | 外化词典：情绪 → 动作 / 表情 / 视线 / 节奏 / 声音，含「（轻松）」变体；「A 层词」一节是 W57 / W-C9 的字典 |
| `references/anti-mechanical.md` | 机械感诊断 |
| `references/causal-chain.md` | 表演状态推进/持续与镜头链 |
| `references/genre-packs.md` | 基调为动作 / 悬疑恐怖 / UGC 广告 / 蒙太奇 / 视觉喜剧 / 暧昧爱情时叠加：难题 → 机制 → 选择 → 风险 |
| `references/source-analysis.md` | 审计 / 更新来源时 |
| `templates/*` | 分镜卡 / Prompt / 资产简报 / 登记表 / 生产记录骨架（`script-scene.md` 为输入格式参照） |
| `scripts/emotion_library.py` | 按编号或关键词读取完整条目，`--list` 查看索引 |
| `scripts/validate_prompt.py` | S6 之后必跑：格式 / 契约 ERROR、E23 方向、节奏 W22–W29、变化轨 W30–W33、基调 W35、官方对齐 W36–W41、焦点 / 括号 / 服装 W43–W45、措辞 W46–W48、衔接 W51、视角 W52、跨镜 / 画外 W54–W55、A 层词 W57；成片教训类默认改。码表见 `references/checks.md` |
| `scripts/camera_plan_check.py` | S5 停靠前（`--stage s5`）与 S6 入口：机位设计做没做（C01–C08）、方位换算对不对（C09）、和 Prompt 的左右矛盾（`--prompt`，C10） |
| `scripts/stage_check.py` | S5 停靠前与 S6 入口：执行卡 25 行、镜头纵览、三段表演翻译（S01–S05、C11、W-C6–W-C10） |
| `scripts/qa_check.py` | QA 改完：现行状态与 Prompt / 校验结果一致（Q01–Q03）、用户已点名类别的 WARN 没写理由保留（Q04） |
| `scripts/evidence.py` | 按编号读 `references/validation-log.md` 成片表的一行（`evidence.py 8 9`、`--grep 关键词`、`--all`）：规则文里的「证据 #n」查单条，不读整表 |
| `scripts/session_cost.py` | 量尺（不进保护区）：读会话 .jsonl，按 message id 去重算真实调用数 / output / 缓存读取 / 上下文均值与峰值、输出构成、规则文 Read 次数、脚本跑几次与"无改动重复"、产物整篇 Write 次数；改版后用下一条 clip 的会话和上一版比 |
| `scripts/check.py` | 一键入口（1.13.0）：`s5 <分镜卡>` / `s6 <分镜卡> [prompt]` / `qa [--sync] <qa.md>` 三个子命令只 import 上面四个脚本的 `check()` / `validate()`，合并报告按 ERROR → 成片教训类 WARN → 其余 WARN → 数字块（可直接粘贴进 QA 现行状态与第 8 道）→ INFO → 输入文件 sha256；`qa --sync` 把现行状态的机器行写回，再独立跑一遍 `qa_check` |
| `scripts/speaker_checks.py` / `layer_checks.py` | 校验模块（由 validate_prompt 调用）：W54 / W55 跨镜与画外归属；W57 A 层词边界，字典读外化词典 |
| `scripts/measure_clip.py` | 有成片时：切点 / 有声占比 / 语速校准 / 视觉变化谱对照 Prompt 的时间轨与变化轨（需 ffmpeg） |
| `examples/example-01-kitchen-keys*.md` | 完整走查 + 通过校验的 Prompt |
| `examples/example-02-one-scene-three-lenses.md` | 同一场戏三个透镜的对照，含一版通过校验的 Prompt |
| `examples/example-03-yogurt-comedy*.md` | 喜剧走查（三拍 + 反讽落差），通过校验 |
| `examples/example-04-parameters-fight*.md` | 同一套规则，参数卡不同：高强度外放吵架，与示例 01 对照 |
| `examples/example-05-stairwell-letter*.md` | 导演语法走查：信息差、有动机的推近与反向跟拍、关键帧作为构图载体，通过校验 |
| `examples/example-06-balcony-cigarette*.md` | 暧昧 / 爱情走查：凝视、距离、未完成的触碰、音乐克制，通过校验 |
| `tests/acceptance-1.1.0/` | 1.1.0 的 review、三份调研摘要（官方文档 / 导演语法 / 台词速率 / 暧昧爱情）与验收协议 |
| `examples/performance/acceptance.md` | 五组验收 Demo、取材/改动说明及成片观察点 |
| `examples/production/acceptance-2.3.1.md` | 生产侧验收与 30 秒对照 |

## 校验脚本

```bash
cd <实际安装的Skill目录>
python3 scripts/validate_prompt.py <prompt.md> [--duration N] [--json]
python3 scripts/validate_prompt.py <fragment.md> --artifact performance --duration 10
python3 scripts/validate_prompt.py <fragment.md> --artifact performance --record <record.json>
python3 scripts/validate_prompt.py <original.txt> --artifact raw --entry-id 6
python3 scripts/measure_clip.py <成片.mp4> --prompt <prompt.md> [--frames DIR]
python3 scripts/camera_plan_check.py [--stage s5] [--prompt <prompt.md>] <分镜卡.md>
python3 scripts/qa_check.py [--prompt <prompt.md>] <qa.md>
python3 scripts/check.py s5 <分镜卡.md>                                  # S5 停靠前
python3 scripts/check.py s6 <分镜卡.md> [<prompt.md>] [--json]           # S6 入口（无 Prompt）与 S6 后
python3 scripts/check.py qa [--sync] [--prompt <prompt.md>] <qa.md>     # QA 改完；--sync 写回机器行
python3 scripts/evidence.py 8 9                                          # 规则文里的「证据 #n」查单条
python3 scripts/session_cost.py --latest 3 [--project-dir ~/.claude/projects/<slug>]   # 会话成本量尺
```

退出码 0 只代表无确定性错误，不代表表演或视频质量通过。多文件默认按连续片段做提示，独立 A/B 对照加 `--batch independent`。Python 3.9+，基础脚本仅用标准库；真实媒体预检另需 PATH 中的 ffprobe（测试另用 ffmpeg）。

完整生产预检：

```bash
python3 scripts/validate_prompt.py <prompt.md> --production-record <production.json> --require-ready --json
```

接口与参数适配见 `references/production-workflow.md`。生产侧验收和 30 秒对照见 `examples/production/acceptance-2.3.1.md`；可直接测试 `examples/production/30s-fight-t2v.prompt.md`。R2V 案例需补真实素材；不会把虚构图号当就绪。

## 项目目录约定

```
<workspace>/<ip-slug>/ip.md · assets/ · <story-slug>/{00_brief, 01_concept, 02_story, 03_script/, 04_shots/, 05_assets/, 06_prompts/, 07_qa/}
```

00–03 层是创意侧输入（film-story 或用户提供），本 Skill 只读不写。

## 事实来源

- `[官方]` 火山方舟《Doubao Seedance 2.5 提示词指南》（PDF 与在线版）、《Seedance 2.5 教程》、《创建视频生成任务 API》、《Seedance 2.0 系列提示词指南》、ByteDance Seed 博客（见 `references/seedance-2.5-capabilities.md` 头部与 `tests/acceptance-1.1.0/research-seedance-official.md`）
- `[一手]` 导演 / 摄影师 / 剪辑师著作与访谈、语音学标准（见 `references/director-grammar.md` §十、能力表 §7）
- `[第三方]` Higgsfield、fal.ai、rundiffusion、runware、the-decoder、mindstudio 等（见 `references/source-analysis.md`）
- 分辨率按官方 API 文档：480p / 720p / 1080p，2.5 无 4k。

## 版本管理

- 语义化版本，记录在 `VERSION` 与 `CHANGELOG.md`。
- 每次改动跑 `bash tests/run_tests.sh`；GitHub Actions 在 push 与 PR 时自动跑。
- 生产/表演核心文件由 `tests/test_protected_zone.py` 哈希锁定；有意变更属于独立的生产版本发布，需同步更新哈希并在 CHANGELOG 说明。

## 维护

- 模型能力更新 → 只改 `references/seedance-2.5-capabilities.md`，并保留事实标签。
- 新任务类型 → 更新对应模板与路由；脚本只增加可确定核对的契约（层、格子、数字），不通过累积情绪关键词模拟语义判断——新的成片教训先进 `validation-log.md` 与外化词典，再考虑校验（SKILL「规则维护」）。
- 规则文只写规则、为什么、一行证据指针；版本注记进 CHANGELOG，案例进 validation-log，校验码细节进 `references/checks.md`。
- 校验脚本回归：`bash tests/run_tests.sh`。

## 安装

```bash
git clone https://github.com/Anelse0/film-director.git <skills目录>/film-director
```
