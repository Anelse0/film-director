# film-director

版本 **1.8.0**。Seedance 2.5 视频 Prompt 生产 Skill：表演外化与情绪提示词、导演与分镜（含导演语法：景别 / 运镜 / 动线 / 剪辑 / 决策载体）、时长与节奏（两条时间轨 + 变化轨）、参考资产计划、Prompt 编译、连续性与质量检查、成片实测。调用：`/film-director` 或在对话中描述任务（拆分镜、转 Prompt、表演测试、改成片）。

1.8.0 接入运镜库：`assets/camera-library.json` 是《AI 运镜提示词库》的原样副本（46 条，Camera / Movement / Speed / Framing / End 五段，保护区锁定），`references/camera-index.json` 是中文阅读索引。S5 先定动机与运动类别，再从库里取一条，按五段填成这一镜的主体、方向、速度、保持不变的东西与终点；原文只在用户指定时用。校验新增 W34（照抄通用句 / 中文 Prompt 夹英文五段骨架）与 W35（E 层运镜来源不成立）。

1.7.0 英文语速默认 4 词/s（用户定；慢戏 2.5–3、短促 4.5 显式写），校验估时随之改变。

1.6.0 每条 clip 至少交付一次变化（硬规则 20）：场级方案的 clip 切分表加 `交付变化` 列，写本条交付剧本事件轨哪几行（没有事件轨时写"谁：进 → 出"）；余韵行不单独成 clip，同一变化只交付一次；`scene_track.py --plan` 核对并逐条列出"删掉损失"。触发：THE ORDER EP03 场 4 clip04（16 s 只有余韵，峰值 / 观众问题 / 无声段理由都填了）。变化轨（W30–W33）、无声段功能（W24）照常查，不被取代。S5 §5.1 / §5.1f / §5.9 与 S7 §7.1 / §7.2 同步，保护区哈希重设。

1.5.0 接 film-creative 3.6 的"场面轨"：剧本告诉本 skill 这场有哪些场地 / 场景、每段做什么、估多长——**参考，不锁定**（台词仍锁定）。S5 可以重分段、换场地，在场级方案写一行"与场面轨的差异"；分镜合计比剧本估时多 20% 以上时只提醒用户，照常继续。新增 `scripts/scene_track.py` 列参考清单、算合计与比值、核差异行。保护区未动。1.5.1 起同样读 film-creative 3.7 的"## 事件轨"（赌注卡与场面轨合成的一行一变化表）。

1.4.0 把"镜与镜之间的变化"做成与时间平权的第三条设计轨：每条 clip 先声明峰值镜（E 层 `峰值镜 | N`），每镜声明四维变化 `【变化：景别 全→近｜机位 固定→推｜光 正→侧｜幅度 1→3】`；校验新增 W30–W33（连续零变化 / 无镜长对比 / 未声明峰值 / 峰值落在全景或越肩），`节奏档` 改为选检查集（对话 = W22–W33，表演 = W24 + W30–W33）；英文语速默认 3.5 词/s（2.5 = 均值 = 下限）；`measure_clip.py` 输出视觉变化谱（抽帧拼图 / 相邻镜直方图距离 / 镜内运动）对照变化轨，指出"平在设计还是渲染"。**工程完成（测试通过）；效果为非盲呈现改善**——触发案例的 v3 尚未生成对照，见 `CHANGELOG.md` 与 `references/validation-log.md`。

创意前端（概念、故事、剧本、台词创作与改写）由独立的 [film-creative](https://github.com/Anelse0/film-creative) Skill 承担。本 Skill 内容取自 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) **v2.3.1** 的生产后端（用户指定以 2.3.1 为生产基线）。

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
| `references/stage-5-directing-storyboard.md` | S5 导演与分镜：决策载体、走位表、变化轨（§5.1f 峰值镜 + 四维变化）、镜头设计顺序、每镜负载 |
| `references/duration-rhythm.md` | 时长与节奏：clip 时长从内容推导、台词窗口 / 连续台词轨、镜长分布、无声段、变化轨、W22–W33 阈值与理由、语速校准、场级合计与剧本场面轨 / 事件轨（§十一） |
| `scripts/scene_track.py` | 剧本场面轨 / 事件轨的参考清单（场地 / 场景 / 段 / 估时）+ 分镜场级合计与比值（≥1.2 提醒）+ 方案"与场面轨的差异"行 + clip 切分表"交付变化"列（每条 clip 交付哪几行变化、删掉损失） |
| `references/director-grammar.md` | S5 主参考：景别 / 运镜 / 动线 / 剪辑 / 构图 / 光 / 载体 / 类型语法，每条附一手来源与核实状态 |
| `references/director-lenses.md` | S5 透镜：场景问题 → 作用机制 → 选择 → 边界 → 语法依据 |
| `references/camera-library.md` | 运镜库用法：决策顺序（先动机后选条目）、五段填写、运镜来源（填写 / 原文 / 库外）、W34–W35 |
| `references/camera-index.json` | 运镜库中文阅读索引：职能、什么时候不用、人物运动、载体、官方术语与词表对应 |
| `references/camera-vocabulary.md` | 镜头语汇：景别 / 机高 / 焦距与景深 / 运镜与终点 / 构图 / 转场 / 光 / 声音符号 |
| `references/stage-5b-reference-assets.md` | S5b 参考资产清单与图像简报（图 + 文核心） |
| `references/stage-6-prompt-compiler.md` | S6 编译规范 |
| `references/stage-7-qa-continuity.md` | S7 检查与成片反馈 |
| `references/production-workflow.md` | 完整生产包：素材绑定、参数、上游版本、审阅记录 |
| `references/validation-log.md` | 成片验证记录与标签变更登记 |
| `references/scene-parameters.md` | 场景参数卡：六参数在表演 / 分镜 / 模型执行中的取值 |
| `references/externalization-lexicon.md` | 外化词典（可选写法） |
| `references/anti-mechanical.md` | 机械感诊断 |
| `references/causal-chain.md` | 表演状态推进/持续与镜头链 |
| `references/genre-packs.md` | 基调为动作 / 悬疑恐怖 / UGC 广告 / 蒙太奇 / 视觉喜剧 / 暧昧爱情时叠加：难题 → 机制 → 选择 → 风险 |
| `references/source-analysis.md` | 审计 / 更新来源时 |
| `templates/*` | 分镜卡 / Prompt / 资产简报 / 登记表 / 生产记录骨架（`script-scene.md` 为输入格式参照） |
| `scripts/camera_library.py` | 运镜库查询：`--list` / `--query` / `--slots`（五段填写模板）/ `--raw`（原文） |
| `scripts/emotion_library.py` | 按编号或关键词读取完整条目，`--list` 查看索引 |
| `scripts/validate_prompt.py` | S6 之后必跑；W22–W29 时间轨、W30–W33 变化轨（`rhythm_checks.py` / `variation_checks.py`） |
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

00–03 层是创意侧输入（film-creative 或用户提供），本 Skill 只读不写。

## 事实来源

- `[官方]` 火山方舟《Doubao Seedance 2.5 提示词指南》（PDF 与在线版）、《Seedance 2.5 教程》、《创建视频生成任务 API》、《Seedance 2.0 系列提示词指南》、ByteDance Seed 博客（见 `references/seedance-2.5-capabilities.md` 头部与 `tests/acceptance-1.1.0/research-seedance-official.md`）
- `[一手]` 导演 / 摄影师 / 剪辑师著作与访谈、语音学标准（见 `references/director-grammar.md` §十、能力表 §7）
- `[第三方]` Higgsfield、fal.ai、rundiffusion、runware、the-decoder、mindstudio 等（见 `references/source-analysis.md`）
- 分辨率按官方 API 文档：480p / 720p / 1080p，2.5 无 4k。

## 版本管理

- 语义化版本，记录在 `VERSION` 与 `CHANGELOG.md`。
- 每次改动跑 `bash tests/run_tests.sh`；GitHub Actions 在 push 与 PR 时自动跑。
- 生产/表演核心文件由 `tests/test_protected_zone.py` 哈希锁定（1.4.0 基线；历史基线 1.0.0 取自 v2.3.1）；有意变更属于独立的生产版本发布，需同步更新哈希并在 CHANGELOG 说明。

## 维护

- 模型能力更新 → 只改 `references/seedance-2.5-capabilities.md`，并保留事实标签。
- 新任务类型 → 更新对应模板与路由；脚本只增加可确定核对的契约，不通过累积情绪关键词或固定动作组合模拟语义判断。
- 校验脚本回归：`bash tests/run_tests.sh`。

## 安装

```bash
git clone https://github.com/Anelse0/film-director.git <skills目录>/film-director
```
