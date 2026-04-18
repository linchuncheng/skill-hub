# AI 写作助手

公众号文章创作、改写、排版与发布一体化流程。

## 核心功能

- ✍️ **创作模式**: 根据主题自动生成文章
- 🔄 **改写模式**: 采集文章智能改写降重
- 🎨 **主题排版**: 6 种精美主题一键排版
- 📤 **发布草稿**: 自动发布到公众号草稿箱

## 快速开始

### 1. 配置公众号

创建 `~/.config/ai-writer/config.json`:

```json
{
  "wechat": {
    "app_id": "你的app_id",
    "app_secret": "你的app_secret"
  },
  "publish": {
    "default_theme": "default"
  }
}
```

### 2. 初始化

```bash
python3 ai-writer/scripts/publish.py --init
```

### 3. 发布文章

```bash
# 使用默认主题
python3 ai-writer/scripts/publish.py article.md

# 指定主题
python3 ai-writer/scripts/publish.py article.md orangesun
```

## 可用主题

| 主题 | 说明 |
|------|------|
| default | 简约默认 |
| orangesun | 橙光 |
| redruby | 红宝石 |
| greenmint | 薄荷绿 |
| purplerain | 紫雨 |
| blackink | 墨黑 |

## 文章格式

Markdown 文件必须包含 frontmatter:

```markdown
---
title: 文章标题
cover: 封面图URL或本地路径
---

正文内容...
```

## 注意事项

- 封面图建议使用公众号已有图片链接
- 国外图床(picsum等)可能下载失败
- 草稿创建成功后需手动在公众号后台发布