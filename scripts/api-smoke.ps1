param(
    [string]$BaseUrl = 'http://localhost:18080'
)

# API 冒烟测试：需要应用已启动（推荐 test 环境 + 18080 端口）。
# 用法：
#   powershell -ExecutionPolicy Bypass -File scripts/api-smoke.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/api-smoke.ps1 -BaseUrl http://localhost:8080
#
# 覆盖：登录 → 列表 → 新增 → 详情 → 批量改状态 → 删除 → 404 → 参数校验 → 注入拦截 → 未登录 401 → 异步审计。

$ErrorActionPreference = 'Stop'
$cookieFile = Join-Path ([System.IO.Path]::GetTempPath()) ("taskmaster-cookie-{0}.txt" -f $PID)
$script:failed = 0

function Invoke-CurlJson {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Json = '',
        [switch]$Anonymous
    )

    $curlArgs = @('-s', '-X', $Method, "$BaseUrl$Path", '-w', "`n%{http_code}")
    if (-not $Anonymous) {
        $curlArgs += @('-b', $cookieFile)
    }

    $jsonFile = $null
    if ($Json) {
        # 通过临时文件传 JSON，避免 PowerShell 向原生 curl 传参时丢失引号
        $jsonFile = Join-Path ([System.IO.Path]::GetTempPath()) ("taskmaster-body-{0}.json" -f $PID)
        [System.IO.File]::WriteAllText($jsonFile, $Json, (New-Object System.Text.UTF8Encoding($false)))
        $curlArgs += @('-H', 'Content-Type: application/json', '--data-binary', "@$jsonFile")
    }

    try {
        $raw = (& curl.exe @curlArgs) -join "`n"
    }
    finally {
        if ($jsonFile -and (Test-Path $jsonFile)) {
            Remove-Item -Path $jsonFile -ErrorAction SilentlyContinue
        }
    }

    $splitAt = $raw.LastIndexOf("`n")
    if ($splitAt -lt 0) {
        throw "无法解析 curl 输出：$raw"
    }
    $bodyText = $raw.Substring(0, $splitAt).Trim()
    $status = [int]$raw.Substring($splitAt + 1).Trim()
    $body = if ($bodyText) { $bodyText | ConvertFrom-Json } else { $null }

    [pscustomobject]@{ Status = $status; Body = $body }
}

function Test-Step {
    param([string]$Name, [bool]$Ok, [string]$Detail = '')
    if ($Ok) {
        Write-Host "[PASS] $Name" -ForegroundColor Green
    }
    else {
        $script:failed++
        Write-Host "[FAIL] $Name  $Detail" -ForegroundColor Red
    }
}

Write-Host "== TaskMaster API 冒烟测试：$BaseUrl ==" -ForegroundColor Cyan

# 0. 登录（表单 POST，保存 JSESSIONID）
& curl.exe -s -o NUL -c $cookieFile -X POST "$BaseUrl/login" `
    -H 'Content-Type: application/x-www-form-urlencoded' `
    -d 'loginName=admin&loginPwd=123456'
$cookieText = if (Test-Path $cookieFile) { Get-Content -Raw $cookieFile } else { '' }
Test-Step '登录并保存 Session Cookie' ($cookieText -match 'JSESSIONID') '请确认 admin/123456 与端口'

# 1. 列表
$list = Invoke-CurlJson -Method GET -Path '/api/tasks?pageNum=1&pageSize=3'
Test-Step 'GET /api/tasks 返回 code=0' ($list.Status -eq 200 -and $list.Body.code -eq 0) "status=$($list.Status)"
Test-Step '分页字段完整（total/current/size/pages）' (
    $null -ne $list.Body.data -and
    $null -ne $list.Body.data.total -and
    $null -ne $list.Body.data.pages
) "data=$($list.Body.data | ConvertTo-Json -Compress -Depth 3)"

# 2. 新增
$createPayload = '{"title":"API 冒烟任务","content":"来自 api-smoke.ps1","status":1}'
$created = Invoke-CurlJson -Method POST -Path '/api/tasks' -Json $createPayload
Test-Step 'POST /api/tasks 返回 201 + 回填 id' (
    $created.Status -eq 201 -and $created.Body.code -eq 0 -and $created.Body.data.id -gt 0
) "status=$($created.Status)"
$id = $created.Body.data.id

# 3. 详情
$detail = Invoke-CurlJson -Method GET -Path "/api/tasks/$id"
Test-Step 'GET /api/tasks/{id} 返回刚创建的任务' (
    $detail.Status -eq 200 -and $detail.Body.data.title -eq 'API 冒烟任务'
) "status=$($detail.Status)"

# 4. 批量改状态
$batch = Invoke-CurlJson -Method PATCH -Path '/api/tasks/batch-status' `
    -Json ('{"ids":[' + $id + '],"status":2}')
Test-Step 'PATCH /api/tasks/batch-status 更新 1 条' (
    $batch.Status -eq 200 -and $batch.Body.code -eq 0 -and $batch.Body.data -eq 1
) "status=$($batch.Status), data=$($batch.Body.data)"

$after = Invoke-CurlJson -Method GET -Path "/api/tasks/$id"
Test-Step '批量更新后状态变为已完成' ($after.Body.data.status -eq 2) "status=$($after.Body.data.status)"

# 5. 删除 + 404
$deleted = Invoke-CurlJson -Method DELETE -Path "/api/tasks/$id"
Test-Step 'DELETE /api/tasks/{id} 删除成功' ($deleted.Status -eq 200 -and $deleted.Body.code -eq 0) "status=$($deleted.Status)"

$missing = Invoke-CurlJson -Method GET -Path "/api/tasks/$id"
Test-Step '查询已删除任务返回 404 + 40401' (
    $missing.Status -eq 404 -and $missing.Body.code -eq 40401
) "status=$($missing.Status), code=$($missing.Body.code)"

# 6. 参数校验
$invalid = Invoke-CurlJson -Method POST -Path '/api/tasks' -Json '{"title":"   ","status":9}'
Test-Step '空标题 / 非法状态返回 400 + 字段错误' (
    $invalid.Status -eq 400 -and $invalid.Body.code -eq 40001 -and
    $null -ne $invalid.Body.data.title -and $null -ne $invalid.Body.data.status
) "status=$($invalid.Status), data=$($invalid.Body.data | ConvertTo-Json -Compress)"

# 7. 注入拦截
$injection = Invoke-CurlJson -Method GET -Path '/api/tasks?sort=createTime%3BDROP%20TABLE%20t_task%3B--'
Test-Step 'ORDER BY 注入载荷被拦截（400）' (
    $injection.Status -eq 400 -and $injection.Body.code -eq 40001
) "status=$($injection.Status), message=$($injection.Body.message)"

$afterInjection = Invoke-CurlJson -Method GET -Path '/api/tasks?pageSize=1'
Test-Step '注入尝试后 t_task 仍可查询（表未被删除）' (
    $afterInjection.Status -eq 200 -and $afterInjection.Body.code -eq 0
) "status=$($afterInjection.Status)"

# 8. 未登录 401
$unauth = Invoke-CurlJson -Method GET -Path '/api/tasks' -Anonymous
Test-Step '未登录访问 /api/tasks 返回 401 + 40100' (
    $unauth.Status -eq 401 -and $unauth.Body.code -eq 40100
) "status=$($unauth.Status), code=$($unauth.Body.code)"

# 9. 异步审计（写操作后最多等 2 秒）
$audit = $null
$auditCount = 0
for ($i = 0; $i -lt 20; $i++) {
    $audit = Invoke-CurlJson -Method GET -Path '/api/audits?limit=20'
    $auditCount = if ($audit.Status -eq 200) { @($audit.Body.data).Count } else { 0 }
    if ($auditCount -gt 0) { break }
    Start-Sleep -Milliseconds 100
}
Test-Step 'GET /api/audits 能看到异步审计事件' (
    $audit.Status -eq 200 -and $auditCount -gt 0
) "count=$auditCount"
Test-Step '审计事件由 task-audit-* 线程写入' (
    @($audit.Body.data | Where-Object { $_.thread -like 'task-audit-*' }).Count -gt 0
) "threads=$((@($audit.Body.data) | Select-Object -ExpandProperty thread -Unique) -join ',')"

Remove-Item -Path $cookieFile -ErrorAction SilentlyContinue

if ($script:failed -gt 0) {
    Write-Host "`n$($script:failed) 项失败" -ForegroundColor Red
    exit 1
}
Write-Host "`n全部通过 ✅" -ForegroundColor Green
