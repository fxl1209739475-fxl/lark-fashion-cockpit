param([string]$WhiteboardToken='CXxkwXOzJhMTUKb6ZVicFZ2cnlk')
$ErrorActionPreference='Stop'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$T_PAIR='tblHZAHcOzkcD4gC'
$T_LIVE='tblAuzO7UsdjlXyL'
$T_RET='tblCwJGr0HTMFtXD'

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

function Sanitize($text){
  if(-not $text){ return '_' }
  return ($text -replace '[\[\](){}|]','').Trim()
}

Write-Host "==================================================="
Write-Host "  Product Relationship Graph → Lark Whiteboard"
Write-Host "==================================================="

$products = Load-Table $T_PROD
$pairs = Load-Table $T_PAIR
$lives = Load-Table $T_LIVE
$returns = Load-Table $T_RET

Write-Host "  Products: $($products.Count) / Pairs: $($pairs.Count) / Live: $($lives.Count) / Returns: $($returns.Count)"
Write-Host ""

# 构建 rid → sku 索引
$rid2sku = @{}
foreach($p in $products){ $rid2sku[$p._rid] = $p.'款号' }

# 生成 Mermaid graph
$lines = @()
$lines += "flowchart LR"
$lines += "  classDef product fill:#FFE4C4,stroke:#8B4513,stroke-width:2px"
$lines += "  classDef pair fill:#FFE4E1,stroke:#DC143C,stroke-width:1.5px"
$lines += "  classDef live fill:#E6F3FF,stroke:#1F4E79,stroke-width:1.5px"
$lines += "  classDef plat fill:#F0F0F0,stroke:#666"
$lines += "  classDef ret fill:#FFE4E1,stroke:#FF0000"
$lines += ""

# 1. 产品节点
$lines += "  %% 产品节点（按品类分组）"
foreach($p in $products){
  $sku = $p.'款号'
  $name = Sanitize($p.'产品名称')
  $price = $p.'售价'
  $sold = $p.'已实销'
  $stock = $p.'库存'
  $status = @($p.'状态')[0]
  $emoji = switch($status){
    '在售' {'🟢'}
    '历史款' {'⚪'}
    '售罄' {'🔴'}
    '开发中' {'🟡'}
    default {''}
  }
  $node = "$emoji $sku<br/>¥$price 实销$sold 库存$stock"
  $lines += "  $sku[`"$node`"]"
  $lines += "  class $sku product"
}
$lines += ""

# 2. 搭配关系
$lines += "  %% 搭配组关系（人工锁定 + 历史成交）"
foreach($pair in $pairs){
  $main = $rid2sku[(@($pair.'主推款') | Select-Object -First 1).id]
  $accessories = @($pair.'搭配款')
  $src = @($pair.'来源')[0]
  $usage = $pair.'使用次数'
  foreach($a in $accessories){
    $accSku = $rid2sku[$a.id]
    if($main -and $accSku){
      $linkLabel = "$src×$usage"
      $lines += "  $main -.->|`"$linkLabel`"| $accSku"
    }
  }
}
$lines += ""

# 3. 直播主推（已成功的场次）
$lines += "  %% 直播主推关系"
foreach($l in $lives){
  $mainArr = @($l.'主推款')
  if($mainArr.Count -eq 0){ continue }
  $sku = $rid2sku[$mainArr[0].id]
  $sched = Sanitize($l.'排期')
  $actual = $l.'实际GMV'
  if(-not $sku){ continue }
  $liveId = ('LIVE_' + ($sched -replace '[^a-zA-Z0-9]','').Substring(0,[Math]::Min(8,($sched -replace '[^a-zA-Z0-9]','').Length)))
  if($actual -gt 0){
    $lines += "  $liveId(`"📺 $sched<br/>GMV ¥$actual`")"
    $lines += "  class $liveId live"
    $lines += "  $sku --> $liveId"
  } else {
    $lines += "  $liveId(`"📅 $sched<br/>预排`")"
    $lines += "  class $liveId live"
    $lines += "  $sku --> $liveId"
  }
}
$lines += ""

# 4. 退货预警节点（高频退货款 → ⚠️ 标注）
$lines += "  %% 退货风险关联"
$retCounts = @{}
foreach($r in $returns){
  $sku = $r.SKU
  if(-not $sku){ continue }
  $stripped = ($sku -split ' ')[0]
  if(-not $retCounts.ContainsKey($stripped)){ $retCounts[$stripped] = 0 }
  $retCounts[$stripped]++
}
foreach($skuRet in $retCounts.Keys){
  if($retCounts[$skuRet] -ge 2){
    $lines += "  RET_$skuRet(`"⚠️ 退货 $($retCounts[$skuRet]) 次`")"
    $lines += "  class RET_$skuRet ret"
    $lines += "  $skuRet -.->|风险| RET_$skuRet"
  }
}

$mermaid = $lines -join "`n"
$mermaidPath = "C:\Users\冯兴龙\AppData\Local\Temp\product-graph.mmd"
$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($mermaidPath, $mermaid, $utf8)
Write-Host "Mermaid DSL ($($lines.Count) lines) saved to %TEMP%\product-graph.mmd"
Write-Host ""
Write-Host "=== Preview ==="
Write-Host ($mermaid.Substring(0, [Math]::Min(800, $mermaid.Length)))
Write-Host "..."
Write-Host ""

# 注入到飞书白板
Write-Host "Injecting into 飞书白板 (token: $WhiteboardToken)..."
$idemToken = "lfc-graph-$(Get-Date -Format 'yyMMddHHmmss')"
cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli docs +whiteboard-update --whiteboard-token $WhiteboardToken --input_format mermaid --source @./product-graph.mmd --overwrite --idempotent-token $idemToken --yes --jq .data"
Write-Host ""
Write-Host "Whiteboard URL: https://my.feishu.cn/docx/Pcvwd9e3qopP4ZxOSk2cTbo8nMf"
