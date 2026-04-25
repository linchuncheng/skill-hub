#!/bin/bash
#
# 一键启动脚本
# 用法: ./start.sh
#
# 该脚本会:
#   1. 检查 Docker 基础设施（MySQL、Redis、Nacos）
#   2. 停止旧服务，清理端口
#   3. 通过 mvn spring-boot:run 启动后端服务
#   4. 启动前端开发服务器
#

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

# 解析参数

for arg in "$@"; do
    case $arg in
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo -e "选项:"
            echo "  --help          显示帮助信息"
            echo ""
            echo "示例:"
            echo "  $0              # 构建并启动所有服务"
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $arg${NC}"
            echo "用法: $0"
            echo "可用选项: --help"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}一键启动${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# ============================================================================
# Step 0: 检查并启动 Docker 基础设施
# ============================================================================
echo -e "${BLUE}[Step 0] 检查 Docker 基础设施...${NC}"

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker 未运行，请先启动 Docker Desktop${NC}"
    exit 1
fi

# 检查 MySQL
if ! docker exec mysql mysqladmin ping -h localhost -u root -p123456 --silent 2>/dev/null; then
    log_warn "MySQL 未运行，正在启动基础设施..."
    docker-compose up -d mysql redis nacos
    log_info "等待 MySQL 就绪..."
    sleep 10
fi

# 检查 Redis
if ! docker exec redis redis-cli ping 2>/dev/null | grep -q PONG; then
    log_warn "Redis 未运行，正在启动..."
    docker-compose up -d redis
    sleep 3
fi

# 检查 Nacos
if ! curl -s http://localhost:8848/nacos/actuator/health | grep -q UP 2>/dev/null; then
    log_warn "Nacos 未运行，正在启动..."
    docker-compose up -d nacos
    log_info "等待 Nacos 就绪..."
    sleep 15
fi

# 检查数据库
DB_EXISTS=$(docker exec mysql mysql -u root -p123456 -sN -e "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'fengqun';" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" -eq 0 ]; then
    echo -e "${RED}✗ 数据库不存在，请先执行数据库迁移${NC}"
    echo -e "${YELLOW}  在 AI 对话中输入: /dbmate 升级${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 基础设施已就绪${NC}"
echo ""

# ============================================================================
# Step 1: 停止旧服务
# ============================================================================
echo -e "${BLUE}[Step 1] 清理旧服务...${NC}"

# 停止占用 8080 端口的进程
if lsof -i :8080 | grep LISTEN > /dev/null 2>&1; then
    PID_8080=$(lsof -ti:8080 -sTCP:LISTEN)
    if [ -n "$PID_8080" ]; then
        log_warn "发现占用 8080 端口的进程 (PID: $PID_8080)，正在停止..."
        kill -9 $PID_8080 2>/dev/null || true
        sleep 2
    fi
fi

# 停止占用 3000 端口的进程
if lsof -i :3000 | grep LISTEN > /dev/null 2>&1; then
    PID_3000=$(lsof -ti:3000 -sTCP:LISTEN)
    if [ -n "$PID_3000" ]; then
        log_warn "发现占用 3000 端口的进程 (PID: $PID_3000)，正在停止..."
        kill -9 $PID_3000 2>/dev/null || true
        sleep 1
    fi
fi

# 停止可能残留的 Java 进程
pkill -9 -f "spring-boot:run" 2>/dev/null || true
sleep 1

echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# ============================================================================
# Step 2: 启动后端服务
# ============================================================================
echo -e "${BLUE}[Step 2] 启动后端服务...${NC}"

# 确保日志目录存在
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p /tmp/fengqun-scm-tomcat
chmod 777 /tmp/fengqun-scm-tomcat 2>/dev/null || true

# 启动服务
SERVICE_LOG="$PROJECT_ROOT/logs/fengqun-scm-service.log"
cd "$PROJECT_ROOT/fengqun-scm-service"
nohup mvn spring-boot:run -Dmaven.test.skip=true > "$SERVICE_LOG" 2>&1 &
SERVICE_PID=$!
disown
cd "$PROJECT_ROOT"

# 等待服务启动
log_info "等待后端服务启动..."
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if lsof -i :8080 | grep LISTEN > /dev/null 2>&1; then
        log_info "✅ 后端服务启动成功 (PID: $(lsof -ti:8080 -sTCP:LISTEN))"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${RED}✗ 后端服务启动超时${NC}"
    echo -e "${YELLOW}查看日志: tail -n 50 $SERVICE_LOG${NC}"
    exit 1
fi
echo ""

# ============================================================================
# Step 3: 启动前端服务
# ============================================================================
echo -e "${BLUE}[Step 3] 启动前端服务...${NC}"

FRONTEND_PORT=3000
FRONTEND_PID=$(lsof -ti:$FRONTEND_PORT -sTCP:LISTEN 2>/dev/null | head -1)

if [ -n "$FRONTEND_PID" ]; then
    echo -e "${GREEN}  ✓ 前端服务已运行 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)${NC}"
else
    # 检查前端依赖
    if [ ! -d "$PROJECT_ROOT/fengqun-scm-admin/node_modules" ]; then
        log_info "安装前端依赖..."
        cd "$PROJECT_ROOT/fengqun-scm-admin"
        npm install
        cd "$PROJECT_ROOT"
    fi
    
    # 启动前端服务
    log_info "启动前端开发服务器..."
    cd "$PROJECT_ROOT/fengqun-scm-admin"
    nohup npm run dev > /tmp/vite-launch.log 2>&1 &
    VITE_PID=$!
    cd "$PROJECT_ROOT"
    
    # 等待前端启动
    log_info "等待前端服务启动..."
    for i in {1..15}; do
        sleep 1
        if lsof -ti:$FRONTEND_PORT -sTCP:LISTEN > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ 前端服务已启动 (PID: $VITE_PID, 端口: $FRONTEND_PORT)${NC}"
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${RED}  ✗ 前端服务启动超时，请查看日志: /tmp/vite-launch.log${NC}"
        fi
    done
fi

echo ""

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✓ 所有服务已启动！${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "访问地址:"
echo -e "  前端界面:   ${BLUE}http://localhost:3000${NC}"
echo -e "  后端服务:   ${BLUE}http://localhost:8080${NC}"
echo -e "  Nacos 控制台: ${BLUE}http://localhost:8848/nacos${NC}"
echo ""
echo -e "默认管理员账号:"
echo -e "  用户名: ${BLUE}super${NC}"
echo -e "  密码:   ${BLUE}123456${NC}"
echo ""
echo -e "查看日志:"
echo -e "  ${BLUE}sh logs.sh${NC}"
echo ""
echo -e "停止服务:"
echo -e "  ${BLUE}pkill -f spring-boot:run${NC}"
echo -e "  ${BLUE}pkill -f vite${NC}"