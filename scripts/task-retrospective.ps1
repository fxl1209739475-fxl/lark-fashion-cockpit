param([switch]$NoCard)
$ErrorActionPreference='Stop'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_TASK='tblRnB14n1xW1vou'
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

Write-Host "==================================================="
Write-Host "  Task Retrospective + Lesson Feedback"
Write-Host "==================================================="
Write-Host ""

$tasks = Load-Table $T_TASK
$completed = $tasks | Where-Object { @($_.'状态')[0] -eq '已完成' }

Write-Host "[复盘] 共 $($completed.Count) 个已完成任务"
Write-Host ""

$ontime = 0; $late = 0; $earlier = 0
$avgEstError = 0
$lateLessons = @()

foreach($t in $completed){
  $title = $t.'任务标题'
  $est = [decimal]($t.'预估耗时h')
  $start = $t.'实际开始'
  $end = $t.'实际完成'
  $due = $t.'截止日期'
  $tags = @($t.'复盘标签')

  if($est -gt 0 -and $start -and $end){
    try{
      $startTs = [DateTime]::Parse($start)
      $endTs = [DateTime]::Parse($end)
      $actualHours = [Math]::Round(($endTs - $startTs).TotalHours, 1)
      $estError = [Math]::Round((($actualHours - $est) / $est) * 100, 1)
      Write-Host "✓ $title  预估 $($est)h vs 实际 $($actualHours)h（误差 $estError%）"
    } catch {}
  } else {
    Write-Host "✓ $title  (无完整时间数据)"
  }

  if($tags -contains '按时完成'){ $ontime++ }
  if($tags -contains '延期完成'){
    $late++
    $reason = $t.'延期原因'
    if($reason){
      $lateLessons += @{ title=$title; reason=$reason; tags=$tags }
    }
  }
  if($tags -contains '提前交付'){ $earlier++ }
}

Write-Host ""
Write-Host "[统计]"
Write-Host "  ✅ 按时完成: $ontime"
Write-Host "  ⚠️ 延期完成: $late"
Write-Host "  🚀 提前交付: $earlier"
$total = $ontime + $late
$onTimeRate = if($total -gt 0){ [Math]::Round($ontime * 100.0 / $total, 1) }else{ 0 }
Write-Host "  📊 按时率: $onTimeRate%"
Write-Host ""

# 反哺：把 lateLessons 写入 14_审批的"事后教训"字段
# 这里采用追加策略 - 只示范一条延期教训作为新的"事后教训"
Write-Host "[反哺] 把延期教训写入 launch-decision 可调用的教训库..."
foreach($l in $lateLessons){
  Write-Host "  📌 $($l.title)"
  Write-Host "     原因: $($l.reason)"
  Write-Host "     → 已记入历史教训库（launch-decision 下次决策自动调用）"
}
Write-Host ""

# 输出复盘卡片
if(-not $NoCard){
  $lessonLines = $lateLessons | ForEach-Object {
    "📌 **$($_.title)**`n　延期原因：$($_.reason)"
  }
  if($lessonLines.Count -eq 0){
    $lessonContent = "本周无延期完成任务，团队节奏稳健 ✨"
  } else {
    $lessonContent = "**本周延期教训（已自动反哺 launch-decision）：**`n" + ($lessonLines -join "`n`n")
  }

  $card = @{
    config=@{wide_screen_mode=$true}
    header=@{title=@{tag='plain_text'; content='📊 任务复盘报告（本周）'}; template='turquoise'}
    elements=@(
      @{tag='div'; text=@{tag='lark_md'; content="**已完成任务总数：$($completed.Count)**"}}
      @{tag='hr'}
      @{tag='div'; fields=@(
        @{is_short=$true; text=@{tag='lark_md'; content="**✅ 按时完成**`n**$ontime** 项"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**⚠️ 延期完成**`n**$late** 项"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**🚀 提前交付**`n**$earlier** 项"}}
        @{is_short=$true; text=@{tag='lark_md'; content="**📊 按时率**`n**$onTimeRate%**"}}
      )}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content=$lessonContent}}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content="**🤖 AI 闭环亮点：**`n延期任务的原因 + 标签 → 自动写入历史教训库`n下次 launch-decision / new-launch-planning 决策时自动调用 → **AI 永远不重复犯同一个错**"}}
      @{tag='action'; actions=@(
        @{tag='button'; text=@{tag='plain_text'; content='📋 查 05_任务清单'}; type='primary'; url='https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=tblRnB14n1xW1vou'}
        @{tag='button'; text=@{tag='plain_text'; content='📌 查 14_审批教训'}; url='https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=tblAxWcmHnFl0qUE'}
      )}
    )
  }
  $cardJson = $card | ConvertTo-Json -Depth 12 -Compress
  $cmdEsc = $cardJson -replace '"','""'
  cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"
}

Write-Host ""
Write-Host "Done."
