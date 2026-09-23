# EP03 场 04〈周一之前〉· 场级导演方案（S5 plan）

2026-09-23 · film-director 1.4.0 · 剧本源：[03_script/scene-04.md](../03_script/scene-04.md)（**v4.1，2026-09-23 采用，生产锁定**：过线后换到牛棚；保留"队伍跑进太阳"；含棒球逻辑微调 "One bounce, he's on third. One fly ball, he scores."）· 语速 4 词/秒（用户定）· 资产（用户 2026-09-23 提供）：@01_Sharks_field 球场参考；@01_bullpen_field、@02_bullpen_field 牛棚参考；@01_Sharks_outfit 全员队服；@girl_uniform02 女生校服（Tess）· 状态：S5 三条分镜卡 + S5b 资产追加，**停靠等用户确认**；Prompt 未编译。v3 方案（Diego↔Isa 两条 clip）已被本版覆盖。

生产原则同场 1–3：无画外句、同框、一段对话一个跟拍长镜承载但切点落在信息变化处；每条一个峰值镜；镜长对比 ≥2×。**clip01 镜 1 按用户指定的侧跟拍**（见下）。

## 场景参数卡（回显）

强度 中→高（冲刺）· 方向 外放（当众点名、冲刺）→ 内收（Isa 看板）· 信息 新（先发的路与条件第一次当面给 Isa）· 权力 Beckett 在上 → 对等（Isa 冲刺赢）· 进场温度 凉 · 密度 中高（142 词 ≈ 35.5 s；三条 51%／80%／7%）

## 视觉方案

- **观众问题**：Isa 会为 Game One 低头吗。
- **主控意象：并排与领先。** clip01–02 两人始终并排（谈判）；clip03 冲刺里 Isa 领先一个身位（他的回答）。镜头跟着这个关系：并排时跟拍保持两人同框（侧、前、后、斜前四种位置轮换），冲刺时侧跟拍加速、看他一点点压过去。
- **clip01 镜 1 摄影（用户 2026-09-23 指定，只用于镜 1）**：Camera: side tracking shot. Movement: move parallel beside the subject along their direction of travel. Speed: match the subject's motion. Framing: keep the subject in side profile or three-quarter profile at a stable distance. End: continue the parallel movement with clear horizontal motion. ——clip01 其余三镜：镜 2 低机位反向跟移（Isa 朝镜头冲来越过 Cole，峰值）、镜 3 身后跟拍（逆光轮廓、前方是太阳）、镜 4 手持斜前跟拍（Isa 三分之二正面）。
- **clip02**：正面反向跟移的正反打（Beckett 条件 → Isa 说出怕，缓推，峰值 → Beckett 近景），最后回到身后跟拍，让观众看见前方的直道和白线，交给 clip03。
- **clip03**：冲刺侧跟拍加速；过线后固定机位（Tess 秒表与板、撑膝笑与 Cole 一眼、队伍跑进太阳）。
- **clip04（v4.1 新增）**：几分钟后牛棚边——从围栏外看进去，前景 Isa 拉肩、后景 Diego 绑护腿；Diego 蹲下拍手套（峰值，隔着围栏微推）；Isa 近景、Beckett 按肩走过；最后一镜围栏把画面分成两半，两人都没动。全条无台词。
- **光**：清晨低角度太阳在外野那头（画左），逆光、长影子、露水反光；侧跟拍时太阳在两人前方偏画左，脸是侧光。
- **轴线**：**全队沿外野围栏内侧的红土警戒跑道逆时针跑，画右→画左。** 侧跟拍机位在内侧（草地一侧）与队伍平行：Beckett 在内道（近机位），Isa 在外道（远机位）——Isa 超过 Cole 时 Cole 在前景近机位、Isa 从他身后外侧超过。反向跟移时 Beckett 画右、Isa 画左（与侧跟拍的前后关系一致）。终点白线在一垒侧界外登记桌前，Tess 与出赛板在白线画左外侧。
- **景别序列**：全（队伍、Beckett 倒跑）→ 中（Isa 加速越过 Cole）→ 双人中近 → 双人近 → 双人中近（正面）→ Isa 近（正面、缓推）→ Beckett 近（正面）→ 双人中（身后，前方白线）→ 双人中（冲出去）→ 中（冲刺、过线）→ 近（秒表）→ 中（撑膝、Cole 一眼）→ 近（Isa 看板）→ 大全（跑进太阳）。
- **声音**：一队人的脚步与呼吸是底；冲刺时口哨与喊 Isa 的名字；秒表一声；笔；远处海。无 bgm、无旁白。
- **载体**：球场图 @01_Sharks_field、牛棚图 @01/02_bullpen_field（空间）；人物形象图＋@01_Sharks_outfit 全员队服、Tess 用 @girl_uniform02；出赛板一行大写由模型生成；队友无图；各种跟拍与冲刺为文字驱动。
- **反向测试**：如果两人停下来面对面说，这是训话；并排跑着说、最后用冲刺回答，才是球员之间的事。

## 走位表（场级，秒为场内绝对秒）

| 秒 | 谁 | 从哪 → 到哪 | 面朝 | 含义 |
|---|---|---|---|---|
| 0–4 | 全队 | 警戒跑道画右→画左；Beckett 领跑、倒跑两步回头喊 | 向前／Beckett 向队伍 | 当众点名 |
| 4–7 | Isa | 队伍中段外道 → 越过 Cole（内道、近机位）→ Beckett 外侧并排 | 向前 | 明星上前 |
| 7–50 | Beckett、Isa | 队伍最前面并排（Beckett 内、Isa 外） | 向前，说话时侧头 | 谈判 |
| 50–58 | Beckett、Isa | 最后直道冲刺 → 白线；Isa 领先一个身位过线 | 向前 | 回答 |
| 58–73 | Tess／Cole／Isa／全队 | Tess 登记桌不动；Cole 随队伍到线前、跑过；Isa 转身看板；队伍跑向太阳 | — | 周一还在 |

## clip 切分（2026-09-23，剧本 v4，三条）

| clip | 场内秒 | 时长 | 分拍 | 主体 | 峰值事件 | 图 |
|---|---|---|---|---|---|---|
| s04-clip01 〈Up front〉 | 0–22 | 22 s | 晨跑、"Two more. Nobody walks. Marsh— up front."→Isa 加速越过 Cole→"You don't usually want me up front, Beck." / scouting sheet→"Has Cole seen that sheet?" / "Cole didn't want to read it." / 笑 / "So Game One's mine." | Beckett、Isa、Cole、队友 | Isa 加速越过 Cole 冲到队伍最前面（镜 2，低机位反向跟移随他加速） | 4 |
| s04-clip02 〈It's on me〉 | 22–50 | 28 s | "Game One could be yours…"→Isa 说出怕（"One bounce, he's on third…" / "…the scholarship kid…"）→"let Diego block it" / "And if he doesn't block it?" / "Then it's on me…"→Isa 看着他不答 | Beckett、Isa | Isa 说出奖学金生的怕（镜 2，正面反向跟移中缓推到 Isa 近景） | 3 |
| s04-clip03 〈To the line〉 | 50–72 | 22 s | "Last one. To the line." / "You're on."→冲刺、Isa 领先一个身位过线→Tess 秒表与板 CUT DAY — MONDAY→撑膝笑、Cole 一眼跑过→队伍跑进太阳 | Isa、Beckett、Tess、Cole、队友 | Isa 一点点压过 Beckett、领先一个身位过线（镜 2，侧跟拍加速） | 5 |
| s04-clip04 〈Bullpen〉 | 72–88 | 16 s | 几分钟后牛棚边：Isa 拉肩、Diego 绑护腿→Diego 蹲下拍手套看他→Isa 看着、Beckett 按肩走开→隔着围栏两人都没动 | Isa、Diego、Beckett、队友 | Diego 蹲到本垒板后拍手套、抬头看 Isa（镜 2，隔着围栏微推） | 7 |

合计 88 s（剧本 v4.1 估 ≈69 s；v4 三条为 74 s，v4.1 clip03 改为 22 s 并新增 clip04 16 s；台词 142 词按 4 词/秒已占 35.5 s，另有越过 Cole、Isa 不答、冲刺、过线后四个无台词功能段）。三条独立生成；clip01 末态＝两人最前面并排、Isa 刚说完 "So Game One's mine."；clip02 末态＝Isa 看着 Beckett 没答、前方是最后直道。

## 变化轨总览

| clip | 镜长（s） | 峰值镜 | 台词占比 |
|---|---|---|---|
| 01 | 4/3/8/7 | 2 | ≈52%（46 词 ≈ 11.5 s） |
| 02 | 6/10/4/8 | 2 | ≈80%（89 词 ≈ 22.3 s） |
| 03 | 4/7/3/4/4 | 2 | ≈8%（7 词 ≈ 1.8 s） |
| 04 | 6/3/3/4 | 2 | 0（无台词） |

## 风险登记

- **球场与牛棚**：用户已提供 @01_Sharks_field 与 @01/02_bullpen_field；跑道、白线、登记桌、出赛板若图里没有则按文字补。
- **跑步跟拍**：侧跟拍、反向跟移、身后跟拍、手持斜前跟拍全部文字驱动，每镜 <15 s，中风险；跑步中说话的口型与喘气未验证。
- **Isa 越过 Cole**：纵深上的超越（外道越过内道的人）3 s，文字驱动，模型可能把 Cole 做得不清楚。
- **clip02 台词占比 80%**：Isa 一句 35 词、跑步中说，逐字执行未验证；窗口已按 4 词/秒放足。
- **冲刺"领先一个身位"**：幅度小，模型可能做成大幅领先或并排；写成"最后十米一点点压过去"。
- **出赛板文字**：一行大写 `CUT DAY — MONDAY`。
- **队服以图为准**：剧本写"灰色训练 T 恤"，生产改按 @01_Sharks_outfit；若图是比赛球衣，晨跑穿球衣以图为准。
- **全队同款队服**：主角靠形象图区分；Cole 金发是识别点。
