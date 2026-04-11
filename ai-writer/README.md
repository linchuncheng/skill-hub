# AI写作技能

微信公众号文章创作、改写与发布一体化流程。

## 功能特性

- ✍️ **创作模式**: 根据主题/观点自动生成文章，搜索最新素材
- 🔄 **改写模式**: 采集公众号文章，搜索补充内容，智能改写降重
- 🎨 **主题发布**: 8种wenyan内置主题，一键发布到公众号草稿箱
- 🖼️ **图片处理**: 自动下载微信图片，转换为本地路径
- 📊 **可视化编辑**: 本地Markdown编辑器，实时预览

## 快速开始

### 1. 安装依赖

```bash
# 安装 wenyan-cli（发布必需）
npm install -g @wenyan-md/cli
```

### 2. 配置微信公众号（可选，仅发布时需要）

创建配置文件 `~/.config/ai-writer/config.json`:

```json
{
  "wechat": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  },
  "publish": {
    "default_theme": "pie",
    "cover_size": {
      "width": 1080,
      "height": 864
    }
  }
}
```

> ⚠️ 需要在微信公众号后台添加服务器IP白名单

## 使用方式

### 创作模式

提供主题或观点，AI自动创作文章：

```
帮我写一篇关于AI编程工具的文章
围绕这3个观点写一篇文章：...
```

### 改写模式

提供公众号文章链接：

```
https://mp.weixin.qq.com/s/xxx
```

### 发布到公众号

```bash
# 使用默认主题（pie）发布
wenyan publish -f article.md

# 指定主题发布
wenyan publish -f article.md -t orangeheart
wenyan publish -f article.md -t lapis
```

## 主题系统

使用 wenyan 内置的 8 种主题：

| 主题ID | 名称 | 风格 |
|--------|------|------|
| pie | 前端之巅 | 现代锐利（默认）|
| default | 简约默认 | 简洁经典 |
| orangeheart | 橙心 | 暖橙色调 |
| rainbow | 彩虹 | 色彩活泼 |
| lapis | 全栈蓝 | 科技蓝 |
| maize | 柠檬黄 | 浅暖纸感 |
| purple | 优雅紫 | 柔和优雅 |
| phycat | 薄荷猫 | 薄荷清新 |

## 文章格式

Markdown 文件必须包含 frontmatter：

```markdown
---
title: 文章标题
cover: /Users/username/Documents/文章/images/封面图.jpg
digest: 可选摘要（不超过120字）
---

正文内容...
```

> ⚠️ 正文不要使用 `#` 一级标题，frontmatter 的 title 会作为文章标题

## 目录结构

```
ai-writer/
├── SKILL.md                 # 技能说明（AI执行指南）
├── manifest.json            # 技能清单
├── references/
│   ├── template.md          # 文章模板
│   └── rewrite-quality-checklist.md
├── scripts/
│   ├── download_images.py   # 图片下载脚本
│   ├── publisher/           # 发布脚本
│   ├── md-editor.html       # 可视化编辑器
│   ├── md-server.js         # 编辑器服务
│   └── md-server.sh         # 服务管理脚本
└── assets/                  # 参考文档
```

## 可视化编辑器

```bash
# 启动编辑器
./scripts/md-server.sh start

# 访问地址
http://localhost:3456

# 停止服务
./scripts/md-server.sh stop
```

## 常见问题

| 问题 | 解决 |
|------|------|
| wenyan 未安装 | `npm install -g @wenyan-md/cli` |
| 发布失败 40164 | 检查IP白名单 |
| 缺少封面图 | frontmatter 中添加 cover 字段 |
| 标题重复 | 删除正文中的 `#` 一级标题 |

## License

MIT
