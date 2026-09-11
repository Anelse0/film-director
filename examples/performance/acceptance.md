# 2.3.0 验收 Demo

这些是针对本轮需求的测试样例，不是后续写作的固定模板。正文可直接复制到视频生成工具；没有虚构参考图编号。尚未生成视频。

## 怎么测

01 与 02 同为强克制，观察低/高情绪负荷差异。02 与 03 镜头、总时长及分段相同，观察控制维持与控制失效的差异。04/05 测试跨情绪衔接。分段只是本组动作的估时，不推广为固定节奏。

### 低强度难过，强克制

[Prompt](01-sadness-low-held.prompt.md) · [编译前表演记录](01-sadness-low-held.performance.json)

Sadness 单条微调：保留内眉角、下拉嘴角、一次下巴颤动和吞咽未解除表情；降低幅度，无泪水表现。与 02 保持强克制，比较情绪负荷。

### 高强度委屈，始终憋住

[Prompt](02-sadness-high-held.prompt.md) · [编译前表演记录](02-sadness-high-held.performance.json)

Sadness + Crying 重组：下眼睑积泪来自对原始落泪动作的克制改编；抬眼、合唇、压住肩部颤动为新增控制过程。不是原文直用。

### 同等高情绪，克制失效后哭出来

[Prompt](03-sadness-high-released.prompt.md) · [编译前表演记录](03-sadness-high-released.performance.json)

与 02 使用相同镜头和分段，改变控制是否失效。前段同样积泪，末段保留 Crying 的落泪、方形嘴部、下巴皱缩与肩膀颤抖；不在结尾恢复平静。

### 害羞 → 想笑 → 真正笑出来

[Prompt](04-shy-to-laughter.prompt.md) · [编译前表演记录](04-shy-to-laughter.performance.json)

Embarrassment + Joy / Laughter。中段把笑压回去是新增过渡；末段保留笑纹、露齿、头部前后运动和肩随呼吸起伏，最后留有笑容。

### 愤怒 → 委屈，最后忍住眼泪

[Prompt](05-rage-to-hurt.prompt.md) · [编译前表演记录](05-rage-to-hurt.performance.json)

Rage + Sadness + Crying。保留怒相的眉、上唇、鼻翼、颈部；怒相松动到委屈属于新增连接。末段积泪抬眼是克制改编。

### 面具与泄漏：表面在笑，眉在说别的，最后面具裂开（2.0.0）

[Prompt](07-mask-and-leak.prompt.md) · [编译前表演记录](07-mask-and-leak.performance.json)

Nervous Fake Smile + Sadness + Crying 重组，按 `performance-grammar.md` §7 的分配：表层占嘴与回位（25），泄漏只占内眉角一个部位（19 的 hinge），回位句在 b2；b3 把 25 的回位句反写（"回位的笑没有再回来"）作为进入 6 的铰链，末态按 6 不收束。特写里肩只在画框下缘，所以肩抖写在结束时才开始。

### 听者反应链：怀疑 → 明白 → 盖住（2.0.0，production）

[Prompt](08-listener-reaction-chain.prompt.md)

B 走 9 → 14 → 25，桥梁按索引 `neighbors`（更高的眉落回、眼睁大、分唇吸气；点头结束后嘴拉出笑）。示范三件事：反应镜先写他看见了什么（镜 2 以"目光从侧面落在 A 身上"开头，镜 4 以"A 说完之后"开头）；可读性地板（9 与 25 的 hinge 都是"特写"级，所以镜 1 的双人中景只写 B 的头转成侧视，hinge 留给镜 2 / 镜 4 的特写）；切点落在思想完成处（镜 1→2 在 A 的句尾、镜 2→3 在 B 不眨的凝视之后、镜 3→4 在 A 嘴闭上之后），不机械落在句号。

## 文本审阅结论

- 01：控制表现为合唇、收稳下颌；吞咽后下拉嘴角仍在，不强加泪水。
- 02：积泪、压回张嘴、压住肩部起动和抬眼共同表现控制，不只是给“哭”加一个“轻微”。
- 03：控制失效在嘴唇分开与呼吸断开中可见，随后落泪、嘴部方形、下巴皱缩与肩颤有连续窗口，末态没有平静。
- 04：中段解释从压唇半笑到真笑的变化；手从嘴旁移开，避免遮住最终嘴部与笑纹。最后四秒承担笑的释放与余笑，有执行压缩风险，需看成片。
- 05：怒相与悲伤眉形先后替换；头部前伸沿用 Rage，不自行加迈步、拍桌。末段保留吞咽未能压回表情及克制积泪。
- 这些文字通过了本次人工语义审阅，但模型能否呈现红眼、下巴细颤和精确时间窗仍未验证。脚本输出的 needs_review 不伪装成自动质量评分。

## 完整生产接入

[06 完整生产骨架](06-production-rage-hurt.prompt.md) 使用 05 的同一表演正文与同一记录。它是明确的无素材文生示例，不声称跨片人物一致性；一个镜头内三个表演节拍，并不剪成三镜。

在 Skill 目录核对：

```bash
python3 scripts/validate_prompt.py examples/performance/02-sadness-high-held.prompt.md --artifact performance --record examples/performance/02-sadness-high-held.performance.json
python3 scripts/validate_prompt.py examples/performance/06-production-rage-hurt.prompt.md --record examples/performance/05-rage-to-hurt.performance.json
python3 scripts/emotion_library.py --id 6 --raw
python3 scripts/validate_prompt.py examples/performance/07-mask-and-leak.prompt.md --artifact performance --record examples/performance/07-mask-and-leak.performance.json
python3 scripts/validate_prompt.py examples/performance/08-listener-reaction-chain.prompt.md
python3 scripts/emotion_library.py --neighbors 25
bash tests/run_tests.sh
```

原文调用的正文由检索命令直接输出，25 条都参与逐字回归；中文 Demo 均明确标注微调/重组。

## 视频验收观察点

分别观察：识别性部位是否可见；控制行为是否发生；高光是否有发展和持续；末态是否正确；情绪切换是否跳变。记录为可见/部分/未执行/不可观察，并记平台、模型版本、参考图、Prompt 版本。裁切或遮挡不等于没演。时间不足先减少无关事件或调整窗口，不自动抹掉细节。
