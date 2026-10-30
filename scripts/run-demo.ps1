param(
    [int]$Port = 18080,
    [ValidateSet('test', 'dev', 'prod')]
    [string]$SpringProfile = 'test',
    [switch]$SkipBuild
)

# 一键启动 Demo：构建可执行 JAR 并以 test 环境（H2 内存库）运行。
# 用法：
#   powershell -ExecutionPolicy Bypass -File scripts/run-demo.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/run-demo.ps1 -Port 18081 -SkipBuild
#   powershell -ExecutionPolicy Bypass -File scripts/run-demo.ps1 -SpringProfile dev

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not $SkipBuild) {
    Write-Host '[1/2] mvn clean package ...' -ForegroundColor Cyan
    mvn -B -ntp clean package
    if ($LASTEXITCODE -ne 0) {
        throw '构建失败：请先修复编译或测试错误'
    }
}

$jar = Join-Path $repoRoot 'target/task-springboot.jar'
if (-not (Test-Path $jar)) {
    throw "未找到 $jar，请先执行 mvn clean package，或去掉 -SkipBuild"
}

Write-Host "[2/2] 启动 profile=$SpringProfile，端口 $Port" -ForegroundColor Cyan
Write-Host "  访问地址：http://localhost:$Port" -ForegroundColor Green
Write-Host '  演示账号：admin / 123456' -ForegroundColor Green
Write-Host '  按 Ctrl+C 停止' -ForegroundColor DarkGray

java -jar $jar "--spring.profiles.active=$SpringProfile" "--server.port=$Port"
