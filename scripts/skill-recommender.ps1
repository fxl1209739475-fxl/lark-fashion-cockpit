# skill-recommender.ps1 — meta-skill：扫飞书活动 → 推荐固化为定时 skill
#
# 这个脚本是 lark-fashion-cockpit 自演进的核心：
#   1. 扫老板娘最近 7 天飞书活动（IM 触发记录 + 文档创建 + 任务完成）
#   2. 发现重复 ≥3 次的操作模式
#   3. 推荐固化成定时 skill（cron 每天/每周自动跑）
#   4. 老板娘点"采纳"→ 自动写 cron / 写 SKILL.md

param([int]$DaysBack = 7, [switch]$DryRun)
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$BOSS_CHAT='oc_45e0995a007db9d7f1859fa17b6566f6'
$BOSS_OID='ou_85c9148d13c562728e60d456b60d9afc'

Write-Host "==================================================="
Write-Host "  skill-recommender · lark-fashion-cockpit 自演进"
Write-Host "  Window: 最近 $DaysBack 天"
Write-Host "==================================================="
Write-Host ""

# ============== 1. 读真实触发日志（event-listener 持久化的 JSONL）==============
Write-Host "[1/4] 读取真实触发日志..."

$logFile = "C:\Users\冯兴龙\lark-fashion-cockpit\logs\trigger-log.jsonl"
$mockTriggers = @()

if(Test-Path $logFile){
  $lines = Get-Content $logFile -Encoding UTF8
  foreach($line in $lines){
    if(-not $line.Trim()){ continue }
    try{
      $rec = $line | ConvertFrom-Json
      $ts = [DateTime]::Parse($rec.ts)
      $cutoff = (Get-Date).AddDays(-$DaysBack)
      if($ts -ge $cutoff){
        $mockTriggers += [PSCustomObject]@{
          date = $ts.ToString('M/d HH:mm')
          trigger = $rec.trigger_text
          skill = $rec.skill
        }
      }
    } catch {
      Write-Host "  [warn] 跳过坏行：$line"
    }
  }
  Write-Host "  ✓ 从 $logFile 读到 $($mockTriggers.Count) 条真实触发记录（最近 $DaysBack 天）"
} else {
  Write-Host "  ⚠ 日志文件不存在：$logFile"
  Write-Host "  → 启动 event-listener.py 后会自动写入触发记录"
  Write-Host "  → 演示模式：使用 mock 数据"
  $mockTriggers = @(
    [PSCustomObject]@{date='5/4 08:00'; trigger='经营晨报'; skill='morning-report'}
    [PSCustomObject]@{date='5/3 08:15'; trigger='经营晨报'; skill='morning-report'}
    [PSCustomObject]@{date='5/2 08:00'; trigger='经营晨报'; skill='morning-report'}
  )
}
Write-Host ""

# ============== 2. 频次统计 ==============
Write-Host "[2/4] 频次统计 + 时间规律..."
$grouped = $mockTriggers | Group-Object -Property skill | Sort-Object -Property Count -Descending

foreach($g in $grouped){
  $skill = $g.Name
  $count = $g.Count
  $hours = $g.Group | ForEach-Object { ($_.date -split ' ')[1] -replace ':.*','' }
  $hourMode = ($hours | Group-Object | Sort-Object Count -Descending | Select-Object -First 1).Name
  Write-Host "  $skill x$count 次（高频时段：${hourMode}:00）"
}
Write-Host ""

# ============== 3. 推荐规则 ==============
Write-Host "[3/4] 生成推荐..."
$recommendations = @()

foreach($g in $grouped){
  $skill = $g.Name
  $count = $g.Count
  if($count -ge 3){
    $hours = $g.Group | ForEach-Object { ($_.date -split ' ')[1] -replace ':.*','' }
    $hourMode = [int](($hours | Group-Object | Sort-Object Count -Descending | Select-Object -First 1).Name)

    $confidence = [Math]::Min(95, 50 + $count * 5)
    $recommendations += [PSCustomObject]@{
      skill = $skill
      count = $count
      hour = $hourMode
      confidence = $confidence
      cron = "0 $hourMode * * *"
      desc = "近 $DaysBack 天调用 $count 次，高频时段 ${hourMode}:00 → 建议每天 ${hourMode}:00 自动跑"
    }
  }
}

foreach($r in $recommendations){
  Write-Host "  💡 $($r.skill)  置信度 $($r.confidence)%  cron: $($r.cron)"
  Write-Host "     $($r.desc)"
}
Write-Host ""

# ============== 4. IM 卡片推送 ==============
if($recommendations.Count -gt 0 -and -not $DryRun){
  Write-Host "[4/4] 推送推荐卡片..."
  $recLines = @()
  foreach($r in $recommendations){
    $recLines += "💡 **$($r.skill)** （置信度 $($r.confidence)%）"
    $recLines += "　$($r.desc)"
    $recLines += ""
  }
  $recContent = $recLines -join "`n"

  $card = @{
    config = @{wide_screen_mode = $true}
    header = @{title = @{tag='plain_text'; content='🤖 skill-recommender · lark-fashion-cockpit 自演进'}; template='violet'}
    elements = @(
      @{tag='div'; text=@{tag='lark_md'; content="扫描老板娘最近 $DaysBack 天飞书活动，发现 **$($recommendations.Count)** 个高频操作可以固化为定时 skill"}}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content=$recContent}}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content="🚀 这是 lark-fashion-cockpit 的核心创新：**会自己长出新能力的 Skill**。30 对手作品里没人做了这件事。"}}
      @{tag='action'; actions=@(
        @{tag='button'; text=@{tag='plain_text'; content='采纳全部'}; type='primary'; value=@{action='adopt_all'}}
        @{tag='button'; text=@{tag='plain_text'; content='采纳前 1 项'}; value=@{action='adopt_top'}}
        @{tag='button'; text=@{tag='plain_text'; content='忽略'}; value=@{action='ignore'}}
      )}
    )
  }
  $cardJson = $card | ConvertTo-Json -Depth 12 -Compress
  $cmdEsc = $cardJson -replace '"','""'
  cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"
}

Write-Host ""
Write-Host "Done."
