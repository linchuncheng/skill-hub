---
name: crud
description: 数据库CRUD操作工具。支持数据查询、增删改、事务控制、表结构查看、SQL 执行、JSON 输出。触发词：MySQL、数据库查询、SQL 执行、查表、数据增删改、查看表结构、EXPLAIN 分析、数据库连接
---

# 数据库CRUD操作

通过 `run_sql.py` 脚本直接执行 SQL。

## 快速使用

```bash
# 查询数据
python3 scripts/run_sql.py "SELECT * FROM users LIMIT 10;"

# 插入/更新/删除
python3 scripts/run_sql.py "INSERT INTO users (name) VALUES ('张三');"
python3 scripts/run_sql.py "UPDATE users SET status = 'active' WHERE id = 1;"
python3 scripts/run_sql.py "DELETE FROM users WHERE id = 1;"

# 事务操作（多条 SQL，全部成功才提交）
python3 scripts/run_sql.py -t \
  "INSERT INTO users (name) VALUES ('张三');" \
  "UPDATE accounts SET balance = balance - 100 WHERE id = 1;"

# JSON 格式输出
python3 scripts/run_sql.py -j "SELECT * FROM users;"
```

> 详细参数说明见下方 [参数说明](#run_sqlpy-参数说明)

## 核心操作

### 查询数据

```bash
python3 scripts/run_sql.py "SELECT * FROM users WHERE id = 1;"
python3 scripts/run_sql.py "SELECT COUNT(*) as total FROM orders;"
```

### 插入/更新/删除

```bash
python3 scripts/run_sql.py "INSERT INTO users (name, email) VALUES ('张三', 'zhangsan@example.com');"
python3 scripts/run_sql.py "UPDATE users SET status = 'active' WHERE id = 1;"
python3 scripts/run_sql.py "DELETE FROM users WHERE id = 1;"
```

### 事务操作

```bash
# 多条 SQL 在同一事务中执行，任一失败则全部回滚
python3 scripts/run_sql.py -t \
  "INSERT INTO users (name) VALUES ('张三');" \
  "UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;" \
  "UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;"
```

### 查看表结构

```bash
python3 scripts/run_sql.py "DESCRIBE users;"
python3 scripts/run_sql.py "SHOW CREATE TABLE users;"
```

## 首次使用配置

首次执行 SQL 时，如果检测到配置不存在，会自动启动交互式配置向导。

也可以手动运行配置命令：

```bash
python3 scripts/run_sql.py --init
```

配置文件位置：`~/.config/crud/config.json`（可通过 `AGENT_MYSQL_CONFIG` 环境变量覆盖）

```json
{
  "current": "local",
  "local": {"host": "localhost", "port": 3306, "user": "root", "password": "pwd", "database": "db"}
}
```

## 自动错误处理

脚本会自动处理以下问题，无需手动操作：

| 问题 | 自动处理 |
|------|----------|
| `pymysql` 未安装 | 自动安装依赖 |
| 配置文件不存在 | 自动启动配置向导 |
| 数据库连接失败 | 显示详细错误信息 |
| SQL 语法错误 | 回滚事务并提示 |

**常见数据库错误**：
- `OperationalError (1045)` - 密码错误，检查用户名/密码
- `OperationalError (1049)` - 数据库不存在，检查数据库名
- `OperationalError (2003)` - 连接失败，检查 MySQL 服务
- `ProgrammingError (1146)` - 表不存在，检查表名

## run_sql.py 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `sql` | 要执行的 SQL 语句（支持多条） | `"SELECT * FROM users;"` |
| `--file, -f` | SQL 文件路径 | `--file query.sql` |
| `--env, -e` | 数据库环境 | `--env dev` |
| `--config, -c` | 配置文件路径 | `--config /path/to/config.json` |
| `--max-rows, -m` | 最大返回行数 | `-m 100` |
| `--json, -j` | JSON 格式输出 | `-j` |
| `--transaction, -t` | **事务模式**（多条SQL在同一事务） | `-t "INSERT..." "UPDATE..."` |
| `--init` | **初始化配置**（交互式配置数据库） | `--init` |

**使用示例**：

```bash
# 单条查询
python3 scripts/run_sql.py "SELECT * FROM users LIMIT 10;"

# 多条 SQL（逐条执行，各自独立提交）
python3 scripts/run_sql.py "INSERT INTO..." "UPDATE..."

# 事务模式（全部成功才提交，任一失败则回滚）
python3 scripts/run_sql.py -t \
  "INSERT INTO users (name) VALUES ('张三');" \
  "UPDATE accounts SET balance = balance - 100 WHERE id = 1;"

# JSON 输出（方便程序处理）
python3 scripts/run_sql.py -j "SELECT * FROM users;"
```

## 数据库管理

```bash
# 查看所有数据库
python3 scripts/run_sql.py "SHOW DATABASES;"

# 查看当前数据库的表
python3 scripts/run_sql.py "SHOW TABLES;"

# 创建数据库
python3 scripts/run_sql.py "CREATE DATABASE IF NOT EXISTS mydb CHARACTER SET utf8mb4;"
```

## 安全建议

1. **禁止**在代码中硬编码密码，使用配置文件或环境变量
2. **使用**参数化查询防止 SQL 注入（拼接 SQL 时注意转义）
3. 生产环境**建议**使用只读账号执行查询
4. 修改操作建议使用事务，确保数据一致性