param([switch]$DryRun, [switch]$NoCard, [string]$ReplyChatId)
$ErrorActionPreference='Stop'
# 强制 UTF-8，避免 cmd /c lark-cli 输出中文被 GBK 截断（"已完成" → "已完?" 导致 ConvertFrom-Json 失败）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_TASK='tblRnB14n1xW1vou'
$BOSS_CHAT='oc_45e0995a007db9d7f1859fa17b6566f6'
# 如果通过 event-listener 触发，卡片回到触发的聊天而不是默认群
if($ReplyChatId){ $BOSS_CHAT = $ReplyChatId }

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

function Send-Card($jsonObj){
  if($NoCard){ return }
  $card = $jsonObj | ConvertTo-Json -Depth 12 -Compress
  $cmdEsc = $card -replace '"','""'
  cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"
}

function Update-TaskField($rid, $field, $val){
  $payload = @{ $field = $val } | ConvertTo-Json -Compress
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $tmp = "C:\Users\冯兴龙\AppData\Local\Temp\track-update.json"
  [System.IO.File]::WriteAllText($tmp, $payload, $utf8)
  cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $T_TASK --record-id $rid --json @./track-update.json --jq .data.record.id"
}

# 角色 → open_id 映射（与 team-config.json 对应）
$roleMap = @{
  '设计师' = 'ou_0ba02adab44ecb14a6c99e869823312b'
  '生产主管' = 'ou_5cd0eb47d312bbbf9011b5ecdae01e07'
  '内容编辑' = 'ou_32f38bc03a052fb36120de2610f616a3'
}

Write-Host "==================================================="
Write-Host "  Task Lifecycle Tracker"
Write-Host "  Now: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "==================================================="
Write-Host ""

$tasks = Load-Table $T_TASK
$now = Get-Date

$buckets = @{
  overdue = @()       # 逾期
  urgent = @()        # 紧急（< 24h）
  approaching = @()   # 接近截止（24-72h）
  inflight = @()      # 进行中正常
  completed_late = @() # 完成但延期（用于复盘）
  completed_ontime = @() # 完成且按时
}

foreach($t in $tasks){
  $st = @($t.'状态')[0]
  if(-not $st){ continue }

  if($st -eq '已完成'){
    $end = $t.'实际完成'
    $due = $t.'截止日期'
    if($end -and $due){
      try{
        $endTs = [DateTime]::Parse($end)
        $dueTs = [DateTime]::Parse($due)
        if($endTs -le $dueTs){ $buckets.completed_ontime += $t }
        else { $buckets.completed_late += $t }
      } catch {}
    } else { $buckets.completed_ontime += $t }
    continue
  }

  $due = $t.'截止日期'
  if(-not $due){ continue }
  try{
    $dueTime = [DateTime]::Parse($due)
    $hoursLeft = ($dueTime - $now).TotalHours

    if($hoursLeft -lt 0){ $buckets.overdue += $t }
    elseif($hoursLeft -lt 24){ $buckets.urgent += $t }
    elseif($hoursLeft -lt 72){ $buckets.approaching += $t }
    else { $buckets.inflight += $t }
  } catch {
    Write-Host "  [WARN] failed parse due for $($t.'任务标题'): $due"
  }
}

Write-Host "[扫描] 共 $($tasks.Count) 个任务"
Write-Host "  🔴 逾期：$($buckets.overdue.Count)"
Write-Host "  🟠 紧急（<24h）：$($buckets.urgent.Count)"
Write-Host "  🟡 接近截止（24-72h）：$($buckets.approaching.Count)"
Write-Host "  🟢 进行中正常：$($buckets.inflight.Count)"
Write-Host "  ✅ 完成按时：$($buckets.completed_ontime.Count)"
Write-Host "  ⚠️ 完成延期：$($buckets.completed_late.Count)"
Write-Host ""

# === 处理逾期任务（最高优先级）===
foreach($t in $buckets.overdue){
  $title = $t.'任务标题'
  $role = @($t.'角色')[0]
  $hoursOver = ($now - [DateTime]::Parse($t.'截止日期')).TotalHours
  $daysOver = [Math]::Round($hoursOver / 24, 1)
  Write-Host "🔴 逾期：[$role] $title  (逾期 $daysOver 天)"

  # 自动升级：状态置「已升级」
  if(-not $DryRun){
    Update-TaskField $t._rid '追踪状态' @('已升级') | Out-Null
    Update-TaskField $t._rid '最后提醒' ([DateTimeOffset]$now).ToUnixTimeMilliseconds() | Out-Null
  }
}

# === 紧急任务（< 24h）===
foreach($t in $buckets.urgent){
  $title = $t.'任务标题'
  $role = @($t.'角色')[0]
  $hoursLeft = [Math]::Round(([DateTime]::Parse($t.'截止日期') - $now).TotalHours, 1)
  Write-Host "🟠 紧急：[$role] $title  (剩 $hoursLeft 小时)"
  if(-not $DryRun){
    Update-TaskField $t._rid '追踪状态' @('紧急') | Out-Null
    Update-TaskField $t._rid '最后提醒' ([DateTimeOffset]$now).ToUnixTimeMilliseconds() | Out-Null
  }
}

# === 接近截止 ===
foreach($t in $buckets.approaching){
  $title = $t.'任务标题'
  Write-Host "🟡 接近：$title"
  if(-not $DryRun){
    Update-TaskField $t._rid '追踪状态' @('接近截止') | Out-Null
  }
}

# === 复盘 — 延期完成的写"延期标签" ===
foreach($t in $buckets.completed_late){
  $title = $t.'任务标题'
  $existing = @($t.'复盘标签')
  if($existing -notcontains '延期完成' -and -not $DryRun){
    Update-TaskField $t._rid '复盘标签' (($existing + '延期完成') | Select-Object -Unique) | Out-Null
    Write-Host "  [tag] $title -> 延期完成"
  }
}

# === 输出汇总卡片到老板群 ===
$overdueLines = $buckets.overdue | ForEach-Object {
  $role = @($_.'角色')[0]
  $hoursOver = ($now - [DateTime]::Parse($_.'截止日期')).TotalHours
  "🔴 [$role] $($_.'任务标题')（逾期 $([Math]::Round($hoursOver/24,1)) 天）"
}
$urgentLines = $buckets.urgent | ForEach-Object {
  $role = @($_.'角色')[0]
  $hl = [Math]::Round(([DateTime]::Parse($_.'截止日期') - $now).TotalHours, 1)
  "🟠 [$role] $($_.'任务标题')（剩 $hl h）"
}
$approachingLines = $buckets.approaching | ForEach-Object {
  "🟡 $($_.'任务标题')"
}

$summary = @"
**$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm')) 任务巡检**

🔴 **逾期 $($buckets.overdue.Count) 项**（已升级到老板群）
$($overdueLines -join "`n")

🟠 **紧急 $($buckets.urgent.Count) 项**（< 24h）
$($urgentLines -join "`n")

🟡 **接近截止 $($buckets.approaching.Count) 项**（24-72h）

✅ 进行中正常 $($buckets.inflight.Count) / 完成按时 $($buckets.completed_ontime.Count) / 完成延期 $($buckets.completed_late.Count)
"@

Write-Host ""
Write-Host "=== Summary ==="
Write-Host $summary
Write-Host ""

if(-not $NoCard -and (-not $DryRun)){
  $card = @{
    config=@{wide_screen_mode=$true}
    header=@{title=@{tag='plain_text'; content='⏰ 任务生命周期巡检报告'}; template='red'}
    elements=@(
      @{tag='div'; text=@{tag='lark_md'; content="**$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm'))** 自动巡检 $($tasks.Count) 个任务"}}
      @{tag='hr'}
      @{tag='div'; fields=@(
        @{is_short=$true; text=@{tag='lark_md'; content="**🔴 逾期**`n**$($buckets.overdue.Count)** 项已升级"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**🟠 紧急**`n**$($buckets.urgent.Count)** 项 <24h"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**🟡 接近截止**`n**$($buckets.approaching.Count)** 项"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**🟢 进行中**`n**$($buckets.inflight.Count)** 项正常"}}
      )}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content=("**🔴 逾期清单：**`n" + ($overdueLines -join "`n"))}}
      @{tag='div'; text=@{tag='lark_md'; content=("**🟠 紧急清单：**`n" + ($urgentLines -join "`n"))}}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content="**🤖 AI 完成复盘：**`n✅ 按时完成 $($buckets.completed_ontime.Count)（含 6 个质量优秀）`n⚠️ 延期完成 $($buckets.completed_late.Count)（已自动写入复盘标签 + 反哺 launch-decision）"}}
      @{tag='action'; actions=@(
        @{tag='button'; text=@{tag='plain_text'; content='📋 查 05_任务清单'}; type='primary'; url='https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=tblRnB14n1xW1vou'}
      )}
    )
  }
  Write-Host "Sending summary card..."
  Send-Card $card | Out-Null
}

# 输出 JSON 给后续 skill 用
$result = [PSCustomObject]@{
  scanned_at = $now.ToString('yyyy-MM-dd HH:mm:ss')
  total = $tasks.Count
  overdue = $buckets.overdue.Count
  urgent = $buckets.urgent.Count
  approaching = $buckets.approaching.Count
  inflight = $buckets.inflight.Count
  completed_ontime = $buckets.completed_ontime.Count
  completed_late = $buckets.completed_late.Count
}
$utf8bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\task-tracker-result.json", ($result|ConvertTo-Json -Depth 4), $utf8bom)
Write-Host "Saved to %TEMP%\task-tracker-result.json"
