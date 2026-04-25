# Agent浏览器 - 浏览器自动化技能

浏览器自动化工具，支持打开网站、填写表单、点击按钮、截图、抓取数据、测试 Web 应用、登录网站等任务。

## 功能特性

- 🌐 **网页导航**：打开网站、页面跳转、前进后退
- 📝 **表单自动化**：自动填写表单、选择下拉框、勾选复选框
- 🖱️ **交互操作**：点击按钮、滚动页面、键盘输入
- 📸 **截图捕获**：整页截图、元素截图、PDF 导出
- 🔐 **认证管理**：登录流程、状态持久化、会话复用
- 📊 **数据提取**：抓取页面文本、提取元素内容
- 🔄 **并行会话**：同时操作多个浏览器实例

## 快速开始

### 首次使用

```bash
# 安装浏览器（只需执行一次）
agent-browser install
```

### 基本用法

```bash
# 设置会话
export AGENT_BROWSER_SESSION=mysession

# 打开网页
agent-browser --headless open https://example.com

# 获取页面快照（获取元素引用）
agent-browser snapshot -i

# 交互操作
agent-browser click @e1
agent-browser fill @e2 "text"
```

## 运行模式

使用前会智能推荐最适合的模式：

| 模式 | 参数 | 适用场景 |
|------|------|----------|
| **代理模式** | `--headless` | 数据抓取、批量操作、自动化测试（推荐） |
| **可视化模式** | `--headed` | 调试脚本、教学演示、人工干预 |
| **CDP 连接** | `--cdp 9222` | 复用已有 Chrome 浏览器 |

## 典型场景

### 场景 1：数据抓取

```bash
export AGENT_BROWSER_SESSION=scrape
agent-browser --headless open https://example.com/products
agent-browser snapshot -i
agent-browser get text body > products.txt
```

### 场景 2：表单提交

```bash
export AGENT_BROWSER_SESSION=form
agent-browser --headless open https://example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @e3
```

### 场景 3：截图保存

```bash
agent-browser --headless open https://example.com
agent-browser screenshot --full page.png
```

## 注意事项

- ⚠️ 必须先 `snapshot -i` 才能使用元素引用（@e1、@e2 等）
- ⚠️ 每次页面导航后必须重新快照
- ⚠️ 使用完毕后执行 `agent-browser close` 清理会话

## 技术支持

遇到问题？查看完整文档：
- 命令参考 → [references/commands.md](references/commands.md)
- 故障排除 → [references/troubleshooting.md](references/troubleshooting.md)
- 认证管理 → [references/authentication.md](references/authentication.md)
