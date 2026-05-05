# deploy-check.ps1 — 部署完整性检查
#
# 在老板娘电脑首次启动 listener 前跑一遍，确保所有依赖都到位。

$ErrorActionPreference='Continue'
Write-Host "==================================================="
Write-Host "  lark-fashion-cockpit · 部署完整性检查"
Write-Host "==================================================="
Write-Host ""

$pass = 0; $fail = 0; $warn = 0

function Check($name, $ok, $detail){
  if($ok -eq 'pass'){ Write-Host "  ✅ $name : $detail"; $script:pass++ }
  elseif($ok -eq 'fail'){ Write-Host "  ❌ $name : $detail"; $script:fail++ }
  else{ Write-Host "  ⚠️ $name : $detail"; $script:warn++ }
}

# 1. 检查 lark-cli
Write-Host "[1] lark-cli 版本"
$ver = cmd /c "lark-cli --version 2>&1"
if($ver -match 'lark-cli|version'){ Check 'lark-cli' 'pass' $ver }
else{ Check 'lark-cli' 'fail' '未安装。运行: npm install -g @larksuite/cli' }
Write-Host ""

# 2. 检查 Python
Write-Host "[2] Python"
$py = cmd /c "python --version 2>&1"
if($py -match 'Python 3'){ Check 'Python' 'pass' $py }
else{ Check 'Python' 'fail' "未安装 Python 3" }
Write-Host ""

# 3. 检查 httpx + jwt
Write-Host "[3] Python 依赖"
$httpx = cmd /c "python -c ""import httpx; print(httpx.__version__)"" 2>&1"
if($httpx -match '^\d'){ Check 'httpx' 'pass' "v$httpx" }
else{ Check 'httpx' 'fail' "运行: pip install httpx" }
Write-Host ""

# 4. 检查 lark-cli profile
Write-Host "[4] lark-cli profile"
$profs = cmd /c "lark-cli profile list 2>&1"
if($profs -match 'lark-fashion-cockpit-bot'){ Check 'bot profile' 'pass' '已配置' }
else{ Check 'bot profile' 'fail' '运行 setup-bot.ps1 配置' }
if($profs -match '\*'){ Check '当前 profile' 'pass' '已激活' }
else{ Check '当前 profile' 'warn' "运行: lark-cli profile use lark-fashion-cockpit-bot" }
Write-Host ""

# 5. 检查 auth status
Write-Host "[5] 飞书 API 连接"
$auth = cmd /c "lark-cli auth status --as bot 2>&1"
if($auth -match 'success|active|valid|ok'){ Check '机器人 token' 'pass' '正常' }
else{ Check '机器人 token' 'warn' '可能需要重新登录' }
Write-Host ""

# 6. 检查 scopes
Write-Host "[6] 关键 scope"
$scopes = cmd /c "lark-cli auth scopes --as bot 2>&1"
foreach($req in @('im:message:send_as_bot','im:message.p2p_msg.readonly','im:resource:upload')){
  if($scopes -match $req){ Check $req 'pass' '已授权' }
  else{ Check $req 'fail' '飞书后台 → 权限管理 → 添加' }
}
Write-Host ""

# 7. 检查关键脚本
Write-Host "[7] 核心脚本"
$scripts = @(
  'event-listener.py',
  'task-tracker.ps1',
  'product-matching-demo.ps1',
  'launch-decision.ps1',
  'profit-analysis.ps1',
  'task-retrospective.ps1'
)
$dir = 'C:\Users\冯兴龙\lark-fashion-cockpit\scripts'
foreach($s in $scripts){
  if(Test-Path "$dir\$s"){ Check $s 'pass' '存在' }
  else{ Check $s 'fail' "缺失: $dir\$s" }
}
Write-Host ""

# 8. 检查 logs 目录
Write-Host "[8] logs 目录"
if(Test-Path "$dir\..\logs"){ Check 'logs/' 'pass' '存在' }
else{
  New-Item -Path "$dir\..\logs" -ItemType Directory -Force | Out-Null
  Check 'logs/' 'pass' '已自动创建'
}
Write-Host ""

# 9. 检查飞书机器人能否真发消息
Write-Host "[9] 测试机器人发消息能力"
$body = '{"text":"deploy-check 测试 - 收到此消息表示部署成功 ✅"}'
$cmdEsc = $body -replace '"','""'
$send = cmd /c "lark-cli im +messages-send --as bot --chat-id oc_45e0995a007db9d7f1859fa17b6566f6 --msg-type text --content `"$cmdEsc`" 2>&1"
if($send -match 'message_id|ok'){ Check '发消息测试' 'pass' '成功送达' }
else{ Check '发消息测试' 'fail' "失败: $send" }
Write-Host ""

# 总结
Write-Host "==================================================="
Write-Host "  结果: ✅ $pass / ⚠️ $warn / ❌ $fail"
Write-Host "==================================================="

if($fail -eq 0){
  Write-Host ""
  Write-Host "🎉 部署完整！可以启动 listener："
  Write-Host ""
  Write-Host "  start /b python C:\Users\冯兴龙\lark-fashion-cockpit\scripts\event-listener.py > C:\Users\冯兴龙\lark-fashion-cockpit\logs\listener.log 2>&1"
  Write-Host ""
  Write-Host "然后老板娘飞书一句话即可触发！"
} else {
  Write-Host ""
  Write-Host "⚠️ 修复上面 ❌ 项再启动"
}
