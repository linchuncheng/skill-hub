# MySQL 操作参考

详细的数据库操作示例和说明。

## 查询数据

### 基础查询

```python
cursor.execute("SELECT * FROM users LIMIT 10;")
results = cursor.fetchall()

for row in results:
    print(row)
```

### JSON 输出

```python
import json

cursor.execute("SELECT * FROM users LIMIT 10;")
results = cursor.fetchall()
print(json.dumps(results, indent=2, ensure_ascii=False))
```

### 统计查询

```python
cursor.execute("SELECT COUNT(*) as total, SUM(amount) as revenue FROM orders WHERE DATE(create_time)=CURDATE();")
stats = cursor.fetchone()
print(stats)
```

### 参数化查询（防止 SQL 注入）

```python
# 单参数
cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
result = cursor.fetchone()

# 多参数
cursor.execute("SELECT * FROM users WHERE status = %s AND age > %s;", ('active', 18))
results = cursor.fetchall()
```

## 数据操作

### 插入数据

```python
cursor.execute(
    "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
    ('张三', 'zhangsan@example.com', 25)
)
connection.commit()
last_id = cursor.lastrowid
print(f"插入成功，ID: {last_id}")
```

### 更新数据

```python
cursor.execute("UPDATE users SET status = %s WHERE id = %s", ('active', 1))
connection.commit()
rows_affected = cursor.rowcount
print(f"更新了 {rows_affected} 条记录")
```

### 删除数据

```python
cursor.execute("DELETE FROM users WHERE id = %s", (1,))
connection.commit()
rows_affected = cursor.rowcount
print(f"删除了 {rows_affected} 条记录")
```

## 查看表结构

### 查看表字段信息

```python
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_COMMENT, IS_NULLABLE, COLUMN_KEY
    FROM information_schema.columns 
    WHERE table_schema = %s AND table_name = %s 
    ORDER BY ORDINAL_POSITION
""", ('your_database', 'users'))
columns = cursor.fetchall()

for col in columns:
    print(f"{col['COLUMN_NAME']}: {col['COLUMN_TYPE']} - {col['COLUMN_COMMENT']}")
```

### 查看建表语句

```python
cursor.execute("SHOW CREATE TABLE users;")
create_stmt = cursor.fetchone()
print(create_stmt['Create Table'])
```

### 查看索引

```python
cursor.execute("SHOW INDEX FROM users;")
indexes = cursor.fetchall()

for idx in indexes:
    print(f"索引: {idx['Key_name']}, 列: {idx['Column_name']}, 唯一: {idx['Non_unique'] == 0}")
```

## EXPLAIN 查询分析

### 基础 EXPLAIN

```python
cursor.execute("EXPLAIN SELECT * FROM users WHERE phone = %s", ('13800138000',))
explain_result = cursor.fetchall()

for row in explain_result:
    print(f"表: {row['table']}, 类型: {row['type']}, 行数: {row['rows']}, Extra: {row['Extra']}")
```

### EXPLAIN 关键字段说明

| 字段 | 说明 |
|------|------|
| type | 连接类型（const > ref > range > ALL），ALL 表示全表扫描需优化 |
| possible_keys | 可能使用的索引 |
| key | 实际使用的索引 |
| rows | 预计扫描行数（越小越好）|
| Extra | 额外信息（Using index=覆盖索引，Using filesort=需优化排序）|

## 事务操作

### 基础事务

```python
try:
    connection.begin()
    
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (%s, %s)", (1, 100.50))
    cursor.execute("UPDATE inventory SET stock = stock - 1 WHERE product_id = %s", (42,))
    
    connection.commit()
    print("事务提交成功")
except Exception as e:
    connection.rollback()
    print(f"事务回滚: {e}")
```

### 带保存点的事务

```python
try:
    connection.begin()
    
    cursor.execute("INSERT INTO users (name) VALUES (%s)", ('张三',))
    savepoint1 = cursor.lastrowid
    
    connection.cursor().execute("SAVEPOINT sp1")
    
    cursor.execute("INSERT INTO orders (user_id) VALUES (%s)", (savepoint1,))
    
    connection.commit()
except Exception as e:
    connection.rollback()
    print(f"事务失败: {e}")
```

## 批量执行 SQL 文件

```python
import re

def execute_sql_file(filepath, cursor):
    """执行 SQL 文件，处理注释"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除单行注释
    content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
    # 移除多行注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 分割并执行
    for statement in content.split(';'):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)

# 使用示例
with open('migrations/init.sql', 'r', encoding='utf-8') as f:
    execute_sql_file('migrations/init.sql', cursor)
    connection.commit()
```

## 数据库管理

### 创建数据库

```python
cursor.execute("CREATE DATABASE IF NOT EXISTS new_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
```

### 列出所有数据库

```python
cursor.execute("SHOW DATABASES;")
databases = cursor.fetchall()
for db in databases:
    print(db.values())
```

### 列出表

```python
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
for table in tables:
    print(table.values())
```

### 查看表大小

```python
cursor.execute("""
    SELECT
        table_name,
        table_rows,
        ROUND(data_length / 1024 / 1024, 2) AS 'data_size_mb',
        ROUND(index_length / 1024 / 1024, 2) AS 'index_size_mb'
    FROM information_schema.tables
    WHERE table_schema = %s
    ORDER BY (data_length + index_length) DESC
""", ('your_database',))

for table in cursor.fetchall():
    print(f"{table['table_name']}: {table['data_size_mb']} MB")
```

## 连接池（高级）

```python
from pymysql import connect

# 简单连接池示例
class ConnectionPool:
    def __init__(self, config, max_connections=5):
        self.config = config
        self.max_connections = max_connections
        self.connections = []
    
    def get_connection(self):
        if len(self.connections) < self.max_connections:
            conn = connect(**self.config)
            self.connections.append(conn)
            return conn
        return self.connections[0]
    
    def close_all(self):
        for conn in self.connections:
            conn.close()
        self.connections = []

# 使用示例
pool = ConnectionPool(config)
conn = pool.get_connection()
```
