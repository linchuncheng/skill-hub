---
name: skill-create
description: 引导用户创建符合规范的高质量新技能（Skill）。当用户请求「创建技能」「新建 Skill」「编写技能」或需要从零开始构建技能时使用。
---

# Skill Create - 技能创建助手

引导用户从零开始创建符合规范的高质量技能，一次性通过审查，避免后续反复修改。

## 技能工作流

调用 `todo_write` 工具创建待办任务：

需求收集 → 结构设计 → 内容生成 → 语义树优化 → 脚本创建 → 质量验证 → 完成交付

## 步骤 1：需求收集

### 1.1 了解技能功能

询问用户以下信息：

1. **技能名称**（英文，使用连字符，如 `skill-create`）
2. **技能描述**（能做什么 + 何时触发）
3. **核心功能**（主要完成什么任务）
4. **触发场景**（用户在什么情况下会使用这个技能）

### 1.2 确认技能类型

根据用户描述，判断技能类型：

| 类型 | 特征 | 示例 | 结构建议 |
|------|------|------|----------|
| 工具型 | 执行具体操作、处理文件 | `gitlab-ci`、`diagram` | 核心操作模式 + 常用命令 |
| 分析型 | 分析内容、生成报告 | `skill-check`、`resume-analyzer` | 简化工作流 |
| 创作型 | 生成内容、编写文档 | `ai-writer`、`coder-report` | 简化工作流 |
| 流程型 | 多步骤工作流 | `wiki-sop`、`ai-coding` | 完整工作流 |

## 步骤 2：结构设计

### 2.1 生成目录结构

根据需求收集结果，**主动判断**是否需要 scripts/、references/、assets/：

**判断是否需要 scripts/**：
- 技能包含数据处理、格式转换、文件操作 → 需要
- 操作步骤固定、容易出错 → 需要
- 需要高可靠性的确定性操作 → 需要

**判断是否需要 references/**：
- 有 API 文档、Schema、配置说明等查阅类内容 → 需要
- 工作流详解超过 200 行 → 需要（拆分到 references/）

**判断是否需要 assets/**：
- 有模板文件、图片、样板代码 → 需要

设计标准目录结构：

```text
skill-name/
├── manifest.json          # 必需：技能元数据
├── SKILL.md               # 必需：核心工作流（< 500 行）
├── scripts/               # 可选：可执行脚本（确定性操作）
│   └── example.py
├── references/            # 可选：参考文档（按需加载）
│   └── api_reference.md
└── assets/                # 可选：资源文件（输出中使用）
    └── template.md
```

### 2.2 目录使用说明

| 目录 | 使用场景 | 示例 |
|------|----------|------|
| `scripts/` | 确定性操作、反复执行的逻辑，优先用 Python 脚本 | `analyze.py`、`validate.py` |
| `references/` | 查阅类文档、API 规范、Schema | `api_reference.md`、`schema.md` |
| `assets/` | 模板、图片、样板代码 | `template.pptx`、`logo.png` |

**脚本化信号**（出现以下情况必须创建脚本）：
- 相同代码反复写
- LLM 多次推理相同逻辑
- 操作步骤固定、易出错
- 需要高可靠性

## 步骤 3：内容生成

### 3.1 生成 frontmatter

```yaml
---
name: {技能名称}
description: {功能描述}，当用户{触发场景}时触发。
---
```

**description 编写规范**：
- 包含「能做什么」+「何时触发」
- 不限定特定工具（避免「在 Qoder 中」「仅适用于 ClaudeCode」）
- 使用中性描述

### 3.2 根据技能类型生成不同结构

**先判断技能类型，再选择模板**：

#### 流程型技能模板（需要工作流）

适用：多步骤、固定顺序、执行时间长（如 wiki-sop、ai-coding）

```markdown
# 技能标题

简短介绍技能的核心功能。

## 技能工作流

调用 `todo_write` 工具创建待办任务：

步骤1 → 步骤2 → 步骤3 → 步骤4

### 步骤 1

步骤 1 详解（具体操作、参数、示例）

### 步骤 2

步骤 2 详解

……

## 使用说明

{清晰的使用方式，包含具体示例}
```

#### 工具型技能模板（不需要工作流）

适用：按需调用、单步操作、实时交互（如 agent-browser、git、find-skills）

```markdown
# 技能标题

简短介绍技能的核心功能。

## 核心操作模式

每个操作都遵循以下模式：
1. 准备环境
2. 执行操作
3. 验证结果

## 常用命令

| 命令 | 用途 |
|------|------|
| cmd1 | 场景1 |
| cmd2 | 场景2 |

## 常见模式

### 场景1：xxx

示例代码...

## 使用说明

{清晰的使用方式，包含具体示例}
```

#### 分析型技能模板（简化工作流）

适用：有诊断流程、但步骤灵活（如 skill-check、resume-analyzer）

```markdown
# 技能标题

简短介绍技能的核心功能。

## 分析流程

调用 `todo_write` 工具创建待办任务：

步骤1 → 步骤2 → 步骤3

### 步骤 1

步骤 1 详解

## 使用说明

{清晰的使用方式，包含具体示例}
```

**SKILL.md 编写原则**：
- 控制在 500 行以内
- 章节层级最多三级
- 使用具体路径、脚本名、工具名（避免模糊指代）
- 避免程度副词（可能、也许、适当、尽量、大约）
- 明确工作目录（使用相对路径时说明工作目录）

### 3.3 生成 manifest.json

```json
{
  "name": "{中文名称}",
  "description": "{简要描述}",
  "normalizedName": "{技能名称}",
  "category": "{分类}"
}
```

**分类参考**：工具、开发、文档、分析、创作、自动化

## 步骤 4：语义树优化

> 在生成内容后、创建脚本前，先优化文档结构，确保一次性通过 skill-check 审查

### 4.1 标注工作流步骤

为核心章节添加工作流步骤标注：

```markdown
# 优化前
## 审查检查清单
## 问题优先级定义
## 常见问题与解决方案

# 优化后
## 审查检查清单（步骤1-2:分析阶段）
## 问题优先级定义（步骤3:报告阶段）
## 常见问题与优化方案（步骤4:修复阶段）
```

### 4.2 优化标题语义

使用决策树、系统化命名替换模糊标题：

| 优化前 | 优化后 | 原因 |
|--------|--------|------|
| 解决方案 | 拆分决策树/脚本化决策树 | 强调决策逻辑 |
| 问题:xxx | xxx策略/xxx方案 | 去除冗余前缀 |
| 指南 | 决策树/操作指南 | 更精确 |
| 信号识别 | 问题识别/信号识别 | 区分场景 |

### 4.3 消除重复内容

检查并合并重复内容：

- [ ] 相同模板是否只出现一次？
- [ ] 示例是否有重复？
- [ ] 说明是否多处重复？
- [ ] 使用交叉引用替代重复内容

### 4.4 调整逻辑链条

确保每个章节遵循渐进式展开：

```markdown
# 标准结构
## xxx策略/方案（步骤N:阶段名）

**诊断**：问题描述

**识别信号**：如何发现问题

**优化方案**：具体操作步骤

**示例**：优化前后对比
```

## 步骤 5：脚本创建

### 5.1 判断是否需要脚本

如果技能包含以下特征，必须创建脚本：
- 确定性操作（每次执行相同步骤）
- 数据处理或格式转换
- 文件操作（读取、写入、移动）
- 验证或检查逻辑

### 5.2 生成 Python 脚本模板

使用 Python 脚本模板（详见 [references/skill-template.md](references/skill-template.md)）：

```python
#!/usr/bin/env python3
"""
{功能描述}

用法:
    python3 scripts/{script_name}.py <参数>

示例:
    python3 scripts/{script_name}.py input.txt
"""

import sys
from pathlib import Path


def main():
    # 参数校验
    if len(sys.argv) < 2:
        print("用法: python3 scripts/{script_name}.py <参数>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # 检查输入
    if not input_path.exists():
        print(f"❌ 错误: 文件不存在: {input_path}")
        sys.exit(1)
    
    # 核心逻辑
    # ...
    
    print("✅ 完成")


if __name__ == "__main__":
    main()
```

**脚本编写规范**：
- 包含参数校验和用法提示
- 包含错误处理（检查文件存在性）
- 输出友好提示（使用 ✅/❌ 等符号）
- 使用相对路径（基于 `__file__`）

## 步骤 6：质量验证

### 6.1 运行验证脚本

从 skill-create 技能目录执行验证（**不要将验证脚本复制到目标技能中**）：

```bash
# 找到 skill-create 技能目录
SKILL_CREATE_DIR="$(find ~/.qoder/skills -maxdepth 1 -name 'skill-create' -type d 2>/dev/null || find .qoder/skills -maxdepth 1 -name 'skill-create' -type d 2>/dev/null)"

# 执行验证
python3 "$SKILL_CREATE_DIR/scripts/validate-skill.py" <skill-dir>
```

**示例**：
```bash
python3 "$SKILL_CREATE_DIR/scripts/validate-skill.py" ./my-new-skill
```

### 6.2 检查清单

验证脚本会检查以下维度（详见 [references/skill-template.md](references/skill-template.md)）：

**结构性检查**：
- ✅ SKILL.md 行数 < 500
- ✅ frontmatter 包含 name 和 description
- ✅ name 与目录名一致
- ✅ description 包含功能和触发场景
- ✅ 目录结构完整（scripts/、references/、assets/ 按需创建）

**语义树检查**：
- ✅ 核心章节标注工作流步骤
- ✅ 标题使用决策树/系统化命名
- ✅ 无重复内容（模板、示例、说明）
- ✅ 逻辑链条完整（诊断→识别→方案→示例）
- ✅ 无冗余标题前缀（问题:xxx、示例:xxx）

**执行确定性检查**：
- ✅ 无模糊目录指代（XX目录、相关目录）
- ✅ 无模糊脚本引用（运行脚本、执行脚本）
- ✅ 无模糊工具指令（使用工具、调用工具）
- ✅ 无程度副词（可能、也许、适当、尽量）
- ✅ 工作目录明确

**Agent 兼容性检查**：
- ✅ 无工具名硬编码（Qoder、ClaudeCode、Cursor）
- ✅ description 不限定特定工具
- ✅ 无特定工具路径（.qoder/、.claude/）

**逻辑性检查**：
- ✅ 工作流完整（包含步骤详解）
- ✅ 使用说明清晰（包含示例）
- ✅ 错误处理覆盖常见场景
- ✅ 禁止事项明确

### 6.3 修复问题

根据验证报告，自动修复发现的问题：

| 问题类型 | 修复方案 |
|----------|----------|
| SKILL.md 过长 | 将详细内容移至 references/ |
| 模糊指代 | 替换为具体路径、脚本名、工具名 |
| 缺少脚本 | 创建 scripts/ 并生成脚本模板 |
| Agent 绑定 | 移除特定工具名和路径 |
| 工作流不完整 | 补充步骤详解章节 |
| 语义树问题 | 标注工作流步骤、优化标题、消除重复 |

### 6.4 循环验证

修复后再次运行验证（从 skill-create 技能目录执行），直到所有 P0/P1 问题通过：

```bash
python3 "$SKILL_CREATE_DIR/scripts/validate-skill.py" <skill-dir>
```

## 步骤 7：完成交付

### 7.1 输出技能摘要

向用户展示创建的技能摘要：

```markdown
# 技能创建完成：{skill-name}

## 结构概览

| 目录/文件 | 状态 | 说明 |
|-----------|------|------|
| manifest.json | ✅ | 元数据完整 |
| SKILL.md | ✅ | {行数} 行 |
| scripts/ | ✅ | {脚本数量} 个 |
| references/ | ✅ | {文档数量} 个 |
| assets/ | ✅ | {资源数量} 个 |

## 验证结果

所有检查项通过 ✅

## 使用方式

{简要说明如何使用这个技能}
```

### 7.2 提供后续建议

根据技能类型，提供优化建议：

| 技能类型 | 建议 |
|----------|------|
| 工具型 | 考虑添加更多错误处理场景 |
| 分析型 | 考虑添加参考文档说明分析标准 |
| 创作型 | 考虑添加模板文件到 assets/ |
| 流程型 | 考虑添加流程图或决策树到 references/ |

## 使用说明

### 快速创建

用户提供技能描述后，自动完成以下步骤：
1. 询问关键信息（名称、功能、触发场景）
2. 生成完整目录结构
3. 生成 SKILL.md、manifest.json
4. 按需创建脚本和参考文档
5. 运行质量验证
6. 输出最终结果

### 交互式创建

如果用户信息不完整，逐步引导：
1. 先问技能名称和核心功能
2. 再问触发场景
3. 判断是否需要脚本和参考文档
4. 最后确认并生成

### 从现有文档创建

如果用户提供文档或需求文档：
1. 提取核心功能和触发场景
2. 识别确定性操作（生成脚本）
3. 识别查阅类内容（生成 references/）
4. 识别资源文件（生成 assets/）
5. 按照规范生成完整技能

## 禁止事项

- ❌ 生成超过 500 行的 SKILL.md
- ❌ 使用模糊指代（合适的目录、相关脚本）
- ❌ 绑定特定 Agent 工具（Qoder、ClaudeCode）
- ❌ 遗漏 frontmatter 的 name 或 description
- ❌ name 字段与目录名不一致
- ❌ 将脚本移出 scripts/ 目录
- ❌ 将参考文档混入 SKILL.md 正文

## 参考资料

- 技能模板 → [references/skill-template.md](references/skill-template.md)
- 审查规范 → [../skill-check/SKILL.md](../skill-check/SKILL.md)
- 结构模式 → [../skill-check/references/structure-patterns.md](../skill-check/references/structure-patterns.md)
