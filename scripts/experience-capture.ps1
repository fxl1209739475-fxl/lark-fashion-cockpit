# experience-capture.ps1 — 员工日常一句话录入经验/教训/建议
# 用法：
#   PowerShell -File experience-capture.ps1 -Type 成功经验 -Title "..." -Desc "..." -Section 生产 -Submitter "申丽媛"

param(
  [Parameter(Mandatory=$true)][ValidateSet('成功经验','失败教训','改进建议')][string]$Type,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Desc,
  [Parameter(Mandatory=$true)][ValidateSet('生产','设计','运营','客服','内容','通用')][string]$Section,
  [Parameter(Mandatory=$true)][string]$Submitter
)
$BASE = if($env:LARK_FASHION_COCKPIT_BASE_TOKEN){$env:LARK_FASHION_COCKPIT_BASE_TOKEN}else{'LWsdbVtIaa2MaDsANm3cNdYgn1j'}
$T19='tbls1h9p2FL87bqG'

$now = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()
$payload = @{
  '经验标题' = $Title
  '类型' = @($Type)
  '板块' = @($Section)
  '详细描述' = $Desc
  '提交日期' = $now
  '部门审批状态' = @('待审批')
  '总决策状态' = @('待审批')
} | ConvertTo-Json -Compress

$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText("C:\Users\冯兴龙\AppData\Local\Temp\exp.json", $payload, $utf8)
Write-Host "[采集] $Submitter 提交 [$Type/$Section] $Title"
cmd /c "cd /d C:\Users\冯兴龙\AppData\Local\Temp && lark-cli base +record-upsert --base-token $BASE --table-id $T19 --json @./exp.json --jq .data.record.id"
Write-Host ""
Write-Host "Done. 已入库待审批。下一步走 experience-approval.ps1。"
