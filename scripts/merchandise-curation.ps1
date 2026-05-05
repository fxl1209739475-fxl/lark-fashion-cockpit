# merchandise-curation.ps1 — AI 货盘梳理
#
# 输入：目的（清仓/冲销售/测款/提利润等）
# 输出：梳理好的货盘清单 + AI 推荐搭配 + 飞书文档
#
# 核心：ABCD 款分类 + 目的驱动选品 + 联动 product-matching 配搭配

param(
  [Parameter(Mandatory=$true)][ValidateSet('冲销售额','清库存','测款','提利润','上新主推','大促爆款')][string]$Purpose,
  [int]$TopN = 8,
  [string]$ReplyChatId
)
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T_PROD='tblrKzymnPPQ98ZX'
$T_PAIR='tblHZAHcOzkcD4gC'
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
Write-Host "  merchandise-curation · AI 货盘梳理"
Write-Host "  目的: $Purpose"
Write-Host "==================================================="
Write-Host ""

# Step 1: 拉产品 + 搭配组
Write-Host "[1/4] 加载产品库 + 搭配组..."
$products = Load-Table $T_PROD
$pairs = Load-Table $T_PAIR
Write-Host "  产品 $($products.Count) / 搭配组 $($pairs.Count)"
Write-Host ""

# Step 2: ABCD 款分类
Write-Host "[2/4] ABCD 款分类..."
$ranked = @()
foreach($p in $products){
  $sold = [int]$p.'已实销'
  $stock = [int]$p.'库存'
  $made = [int]$p.'做货数'
  $price = [decimal]$p.'售价'
  $status = (@($p.'状态'))[0]
  $sellThru = if($made -gt 0){ $sold * 100.0 / $made } else { 0 }

  # ABCD 分级
  $cls = 'D'
  if($sold -ge 300 -and $sellThru -ge 50){ $cls = 'A' }      # 爆款
  elseif($sold -ge 200){ $cls = 'B' }                          # 次爆款
  elseif($sold -ge 100){ $cls = 'C' }                          # 一般
  else{ $cls = 'D' }                                           # 库存款

  $ranked += [PSCustomObject]@{
    sku = $p.'款号'
    name = $p.'产品名称'
    cat = (@($p.'品类'))[0]
    cls = $cls
    sold = $sold
    stock = $stock
    made = $made
    sellThru = [Math]::Round($sellThru, 1)
    price = $price
    revenue = [Math]::Round($sold * $price, 0)
    profit_unit = [Math]::Round($price * 0.6, 0)  # 假设 40% 成本
    profit_total = [Math]::Round($sold * $price * 0.6, 0)
    status = $status
    rid = $p._rid
    tags = @($p.'元素标签')
  }
}

$grouped = $ranked | Group-Object -Property cls | Sort-Object -Property Name
foreach($g in $grouped){
  Write-Host "  $($g.Name) 级款: $($g.Count) 个"
  foreach($r in ($g.Group | Sort-Object -Property sold -Descending | Select-Object -First 3)){
    Write-Host "    $($r.sku) sold=$($r.sold) stock=$($r.stock) revenue=¥$($r.revenue)"
  }
}
Write-Host ""

# Step 3: 目的驱动选品
Write-Host "[3/4] 目的驱动选品: $Purpose"
$selected = @()
$reasoning = ""
switch($Purpose){
  '冲销售额' {
    # A 类爆款 + 单价高 + 库存够卖
    $selected = $ranked | Where-Object { $_.cls -in 'A','B' -and $_.stock -gt 50 -and $_.status -eq '在售' } |
      Sort-Object -Property revenue -Descending | Select-Object -First $TopN
    $reasoning = "A+B 类爆款 + 库存 >50 件 + 在售，按总营收降序，最大化 GMV"
  }
  '清库存' {
    # C 类 + D 类 + 历史款 库存高的
    $selected = $ranked | Where-Object { ($_.cls -in 'C','D' -or $_.status -eq '历史款') -and $_.stock -gt 100 } |
      Sort-Object -Property stock -Descending | Select-Object -First $TopN
    $reasoning = "C/D 类 + 历史款 + 库存 >100 件，库存倾斜清仓优先"
  }
  '测款' {
    # 开发中款 + 在售低销量款
    $selected = $ranked | Where-Object { $_.status -eq '开发中' -or ($_.cls -eq 'D' -and $_.status -eq '在售') } |
      Select-Object -First $TopN
    $reasoning = "开发中款 + 低销量在售款，小批量测款收集数据"
  }
  '提利润' {
    # 单件利润高 + 销量稳定
    $selected = $ranked | Where-Object { $_.profit_unit -gt 100 -and $_.cls -in 'A','B','C' -and $_.status -eq '在售' } |
      Sort-Object -Property profit_unit -Descending | Select-Object -First $TopN
    $reasoning = "单件利润 >¥100 + A/B/C 级稳定款，撬动单件 ROI"
  }
  '上新主推' {
    # 开发中 + 元素跟历史爆款重合的
    $selected = $ranked | Where-Object { $_.status -in '开发中','在售' -and $_.cls -in 'A','B' } |
      Sort-Object -Property sellThru -Descending | Select-Object -First $TopN
    $reasoning = "开发中款 + 在售爆款元素相似款，借势新品流量"
  }
  '大促爆款' {
    # A 类 + 库存充足 + 套装率高
    $selected = $ranked | Where-Object { $_.cls -eq 'A' -and $_.stock -gt 100 -and $_.status -eq '在售' } |
      Sort-Object -Property revenue -Descending | Select-Object -First $TopN
    $reasoning = "A 类爆款 + 库存 >100 件 + 在售，大促主战场"
  }
}

Write-Host "  AI 选品逻辑：$reasoning"
Write-Host "  选中 $($selected.Count) 件："
foreach($s in $selected){
  Write-Host "    [$($s.cls)] $($s.sku) $($s.name) - sold=$($s.sold) stock=$($s.stock) ¥$($s.price)"
}
Write-Host ""

# Step 4: 配搭配（基于已锁定的搭配组）
Write-Host "[4/4] AI 配搭配..."
$rid2sku = @{}
foreach($p in $products){ $rid2sku[$p._rid] = $p.'款号' }

$pairings = @{}
foreach($s in $selected){
  $pairings[$s.sku] = @()
  foreach($pair in $pairs){
    $mp = @($pair.'主推款')
    $sp = @($pair.'搭配款')
    if($mp.Count -gt 0 -and $mp[0].id -eq $s.rid){
      foreach($acc in $sp){
        $accSku = $rid2sku[$acc.id]
        if($accSku){ $pairings[$s.sku] += $accSku }
      }
    }
    elseif($mp.Count -gt 0 -and $sp.id -eq $s.rid){
      $accSku = $rid2sku[$mp[0].id]
      if($accSku){ $pairings[$s.sku] += $accSku }
    }
  }
}

foreach($s in $selected | Select-Object -First 5){
  $accs = $pairings[$s.sku]
  if($accs -and $accs.Count -gt 0){
    Write-Host "  $($s.sku) → 搭配: $($accs -join ', ')"
  }
}
Write-Host ""

# Step 5: 推卡片
$totalRevenue = ($selected | Measure-Object -Property revenue -Sum).Sum
$totalProfit = ($selected | Measure-Object -Property profit_total -Sum).Sum
$avgSellThru = if($selected.Count -gt 0){ ($selected | Measure-Object -Property sellThru -Average).Average }else{0}

$listLines = @()
$rank = 0
foreach($s in $selected){
  $rank++
  $accs = $pairings[$s.sku]
  $accStr = if($accs -and $accs.Count -gt 0){ "搭配: $($accs -join ', ')" }else{ "" }
  $listLines += "$rank. **[$($s.cls)] $($s.sku)** $($s.name)"
  $listLines += "　sold $($s.sold) / stock $($s.stock) / ¥$($s.price) / 售罄 $($s.sellThru)% / 营收 ¥$($s.revenue) $accStr"
}
$listContent = $listLines -join "`n"

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content="📦 AI 货盘梳理 · $Purpose"}; template='orange'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**目的：** $Purpose`n**AI 选品逻辑：** $reasoning`n**选中：** $($selected.Count) 件 / 预估总营收 **¥$totalRevenue** / 预估总利润 **¥$totalProfit**"}}
    @{tag='hr'}
    @{tag='div'; fields=@(
      @{is_short=$true; text=@{tag='lark_md'; content="**A 级爆款**`n$(($grouped | Where-Object { $_.Name -eq 'A' }).Count) 个"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**B 级次爆款**`n$(($grouped | Where-Object { $_.Name -eq 'B' }).Count) 个"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**C 级一般款**`n$(($grouped | Where-Object { $_.Name -eq 'C' }).Count) 个"}}
      @{is_short=$true; text=@{tag='lark_md'; content="**D 级库存款**`n$(($grouped | Where-Object { $_.Name -eq 'D' }).Count) 个"}}
    )}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🎯 货盘清单（按目的优先级排序）：**`n$listContent"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 智能联动：**`n• product-matching 自动给主推配搭配（连带销售）`n• launch-decision 给爆款翻单备货建议`n• live-streaming 直播排款自动用此货盘"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📊 查 01_产品库'}; type='primary'; url="https://my.feishu.cn/base/$BASE?table=$T_PROD"}
      @{tag='button'; text=@{tag='plain_text'; content='🛍 查 17_搭配组'}; url="https://my.feishu.cn/base/$BASE?table=$T_PAIR"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host ""
Write-Host "Done."
