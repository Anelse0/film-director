# 调研：Seedance 2.5 官方文档（2026-09-17）

来源全部为火山方舟 / ByteDance Seed 一手页面（文档站为 JS 渲染，经其后端接口 `getDocDetail` 取得同页 Markdown）。已并入 `references/seedance-2.5-capabilities.md`；此处记录来源与未能读取项。

| 文档 | URL | 首发 / 最近更新 |
|---|---|---|
| Doubao Seedance 2.5 提示词指南（在线版 = 用户提供的 PDF） | https://docs.volcengine.com/docs/82379/2607689 | 2026-08-07 / 2026-09-08 |
| Doubao Seedance 2.5 教程 | https://docs.volcengine.com/docs/82379/2607688 | 2026-08-07 / 2026-09-11 |
| Doubao Seedance 2.0 系列提示词指南 | https://docs.volcengine.com/docs/82379/2222480 | 2026-04-02 / 2026-09-08 |
| Doubao Seedance 2.0 系列教程 | https://docs.volcengine.com/docs/82379/2291680 | — / 2026-09-15 |
| 创建视频生成任务 API | https://docs.volcengine.com/docs/82379/1520757 | 2025-04-10 / 2026-09-17 |
| Seedance 1.0 系列提示词指南 | https://docs.volcengine.com/docs/82379/1631633 | — / 2026-08-13 |
| Seedance 2.0 官方提示词 Skill（sd2-pe） | https://arkdocs.tos-cn-beijing.volces.com/files/video-generation/SKILL.md | 无日期 |
| Seed 博客 "Seedance 2.5: One-take Creation, Flexible Referencing" | https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5 | 2026-07-31 |
| 便利创作含肖像视频 | https://docs.volcengine.com/docs/82379/2608626 | — |

## PDF 之外的新事实（已进能力表）

- Model ID `doubao-seedance-2-5-260628`；`duration` [4, 30] 或 -1；`resolution` 480p / 720p / 1080p（10bit HEVC），**无 4k**；`ratio` 六档 + adaptive，编辑 / 延长 / 首尾帧只允许 adaptive；`output_format` mp4 / mov；`watermark`；`omni_reference_task_type` auto / reference / edit / extend；`seed` / `camera_fixed` 不支持。
- 输入规格：图 [300, 6000] px、<30 MB；视频 [2, 30] s（编辑 [4, 30] s）、FPS [24, 60]、≤200 MB；音频 wav/mp3 [2, 30] s、≤15 MB；**可仅传音频**；**不支持直接上传真人人脸**。
- 11 种语言；提示词建议中文 ≤500 字、英文 ≤1000 词；编辑输出可能短 ≤0.4 s（PDF 写 0.3 s）。
- 教程"基础公式"：主体 + 动作/事件 + 场景与环境 + 视觉风格 + 运镜/切镜 + 声音；声音符号 `()` 音乐、`<>` 音效、`{}` 台词、`【】` 字幕。
- 教程多语言说唱范例：8 镜 / 20 s，每镜"景别 + 机位 + 运镜 + 速度 + 质感"，每镜末尾"硬切"。
- 2.0 指南 FAQ（2.5 声明参考方式与 2.0 一致）：ID 漂移用大头照 + 全身照、精准素材放前面；字幕无法 100% 避免；双胞胎问题；多次续写劣化；多音字换同音字；参考人物 >4 人稳定性下降。
- 2.0 指南：编辑 / 延长直接用 `<视频N>` 指代，不写"参考"；`@图片1跑向` 数字粘连需断句。

## 未能读取

- 《Seedance 2.5 提示词模板》飞书文档（需登录）。
- 官方 `sd25-pe` Skill 原文（TOS 桶路径未探测到；`sd2-pe` 已读）。
- Seed 中文博客页（超时）；即梦 / Dreamina 帮助中心无可抓取的一手页。
- 2.5 无技术报告（只有 2.0 的 arXiv 2604.14148）。

## 第三方口径纠错

UIED（2026-08-08）称方舟 2.5 "暂不支持 1080P" 已过时；"不支持 4k" 仍正确。旧能力表"分辨率各来源不一致"一行据此改为 [官方]。
