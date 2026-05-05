# livestream-daily-report.ps1 — 直播日报自动生成
#
# 输入：日期（默认今天）
# 输出：飞书 IM 卡片（早场+晚场对比 + 主推款排行 + 库存 GMV + AI 总结）

param([string]$Date='2026-08-11', [string]$ReplyChatId)
$ErrorActionPreference='Continue'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T21='tblKHslcP48tXi09'
$T22='tblbzKMGjdJUja5O'
$T23='tbljntqmTIyKraiE'
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
Write-Host "  livestream-daily-report · $Date"
Write-Host "==================================================="

$sessions = Load-Table $T21
$products = Load-Table $T22
$ads = Load-Table $T23

# 按场次 + 平台聚合
$dawnSessions = $sessions | Where-Object { (@($_.场次))[0] -eq '早场' }
$nightSessions = $sessions | Where-Object { (@($_.场次))[0] -eq '晚场' }

function Phase-Total($rows){
  $sale = ($rows | Measure-Object -Property '实销金额' -Sum).Sum
  $refund = ($rows | Measure-Object -Property '退款金额' -Sum).Sum
  $uv = ($rows | Measure-Object -Property 'UV' -Sum).Sum
  $fans = ($rows | Measure-Object -Property '涨粉' -Sum).Sum
  $invGmv = ($rows | Measure-Object -Property '库存GMV' -Sum).Sum
  return @{sale=$sale; refund=$refund; uv=$uv; fans=$fans; invGmv=$invGmv;
    refundPct=if($sale -gt 0){[Math]::Round($refund*100.0/($sale+$refund),1)}else{0};
    invPct=if($sale -gt 0){[Math]::Round($invGmv*100.0/$sale,1)}else{0}}
}

$dawnT = Phase-Total $dawnSessions
$nightT = Phase-Total $nightSessions

# 各场 4 平台
function Phase-Platforms($rows){
  $byPlat = @()
  foreach($p in @('抖音','小红书','视频号','淘宝')){
    $r = $rows | Where-Object { (@($_.平台))[0] -eq $p }
    if($r){
      $byPlat += [PSCustomObject]@{
        plat = $p
        uv = ($r | Measure-Object -Property 'UV' -Sum).Sum
        sale = ($r | Measure-Object -Property '实销金额' -Sum).Sum
        invGmv = ($r | Measure-Object -Property '库存GMV' -Sum).Sum
        fans = ($r | Measure-Object -Property '涨粉' -Sum).Sum
      }
    }
  }
  return $byPlat
}
$dawnPlats = Phase-Platforms $dawnSessions
$nightPlats = Phase-Platforms $nightSessions

# 主推款排行
$dawnProds = $products | Where-Object { (@($_.场次))[0] -eq '早场' } | Group-Object -Property '产品名' | ForEach-Object {
  [PSCustomObject]@{name=$_.Name; sold=($_.Group | Measure-Object -Property '出单数' -Sum).Sum}
} | Sort-Object -Property sold -Descending

$nightProds = $products | Where-Object { (@($_.场次))[0] -eq '晚场' } | Group-Object -Property '产品名' | ForEach-Object {
  [PSCustomObject]@{name=$_.Name; sold=($_.Group | Measure-Object -Property '出单数' -Sum).Sum}
} | Sort-Object -Property sold -Descending

# 投流
$totalAd = ($ads | Measure-Object -Property '花费' -Sum).Sum
$adByPhase = $ads | Group-Object -Property { (@($_.场次))[0] } | ForEach-Object {
  [PSCustomObject]@{phase=$_.Name; ad=($_.Group | Measure-Object -Property '花费' -Sum).Sum}
}

Write-Host ""
Write-Host "[早场] $($dawnT.sale) 元 / 退款 $($dawnT.refundPct)% / 库存 GMV $($dawnT.invGmv) ($($dawnT.invPct)%)"
Write-Host "[晚场] $($nightT.sale) 元 / 退款 $($nightT.refundPct)% / 库存 GMV $($nightT.invGmv) ($($nightT.invPct)%)"
$total = $dawnT.sale + $nightT.sale
$totalInv = $dawnT.invGmv + $nightT.invGmv
$totalInvPct = if($total -gt 0){[Math]::Round($totalInv*100.0/$total,1)}else{0}
Write-Host "[全天] $total 元 / 投流 $totalAd 元 / 总库存 GMV $totalInv ($totalInvPct% 占比)"
Write-Host ""

# AI 综合分析
$aiSummary = @()
$aiSummary += "**🟢 整体表现：** 全天 GMV ¥$total / 投流 ¥$totalAd（占比 $([Math]::Round($totalAd*100.0/$total,2))%）"
if($nightT.sale -gt $dawnT.sale){
  $aiSummary += "**📈 晚场表现强：** 晚场 GMV ¥$($nightT.sale) > 早场 ¥$($dawnT.sale)，建议加大晚场投流权重"
}
if($totalInvPct -gt 5){
  $aiSummary += "**💰 库存消化效果好：** 库存 GMV 占比 $totalInvPct%（高于 5% 阈值），主播搭配主推库存款方法有效"
} else {
  $aiSummary += "**🟡 库存消化弱：** 库存 GMV 占比仅 $totalInvPct%，建议下次直播专门排库存搭配款"
}
if($dawnT.refundPct -gt 15 -or $nightT.refundPct -gt 15){
  $aiSummary += "**⚠️ 退款率高：** 早场 $($dawnT.refundPct)% / 晚场 $($nightT.refundPct)%，建议复盘哪款退货突出 + 详情页加尺码引导"
}
$topProd = if($nightProds.Count -gt 0){$nightProds[0]}else{$dawnProds[0]}
$aiSummary += "**🏆 当日爆款：** $($topProd.name) 出单 $($topProd.sold) 件 → 备货检查 + 明日加大主推"

# 推卡片
$dawnPlatLines = $dawnPlats | ForEach-Object { "  $($_.plat): UV $($_.uv) / GMV ¥$($_.sale) / 库存 ¥$($_.invGmv) / 粉 +$($_.fans)" }
$nightPlatLines = $nightPlats | ForEach-Object { "  $($_.plat): UV $($_.uv) / GMV ¥$($_.sale) / 库存 ¥$($_.invGmv) / 粉 +$($_.fans)" }
$dawnProdLines = ($dawnProds | Select-Object -First 3 | ForEach-Object { "  $($_.name): $($_.sold) 件" })
$nightProdLines = ($nightProds | Select-Object -First 3 | ForEach-Object { "  $($_.name): $($_.sold) 件" })

$content1 = ("**🌅 早场（东东）**`n实销 ¥$($dawnT.sale) / 退款率 $($dawnT.refundPct)% / 库存 GMV ¥$($dawnT.invGmv)（$($dawnT.invPct)%）`n" + ($dawnPlatLines -join "`n"))
$content2 = ("**🌙 晚场（梦瑶）**`n实销 ¥$($nightT.sale) / 退款率 $($nightT.refundPct)% / 库存 GMV ¥$($nightT.invGmv)（$($nightT.invPct)%）`n" + ($nightPlatLines -join "`n"))
$prodContent = ("**🏆 早场主推 Top 3：**`n" + ($dawnProdLines -join "`n") + "`n`n**🏆 晚场主推 Top 3：**`n" + ($nightProdLines -join "`n"))
$aiContent = $aiSummary -join "`n`n"

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content="📺 直播日报 · $Date"}; template='violet'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**全天总览：**`n💰 GMV ¥$total / 库存 GMV ¥$totalInv（$totalInvPct% 占比）/ 投流 ¥$totalAd"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content=$content1}}
    @{tag='div'; text=@{tag='lark_md'; content=$content2}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content=$prodContent}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 AI 综合分析：**`n$aiContent"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📊 查 21_场次数据'}; type='primary'; url="https://my.feishu.cn/base/$BASE?table=$T21"}
      @{tag='button'; text=@{tag='plain_text'; content='🏆 查 22_主推款'}; url="https://my.feishu.cn/base/$BASE?table=$T22"}
      @{tag='button'; text=@{tag='plain_text'; content='💸 查 23_投流'}; url="https://my.feishu.cn/base/$BASE?table=$T23"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host "Done."
