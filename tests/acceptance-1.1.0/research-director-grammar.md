# 调研：好莱坞与欧美导演的导演语法（2026-09-17）

已整理进 `references/director-grammar.md`（含 §十 来源与核实状态表）。本文记录调研过程与取舍。

## 方法

优先实践者 / 学者一手著作与访谈（Mackendrick、Mamet、Hitchcock/Truffaut、Lumet、Murch、Bordwell、Block、Katz、Proferes、Weston、Deakins、Fincher、Lubezki、Villeneuve、Spinotti/Mann、Richards/Zhao、Gerwig/Levy、Nolan），其次 Every Frame a Painting 等视频论文 [第三方]。网络在调研后半段大面积失败（socket closed / 300 s 超时 / 域名拦截：davidbordwell.net、goodreads、filmmakermagazine、halcyonrealms），因此约三分之二条目只经搜索摘要核对，在 grammar 文件里标 [一手·摘要]，不冒充读过原页。

## 采纳原则

1. 每条规则必须能转成"写进 C 层长什么样"，否则不进 Skill。
2. 导演姓名只留在 grammar / lenses 文件与 A 层，不进 Prompt（硬规则 10 不变）。
3. 与官方指南冲突时以官方为准（例：官方 2.0 建议一镜一运镜 → 本 Skill 允许复合但要求写同步 / 先后）。
4. 未能核实的名言不引用：Spielberg "the third eye"、Kubrick "the first idea is usually the worst"、Kurosawa "never avert one's eyes"、Lumet《城市王子》焦距数值、Bresson 原文。

## 对 Skill 的直接影响

- 新增 `director-grammar.md`（景别 / 运镜 / 动线 / 剪辑 / 构图 / 光 / 载体 / 类型 / 十条推导规则）。
- `stage-5` 重写：5.0 决策载体、5.1c 走位表、5.2 顺序加入"机器要不要动""每镜负载"、5.4 推近的动机改为"人物内部变化"。
- `director-lenses.md` 每条补"作用机制"与"语法依据"。
- `camera-vocabulary.md` 加焦距 / 景深 / 机高 / 终点写法 / 声音符号。
- `externalization-lexicon.md` 去掉"情绪 → 运镜"固定伴随。
- 示例 05 展示悬念信息差 + 有动机的推近 / 反向跟拍 + 关键帧载体。
