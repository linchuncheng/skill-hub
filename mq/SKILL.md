---
name: mq
description: 消息队列操作工具。支持 Kafka、RabbitMQ、RocketMQ，支持查看主题/队列、消费组、消息堆积、消息采样等。触发词：MQ、消息队列、Kafka、RabbitMQ、RocketMQ、查堆积、查消费组、消息队列管理
---

# MQ 操作

通过 `mq_cli.py` 脚本直接操作 Kafka、RabbitMQ、RocketMQ，支持查看主题/队列、消费组、消息堆积、消息采样等。

## 快速使用

**脚本路径**：`<SKILL目录>/scripts/mq_cli.py`

```bash
# 交互式配置
python3 <SKILL目录>/scripts/mq_cli.py --init

# 查看所有 topic / queue
python3 <SKILL目录>/scripts/mq_cli.py --list

# 查看消费组
python3 <SKILL目录>/scripts/mq_cli.py --groups

# 查看堆积
python3 <SKILL目录>/scripts/mq_cli.py --lag order-topic
python3 <SKILL目录>/scripts/mq_cli.py --lag order-topic --group order-consumer

# 查看消息
python3 <SKILL目录>/scripts/mq_cli.py --peek order-topic
python3 <SKILL目录>/scripts/mq_cli.py --peek order-queue --count 10

# 查看集群信息
python3 <SKILL目录>/scripts/mq_cli.py --info

# 切换环境
python3 <SKILL目录>/scripts/mq_cli.py --env prod --list

# JSON 输出
python3 <SKILL目录>/scripts/mq_cli.py -j --list
```

> **注意**：`<SKILL目录>` 会被自动替换为当前技能的实际路径

> 详细参数说明见下方 [参数说明](#mq_cli-参数说明)

## 核心操作

### Kafka

```bash
# 列出所有 topic
python3 <SKILL目录>/scripts/mq_cli.py --list

# 列出所有消费组
python3 <SKILL目录>/scripts/mq_cli.py --groups

# 查看 topic 堆积（所有消费组）
python3 <SKILL目录>/scripts/mq_cli.py --lag user-topic

# 查看指定消费组堆积
python3 <SKILL目录>/scripts/mq_cli.py --lag user-topic --group user-consumer

# 查看消息
python3 <SKILL目录>/scripts/mq_cli.py --peek user-topic --count 5

# 查看集群 broker 信息
python3 <SKILL目录>/scripts/mq_cli.py --info
```

### RabbitMQ

```bash
# 列出所有 queue
python3 <SKILL目录>/scripts/mq_cli.py --list

# 列出所有 consumers
python3 <SKILL目录>/scripts/mq_cli.py --groups

# 查看 queue 堆积
python3 <SKILL目录>/scripts/mq_cli.py --lag order-queue

# 查看消息
python3 <SKILL目录>/scripts/mq_cli.py --peek order-queue --count 5

# 查看集群概览
python3 <SKILL目录>/scripts/mq_cli.py --info
```

### RocketMQ

通过 Remoting 协议直连 NameServer 和 Broker，无需额外 SDK。

```bash
# 列出所有 topic
python3 <SKILL目录>/scripts/mq_cli.py --list

# 列出所有消费组
python3 <SKILL目录>/scripts/mq_cli.py --groups

# 查看 topic 路由信息（broker、queue 数量）
python3 <SKILL目录>/scripts/mq_cli.py --lag order-topic

# 查看指定消费组堆积（逐 queue 的 max/consumer offset）
python3 <SKILL目录>/scripts/mq_cli.py --lag order-topic --group order-consumer

# 查看集群信息
python3 <SKILL目录>/scripts/mq_cli.py --info
```

## 首次使用配置

首次执行命令时，如果检测到配置不存在，会自动启动交互式配置向导。

也可以手动运行配置命令:

```bash
python3 <SKILL目录>/scripts/mq_cli.py --init
```

配置文件位置：`~/.config/mq/config.json`（可通过 `AGENT_MQ_CONFIG` 环境变量覆盖）

### 配置示例

**Kafka:**

```json
{
  "current": "local",
  "local": {
    "type": "kafka",
    "bootstrap_servers": "localhost:9092",
    "sasl_mechanism": "",
    "sasl_plain_username": "",
    "sasl_plain_password": "",
    "security_protocol": "PLAINTEXT"
  }
}
```

**RabbitMQ:**

```json
{
  "current": "local",
  "local": {
    "type": "rabbitmq",
    "host": "localhost",
    "port": 5672,
    "management_port": 15672,
    "username": "guest",
    "password": "guest",
    "vhost": "/"
  }
}
```

**RocketMQ:**

```json
{
  "current": "local",
  "local": {
    "type": "rocketmq",
    "nameserver": "localhost:9876",
    "access_key": "",
    "secret_key": "",
    "group_id": ""
  }
}
```

### 多环境配置

支持同时配置多个环境，通过 `--env` 切换：

```json
{
  "current": "local",
  "local": {
    "type": "kafka",
    "bootstrap_servers": "localhost:9092"
  },
  "prod": {
    "type": "kafka",
    "bootstrap_servers": "kafka.prod.example.com:9092",
    "sasl_mechanism": "PLAIN",
    "sasl_plain_username": "app",
    "sasl_plain_password": "secret",
    "security_protocol": "SASL_SSL"
  }
}
```

切换环境：

```bash
python3 <SKILL目录>/scripts/mq_cli.py --env prod --list
```

## 自动错误处理

脚本会自动处理以下问题，无需手动操作：

| 问题 | 自动处理 |
|------|----------|
| `kafka-python` / `requests` 未安装 | 自动安装依赖 |
| 配置文件不存在 | 自动启动配置向导 |
| MQ 连接失败 | 显示详细错误信息 |

**常见错误**:
- `ConnectionError` - 连接失败，检查服务地址和端口
- `AuthenticationError` - 认证失败，检查用户名密码
- `UnknownTopicOrPartitionError` - Topic 不存在

## mq_cli.py 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--init` | 初始化配置 | `--init` |
| `--env, -e` | MQ 环境 | `--env prod` |
| `--config, -c` | 配置文件路径 | `--config /path/to/config.json` |
| `--json, -j` | JSON 格式输出 | `-j` |
| `--list` | 列出 topics / queues | `--list` |
| `--groups` | 列出消费组 / consumers | `--groups` |
| `--lag` | 查看堆积 | `--lag order-topic` |
| `--group` | 指定消费组 | `--group order-consumer` |
| `--peek` | 查看消息 | `--peek order-topic` |
| `--count` | 查看消息数量 | `--count 10` |
| `--info` | 查看集群信息 | `--info` |

## 执行规则（AI 必读）

### 强制预检查

**在执行 MQ 操作前，必须遵循：**

1. **不确定 topic/queue 名** → 先用 `--list` 查看
2. **查询堆积** → 先用 `--lag` 查看整体情况，再用 `--group` 指定消费组
3. **查看消息** → 使用 `--peek` 采样，避免大量消费影响业务

### 查询流程建议

| 需求 | 推荐命令 |
|------|---------|
| 查看有哪些 topic/queue | `--list` |
| 查看堆积情况 | `--lag <name>` |
| 查看谁在消费 | `--groups` |
| 查看消息内容 | `--peek <name> --count 5` |

### 安全注意事项

- `--peek` 默认只采样 5 条消息，不会大量消费
- Kafka 的 `--peek` 使用独立 consumer，不会影响业务消费组
- RabbitMQ 的 `--peek` 使用 `ack_requeue_true` 模式，消息不会被消费

### 执行前自检清单

- [ ] topic/queue 名是否正确？（不确定的话 `--list`）
- [ ] 环境是否正确？（不确定的话 `--env`）
- [ ] 生产环境操作是否谨慎？
