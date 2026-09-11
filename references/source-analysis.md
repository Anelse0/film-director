# 资源分析与研究记录

初始分析2026-09-04，纠偏2026-09-05。本文件是来源账本，生成流程不读它；现行约束以能力表和 production-workflow.md 为准。下列旧研究条目不是逐条第一手核实记录，不再用来生成导演硬规则。

## 资源一：Higgsfield《Seedance 2.5 Prompting Guide》

- URL：https://higgsfield.ai/blog/seedance-2-5-prompting-guide
- 性质：第三方平台博客（英文），面向该平台用户。
- 作用：提供一种"整块文本、九段标签"的 Prompt 结构和 8 个题材范本（戏剧外景 / 动作 / 商业产品 / 史诗风景 / 黑色电影 / 多角色 / 奇幻动作 / UGC 广告）。
- 可复用内容：
  - 九段结构：GLOBAL STYLE → SCENE → CHARACTERS → LOCATION → FIRST FRAME AND BLOCKING → Shot 1…N（每镜以 Hard cut 结束）→ OPTICS AND CAMERA → PHYSICS → LIGHTING / AUDIO。
  - "漏掉一段会以可预测的方式失败"；"地点写模糊是多镜序列漂移的最常见原因"。
  - 起始帧与站位锁定（谁在哪、面朝哪），甚至用画面百分比定位。
  - 连续性锁：地理关系逐镜保持、屏幕方向不翻转。
  - 光源哲学：一个真实光源；避免默认好莱坞黄金时刻。
  - 剪辑纪律：只用硬切，切点落在动作或对白节拍上。
  - 台词写法："exactly two scripted spoken lines, nothing else spoken"；"speaks on camera with accurate lip-sync"；"All speech ends by 25s"。
- 声称的参数：1080p、30s、9:16 到 21:9、50 个参考。→ 均标 `[第三方]`。
- 局限：不用 @image 编号语法（与官方相反）；范本大量使用画面负向词（No logos, no text）；有一个 24 快切范例与评测"抗拒快切"冲突；参数未标出处。

## 资源二：火山方舟《Doubao Seedance 2.5 提示词指南》（PDF，41物理页／38页正文编号）

- 路径：`/Users/leo/Downloads/火山方舟_Doubao Seedance 2.5 提示词指南_1786425487 (1).pdf`；初版参考过转写；2.3.1 直接复读PDF相关规则及范例，对照其正文页码。
- 性质：官方第一手文档。
- 作用：定义任务类型、锁定规则、素材上限、Prompt 结构、时间戳与负向控制规则，并给出白模 / 宫格分镜 / 关键帧 / 编辑 / 延长 / 一键成片 / 无缝转场 8 个案例。
- 可复用内容：已全部结构化进 `seedance-2.5-capabilities.md` §2–§4。最关键的三条：
  1. 有锁定 / 无锁定 决定 ratio、duration 参数与 content.role。
  2. 素材按上传顺序编号绑定，不靠图片内文字。
  3. 指南明确支持字幕/音频负向；不能推导为不支持其他负向。
- 官方范例揭示的写法：`台词 (角色): "…"` 逐镜绑定；镜头段落用【景别 运镜 构图】方括号开头；【严格排除】段（宫格案例中的画面排除说明“仅声音可负向”的旧推断不成立）。
- 缺口：文中"主体/运动/音频/风格参考的使用方式与 Seedance 2.0 一致，可以参考 附录：提示词案例"——该附录不在本文档内（在 2.0 指南里）。因此 R2V 基础参考（单主体图参考、动作参考）的官方范例缺失，本 Skill 用 §4.2 的规则 + 第三方范例补齐，标注来源。
- 另一个缺口：文中推荐安装官方 `sd25-pe` skill（`npx skills add …`），本 Skill 未获取其内容，不假设其规则。

## 两份资源的关系

| 维度 | 资源一（Higgsfield） | 资源二（官方） | 本 Skill 的处理 |
|---|---|---|---|
| Prompt 结构 | 九段标签整块 | 素材指代 → 概述 → 情节（镜头 N / 时间戳）→ 贯穿细节 | 以官方四段为骨架，把九段中"起始站位 / 光学 / 物理 / 光源"并入"概述"和"贯穿细节"，"Shot N + Hard cut"用官方"镜头 N（a-bs）"表达 |
| 素材指代 | 描述性 | 编号绑定 | 编号绑定（官方） |
| 负向描述 | 使用画面负向 | 明确支持字幕/音频，范例也有风格排除 | 正向清楚描述优先；按意图补排除，不设白名单或执行保证 |
| 切镜密度 | 有快切范例 | 未规定统一镜数 | 按内容承载估时，风险需成片验证 |
| 台词 | 引号 + 时间点 | `台词 (角色): "…"` | 合并：说话人 + 引号 + 时间窗 + 语言 + 非说话时嘴部状态 |
| 参数 | 1080p 等 | 不谈分辨率 | 分辨率标"不统一" |

可保留：起始状态、空间、光源与音效的明确描述。单一运镜、单一光源和只用硬切均不是通用能力限制。

## 外部研究（核实 Seedance 2.5）

| 来源 | 类型 | 采纳内容 |
|---|---|---|
| 搜狐 / 七牛 / 知乎 / CSDN 转载的发布稿 | 媒体 | 2026-06-23 展示、07-31 上线；30s、50 素材、10 余语言（与官方一致）；"原生 4K"（与其它来源冲突，不采纳为事实） |
| the-decoder | 媒体 | 30 图 / 10 视频 / 10 音频；音画一次生成；可多次延长 |
| fal.ai 指南 | 平台实践 | 因果先后、遮挡连续性、一素材一职责、台词时间窗、末帧续接、单变量迭代；T2V 4–30s；480p/720p |
| rundiffusion 指南 | 平台实践 | 主体→动作→镜头→风格；空泛形容词黑名单；故障对照表；人物审核限制 |
| runware / renderforest | 平台文档 | 台词加引号即生成口型与配音；在 Prompt 中点名语言 |
| mindstudio / novoads 评测 | 评测 | 快动作形变；文字渲染只"减少"；2.5 抗拒快切；Prompt 更长更结构化 |
| cutout.pro 2.0 音频指南 | 经验 | 2.0 技术报告承认多人口型同步未解决 |

## 外部研究（导演 / 分镜 / 台词方法）

采纳的通用方法（行业常识，不单独标注出处）：

- 场景单元 = 目标（objective）+ 阻力（obstacle）+ 策略（tactic）+ 转折（turn）；节拍四步：尝试 → 受阻 → 调整 → 代价。
- Show don't tell：情绪由动作、视觉与潜台词传达。"John 很紧张" → "John 摆弄衣领，瞟向门口"。
- 潜台词成立的三个条件：隐藏的欲望、阻止直说的压力、观众已知真实赌注。
- 台词：短、可说出口、每句有目的；回答"没被问的问题"；沉默是台词。
- 分镜：先定轴线与视线，再定景别阶梯（建立 → 关系 → 反应 → 细节），运镜必须有动机（信息、关系、空间或视点变化）。

## 外部研究（导演方法，2026-09-04 二次调研）

用于 `director-lenses.md`。全部为方法层面引用，标 `[第三方]`；转成 Seedance 可观察量的写法为本 Skill `[推论]`。

| 导演 / 作者 | 采纳的方法 | 来源类型 |
|---|---|---|
| Hitchcock | 悬念 vs 惊讶：桌下的炸弹；"只要有可能就让观众知道" | Hitchcock/Truffaut 访谈转述（nofilmschool、faroutmagazine） |
| Spielberg | 纵深调度 oner：摇、移、走位、焦点转移在一镜内完成多个构图；调度即潜台词 | studiobinder、nofilmschool 对 Hook / Jurassic Park / Close Encounters 的拆解 |
| Fincher | 镜头不动除非有角色理由；剪掉一切分散注意力的东西 | 访谈与评论（thefincheranalyst、nofilmschool、premiumbeat） |
| Haneke | 暴力在画外，声音承担事件；长静止镜头给观众"思考空间" | sensesofcinema、Criterion 论 Funny Games |
| Cuarón | 实时长镜头，危险从背景进入前景 | ASC、johnaugust、nofilmschool 论 Children of Men |
| Villeneuve | 尺度压缩人物 + 沉默特写停留 | talkhouse 视频论文、filmlifestyle |
| Lanthimos | 全景、几何阵列、冷面念白 | indiewire 访谈、birthmoviesdeath |
| Coen 兄弟 | 期待与结果的落差；反应比事件小一号 | 学术与评论（tandfonline、rogerebert） |
| Edgar Wright | 视觉喜剧：去而复返三拍、擦画转场、动作配音效 | 《How to Do Visual Comedy》视频论文及多篇拆解 |
| Lumet | "这片子讲什么"一句话裁决所有部门决定 | 《Making Movies》 |
| Mamet | 从目标推镜头表；无表情镜头并置产生意义 | 《On Directing Film》 |
| Weston | 给演员动词不给结果 | 《Directing Actors》 |
| Murch | 剪辑六律：情绪 > 故事 > 节奏 > 视线 > 2D > 3D | 《In the Blink of an Eye》 |
| Scorsese / Bergman | 视点归属；主观镜头；两张脸 | 通识 |

设计决定：不把这些做成"风格预设"，而做成"透镜 = 它回答的问题 + 误用信号"，用上下文审阅防止套用，不能以配额或词频裁决。2.3.1 保留方法 IDs、去掉未经第一手核实的作者硬性归属；具体导演请求需读取其访谈或作品材料。

## 2.0.0 调研（2026-09-11）：一手来源，仅读摘要

本轮按用户要求只用搜索、不抓取全文，因此每条只收录搜索摘要中直接出现的说法，标 `[一手·摘要]`；按用户约定，未通读原文的链接不得标"已读"。提炼结果写在 `director-craft.md`（导演 / 摄影 / 剪辑）与 `performance-grammar.md`（表演）。来源清单：

| 作者 / 机构 | 材料 | 采纳要点 | 去处 |
|---|---|---|---|
| Hitchcock（Truffaut 访谈；1964 CBC《Telescope》） | https://thequietus.com/culture/film/hitchcock-truffaut-article/ · https://www.openculture.com/2012/05/alfred_hitchcock_on_the_essential_filmmakers_tool_the_great_kuleshov_effect.html | "影像尺寸随情绪重要性变化"；用自己的脸演示 Kuleshov，"纯电影 = 胶片的组装" | craft A、B |
| Pudovkin 记述 Kuleshov 实验 | https://en.wikipedia.org/wiki/Kuleshov_effect（转述 Pudovkin） | 同一张脸接汤 / 棺材 / 女人，观众读出三种情绪并称赞表演 | craft B、grammar §8 |
| Lumet《Making Movies》 | https://www.bfi.org.uk/features/how-12-angry-men-works-25-frames/ · https://www.rogerebert.com/reviews/great-movie-12-angry-men-1957 | 《十二怒汉》焦距 28–40 → 50 → 75 → 100mm；机位高 → 平 → 低 | craft E、stage-5 §5.11 |
| Murch《In the Blink of an Eye》 | https://www.provideocoalition.com/aotc-murch-books/ · https://www.lrb.co.uk/the-paper/v47/n19/john-lahr/every-blink | 六律权重 51/23/10/7/5/4，从底放弃；眨眼 = 思想完成 = 切点 | craft C、grammar §8 |
| Ekman（Paul Ekman Group） | https://www.paulekman.com/blog/fake-smile-or-genuine-smile/ · https://www.paulekman.com/resources/micro-expressions/ · https://www.paulekman.com/blog/my-six-discoveries/ | Duchenne 眼轮匝肌；reliable facial expressions；微表情 1/25–1/2 s；leakage | grammar §2、§4、§7；索引 hinge |
| Caine（BBC 1987 表演课；《Acting in Film》） | https://www.backstage.com/magazine/article/watch-hour-acting-advice-masterful-michael-caine-5422/ | 特写里不眨眼更强；盯对方一只眼；少即是多 | craft J、grammar §7 |
| Weston《Directing Actors》 | https://books.google.com/books/about/Directing_Actors.html?id=p6hiAAAAMAAJ（摘要经 scriptreader.ai 等转述） | 动作动词、结果导向指导、as-if 调整 | craft J、stage-4 §4.0c 依据 |
| Bergman | https://www.bfi.org.uk/features/ingmar-bergman-faces-close-ups · https://www.ingmarbergman.se/en/production/each-film-my-last | "我们的工作从人脸开始"；特写是电影摄影的顶点 | craft A |
| Deakins | https://www.rogerdeakins.com/forums/topic/lighting/ · https://www.theparisreview.org/blog/2017/05/09/master-light/ | 动机光源、单一实用光源 | craft F |
| ASC Shot Craft | https://theasc.com/article/shot-craft-where-do-you-put-the-camera/ · https://theasc.com/article/shot-craft-light-quality-101/ | 视线 = 180 度线，越近越亲密；机位高低相对视线；block-light-rehearse-shoot | craft G |
| Fincher / Messerschmidt | https://filmmakermagazine.com/108283-erik-messerschmidt-mindhunter-season-two/ · https://nofilmschool.com/2017/10/watch-david-fincher-camera-movement-characters | 镜头跟人物行为，"行为是一切"；为有趣而动镜头说明戏不有趣 | craft D、J |
| Kubrick（Ciment 访谈，Kubrick Site） | http://www.visual-memory.co.uk/amk/doc/interview.html | 排练时不想镜头；运动是电影语法基本元素 | craft D |
| Cuarón / Lubezki（ASC） | https://theasc.com/article/children-of-men-humanitys-last-hope/ | 长镜更沉浸；手持有时自走不跟演员 | craft D |
| Villeneuve（DGA 问答） | https://www.dga.org/Events/2024/May2024/DunePartTwo_QnA_0324 | 大远景 + 大特写以贴近人物内心 | craft A |
| Haneke | https://www.ioncinema.com/news/uncategorized/interview-michael-haneke-funny-games-u-s · https://www.fangoria.com/exclusive-interview-michael-haneke-on-revisiting-his-anti-horror-film-funny-games/ | 暴力在画外、靠声音；反恐怖片 | craft H |
| Nolan（DGA Quarterly 2012） | https://www.dga.org/craft/dgaq/issues/1202-spring-2012/dga-interview-christopher-nolan | 平行动作 / 交叉剪辑；拍得省、剪辑选择多 | craft M |
| Lanthimos（BFI / ASC） | https://www.bfi.org.uk/interviews/yorgos-lanthimos-screen-talk-poor-things-bugonia · https://theasc.com/article/life-anew-poor-things/ | 不拍常规正反打；10mm 广角 | craft L |
| Coen / Deakins（ASC《Fargo》） | https://theasc.com/article/fargo-cold-blooded-scheming/ | 分镜是出发点，现场可扔 | craft L |
| Tarkovsky《雕刻时光》 | https://offscreen.com/view/tarkovsky1 | 时间压力；节奏不由镜长决定 | craft I、stage-5 §5.1c |
| DGA Shot to Remember：Jenkins / Sonnenfeld / Payne / Spielberg | https://www.dga.org/news/guild-news/2026/craftarticles/0526-shot2remember-wonderwoman · https://www.dga.org/craft/dgaq/issues/1902-spring-2019/shot-to-remember-men-in-black · https://www.dga.org/News/Guild-News/2025/December2025/1225-Shot2Remember-SIDEWAYS · https://www.dga.org/craft/dgaq/issues/1103-fall-2011/shot-to-remember-saving-private-ryan | 背景反应赋予地位；特写杀喜剧；150mm 特写靠表演；手持 + 震动匹配 Capa | craft A、K |
| 火山方舟 2.5 指南（PDF 逐页复读） | 用户提供的 PDF | §4.9 官方案例写法；白模 / 表情参考；相对时间 | capabilities、stage-5/5b/6 |
| 火山方舟 2.0 指南（附录位置） | https://docs.volcengine.com/docs/82379/2222480 | 仅确认附录所在，未读内容 | capabilities §4.9 缺口 |

未采纳：Edgar Wright 的《How to Do Visual Comedy》为第三方视频论文（Tony Zhou），非导演本人材料，L9 维持既有 `[第三方]` 标注；Spielberg 关于纵深调度的 DGA 访谈摘要未含具体说法，L2 不再以其姓名归因。
