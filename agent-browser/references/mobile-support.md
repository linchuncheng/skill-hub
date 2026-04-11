# 移动端支持

iOS 模拟器（移动 Safari）浏览器自动化。

**注意**：此功能需要 macOS 配合 Xcode，门槛较高，仅适用于特定场景。

## 目录

- [移动端支持](#移动端支持)
  - [目录](#目录)
  - [环境要求](#环境要求)
  - [基本用法](#基本用法)
  - [移动端专属操作](#移动端专属操作)
  - [真机测试](#真机测试)

## 环境要求

**必需软件**：
- macOS 系统
- Xcode（用于 iOS 模拟器）
- Appium：`npm install -g appium && appium driver install xcuitest`

## 基本用法

```bash
# 列出可用的 iOS 模拟器
agent-browser device list

# 在特定设备上启动 Safari
agent-browser -p ios --device "iPhone 16 Pro" open https://example.com

# 与桌面版相同的工作流程 - 快照、交互、重新快照
agent-browser -p ios snapshot -i
agent-browser -p ios tap @e1          # 点击（click 的别名）
agent-browser -p ios fill @e2 "text"
agent-browser -p ios swipe up         # 移动端专属手势

# 截图
agent-browser -p ios screenshot mobile.png

# 关闭会话（关闭模拟器）
agent-browser -p ios close
```

## 移动端专属操作

**手势操作**：

```bash
agent-browser -p ios swipe up         # 上滑
agent-browser -p ios swipe down       # 下滑
agent-browser -p ios swipe left       # 左滑
agent-browser -p ios swipe right      # 右滑
agent-browser -p ios tap @e1          # 点击（等同于 click）
agent-browser -p ios longpress @e1    # 长按
```

**设备模拟**：

```bash
# 使用不同设备
agent-browser -p ios --device "iPhone 15" open https://example.com
agent-browser -p ios --device "iPad Pro" open https://example.com
```

## 真机测试

如果预先配置好，可与实体 iOS 设备配合使用。

```bash
# 获取设备 UDID
xcrun xctrace list devices

# 使用 UDID 连接真机
agent-browser -p ios --device "<UDID>" open https://example.com
```

**注意**：真机测试需要额外的签名和配置，建议优先使用模拟器。
