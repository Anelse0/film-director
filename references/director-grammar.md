# 导演语法：景别、运镜、动线与剪辑的决策规则

S5 的主参考。本文件回答的问题只有一个：**在一条 ≤30 秒、由文字（可加参考图 / 白模 / 动作视频）驱动的 Seedance 2.5 片段里，导演应当怎样决定拍谁、多近、机器动不动、人怎么走、在哪里切。** 每条规则给出：它解决什么问题 → 决策规则 → 写进 C 层长什么样 → 来源与标签。

标签：`[一手]` 实践者 / 学者本人著作或访谈原话；`[一手·摘要]` 本人原话但本次只经搜索摘要核对，未读原页；`[第三方]` 视频论文、教学站转述；`[推论]` 本 Skill 把方法转成 Seedance 写法的设计推论。来源清单在 §十。导演名字只出现在本文件与 A 层，不进 Prompt（硬规则 10）。

## 零、三个元问题（每镜先答）

Mackendrick 给导演的三问 `[一手]`（*On Film-making*，Film Grammar 部分）：

1. "If I move the camera, from whose point of view will the audience be experiencing the action?"（机器动，观众从谁的视点经历这件事？）
2. "If I use a close-up here rather than a long shot, what am I asking the audience to think about?"（用特写而不用远景，我在要求观众想什么？）
3. "If I cut here, what will be revealed to the audience, what will be left out, and how will this help tell the story?"（在这里切，观众会得到什么、失去什么？）

同书的可证伪检验：关掉对白，一部真正的电影仍应有六到八成可理解 `[一手]`。对本 Skill 的含义：**分镜卡的 A 层先写这三问的答案，C 层的景别 / 运镜 / 切点必须能指回答案**；答不上来的运镜删掉。

第二条元原则来自 Mamet `[一手]`（*On Directing Film*）："The job of the film director is to tell the story through the juxtaposition of uninflected images."——单个镜头不"演"情绪，情绪产生于镜头 A 与 B 的并置（Kuleshov 效应，Hitchcock 在 CBC 访谈中用同一张脸接婴儿与接泳装女郎做过演示 `[一手·摘要]`）。对 Seedance 的含义：**不要在一镜里堆表情词让模型"演"，把反应放进下一镜或下一节拍**。

第三条来自 Hitchcock `[一手·摘要]`（*Hitchcock/Truffaut*）："I maintained the rule of varying the size of the image in relation to its emotional importance."——画面里最大的东西必须是此刻最重要的东西。

## 一、景别（Shot Size）

| 问题 | 决策规则 | 写进 C 层 | 来源 |
|---|---|---|---|
| 这一镜该多近 | 由"此刻最重要的东西"决定，不由谁在说话决定。重要的是一把钥匙就让钥匙占满画面 | 【特写，桌上的钥匙占画面下半，手从画右入画】 | Hitchcock 尺寸规则 `[一手·摘要]` |
| 信息 vs 情绪 | 远 / 全景给空间与关系信息，近景 / 特写给情绪；不要用特写交代空间，也不要用全景要求观众读微表情 | 全景写"谁在哪、门窗在哪"；特写写"部位" | Mackendrick 第二问 `[一手]` |
| 当代默认值 | Bordwell 归纳的"强化连续性"：对话场景越框越近、剪得更快、广角与长焦两极并用、机器常动。按此拍会"像当代好莱坞"；反其道（中景、中焦、固定、长镜）读作作者电影或年代感 | 在【画面基调】声明取向，不在镜头间随机摇摆 | Bordwell 2002 *Film Quarterly* `[一手·摘要]` |
| 景别序列 | 景别本身是一条"镜头情节"。Lumet 在《十二怒汉》中让焦距随剧情从广到长、机位从高于视线降到低于视线，让房间"越来越小"，最后一个外景用全片最广镜头释放。30 秒片段也可以规划一条微型序列：开始广结束窄（压迫、逼近真相），或开始窄结束广（揭示处境、孤立） | 分镜卡头部写"景别序列：全 → 中 → 近 → 全"及理由 | Lumet *Making Movies* `[一手·摘要]` |
| 广角特写 vs 长焦特写 | 广角贴脸：把机器放进对话空间内部，脸略变形、背景空间可见，效果是同情加一点滑稽（Coen / Deakins 的正反打）；长焦特写：压缩、隔离、偷窥感。Seedance 能执行"广角 / 长焦"的可见结果 `[推论]`，写法见 `camera-vocabulary.md` §焦距 | 【近景，广角，机位贴近，背景货架可见】/【近景，长焦压缩，背景虚化成色块】 | Every Frame a Painting《Coen — Shot/Reverse Shot》`[第三方]`；Lumet 论广角"gargoyle-like"与长焦"compress space" `[一手·摘要]` |
| 推到谁的脸 | "Spielberg face"：dolly-in 到一张仰望画外的脸——从群体到个体、从客观事件到主观体验；这张脸是观众反应的替身。先给反应脸，再给（或不给）奇观 | 镜头 N：【中景缓推至近景，3 秒，止于面部近景】她抬头看向画外右上，嘴微张 → 镜头 N+1 才给她看到的东西 | Kevin B. Lee《The Spielberg Face》`[第三方]` |

**Seedance 特有约束** `[推论]`：口型在正面或 3/4 侧脸的中近景最稳（能力表 §4.8）；部位级表情只在近景 / 特写可见，全景里写"下唇内收"是浪费负载（S4 §4.4 每镜负载）。

## 二、运镜（Camera Movement）

### 2.1 动机原则

| 原则 | 原话 | 决策规则 |
|---|---|---|
| 不为有趣而动 | Deakins："When you move the camera... it's got to mean something... it's got to be for a reason within the story, and to further the story." `[一手·摘要]` | 每个运镜在 A 层写一个动机；写不出就固定机位 |
| 机器跟着人物 | Fincher 的机器"全知"而无个性："I just love the idea of this omniscience... it doesn't have any personality to it. It's very much like what's happening was doomed to happen." `[一手·摘要]`；Every Frame a Painting 归纳为"人物动机器才动，人物停机器就停" `[第三方]` | 人物走位 → 跟 / 横移 / 摇；人物静止 → 机器静止，除非有下表的内部动机 |
| 机器动等于场景不够好 | Messerschmidt（Fincher 的摄影师）："If a director feels the need to move the camera simply to 'make it interesting,' it's likely an indicator the scene itself isn't that interesting." `[一手·摘要]` | 想加运镜时先回 S3 / S4 检查这一镜有没有事件 |
| 一镜内换景别靠走位 | Spielberg 的 oner：演员走位加机器小幅移动，一个镜头完成多个构图（《第三类接触》一镜 8 种构图，《铁钩船长》35 秒 9 种） `[第三方]` | 只能一镜时，让人物从后景走到前景把中景走成近景，而不是让机器独自"表演" |

### 2.2 各运动的叙事职能与终点

写运镜必须写**动机、动作、终点**三件事（终点 = 结束时的景别与构图；官方要求起止状态 `[官方]`）。

| 运动 | 叙事职能 | 什么时候不用 | C 层写法示例 |
|---|---|---|---|
| 推（push-in / dolly-in） | 注意力收窄；人物内部发生了变化（意识到 / 决定 / 被击中）；观众主观化。**动机是"变化"不是"有情绪"**——对着一张悲伤的脸缓推而没有变化，就是 W15 拦的陈词滥调 | 人物状态持续不变时；已在特写时 | "镜头用 3 秒从中景缓推到面部近景，止于眼睛在画面上三分之一，推的过程中她的视线从桌面抬到门口" |
| 拉（pull-back / dolly-out） | 揭示环境、孤立人物、"从具体到普遍"（Kubrick《巴里·林登》慢速反向变焦把人物钉在环境里）`[第三方]` | 需要读表情时 | "镜头从手部特写用 4 秒缓拉到全景，止于她一个人站在空走廊中央" |
| 摇（pan）/ 上下摇（tilt） | 揭示（把画外之物带进画内）、跟随视线、连接两个空间 | 揭示物不重要时（摇过去什么都没有） | "第 5 秒镜头向右缓摇 2 秒，露出门口站着的第二个人，止于两人同框的中景" |
| 横移 / 跟拍（truck / track） | 陪伴（观众与人物同行）、沿路揭示；反向跟拍（人物朝镜头走、机器后退）让观众"不知目的地"而生张力（Kubrick《光荣之路》战壕）`[第三方]` | 人物不动时 | "手持跟拍，保持她在画面左三分之一，从走廊尽头走到门前停下，镜头随之停" |
| 环绕（orbit / arc） | 失衡、包围、关系翻转；Bayhem 配方：低角度加机器绕一侧、演员转向另一侧，前后景视差 `[第三方]` | 对话戏（多人口型与轴线都会乱） | "镜头以他为中心顺时针环绕四分之一圈，4 秒，从看到他的背影到看到他的正脸" |
| 升降（crane / boom） | 尺度、超越人物视点、开场或收场的"退出" | 室内小空间 | "镜头从两人的中景缓缓升起到俯视全景，止于两人在空旷广场上变成两个点" |
| 手持 | 在场感与不确定（Lubezki《人类之子》："the way you would if you were in the middle of a war with a camera on your shoulder"）`[一手·摘要]`；Chazelle 用手持表现"从现实过渡到歌"的最不确定时刻 `[一手·摘要]` | 需要观众感到"命中注定"的场景（Fincher 式全知） | "轻微手持，呼吸感晃动，中近景" |
| 甩镜（whip pan） | 高能转场、视觉喜剧的"去而复返"、把两个空间硬连在一起（Scorsese Copa 长镜、Wright）`[第三方]` | 严肃对话 | "第 8 秒快速向左甩镜，画面短暂拖影，止于门口的中景" |
| 希区柯克变焦（dolly zoom） | 现实扭曲、眩晕、认知崩塌的一瞬 | 一部片用一次以上 | "希区柯克变焦：机器后拉同时变焦推近，人物大小不变、背景被拉远" |
| 固定 | 审判、无处可逃、让持续的压力自己说话；Fincher 式全知；一场戏里"唯一一次运动"的对比基础 | 人物大幅走位需要跟随时 | "固定机位，全程不动，两人在画内走位" |

**复合运镜**：官方 2.0 指南建议一镜一种运镜；2.5 未重申。本 Skill 允许复合，但必须写清同步（"边推边升"）或先后（"先横移 3 秒，停 1 秒后缓推"）`[推论]`。

### 2.3 长镜头的理由

长镜头不是"高级"，是让观众**在场而非观看**（Lubezki）。用它的条件：空间里有可读的走位（§三）、或有一个需要不被打断的持续表演（S4 高光）。Villeneuve 拍沙虫"像用望远镜从远处看"、拒绝"artificially dynamic" `[一手·摘要]`；Fincher 与 Villeneuve 的《银翼杀手 2049》全部预先分镜、单机、无 coverage `[第三方]`——对 Seedance 的含义：长镜头必须在关键帧或白模里预先锁住构图（§七），文字驱动的 20 秒一镜到底走位是高风险项。

## 三、人物动线与调度（Blocking / Staging）

### 3.1 先写走位表，再写镜头

Spielberg 在主演化妆时用替身把整个镜头的走位、推轨速度、机高、过画时刻算好，再向演员解释"为什么你在这里动" `[第三方]`。对本 Skill：**S5 先产出走位表**（谁 / 第几秒 / 从哪到哪 / 面朝哪 / 手里什么），镜头随后从走位表推导。模板见 `shot-card.md` 的"clip 起始状态 / 结束状态"与每镜起止状态。

### 3.2 两种世界观：平面调度与纵深调度

| 调度 | 定义 | 效果 | 何时用 |
|---|---|---|---|
| 平面（planimetric） | 机器垂直于后墙，人物像晾衣绳上的衣服排成一排；配套"罗盘剪辑"只在 90° / 180° 轴向切换（Bordwell 定义 `[一手·摘要]`；Wes Anderson、Kubrick 走廊） | 秩序、童话、反讽、"从外面看一个封闭世界"；Bordwell 评 Anderson："a somewhat awkward formality" | 冷面喜剧、制度荒诞（L7）、需要几何对称的一切 |
| 纵深（staging in depth） | 人物在前 / 中 / 后景之间移动，靠遮挡与显露引导注意力（Bordwell *Figures Traced in Light* 论 Feuillade、沟口、安哲、侯孝贤 `[一手·摘要]`；Spielberg oner） | 真实、复杂、观众自己找重点 | 关系变化要不剪就讲清（L2）、一镜到底 |

Seedance 写法 `[推论]`：平面调度写"两人并排面向镜头，与后墙平行，等距"；纵深调度写"A 在前景左侧背对镜头占画面三分之一，B 在后景门口，A 向后景走去时 B 转身"。纵深调度对模型的空间一致性要求高，建议配场景空镜或白模。

### 3.3 动线语法（人怎么动就是在说什么）

| 动线 | 含义 | C 层写法 |
|---|---|---|
| 逼近 / 退让 | 权力与压力；最后一次"不退"是转折 | "A 向前一步，B 退半步；第三次 A 再上前时 B 不动" |
| 转向 / 背向 | 转向 = 接受或对峙；转身背对 = 拒绝、羞耻、结束；转身前的停顿是决定 | "她转身前停 1 秒，然后背对他走向画右" |
| 穿越画面 | 立场交换、一段关系的结束；两人擦身而过各到对方原位 | "两人从画面两侧走向中央，擦身而过，各自停在对方原来的位置" |
| 进画 / 出画 | 出画 = 离开这个世界；出画后机器停留 = 失去（Haneke 式画外，L4）；喜剧里进出画本身是笑点（Wright）`[第三方]` | "她走出画右后，镜头在空门口停 3 秒不切" |
| 坐 / 站 | 高度差 = 权力差；坐下 = 放弃或安顿；站起 = 决定 | "他站起来，比坐着的她高出一头，镜头不变" |
| 以物件为动作 | Mackendrick 区分"活动"（activity，填时间）与"行动"（action，改变处境）`[一手·摘要]`；物件动作只有在改变处境时才是行动（放下钥匙 = 决定留下） | "她把钥匙放回桌上，手离开钥匙后停在桌面 1 秒" |
| 距离作为刻度 | 一臂、半米、两步：距离数字化，变化写秒数 | "两人相距从两步缩到半米，用时 1 秒" |
| 三层运动 | Kurosawa 把运动分为自然 / 群体 / 个体 / 机器几类并让它们同时存在 `[第三方]`；每镜至少一层非人物运动（雨、风、烟、人群）作背景节拍 | "前景对话静止，后景一列人从远处走近；窗外雨" |

### 3.4 轴线（180°）的建立与合法越轴

1. 定轴：两个主体的连线（或一个人的视线方向）是轴线；机器只在轴线一侧拍，屏幕方向才稳定。
2. C 层写法：clip 头部写"轴线：A 画左、B 画右，机位在两人南侧"；每镜写画左 / 画右；物理位置与屏幕位置分开写（S5 §5.2）。
3. 合法越轴三种：**镜内越过**（机器在同一镜里绕过轴线，观众看着它过去）、**中性镜头过渡**（先切到轴线上的正面或背面镜头，再从另一侧拍）、**人物走位重画轴线**（人物移动后新轴线成立）。Coen 兄弟把机位放进对话空间内部、用单人镜头正反打，有意打破轴线时是喜剧或失衡信号 `[第三方]`。
4. Seedance 风险 `[推论]`：切镜后"人物换边"是常见失败（S7 §7.2），每镜重写画左 / 画右比写一次全局锁更有效。

### 3.5 对话调度的三种基本图形

Katz《Film Directing Shot by Shot》把对话场景的人物排布简化为 A 型（两人相对）、I 型（一前一后同向）、L 型（垂直）三种，并单列"故意打破轴线"的实验 `[一手·摘要]`。本 Skill 的 S5 §5.1e 调度模式（逼近退让、交叉、揭示、镜像、前景遮挡、背景动作、出画停留、单向长镜、几何阵列、三拍）都是这三种图形加动线语法的组合，不是独立食谱。

### 3.6 给"演员"动词，不给结果

Weston `[一手]`："Although we can't decide how to feel, we can decide what to do."——动词、事实、意象、身体任务比形容词可演。对本 Skill：A 层写意图动词（恳求、审问、无视），C 层写人物**实际做的事**（把杯子推远、目光落到门上），**不建立"恳求 = 前倾 + 伸手"的固定映射**（S4 §4.0c）。

## 四、覆盖与场内剪辑（Coverage & Editing Grammar）

| 规则 | 内容 | 对 Seedance 的含义 |
|---|---|---|
| Murch 六准则 | 情绪 51% > 故事 23% > 节奏 10% > 视线 7% > 二维平面 5% > 三维空间 4% `[一手]`（*In the Blink of an Eye*）。可证伪推论：情绪对而空间连贯错的切，好过空间对而情绪错的切 | 切点先服务情绪与故事；轴线是第五位的考虑，但对模型而言它是稳定性问题（§3.4），所以本 Skill 把它提前到 C 层必写项 `[推论]` |
| 眨眼即剪 | Huston 对 Murch："Look at that lamp across the room. Now look back at me... You blinked. Those are cuts." `[一手·摘要]`——一个思想单元结束、观众想看别处的一刻就是切点 | 镜头时长由"观众何时想看别处"决定，不按景别配秒数 |
| POV 三联 | Hitchcock 称《后窗》是"purely cinematic"：人看 → 他看到什么 → 他如何反应 `[一手·摘要]` | 反应镜头是必要的第三件事；三联可以在一镜内用摇 / 走位完成，也可以三镜 |
| 节奏的变化才被感知 | Lumet："it's the change in tempo we feel, not the tempo itself." `[一手]` | 30 秒里至少一次镜长或运动的对比（一次静止之后的运动、一串快切之后的停留） |
| 迟进早出 | Goldman："starting each scene as late as possible" `[一手·摘要]` | 片段不从开门、坐下开始；从失序事件的一刻开始，事件结束就停 |
| 动作接切 | 切在动作进行中（伸手到握住之间）比切在动作前后更隐形；官方"镜头 N（a-bs）"分段是切点声明 | "镜头 3 结束于她的手伸向钥匙；镜头 4 开始于手握住钥匙" |
| 插入与切出 | 插入（手、物件）用于转折点，不是装饰；切出（窗外、钟）是时间与画外的桥 | 每个插入镜头在 A 层写"观众此刻需要看到它因为 __" |
| 过长 | Lumet："Over-length is one of the things that most often results in the destruction of the movie in the cutting room." `[一手]` | 官方：时段内容过多会被过度剪切或遗漏 `[官方]`；两者指向同一处理：减事件，不减秒 |

Coverage（建立 → 关系 → 说话者 → 听者 → 插入 → 收束，S5 §5.3）是电视剧的安全网，不是默认；用它的理由是"多个信息点需要分别看清"，不是"有对话"。

### 4.1 镜与镜之间的变化：四个维度与峰值镜 `[一手]` + `[实测]` + `[推论]`

Lumet 的"感到的是节奏的变化"只说了镜长；Block 的对比 / 亲和律（§五）说的是画面成分。把两者合起来，一个 ≤30 秒的片段里相邻两镜可以在四个维度上不同：**景别**（Hitchcock 尺寸规则：重要的东西变大）、**机位或运镜**（§二：机器动要有动机，不动时靠其余三维）、**光**（§六：人物转身、靠近光源、走出主光区都是有动机的换光）、**动作幅度**（0 静止 / 1 部位级 / 2 头手上身一个动作 / 3 全身位移）。规则：

1. 先找**峰值**——片段里最大的物理动作或最大的信息变化（Proferes 的支点，§九 第 2 条）。峰值拿最可见的景别和这条片段首要的有动机运镜；不放全景（读不到部位），不放越肩（前景的肩吃掉幅度），不在镜头开始前做完。
2. 每一次切至少换一维；连续三镜四维都不换，观众感到的就是"同一张画面再放一遍"。
3. 镜长要有对比：最长 ≥ 2× 最短。等长的 3 秒镜序列是本 Skill 实测里被用户判"没有变化"的形态（`validation-log.md` 2026-09-20：切点逐镜跟随、口型都对，仍平）。
4. 机器不动（§2.1 Fincher 式全知）不等于画面不变——不动的机器要用景别、光、幅度和镜长补回变化；否则"人物动机器才动"和"一镜一事件"合力得到的就是等长固定机位微动作序列。

写进 C 层：每镜一条 `【变化：景别 全→近｜机位 固定→推｜光 正→侧｜幅度 1→3】`，E 层 `峰值镜 | N`（S5 §5.1f，校验 W30–W33）。

## 五、构图与镜头（Composition & Lens）

| 规则 | 内容 | C 层写法 |
|---|---|---|
| 对比 / 亲和律 | Block `[一手]`（*The Visual Story* Ch.2）："The greater the contrast in a visual component, the more the visual intensity of the picture increases; the greater the affinity, the more the visual intensity decreases."——适用于空间、线、形、影调、色、运动、节奏七个成分 | 高潮前用亲和蓄势（同色、同向、同速），高潮处切换到对比（唯一的红、唯一的逆向运动、唯一的静止） |
| 一点透视 / 对称 | 权威、秩序、被观看；Kubrick 的威压与 Anderson 的冷面是同一构图的两种用法 `[第三方]` | "走廊一点透视，消失点在画面正中，人物在中轴线上向镜头走来" |
| 焦距即心理 | 广角：空间、畸变、把人和环境绑在一起；长焦：压缩、隔离、偷窥；当代惯例两极并用（Bordwell） | 见 `camera-vocabulary.md` §焦距 |
| 前景层次 | 前景遮挡（门框、肩膀、货架）= 偷看 / 隐忍；前景物件占画面 = 它比人重要（Hitchcock 尺寸规则） | "前景是 A 的后背肩膀，占画面左三分之一，焦点在 B 的面部" |
| 视线空间 / 头部空间 | 人物看向的一侧留空间 = 稳定；反向留空 = 不安、有东西在背后 | "她在画面右三分之一，看向画左，左侧留空" |
| 负空间 / 尺度 | 人物在大空间里的渺小（Villeneuve 的"保持距离"）| "大远景，人物只占画面高度十分之一，站在画面下三分之一" |
| 机高 | 高于视线 → 俯视、审判、渺小；平视 → 对等；低于视线 → 威压、英雄（Bayhem 低角度 + 环绕）；Lumet 的机高随剧情从高到低 | "机位低于她的视线，略仰" |

## 六、光与色作为导演决定

- Storaro 自称"a writer of light"，主张研究光与色的象征、生理与戏剧功能后"像音乐家用音符一样使用" `[一手·摘要]`。
- Mann / Spinotti 拍《盗火线》：照亮区域而非镜头，为多机位与剪辑动态服务 `[一手]`（ASC "Hot Set: Shooting Heat"）。
- Zhao / Richards 拍《无依之地》：几乎全自然光，日程围绕 magic hour 的 20 分钟窗口安排 `[一手]`。
- Gerwig / Levy 拍《伯德小姐》：画质设计成"a memory — the viewer should be slightly removed from the image"，参考物是彩色复印件的褪色质感；Levy 的告诫："If you want that melodramatic shaft of light, you'd better mean it" `[一手·摘要]`。
- 对本 Skill：每个 clip 在【画面基调】声明**一个主光方向与动机光源**（窗 / 灯 / 火），说明高调或低调；同一场景内不无动机换光；"黄金时刻逆光"是 W15 拦的默认美学，用它要有理由。

## 七、把导演决策交给合适的载体（Seedance 2.5 特有）

模型的价值主张是多素材参考（能力表 §2）。导演决策不必全靠文字：

| 决策 | 文字能承载吗 | 更稳的载体 | 依据 |
|---|---|---|---|
| 景别、角度、单一运镜、起止状态 | 能 | 文字 | 官方通识术语可直写 `[官方]` |
| 精确构图（一点透视、前景层次、人物在画面的位置） | 勉强 | **关键帧图**（相对严格对齐）`[官方]`：每镜一张，首句"以图片 1 至图片 N 的顺序作为关键帧" | 能力表 §2 |
| 复杂走位与机器运动的时序（一镜到底、纵深调度、环绕） | 弱 | **粗粒度白模视频**：简单几何体表示人物，含切镜 / 运镜 / 光照；"白模视频仅作为运镜、镜头运动和角色动画参考，不参考画面内容" `[官方]` | PDF p.14–15 案例 |
| 具体动作与节奏（打斗、舞蹈、手部动作） | 弱 | **动作参考视频**："严格参考视频 1 的动作与运镜，顺序一致"，不复述 `[官方]` | 能力表 §4.2 |
| 整体镜头结构与顺序（不要求精确构图） | 能 | **线稿宫格分镜**（≤15 格，不严格对齐）`[官方]` | 能力表 §2 |
| 角色外观、场景光与陈设 | 弱（跨 clip 漂移） | 主体图 + 场景空镜 | S5b |

S5 的新步骤 **5.0 决策载体**：每场戏的视觉方案里写明哪些决策靠文字、哪些靠图 / 白模 / 视频；S5b 据此列资产。文字驱动的一镜到底纵深走位是高风险项，关键帧或白模是它的正确载体 `[推论]`。

## 八、类型专用语法

### 8.1 悬念：先告诉观众

Hitchcock `[一手]`："In the first case, we have given the public fifteen seconds of surprise at the moment of the explosion. In the second we have provided them with fifteen minutes of suspense... whenever possible the public must be informed."——片段的前 1–3 秒交代威胁与时钟（桌下的炸弹、包里的车票），其后所有平淡对话自动变成悬念（L1 信息差）。Mackendrick 的戏剧反讽定义："a situation where one or more of the characters on the screen is ignorant of the circumstances known to us in the audience." `[一手·摘要]`

C 层：镜头 1 给观众威胁的插入镜头（观众视点），之后的镜头里人物看不见它但它在画内（前景或背景），每镜写它在哪。

### 8.2 视觉喜剧：Wright 工具箱

Every Frame a Painting《How to Do Visual Comedy》转录中可确认的条目 `[第三方]`：以有趣的方式进画；以有趣的方式出画；匹配转场；精确到帧的音效；动作与音乐同步；戏剧化的灯光提示。批评对象："everyone stands still and talks at each other in close up. Almost none of these jokes come visually."——笑点来自画面而非台词。甩镜、急推变焦、匹配剪辑是实现手段。

C 层：把笑点写成可见事件（进出画的时机、音效落在哪个动作上），三拍（看见 → 关上 → 再关一层）是选项不是配额（L9）。

### 8.3 动作：地理清晰优先于冲击力

- Jackie Chan 九原则（EFAP 转述）`[第三方]`：从劣势开始；利用环境；镜头清楚；动作与反应同框；拍到够为止；让观众感到节奏；两次好击中等于一次伟大击中；疼痛让人物可信。
- Mann《盗火线》街头枪战"arose out of choreography"，像排音乐剧一样让每个枪手知道每一刻在哪，按 1:1 复刻街道排练，用现场原声 `[第三方]`。
- Bayhem 的反面：模仿者失败在没有尺度、视差与地理 `[第三方]`。

C 层：先一镜全景建立地理（起点、障碍、终点各一个可见地标，S5 §5.10）；攻与受尽量同框；切点落在击中而非挥出；每镜写两人相对位置与方向；快动作与快切分别登记风险（能力表 §4.6：模型弱项是复杂运动的物理合理性）。

### 8.4 封闭空间的对话悬念

Tarantino《无耻混蛋》酒馆戏：狭小空间、多语言、"谁在撒谎"的语言游戏，让观众"别无选择只能看和听" `[第三方]`；Ramsay《你从未在此》："physical action plays off-screen"，脸在画内 `[第三方]`。对 Seedance：把暴力放画外、把听者的脸放画内，是同时降低执行风险与提高张力的一种选择（L4），不是回避用户要验证的高光。

### 8.5 暧昧 / 爱情：把欲望压到只剩一个泄漏点

"高级"的浪漫不是更美的光，而是**导演替观众省略了什么**。十条机制（来源见 §十 "暧昧 / 爱情"行；两条为已读原文的一手，其余经搜索摘要核对，标 `[一手·摘要]` / `[第三方]`）：

| # | 机制 | 为什么读起来克制而强烈 | 写进 C 层 | 依据 |
|---|---|---|---|---|
| 1 | 错位的注视 | 两人轮流看对方，总有一方在对方看过来时移开；观众自己完成"他在看她"的推断 | "A 转头看 B（2 秒），B 转过来时 A 已看回前方；B 看 A（3 秒），A 转回时 B 低头" | Linklater《爱在黎明破晓前》听歌亭 `[第三方]` |
| 2 | 对等的凝视 | 不设"看的人"与"被看的物"；两人的景别、机高、镜头时长完全对称 | 正反打各 5 秒同景别；或一个平齐双人镜头，眼线同高 | Sciamma："They have the same age and height – that is so important in cinema!"；"The model and the artist are co-creators." `[一手]` |
| 3 | 隔着东西看 | 玻璃、雨、倒影、门框、走廊把人物放进第二层框；物理阻隔外化心理阻隔，观众被放到偷看的位置 | "长焦隔着车窗拍，前景有雨痕反光，人物只占画面右下三分之一" | Lachman《卡罗尔》："seeing them through glass, objects, reflections"；"shards of emotion… without giving certain content" `[一手]`；《花样年华》"every shot is a frame within a frame" `[第三方]` |
| 4 | 关上的门 | 最重要的动作（吻、告白）放在画外或永远不发生；观众自己加二加二 | 拍门、拍走廊、拍事后一个人的脸；拍"演练"不拍"正戏" | Lubitsch touch（Wilder："more with a closed door…"）`[一手·摘要]`；《迷失东京》耳语留空 `[一手·摘要]` |
| 5 | 身体先于头脑 | 接触极短（递物、扶手、肩上停留一秒），戏在接触之后的身体反应；礼仪把欲望压到一个泄漏点 | "递烟时手指碰到，停 1 秒；切到手的特写：手指在栏杆上收紧又松开"，不切脸 | Joe Wright《傲慢与偏见》手部一抖："our bodies know best" `[一手·摘要]` |
| 6 | 音乐禁令 | 配乐替观众感动是作弊；无声让观众读脸，音乐只在挣得的一刻进入且是画内音源 | 【贯穿要求】无 bgm；若有歌，写"唱片机 / 耳机 / 街头琴声"并给进入秒数 | Sciamma："making a love story without a score is pretty challenging"；音乐一来"how precious it is" `[一手·摘要]` |
| 7 | 距离与单一焦距 | 一只标准镜头、旁观者距离、不推近；亲密来自两人间距的变化，不来自变焦 | "全程 35mm 等效、固定机位；两人从画面两端各自做事，一方走到另一方同侧" | Mukdeeprom《请以你的名字呼唤我》："tie my hand to this approach"、"the sense of the human eye" `[一手·摘要]` |
| 8 | 直视镜头 | 关键一刻让人物看向镜头轴线（观众 = 对方），只用一次 | "A 的近景眼线正对镜头 2 秒，手里继续点烟" | Jenkins《月光男孩》餐馆戏："right into the lens" `[一手·摘要]` |
| 9 | 时间的手感 | 慢放 / 重复用在日常动作（擦肩、下楼）而非高潮；同一构图出现两次，第二次多一个眼神 | "同一走廊构图第二次出现，这次她回了头"；抽帧慢放只给腰部以下或背影 | 《花样年华》抽帧与重复 `[第三方]` |
| 10 | 不切 | 场景内不剪，让间距、朝向、停顿在实时里变化；剪辑是替观众指，不剪是交出判断权 | "单镜 20 秒：并肩坐不对视，间距从一臂到半臂，一人起身出画，留下另一人的脸" | Haigh《周末》场景内不剪 `[一手·摘要]`；《请以你的名字呼唤我》壁炉长镜 `[第三方]` |

**廉价的来源**（反向检查）：管弦乐向初吻推进；切得太碎；一上来就特写（没有距离可缩短）；用台词解释感情；把高潮拍成高潮；配偶 / 第三者露正脸；无理由的黄金时刻逆光；不对等的凝视（一方始终是被拍的物）。一条 30 秒片段最多叠三条机制，超过就变成技巧展示 `[推论]`。

## 九、给 ≤30 秒片段的十一条推导规则 `[推论]`

1. 先写走位表，再写镜头（§3.1）。
2. 一个片段一个戏剧块、一个支点（人物可能转向的时刻，Proferes 的 fulcrum `[一手·摘要]`）；机器的每次"揭示"对准支点。
3. 画面里最大的东西必须是此刻最重要的东西（§零）。
4. 机器只在人物动或人物内部变化时动；动就写动机、动作、终点（§二）。
5. 只能一镜时，用人物走位换景别，不让机器独舞（§2.1）。
6. 悬念片段：前 3 秒交代威胁与时钟（§8.1）。
7. 动作片段：先全景建立地理，攻受同框，切在击中（§8.3）。
8. 喜剧片段：笑点来自进出画、同步音效、匹配转场，而非台词（§8.2）。
9. 情绪靠相邻镜头并置产生，不靠单镜堆表情词（§零）。
10. 声明主光方向与动机光源；同场景内不无故换光（§六）。
11. 先定峰值镜（最可见景别 + 首要的有动机运镜），再让每一次切至少换一维（景别 / 机位 / 光 / 幅度），镜长最长 ≥ 2× 最短（§4.1）。

## 十、来源与核实状态（2026-09-17）

| 来源 | 定位 | 核实状态 |
|---|---|---|
| Alexander Mackendrick, *On Film-making*（Faber 2004），Film Grammar / Dramatic irony / Activity vs action | 三问、六到八成检验、戏剧反讽定义 | 摘录页 https://www.thestickingplace.com/alexander-mackendrick/ 已读 |
| David Mamet, *On Directing Film*（1991） | 未加修饰镜头的并置 | 摘录 https://castig.org/on-directing-film-by-david-mamet/ 已读 |
| Hitchcock / Truffaut, *Hitchcock*（1966） | 尺寸规则、炸弹与悬念、《后窗》三联 | 悬念段 https://nofilmschool.com/alfred-hitchcock-and-francois-truffaut-explain-surprise-vs-suspense 已读；尺寸规则与《后窗》为搜索摘要 |
| Sidney Lumet, *Making Movies*（1995） | 镜头情节、节奏变化、过长、广角 / 长焦 | 语录页 https://azevedosreviews.wordpress.com/2013/08/07/sidney-lumets-20-quotes-on-film/ 与 https://www.studiobinder.com/blog/making-movies-sidney-lumet/ 已读；《十二怒汉》数值为转引 |
| Walter Murch, *In the Blink of an Eye*（2nd ed. 2001） | 六准则权重、眨眼即剪 | https://www.studiobinder.com/blog/walter-murch-rule-of-six/ 搜索摘要；权重数字为原书内容 |
| David Bordwell, "Intensified Continuity" *Film Quarterly* 55(3) 2002；"Shot-consciousness" 博客 2007；*Figures Traced in Light*（2005） | 强化连续性四特征、平面调度定义、纵深调度 | 搜索摘要；davidbordwell.net 本次被拦截 |
| Bruce Block, *The Visual Story*（3rd ed.）Ch.2 | 对比 / 亲和律 | https://www.taylorfrancis.com/chapters/mono/10.4324/9781315794839-2/ 摘要 |
| Steven D. Katz, *Film Directing Shot by Shot*（1991） | A / I / L 型对话排布、轴线实验 | 搜索摘要 |
| Nicholas Proferes, *Film Directing Fundamentals*（4th ed.） | 摄影机作为叙述者、戏剧块、支点 | https://www.oreilly.com/library/view/film-directing-fundamentals/9781351683111/ 目录 |
| Judith Weston, *Directing Actors*（1996） | 动词不给结果 | https://kortina.nyc/notes/directing-actors/ 摘录 |
| Roger Deakins, Hazlitt 访谈 "If the Camera Moves it's Got To Be for a Reason" | 动机原则 | 搜索摘要 |
| Erik Messerschmidt, Filmmaker Magazine（Mindhunter S2） | 机器动等于场景不够好 | 标题已核 |
| David Fincher 访谈汇编 https://www.studiobinder.com/blog/david-fincher-interview-directing/ | 全知机器、Steadicam | 搜索摘要 |
| Emmanuel Lubezki, Variety 2007（*Children of Men*） | 在场感 | 搜索摘要 |
| Denis Villeneuve × del Toro, Interview Magazine（*Dune*） | 保持距离 | 搜索摘要 |
| Dante Spinotti / Michael Mann, ASC "Hot Set: Shooting Heat" https://theasc.com/article/hot-set-shooting-heat/ | 照亮区域、枪战排练 | 已读 |
| Joshua James Richards, Variety 2020（*Nomadland*） | magic hour | 已读（摘要页） |
| Greta Gerwig / Sam Levy, IndieWire 2017、Filmmaker Magazine | 记忆画质 | 搜索摘要 |
| Christopher Nolan, Gulf News（*Dunkirk*） | 交叉剪辑节奏 | 搜索摘要 |
| Every Frame a Painting：Spielberg Oner（2014）、Fincher（2014）、Kurosawa Composing Movement（2015）、Coen Shot/Reverse Shot（2016）、Edgar Wright Visual Comedy（2014）、Jackie Chan（2014）、Bayhem（2014） | 视频论文 | Wright 转录 https://gotranscript.com/public/exploring-edgar-wrights-visual-comedy-a-masterclass-in-filmmaking 已读；Spielberg oner 拆解 https://viewinder.com/spielberg-oner/ 已读；其余搜索摘要 |
| Kevin B. Lee, *The Spielberg Face*（Fandor 2011）；Slate 评论 | 推到观看者的脸 | https://slate.com/culture/2011/12/the-spielberg-face-a-brilliant-video-essay-by-kevin-b-lee.html 摘要 |
| William Goldman（转引） | 迟进早出 | 搜索摘要 |
| StudioBinder camera-movements 页 | 各运动职能汇总 | `[第三方]` |
| 暧昧 / 爱情：Céline Sciamma, BFI Sight & Sound 专访 https://www.bfi.org.uk/sight-and-sound/interviews/no-mans-land-celine-sciamma-portrait-lady-fire | 对等凝视、co-creators、无配乐 | 已读 |
| 暧昧 / 爱情：Ed Lachman, The Film Stage 专访（*Carol*） https://thefilmstage.com/ed-lachman-discusses-the-cinematic-language-of-carol-and-capturing-a-womans-point-of-view/ | 隔玻璃 / 倒影、shards of emotion | 已读 |
| 暧昧 / 爱情：Sciamma Film Comment；Joe Wright IndieWire（hand flex）；Coppola i-D（耳语）；Jenkins Deadline（餐馆戏）；Mukdeeprom CineD / Cooke（单一 35mm）；Haigh Criterion（不剪）；Wilder 论 Lubitsch；Linklater 听歌亭（Far Out / Criterion）；Nerdwriter《花样年华》框中框 | 其余八条机制 | 搜索摘要 `[一手·摘要]` / `[第三方]`；详见 `../tests/acceptance-1.1.0/research-romance.md` |

**未能核实、本文件不引用**：Spielberg "the third eye"；Kubrick "the first idea is usually the worst"；Kurosawa "never avert one's eyes"；Lumet《城市王子》的具体焦距数值；Bresson《电影书写札记》原文（只有搜索摘要）。用户指定某位导演时，按所问手法补查其访谈或原著，不凭本表泛化。
