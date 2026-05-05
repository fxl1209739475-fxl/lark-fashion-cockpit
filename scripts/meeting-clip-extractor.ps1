# meeting-clip-extractor.ps1 — 妙记自动剪辑高光片段
#
# 输入：minute_token + 主题关键词 + 时长
# 输出：mp4（含自动 SRT 字幕）
#
# 工作流：
#   1. lark-cli vc +notes 拉章节摘要
#   2. 关键词匹配最佳章节
#   3. lark-cli minutes +download 下载音频（如未下载）
#   4. 解析 transcript.txt 提取该时段的 "说话人+时间戳+文字"
#   5. 自动转 SRT（时间戳相对化）
#   6. PIL 生成 bg.png（标题 = 主题）
#   7. ffmpeg 一站式：剪音频 + 烧字幕 + 合成 mp4

param(
  [Parameter(Mandatory=$true)][string]$MinuteToken,
  [Parameter(Mandatory=$true)][string]$Theme,
  [int]$Duration = 20,
  [string]$OutDir = 'C:\Users\冯兴龙\lark-fashion-cockpit\assets\clips'
)
$ErrorActionPreference='Stop'
$BOSS_CHAT='oc_45e0995a007db9d7f1859fa17b6566f6'
$WORK = 'C:\temp\clip-extract'
$FFMPEG = "C:\Users\冯兴龙\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-essentials_build\bin\ffmpeg.exe"

mkdir $OutDir -Force | Out-Null
mkdir $WORK -Force | Out-Null

Write-Host "==================================================="
Write-Host "  meeting-clip-extractor"
Write-Host "  Token: $MinuteToken"
Write-Host "  Theme: $Theme"
Write-Host "  Duration: $Duration s"
Write-Host "==================================================="
Write-Host ""

# Step 1: 拉妙记章节
Write-Host "[1/7] 拉妙记章节..."
$out = cmd /c "lark-cli vc +notes --minute-tokens $MinuteToken 2>nul"
$idx = $out.IndexOf('{')
$obj = $out.Substring($idx) | ConvertFrom-Json
$note = $obj.data.notes[0]
$chapters = $note.artifacts.chapters
$title = $note.title
Write-Host "  ✓ $title / $($chapters.Count) 章节"
Write-Host ""

# Step 2: 关键词匹配最佳章节
Write-Host "[2/7] 主题匹配..."
$themeKeys = $Theme -split '\s+|,|，|/|和|或'
$best = $null
$bestScore = 0
foreach($c in $chapters){
  $score = 0
  foreach($k in $themeKeys){
    if($k.Length -lt 2){ continue }
    if($c.title -match $k){ $score += 3 }
    if($c.summary_content -match $k){ $score += 2 }
  }
  if($score -gt $bestScore){
    $bestScore = $score
    $best = $c
  }
}
if(-not $best){
  Write-Host "  ⚠ 无章节匹配，使用第 5 个章节作为默认"
  $best = $chapters[4]
}
$chStartSec = [Math]::Floor([int]$best.start_ms / 1000)
$chStopSec = [Math]::Floor([int]$best.stop_ms / 1000)
Write-Host "  ✓ 最佳章节: $($best.title)"
Write-Host "  ✓ 时段: $([Math]::Floor($chStartSec/60)):$($chStartSec%60).PadLeft(2,'0') ~ $([Math]::Floor($chStopSec/60)):$($chStopSec%60).PadLeft(2,'0')"
Write-Host ""

# Step 3: 确保音频已下载
Write-Host "[3/7] 检查音频文件..."
$mediaDir = "C:\Users\冯兴龙\lark-fashion-cockpit\minutes\clip-extractor"
$mediaFile = Get-ChildItem -Path $mediaDir -Filter "*$MinuteToken*" -ErrorAction SilentlyContinue | Where-Object { $_.Extension -in '.m4a','.mp4','.mp3' } | Select-Object -First 1
if(-not $mediaFile){
  $mediaFile = Get-ChildItem -Path $mediaDir -Filter "*audio*" -ErrorAction SilentlyContinue | Select-Object -First 1
}
if(-not $mediaFile){
  Write-Host "  下载中..."
  cmd /c "lark-cli minutes +download --minute-tokens $MinuteToken --output-dir $mediaDir 2>&1" | Out-Null
  $mediaFile = Get-ChildItem -Path $mediaDir -Filter "*audio*" | Select-Object -First 1
}
Write-Host "  ✓ 音频: $($mediaFile.Name)"
Write-Host ""

# Step 4: 解析 transcript 找该章节内的金句
Write-Host "[4/7] 解析 transcript 选金句..."
$transcriptPath = "C:\Users\冯兴龙\lark-fashion-cockpit\minutes\$MinuteToken\transcript.txt"
if(-not (Test-Path $transcriptPath)){
  Write-Host "  ⚠ transcript 不存在: $transcriptPath"
  exit 1
}
$lines = Get-Content $transcriptPath -Encoding UTF8

# 解析"说话人 时间戳 内容"格式
$segments = @()
for($i=0; $i -lt $lines.Count; $i++){
  $l = $lines[$i]
  if($l -match '^\S.*\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*$'){
    $h = [int]$matches[1]; $m = [int]$matches[2]; $s = [int]$matches[3]
    $absSec = $h*3600 + $m*60 + $s
    # 内容在下一非空行
    $content = ''
    for($j=$i+1; $j -lt $lines.Count -and $j -lt $i+5; $j++){
      if($lines[$j].Trim()){ $content = $lines[$j].Trim(); break }
    }
    $segments += [PSCustomObject]@{ time_sec = $absSec; text = $content }
  }
}
Write-Host "  ✓ 解析 $($segments.Count) 段"

# 在章节时间范围内匹配主题关键词
$candidateSegs = $segments | Where-Object {
  $_.time_sec -ge $chStartSec -and $_.time_sec -le $chStopSec -and $_.text.Length -gt 30
}

# 对每段评分（含主题关键词数 + 长度）
$bestStartSeg = $null
$bestSegScore = 0
foreach($seg in $candidateSegs){
  $score = 0
  foreach($k in $themeKeys){
    if($k.Length -lt 2){ continue }
    if($seg.text -match $k){ $score += 5 }
  }
  $score += [Math]::Min(3, [int]($seg.text.Length / 100))
  if($score -gt $bestSegScore){ $bestSegScore = $score; $bestStartSeg = $seg }
}

if(-not $bestStartSeg){
  Write-Host "  ⚠ 章节内无金句段，用章节起点"
  $clipStartSec = $chStartSec
} else {
  $clipStartSec = $bestStartSeg.time_sec
  Write-Host "  ✓ 金句起点: ${clipStartSec}s ($($bestStartSeg.text.Substring(0, [Math]::Min(60, $bestStartSeg.text.Length)))...)"
}
$clipEndSec = $clipStartSec + $Duration
$startMin = [Math]::Floor($clipStartSec/60).ToString().PadLeft(2,'0')
$startSecOnly = ($clipStartSec%60).ToString().PadLeft(2,'0')
$ssExpr = "00:${startMin}:${startSecOnly}"
Write-Host "  ✓ 剪辑窗口: $ssExpr +${Duration}s"
Write-Host ""

# Step 5: 提取 clip 内的 transcript 段并生成 SRT
Write-Host "[5/7] 自动生成 SRT 字幕..."
$clipSegs = @()
foreach($s in $segments){
  if([int]$s.time_sec -ge [int]$clipStartSec -and [int]$s.time_sec -lt [int]$clipEndSec -and $s.text -and $s.text.Length -gt 0){
    $clipSegs += $s
  }
}
Write-Host "  在窗口 [$clipStartSec, $clipEndSec) 找到 $($clipSegs.Count) 段"
$srtLines = @()
$idx = 1
for($k=0; $k -lt $clipSegs.Count; $k++){
  $seg = $clipSegs[$k]
  $relStart = $seg.time_sec - $clipStartSec
  if($k -lt $clipSegs.Count - 1){
    $relEnd = $clipSegs[$k+1].time_sec - $clipStartSec
  } else {
    $relEnd = $Duration
  }
  if($relEnd -gt $Duration){ $relEnd = $Duration }
  if($relStart -ge $Duration){ break }
  # 截短文字（每条字幕最多 60 字）
  $txt = $seg.text
  if($txt.Length -gt 60){ $txt = $txt.Substring(0, 60) + '...' }

  $sH = [Math]::Floor($relStart/3600).ToString().PadLeft(2,'0')
  $sM = [Math]::Floor(($relStart%3600)/60).ToString().PadLeft(2,'0')
  $sS = ($relStart%60).ToString().PadLeft(2,'0')
  $eH = [Math]::Floor($relEnd/3600).ToString().PadLeft(2,'0')
  $eM = [Math]::Floor(($relEnd%3600)/60).ToString().PadLeft(2,'0')
  $eS = ($relEnd%60).ToString().PadLeft(2,'0')
  $srtLines += "$idx"
  $srtLines += "${sH}:${sM}:${sS},000 --> ${eH}:${eM}:${eS},000"
  $srtLines += $txt
  $srtLines += ""
  $idx++
}
$srtContent = $srtLines -join "`n"
$utf8 = [System.Text.UTF8Encoding]::new($false)
$srtPath = "$WORK\sub.srt"
[System.IO.File]::WriteAllText($srtPath, $srtContent, $utf8)
Write-Host "  ✓ 生成 $($idx-1) 条字幕"
Write-Host ""

# Step 6: 生成背景图（PIL）
Write-Host "[6/7] 生成背景图..."
$bgPy = @"
from PIL import Image, ImageDraw, ImageFont
W,H=1920,1080
img=Image.new('RGB',(W,H),(24,24,32))
d=ImageDraw.Draw(img)
d.rectangle([0,0,W,8],fill=(220,50,50))
ft=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',90)
title='$Theme'
b=d.textbbox((0,0),title,font=ft)
d.text((W//2-(b[2]-b[0])//2,180),title,font=ft,fill=(255,220,100))
fs=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',40)
sub='lark-fashion-cockpit · 妙记自动剪辑'
b=d.textbbox((0,0),sub,font=fs)
d.text((W//2-(b[2]-b[0])//2,310),sub,font=fs,fill=(180,180,200))
fe=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',220)
b=d.textbbox((0,0),'❝',font=fe)
d.text((W//2-(b[2]-b[0])//2,440),'❝',font=fe,fill=(80,60,60))
d.rectangle([0,H-100,W,H],fill=(40,40,50))
ff=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
foot='来源: $title (token $MinuteToken) · ${ssExpr} +${Duration}s'
b=d.textbbox((0,0),foot,font=ff)
d.text((W//2-(b[2]-b[0])//2,H-65),foot,font=ff,fill=(160,160,180))
img.save('$WORK\\bg.png')
print('OK')
"@ -replace '\\','\\'
$bgPy | Out-File "$WORK\bg.py" -Encoding utf8
$env:PYTHONIOENCODING='utf-8'
python "$WORK\bg.py"
Write-Host ""

# Step 7: ffmpeg 一站式
Write-Host "[7/7] ffmpeg 合成..."
Copy-Item $mediaFile.FullName "$WORK\src.m4a" -Force

cd $WORK
$outFile = "$OutDir\clip-$(Get-Date -Format 'yyyyMMdd-HHmmss').mp4"

# 临时关闭错误抛出（ffmpeg stderr 输出量大但不是真错）
$savedEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'

$ffmpegLog = "$WORK\ffmpeg.log"
$ffmpegCmd = "& '$FFMPEG' -y -loop 1 -i bg.png -ss $ssExpr -t $Duration -i src.m4a -vf `"subtitles=sub.srt:force_style='FontName=Microsoft YaHei,FontSize=42,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=1,Outline=3,Alignment=2,MarginV=80'`" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest '$outFile' *> '$ffmpegLog'"
Invoke-Expression $ffmpegCmd

$ErrorActionPreference = $savedEAP

if(Test-Path $outFile){
  $size = [Math]::Round((Get-Item $outFile).Length / 1MB, 2)
  Write-Host ""
  Write-Host "✅ 视频生成成功:"
  Write-Host "   $outFile"
  Write-Host "   $size MB · ${Duration}s"
  Write-Host ""

  # 推送卡片
  $card = @{
    config=@{wide_screen_mode=$true}
    header=@{title=@{tag='plain_text'; content="🎬 高光剪辑完成 · $Theme"}; template='violet'}
    elements=@(
      @{tag='div'; text=@{tag='lark_md'; content="**会议:** $title`n**主题:** $Theme`n**时长:** ${Duration} 秒`n**起点:** $ssExpr`n**字幕:** $($idx-1) 条自动生成"}}
      @{tag='hr'}
      @{tag='div'; text=@{tag='lark_md'; content="**🤖 全自动链路（30 秒出片）：**`n1. lark-cli 拉妙记章节`n2. 关键词匹配最佳章节`n3. transcript 找金句段`n4. 自动生成 SRT（时间戳相对化）`n5. PIL 生成主题背景图`n6. ffmpeg 烧字幕合成 mp4`n`n**这是 lark-fashion-cockpit 第 32 个能力。**"}}
    )
  } | ConvertTo-Json -Depth 12 -Compress
  $cmdEsc = $card -replace '"','""'
  cmd /c "lark-cli im +messages-send --chat-id $BOSS_CHAT --msg-type interactive --content `"$cmdEsc`" --jq .data.message_id"
}
