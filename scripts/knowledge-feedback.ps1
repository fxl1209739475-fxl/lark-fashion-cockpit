# knowledge-feedback.ps1 — 智能助手反哺日常工作
#
# 员工日常说一件事 → AI 实时检索 19_经验沉淀库 → 给出"别人犯过/有人用过"提示
# 输入：员工 query（IM 消息或脚本调用）
# 输出：相关经验/教训/建议 + 联系人

param(
  [Parameter(Mandatory=$true)][string]$Query,
  [string]$Submitter='匿名'
)
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T19='tbls1h9p2FL87bqG'
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
Write-Host "  knowledge-feedback · 智能反哺"
Write-Host "  Query: $Query"
Write-Host "==================================================="
Write-Host ""

$records = Load-Table $T19
$published = $records | Where-Object { (@($_.'总决策状态'))[0] -eq '已通过' -and $_.'是否入Wiki' -eq $true }
Write-Host "[扫描] 知识库 $($published.Count) 条已通过经验"
Write-Host ""

# 关键词匹配（生产可换 embeddings）
$keywords = $Query -split '\s+|,|，|/|的'
$matched = @()
foreach($r in $published){
  $score = 0
  $hits = @()
  foreach($kw in $keywords){
    if($kw.Length -lt 2){ continue }
    if($r.'经验标题' -match $kw){ $score += 3; $hits += "标题含'$kw'" }
    if($r.'详细描述' -match $kw){ $score += 2; $hits += "描述含'$kw'" }
  }
  if($score -gt 0){
    $matched += [PSCustomObject]@{
      record = $r; score = $score; hits = ($hits | Select-Object -Unique) -join ' / '
    }
  }
}
$matched = $matched | Sort-Object -Property score -Descending | Select-Object -First 5

Write-Host "[匹配] $($matched.Count) 条相关经验"
Write-Host ""

# 输出
$tipsLines = @()
foreach($m in $matched){
  $r = $m.record
  $type = (@($r.'类型'))[0]
  $section = (@($r.'板块'))[0]
  $stars = (@($r.'价值评分'))[0]
  $emoji = switch($type){
    '成功经验' {'✅'}
    '失败教训' {'⚠️'}
    '改进建议' {'💡'}
    default {'📌'}
  }
  $tipsLines += "$emoji **[$type · $section · $stars]** $($r.'经验标题')"
  $tipsLines += "　$($r.'详细描述'.Substring(0, [Math]::Min(100, $r.'详细描述'.Length)))..."
  $tipsLines += "　🎯 匹配：$($m.hits)"
  $tipsLines += ""
  Write-Host "$emoji [$type/$section/$stars] $($r.'经验标题')"
  Write-Host "   匹配：$($m.hits)"
}
Write-Host ""

if($matched.Count -eq 0){
  Write-Host "[反馈] 未匹配到相关经验"
  exit 0
}

# IM 卡片
$tipsContent = $tipsLines -join "`n"
$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content="🤖 知识库反哺：跟你问的事相关的 $($matched.Count) 条经验"}; template='turquoise'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**$Submitter 问：** $Query`n`n**🤖 AI 实时从 19_经验沉淀库 检索（按价值评分排序）：**"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content=$tipsContent}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🚀 这是 lark-fashion-cockpit 的组织学习闭环 #3：**`n员工日常 ↔ 知识库实时检索 ↔ AI 提示'别人犯过/有人用过/可联系谁'`n`n**经验不再睡在 Wiki 里，而是在员工每次决策时主动出现。**"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📚 查全部经验库'}; type='primary'; url="https://my.feishu.cn/base/$BASE?table=$T19"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host "Done."
