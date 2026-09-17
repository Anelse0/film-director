# 调研：英文 / 中文台词每秒长度（2026-09-17）

用途：为 `references/seedance-2.5-capabilities.md` §7 的估时假设提供来源。标签：[一手] 原文已读；[官方] 平台 / 机构官方页；[第三方] 转述；[未验证] 仅见搜索摘要；[推论] 本 Skill 换算。

## 一、英文语速

| 来源 | 数值 | 标签 |
|---|---|---|
| NCVS《Voice Qualities》：“The average rate of speech for English speakers in the United States is about 150 words per minute” https://ncvs.org/tutorials/voice-qualities/ | 150 wpm = 2.5 词/s | [一手][官方] |
| Yuan, Liberman & Cieri 2006, *Towards an integrated understanding of speaking rate in conversation*, Interspeech https://www.isca-archive.org/interspeech_2006/yuan06_interspeech.pdf | Switchboard 按总时长 196 wpm、剔除静音 236 wpm、按发言段 164 wpm；CallHome 214±6.7、Fisher 193±0.7；话题 152–170 | [一手] |
| Tauroza & Allison 1990, *Speech Rates in British English*, Applied Linguistics 11(1) | 广播独白 150–170、访谈 160–210、对话 190–230 wpm（约 4.3 音节/s） | [一手·摘要]，数值经转引 |
| Netflix English (USA) Timed Text Style Guide | 成人 ≤20 字符/s，儿童 ≤17；每行 ≤42 字符 | [一手][官方] |
| BBC Subtitle Guidelines | 160–180 wpm | [第三方转述] |
| Wikipedia *Words per minute*；ACX 9,300 词/小时 | 有声书 150–160 wpm | [第三方] |
| Final Draft 博客 | 100 页约 95–110 分钟；对话密集的段落跑得更快 | [一手·行业] |
| Banse & Scherer 1996, JPSP 70(3) http://www.columbia.edu/~rmk7/HC/HC_Readings/Scherer.pdf | 愤怒、恐惧、喜悦发音速率上升；悲伤下降（方向性） | [一手] |
| Juslin & Laukka 2003, Psych. Bulletin 129(5) | 104 项研究综述：anger / fear / happiness 快，sadness / tenderness 慢 | [第三方转述] |

关键区分：净说话时间语速（190–240 wpm）明显高于含停顿的总时长语速（150–165 wpm）；台词预算必须区分"说话时间"与"镜头时长"。

## 二、Seedance 官方与第三方

- 官方（2.5 指南、2.0 指南、API 文档、火山引擎文章《Seedance 2.0 对白生成》 https://www.volcengine.com/article/40767 ）：**没有任何字数 / 秒的数值建议** [官方未说明]。官方 30 秒范例 8 句英文 7 句在 0.75–3.0 词/s，第 9 镜 2 秒 10 词，范例本身不按语速预算。
- fal.ai 指南 https://fal.ai/learn/tools/seedance-2-0-prompting-guide ：短句、长独白漂移、两句短句跨切胜过一长句 [一手][第三方]。
- Cutout.pro https://www.cutout.pro/learn/blog-seedance-2-0-audio-guide/ ：5–10 词一句最稳；超过 8 秒口型变糊；中文口型最稳、英文其次 [一手][第三方]。
- VideoAI.me https://videoai.me/blog/seedance-2-0-dialogue-prompts ：每人每镜 ≤2 句 [一手][第三方]。
- 搜索摘要（未打开）：12 词 / 10 s、20 词 / 15 s；5–8 秒单人一镜作基准测试 [未验证]。

## 三、中文参照

| 来源 | 数值 | 标签 |
|---|---|---|
| Yuan et al. 2006 | 中文 CallHome/CallFriend 247 字/分、Fisher 228 字/分（3.8–4.1 字/s） | [一手] |
| 搜狐《播音丨每分钟要读多少字》 https://www.sohu.com/a/531294102_121156125 | 播音 250–260 字/分 | [第三方] |
| 闪电配音 https://www.soundems.com/news/detail/7198.html | 一般 200 字/分；专题 210–220；新闻 300 | [第三方] |
| 配音行业经验 | 配音员正常 4 字/s，不能满打满算 | [第三方][未验证] |
| Netflix 简体中文 TTSG | 9 字/s 阅读速度 | [第三方转述] |
| GY/T 301—2016、GY/T 288—2014 | 存在，是否含每秒字数条款未读到 | [官方][未验证] |

## 四、推导（[推论]，进入能力表 §7）

净说话语速 slow / normal / fast = 2.0 / 2.5 / 3.0 词/s（中文 3 / 4 / 5 字/s）；镜头填充 2/3（≈70%）；词数 = 时长 × 2/3 × 语速。5 秒默认约 8 词（中文约 13 字），10 秒约 17 词。超过 8 秒或 10 词拆两句并留停顿。第三方 Seedance 经验值（12 词 / 10 s）约等于 slow 列再打折，首版提示词偏保守、口型稳定后再靠近 normal。

## 五、未找到 / 未验证

官方每秒字数建议 [未找到]；英文配音 / ADR 每秒词数硬性规范 [未找到，只有 isochrony 原则]；ASHA 130 wpm 一手页 [未找到]；Tauroza & Allison 原文数值、Juslin & Laukka 原文、BBC 原页、Netflix 中文页 [未验证]。
