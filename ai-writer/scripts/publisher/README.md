# 公众号发布模块

## 概述

复用 ai-writer 现有的 **styles.json 主题系统**(14 种 mdnice 风格主题),将 Markdown 文章发布到微信公众号草稿箱。

## 主题系统

### 14 种内置主题

所有主题定义在 `../styles.json` 中,与可视化编辑器共用同一套主题系统:

| 主题名称 | 适用场景 |
|---------|----------|
| 灵动蓝 | 科技、互联网、AI 相关文章 |
| 锤子便签 | 随笔、感悟、个人成长 |
| 科技蓝 | 技术教程、工具介绍 |
| 全栈蓝 | 全栈开发、架构设计 |
| 前端之巅同款 | 前端技术、Vue/React |
| 极简黑 | 极简风格、高级感 |
| 柠檬黄 | 轻松活泼、生活方式 |
| 橙心 | 温暖亲切、情感类 |
| 红绯 | 活力热情、营销推广 |
| 绿意 | 环保自然、健康生活 |
| 草原绿 | 清新自然、户外旅行 |
| 重影 | 艺术感、创意设计 |
| 雁栖湖 | 学术严肃、研究报告 |
| Obsidian | 知识管理、笔记风格 |

### 主题优势

与 wechat-toolkit 的 wenyan CSS 主题相比:
- ✅ **所见即所得**: 编辑器中预览的效果就是发布后的效果
- ✅ **HTML 内联样式**: 微信公众号完美兼容
- ✅ **14 种精心调校的主题**: 覆盖多种内容类型
- ✅ **零额外依赖**: 不需要学习新的主题系统

## 使用方法

### 1. 前置配置

```bash
# 安装 wenyan-cli
npm install -g @wenyan-md/cli

# 配置微信公众号凭证 (推荐,只需配置一次)
# 编辑 ~/.config/ai-writer/config.json
mkdir -p ~/.config/ai-writer
```

在 `~/.config/ai-writer/config.json` 中添加:
```json
{
  "wechat": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  }
}
```

**凭证读取优先级**:
1. `~/.config/ai-writer/config.json` (推荐)
2. 环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`
3. `~/.openclaw/workspace/TOOLS.md`

### 2. 准备 Markdown 文件

文件顶部**必须**包含 frontmatter:

```markdown
---
title: 文章标题(必填!)
cover: /Users/username/Documents/文章/images/封面图.jpg  # 封面图绝对路径(必填!)
digest: 这是一段可选的文字摘要,会显示在公众号文章列表中(选填,建议不超过120字)
---

# 正文内容...
```

**⚠️ 关键要求**:
- `title` 和 `cover` **缺一不可**
- `digest` **选填**,如果不填写,微信会自动提取正文前54个字作为摘要
- **所有图片路径必须使用绝对路径**
- 封面图建议尺寸: 1080×864 像素
- 摘要建议长度: 不超过 120 字

### 3. 查看可用主题

```bash
node publish.js --list
```

### 4. 发布文章

```bash
# 使用默认主题(灵动蓝)
node publish.js /path/to/article.md

# 指定主题
node publish.js /path/to/article.md 科技蓝
node publish.js /path/to/article.md 锤子便签
node publish.js /path/to/article.md 红绯
```

## 技术架构

### 与 wechat-toolkit 的对比

| 特性 | ai-writer (当前) | wechat-toolkit |
|------|------------------|----------------|
| 主题系统 | styles.json (HTML 内联样式) | wenyan CSS 主题 |
| 主题数量 | 14 种 | 12 种 bundled + 可安装 |
| 预览方式 | md-editor.html 实时预览 | 生成静态 HTML 预览 |
| 所见即所得 | ✅ 是 | ❌ 需要额外生成预览 |
| 依赖 | wenyan-cli | wenyan-cli + 主题文件 |
| 复杂度 | 低 | 中 |

### 发布流程

```
Markdown 文件
    ↓
解析 frontmatter (title + cover)
    ↓
验证图片路径(必须绝对路径)
    ↓
调用 wenyan-cli publish
    ↓
发布到微信公众号草稿箱
    ↓
返回草稿箱链接
```

## 故障排查

| 问题 | 解决方法 |
|------|----------|
| wenyan-cli 未安装 | `npm install -g @wenyan-md/cli` |
| 凭证未设置 | 写入 `~/.config/ai-writer/config.json` |
| 缺少 frontmatter | 添加 title 和 cover 字段 |
| IP 不在白名单 | `curl ifconfig.me` 获取 IP,添加到公众号后台 |
| 封面图路径错误 | 必须使用绝对路径 |
| 封面图尺寸错误 | 使用 1080×864 像素 |
| 40001 token 失效 | 检查 APP_ID 和 APP_SECRET 是否正确 |

## 扩展建议

未来可以考虑:
1. 自动将相对路径转为绝对路径
2. 集成生图 skill 自动生成封面图
3. 支持含视频文章发布(参考 wechat-toolkit 的 publish_with_video.js)
4. 主题自定义(允许用户添加新主题到 styles.json)
