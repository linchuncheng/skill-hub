# Nacos 操作技能

通过自然语言直接操作 Nacos 服务注册与发现、配置中心，推荐用 `/nacos` 显式调用。

## 使用方法

```
/nacos 连接本地 Nacos
/nacos 查看所有服务
/nacos 看看 order-service 的实例
/nacos 查一下 app.yaml 的配置内容
/nacos 查看配置历史
/nacos 切换到测试环境
```

## 能做什么

| 场景 | 示例 |
|------|------|
| 连接配置 | `/nacos 连接本地`、`/nacos 切换到测试环境` |
| 服务发现 | `/nacos 查看所有服务`、`/nacos 有哪些命名空间` |
| 服务详情 | `/nacos 看看 user-service 的详情` |
| 实例状态 | `/nacos 查 order-service 有哪些实例`、`/nacos 看看哪些服务不健康` |
| 配置管理 | `/nacos 查看所有配置`、`/nacos 查 app.yaml 的内容` |
| 配置历史 | `/nacos 看看 app.yaml 的历史版本` |

## 首次使用

首次执行时会自动引导配置 Nacos 连接信息，配置文件保存在 `~/.config/nacos/config.json`，支持多环境切换。

```json
{
  "current": "local",
  "local": {
    "server_addr": "localhost:8848",
    "namespace": "",
    "username": "",
    "password": "",
    "group": "DEFAULT_GROUP"
  }
}
```

支持多环境：
```
/nacos 切换到 test 环境
/nacos --env prod 查看所有服务
```
