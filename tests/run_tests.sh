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
# 1.12.0: a pre-baseline 30 s design (5-6 s shots, 3 s held silence) -> rhythm-baseline ERRORs only, no format errors
[ $rc -eq 1 ]; check "example-04 exits 1 on the rhythm baseline only" $? "rc=$rc"
echo "$out" | grep -q "^ERROR E"; rc=$?
[ "$rc" -ne 0 ]; check "example-04 has no format (E) errors" $? "$out"
echo "$out" | grep -q "^ERROR R01"; check "example-04 baseline R01" $? "$out"
echo "$out" | grep -q "W05\|W29\|台词轨"; check "original long line retains timing review (W05 / W29 / 台词轨)" $? "$out"

out=$($V examples/example-05-stairwell-letter.prompt.md); rc=$?
check "example-05 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-05 clean (keyframe carrier)" $? "$(echo "$out" | tail -1)"

out=$($V examples/example-06-balcony-cigarette.prompt.md); rc=$?
check "example-06 exits 0" $rc "$out"
echo "$out" | grep -q "0 error(s), 0 warning(s)"; check "example-06 clean (romance)" $? "$(echo "$out" | tail -1)"

# 1.12.0 user rhythm baseline: the Offset EP01 s04 v4 incident (2/2/2/6/2/6 s) fails; examples 01/03/05/06 stay clean above
out=$($V tests/fixtures/rhythm/offset-ep01-s04-clip01-v4.prompt.md); rc=$?
[ $rc -eq 1 ]; check "s04 v4 fails the rhythm baseline" $? "rc=$rc"
for pat in "ERROR R01 镜头4 6s" "ERROR R01 镜头6 6s" "ERROR R02 开头" "ERROR R02 结尾" "WARN  W28 镜头4" "rhythm_baseline\": \"failed"; do
  echo "$out" | grep -q "$pat"; check "s04 v4 has $pat" $? ""
done

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
