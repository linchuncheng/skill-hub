# Skill Hub

一个包含多种实用技能的集合库，每个技能都是独立的功能模块，可被AI助手调用以完成特定任务。

## 技能列表

| 技能名称 | 功能简介 |
|---------|---------|
| [agent-browser](agent-browser/) | 浏览器自动化工具，支持网页操作、数据抓取、截图、表单填写等自动化任务 |
| [dba](dba/) | 数据库操作工具，支持MySQL和PostgreSQL的数据查询、增删改、事务控制和SQL执行 |
| [dbmate](dbmate/) | 数据库迁移工具，支持多模块动态发现、环境配置管理、迁移和回滚操作 |
| [diagram](diagram/) | 绘制各种类型的动态SVG图，包括系统架构图、调用链路图、部署架构图、领域模型图等 |
| [project-boot](project-boot/) | 基于模板快速生成微服务项目脚手架，支持自动替换项目名、包名等关键信息 |
| [skill-analyze](skill-analyze/) | 分析SKILL执行过程，进行复盘优化与规则沉淀，帮助持续改进技能质量 |
| [skill-check](skill-check/) | 审查和优化现有技能（Skill）结构质量，检查规范性和完整性 |
| [skill-create](skill-create/) | 引导用户创建符合规范的高质量新技能，从零开始构建完整的技能模块 |

## 使用方式

每个技能目录包含：
- `SKILL.md` - 技能核心文档，包含工作流和使用说明
- `scripts/` - 可执行脚本（如需要）
- `references/` - 参考文档（如需要）
- `assets/` - 资源文件（如需要）
- `manifest.json` - 技能元数据（可选）

## 目录结构

```
skill-hub/
├── agent-browser/     # 浏览器自动化
├── dba/               # 数据库操作
├── dbmate/            # 数据库迁移
├── diagram/           # 技术图表绘制
├── project-boot/      # 项目脚手架生成
├── skill-analyze/     # 技能执行分析
├── skill-check/       # 技能质量审查
└── skill-create/      # 技能创建引导
```