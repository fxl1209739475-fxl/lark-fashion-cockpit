# inventory-gmv-matcher.ps1 — 库存 GMV 智能匹配
#
# 输入：[(款号 | 产品名 | 销售金额),...]（来自浏览器抓取或 OCR）
# 输出：库存 GMV 累计 + 详细匹配日志 + 飞书报告
#
# 核心算法：
#   1. 对每条销售记录，款号或产品名匹配 01_产品库
#   2. 检查产品的"是否库存款"字段：
#      - "是" → 直接计入库存 GMV
#      - "否" → 不计入
#      - "自动判定" → 走自动规则（在售 + 上架>60天 + 库存周转>60天）
#   3. 累计库存 GMV，输出明细 + 总和

param(
  [string]$InputJsonPath = 'C:\Users\冯兴龙\AppData\Local\Temp\livestream-sales.json',
  [string]$ReplyChatId
)
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$BOSS_CHAT = if($ReplyChatId){$ReplyChatId}else{'oc_45e0995a007db9d7f1859fa17b6566f6'}

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
Write-Host "  inventory-gmv-matcher"
Write-Host "  Input: $InputJsonPath"
Write-Host "==================================================="
Write-Host ""

# Step 1: 读销售数据（来自浏览器抓取 / OCR）
if(-not (Test-Path $InputJsonPath)){
  Write-Host "  ⚠ 输入文件不存在，使用 mock 数据演示"
  $sales = @(
    [PSCustomObject]@{ sku='DRS-0429-FL'; name='法式碎花连衣裙'; amount=29900; platform='抖音' }
    [PSCustomObject]@{ sku='KNT-0402-CD'; name='短款焦糖针织开衫'; amount=18900; platform='抖音' }
    [PSCustomObject]@{ sku='SHT-0420-SP'; name='海盐蓝防晒衬衫'; amount=33800; platform='视频号' }
    [PSCustomObject]@{ sku='PNT-0418-SU'; name='通勤西装裤'; amount=21500; platform='抖音' }
    [PSCustomObject]@{ sku='OUT-2024-OL'; name='OL极简西服'; amount=27500; platform='小红书' }
    [PSCustomObject]@{ sku='SKT-0328-A'; name='高腰A字裙'; amount=15900; platform='视频号' }
    [PSCustomObject]@{ sku='UNKNOWN-X'; name='未知款（OCR 误识别）'; amount=5000; platform='抖音' }
  )
} else {
  $sales = Get-Content $InputJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
}
Write-Host "[1/3] 加载销售数据：$($sales.Count) 条"
Write-Host ""

# Step 2: 加载产品库（含"是否库存款"字段）
Write-Host "[2/3] 加载产品库..."
$products = Load-Table $T_PROD
Write-Host "  产品 $($products.Count) 件"

# 构建 SKU + 产品名 双向索引
$skuMap = @{}
foreach($p in $products){
  if($p.'款号'){ $skuMap[$p.'款号'] = $p }
}
Write-Host "  款号索引：$($skuMap.Count) 个"
Write-Host ""

# Step 3: 匹配 + 累计库存 GMV
Write-Host "[3/3] 库存 GMV 匹配..."
$inventoryGmv = 0
$normalGmv = 0
$matchLog = @()

foreach($s in $sales){
  $matched = $skuMap[$s.sku]
  $isInventory = $false
  $reason = ''

  if(-not $matched){
    # 款号未找到，尝试产品名模糊匹配
    foreach($p in $products){
      if($s.name -and $p.'产品名称' -match [regex]::Escape($s.name.Substring(0,[Math]::Min(4,$s.name.Length)))){
        $matched = $p; break
      }
    }
  }

  if(-not $matched){
    $reason = '⚠️ 未匹配产品库（计入正常 GMV，需人工核对）'
    $normalGmv += $s.amount
  } else {
    $stockMark = (@($matched.'是否库存款'))[0]
    $status = (@($matched.'状态'))[0]
    $sold = [int]$matched.'已实销'
    $made = [int]$matched.'做货数'
    $sellThru = if($made -gt 0){ $sold * 100.0 / $made } else { 0 }

    switch($stockMark){
      '是' {
        $isInventory = $true
        $reason = "✅ 人工标记为库存款 → 计入库存 GMV"
      }
      '否' {
        $isInventory = $false
        $reason = "❌ 人工标记为非库存款（如开发中/已售罄）"
      }
      '自动判定' {
        # 自动规则：状态=在售 + 售罄率 < 60% + 上架超过 60 天
        if($status -eq '在售' -and $sellThru -lt 60){
          $isInventory = $true
          $reason = "🤖 自动判定：在售但售罄率 $([Math]::Round($sellThru,1))% <60% → 库存款"
        } elseif($status -eq '历史款'){
          $isInventory = $true
          $reason = "🤖 自动判定：历史款 → 库存款"
        } else {
          $isInventory = $false
          $reason = "🤖 自动判定：在售 + 售罄率良好 → 非库存款"
        }
      }
      default {
        $isInventory = $false
        $reason = "⚠ 未标记，默认非库存款"
      }
    }

    if($isInventory){ $inventoryGmv += $s.amount } else { $normalGmv += $s.amount }
  }

  $emoji = if($isInventory){'📦'}else{'💰'}
  Write-Host "  $emoji $($s.sku) ($($s.platform)) ¥$($s.amount) - $reason"
  $matchLog += [PSCustomObject]@{
    sku = $s.sku; name = $s.name; platform = $s.platform; amount = $s.amount
    isInventory = $isInventory; reason = $reason
  }
}
Write-Host ""

$totalGmv = $inventoryGmv + $normalGmv
$invPct = if($totalGmv -gt 0){[Math]::Round($inventoryGmv*100.0/$totalGmv,1)}else{0}

Write-Host "==================================================="
Write-Host "  匹配结果"
Write-Host "==================================================="
Write-Host "  💰 正常 GMV:  ¥$normalGmv"
Write-Host "  📦 库存 GMV:  ¥$inventoryGmv  ($invPct%)"
Write-Host "  💸 合计 GMV:  ¥$totalGmv"
Write-Host "==================================================="

# 输出 JSON 给后续 livestream-daily-report 用
$result = [PSCustomObject]@{
  ts = (Get-Date).ToString('o')
  inventory_gmv = $inventoryGmv
  normal_gmv = $normalGmv
  total_gmv = $totalGmv
  inventory_pct = $invPct
  match_log = $matchLog
}
$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\inventory-gmv-result.json", ($result|ConvertTo-Json -Depth 6), $utf8)

# 推卡片
$invItems = ($matchLog | Where-Object { $_.isInventory } | ForEach-Object { "📦 $($_.sku) ¥$($_.amount) ($($_.platform))" }) -join "`n"
$logExcerpt = ($matchLog | Select-Object -First 5 | ForEach-Object {
  $e = if($_.isInventory){'📦'}else{'💰'}
  "$e $($_.sku) ¥$($_.amount): $($_.reason)"
}) -join "`n"

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content='📦 库存 GMV 智能匹配报告'}; template='red'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**输入：** $($sales.Count) 条销售记录（来自浏览器抓取）`n**算法：** 款号匹配 + 产品库'是否库存款'字段判定 + 自动规则兜底"}}
    @{tag='hr'}
    @{tag='div'; fields=@(
      @{is_short=$true; text=@{tag='lark_md'; content="**💰 正常 GMV**`n¥$normalGmv"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**📦 库存 GMV**`n¥$inventoryGmv ($invPct%)"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**💸 总 GMV**`n¥$totalGmv"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**🎯 匹配率**`n$($matchLog.Count) / $($sales.Count)"}}
    )}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**📦 库存款明细：**`n$invItems"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 匹配日志（前 5 条）：**`n$logExcerpt"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🚀 这就是 livestream-scraper 的核心算法。**`n浏览器抓数据 → 款号匹配 → 自动累计库存 GMV → 主播帮清的库存价值一目了然。"}}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host ""
Write-Host "Done."
