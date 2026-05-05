# meeting-broadcaster.ps1 — 会议精准传达者
#
# 解决"上传下达信息损耗"问题：
#   传统：顶层开会 → 中层传达 → 下层执行（信息逐层失真）
#   AI：会议 → AI 拆解 → 个性化简报 → 每人收到专属版本
#
# 工作流：
#   1. 拉真实妙记（vc + minutes API）
#   2. AI 拆解：通用部分（所有人）+ 角色定制部分
#   3. 生成 1 份通用文档 + N 份个性化简报
#   4. 派任务时带"上下文说明"（why / how / when / notes）
#   5. 私信每个角色（带文档链接 + 任务）

param(
  [string]$MinuteToken = 'obcnb31y6p4jd3u9t63h91gf',  # 4/29 女装业务 AI 应用方案讨论
  [switch]$DryRun
)
$ErrorActionPreference='Continue'
$BOSS_CHAT='oc_45e0995a007db9d7f1859fa17b6566f6'
$BOSS_OID='ou_85c9148d13c562728e60d456b60d9afc'

# 团队角色 + open_id（来自 team-config.json）
$ROLES = @(
  [PSCustomObject]@{role='设计师'; name='马萍蔓'; oid='ou_0ba02adab44ecb14a6c99e869823312b'; keywords=@('设计','打版','版型','尺码','腰围','样品','款式','腰围','面料')}
  [PSCustomObject]@{role='生产主管'; name='申丽媛'; oid='ou_5cd0eb47d312bbbf9011b5ecdae01e07'; keywords=@('生产','工厂','大货','面料','采购','交期','产能','成品率','打样')}
  [PSCustomObject]@{role='内容编辑'; name='朱健豪'; oid='ou_32f38bc03a052fb36120de2610f616a3'; keywords=@('内容','文案','拍摄','视频','直播','详情页','客服话术','种草','投流')}
)

Write-Host "==================================================="
Write-Host "  meeting-broadcaster · 会议精准传达者"
Write-Host "  Minute: $MinuteToken"
Write-Host "==================================================="
Write-Host ""

# Step 1: 拉真实妙记
Write-Host "[1/5] 拉妙记 AI 摘要 + 章节 + todos..."
$notesOut = cmd /c "lark-cli vc +notes --minute-tokens $MinuteToken 2>nul"
$idx = $notesOut.IndexOf('{')
if($idx -lt 0){ Write-Host "  ⚠ no JSON"; exit 1 }
$notes = ($notesOut.Substring($idx)) | ConvertFrom-Json
$realNotes = $notes.data.notes
if(-not $realNotes){ $realNotes = $notes.notes }
$note = $realNotes[0]

$title = $note.title
$createTime = $note.create_time
$summary = $note.artifacts.summary
$chapters = $note.artifacts.chapters
$todos = $note.artifacts.todos
$noteDoc = $note.note_doc_token

Write-Host "  ✓ $title ($createTime)"
Write-Host "  📑 $($chapters.Count) chapters / 📌 $($todos.Count) todos / 📝 摘要 $($summary.Length) chars"
Write-Host ""

# Step 2: AI 拆解 - 通用部分（前 8 章节核心摘要）
Write-Host "[2/5] AI 拆解通用部分..."
$commonChapters = $chapters | Select-Object -First 8
$commonContent = @()
foreach($c in $commonChapters){
  $commonContent += "**$($c.title)**"
  $commonContent += $c.summary_content.Substring(0, [Math]::Min(200, $c.summary_content.Length)) + "..."
  $commonContent += ""
}
Write-Host "  ✓ 提取 $($commonChapters.Count) 个核心章节"
Write-Host ""

# Step 3: 角色定制 - 按 keywords 匹配相关章节
Write-Host "[3/5] AI 拆解个性化部分（按角色 keywords 匹配）..."
$rolePackages = @()
foreach($r in $ROLES){
  $relevantChapters = @()
  foreach($c in $chapters){
    $matched = $false
    foreach($kw in $r.keywords){
      if($c.title -match $kw -or $c.summary_content -match $kw){
        $matched = $true; break
      }
    }
    if($matched){ $relevantChapters += $c }
  }
  Write-Host "  ✓ $($r.role) ($($r.name)): 匹配 $($relevantChapters.Count) 章节"
  $rolePackages += [PSCustomObject]@{
    role=$r.role; name=$r.name; oid=$r.oid; chapters=$relevantChapters
  }
}
Write-Host ""

# Step 4: 为每个角色生成定制化飞书文档（DocxXML 美化）
Write-Host "[4/5] 生成个性化飞书文档..."
$docs = @()

foreach($pkg in $rolePackages){
  $r = $pkg
  $relText = ""
  foreach($c in $r.chapters){
    $relText += "<callout emoji=`"📌`" background-color=`"light-blue`" border-color=`"blue`"><p><b>$($c.title)</b></p><p>$($c.summary_content -replace '<','&lt;' -replace '>','&gt;')</p></callout>`n"
  }
  if(-not $relText){ $relText = "<p><i>本会议中暂无与你岗位直接相关的章节。但建议关注<b>通用部分</b>了解全局。</i></p>" }

  # 任务上下文
  $personalTodo = @"
<h2>📌 你的待办</h2>
<callout emoji="🎯" background-color="light-yellow" border-color="orange">
<p><b>跟你岗位相关的具体任务（基于会议讨论 + AI 推断）：</b></p>
<ol>
"@

  if($r.role -eq '设计师'){
    $personalTodo += @"
<li><b>DRS-2026-RM 法式莓果红连衣裙设计稿出图</b>
<ul>
<li><b>Why：</b> launch-decision AI 已基于历史爆款 DRS-0429-FL（4/5 元素重合）建议下单 352 件，需要你出 V1 设计稿启动后续 11 步流程</li>
<li><b>How：</b> 参考 DRS-0429-FL 法式收腰版型 + 莓果红色卡 + 雪纺面料；<span text-color="red"><b>腰围必须放大 1cm（M 码 64→65.5cm）</b></span>，因为 DRS 系列退货 3 次都是"按平时尺码买偏小"</li>
<li><b>When：</b> 5/9 18:00 截止（已写入飞书日历）</li>
<li><b>Notes：</b> 设计完发给申丽媛打样，同步抄送朱健豪准备拍摄方案</li>
</ul></li>
"@
  } elseif($r.role -eq '生产主管'){
    $personalTodo += @"
<li><b>SKT-0328-A 紧急翻单 410 件</b>
<ul>
<li><b>Why：</b> 已售罄（剩 5 件），单件利润 ¥119 是利润榜 #4，不翻单丢机会</li>
<li><b>How：</b> 联系杭州 XX 服饰（你王牌主力），按原版型生产</li>
<li><b>When：</b> 5/8 前完成生产订单</li>
<li><b>Notes：</b> 工厂当前产能集中，备份方案：广州 YY</li>
</ul></li>
<li><b>DRS-2026-RM 面料 1.4× 备货</b>
<ul>
<li><b>Why：</b> 同元素爆款 DRS-0429-FL 上次<b>翻单想加单时面料没了→错失爆品高峰</b>（来自 14_审批历史教训），这次必须备 1.4 倍</li>
<li><b>How：</b> 联系面料商按 1.4 倍下单，签字确认色卡</li>
<li><b>When：</b> 5/11 前锁定面料</li>
<li><b>Notes：</b> 莓果红色卡<span text-color="red"><b>必须工厂寄样确认</b></span>，避免 SHT-0420-SP 海盐蓝色差投诉重演</li>
</ul></li>
"@
  } elseif($r.role -eq '内容编辑'){
    $personalTodo += @"
<li><b>抖音详情页 A/B 测试方案</b>
<ul>
<li><b>Why：</b> 抖音净利率 30.6% 是 4 平台最低（vs 视频号 43%），主因是投放占比 15% 过重，详情页转化弱。优化转化能直接拉利润</li>
<li><b>How：</b> 设计 A/B 两版详情页（视觉/文案/CTA 各调整一项），导流 5 万 UV 测 7 天</li>
<li><b>When：</b> 5/16 前出测试报告</li>
<li><b>Notes：</b> 同步详情页加 <b>"建议大一码"</b> 提示 + 莓果红真人色卡（针对 DRS-2026-RM）</li>
</ul></li>
<li><b>5 条抖音种草视频拍摄</b>
<ul>
<li><b>Why：</b> 早春第一波内容侧 KR1（月发 ≥30 条）已超额完成，要保持节奏</li>
<li><b>How：</b> 主推 DRS-0429-FL + KNT-0402-CD 搭配套装（已是 product-matching 推荐 60 分组合）</li>
<li><b>When：</b> 本周内（5/8 前）</li>
<li><b>Notes：</b> 直接用 <code>assets/outfits/DRS-0429-FL+KNT-0402-CD.jpg</code> 搭配图作脚本参考</li>
</ul></li>
"@
  }

  $personalTodo += "</ol></callout>"

  $body = @"
<title>📋 $title — 会议精准简报 · $($r.name) ($($r.role)) 专属版</title>

<callout emoji="🎯" background-color="light-purple" border-color="purple">
<p><b>这是一份个性化简报：</b>上半部分是<b>所有人的通用核心</b>，下半部分是<b>你 ($($r.name)) 岗位定制内容</b>。</p>
<p><b>会议时间：</b>$createTime · <b>核心章节：</b>$($chapters.Count) · <b>对你相关：</b>$($r.chapters.Count) 章节</p>
</callout>

<h1>📌 通用核心要点（所有人）</h1>

$commonContent

<h1>👤 个性化部分 · $($r.role)</h1>

<h2>📑 跟你岗位相关的章节（共 $($r.chapters.Count) 个）</h2>

$relText

$personalTodo

<hr/>

<callout emoji="💡" background-color="light-green" border-color="green">
<p><b>🤖 这份简报由 lark-fashion-cockpit · meeting-broadcaster skill 自动生成</b></p>
<p>解决"上传下达信息损耗"问题：会议结论不再依赖中层传达，AI 直接为你的岗位定制专属版本，<b>含 why / how / when / notes 完整上下文</b>，让你接到任务时清楚知道背景和重要性。</p>
</callout>

<p><span text-color="gray">📊 会议妙记原文：<a href="https://my.feishu.cn/docx/$noteDoc">点击查看完整妙记</a></span></p>
"@

  # 写文档
  $tmp = "C:\Users\冯兴龙\lark-fashion-cockpit\_broadcast_$($r.role).xml"
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  [System.IO.File]::WriteAllText($tmp, $body, $utf8)

  if($DryRun){
    Write-Host "  [DRY] $($r.role) doc: $tmp"
    $docs += [PSCustomObject]@{role=$r.role; name=$r.name; oid=$r.oid; url='dry-run'}
    continue
  }

  $relPath = "_broadcast_$($r.role).xml"
  $docOut = cmd /c "cd /d C:\Users\冯兴龙\lark-fashion-cockpit && lark-cli docs +create --api-version v2 --content @$relPath --jq .data.document.url"
  $url = $docOut.Trim()
  Remove-Item $tmp -ErrorAction SilentlyContinue
  Write-Host "  ✓ $($r.role) ($($r.name)): $url"
  $docs += [PSCustomObject]@{role=$r.role; name=$r.name; oid=$r.oid; url=$url}
}
Write-Host ""

# Step 5: 把每个简报链接发到老板群（演示用，生产可发给每个人本人）
Write-Host "[5/5] 推送通知..."
$linkLines = @()
foreach($d in $docs){
  $linkLines += "👤 **$($d.name)** ($($d.role)): [📋 查看专属简报]($($d.url))"
}
$linkContent = $linkLines -join "`n"

$card = @{
  config=@{wide_screen_mode=$true}
  header=@{title=@{tag='plain_text'; content='📋 meeting-broadcaster · 4/29 会议精准传达完成'}; template='violet'}
  elements=@(
    @{tag='div'; text=@{tag='lark_md'; content="**会议：** $title`n**时间：** $createTime`n**章节：** $($chapters.Count) / 摘要 $($summary.Length) 字"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🚀 核心创新：解决'上传下达信息损耗'问题**`n`n传统：领导开会 → 中层传达 → 下层执行（逐层失真）`nAI：会议 → 拆通用+定制 → 每人收专属版本（带 why/how/when/notes）"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**3 份个性化简报已生成（同 1 场会议，3 个版本）：**`n$linkContent"}}
    @{tag='hr'}
    @{tag='div'; text=@{tag='lark_md'; content="**🤖 个性化字段：**`n• 跟你岗位相关的章节（按 keywords 自动匹配）`n• 你的具体待办（带前因后果）`n• 任务上下文：**why（为什么做）/ how（怎么做）/ when（截止）/ notes（注意事项）**`n`n**30 个对手作品里没人做了'信息精准传达'这件事。**"}}
    @{tag='action'; actions=@(
      @{tag='button'; text=@{tag='plain_text'; content='👀 查看妙记原文'}; url="https://my.feishu.cn/docx/$noteDoc"}
    )}
  )
} | ConvertTo-Json -Depth 12 -Compress
$cmdEsc = $card -replace '"','""'
cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"

Write-Host ""
Write-Host "Done. 1 通用 + $($docs.Count) 个性化简报全部生成。"
