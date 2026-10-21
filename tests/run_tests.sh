#!/usr/bin/env bash
# 回归测试：校验脚本对示例文件的预期结果。任何一项不符即失败。
set -u
cd "$(dirname "$0")/.."
V="python3 scripts/validate_prompt.py"
fail=0
check() { # name, condition-expression-result(0/1), detail
  if [ "$2" -eq 0 ]; then echo "PASS $1"; else echo "FAIL $1 — $3"; fail=1; fi
}

out=$($V examples/example-01-kitchen-keys.prompt.md); rc=$?
check "example-01 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-01 clean" $? "$(echo "$out" | tail -1)"

out=$($V examples/example-02-lens-B-haneke.prompt.md); rc=$?
check "lens-B exits 0" $rc "$out"
echo "$out" | grep -q "W11"; rc=$?
[ "$rc" -ne 0 ]; check "explicit sequential speakers are not overlap" $? "$out"

out=$($V examples/example-03-yogurt-comedy.prompt.md); rc=$?
check "example-03 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-03 clean" $? "$(echo "$out" | tail -1)"

out=$($V examples/example-04-parameters-fight.prompt.md); rc=$?
check "example-04 exits 0" $rc "$out"
echo "$out" | grep -q "W05\|W29\|台词轨"; check "original long line retains timing review (W05 / W29 / 台词轨)" $? "$out"

out=$($V examples/example-05-stairwell-letter.prompt.md); rc=$?
check "example-05 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-05 clean (keyframe carrier)" $? "$(echo "$out" | tail -1)"

out=$($V examples/example-06-balcony-cigarette.prompt.md); rc=$?
check "example-06 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-06 clean (romance)" $? "$(echo "$out" | tail -1)"

out=$($V examples/bad-example.prompt.md); rc=$?
[ $rc -eq 1 ]; check "bad-1 exits 1" $? "rc=$rc"
for code in E01 E12 E05 E02 E03 E04 W06 W09 W10 W02; do
  echo "$out" | grep -q "$code"; check "bad-1 has $code" $? ""
done

out=$($V examples/bad-example-2.prompt.md)
for code in W13 W15 W17; do
  echo "$out" | grep -q "$code"; check "bad-2 has $code" $? ""
done

# 2.3: these are varying states and reusable body cues, not prohibited copying.
echo "$out" | grep -q 'W14\|W18'; rc=$?
[ "$rc" -ne 0 ]; check "body-part reuse no longer emits W14/W18" $? "$out"

tmp=$(mktemp -d); cp examples/example-02-lens-B-haneke.prompt.md "$tmp/clip02.prompt.md"
out=$($V examples/example-02-lens-B-haneke.prompt.md "$tmp/clip02.prompt.md")
echo "$out" | grep -q "W16"; check "multi-file W16" $? ""
rm -rf "$tmp"

# 1.13.0 check.py：一键入口冒烟（分镜卡 / QA 由测试夹具生成，Prompt 用 examples）
tmp=$(mktemp -d)
python3 -c "import sys; sys.path.insert(0, 'tests'); import test_check; test_check.write_fixture('$tmp')"
out=$(python3 scripts/check.py s5 "$tmp/04_shots/clip.md"); rc=$?
check "check.py s5 exits 0" $rc "$out"
echo "$out" | grep -q "^- 执行卡：stage_check 0 ERROR（S5 25 行；无）"; check "check.py s5 number block" $? "$out"
# 1.14.0 check.py plan：停靠 A（方案）——机位设计 + 纵览算术，不跑 stage_check
out=$(python3 scripts/check.py plan "$tmp/04_shots/clip.md"); rc=$?
check "check.py plan exits 0" $rc "$out"
echo "$out" | grep -q "镜头纵览 3 行"; check "check.py plan overview arithmetic" $? "$out"
echo "$out" | grep -q "执行卡："; rc=$?; [ "$rc" -ne 0 ]; check "check.py plan does not run stage_check" $? "$out"
# 1.14.1 版本行一行制：超过 200 字的版本行给 NOTE，不改退出码
sed -i '' "s/^\*\*版本：v1.3 · 2026-10-20\*\*（示例）/**版本：v1.3 · 2026-10-20**（示例）$(printf '改了什么%.0s' $(seq 60))/" "$tmp/04_shots/clip.md"
out=$(python3 scripts/check.py s5 "$tmp/04_shots/clip.md"); rc=$?
check "check.py s5 long version line still exits 0" $rc "$out"
echo "$out" | grep -q "^NOTE  分镜卡版本行"; check "check.py s5 long version line NOTE" $? "$out"
python3 -c "import sys; sys.path.insert(0, 'tests'); import test_check; test_check.write_fixture('$tmp/door-right', card=test_check.card_text(door_left=False))"
out=$(python3 scripts/check.py s6 "$tmp/door-right/04_shots/clip.md" examples/example-01-kitchen-keys.prompt.md); rc=$?
check "check.py s6 with example-01 exits 0" $rc "$out"
echo "$out" | grep -q "^- 校验：validate_prompt [0-9-]* 0 ERROR；WARN 无；成片教训类 无"; check "check.py s6 example-01 clean" $? "$out"
echo "$out" | grep -q "^- 机位设计：camera_plan_check 0 ERROR；C10 无矛盾；WARN 无"; check "check.py s6 example-01 C10 clean" $? "$out"
echo "$out" | grep -c "^HASH  " | grep -q "^2$"; check "check.py s6 prints two hashes" $? "$out"
out=$(python3 scripts/check.py s6 "$tmp/door-right/04_shots/clip.md" examples/bad-example.prompt.md); rc=$?
[ $rc -eq 1 ]; check "check.py s6 bad-example exits 1" $? "rc=$rc"
echo "$out" | grep -q "^ERROR \[validate_prompt\] E01"; check "check.py s6 bad-example E01 tagged" $? "$out"
out=$(python3 scripts/check.py qa --sync "$tmp/07_qa/clip.qa.md"); rc=$?
check "check.py qa --sync exits 0" $rc "$out"
echo "$out" | grep -q "^== qa_check（写回后独立跑）"; check "check.py qa --sync reruns qa_check" $? "$out"
python3 scripts/check.py --json s6 "$tmp/04_shots/clip.md" "$tmp/06_prompts/clip.prompt.md" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d['exit']==0 and len(d['block'])==4 else 1)"
check "check.py --json" $? ""
rm -rf "$tmp"

# 结构：保留已安装的调用名称（目录大小写可以不同）
grep -q "^name: film-director" SKILL.md; check "SKILL.md invocation name preserved" $? ""
# 所有 SKILL.md 引用的 references/templates 文件存在
missing=""
for f in $(grep -oE '`(references|templates|scripts|examples)/[^`]+`' SKILL.md | tr -d '`' | sort -u); do
  [ -e "$f" ] || missing="$missing $f"
done
[ -z "$missing" ]; check "SKILL.md links resolve" $? "$missing"

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
check "performance regression suite" $? ""
exit $fail
