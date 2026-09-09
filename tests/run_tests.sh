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
echo "$out" | grep -q "W05"; check "original long line retains timing review" $? "$out"

out=$($V examples/bad-example.prompt.md); rc=$?
[ $rc -eq 1 ]; check "bad-1 exits 1" $? "rc=$rc"
for code in E01 E12 E05 E02 E03 E04 W06 W09 W10 W02 W20; do
  echo "$out" | grep -q "$code"; check "bad-1 has $code" $? ""
done

out=$($V examples/bad-example-2.prompt.md)
for code in W13 W15 W17; do
  echo "$out" | grep -q "$code"; check "bad-2 has $code" $? ""
done

out=$($V examples/bad-example-3-lazy-long-take.prompt.md); rc=$?
check "bad-3 exits 0 (pacing hints are WARN)" $rc "$out"
for code in W22 W23; do
  echo "$out" | grep -q "$code"; check "bad-3 has $code" $? ""
done

# 1.4.0 W24: E 层注释泄漏进【素材绑定】即告警；干净绑定不触发
tmp=$(mktemp -d)
printf '【素材绑定】图1 = A 人物形象，只参考面部、发型、体型，不参考服装、背景与姿势。（约定：每人两图，共 3 张 ≤6。本条为草稿。）\n【总述】10秒 9:16，室内。\n【起始状态】图1 的 A 在画左。\n【整体情绪弧线】平静。\n- A：平静（镜1，抬眼）\n【分镜时间线】\n镜头1（0-10s）：【中景，正面，固定】〔A：平静〕A 抬眼。\n【贯穿要求】A 外观锁；无 bgm；不要字幕。\n' > "$tmp/leak.prompt.md"
out=$($V "$tmp/leak.prompt.md"); echo "$out" | grep -q "W24"; check "note leak in 素材绑定 triggers W24" $? "$out"
echo "$out" | grep -q "E01"; rc=$?; [ "$rc" -ne 0 ]; check "W24 is a warning, prompt still structurally valid" $? "$out"
echo "$out" | grep -q "0 error"; check "leak prompt has 0 error (W24 is WARN)" $? "$out"
rm -rf "$tmp"
out=$($V examples/example-03-yogurt-comedy.prompt.md examples/example-01-kitchen-keys.prompt.md --batch independent)
echo "$out" | grep -q "W22\|W23"; rc=$?
[ "$rc" -ne 0 ]; check "accepted one-take and 6s shots do not trigger W22/W23" $? "$out"

# 1.3.0 ledger check on a generated fixture
L="python3 scripts/ledger_check.py"
tmpl=$(mktemp -d); python3 - "$tmpl/ledger.xlsx" <<'PY'
import sys; sys.path.insert(0, 'scripts')
from xlsx_lite import write_workbook
H = ['镜号', '段', '入点', '出点', '时长', '场景', '景别与运镜', '画面', '英语台词', '声音', '连续性', '情绪']
rows = [['01', '1', '00:00:00', '00:00:03', '', '厅', '中景，固定', '看', 'A 00:00–00:03\n"Hi."', '', '', ''],
        ['02', '1', '00:00:03', '00:00:12', '', '厅', '近景，微推', '说', 'B 00:03–00:11\n"Long."', '', '', ''],
        ['03', '1', '00:00:12', '00:00:20', '', '厅', '特写，固定', '答', 'A 00:12–00:15\n"One."\nB 00:16–00:19\n"Two."', '', '', '']]
write_workbook(sys.argv[1], {'分镜总表': [['t'], [], [], [], H] + rows})
PY
out=$($L "$tmpl/ledger.xlsx"); rc=$?
check "ledger fixture exits 0" $rc "$out"
echo "$out" | grep -q "L03 镜02"; check "ledger flags 9s single-line shot (L03)" $? "$out"
echo "$out" | grep -q "L03 镜03"; rc=$?
[ "$rc" -ne 0 ]; check "ledger does not flag 8s two-line shot (W22 口径)" $? "$out"
rm -rf "$tmpl"

# 2.3: these are varying states and reusable body cues, not prohibited copying.
out=$($V examples/example-04-parameters-fight.prompt.md)
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
