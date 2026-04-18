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

### 1. 下载技能库

```bash
git clone https://gitee.com/your-username/skill-hub.git
cd skill-hub
```

### 2. 选择需要的技能

浏览本README上方的技能列表，找到你需要的技能目录，例如 `agent-browser/`、`dba/` 等。

### 3. 复制到你的AI工具

不同AI工具的技能目录位置不同，将技能文件夹复制到对应位置：

| AI工具 | 技能存放路径 |
|--------|-------------|
| **Claude Code** | `.claude/skills/<skill-name>/` (项目级别) 或 `~/.claude/skills/<skill-name>/` (全局) |
| **Cursor** | `.cursor/skills/<skill-name>/` (项目级别) 或 `~/.cursor/skills/<skill-name>/` (全局) |
| **Qoder** | `.qoder/skills/<skill-name>/` (项目级别) 或 `~/.qoder/skills/<skill-name>/` (全局) |
| **QoderWork** | `~/.qoderwork/skills/<skill-name>/` (全局) |
| **OpenClaw** | `~/.openclaw/skills/<skill-name>/` (全局) |

**示例：复制 dba 技能到 Qoder**

```bash
cp -r dba ~/.qoder/skills/dba
```

**示例：复制多个技能到 Cursor**

```bash
cp -r dba diagram project-boot ~/.cursor/skills/
```

### 4. 验证安装

重启你的AI工具，在对话中触发对应的技能即可使用。每个技能的 `SKILL.md` 文件中都定义了触发词和使用场景。

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