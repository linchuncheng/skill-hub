---
name: redis
description: Redis 操作工具。支持键值查询、字符串、哈希、列表、集合、有序集合等数据类型的增删改查，支持 Pipeline 批量操作、键扫描、TTL 管理。触发词：Redis、缓存查询、查键、查缓存、键值操作、缓存管理
---

# Redis 操作

通过 `redis_cli.py` 脚本直接执行 Redis 命令，支持所有 Redis 数据类型和常用操作。

## 快速使用

**脚本路径**：`<SKILL目录>/scripts/redis_cli.py`

```bash
# 查询字符串
python3 <SKILL目录>/scripts/redis_cli.py GET user:1001

# 查询哈希
python3 <SKILL目录>/scripts/redis_cli.py HGETALL user:1001

# 查询列表
python3 <SKILL目录>/scripts/redis_cli.py LRANGE mylist 0 -1

# 查询集合
python3 <SKILL目录>/scripts/redis_cli.py SMEMBERS myset

# 查询有序集合
python3 <SKILL目录>/scripts/redis_cli.py ZRANGE myzset 0 -1 WITHSCORES

# 检查键是否存在
python3 <SKILL目录>/scripts/redis_cli.py EXISTS user:1001

# 查看键的 TTL
python3 <SKILL目录>/scripts/redis_cli.py TTL user:1001

# 扫描键(安全方式,使用 SCAN)
python3 <SKILL目录>/scripts/redis_cli.py --scan "user:*"

# Pipeline 批量执行
python3 <SKILL目录>/scripts/redis_cli.py -p "GET key1" "HGETALL hash1" "LRANGE list1 0 -1"

# JSON 格式输出
python3 <SKILL目录>/scripts/redis_cli.py -j GET user:1001
```

> **注意**：`<SKILL目录>` 会被自动替换为当前技能的实际路径

> 详细参数说明见下方 [参数说明](#redis_cli-参数说明)

## 核心操作

### 字符串 (String)

```bash
# 获取值
python3 <SKILL目录>/scripts/redis_cli.py GET mykey

# 设置值
python3 <SKILL目录>/scripts/redis_cli.py SET mykey "hello"

# 删除键
python3 <SKILL目录>/scripts/redis_cli.py DEL mykey

# 自增
python3 <SKILL目录>/scripts/redis_cli.py INCR counter

# 设置过期时间(秒)
python3 <SKILL目录>/scripts/redis_cli.py EXPIRE mykey 3600
```

### 哈希 (Hash)

```bash
# 获取全部字段
python3 <SKILL目录>/scripts/redis_cli.py HGETALL user:1001

# 获取单个字段
python3 <SKILL目录>/scripts/redis_cli.py HGET user:1001 name

# 设置字段
python3 <SKILL目录>/scripts/redis_cli.py HSET user:1001 name "张三"

# 获取所有字段名
python3 <SKILL目录>/scripts/redis_cli.py HKEYS user:1001

# 删除字段
python3 <SKILL目录>/scripts/redis_cli.py HDEL user:1001 name
```

### 列表 (List)

```bash
# 获取列表全部元素
python3 <SKILL目录>/scripts/redis_cli.py LRANGE mylist 0 -1

# 左侧推入
python3 <SKILL目录>/scripts/redis_cli.py LPUSH mylist "item1"

# 右侧弹出
python3 <SKILL目录>/scripts/redis_cli.py RPOP mylist

# 获取列表长度
python3 <SKILL目录>/scripts/redis_cli.py LLEN mylist
```

### 集合 (Set)

```bash
# 获取全部成员
python3 <SKILL目录>/scripts/redis_cli.py SMEMBERS myset

# 添加成员
python3 <SKILL目录>/scripts/redis_cli.py SADD myset "member1"

# 判断成员是否存在
python3 <SKILL目录>/scripts/redis_cli.py SISMEMBER myset "member1"

# 删除成员
python3 <SKILL目录>/scripts/redis_cli.py SREM myset "member1"
```

### 有序集合 (Sorted Set)

```bash
# 获取全部成员(带分数)
python3 <SKILL目录>/scripts/redis_cli.py ZRANGE myzset 0 -1 WITHSCORES

# 添加成员
python3 <SKILL目录>/scripts/redis_cli.py ZADD myzset 100 "member1"

# 获取成员分数
python3 <SKILL目录>/scripts/redis_cli.py ZSCORE myzset "member1"

# 删除成员
python3 <SKILL目录>/scripts/redis_cli.py ZREM myzset "member1"
```

### 键扫描

```bash
# 扫描匹配 user:* 的键
python3 <SKILL目录>/scripts/redis_cli.py --scan "user:*"

# 扫描所有键(限制每次扫描数量)
python3 <SKILL目录>/scripts/redis_cli.py --scan "*" --count 50
```

> ⚠️ 使用 `--scan` 参数时底层使用 `SCAN` 命令,不会阻塞 Redis 实例,适合生产环境。

### Pipeline 批量操作

```bash
# 批量查询多个键
python3 <SKILL目录>/scripts/redis_cli.py -p \
  "GET user:1001" \
  "GET user:1002" \
  "HGETALL user:1003"
```

> Pipeline 模式将多条命令打包发送,减少网络往返,提升批量操作性能。

### Key 设计分析

```bash
# 分析所有 key 设计合理性
python3 <SKILL目录>/scripts/redis_cli.py --analyze

# 分析指定模式的 key
python3 <SKILL目录>/scripts/redis_cli.py --analyze --scan "user:*"

# JSON 格式输出分析报告
python3 <SKILL目录>/scripts/redis_cli.py --analyze -j
```

分析内容包括：
- 前缀分布统计
- 数据类型分布
- TTL 过期策略统计
- 内存占用分析
- 异常 key 检测（值大小偏离平均值 >50%）

## 首次使用配置

首次执行命令时,如果检测到配置不存在,会自动启动交互式配置向导。

也可以手动运行配置命令:

```bash
python3 <SKILL目录>/scripts/redis_cli.py --init
```

配置文件位置：`~/.config/redis/config.json`（可通过 `AGENT_REDIS_CONFIG` 环境变量覆盖）

### 配置示例

```json
{
  "current": "local",
  "local": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": ""
  }
}
```

## 自动错误处理

脚本会自动处理以下问题,无需手动操作:

| 问题 | 自动处理 |
|------|----------|
| `redis-py` 未安装 | 自动安装依赖 |
| 配置文件不存在 | 自动启动配置向导 |
| Redis 连接失败 | 显示详细错误信息 |
| 命令不存在 | 提示可用命令建议 |

**常见 Redis 错误**:
- `ConnectionError` - 连接失败,检查 Redis 服务是否启动
- `AuthenticationError` - 密码错误,检查配置文件中的密码
- `ResponseError` - 命令或参数错误,检查命令格式
- `TimeoutError` - 连接超时,检查网络或 Redis 负载

## redis_cli.py 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `command` | Redis 命令及参数 | `GET mykey`, `HGETALL myhash` |
| `--env, -e` | Redis 环境 | `--env prod` |
| `--config, -c` | 配置文件路径 | `--config /path/to/config.json` |
| `--json, -j` | JSON 格式输出 | `-j` |
| `--pipeline, -p` | Pipeline 批量模式 | `-p "GET k1" "GET k2"` |
| `--scan, -s` | 键扫描模式(使用 SCAN) | `--scan "user:*"` |
| `--count` | SCAN 每次扫描数量 | `--count 50` |
| `--init` | 初始化配置 | `--init` |
| `--analyze, -a` | 分析 key 设计合理性 | `--analyze` |

**使用示例**:

```bash
# 单条命令
python3 <SKILL目录>/scripts/redis_cli.py GET mykey

# Pipeline 批量执行
python3 <SKILL目录>/scripts/redis_cli.py -p "GET key1" "HGETALL hash1"

# 扫描键
python3 <SKILL目录>/scripts/redis_cli.py --scan "session:*"

# JSON 输出（方便程序处理）
python3 <SKILL目录>/scripts/redis_cli.py -j HGETALL user:1001
```

## 执行规则（AI 必读）

### 强制预检查

**在执行 Redis 命令前,必须遵循：**

1. **不确定键名** → 先用 `--scan "pattern:*"` 查找键
2. **不确定数据结构** → 先用 `TYPE key` 查看数据类型
3. **命令报错** → 根据错误信息调整,不要盲目重试

### 数据类型查询建议

| 数据类型 | 推荐查询命令 |
|---------|-------------|
| string | `GET key` |
| hash | `HGETALL key` 或 `HKEYS key` |
| list | `LRANGE key 0 -1` |
| set | `SMEMBERS key` |
| zset | `ZRANGE key 0 -1 WITHSCORES` |

> 💡 **查询流程建议**：先用 `TYPE key` 确认类型 → 再用对应命令查询数据

### 常见错误处理

| 错误信息 | 原因 | 解决方法 |
|---------|------|----------|
| `WRONGTYPE` | 命令与数据类型不匹配 | `TYPE key` 查看正确类型后使用对应命令 |
| `NOAUTH` | 未认证/密码错误 | 检查配置文件中的密码 |
| `OOM` | 内存不足 | 检查 Redis 内存使用情况 |

### 执行前自检清单

- [ ] 键名是否正确？（不确定的话 `--scan "pattern*"`）
- [ ] 数据类型是否确认？（`TYPE key`）
- [ ] 删除/修改操作是否确认？

**记住**：花 5 秒钟预检查,胜过花 5 分钟调试错误！
