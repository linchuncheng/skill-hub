---
name: agent-browser
description: 浏览器自动化工具。当用户需要打开网站、填写表单、点击按钮、截图、抓取数据、测试 Web 应用、登录网站或执行浏览器自动化任务时使用。
allowed-tools: Bash(agent-browser:*)
---

# 使用 agent-browser 进行浏览器自动化

## 首次设置（重要！）

在首次使用 `agent-browser` 之前，**必须**安装浏览器二进制文件：

```bash
agent-browser install
```

这将下载并安装 Chromium 浏览器。只需执行一次。

## 会话要求（关键！）

使用 `agent-browser` 时**必须指定会话名称**。不指定会话将触发以下错误：
> "Browser not launched. Call launch first."

有两种方式指定会话：

1. **环境变量**（推荐用于链式命令）：
```bash
export AGENT_BROWSER_SESSION=mysession
agent-browser --headed open https://example.com
agent-browser snapshot -i
agent-browser click @e1
```

2. **命令行参数**：
```bash
agent-browser --session mysession --headed open https://example.com
agent-browser --session mysession snapshot -i
agent-browser --session mysession click @e1
```

会话名称可以是任意字符串（例如 `taobao`、`google`、`test1`）。使用一致的会话名称可以在多个命令之间保持浏览器状态。

## 使用前确认

在首次使用 `agent-browser` 执行任务前，**必须**通过 `ask_user_question` 与用户确认运行模式，**并根据任务场景智能推荐**：

### 场景识别与推荐逻辑

**推荐使用代理模式（--headless）的场景**：
- 数据抓取/爬取任务
- 批量操作（批量截图、批量测试）
- 自动化测试脚本
- 后台监控任务
- 用户提到"快速"、"批量"、"自动"等关键词

**推荐使用可视化模式（--headed）的场景**：
- 调试自动化脚本
- 用户明确说"显示浏览器"、"让我看看"
- 需要人工干预的操作（如 2FA 验证码）
- 教学演示场景
- 用户提到"调试"、"看一下"、"演示"等关键词

**默认推荐**：如果无法判断场景，推荐代理模式（性能更优）

### 询问示例

```markdown
询问用户：
「检测到您需要[任务类型]，推荐使用[代理模式/可视化模式]：
- **代理模式（无头）**：后台运行，性能更优，速度快 20-40%
- **可视化模式（有头）**：显示浏览器窗口，便于观察操作过程

您希望使用哪种模式？」

选项：
1. [推荐模式]（推荐）→ 使用对应参数
2. [另一种模式] → 使用对应参数
```

**实际示例**：

**场景 1：数据抓取**
```
「检测到您需要抓取网页数据，推荐使用代理模式：
- 代理模式（无头）：后台运行，性能更优，速度快 20-40%
- 可视化模式（有头）：显示浏览器窗口，便于观察操作过程

您希望使用哪种模式？」
选项：
1. 代理模式（推荐）→ 使用 --headless
2. 可视化模式 → 使用 --headed
```

**场景 2：调试脚本**
```
「检测到您在调试自动化脚本，推荐使用可视化模式：
- 可视化模式（有头）：显示浏览器窗口，可以看到操作过程
- 代理模式（无头）：后台运行，性能更优

您希望使用哪种模式？」
选项：
1. 可视化模式（推荐）→ 使用 --headed
2. 代理模式 → 使用 --headless
```

**说明**：
- 代理模式（`--headless`）：浏览器在后台运行，不显示窗口，速度快 20-40%，适合大多数场景
- 可视化模式（`--headed`）：显示浏览器窗口，可以看到操作过程，适合调试和需要人工干预的场景

用户确认后，在整个会话中保持一致的模式选择。

## 浏览器模式

**模式选择**（根据用户确认）：

- **代理模式**（`--headless`）：后台运行，性能更优
- **可视化模式**（`--headed`）：显示窗口，便于调试
- **CDP 连接**：检测到端口 9222 有 Chrome 监听时，自动复用（最优先）

**快速用法**：

```bash
# 根据用户选择的模式执行
agent-browser --headless open https://example.com      # 代理模式
agent-browser --headed open https://example.com        # 可视化模式
agent-browser --cdp 9222 open https://example.com      # 复用已有浏览器（自动检测）
```

完整说明见 [references/browser-mode.md](references/browser-mode.md)

## 核心工作流程

每个浏览器自动化都遵循以下模式：

1. **设置会话**：`export AGENT_BROWSER_SESSION=mysite`
2. **检测并连接/启动**：运行 `scripts/detect-browser.sh` 自动检测
3. **导航**：根据检测结果使用 `--cdp` 或 `--headless`
4. **快照**：`agent-browser snapshot -i`（获取元素引用如 `@e1`、`@e2`）
5. **交互**：使用引用进行点击、填写、选择
6. **重新快照**：导航或 DOM 变化后，获取新的引用

```bash
# 设置会话
export AGENT_BROWSER_SESSION=mysite

# 自动检测：复用已有浏览器或启动新实例
MODE=$(./scripts/detect-browser.sh)
if [[ "$MODE" == cdp:* ]]; then
    agent-browser --cdp 9222 open https://example.com/form
else
    agent-browser --headless open https://example.com/form
fi

agent-browser snapshot -i
# 输出：@e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 检查结果
```

## 常用命令

**注意**：以下所有命令假设你已设置 `AGENT_BROWSER_SESSION` 或使用 `--session <name>`。

```bash
# 首次设置（运行一次）
agent-browser install                 # 安装 Chromium 浏览器

# 导航（自动检测已有浏览器）
# 使用 scripts/detect-browser.sh 检测，或直接指定模式
agent-browser --headless open <url>   # 无头模式（默认，推荐）
agent-browser --cdp 9222 open <url>   # 复用已有浏览器
agent-browser --headed open <url>     # 有头模式（仅调试时使用）
agent-browser close                   # 关闭浏览器

# 快照
agent-browser snapshot -i             # 交互式元素及引用（推荐）
agent-browser snapshot -s "#selector" # 限定在 CSS 选择器范围内

# 交互（使用快照中的 @refs）
agent-browser click @e1               # 点击元素
agent-browser fill @e2 "text"         # 清空并输入文本
agent-browser type @e2 "text"         # 直接输入（不清空）
agent-browser select @e1 "option"     # 选择下拉选项
agent-browser check @e1               # 勾选复选框
agent-browser press Enter             # 按键
agent-browser scroll down 500         # 滚动页面

# 获取信息
agent-browser get text @e1            # 获取元素文本
agent-browser get url                 # 获取当前 URL
agent-browser get title               # 获取页面标题

# 等待
agent-browser wait @e1                # 等待元素出现
agent-browser wait --load networkidle # 等待网络空闲
agent-browser wait --url "**/page"    # 等待 URL 匹配模式
agent-browser wait 2000               # 等待指定毫秒数

# 捕获
agent-browser screenshot              # 截图保存到临时目录
agent-browser screenshot --full       # 整页截图
agent-browser pdf output.pdf          # 保存为 PDF
```

## 常见模式

### 表单提交

```bash
export AGENT_BROWSER_SESSION=signup
agent-browser --headed open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### 带状态持久化的认证

```bash
# 登录一次并保存状态
export AGENT_BROWSER_SESSION=auth
agent-browser --headed open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 在后续会话中复用
agent-browser state load auth.json
agent-browser --headed open https://app.example.com/dashboard
```

### 数据提取

```bash
export AGENT_BROWSER_SESSION=scrape
agent-browser --headed open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5           # 获取特定元素文本
agent-browser get text body > page.txt  # 获取整个页面文本

# JSON 输出便于解析
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### 并行会话

```bash
agent-browser --headed --session site1 open https://site-a.com
agent-browser --headed --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

### 无头模式（仅在请求时使用）

```bash
# 仅在用户显式请求时使用无头模式
agent-browser --headless open https://example.com
```

### 调试工具

```bash
agent-browser --headed open https://example.com
agent-browser highlight @e1          # 高亮元素
agent-browser record start demo.webm # 录制会话
```

详见 [references/mobile-support.md](references/mobile-support.md) 了解 iOS 模拟器用法。

## 引用生命周期（重要）

引用（`@e1`、`@e2` 等）在页面变化时会失效。以下情况后**务必重新快照**：

- 点击链接或按钮导致导航
- 表单提交
- 动态内容加载（下拉菜单、模态框）

```bash
agent-browser click @e5              # 导航到新页面
agent-browser snapshot -i            # 必须重新快照
agent-browser click @e1              # 使用新的引用
```

## 语义定位器（引用的替代方案）

当引用不可用或不可靠时，使用语义定位器：

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```

## 深入文档

| 参考文档 | 使用场景 |
|-----------|-------------|
| [references/commands.md](references/commands.md) | 完整命令参考及所有选项 |
| [references/snapshot-refs.md](references/snapshot-refs.md) | 引用生命周期、失效规则、故障排除 |
| [references/session-management.md](references/session-management.md) | 并行会话、状态持久化、并发抓取 |
| [references/authentication.md](references/authentication.md) | 登录流程、OAuth、2FA 处理、状态复用 |
| [references/browser-mode.md](references/browser-mode.md) | 浏览器模式选择、CDP 连接、环境检测 |
| [references/troubleshooting.md](references/troubleshooting.md) | 常见问题诊断与解决方案 |
| [references/mobile-support.md](references/mobile-support.md) | iOS 模拟器、移动端自动化 |
| [references/video-recording.md](references/video-recording.md) | 录制工作流程用于调试和文档 |
| [references/proxy-support.md](references/proxy-support.md) | 代理配置、地理位置测试、轮换代理 |

## 即用模板脚本

| 脚本 | 描述 |
|----------|-------------|
| [scripts/form-automation.sh](scripts/form-automation.sh) | 带验证的表单填写 |
| [scripts/authenticated-session.sh](scripts/authenticated-session.sh) | 一次登录，状态复用 |
| [scripts/capture-workflow.sh](scripts/capture-workflow.sh) | 带截图的内容提取 |

```bash
./scripts/form-automation.sh https://example.com/form
./scripts/authenticated-session.sh https://app.example.com/login
./scripts/capture-workflow.sh https://example.com ./output
```

## 常见问题

**"Browser not launched"** → 详见 [references/troubleshooting.md](references/troubleshooting.md#browser-not-launched)

**找不到浏览器** → 运行 `agent-browser install`

**引用失效** → 详见 [references/snapshot-refs.md](references/snapshot-refs.md#引用生命周期)

**其他问题** → 完整故障排除指南见 [references/troubleshooting.md](references/troubleshooting.md)