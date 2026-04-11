# 浏览器模式

浏览器启动模式选择、CDP 连接复用、环境检测。

**快速参考**：[SKILL.md](../SKILL.md#浏览器模式) 了解快速用法。

## 目录

- [浏览器模式](#浏览器模式)
  - [目录](#目录)
  - [模式选择规则](#模式选择规则)
  - [CDP 连接复用](#cdp-连接复用)
    - [场景](#场景)
    - [方法一：通过 CDP 端口连接（推荐）](#方法一通过-cdp-端口连接推荐)
    - [方法二：使用 connect 命令](#方法二使用-connect-命令)
    - [注意事项](#注意事项)
  - [无头模式](#无头模式)
  - [有头模式](#有头模式)
  - [自动检测脚本](#自动检测脚本)
    - [detect-browser.sh](#detect-browsersh)
  - [虚拟机环境](#虚拟机环境)

## 模式选择规则

**优先级（从高到低）**：

1. **CDP 连接（最优先）**：检测到端口 9222 有 Chrome 监听时，自动使用 `--cdp 9222` 复用
2. **无头模式（默认）**：未检测到已有浏览器时，使用 `--headless`（性能更优，快 20-40%）
3. **有头模式（按需）**：用户明确要求"显示浏览器窗口"时使用 `--headed`
4. **虚拟机环境**：强制使用 `--headless`（无显示环境）

**模式说明**：
- `--cdp <port>`：复用已有浏览器实例（推荐，零启动开销）
- `--headless`：无头模式（默认，性能最优）
- `--headed`：有头模式（仅调试时使用，慢 20-40%）

## CDP 连接复用

### 场景

用户已手动打开 Chrome 浏览器，希望复用该实例而非打开新窗口。

### 方法一：通过 CDP 端口连接（推荐）

如果用户的 Chrome 已启用远程调试端口：

```bash
# 连接到已在端口 9222 上监听的 Chrome 实例
agent-browser --session mysession --cdp 9222 open https://example.com
agent-browser --session mysession snapshot -i
agent-browser --session mysession click @e1
```

**如何启动带 CDP 端口的 Chrome**（如果用户浏览器未启用调试端口）：

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**提示用户**：如果检测到端口 9222 未被占用，可以提示用户：
> "检测到您未启用 Chrome 远程调试。如需复用已有浏览器，请用以下命令重启 Chrome：
> `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222`"

### 方法二：使用 connect 命令

```bash
# 替代语法：先连接，后操作
agent-browser --session mysession connect 9222
agent-browser --session mysession open https://example.com
agent-browser --session mysession snapshot -i
```

### 注意事项

- 通过 CDP 连接时，**不要使用** `--headed` 或 `--headless` 标志
- CDP 连接复用现有浏览器状态（Cookie、标签页等）
- 连接结束后使用 `agent-browser close` 会断开连接，但不会关闭用户的浏览器

## 无头模式

**适用场景**：
- 服务器/CI 环境（无显示）
- 自动化脚本（性能优先）
- 批量任务（快 20-40%）

```bash
# 默认推荐
agent-browser --headless open https://example.com
```

## 有头模式

**适用场景**：
- 调试自动化脚本
- 用户要求"显示浏览器窗口"
- 需要视觉验证操作结果

```bash
# 仅调试时使用
agent-browser --headed open https://example.com
```

## 自动检测脚本

### detect-browser.sh

**位置**：`scripts/detect-browser.sh`

**功能**：检测 Chrome 是否已在 CDP 端口监听

**用法**：

```bash
# 检测端口 9222
MODE=$(./scripts/detect-browser.sh)
if [[ "$MODE" == cdp:* ]]; then
    # 复用已有浏览器
    agent-browser --cdp 9222 open https://example.com
else
    # 启动新浏览器
    agent-browser --headless open https://example.com
fi
```

**检测命令**（手动检查）：

```bash
# 检查端口 9222 是否被占用
lsof -i :9222 | grep LISTEN

# 或使用 curl 测试
curl -s http://localhost:9222/json/version > /dev/null 2>&1 && echo "Chrome 已启动" || echo "Chrome 未启动"
```

**示例：自动检测并连接**：

```bash
# 检测到已有 Chrome 时的用法
if curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
    # 复用已有浏览器
    agent-browser --session mysession --cdp 9222 open https://example.com
else
    # 启动新浏览器
    agent-browser --session mysession --headed open https://example.com
fi
agent-browser --session mysession snapshot -i
```

## 虚拟机环境

**检测指标**：
- 无显示的 Linux
- SSH 会话
- Docker 容器
- 云服务器

**处理方式**：强制使用 `--headless`

```bash
# 虚拟机环境下始终使用无头模式
agent-browser --headless open https://example.com
```

如果不确定环境，先尝试 `--headless`。
