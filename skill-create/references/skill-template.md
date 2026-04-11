# 技能模板与检查清单

本文档提供技能创建的详细模板和检查清单，确保每个技能都符合规范。

## SKILL.md 完整模板

```markdown
---
name: {技能名称}
description: {功能描述}，当用户{触发场景}时触发。
---

# {技能标题}

{简短介绍技能的核心功能（1-2 句话）}

## 技能工作流

调用 `todo_write` 工具创建待办任务：

步骤1 → 步骤2 → 步骤3 → 步骤4

### 步骤 1：{步骤名称}

{步骤 1 详解}
- 具体操作
- 参数说明
- 示例代码

### 步骤 2：{步骤名称}

{步骤 2 详解}

### 步骤 3：{步骤名称}

{步骤 3 详解}

## 使用说明

### 快速使用

{简要说明最常用使用方式}

### 高级选项

{说明可选参数或高级用法}

### 示例

{提供 2-3 个具体使用示例}

## 错误处理

| 错误 | 处理方式 |
|------|---------|  
| {错误场景 1} | {处理方案} |
| {错误场景 2} | {处理方案} |

## 禁止事项

- ❌ {不该做的操作 1}
- ❌ {不该做的操作 2}

## 参考资料

- {详细说明 1} → [references/xxx.md](references/xxx.md)
- {详细说明 2} → [references/yyy.md](references/yyy.md)
```

## manifest.json 模板

```json
{
  "name": "{中文名称}",
  "description": "{简要描述（50 字以内）}",
  "normalizedName": "{技能名称（与目录名一致）}",
  "category": "{分类}"
}
```

**分类选项**：工具、开发、文档、分析、创作、自动化

## Python 脚本模板

```python
#!/usr/bin/env python3
"""
{功能描述}

用法:
    python3 scripts/{script_name}.py <参数>

示例:
    python3 scripts/{script_name}.py input.txt
    python3 scripts/{script_name}.py input.txt --output output.md
"""

import sys
import argparse
from pathlib import Path


def main():
    # 参数解析
    parser = argparse.ArgumentParser(description='{功能描述}')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径', default=None)
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # 检查输入
    if not input_path.exists():
        print(f"❌ 错误: 文件不存在: {input_path}")
        sys.exit(1)
    
    # 核心逻辑
    print(f"🔍 开始处理: {input_path}")
    
    try:
        # 处理逻辑
        # ...
        
        if args.output:
            output_path = Path(args.output)
            # 写入输出
            print(f"✅ 完成: {output_path}")
        else:
            print("✅ 完成")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## 检查清单

### Frontmatter 检查

- [ ] 包含 `---` 分隔符
- [ ] `name` 字段与目录名完全一致
- [ ] `description` 包含功能描述
- [ ] `description` 包含触发场景（「当用户...时触发」）
- [ ] `description` 不限定特定工具

### 内容结构检查

- [ ] 总行数 < 500 行
- [ ] 章节层级最多三级（###）
- [ ] 包含「技能工作流」章节
- [ ] 工作流步骤 ≤ 10 个
- [ ] 每个步骤有独立章节（简单步骤除外）
- [ ] 包含「使用说明」章节
- [ ] 包含「错误处理」章节
- [ ] 包含「禁止事项」章节

### 执行确定性检查

- [ ] 无模糊目录指代（合适的目录、相关目录、目标目录）
- [ ] 无模糊脚本引用（运行脚本、执行脚本、相关脚本）
- [ ] 无模糊工具指令（使用工具、调用工具、合适的工具）
- [ ] 无程度副词（可能、也许、适当、尽量、大约、左右）
- [ ] 使用相对路径时明确工作目录

### Agent 兼容性检查

- [ ] 无工具名硬编码（Qoder、ClaudeCode、OpenClaw、Cursor）
- [ ] description 不限定特定工具
- [ ] 无特定工具路径（.qoder/、.claude/、.cursor/）
- [ ] 脚本不依赖特定工具 CLI

### 脚本检查

- [ ] 包含参数校验
- [ ] 包含错误处理
- [ ] 输出友好提示
- [ ] 使用相对路径

### 参考文档检查

- [ ] 文档命名语义化（小写、连字符）
- [ ] 内容为查阅类、参考类
- [ ] 未将核心工作流混入

### 资源文件检查

- [ ] 文件类型为模板、图片、样板代码
- [ ] 使用相对路径引用
- [ ] 脚本文件未混入 assets/

## 常见问题解答

### Q: 如何判断是否需要脚本？

**A**: 出现以下情况必须创建脚本：
1. 相同代码反复写
2. LLM 多次推理相同逻辑
3. 操作步骤固定、易出错
4. 需要高可靠性

### Q: 什么内容应该放到 references/？

**A**: 以下内容应分离到 references/：
- API 完整参数列表
- 错误码对照表
- 配置项说明
- Schema 定义
- 工作流详解（超过 500 行时）
- 常见问题解答

### Q: SKILL.md 超过 500 行怎么办？

**A**: 按以下优先级拆分：
1. 将详细说明移至 references/
2. 将示例代码移至 references/
3. 将参考资料移至 references/
4. 保留核心工作流和简要说明

### Q: 如何处理 Agent 兼容性问题？

**A**: 
1. 移除所有特定工具名（Qoder、ClaudeCode 等）
2. 使用通用描述（「执行」而非「在 Qoder 中执行」）
3. 使用相对路径而非工具特定路径
4. 脚本使用环境变量或参数化配置

### Q: 如何编写好的 description？

**A**: 遵循公式：`能做什么 + 何时触发`

**示例**：
- ✅ `处理 PDF 文件，当用户提到 PDF 时触发`
- ✅ `生成 Git 提交报告，当用户要求写日报或汇总工作时触发`
- ❌ `在 Qoder 中处理 PDF 文件`（限定工具）
- ❌ `PDF 处理工具`（缺少触发场景）

## 验证命令

创建完成后，运行验证脚本：

```bash
python3 scripts/validate-skill.py <skill-dir>
```

**示例**：
```bash
python3 scripts/validate-skill.py ./my-new-skill
```

**输出解读**：
- ✅ 所有检查项通过：技能质量优秀
- ⚠️ 存在 P1/P2 问题：建议修复
- ❌ 存在 P0 问题：必须修复

## 技能创建流程总结

```
用户需求
  ↓
需求收集（7 个关键问题）
  ↓
结构设计（目录、脚本、参考文档）
  ↓
内容生成（SKILL.md、manifest.json）
  ↓
脚本创建（确定性操作）
  ↓
质量验证（运行 validate-skill.py）
  ↓
问题修复（循环验证）
  ↓
完成交付（输出摘要）
```

遵循此模板和检查清单，可以确保创建的技能一次性通过 skill-review 审查，避免后续反复修改。
