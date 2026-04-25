---
name: nacos
description: Nacos 服务注册与发现、配置中心操作工具。支持查看服务列表、服务详情、实例状态，以及配置列表、配置内容、配置历史等。触发词：Nacos、服务发现、配置中心、注册中心、微服务治理
---

# Nacos 操作

通过 `nacos_cli.py` 脚本直接操作 Nacos 服务注册与发现和配置中心。

## 快速使用

**脚本路径**：`<SKILL目录>/scripts/nacos_cli.py`

```bash
# 交互式配置
python3 <SKILL目录>/scripts/nacos_cli.py --init

# 查看命名空间
python3 <SKILL目录>/scripts/nacos_cli.py --namespaces

# 查看服务列表
python3 <SKILL目录>/scripts/nacos_cli.py --services

# 查看服务详情
python3 <SKILL目录>/scripts/nacos_cli.py --service order-service

# 查看服务实例
python3 <SKILL目录>/scripts/nacos_cli.py --instances order-service

# 查看配置列表
python3 <SKILL目录>/scripts/nacos_cli.py --configs

# 查看配置详情
python3 <SKILL目录>/scripts/nacos_cli.py --config-item app.yaml

# 查看配置历史
python3 <SKILL目录>/scripts/nacos_cli.py --history app.yaml

# 切换环境
python3 <SKILL目录>/scripts/nacos_cli.py --env prod --services

# JSON 输出
python3 <SKILL目录>/scripts/nacos_cli.py -j --services
```

> **注意**：`<SKILL目录>` 会被自动替换为当前技能的实际路径

> 详细参数说明见下方 [参数说明](#nacos_cli-参数说明)

## 核心操作

### 服务注册与发现

```bash
# 查看命名空间列表
python3 <SKILL目录>/scripts/nacos_cli.py --namespaces

# 查看所有服务
python3 <SKILL目录>/scripts/nacos_cli.py --services

# 分页查看
python3 <SKILL目录>/scripts/nacos_cli.py --services --page 1 --page-size 20

# 查看指定服务详情
python3 <SKILL目录>/scripts/nacos_cli.py --service user-service

# 查看指定服务的实例列表
python3 <SKILL目录>/scripts/nacos_cli.py --instances user-service

# 指定分组查询
python3 <SKILL目录>/scripts/nacos_cli.py --instances user-service --group MY_GROUP
```

### 配置中心

```bash
# 查看配置列表
python3 <SKILL目录>/scripts/nacos_cli.py --configs

# 分页查看
python3 <SKILL目录>/scripts/nacos_cli.py --configs --page 1 --page-size 20

# 查看指定配置内容
python3 <SKILL目录>/scripts/nacos_cli.py --config-item app.yaml

# 指定分组
python3 <SKILL目录>/scripts/nacos_cli.py --config-item app.yaml --group MY_GROUP

# 查看配置历史版本
python3 <SKILL目录>/scripts/nacos_cli.py --history app.yaml
```

## 首次使用配置

首次执行命令时，如果检测到配置不存在，会自动启动交互式配置向导。

也可以手动运行配置命令：

```bash
python3 <SKILL目录>/scripts/nacos_cli.py --init
```

配置文件位置：`~/.config/nacos/config.json`（可通过 `AGENT_NACOS_CONFIG` 环境变量覆盖）

### 配置示例

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

配置字段说明：

| 字段 | 说明 | 示例 |
|------|------|------|
| `server_addr` | Nacos 服务器地址 | `localhost:8848`、`nacos.example.com:8848` |
| `namespace` | 命名空间 ID，空字符串表示 public | `dev`、`prod`、`` |
| `username` | 用户名（开启认证时填写） | `nacos` |
| `password` | 密码（开启认证时填写） | `nacos` |
| `group` | 默认分组 | `DEFAULT_GROUP` |

### 多环境配置

支持同时配置多个环境，通过 `--env` 切换：

```json
{
  "current": "local",
  "local": {
    "server_addr": "localhost:8848",
    "namespace": "",
    "username": "",
    "password": "",
    "group": "DEFAULT_GROUP"
  },
  "test": {
    "server_addr": "nacos.test.example.com:8848",
    "namespace": "test",
    "username": "nacos",
    "password": "nacos",
    "group": "DEFAULT_GROUP"
  }
}
```

切换环境：

```bash
python3 <SKILL目录>/scripts/nacos_cli.py --env test --services
```

## 自动错误处理

脚本会自动处理以下问题，无需手动操作：

| 问题 | 自动处理 |
|------|----------|
| `requests` 未安装 | 自动安装依赖 |
| 配置文件不存在 | 自动启动配置向导 |
| Nacos 连接失败 | 显示详细错误信息 |

**常见错误**：
- `HTTP 403` - 认证失败，检查用户名密码
- `HTTP 404` - 服务或配置不存在
- `ConnectionError` - 连接失败，检查 Nacos 服务地址和端口

## nacos_cli.py 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--init` | 初始化配置 | `--init` |
| `--env, -e` | Nacos 环境 | `--env prod` |
| `--config, -c` | 配置文件路径 | `--config /path/to/config.json` |
| `--json, -j` | JSON 格式输出 | `-j` |
| `--namespaces` | 查看命名空间列表 | `--namespaces` |
| `--services` | 查看服务列表 | `--services` |
| `--service` | 查看服务详情 | `--service order-service` |
| `--instances` | 查看服务实例 | `--instances order-service` |
| `--configs` | 查看配置列表 | `--configs` |
| `--config-item` | 查看配置详情 | `--config-item app.yaml` |
| `--history` | 查看配置历史 | `--history app.yaml` |
| `--group, -g` | 指定分组 | `--group MY_GROUP` |
| `--page` | 页码 | `--page 1` |
| `--page-size` | 每页数量 | `--page-size 20` |

## 执行规则（AI 必读）

### 强制预检查

**在执行 Nacos 操作前，必须遵循：**

1. **不确定服务名** → 先用 `--services` 查看服务列表
2. **不确定配置名** → 先用 `--configs` 查看配置列表
3. **不确定命名空间** → 先用 `--namespaces` 查看命名空间列表

### 查询流程建议

| 需求 | 推荐命令 |
|------|---------|
| 查看有哪些服务 | `--services` |
| 查看服务运行状态 | `--instances <service>` |
| 查看有哪些配置 | `--configs` |
| 查看配置内容 | `--config-item <dataId>` |
| 查看配置变更历史 | `--history <dataId>` |

### 安全注意事项

- 生产环境操作前确认环境是否正确（`--env`）
- 查看配置内容时注意敏感信息（密码、密钥等）不要泄露

### 执行前自检清单

- [ ] Nacos 地址是否正确？
- [ ] 环境是否正确？（不确定的话检查 `--env`）
- [ ] 服务名/配置名是否正确？（不确定的话先 `--services` / `--configs`）
- [ ] 生产环境操作是否谨慎？
