# Skill Create - 技能创建助手

引导用户从零创建符合规范的高质量技能，一次性通过审查。

## 功能特点

- 📋 智能需求收集（4 个关键问题）
- 🏗️ 自动结构设计（主动判断 scripts/references/assets）
- 📝 规范内容生成（SKILL.md + manifest.json）
- 🔧 脚本自动生成（标准 Python 模板）
- ✅ 内置质量验证（validate-skill.py）

## 使用场景

触发词："创建技能"、"新建 Skill"、"编写技能"

## 工作流程

需求收集 → 结构设计 → 内容生成 → 脚本创建 → 质量验证 → 完成交付

## 验证脚本

```bash
python3 scripts/validate-skill.py <skill-dir>
```

## 目录结构

```
skill-create/
├── SKILL.md                          # 核心工作流
├── manifest.json                     # 技能元数据
├── README.md                         # 本文件
├── scripts/validate-skill.py        # 质量验证脚本
└── references/skill-template.md     # 模板和检查清单
```

## 核心规范

- SKILL.md < 500 行，章节最多三级
- description 包含功能和触发场景
- 无模糊指代、无程度副词、无工具绑定
- 必须包含工作流、使用说明、错误处理、禁止事项

## 参考资料

- 技能模板 → [references/skill-template.md](references/skill-template.md)
- 审查规范 → [../skill-review/SKILL.md](../skill-review/SKILL.md)