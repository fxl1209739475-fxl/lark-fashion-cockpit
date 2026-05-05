param([switch]$Clean)
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T='tbl150NzR6ByiCjG'
$now = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()

# 清掉之前的 test 记录
if($Clean){
  $rids = (cmd /c "lark-cli base +record-list --base-token $BASE --table-id $T --jq "".data.record_id_list""") | ConvertFrom-Json
  foreach($rid in $rids){
    Write-Host "删 $rid"
    cmd /c "lark-cli base +record-delete --base-token $BASE --table-id $T --record-id $rid --yes" | Out-Null
  }
}

function Add-Todo($p){
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $json = $p | ConvertTo-Json -Compress -Depth 5
  [System.IO.File]::WriteAllText('C:\Users\冯兴龙\AppData\Local\Temp\todo.json', $json, $utf8)
  # hardcoded base + table_id（避免 PowerShell scope 问题）
  $out = cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token LWsdbVtIaa2MaDsANm3cNdYgn1j --table-id tbl150NzR6ByiCjG --json @./todo.json --jq .data.record.record_id"
  return $out
}

$todos = @(
  @{
    '待办标题' = '直播数据自动抓取 Playwright DOM selector 真接通'
    '类别' = @('数据接入')
    '优先级' = @('P1')
    '阻塞原因' = '商家后台 DOM 选择器调试需要扫码登录 + F12 圈选元素，老板娘不熟悉开发者工具圈选'
    '解决路径' = '路径 A：找懂前端的朋友帮调一次 selector（30 分钟/平台）；路径 B：商业化阶段直接接抖音电商开放 API（更稳，1-3 天审批）；路径 C：让朋友或运营专门挑 1 个平台先调通'
    '预估工时' = '每平台 30-60 分钟，3 平台合计 1.5-3 小时'
    '已搭好的基础' = '24_直播记录表 12 字段 / inventory-gmv-matcher 库存匹配算法 / livestream-fetch-by-record 主脚本 / Playwright 环境 chromium 145 / Mock 端到端跑通（实销 14.7 万 + 库存 9.78 万 + 64.1 占比）。仅缺 3 平台真实 DOM selector'
    '备注' = '老板娘只需 30 秒粘 URL，selector 调通后真生产可用'
    '创建日期' = $now
    '状态' = @('已搁置')
  },
  @{
    '待办标题' = '虚拟模特换装 真 VTON 接通（产品图穿身上）'
    '类别' = @('AI 模型')
    '优先级' = @('P1')
    '阻塞原因' = '当前 PIL 占位版只是色块叠加，不是真模特换装效果。真接通需要 VTON API：阿里 OutfitAnyone（要申请） 或 可灵 Kolors-VTON（要充值） 或 开源 OOTDiffusion（要 GPU）'
    '解决路径' = '路径 A 推荐：阿里通义万相 AI 试衣（电商业最强）；路径 B：可灵 Kolors-VTON（已有 access key 充 10 元即可）；路径 C：开源 OOTDiffusion 自部署；路径 D 最完整：路径 A + 尺寸合身度可视化图层（解决 VTON 不算尺寸的问题）'
    '预估工时' = 'VTON 接通：30 分钟；路径 D 完整版：3 小时'
    '已搭好的基础' = '8 款产品占位图（PIL 生成） / assets/products 完整产品图库 / 17_产品搭配组数据 / 模特占位图框架。缺真 VTON API 接通'
    '备注' = '商业化版本核心卖点。比赛阶段 mock 演示版可用，赛后接通真生产'
    '创建日期' = $now
    '状态' = @('已搁置')
  }
)

foreach($t in $todos){
  $r = Add-Todo $t
  Write-Host "✓ $($t.待办标题) → $r"
}
