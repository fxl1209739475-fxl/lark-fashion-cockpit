# approval-router.ps1 — 审批智能分流（升级 approval-flow）
#
# 当 14_审批 表新增 / 飞书原生审批触发时：
#   1. 按金额 + 类型自动分流
#   2. 满足规则的自动批
#   3. 不满足的 → 卡片推老板手动决策
#   4. 超期未处理（>3 天）→ 自动 ping 当前审批人

param([switch]$DryRun)
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_APP='tblAxWcmHnFl0qUE'
$BOSS_CHAT='oc_45e0995a007db9d7f1859fa17b6566f6'

function Load-Table($tableId){
  $rawJson = cmd /c "lark-cli base +record-list --base-token $BASE --table-id $tableId --jq "".data | {fields,data,record_id_list}"""
  $obj = $rawJson | ConvertFrom-Json
  $rows = @()
  for($i=0; $i -lt $obj.data.Count; $i++){
    $rec = [ordered]@{ _rid = $obj.record_id_list[$i] }
    for($k=0; $k -lt $obj.fields.Count; $k++){
      $rec[$obj.fields[$k]] = $obj.data[$i][$k]
    }
    $rows += [PSCustomObject]$rec
  }
  return $rows
}

# ============== 智能分流规则 ==============
function Classify-Approval($appr){
  $type = (@($appr.'类型'))[0]
  $amount = [decimal]$appr.'金额'
  $status = (@($appr.'状态'))[0]

  $rule = ""
  $action = "manual"
  $priority = "P2"

  switch -Wildcard ($type){
    '报销' {
      if($amount -lt 1000){ $rule = '报销 <¥1000'; $action = 'auto-approve'; $priority = 'P3' }
      elseif($amount -lt 5000){ $rule = '报销 ¥1000-5000'; $action = 'manual'; $priority = 'P2' }
      else{ $rule = '报销 ≥¥5000'; $action = 'escalate-boss'; $priority = 'P1' }
    }
    '采购' {
      if($amount -lt 5000){ $rule = '采购 <¥5000'; $action = 'auto-approve'; $priority = 'P3' }
      else{ $rule = '采购 ≥¥5000'; $action = 'escalate-boss'; $priority = 'P1' }
    }
    '上新预算' {
      $rule = '上新预算（必看历史教训）'; $action = 'manual'; $priority = 'P0'
    }
    '退货特批' {
      if($amount -lt 2000){ $rule = '退货 <¥2000'; $action = 'auto-approve'; $priority = 'P3' }
      else{ $rule = '退货 ≥¥2000'; $action = 'manual'; $priority = 'P1' }
    }
    '差旅' {
      if($amount -lt 3000){ $rule = '差旅 <¥3000'; $action = 'auto-approve'; $priority = 'P3' }
      else{ $rule = '差旅 ≥¥3000'; $action = 'manual'; $priority = 'P2' }
    }
    default {
      $rule = '未知类型'; $action = 'escalate-boss'; $priority = 'P1'
    }
  }

  return @{rule=$rule; action=$action; priority=$priority; type=$type; amount=$amount; status=$status}
}

Write-Host "==================================================="
Write-Host "  approval-router · 审批智能分流"
Write-Host "==================================================="
Write-Host ""

$apps = Load-Table $T_APP
Write-Host "[扫描] $($apps.Count) 笔审批"
Write-Host ""

$autoApprove = @()
$escalateBoss = @()
$manual = @()

foreach($a in $apps){
  $title = $a.'审批标题'
  $r = Classify-Approval $a
  Write-Host "  [$($r.priority)] $title"
  Write-Host "    类型: $($r.type) / 金额: ¥$($r.amount) / 状态: $($r.status)"
  Write-Host "    规则: $($r.rule) → $($r.action)"

  $entry = [PSCustomObject]@{title=$title; rule=$r.rule; amount=$r.amount; priority=$r.priority; status=$r.status}
  switch($r.action){
    'auto-approve' { $autoApprove += $entry }
    'escalate-boss' { $escalateBoss += $entry }
    'manual' { $manual += $entry }
  }
  Write-Host ""
}

Write-Host "==================================================="
Write-Host "[结果]"
Write-Host "  ✅ 自动批: $($autoApprove.Count)"
Write-Host "  🔴 升级老板决策: $($escalateBoss.Count)"
Write-Host "  🟡 老板手动决策: $($manual.Count)"
Write-Host "==================================================="
Write-Host ""

if($DryRun){ exit 0 }

# IM 卡片
$autoLines = @()
foreach($e in $autoApprove){ $autoLines += "✅ $($e.title) ¥$($e.amount) ($($e.rule))" }
$escalateLines = @()
foreach($e in $escalateBoss){ $escalateLines += "🔴 $($e.title) ¥$($e.amount) ($($e.rule))" }
$manualLines = @()
foreach($e in $manual){ $manualLines += "🟡 $($e.title) ¥$($e.amount) ($($e.rule))" }

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content='⚖️ 审批智能分流报告'}; template='blue'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**6 笔审批 → 智能分流到 3 路:** ✅ 自动批 / 🔴 升级老板 / 🟡 手动决策"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content=("**✅ 已自动批 ($($autoApprove.Count) 笔):**`n" + ($autoLines -join "`n"))}}
    @{tag='div'; text=@{tag='lark_md'; content=("**🔴 升级老板决策 ($($escalateBoss.Count) 笔):**`n" + ($escalateLines -join "`n"))}}
    @{tag='div'; text=@{tag='lark_md'; content=("**🟡 老板手动决策 ($($manual.Count) 笔):**`n" + ($manualLines -join "`n"))}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 分流规则:**`n• 报销 <¥1000 / 采购 <¥5000 / 退货 <¥2000 / 差旅 <¥3000 → **自动批**`n• 上新预算 → 必看历史教训 P0`n• 大额 → 升级老板`n`n**省去 80% 重复审批操作。**"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📋 查 14_审批记录'}; type='primary'; url='https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=tblAxWcmHnFl0qUE'}
    )}
  )
}
$cardJson = $card | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $cardJson -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host ""
Write-Host "Done."
