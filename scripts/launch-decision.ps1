param(
  [string]$Tags = '色-同色系-莓果红,风-法式,品-连衣裙,料-雪纺,景-约会,景-派对',
  [string]$NewSku = 'DRS-2026-RM',
  [string]$NewName = '法式莓果红雪纺连衣裙(新品)'
)

$ErrorActionPreference = 'Stop'

$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$T_RET='tblCwJGr0HTMFtXD'
$T_APP='tblAxWcmHnFl0qUE'

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
Write-Host "  Launch Decision · $NewSku"
Write-Host "  Tags: $Tags"
Write-Host "==================================================="
Write-Host ""

$newTags = $Tags -split ','
$newCat = ($newTags | Where-Object { $_ -like '品-*' } | Select-Object -First 1) -replace '^品-',''
Write-Host "New product category: $newCat"
Write-Host ""

# Step 1: Pull data
Write-Host "[1/5] Loading 01_产品库 / 11_退货反馈 / 14_审批记录..."
$products = Load-Table $T_PROD
$returns = Load-Table $T_RET
$approvals = Load-Table $T_APP
Write-Host "  Products: $($products.Count) / Returns: $($returns.Count) / Approvals: $($approvals.Count)"
Write-Host ""

# Step 2: Score similarity for each product
Write-Host "[2/5] Scoring element similarity for all products..."
$similar = @()
foreach($p in $products){
  $pTags = @($p.'元素标签')
  $overlap = ($newTags | Where-Object { $pTags -contains $_ }).Count
  if($overlap -ge 3){
    $stat = @($p.'状态')[0]
    $sold = [int]$p.'已实销'
    $stock = [int]$p.'库存'
    $made = [int]$p.'做货数'
    $sellThru = if($made -gt 0){ [Math]::Round($sold * 100.0 / $made, 1) } else { 0 }
    $similar += [PSCustomObject]@{
      sku = $p.'款号'
      name = $p.'产品名称'
      cat = (@($p.'品类'))[0]
      status = $stat
      tags_overlap = $overlap
      sold = $sold
      stock = $stock
      made = $made
      sellThru = $sellThru
      tags = $pTags
    }
  }
}
$similar = $similar | Sort-Object -Property tags_overlap, sold -Descending
Write-Host "  Similar products (overlap >= 3): $($similar.Count)"
foreach($s in $similar){
  Write-Host "    $($s.sku) [$($s.status)] overlap=$($s.tags_overlap) sold=$($s.sold) stock=$($s.stock) sellThru=$($s.sellThru)%"
}
Write-Host ""

# Step 3: Categorize
$hits = $similar | Where-Object { $_.sellThru -ge 50 -and ($_.status -eq '在售' -or $_.status -eq '历史款') } | Select-Object -First 5
$flops = $similar | Where-Object { $_.sellThru -lt 30 -and $_.made -gt 0 } | Select-Object -First 3
$dev = $similar | Where-Object { $_.status -eq '开发中' } | Select-Object -First 3

Write-Host "[3/5] Bucketed:"
Write-Host "  HITS (sellThru >= 50%): $($hits.Count)"
foreach($h in $hits){ Write-Host "    + $($h.sku) sold $($h.sold)/$($h.made) ($($h.sellThru)%)" }
Write-Host "  FLOPS (sellThru < 30%): $($flops.Count)"
foreach($f in $flops){ Write-Host "    - $($f.sku) sold $($f.sold)/$($f.made) ($($f.sellThru)%)" }
Write-Host "  DEV: $($dev.Count)"
Write-Host ""

# Step 4: Compute recommended order qty
Write-Host "[4/5] Computing recommendation..."

if($hits.Count -gt 0){
  $avgSold = ($hits | Measure-Object -Property sold -Average).Average
  $avgMade = ($hits | Measure-Object -Property made -Average).Average
} else {
  $avgSold = 200
  $avgMade = 400
}

# 元素重合因子
$maxOverlap = 5
$avgOverlap = ($hits | Measure-Object -Property tags_overlap -Average).Average
if(-not $avgOverlap){ $avgOverlap = 3 }
$overlapFactor = [Math]::Round($avgOverlap / $maxOverlap, 2)

# 季节因子（mock：连衣裙春夏 1.1）
$seasonFactor = if($newCat -match '连衣裙|衬衫|半裙'){ 1.1 } else { 0.95 }

$baseQty = [int]([Math]::Round($avgMade * $overlapFactor * $seasonFactor))
$lowQty = [int]([Math]::Round($baseQty * 0.8))
$highQty = [int]([Math]::Round($baseQty * 1.25))

Write-Host "  avg made (hits): $avgMade"
Write-Host "  avg overlap factor: $overlapFactor"
Write-Host "  season factor: $seasonFactor"
Write-Host "  base qty: $baseQty (range $lowQty-$highQty)"
Write-Host ""

# 翻单率推算备料
$reorderRate = if($hits.Count -gt 0){
  ($hits | Where-Object { $_.sellThru -ge 80 }).Count / [Math]::Max(1, $hits.Count)
} else { 0.4 }
$fabricMultiplier = [Math]::Round(1 + $reorderRate, 2)

Write-Host "  reorder rate (hits sellThru>=80): $($reorderRate * 100)%"
Write-Host "  fabric multiplier: $fabricMultiplier x"
Write-Host ""

# 风险项：从 11 拉同品类退货
Write-Host "[5/5] Risk scan..."
$relevantReturns = @()
foreach($r in $returns){
  $sku = $r.SKU
  if(-not $sku){ continue }
  $stripped = ($sku -split ' ')[0]  # e.g. "DRS-0429-FL 莓果红/M" -> "DRS-0429-FL"
  $matched = $similar | Where-Object { $_.sku -eq $stripped }
  if($matched){
    $relevantReturns += [PSCustomObject]@{
      sku = $stripped
      reason = (@($r.'退货原因'))[0]
      voice = $r.'客户原话'
    }
  }
}
Write-Host "  Relevant returns: $($relevantReturns.Count)"
$reasonCounts = $relevantReturns | Group-Object -Property reason | Sort-Object -Property Count -Descending
foreach($g in $reasonCounts){
  Write-Host "    $($g.Name): $($g.Count) 次"
}
Write-Host ""

# 人为操作教训：从 14 拉
$lessons = @()
foreach($a in $approvals){
  $les = $a.'事后教训'
  if($les){ $lessons += $les }
}
Write-Host "  Historical lessons: $($lessons.Count)"
foreach($l in $lessons){ Write-Host "    > $l" }
Write-Host ""

# 输出 JSON
$output = [PSCustomObject]@{
  new_product = @{ sku=$NewSku; name=$NewName; tags=$newTags; category=$newCat }
  similar = @{
    hits = $hits | Select-Object sku, name, sold, made, sellThru, tags_overlap
    flops = $flops | Select-Object sku, name, sold, made, sellThru
    dev = $dev | Select-Object sku, name
  }
  recommendation = @{
    suggested_qty = $baseQty
    range = "$lowQty-$highQty"
    fabric_multiplier = $fabricMultiplier
    size_split = @{ S=25; M=40; L=25; XL=10 }
    color_split = @{ '莓果红'=50; '米白'=30; '焦糖'=20 }
    factors = @{
      avg_made_hits = $avgMade
      overlap_factor = $overlapFactor
      season_factor = $seasonFactor
      reorder_rate = $reorderRate
    }
  }
  risks = @{
    return_reasons = $reasonCounts | Select-Object @{N='reason';E={$_.Name}}, Count
    historical_lessons = $lessons
  }
  generated_at = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
}
$utf8bom = New-Object System.Text.UTF8Encoding $true
$jsonOut = $output | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\launch-decision-result.json", $jsonOut, $utf8bom)

Write-Host "==================================================="
Write-Host "  RECOMMENDATION"
Write-Host "==================================================="
Write-Host ""
Write-Host "  Suggested order qty: $baseQty (range $lowQty-$highQty)"
Write-Host "  Size split:  S25 / M40 / L25 / XL10"
Write-Host "  Color split: 莓果红 50 / 米白 30 / 焦糖 20"
Write-Host "  Fabric:      $fabricMultiplier x base (allow reorder window)"
Write-Host ""
Write-Host "  Reference HITS: $($hits.Count)"
foreach($h in ($hits | Select-Object -First 3)){
  Write-Host "    $($h.sku) - $($h.sold)/$($h.made) ($($h.sellThru)%)"
}
Write-Host ""
Write-Host "  Risk reasons (from 11_退货反馈):"
foreach($g in $reasonCounts){ Write-Host "    $($g.Name) x$($g.Count)" }
Write-Host ""
Write-Host "  Historical lessons (from 14_审批记录):"
foreach($l in $lessons){ Write-Host "    > $l" }
Write-Host ""
Write-Host "Saved to %TEMP%\launch-decision-result.json"
