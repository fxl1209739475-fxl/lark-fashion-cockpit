param([string]$Sku='DRS-0429-FL', [int]$TopN=3, [string]$ReplyChatId='')
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$T_PAIR='tblHZAHcOzkcD4gC'

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

$products = Load-Table $T_PROD
$pairs = Load-Table $T_PAIR

$main = $products | Where-Object { $_.'款号' -eq $Sku } | Select-Object -First 1
if(-not $main){ Write-Host "Not found: $Sku"; exit 1 }
$mainTags = @($main.'元素标签')
$mainCat = @($main.'品类')[0]
$mainRid = $main._rid

Write-Host ("Main: " + $main.'款号' + " - " + $main.'产品名称')
Write-Host ("  Tags: " + ($mainTags -join ' / '))
Write-Host ("  Category: " + $mainCat)
Write-Host ""

$candidates = $products | Where-Object {
  $st = @($_.'状态')[0]
  ($st -eq '在售' -or ($st -eq '历史款' -and [int]$_.'库存' -gt 0)) -and
  ($_.'款号' -ne $Sku) -and (@($_.'品类')[0] -ne $mainCat)
}
Write-Host ("Candidates: " + $candidates.Count)
Write-Host ""

$complementary = @{
  '连衣裙' = @('外套','针织','配饰','上衣','下装','裤装','半裙','衬衫')
  '上衣'   = @('裤装','半裙','外套','下装','针织')
  '下装'   = @('上衣','外套','针织','衬衫')
  '裤装'   = @('上衣','外套','针织','衬衫')
  '半裙'   = @('上衣','针织','衬衫','外套','连衣裙')
  '针织'   = @('裤装','半裙','下装','连衣裙','上衣')
  '外套'   = @('上衣','下装','连衣裙','衬衫','裤装','半裙','针织')
  '衬衫'   = @('裤装','半裙','下装','外套')
}

$maxUsage = 1
foreach($p in $pairs){ if([int]$p.'使用次数' -gt $maxUsage){ $maxUsage = [int]$p.'使用次数' } }

$scored = @()
foreach($c in $candidates){
  $score = 0
  $reasons = @()
  $cTags = @($c.'元素标签')

  $colorMatch = ($mainTags | Where-Object { $_ -like '色-*' -and $cTags -contains $_ }).Count
  $styleMatch = ($mainTags | Where-Object { $_ -like '风-*' -and $cTags -contains $_ }).Count
  $sceneMatch = ($mainTags | Where-Object { $_ -like '景-*' -and $cTags -contains $_ }).Count

  if($colorMatch -gt 0){ $score += 30; $reasons += "color+30" }
  if($styleMatch -gt 0){ $score += 25; $reasons += "style+25" }
  if($sceneMatch -gt 0){ $score += 15; $reasons += "scene+15" }

  $cCat = @($c.'品类')[0]
  $compl = $complementary[$mainCat]
  if($compl -and ($compl -contains $cCat)){ $score += 20; $reasons += "complementary+20" }

  $cRid = $c._rid
  $matchedPair = $null
  foreach($p in $pairs){
    $mp = @($p.'主推款')
    $sp = @($p.'搭配款')
    $mpHasMain = ($mp.Count -gt 0 -and $mp[0].id -eq $mainRid)
    $mpHasCand = ($mp.Count -gt 0 -and $mp[0].id -eq $cRid)
    $spHasMain = (@($sp | Where-Object { $_.id -eq $mainRid }).Count -gt 0)
    $spHasCand = (@($sp | Where-Object { $_.id -eq $cRid }).Count -gt 0)
    if(($mpHasMain -and $spHasCand) -or ($spHasMain -and $mpHasCand)){
      $matchedPair = $p
      break
    }
  }
  if($matchedPair){
    $w = [Math]::Min(10, [Math]::Round(([int]$matchedPair.'使用次数' / $maxUsage) * 10))
    $score += $w + 10
    $reasons += ("locked+" + ($w+10))
  }

  $inv = [int]$c.'库存'
  $sold = [int]$c.'已实销'
  $dailySold = if($sold -gt 0){ $sold / 90.0 } else { 1 }
  $daysLeft = if($dailySold -gt 0){ $inv / $dailySold } else { 999 }

  if($inv -le 10){ $score -= 50; $reasons += "near_zero-50" }
  elseif($daysLeft -lt 7){ $score += 20; $reasons += "urgent_clear+20" }
  elseif($daysLeft -gt 30){ $score += 10; $reasons += "slow_clear+10" }

  $cStatus = @($c.'状态')[0]
  if($cStatus -eq '历史款'){ $score += 15; $reasons += "old_stock+15" }

  $scored += [PSCustomObject]@{
    sku = $c.'款号'
    name = $c.'产品名称'
    cat = $cCat
    inv = $inv
    days = [Math]::Round($daysLeft, 1)
    score = $score
    reasons = ($reasons -join ' ')
  }
}

$top = $scored | Sort-Object -Property score -Descending | Select-Object -First $TopN
Write-Host "Top recommendations:"
$rank = 0
$medals = @('1st','2nd','3rd')
foreach($r in $top){
  $rank++
  Write-Host ($medals[$rank-1] + " " + $r.sku + " (" + $r.name + ")")
  Write-Host ("   score=" + $r.score + " inv=" + $r.inv + " days=" + $r.days + " " + $r.reasons)
}

$output = [PSCustomObject]@{
  main = @{ sku=$Sku; name=$main.'产品名称'; tags=$mainTags; cat=$mainCat }
  recommendations = $top
  generated_at = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
}
$utf8bom = New-Object System.Text.UTF8Encoding $true
$jsonOut = $output | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\matching-result.json", $jsonOut, $utf8bom)
Write-Host ""
Write-Host "Saved to: %TEMP%\matching-result.json"

# 发飞书卡片（如果有 ReplyChatId）
if($ReplyChatId){
  $cardElements = @(
    @{tag='div'; text=@{tag='lark_md'; content=("**主款：** ``$($main.'款号')`` - $($main.'产品名称')`n**品类：** $mainCat | **标签：** $($mainTags -join ' / ')")}},
    @{tag='hr'}
  )
  $rank = 0
  foreach($r in $top){
    $rank++
    $invMsg = if($r.inv -le 10){ "⚠️ 库存仅 $($r.inv) 件" } else { "✅ 库存 $($r.inv) 件" }
    $cardElements += @{tag='div'; text=@{tag='lark_md'; content=("**[$rank] ``$($r.sku)``** · $($r.name)`n品类：$($r.cat) | $invMsg | 售完约 $($r.days) 天`n🎯 **评分 $($r.score) 分** · $($r.reasons)")}}
  }
  $cardElements += @{tag='hr'}
  $cardElements += @{tag='action'; actions=@(
    @{tag='button'; text=@{tag='plain_text'; content='📋 查 17 表完整搭配'}; type='primary'; url=("https://my.feishu.cn/base/$BASE" + "?table=$T_PAIR")}
  )}
  $card = @{
    config=@{wide_screen_mode=$true}
    header=@{title=@{tag='plain_text'; content=("🛍 $Sku 搭配推荐 TOP $TopN")}; template='blue'}
    elements=$cardElements
  }
  $cardJson = $card | ConvertTo-Json -Depth 12 -Compress
  Write-Host "Sending card to $ReplyChatId ..."
  # 用 cmd /c 包装绕开 PowerShell 5.1 把 JSON 引号吃掉的 bug
  $cardEsc = $cardJson -replace '"', '""'
  cmd /c "lark-cli im +messages-send --chat-id $ReplyChatId --msg-type interactive --content `"$cardEsc`"" | Out-Null
}
