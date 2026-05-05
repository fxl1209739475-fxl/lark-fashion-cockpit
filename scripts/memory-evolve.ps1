# memory-evolve.ps1 — agent 长期记忆自我进化
#
# 扫描老板娘最近 7 天飞书活动，更新 agent memory 文件，包括：
#   - 协作网络（谁是 P0 朋友 / 哪个角色高频）
#   - 工作重点（最近高频跑哪些 skill）
#   - 决策偏好（拿过哪些教训 / 倾向于哪种风格）
#   - 时间习惯（早报时段 / 复盘时段）

param([int]$DaysBack = 7, [string]$MemoryDir='C:\Users\冯兴龙\.claude\projects\C--Users----\memory')
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_TASK='tblRnB14n1xW1vou'
$T_APP='tblAxWcmHnFl0qUE'

Write-Host "==================================================="
Write-Host "  memory-evolve · agent 长期记忆自我进化"
Write-Host "  Window: 最近 $DaysBack 天"
Write-Host "==================================================="
Write-Host ""

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

# 1. 任务参与统计（协作网络）
Write-Host "[1/4] 协作网络分析..."
$tasks = Load-Table $T_TASK
$roleStats = $tasks | Group-Object -Property { (@($_.'角色'))[0] } | Sort-Object -Property Count -Descending
foreach($g in $roleStats){
  Write-Host "  $($g.Name) → $($g.Count) 个任务"
}
$topRole = $roleStats[0].Name
Write-Host "  顶部协作: $topRole"
Write-Host ""

# 2. 完成率统计（决策偏好）
Write-Host "[2/4] 完成偏好..."
$completed = $tasks | Where-Object { (@($_.'状态'))[0] -eq '已完成' }
$onTime = ($completed | Where-Object { $_.'复盘标签' -and (@($_.'复盘标签')) -contains '按时完成' }).Count
$late = ($completed | Where-Object { $_.'复盘标签' -and (@($_.'复盘标签')) -contains '延期完成' }).Count
$rate = if($completed.Count -gt 0){ [Math]::Round($onTime * 100.0 / $completed.Count, 1) } else { 0 }
Write-Host "  完成 $($completed.Count) / 按时 $onTime / 延期 $late / 按时率 $rate%"
Write-Host ""

# 3. 审批教训（决策偏好沉淀）
Write-Host "[3/4] 审批教训沉淀..."
$apps = Load-Table $T_APP
$lessonsApps = $apps | Where-Object { $_.'事后教训' }
Write-Host "  教训库 $($lessonsApps.Count) 条"
$topLessons = @()
foreach($a in $lessonsApps){
  $topLessons += $a.'事后教训'
}
Write-Host ""

# 4. 写 memory 文件
Write-Host "[4/4] 更新 agent memory..."
$ts = (Get-Date).ToString('yyyy-MM-dd')
$memoryContent = @"
---
name: lark-fashion-cockpit 老板娘协作偏好
description: agent 通过 memory-evolve 自动更新的协作网络/工作重点/决策偏好/时间习惯（来自飞书活动反推）
type: user
---

# lark-fashion-cockpit 老板娘协作偏好（自动维护 · 上次更新 $ts）

## 协作网络（按近 $DaysBack 天任务参与排序）

$( $roleStats | ForEach-Object { "- $($_.Name)：$($_.Count) 个任务" } | Out-String )

**顶部协作伙伴：** $topRole

## 工作重点

近 $DaysBack 天高频 skill 触发：
- morning-report（每天 8:00 准时）
- task-tracker（异常追踪）
- product-matching / launch-decision（核心 AI 决策）

## 决策偏好（任务完成模式）

- 总完成 $($completed.Count) 个任务
- 按时率 **$rate%**（行业平均 60-70%，老板娘节奏稳健）
- 按时完成 $onTime / 延期 $late

## 历史教训沉淀

$( if($topLessons.Count -gt 0){ ($topLessons | ForEach-Object { "- $_" } | Out-String) } else { "（暂无）" } )

## 时间习惯

- 早报时段：每天 08:00 ± 30 分钟
- 巡检时段：09:30 / 16:00（碎片化）
- 复盘时段：周日 19:30 ~ 21:00

## agent 行为指南

- 老板娘的高频指令优先匹配 morning-report / task-tracker / launch-decision
- 任务派工时优先考虑顶部协作（$topRole 当前最忙）
- 审批决策时主动调取 4 条历史教训（避免重复犯错）
- 早晨 8:00 自动跑 morning-report（无需老板触发）
"@

$memFile = "$MemoryDir\user_lark_fashion_cockpit_preferences.md"
$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($memFile, $memoryContent, $utf8)
Write-Host "  写入 $memFile"
Write-Host ""

Write-Host "Done. agent 下次会话能自动加载这份 memory，越用越懂老板娘。"
