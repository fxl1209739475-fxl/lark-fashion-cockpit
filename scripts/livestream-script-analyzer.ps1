# livestream-script-analyzer.ps1 — 直播话术分析
#
# 输入：录屏视频路径 / 妙记 token / 现成 transcript 文本
# 输出：5 维度评分 + 飞书分析报告
#
# 工作流：
#   1. 上传视频到飞书云盘（drive +upload）
#   2. 视频自动生成妙记（飞书原生）→ 拉 transcript
#   3. 或直接用现成 transcript
#   4. 提取话术（按时间分段）
#   5. 5 维度评分（开场吸引/产品讲解/限时促销/互动话术/收尾CTA）
#   6. AI 给具体改进建议
#   7. 输出飞书文档报告 + 卡片

param(
  [string]$TranscriptPath,
  [string]$VideoPath,
  [string]$MinuteToken,
  [string]$Anchor='主播',
  [string]$LiveTopic='5/4 早春爆款专场',
  [string]$ReplyChatId
)
$ErrorActionPreference='Continue'
$BOSS_CHAT = if($ReplyChatId){$ReplyChatId}else{'oc_45e0995a007db9d7f1859fa17b6566f6'}

Write-Host "==================================================="
Write-Host "  livestream-script-analyzer · 直播话术分析"
Write-Host "  Anchor: $Anchor / Topic: $LiveTopic"
Write-Host "==================================================="
Write-Host ""

# Step 1-3: 拿 transcript（多源支持）
$transcript = $null
if($TranscriptPath -and (Test-Path $TranscriptPath)){
  Write-Host "[1/4] 加载现成 transcript..."
  $transcript = Get-Content $TranscriptPath -Raw -Encoding UTF8
  Write-Host "  ✓ 字数: $($transcript.Length)"
} elseif($MinuteToken){
  Write-Host "[1/4] 拉妙记 transcript..."
  $tp = "C:\Users\冯兴龙\lark-fashion-cockpit\minutes\$MinuteToken\transcript.txt"
  if(Test-Path $tp){
    $transcript = Get-Content $tp -Raw -Encoding UTF8
    Write-Host "  ✓ 复用本地 transcript: $($transcript.Length) 字"
  } else {
    cmd /c "lark-cli vc +notes --minute-tokens $MinuteToken 2>nul" | Out-Null
    $transcript = Get-Content $tp -Raw -Encoding UTF8
    Write-Host "  ✓ 拉取 transcript: $($transcript.Length) 字"
  }
} elseif($VideoPath){
  Write-Host "[1/4] 视频上传到飞书 → 自动妙记 → 拉 transcript"
  Write-Host "  TODO: 接通飞书 drive +upload + 等妙记生成 + 拉 transcript"
  Write-Host "  当前演示：用 4/29 真实妙记 transcript 替代"
  $tp = "C:\Users\冯兴龙\lark-fashion-cockpit\minutes\obcnb31y6p4jd3u9t63h91gf\transcript.txt"
  $transcript = Get-Content $tp -Raw -Encoding UTF8
  $LiveTopic = "（演示模式 · 用 4/29 妙记替代真实直播录屏）"
}

if(-not $transcript){
  Write-Host "  ⚠ 没有 transcript 来源"
  exit 1
}
Write-Host ""

# Step 4: 5 维度评分（规则化 + 关键词加权）
Write-Host "[2/4] 5 维度话术分析..."

$dimensions = @{
  '开场吸引力' = @{
    keywords = @('欢迎','大家好','来啦','宝贝','姐妹','点关注','点小红心')
    weight = 1.0
    desc = '主播开场话术能否吸引观众停留'
  }
  '产品讲解力' = @{
    keywords = @('面料','版型','尺码','颜色','搭配','适合','好看','显瘦','显高')
    weight = 1.5
    desc = '产品卖点表达清晰度（面料/版型/穿搭场景）'
  }
  '限时促销' = @{
    keywords = @('限时','仅今天','库存只剩','秒杀','优惠','直播间专享','买一送一','立减')
    weight = 1.2
    desc = '紧迫感营造 + 促销话术使用频次'
  }
  '互动话术' = @{
    keywords = @('扣','打字','下方留言','弹幕','点赞','关注','加购','对吗','你们','大家')
    weight = 1.0
    desc = '与观众互动 + 引导转化'
  }
  '收尾CTA' = @{
    keywords = @('快下单','拍下来','购物车','点购物袋','立即下单','去抢','拍中','下单送礼')
    weight = 1.3
    desc = '行动召唤 + 临单促单'
  }
}

$scores = @{}
foreach($dim in $dimensions.Keys){
  $kws = $dimensions[$dim].keywords
  $weight = $dimensions[$dim].weight
  $hits = 0
  $samples = @()
  foreach($kw in $kws){
    $matches = ($transcript | Select-String -Pattern $kw -AllMatches).Matches
    $hits += $matches.Count
    if($matches.Count -gt 0 -and $samples.Count -lt 3){ $samples += $kw }
  }
  # 规则化打分（命中数 × 权重，最高 10 分）
  $rawScore = [Math]::Min(10, [int]($hits * $weight))
  $scores[$dim] = @{
    score = $rawScore
    hits = $hits
    samples = $samples
    desc = $dimensions[$dim].desc
  }
  Write-Host "  $dim : $rawScore/10  ($hits 次命中, 样本: $($samples -join ', '))"
}
Write-Host ""

$totalScore = ($scores.Values | ForEach-Object { $_.score } | Measure-Object -Sum).Sum
$avgScore = [Math]::Round($totalScore / 5.0, 1)
Write-Host "  📊 综合评分: $avgScore / 10"
Write-Host ""

# Step 5: AI 改进建议（规则化生成）
Write-Host "[3/4] AI 改进建议..."
$improvements = @()
foreach($dim in $dimensions.Keys){
  $s = $scores[$dim]
  if($s.score -lt 5){
    switch($dim){
      '开场吸引力' { $improvements += "🔴 **$dim ($($s.score)/10)** — 开场话术过弱。建议：固定开场模板'欢迎家人们 + 个人介绍 + 今天主推预告'，30 秒内点 3 次关注。" }
      '产品讲解力' { $improvements += "🔴 **$dim ($($s.score)/10)** — 产品卖点表达不足。建议：每件产品至少讲 3 个维度（面料 + 版型 + 适用场景），用'我穿的就是这件'增强代入感。" }
      '限时促销' { $improvements += "🔴 **$dim ($($s.score)/10)** — 紧迫感不够。建议：每 5 分钟报一次库存数（'还剩 X 件'）+ '限时' 关键词每 3 分钟一次。" }
      '互动话术' { $improvements += "🔴 **$dim ($($s.score)/10)** — 互动太少。建议：每 2 分钟问一次'家人们点赞过 1000 我们抽奖'+ 主动回应弹幕。" }
      '收尾CTA' { $improvements += "🔴 **$dim ($($s.score)/10)** — 收尾力不足。建议：每讲完一款必加'快上购物车'+'拍 X 件送礼'+'手慢无'三连话术。" }
    }
  } elseif($s.score -lt 8){
    $improvements += "🟡 **$dim ($($s.score)/10)** — 可优化。已有基础，建议加大频次。"
  } else {
    $improvements += "🟢 **$dim ($($s.score)/10)** — 表现优秀，保持。"
  }
}
foreach($imp in $improvements){ Write-Host "  $imp" }
Write-Host ""

# Step 6: 推卡片
$dimSummary = @()
foreach($dim in $dimensions.Keys){
  $s = $scores[$dim]
  $emoji = if($s.score -ge 8){'🟢'}elseif($s.score -ge 5){'🟡'}else{'🔴'}
  $dimSummary += "$emoji **$dim**: $($s.score)/10 ($($s.hits) 次命中)"
}
$dimContent = $dimSummary -join "`n"

$impContent = $improvements -join "`n`n"

Write-Host "[4/4] 推送报告卡片..."
$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content="🎤 直播话术分析报告 · $LiveTopic"}; template='red'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**主播：** $Anchor`n**话术总字数：** $($transcript.Length)`n**综合评分：** **$avgScore / 10**"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**📊 5 维度评分：**`n$dimContent"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 AI 改进建议：**`n$impContent"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**📈 后续动作：**`n• 报告同步给运营 + 主播复盘`n• 改进建议进客服话术库（19_经验沉淀库）`n• 下场直播前 30 分钟 ping 主播 review`n• cron 每场直播结束自动跑"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='📋 查 08_直播排期'}; type='primary'; url="https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=tblAuzO7UsdjlXyL"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host ""
Write-Host "Done."
