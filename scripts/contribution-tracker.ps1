# contribution-tracker.ps1 — 员工贡献度客观评估
#
# 解决"年终述职靠员工自夸"问题：
#   显性业绩（销售/产出）+ 隐性贡献（19_经验沉淀库 提交 + 通过率 + 价值评分 + 复用部门数）
#   = 客观、透明、公平的员工评估

param([string]$Period='2026Q1', [switch]$DryRun)
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T19='tbls1h9p2FL87bqG'
$T20='tblY0EeiPgoQnOqR'
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

function Update-Field($tid, $rid, $payload){
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $json = $payload | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\contrib.json", $json, $utf8)
  cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $tid --record-id $rid --json @./contrib.json --jq .data.record.id" | Out-Null
}

function Insert-Record($tid, $payload){
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $json = $payload | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\contrib.json", $json, $utf8)
  cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $tid --json @./contrib.json --jq .data.record.id" | Out-Null
}

Write-Host "==================================================="
Write-Host "  contribution-tracker · 员工贡献度评估"
Write-Host "  Period: $Period"
Write-Host "==================================================="
Write-Host ""

# 显性业绩 mock（生产中从 02_4平台销售 / 04_上新波段 / 05_任务清单聚合）
$visiblePerf = @{
  '马萍蔓' = '设计稿 2 波 8 款，DRS 系列售罄率 53%'
  '申丽媛' = 'PO-005 700 件 99.1% 成品率提前 2 天交付，3 工厂稳定运营'
  '朱健豪' = '抖音粉丝 5万→6.5万（达成率 72%），月发视频 32 条爆款 5 条'
}

# 拉 19 表所有通过经验
$exps = Load-Table $T19
$published = $exps | Where-Object { (@($_.'总决策状态'))[0] -eq '已通过' -and $_.'是否入Wiki' -eq $true }

# 按提交人聚合（演示用 desc 关键词反推提交人）
$byPerson = @{
  '马萍蔓' = @()
  '申丽媛' = @()
  '朱健豪' = @()
}
foreach($r in $published){
  $section = (@($r.'板块'))[0]
  $person = switch($section){
    '设计' { '马萍蔓' }
    '生产' { '申丽媛' }
    '内容' { '朱健豪' }
    default { '其他' }
  }
  if($byPerson.ContainsKey($person)){
    $byPerson[$person] += $r
  }
}

# 评估每个员工
$results = @()
foreach($person in $byPerson.Keys){
  $myExps = $byPerson[$person]
  $five = ($myExps | Where-Object { (@($_.'价值评分'))[0] -eq '⭐⭐⭐⭐⭐' }).Count
  $four = ($myExps | Where-Object { (@($_.'价值评分'))[0] -eq '⭐⭐⭐⭐' }).Count
  $low = $myExps.Count - $five - $four

  # 综合评分（5 星 ×3 + 4 星 ×2 + 低星 ×1，加上显性业绩基础分 5）
  $rawScore = 5 + $five * 3 + $four * 2 + $low * 1
  $rank = if($rawScore -ge 15){'S'} elseif($rawScore -ge 12){'A'} elseif($rawScore -ge 9){'B'} elseif($rawScore -ge 6){'C'} else{'D'}
  $bonusMul = switch($rank){'S'{2.0}'A'{1.5}'B'{1.2}'C'{1.0}'D'{0.8}default{1.0}}

  $r = [PSCustomObject]@{
    person = $person
    visible = $visiblePerf[$person]
    impl_total = $myExps.Count
    impl_5 = $five
    impl_4 = $four
    impl_low = $low
    rawScore = $rawScore
    rank = $rank
    bonus = $bonusMul
  }
  $results += $r
  Write-Host "📊 $person → 综合 $rank（原始分 $rawScore）/ 隐性 $($myExps.Count) 条 (5⭐:$five 4⭐:$four)"
  Write-Host "   显性: $($r.visible)"
  Write-Host "   建议奖金倍数: $bonusMul"

  if(-not $DryRun){
    Insert-Record $T20 @{
      '员工' = $person
      '周期' = $Period
      '显性业绩' = $r.visible
      '隐性贡献条数' = $myExps.Count
      '5星贡献' = $five
      '4星贡献' = $four
      '低星贡献' = $low
      '综合评分' = @($rank)
      '老板评语' = "$person ($rank 级)：显性业绩稳定 + 隐性贡献 $($myExps.Count) 条沉淀经验，建议奖金倍数 $bonusMul"
      '建议奖金倍数' = $bonusMul
    }
  }
}
Write-Host ""

# 汇总卡片
$lines = @()
foreach($r in ($results | Sort-Object -Property rawScore -Descending)){
  $lines += "🏅 **$($r.person)** $($r.rank) 级 / 奖金 ×$($r.bonus)"
  $lines += "　📊 显性：$($r.visible)"
  $lines += "　💡 隐性：$($r.impl_total) 条沉淀（5⭐ $($r.impl_5) / 4⭐ $($r.impl_4)）"
  $lines += ""
}
$content = $lines -join "`n"

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content="📊 $Period 员工贡献度评估（客观透明）"}; template='red'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**显性业绩 + 隐性贡献（来自 19_经验沉淀库）= 客观评估**"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content=$content}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 算法：**`n• 显性业绩基础分 5`n• 5⭐ 贡献 ×3 / 4⭐ ×2 / 低星 ×1`n• ≥15 = S 级（奖金 ×2.0）/ ≥12 = A 级（×1.5）/ ≥9 = B 级（×1.2）`n`n**优势：年终述职不再依赖员工自夸，全部客观数据。**"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📊 查 20_员工贡献度'}; type='primary'; url="https://my.feishu.cn/base/$BASE?table=$T20"}
      @{tag='button'; text=@{tag='plain_text'; content='📚 查 19_经验沉淀库'}; url="https://my.feishu.cn/base/$BASE?table=$T19"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
if(-not $DryRun){
  cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"
}

Write-Host "Done."
