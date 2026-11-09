param(
    [int]$Port = 18080,
    [switch]$SkipSmoke
)

# =====================================================================
# 本地一键验收：环境自检 → mvn clean test → 统计用例 → mvn package
#               → 启动 test 环境 → api-smoke 冒烟 → 汇总
#
# 用法（在仓库根目录执行）：
#   powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1 -SkipSmoke   # 只跑构建
#   powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1 -Port 18081  # 换端口（端口占用时）
#
# 说明：不依赖物理 MySQL —— test 环境走 H2 内存库，每次启动重建 7 条预置任务。
# 本脚本只在本机读写 target/ 下的构建产物，结束后自动关闭自己启动的进程。
# =====================================================================

# 注意：PowerShell 5.1 会把原生程序写到 stderr 的内容当成 ErrorRecord，
# 在 $ErrorActionPreference='Stop' 下会直接终止脚本（java -version / mvn 都会这样）。
# 因此这里用 'Continue'，靠 $LASTEXITCODE 判断成败并显式 throw。
$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$jar = Join-Path $repoRoot 'target/task-springboot.jar'
$appProc = $null
$reusedApp = $false
$exitCode = 0
$summary = [ordered]@{}

function Write-Step([string]$Text) {
    Write-Host ''
    Write-Host "==== $Text ====" -ForegroundColor Cyan
}

function Test-Ready([int]$P) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$P/login" -UseBasicParsing -TimeoutSec 2
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

try {
    # ------------------------------------------------------------------
    Write-Step '1/5 环境自检'
    # ------------------------------------------------------------------
    # java -version 写到 stderr；用 cmd 先把两个流合并，避免被当成 ErrorRecord
    $javaLine = (cmd /c 'java -version 2>&1' | Select-Object -First 1)
    $mvnLine = (cmd /c 'mvn -v 2>&1' | Select-Object -First 1)
    Write-Host "JDK : $javaLine"
    Write-Host "Maven: $mvnLine"
    if ($javaLine -notmatch '17') {
        Write-Host '[WARN] 当前 JDK 主版本不是 17，与 pom.xml / ci.yml 不一致，截图前请切换 JDK 17' -ForegroundColor Yellow
    }

    # ------------------------------------------------------------------
    Write-Step '2/5 质量门禁：mvn clean test（CI 的 Quality gate 同一条命令）'
    # ------------------------------------------------------------------
    & mvn -B -ntp clean test
    if ($LASTEXITCODE -ne 0) { throw 'mvn clean test 失败：测试未全绿，不要继续截图' }

    # ------------------------------------------------------------------
    Write-Step '3/5 统计测试用例（surefire 报告）'
    # ------------------------------------------------------------------
    $reports = Get-ChildItem -Path 'target/surefire-reports' -Filter '*.txt' -ErrorAction Stop
    $tests = 0; $failures = 0; $errors = 0; $skipped = 0
    foreach ($r in $reports) {
        $line = (Select-String -Path $r.FullName -Pattern 'Tests run:.*Failures' | Select-Object -First 1).Line
        if ($line -match 'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)') {
            $tests += [int]$Matches[1]; $failures += [int]$Matches[2]
            $errors += [int]$Matches[3]; $skipped += [int]$Matches[4]
        }
    }
    Write-Host ("测试类：{0} 个；用例：{1} 个；失败：{2}；错误：{3}；跳过：{4}" -f `
            $reports.Count, $tests, $failures, $errors, $skipped)
    $summary['测试类'] = $reports.Count
    $summary['用例总数'] = $tests
    if ($failures -gt 0 -or $errors -gt 0) { throw '存在失败用例，验收中止' }

    # ------------------------------------------------------------------
    Write-Step '4/5 构建产物：mvn package -DskipTests（CI 的 Build artifact 同一条命令）'
    # ------------------------------------------------------------------
    & mvn -B -ntp package -DskipTests
    if ($LASTEXITCODE -ne 0) { throw 'mvn package 失败' }
    if (-not (Test-Path $jar)) { throw "未找到可执行 JAR：$jar" }
    $jarMb = [math]::Round((Get-Item $jar).Length / 1MB, 2)
    Write-Host "产物：target/task-springboot.jar（$jarMb MB）"
    $summary['JAR'] = "$jarMb MB"

    if ($SkipSmoke) {
        Write-Host '[跳过] -SkipSmoke，未执行接口冒烟' -ForegroundColor Yellow
    }
    else {
        # --------------------------------------------------------------
        Write-Step "5/5 运行时验收：test 环境启动 + api-smoke（端口 $Port）"
        # --------------------------------------------------------------
        if (Test-Ready $Port) {
            $reusedApp = $true
            Write-Host "端口 $Port 上已有实例在响应 /login，直接复用（不重复启动）" -ForegroundColor Yellow
        } else {
            Write-Host "启动 java -jar target/task-springboot.jar --spring.profiles.active=test --server.port=$Port"
            # 用 .NET Process 而不是 Start-Process：部分机器上环境变量同时存在
            # HTTPS_PROXY / https_proxy 时，Start-Process 会因大小写不敏感的重复键直接报错。
            # 不重定向输出：应用日志与脚本输出同屏，截图时能一并看到 Profile 与端口。
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = 'java'
            $psi.Arguments = "-jar `"target/task-springboot.jar`" --spring.profiles.active=test --server.port=$Port"
            $psi.UseShellExecute = $false
            $psi.CreateNoWindow = $true
            $appProc = New-Object System.Diagnostics.Process
            $appProc.StartInfo = $psi
            $null = $appProc.Start()

            $deadline = (Get-Date).AddSeconds(60)
            while ((Get-Date) -lt $deadline) {
                if (Test-Ready $Port) { break }
                Start-Sleep -Milliseconds 500
            }
            if (-not (Test-Ready $Port)) {
                throw "应用 60 秒内未就绪：请确认端口 $Port 未被占用，或改 -Port 18081 重试"
            }
            Write-Host "应用已就绪：http://localhost:$Port  （账号 admin / 123456）" -ForegroundColor Green
        }

        & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'api-smoke.ps1') -BaseUrl "http://localhost:$Port"
        $smokeExit = $LASTEXITCODE
        $summary['接口冒烟'] = if ($smokeExit -eq 0) { '15/15 PASS' } else { '存在失败项' }
        if ($smokeExit -ne 0) { throw 'api-smoke 存在失败项，请按上面 [FAIL] 定位' }
    }
}
catch {
    Write-Host ''
    Write-Host "[失败] $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}
finally {
    if ($appProc -and -not $appProc.HasExited) {
        Write-Host "`n停止本次启动的应用进程（PID $($appProc.Id)）" -ForegroundColor DarkGray
        Stop-Process -Id $appProc.Id -Force -ErrorAction SilentlyContinue
    }
    if ($reusedApp) {
        Write-Host '复用了已有实例，脚本不负责关闭它（需要时请手动 Ctrl+C）' -ForegroundColor DarkGray
    }
}

if ($exitCode -ne 0) {
    Write-Host ''
    Write-Host '结论：本地验收未通过，先按上面的报错修复，再重新执行本脚本' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '================ 验收汇总 ================' -ForegroundColor Cyan
foreach ($k in $summary.Keys) {
    Write-Host ("{0,-8}: {1}" -f $k, $summary[$k])
}
Write-Host '结论：本地全绿，可进入 GitHub Actions 与 PR 环节' -ForegroundColor Green
exit 0
