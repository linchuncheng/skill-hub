# Redis 操作技能

通过自然语言直接操作 Redis，推荐用 `/redis` 显式调用。

## 使用方法

```
/redis 连接本地
/redis 查看所有键
/redis 查 mykey 的值
/redis 扫描 user 开头的键
/redis 分析所有 key 的设计是否合理
```

## 能做什么

| 场景 | 示例 |
|------|------|
| 连接配置 | `/redis 连接本地`、`/redis 切换到test环境` |
| 数据查询 | `/redis 查 mykey 的值`、`/redis 看看 user:1001` |
| 键扫描 | `/redis 扫描所有键`、`/redis 找 session 开头的键` |
| 批量操作 | `/redis 批量查 key1、key2、key3` |
| 设计分析 | `/redis 分析所有 key 设计是否合理` |
| 信息查看 | `/redis Redis 基本信息`、`/redis 查看内存使用情况` |

## 首次使用

首次执行时会自动引导配置 Redis 连接信息，配置文件保存在 `~/.config/redis/config.json`，支持多环境切换。
