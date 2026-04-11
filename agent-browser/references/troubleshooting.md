# 故障排除

常见问题诊断与解决方案。

**快速参考**：[SKILL.md](../SKILL.md#常见问题) 了解快速处理。

## 目录

- [故障排除](#故障排除)
  - [目录](#目录)
  - [Browser not launched](#browser-not-launched)
    - [原因 1：未指定会话](#原因-1未指定会话)
    - [原因 2：过期/僵尸会话（更常见）](#原因-2过期僵尸会话更常见)
  - [找不到浏览器二进制文件](#找不到浏览器二进制文件)
  - [引用失效](#引用失效)
  - [页面加载超时](#页面加载超时)
  - [元素未找到](#元素未找到)
  - [代理连接问题](#代理连接问题)
    - [代理连接失败](#代理连接失败)
    - [通过代理的 SSL/TLS 错误](#通过代理的-ssltls-错误)
    - [性能缓慢](#性能缓慢)
  - [MCP 替代方案](#mcp-替代方案)

## Browser not launched

**错误信息**：`"Browser not launched. Call launch first."`

### 原因 1：未指定会话

**解决方案**：

```bash
# 方式一：环境变量（推荐）
export AGENT_BROWSER_SESSION=mysession
agent-browser --headed open https://example.com

# 方式二：命令行参数
agent-browser --session mysession --headed open https://example.com
```

### 原因 2：过期/僵尸会话（更常见）

如果你已指定会话但仍遇到此错误，这是之前运行留下的过期会话：浏览器进程已终止但会话记录仍存在。

**诊断**：

```bash
# 检查现有会话
agent-browser session list
```

**解决方案**：

```bash
# 先关闭所有过期会话，然后打开
agent-browser close 2>/dev/null
agent-browser --session mysession close 2>/dev/null
sleep 1
agent-browser --session mysession --headed open https://example.com
```

**可靠的启动模式推荐**：

```bash
# 打开前始终关闭潜在的过期会话
agent-browser --session mysite close 2>/dev/null; sleep 1; agent-browser --session mysite --headed open https://example.com
```

## 找不到浏览器二进制文件

**症状**：执行 `agent-browser` 命令时报错找不到浏览器。

**解决方案**：

```bash
# 首次使用前必须安装浏览器
agent-browser install
```

这将下载并安装 Chromium 浏览器。只需执行一次。

## 引用失效

**症状**：`"Ref not found"` 错误

**原因**：页面变化后引用（@e1、@e2 等）会失效

**解决方案**：

```bash
# 导航或 DOM 变化后必须重新快照
agent-browser click @e5              # 导航到新页面
agent-browser snapshot -i            # 必须重新快照
agent-browser click @e1              # 使用新的引用
```

**引用失效的场景**：
- 点击链接或按钮导致导航
- 表单提交
- 动态内容加载（下拉菜单、模态框）

详见 [references/snapshot-refs.md](snapshot-refs.md)

## 页面加载超时

**症状**：页面长时间加载，命令卡住

**解决方案**：

```bash
# 设置超时时间
agent-browser wait --load networkidle --timeout 30000

# 或使用固定超时
agent-browser wait 10000  # 等待 10 秒
```

## 元素未找到

**症状**：快照中找不到预期的元素

**解决方案**：

```bash
# 1. 滚动页面
agent-browser scroll down 500
agent-browser snapshot -i

# 2. 等待动态内容加载
agent-browser wait 2000
agent-browser snapshot -i

# 3. 快照特定区域
agent-browser snapshot -s "#main-content"

# 4. 使用语义定位器（替代引用）
agent-browser find text "Sign In" click
agent-browser find role button click --name "Submit"
```

详见 [references/snapshot-refs.md](snapshot-refs.md#故障排除)

## 代理连接问题

### 代理连接失败

```bash
# 先测试代理连通性
curl -x http://proxy.example.com:8080 https://httpbin.org/ip

# 检查代理是否需要认证
export HTTP_PROXY="http://user:pass@proxy.example.com:8080"
```

### 通过代理的 SSL/TLS 错误

某些代理执行 SSL 检查。如果遇到证书错误：

```bash
# 仅用于测试 - 不推荐用于生产环境
agent-browser open https://example.com --ignore-https-errors
```

### 性能缓慢

```bash
# 仅在必要时使用代理
export NO_PROXY="*.cdn.com,*.static.com"  # 直接访问 CDN
```

详见 [references/proxy-support.md](proxy-support.md#故障排除)

## MCP 替代方案

如果 `agent-browser` CLI 遇到问题（安装问题、显示错误、兼容性问题），可以使用内置的浏览器 MCP 服务器。

**启用步骤**：

1. 打开 **设置** > **MCP 服务器**
2. 找到并启用 **Browser** MCP 服务器
3. 使用 MCP 浏览器工具（`mcp__browser-use__*`）替代 `agent-browser` CLI

**适用场景**：
- `agent-browser` CLI 未安装或有依赖问题
- 在 CLI 工具受限的环境中运行
- 用户偏好基于 MCP 的浏览器自动化
