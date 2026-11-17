# 1.1.0 验收协议（导演语法与官方对齐版本）

授权：用户要求（1）调研 Seedance 2.5 官方提示词指南与一手文档，（2）调研好莱坞及欧美导演的导演语法（运镜、景别、人物动线等），（3）对 film-director 做全面 review，（4）据此迭代 skill，禁止机械套用与 lazy patch；追加（5）英文台词每秒长度依据，（6）暧昧 / 爱情类型的导演方法并让 skill 具备该能力。基线 1.0.0 / 4fb2f7b。

## 交付物

- `review.md`：全面 review（官方偏差 O1–O8、导演语法缺口 D1–D9、结构与工具 T1–T4、1.0.0 遗留 F1–F11）。
- `research-seedance-official.md` / `research-director-grammar.md` / `research-dialogue-rate.md` / `research-romance.md`：四份调研摘要，均带来源与核实状态。
- 代码与文档变更见 `CHANGELOG.md` 1.1.0。

## 验收分两句

- **工程完成**：`bash tests/run_tests.sh` 全过（含新增 `tests/test_directing_release.py`）；示例 05 / 06 通过校验；保护区哈希在同一提交内重设并在 CHANGELOG 说明；已提交推送。
- **效果提升：未验证。** 本版没有生成对照成片，也没有用户盲选；能力表 §7 的台词预算、S5 §5.0 的载体选择、§8.5 的暧昧机制均为 `[推论]` 或一手方法的转译，待 `validation-log.md` 待验证队列 9–12 项实测。非盲自评只能称"非盲呈现改善"。

## 保护区处理

`tests/test_protected_zone.py` 的 1.0.0 基线在本次公开重设：本版是生产 / 导演核心的有意变更，符合该测试文档字符串"属于独立的生产版本发布，须在同一提交更新基线并写 CHANGELOG"的规定。情绪库、emotion-performance、performance-record、production_contract、production_preflight、emotion_library、performance_checks、prompt_structure 的哈希保持 1.0.0 不变（未改动）。
