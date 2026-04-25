# MQ 操作技能

通过自然语言直接操作 Kafka、RabbitMQ、RocketMQ，推荐用 `/mq` 显式调用。

## 使用方法

```
/mq 连接本地 Kafka
/mq 查看所有 topic
/mq 看看订单队列的堆积情况
/mq 查一下 user-topic 的消费组
/mq 查看 user-queue 的前 3 条消息
/mq 切换到生产环境
```

## 能做什么

| 场景 | 示例 |
|------|------|
| 连接配置 | `/mq 连接本地 Kafka`、`/mq 切换到生产环境` |
| 查看主题 | `/mq 查看所有 topic`、`/mq 有哪些队列` |
| 消费组 | `/mq 查 user-topic 的消费组`、`/mq 看看谁在消费` |
| 堆积查询 | `/mq 订单队列堆积多少`、`/mq 查 user-topic 的 lag` |
| 消息查看 | `/mq 看看 user-queue 的前 5 条消息` |
| 集群信息 | `/mq 查看 Kafka 集群信息`、`/mq 查看 RocketMQ 集群` |

## 首次使用

首次执行时会自动引导配置 MQ 连接信息，配置文件保存在 `~/.config/mq/config.json`，支持多环境切换。

```json
{
  "current": "local",
  "local": {
    "type": "kafka",
    "bootstrap_servers": "localhost:9092"
  },
  "test": {
    "type": "rocketmq",
    "nameserver": "localhost:9876",
    "access_key": "",
    "secret_key": "",
    "group_id": ""
  }
}
```

支持 Kafka、RabbitMQ、RocketMQ 三种类型：
- **Kafka** / **RabbitMQ**：自动安装对应 Python 驱动
- **RocketMQ**：通过 Remoting 协议直连 NameServer/Broker，无需额外 SDK
