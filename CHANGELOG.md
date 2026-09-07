# Changelog

## 1.0.0 — 2026-09-07

从 [Film-Seedance-Director](https://github.com/Anelse0/Film-Seedance-Director) 2.6.0-alpha.3（commit 0436abd）拆分出的生产后端 Skill，首个独立版本。

- 范围：S1 资源读取、S2 需求识别、S4 表演外化（含情绪表演库）、S5 导演与分镜、S5b 参考资产、S6 Prompt 编译、S7 检查；表演优先路由（performance / production / raw）完整保留。
- 创意前端（S3a 概念、S3b 故事、S3c 剧本、台词创作与改写）拆至独立的 film-creative Skill；输入契约接受任何来源的剧本场景文本。
- 移除创意侧文件：stage-3a/3b/3c、concept-generation、story-development、screenwriting-traditions、character-scene-development、creative-loop、research-to-craft、dialogue-*、preference-ledger、概念脚本与示例、创意测试。
- 共用文件（execution-contract、stage-1-intake、scene-parameters、causal-chain、anti-mechanical、genre-packs、project-state、script-scene 模板）按生产侧范围裁剪；genre-packs 保持与 film-creative 相同内容。
- 保护区哈希基线从 v2.5.0 更新为 1.0.0：stage-4 / stage-7 / director-lenses 三个受锁文件中指向创意侧文件的引用改为交接说明（各 1–3 行），其余受锁文件字节不变；对照 v2.5.0 的差异可在源仓库 tags 中核查。
- 历史版本记录（1.2.0–2.6.0-alpha.3）见源仓库 Film-Seedance-Director 的 CHANGELOG 与 tags。
