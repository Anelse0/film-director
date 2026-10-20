# film-director

Seedance 2.5 视频 Prompt 生产 Skill：表演外化与情绪提示词、导演与分镜（导演语法、机位设计、变化轨、执行卡）、时长与节奏、参考资产计划、Prompt 编译、连续性与质量检查、成片实测。调用：`/film-director` 或在对话中描述任务（拆分镜、转 Prompt、表演测试、改成片）。

## 一句话

先做导演决策，再把决策翻译成模型能看见的东西，最后才写 Prompt。

## 怎么用

- 入口、流水线、停靠点、硬规则：`SKILL.md`。
- 每阶段的规则：`references/stage-*.md`；导演语法 `references/director-grammar.md`；时长与节奏 `references/duration-rhythm.md`；外化词典（情绪 → 可见写法 + 声音写法，也是 A 层词的字典）`references/externalization-lexicon.md`。
- 校验码总表（触发 / 处置 / 分类）：`references/checks.md`。
- 成片证据账本（规则文里"证据 #n"指它）：`references/validation-log.md`。
- 脚本：`scripts/validate_prompt.py`（Prompt）、`camera_plan_check.py` / `stage_check.py`（分镜卡）、`qa_check.py`（QA）、`measure_clip.py`（成片实测）。
- 测试：`bash tests/run_tests.sh`。保护区（`tests/test_protected_zone.py`）锁住规则文、模板与脚本的哈希，改动要连 CHANGELOG 一起提交。

## 版本

版本号在 `VERSION`；每一版改了什么、为什么、依据哪条成片，见 `CHANGELOG.md`。创意前端（概念、故事、剧本、台词）由独立的 film-story Skill 承担，本 skill 不创作剧本。
