# seed-livestream-811.ps1 — 把图片中的 8/11 真实数据导入 21/22/23 表

$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T21='tblKHslcP48tXi09'
$T22='tblbzKMGjdJUja5O'
$T23='tbljntqmTIyKraiE'

function Ts($iso){ [DateTimeOffset]::Parse($iso).ToUnixTimeMilliseconds() }
$d_811 = Ts '2026-08-11T20:00:00+08:00'

function Insert($tid, $payload){
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $json = $payload | ConvertTo-Json -Compress
  [System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\seed.json", $json, $utf8)
  cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $tid --json @./seed.json --jq .data.record.id" | Out-Null
}

Write-Host "[1/3] 21_直播场次数据..."
# 早场 4 平台
$dawn = @(
  @{platform='抖音';   uv=89144;  sale=69000;  refund=20000; fans=8;  invGmv=34483}
  @{platform='小红书'; uv=23296;  sale=22000;  refund=1000;  fans=15; invGmv=6960}
  @{platform='视频号'; uv=67886;  sale=64000;  refund=4000;  fans=2;  invGmv=21798}
  @{platform='淘宝';   uv=3178;   sale=0;      refund=0;     fans=4;  invGmv=2580}
)
foreach($p in $dawn){
  Insert $T21 @{
    '场次'=@('早场'); '日期'=$d_811; '主播'='东东'; '平台'=@($p.platform)
    'UV'=$p.uv; '实销金额'=$p.sale; '退款金额'=$p.refund; '涨粉'=$p.fans; '库存GMV'=$p.invGmv
  }
}
# 晚场 4 平台
$night = @(
  @{platform='抖音';   uv=124598; sale=106000; refund=18000; fans=13; invGmv=880}
  @{platform='小红书'; uv=52825;  sale=46000;  refund=7000;  fans=39; invGmv=0}
  @{platform='视频号'; uv=135302; sale=119000; refund=16000; fans=4;  invGmv=1560}
  @{platform='淘宝';   uv=29916;  sale=0;      refund=6000;  fans=2;  invGmv=1580}
)
foreach($p in $night){
  Insert $T21 @{
    '场次'=@('晚场'); '日期'=$d_811; '主播'='梦瑶'; '平台'=@($p.platform)
    'UV'=$p.uv; '实销金额'=$p.sale; '退款金额'=$p.refund; '涨粉'=$p.fans; '库存GMV'=$p.invGmv
  }
}
Write-Host "  ✓ 8 场次记录"

Write-Host "[2/3] 22_直播主推款..."
# 早场主推
$dawnProds = @(
  @{name='miu风原牛';     plat='抖音';   sold=10; ctr=16.00; cvr=4.31; refund=20.00}
  @{name='miu风原牛';     plat='小红书'; sold=6;  ctr=9.27;  cvr=0;    refund=0.00}
  @{name='miu风原牛';     plat='视频号'; sold=10; ctr=15.69; cvr=5.81; refund=10.00}
  @{name='半开拉链卫衣';  plat='抖音';   sold=18; ctr=21.68; cvr=5.16; refund=16.70}
  @{name='半开拉链卫衣';  plat='小红书'; sold=1;  ctr=9.52;  cvr=0;    refund=0.00}
  @{name='半开拉链卫衣';  plat='视频号'; sold=22; ctr=23.52; cvr=6.99; refund=0.00}
)
foreach($p in $dawnProds){
  Insert $T22 @{
    '场次'=@('早场'); '日期'=$d_811; '产品名'=$p.name; '平台'=@($p.plat)
    '出单数'=$p.sold; '点击率'=$p.ctr; '转化率'=$p.cvr; '退款率'=$p.refund
  }
}
# 晚场主推
$nightProds = @(
  @{name='双色风衣';     plat='抖音';   sold=54; ctr=21.27; cvr=7.34;  refund=18.15}
  @{name='双色风衣';     plat='小红书'; sold=14; ctr=14.81; cvr=0;     refund=0.00}
  @{name='双色风衣';     plat='视频号'; sold=67; ctr=23.62; cvr=10.11; refund=17.20}
  @{name='Prada半身裙';  plat='抖音';   sold=12; ctr=21.25; cvr=4.84;  refund=8.12}
  @{name='Prada半身裙';  plat='小红书'; sold=6;  ctr=13.19; cvr=0;     refund=0.00}
  @{name='Prada半身裙';  plat='视频号'; sold=9;  ctr=21.54; cvr=3.78;  refund=11.10}
  @{name='皮草';         plat='抖音';   sold=5;  ctr=19.25; cvr=1.53;  refund=0.00}
  @{name='皮草';         plat='小红书'; sold=3;  ctr=8.54;  cvr=0;     refund=33.33}
  @{name='皮草';         plat='视频号'; sold=6;  ctr=16.84; cvr=2.78;  refund=0.00}
)
foreach($p in $nightProds){
  Insert $T22 @{
    '场次'=@('晚场'); '日期'=$d_811; '产品名'=$p.name; '平台'=@($p.plat)
    '出单数'=$p.sold; '点击率'=$p.ctr; '转化率'=$p.cvr; '退款率'=$p.refund
  }
}
Write-Host "  ✓ 15 主推款记录"

Write-Host "[3/3] 23_直播投流..."
$ads = @(
  @{phase='早场'; plat='抖音';   ad=696.00;  roi=34.13}
  @{phase='早场'; plat='视频号'; ad=409.00;  roi=51.45}
  @{phase='晚场'; plat='抖音';   ad=1506.00; roi=28.34}
  @{phase='晚场'; plat='视频号'; ad=717.10;  roi=38.43}
)
foreach($a in $ads){
  Insert $T23 @{
    '场次'=@($a.phase); '日期'=$d_811; '平台'=@($a.plat); '投流类型'=@('千川')
    '花费'=$a.ad; 'ROI'=$a.roi
  }
}
Write-Host "  ✓ 4 投流记录"

Write-Host ""
Write-Host "Done."
