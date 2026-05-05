param([decimal]$CostRatio = 0.4)

$ErrorActionPreference='Stop'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$T_SALES='tbll7UHbL6kDxZua'

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
Write-Host "  Profit Analysis · Cost Ratio = $($CostRatio*100)%"
Write-Host "==================================================="
Write-Host ""

$products = Load-Table $T_PROD
$sales = Load-Table $T_SALES

# 单品利润
Write-Host "[1/3] Per-product profit ranking..."
$ranking = @()
foreach($p in $products){
  $sold = [int]$p.'已实销'
  $price = [decimal]$p.'售价'
  $cost = $price * $CostRatio
  $unitProfit = $price - $cost
  $totalRevenue = $sold * $price
  $totalProfit = $sold * $unitProfit
  $stat = @($p.'状态')[0]
  $ranking += [PSCustomObject]@{
    sku = $p.'款号'
    name = $p.'产品名称'
    status = $stat
    sold = $sold
    price = $price
    cost = [Math]::Round($cost,2)
    unit_profit = [Math]::Round($unitProfit,2)
    revenue = [Math]::Round($totalRevenue,0)
    profit = [Math]::Round($totalProfit,0)
  }
}
$ranking = $ranking | Sort-Object -Property profit -Descending

$totalRev = ($ranking | Measure-Object -Property revenue -Sum).Sum
$totalProf = ($ranking | Measure-Object -Property profit -Sum).Sum
$avgRate = if($totalRev -gt 0){ [Math]::Round($totalProf*100.0/$totalRev,1) }else{0}

Write-Host "  Top 5 by profit:"
foreach($r in ($ranking | Select-Object -First 5)){
  Write-Host "    + $($r.sku) profit=¥$($r.profit) (sold $($r.sold) × ¥$($r.unit_profit) unit)"
}
Write-Host "  Bottom 3:"
foreach($r in ($ranking | Where-Object { $_.sold -gt 0 } | Select-Object -Last 3)){
  Write-Host "    - $($r.sku) profit=¥$($r.profit)"
}
Write-Host ""

# 平台利润拆解
Write-Host "[2/3] Per-platform profit breakdown..."
# 平台扣点系数（行业经验值）
$platformCommission = @{
  '淘宝' = 0.05    # 平台扣点 5%
  '抖音' = 0.06    # 抖音 5-6%
  '小红书' = 0.05
  '视频号' = 0.03
}
$platformLogistics = 12  # 物流均摊 ¥12/单
$platformAdRatio = @{    # 投放占 GMV 比例
  '淘宝' = 0.10
  '抖音' = 0.15
  '小红书' = 0.05
  '视频号' = 0.03
}

$platformAgg = $sales | Group-Object -Property {$_.'平台'[0]}
$platformResult = @()
foreach($g in $platformAgg){
  $platform = $g.Name
  $gmv = ($g.Group | Measure-Object -Property 'GMV' -Sum).Sum
  $orders = ($g.Group | Measure-Object -Property '订单数' -Sum).Sum
  $commission = $gmv * $platformCommission[$platform]
  $logistics = $orders * $platformLogistics
  $ad = $gmv * $platformAdRatio[$platform]
  $cost_of_goods = $gmv * $CostRatio
  $netProfit = $gmv - $commission - $logistics - $ad - $cost_of_goods
  $netRate = if($gmv -gt 0){ [Math]::Round($netProfit*100.0/$gmv,1) }else{0}
  $platformResult += [PSCustomObject]@{
    platform = $platform
    gmv = [Math]::Round($gmv,0)
    orders = $orders
    commission = [Math]::Round($commission,0)
    logistics = [Math]::Round($logistics,0)
    ad = [Math]::Round($ad,0)
    cogs = [Math]::Round($cost_of_goods,0)
    net = [Math]::Round($netProfit,0)
    rate = $netRate
  }
}
$platformResult = $platformResult | Sort-Object -Property net -Descending

Write-Host "  Platform net profit:"
foreach($p in $platformResult){
  Write-Host "    $($p.platform): GMV ¥$($p.gmv) - 扣点 ¥$($p.commission) - 物流 ¥$($p.logistics) - 投放 ¥$($p.ad) - 成本 ¥$($p.cogs) = 净利 ¥$($p.net) ($($p.rate)%)"
}
Write-Host ""

# 总览
Write-Host "[3/3] Summary"
Write-Host "  Total revenue: ¥$totalRev"
Write-Host "  Total profit:  ¥$totalProf  ($avgRate% margin)"
$totalGmvNet = ($platformResult | Measure-Object -Property net -Sum).Sum
$totalGmv = ($platformResult | Measure-Object -Property gmv -Sum).Sum
Write-Host "  Cross-platform 7d GMV ¥$totalGmv → Net ¥$totalGmvNet"
Write-Host ""

$output = [PSCustomObject]@{
  per_product = $ranking
  per_platform = $platformResult
  summary = @{
    total_revenue = $totalRev
    total_profit = $totalProf
    avg_margin_pct = $avgRate
    cross_platform_7d_gmv = $totalGmv
    cross_platform_7d_net = $totalGmvNet
  }
  cost_assumptions = @{
    cost_ratio = $CostRatio
    platform_commission = $platformCommission
    platform_ad_ratio = $platformAdRatio
    logistics_per_order = $platformLogistics
  }
  generated_at = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
}
$utf8bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\profit-analysis.json", ($output|ConvertTo-Json -Depth 6), $utf8bom)
Write-Host "Saved to %TEMP%\profit-analysis.json"
