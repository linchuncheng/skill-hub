#!/bin/bash
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印信息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

SERVICE_LOG="$PROJECT_ROOT/logs/fengqun-scm-service.log"
if [ -f "$SERVICE_LOG" ]; then
    tail -f "$SERVICE_LOG"
else
    echo -e "${RED}日志文件不存在: $SERVICE_LOG${NC}"
fi
