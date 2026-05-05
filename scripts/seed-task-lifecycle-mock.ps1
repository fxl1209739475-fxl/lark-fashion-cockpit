param([switch]$DryRun)
$ErrorActionPreference='Stop'
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T='tblRnB14n1xW1vou'

function Ts([string]$iso){ [DateTimeOffset]::Parse($iso).ToUnixTimeMilliseconds() }

# 时间戳（中国时区 +08:00）
$d_apr15 = Ts '2026-04-15T18:00:00+08:00'
$d_apr22 = Ts '2026-04-22T18:00:00+08:00'
$d_apr24 = Ts '2026-04-24T18:00:00+08:00'
$d_apr27 = Ts '2026-04-27T18:00:00+08:00'
$d_apr30 = Ts '2026-04-30T18:00:00+08:00'
$d_may02 = Ts '2026-05-02T18:00:00+08:00'
$d_may03 = Ts '2026-05-03T18:00:00+08:00'
$d_may04_14 = Ts '2026-05-04T14:00:00+08:00'
$d_may04_18 = Ts '2026-05-04T18:00:00+08:00'
$d_may05 = Ts '2026-05-05T18:00:00+08:00'
$d_may06 = Ts '2026-05-06T18:00:00+08:00'
$d_may08 = Ts '2026-05-08T18:00:00+08:00'
$d_may14 = Ts '2026-05-14T18:00:00+08:00'

# 24 个任务的 mock 状态铺设（演示 4 种生命周期状态）
$updates = @(
  # ✅ 已完成 4 个（含质量评估 + 复盘标签）
  @{ rid='recviy1SMyw7VP'; status='已完成'; due=$d_apr15; est=4;  start=$d_apr15-86400000;   end=$d_apr15;            track='已完成'; tags=@('按时完成','质量优秀') }
  @{ rid='recviy1SMyjM68'; status='已完成'; due=$d_apr22; est=16; start=$d_apr22-7*86400000; end=$d_apr24; tags=@('延期完成');          track='已完成'; reason='设计师同时跟两波打版，分身乏术' }
  @{ rid='recviy1SMyOcPT'; status='已完成'; due=$d_apr27; est=12; start=$d_apr27-3*86400000; end=$d_apr27;            track='已完成'; tags=@('按时完成') }
  @{ rid='recviy1SMyq2Qv'; status='已完成'; due=$d_apr30; est=8;  start=$d_apr30-2*86400000; end=$d_apr30;            track='已完成'; tags=@('按时完成','质量优秀') }

  # 🔴 逾期 2 个
  @{ rid='recviy1SMyEFSy'; status='进行中'; due=$d_may02; est=20; start=$d_may02-3*86400000; reminder='P1每3天'; track='逾期' }
  @{ rid='recviy1SMyLR7C'; status='进行中'; due=$d_may03; est=24; start=$d_may03-2*86400000; reminder='P1每3天'; track='逾期' }

  # 🟠 紧急今天 1 个
  @{ rid='recviy1SMyuMHI'; status='进行中'; due=$d_may04_18; est=8; start=$d_may04_14-86400000; reminder='P0每天'; track='紧急' }

  # 🟡 接近截止 2 个
  @{ rid='recviy1SMyyxDe'; status='待启动'; due=$d_may05; est=10; reminder='P1每3天'; track='接近截止' }
  @{ rid='recviy1SMyzOAv'; status='待启动'; due=$d_may06; est=8;  reminder='P1每3天'; track='接近截止' }

  # 🟢 正常进行 7 个
  @{ rid='recviy1SMyFWbs'; status='进行中'; due=$d_may08; est=80; start=$d_may03; reminder='P0每天'; track='正常' }
  @{ rid='recviy1SMyC9WV'; status='待启动'; due=$d_may08; est=6;  reminder='P1每3天'; track='正常' }
  @{ rid='recviy1SMyKGCV'; status='待启动'; due=$d_may14; est=4;  reminder='P2每周'; track='正常' }
  @{ rid='recviytp8nMsht'; status='进行中'; due=$d_may14; est=60; start=$d_may04_14; reminder='P0每天'; track='正常' }
  @{ rid='recviytp8nI8m2'; status='进行中'; due=$d_may08; est=16; start=$d_may03; reminder='P1每3天'; track='正常' }
  @{ rid='recviytp8n3X7w'; status='待启动'; due=$d_may14; est=12; reminder='P1每3天'; track='正常' }
  @{ rid='recviytp8nfJGF'; status='待启动'; due=$d_may14; est=10; reminder='P1每3天'; track='正常' }

  # 第二波其他保留默认（已完成无时间）
  @{ rid='recviytp8nvdlr'; status='已完成'; due=$d_apr15; est=4; start=$d_apr15-86400000; end=$d_apr15; track='已完成'; tags=@('按时完成') }
  @{ rid='recviytp8n28LH'; status='已完成'; due=$d_apr22; est=12; start=$d_apr22-3*86400000; end=$d_apr22; track='已完成'; tags=@('按时完成','质量优秀') }
  @{ rid='recviytp8nZzX8'; status='已完成'; due=$d_apr27; est=10; start=$d_apr27-2*86400000; end=$d_apr27; track='已完成'; tags=@('按时完成') }
  @{ rid='recviytp8nf2Zq'; status='已完成'; due=$d_apr30; est=6;  start=$d_apr30-86400000;   end=$d_apr30; track='已完成'; tags=@('按时完成') }
  @{ rid='recviytp8nHSVW'; status='待启动'; due=$d_may08; est=8;  reminder='P1每3天'; track='正常' }
  @{ rid='recviytp8nGj1o'; status='待启动'; due=$d_may14; est=8;  reminder='P2每周'; track='正常' }
  @{ rid='recviytp8nRCoy'; status='待启动'; due=$d_may14; est=10; reminder='P1每3天'; track='正常' }
  @{ rid='recviytp8nn6bd'; status='待启动'; due=$d_may14; est=4;  reminder='P2每周'; track='正常' }
)

$utf8 = [System.Text.UTF8Encoding]::new($false)
$tmpFile = "C:\Users\冯兴龙\AppData\Local\Temp\task-update.json"

$count = 0
foreach($u in $updates){
  $payload = [ordered]@{}
  $payload['状态'] = @($u.status)
  if($u.due){ $payload['截止日期'] = $u.due }
  if($u.est){ $payload['预估耗时h'] = $u.est }
  if($u.start){ $payload['实际开始'] = $u.start }
  if($u.end){ $payload['实际完成'] = $u.end }
  if($u.reminder){ $payload['提醒级别'] = @($u.reminder) }
  if($u.track){ $payload['追踪状态'] = @($u.track) }
  if($u.tags){ $payload['复盘标签'] = $u.tags }
  if($u.reason){ $payload['延期原因'] = $u.reason }

  $json = $payload | ConvertTo-Json -Compress -Depth 5
  [System.IO.File]::WriteAllText($tmpFile, $json, $utf8)

  if($DryRun){
    Write-Host "DRY $($u.rid): $json"
  } else {
    Write-Host "UPD $($u.rid)"
    cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $T --record-id $($u.rid) --json @./task-update.json --jq .data.record.id"
  }
  $count++
}
Write-Host ""
Write-Host "Done $count tasks updated."
