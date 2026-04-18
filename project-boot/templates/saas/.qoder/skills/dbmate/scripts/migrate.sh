#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# dbmate 数据库迁移脚本（动态模块发现）
# ==========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 优先使用当前工作目录，如果当前目录包含 sql/ 目录
if [ -d "$(pwd)/sql" ]; then
  PROJECT_ROOT="$(pwd)"
else
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
fi
SQL_DIR="$PROJECT_ROOT/sql"

# 解析命令行参数
CONFIG_NAME=""
MODULE_FILTER=""
COMMAND="up"

usage() {
  echo "用法: $0 [选项]"
  echo ""
  echo "选项:"
  echo "  --config=<name>       配置文件名 (local/test/production)"
  echo "                        会自动读取 config.<name>.json"
  echo "  --module=<name>       指定模块 (如 dbmate_erp)"
  echo "  --command=<cmd>       执行命令 (up/down/status)"
  echo "                        默认: up"
  echo "  --help                显示帮助"
  echo ""
  echo "示例:"
  echo "  $0                          # 执行所有模块迁移，使用默认配置"
  echo "  $0 --config=local           # 使用 config.local.json"
  echo "  $0 --module=dbmate_erp      # 只迁移 erp 模块"
  echo "  $0 --command=status         # 查看迁移状态"
  exit 1
}

for arg in "$@"; do
  case $arg in
    --config=*)
      CONFIG_NAME="${arg#*=}"
      ;;
    --module=*)
      MODULE_FILTER="${arg#*=}"
      ;;
    --command=*)
      COMMAND="${arg#*=}"
      ;;
    --help)
      usage
      ;;
    *)
      echo "❌ 未知参数: $arg"
      usage
      ;;
  esac
done

# 检查并自动安装 dbmate
if ! command -v dbmate &> /dev/null; then
  echo "⚠️  未找到 dbmate，正在自动安装..."
  echo ""
  
  # 设置 Homebrew 镜像源（加速国内下载）
  export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
  export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
  export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
  export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
  
  echo "📦 正在安装 dbmate（使用国内镜像源）..."
  if command -v brew &> /dev/null; then
    brew install dbmate
  else
    echo "❌ 错误: 未找到 brew 命令"
    echo "请先安装 Homebrew: https://brew.sh"
    exit 1
  fi
  
  # 验证安装
  if ! command -v dbmate &> /dev/null; then
    echo "❌ 错误: dbmate 安装失败"
    exit 1
  fi
  
  echo "✅ dbmate 安装成功: $(dbmate --version)"
  echo ""
fi

# 检查 sql/ 目录
if [ ! -d "$SQL_DIR" ]; then
  echo "❌ 错误: 未找到 sql/ 目录"
  echo "当前目录: $PROJECT_ROOT"
  exit 1
fi

# ==========================================
# 1. 确定配置文件
# ==========================================

if [ -n "$CONFIG_NAME" ]; then
  CONFIG_FILE="$SQL_DIR/${CONFIG_NAME}.env"
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
  fi
else
  # 自动选择：优先使用 local.env
  if [ -f "$SQL_DIR/local.env" ]; then
    CONFIG_FILE="$SQL_DIR/local.env"
  elif [ -f "$SQL_DIR/.env" ]; then
    CONFIG_FILE="$SQL_DIR/.env"
  else
    echo "❌ 错误: 未找到配置文件"
    echo "可用配置:"
    ls -1 "$SQL_DIR"/*.env "$SQL_DIR"/.env 2>/dev/null || echo "  (无)"
    exit 1
  fi
fi

echo "📄 使用配置: $(basename "$CONFIG_FILE")"

# ==========================================
# 2. 读取数据库配置
# ==========================================

# 从 .env 文件读取 DATABASE_URL
source_env_file() {
  local file="$1"
  # 读取并导出 DATABASE_URL
  eval "$(grep -E '^DATABASE_URL=' "$file")"
}

source_env_file "$CONFIG_FILE"

# 环境变量覆盖（可选）
DBMATE_URL="${DATABASE_URL:-$DBMATE_URL}"

if [ -z "$DBMATE_URL" ]; then
  echo "❌ 错误: 未找到 DATABASE_URL"
  echo "请检查配置文件: $CONFIG_FILE"
  exit 1
fi

# ==========================================
# 3. 动态读取模块列表
# ==========================================

if [ -n "$MODULE_FILTER" ]; then
  MODULES="$MODULE_FILTER"
  if [ ! -d "$SQL_DIR/$MODULES" ]; then
    echo "❌ 错误: 模块目录不存在: $SQL_DIR/$MODULES"
    exit 1
  fi
else
  MODULES=$(find "$SQL_DIR" -mindepth 1 -maxdepth 1 -type d -not -name '.*' | xargs -I{} basename {})
fi

if [ -z "$MODULES" ]; then
  echo "❌ 错误: 未找到任何模块"
  echo "预期目录结构: sql/<module>/"
  exit 1
fi

echo "📦 检测到模块: $MODULES"
echo ""

# ==========================================
# 4. 执行迁移命令
# ==========================================

SUCCESS_COUNT=0
FAIL_COUNT=0

for MODULE in $MODULES; do
  SQL_PATH="$SQL_DIR/$MODULE"
  
  echo "=========================================="
  echo "▶ 模块: $MODULE"
  echo "   SQL目录: sql/$MODULE/"
  echo "   迁移表: $MODULE"
  echo "   命令: $COMMAND"
  echo "=========================================="
  
  # 检查是否有 SQL 文件（支持 dbmate 时间戳格式和 Flyway 格式）
  SQL_COUNT=$(find "$SQL_PATH" -name "*.sql" -type f | wc -l | tr -d ' ')
  if [ "$SQL_COUNT" -eq 0 ]; then
    echo "⚠️  警告: 没有找到 SQL 文件，跳过"
    echo ""
    continue
  fi
  
  echo "📝 找到 $SQL_COUNT 个 SQL 文件"
  echo ""
  
  # 执行 dbmate 命令
  export DATABASE_URL="$DBMATE_URL"
  
  if dbmate \
    --migrations-dir "$SQL_PATH" \
    --migrations-table "$MODULE" \
    --schema-file /dev/null \
    "$COMMAND"; then
    echo "✅ $MODULE 迁移成功"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "❌ $MODULE 迁移失败"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  
  echo ""
done

# ==========================================
# 5. 输出汇总
# ==========================================

echo "=========================================="
echo "📊 迁移汇总"
echo "=========================================="
echo "成功: $SUCCESS_COUNT 个模块"
echo "失败: $FAIL_COUNT 个模块"
echo ""

if [ $FAIL_COUNT -gt 0 ]; then
  echo "❌ 部分模块迁移失败，请检查上方错误信息"
  exit 1
else
  echo "✅ 所有模块迁移完成"
fi
