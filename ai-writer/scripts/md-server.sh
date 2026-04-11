#!/bin/bash
# Markdown Editor Server 管理脚本
# 用法: ./md-server.sh [start|stop|restart|status|logs]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/md-server.pid"
PORT=3456

check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    # 检查是否有其他实例在运行
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "$PID" > "$PID_FILE"
        return 0
    fi
    return 1
}

start() {
    if check_running; then
        echo "✅ 服务已在运行 (PID: $(cat $PID_FILE))"
        echo "🌐 访问地址: http://localhost:$PORT"
        return 0
    fi
    
    echo "🚀 启动 Markdown Editor Server..."
    cd "$SCRIPT_DIR" || exit 1
    nohup node md-server.js > /tmp/md-server.log 2>&1 &
    PID=$!
    echo "$PID" > "$PID_FILE"
    
    # 等待服务启动
    sleep 2
    if check_running; then
        echo "✅ 服务已启动 (PID: $PID)"
        echo "🌐 访问地址: http://localhost:$PORT"
        echo "📋 日志文件: /tmp/md-server.log"
    else
        echo "❌ 启动失败，查看日志: /tmp/md-server.log"
        return 1
    fi
}

stop() {
    if ! check_running; then
        echo "ℹ️ 服务未在运行"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    echo "🛑 停止服务 (PID: $PID)..."
    kill "$PID" 2>/dev/null
    
    # 等待进程结束
    for i in {1..5}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # 强制结束如果还在运行
    if ps -p "$PID" > /dev/null 2>&1; then
        kill -9 "$PID" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    echo "✅ 服务已停止"
}

restart() {
    stop
    sleep 1
    start
}

status() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        echo "✅ 服务运行中 (PID: $PID)"
        echo "🌐 访问地址: http://localhost:$PORT"
        echo "📋 日志文件: /tmp/md-server.log"
    else
        echo "ℹ️ 服务未运行"
    fi
}

logs() {
    if [ -f "/tmp/md-server.log" ]; then
        tail -f "/tmp/md-server.log"
    else
        echo "ℹ️ 暂无日志文件"
    fi
}

# 主命令处理
case "${1:-start}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "用法: $0 [start|stop|restart|status|logs]"
        echo ""
        echo "命令说明:"
        echo "  start    启动服务 (默认)"
        echo "  stop     停止服务"
        echo "  restart  重启服务"
        echo "  status   查看状态"
        echo "  logs     查看日志"
        exit 1
        ;;
esac
