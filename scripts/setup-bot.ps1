# setup-bot.ps1 — lark-fashion-cockpit 机器人一键配置
#
# 用法：
#   PowerShell -File setup-bot.ps1 -AppId cli_xxx -AppSecret xxx
#
# 做的事：
#   1. 添加新 profile "lark-fashion-cockpit-bot"
#   2. 测试连接（auth status）
#   3. 检查 scope 配置
#   4. 用 bot 身份发测试消息验证

param(
  [Parameter(Mandatory=$true)][string]$AppId,
  [Parameter(Mandatory=$true)][string]$AppSecret,
  [string]$ProfileName='lark-fashion-cockpit-bot',
  [string]$BossChat='oc_45e0995a007db9d7f1859fa17b6566f6'
)
$ErrorActionPreference='Stop'

Write-Host "==================================================="
Write-Host "  setup-bot · 飞书机器人一键配置"
Write-Host "==================================================="
Write-Host ""

# Step 1: 添加 profile
Write-Host "[1/4] 添加 lark-cli profile..."
$AppSecret | cmd /c "lark-cli profile add --name $ProfileName --app-id $AppId --app-secret-stdin --brand feishu --use"
Write-Host ""

# Step 2: 测试 auth
Write-Host "[2/4] 测试机器人连接..."
$status = cmd /c "lark-cli auth status 2>&1"
Write-Host $status
if($status -match 'error|fail'){
  Write-Host "❌ 机器人连接失败 - 检查 App ID / Secret 是否正确"
  exit 1
}
Write-Host "✅ 机器人连接正常"
Write-Host ""

# Step 3: 检查事件订阅 + 必需 scope
Write-Host "[3/4] 检查权限 scope..."
$scopes = cmd /c "lark-cli auth scopes 2>&1"
$required = @(
  'im:message:send_as_bot',
  'im:message.p2p_msg.readonly',
  'im:resource:upload'
)
$missing = @()
foreach($s in $required){
  if($scopes -notmatch $s){
    $missing += $s
  }
}
if($missing.Count -gt 0){
  Write-Host "⚠️ 缺少 scope（去飞书后台权限管理添加）："
  foreach($m in $missing){ Write-Host "  - $m" }
} else {
  Write-Host "✅ 所有 scope 已配置"
}
Write-Host ""

# Step 4: 发测试消息
Write-Host "[4/4] 发测试消息到老板群..."
$body = @"
{"config":{"wide_screen_mode":true},"header":{"title":{"tag":"plain_text","content":"🤖 机器人已上线"},"template":"green"},"elements":[{"tag":"div","text":{"tag":"lark_md","content":"**lark-fashion-cockpit 助手机器人配置成功**\n\nApp: $AppId\nProfile: $ProfileName\n时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')\n\n下一步:\n1. 启动 event-listener.py（24h 后台跑）\n2. 老板娘飞书一句话指挥即可"}}]}
"@
$cmdEsc = $body -replace '"','""'
$result = cmd /c "lark-cli im +messages-send --as bot --chat-id $BossChat --msg-type interactive --content `"$cmdEsc`""
Write-Host $result
Write-Host ""

Write-Host "==================================================="
Write-Host "  ✅ 配置完成"
Write-Host "==================================================="
Write-Host ""
Write-Host "下一步："
Write-Host "  1. 启动 listener:"
Write-Host "     start /b python C:\Users\冯兴龙\lark-fashion-cockpit\scripts\event-listener.py"
Write-Host ""
Write-Host "  2. 老板娘飞书私聊机器人 / 群里@机器人"
Write-Host "     说: 巡检任务 / DRS 配什么好 / 看下利润"
Write-Host ""
Write-Host "  切回原 user profile:"
Write-Host "     lark-cli profile use -"
