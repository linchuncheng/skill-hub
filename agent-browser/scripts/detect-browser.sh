#!/bin/bash
# 检测 Chrome 是否已在 CDP 端口监听
# 用法：./scripts/detect-browser.sh [端口号]
# 返回：
#   - cdp:<port>  如果 Chrome 已在监听（退出码 0）
#   - headless    如果未检测到 Chrome（退出码 1）

CDP_PORT="${1:-9222}"

if curl -s http://localhost:${CDP_PORT}/json/version > /dev/null 2>&1; then
    echo "cdp:${CDP_PORT}"
    exit 0
else
    echo "headless"
    exit 1
fi
