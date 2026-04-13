---
name: agent-mysql
description: MySQL 数据库操作工具。支持数据查询、增删改、事务控制、表结构查看、SQL 执行、JSON 输出。触发词：MySQL、数据库查询、SQL 执行、查表、数据增删改、查看表结构、EXPLAIN 分析、数据库连接
---

# MySQL 数据库操作

通过 Python + pymysql 执行数据库操作。快速、简洁、无需安装 mysql CLI。

## 快速使用

```python
import pymysql

config = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'your_password', 'database': 'your_database',
    'charset': 'utf8mb4', 'cursorclass': pymysql.cursors.DictCursor
}

connection = pymysql.connect(**config)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users LIMIT 10;")
        results = cursor.fetchall()
        for row in results:
            print(row)
finally:
    connection.close()
```

> 完整示例参考：[scripts/examples.py](scripts/examples.py)  
> 详细操作参考：[references/operations.md](references/operations.md)

## 核心操作

### 查询数据

```python
cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
result = cursor.fetchone()
```

### 插入/更新/删除

```python
cursor.execute("INSERT INTO users (name) VALUES (%s);", ('张三',))
cursor.execute("UPDATE users SET status = %s WHERE id = %s;", ('active', 1))
cursor.execute("DELETE FROM users WHERE id = %s;", (1,))
connection.commit()
```

### 事务操作

```python
try:
    connection.begin()
    cursor.execute("...")
    connection.commit()
except Exception as e:
    connection.rollback()
```

### 查看表结构

```python
cursor.execute("""
    SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT 
    FROM information_schema.columns 
    WHERE table_schema = %s AND table_name = %s
""", (database, table))
```

> 更多操作 → [references/operations.md](references/operations.md)

## 连接配置

配置文件 `~/.config/agent-mysql/config.json`（可通过 `AGENT_MYSQL_CONFIG` 环境变量覆盖）：

```json
{
  "current": "local",
  "local": {"host": "localhost", "port": 3306, "user": "root", "password": "pwd", "database": "db"}
}
```

加载配置：

```python
import json, os

config_path = os.getenv('AGENT_MYSQL_CONFIG', os.path.expanduser('~/.config/agent-mysql/config.json'))
with open(config_path) as f:
    data = json.load(f)
config = {**data[data['current']], 'charset': 'utf8mb4', 'cursorclass': pymysql.cursors.DictCursor}
```

## 连接参数

pymysql.connect() 常用参数：

| Parameter | Description |
|-----------|-------------|
| `host` | 数据库主机地址（默认：localhost）|
| `port` | 端口号（默认：3306）|
| `user` | 用户名 |
| `password` | 密码 |
| `database` | 数据库名 |
| `charset` | 字符集（推荐：utf8mb4）|
| `cursorclass` | 游标类型（DictCursor 返回字典）|
| `connect_timeout` | 连接超时（秒）|
| `read_timeout` | 读取超时（秒）|
| `write_timeout` | 写入超时（秒）|

## 错误处理

| 异常 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'pymysql'` | pymysql 未安装 | 运行 `python3 scripts/mysql_helper.py --install` |
| `FileNotFoundError: config.json` | 配置文件不存在 | 运行 `python3 scripts/mysql_helper.py --init` 创建配置 |
| `OperationalError (1045)` | 密码错误 | 检查用户名/密码 |
| `OperationalError (1049)` | 数据库不存在 | 检查数据库名 |
| `OperationalError (2003)` | 连接失败 | 检查 MySQL 服务 |
| `ProgrammingError (1146)` | 表不存在 | 检查表名 |

**备选流程**：
- 遇到 `ModuleNotFoundError` → 引导用户运行 `python3 scripts/mysql_helper.py --install`
- 遇到配置文件不存在 → 引导用户运行 `python3 scripts/mysql_helper.py --init` 交互式创建
- 其他数据库错误 → 根据错误码对照表排查

## 数据库管理

```python
cursor.execute("CREATE DATABASE IF NOT EXISTS db CHARACTER SET utf8mb4;")
cursor.execute("SHOW DATABASES;")
cursor.execute("SHOW TABLES;")
```

## 安全建议

1. **禁止**在代码中硬编码密码，使用配置文件或环境变量
2. **使用**参数化查询防止 SQL 注入（`%s` 占位符）
3. 生产环境**建议**使用 SSL 连接（`ssl={'ca': 'path/to/ca.pem'}`）
4. 查询操作使用只读账号
5. **务必**使用 try-finally 确保连接关闭
