#!/usr/bin/env bash
# 一键启动 Demo：构建可执行 JAR 并以 test 环境（H2 内存库）运行。
# 用法：
#   bash scripts/run-demo.sh
#   PORT=18081 SKIP_BUILD=1 bash scripts/run-demo.sh
#   PROFILE=dev bash scripts/run-demo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-18080}"
PROFILE="${PROFILE:-test}"

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
    echo "[1/2] mvn clean package ..."
    mvn -B -ntp clean package
fi

JAR="$ROOT/target/task-springboot.jar"
if [[ ! -f "$JAR" ]]; then
    echo "未找到 $JAR，请先执行 mvn clean package" >&2
    exit 1
fi

echo "[2/2] 启动 profile=$PROFILE，端口 $PORT"
echo "  访问地址：http://localhost:$PORT"
echo "  演示账号：admin / 123456"
exec java -jar "$JAR" "--spring.profiles.active=$PROFILE" "--server.port=$PORT"
