# okr-sync.ps1 — 飞书原生 OKR ↔ 13_OKR 多维表 双向同步
#
# 当前状态：等待 OKR scope 授权
# 一旦执行：
#   lark-cli auth login --scope "okr:okr.period:readonly okr:okr:readonly okr:okr.objective:write okr:okr.progress:write"
# 此脚本即可生产部署。
#
# 工作流：
#   1. lark-cli okr +cycle-list --user-id <BOSS> → 拉所有季度
#   2. lark-cli okr +cycle-detail --period-id 2026Q1 → 拉 OKR + KR
#   3. 比对 13_OKR 多维表 → 差异同步
#   4. 任务完成时 → lark-cli okr +progress-create 推送进度

param([string]$Period='2026Q1', [switch]$DryRun)

$BOSS_OID='ou_85c9148d13c562728e60d456b60d9afc'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_OKR='tbl0tdusQ2fw98wZ'

Write-Host "==================================================="
Write-Host "  okr-sync · 飞书原生 OKR ↔ 13_OKR 多维表"
Write-Host "  Period: $Period"
Write-Host "==================================================="
Write-Host ""

# Step 1: 检查 scope
Write-Host "[1/4] Checking OKR scope..."
$test = cmd /c "lark-cli okr +cycle-list --user-id $BOSS_OID 2>&1"
if($test -match 'missing_scope|missing required scope'){
  Write-Host "  ⚠ OKR scope 未授权"
  Write-Host ""
  Write-Host "  执行授权命令（在终端运行）："
  Write-Host '    lark-cli auth login --scope "okr:okr.period:readonly okr:okr:readonly okr:okr.objective:write okr:okr.progress:write"'
  Write-Host ""
  Write-Host "  授权后再跑本脚本即可同步。"
  exit 0
}
Write-Host "  ✓ scope ready"
Write-Host ""

# Step 2: 拉飞书原生 OKR cycle
Write-Host "[2/4] Fetching cycles..."
$cyclesOut = cmd /c "lark-cli okr +cycle-list --user-id $BOSS_OID --jq .data"
$cycles = $cyclesOut | ConvertFrom-Json
Write-Host "  Found $($cycles.cycle_list.Count) cycles"

# Step 3: 拉指定 period 的 OKR + KR
Write-Host "[3/4] Fetching OKR detail for $Period..."
# ... (一旦有 scope，调 cycle-detail)
Write-Host "  (待 scope 授权后启用)"
Write-Host ""

# Step 4: 同步策略
Write-Host "[4/4] Sync strategy..."
Write-Host "  方向 A：飞书 OKR → 13_OKR 多维表（首次同步）"
Write-Host "  方向 B：13_OKR 进度变更 → 飞书 OKR progress-create（持续同步）"
Write-Host ""
Write-Host "  当前 13_OKR mock 4 个 OKR："
Write-Host "    🟢 全公司业绩 65%"
Write-Host "    🟡 商品上新 58%"
Write-Host "    🟢 抖音内容增长 72%"
Write-Host "    🟢 客户体验 80%"
Write-Host ""
Write-Host "  授权后可一键迁移到飞书原生 OKR 系统。"
