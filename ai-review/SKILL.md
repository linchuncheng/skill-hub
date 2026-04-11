---
name: ai-review
description: AI 代码评审 - 提供渐进式、领域化的AI代码评审技能
---

# AI 代码评审技能

## 概述

AI代码评审专家，发现关键问题、提升代码质量、防止架构腐化。

## 工作环境

**工作目录**: 目标项目根目录

**输入参数**

| 参数 | 说明 |
|------|------|
| `GitLabProject` | GitLab工程ID |
| `MR` | MR IID |
| `ReviewMode` | `full`(全量) / `incremental`(增量) |
| `ProjectType` | `JAVA` / `小程序` / `ADMIN` / `PYTHON` / `FLUTTER` |
| `DiffRange` | 变更范围,如 `origin/master...HEAD` |

**可用工具**: GitLab REST API (通过 `$GITLAB_TOKEN` 认证)

| API | 用途 | 详细说明 |
|-----|------|----------|
| `GET /api/v4/projects/:id/merge_requests/:iid` | 获取MR详情 | 见 [GitLab API 参考](references/gitlab-api.md#获取mr详情) |
| `POST /api/v4/projects/:id/merge_requests/:iid/discussions` | 发布行内评审 | 见 [GitLab API 参考](references/gitlab-api.md#发布行内评审) |
| `POST /api/v4/projects/:id/merge_requests/:iid/notes` | 发布顶级报告 | 见 [GitLab API 参考](references/gitlab-api.md#发布顶级报告) |

⚠️ API调用示例详见 [GitLab API 参考](references/gitlab-api.md)

**环境变量** (GitLab CI 自动提供):
- `$GITLAB_TOKEN` - GitLab API Token
- `$CI_API_V4_URL` - GitLab API v4 地址
- `$CI_PROJECT_ID` - 项目ID
- `$CI_MERGE_REQUEST_IID` - MR IID
- `$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME` - 源分支
- `$CI_MERGE_REQUEST_TARGET_BRANCH_NAME` - 目标分支

⚠️ `/cicd` 目录不参与评审

## 问题分级

### 通用分级标准

| 级别 | 说明 | 处理策略 |
|------|------|----------|
| 🔴 严重 | 必须修复 | 必须指出并提供修复方案 |
| 🟡 重要 | 建议修复 | 建议修复并说明原因 |
| ⚪ 可选 | 优化建议 | 作为优化建议提出 |
| ❌ 忽略 | 个人风格 | 不评审 |

### 技术栈特定问题

**规范文档**：
- JAVA: [Java编码规范](references/Java编码规范.md)、[接口设计规范](references/接口设计规范.md)、[缓存设计规范](references/缓存设计规范.md)、[数据库设计规范](references/数据库设计规范.md)
- 小程序: [小程序编码规范](references/小程序编码规范.md)
- ADMIN: [Admin编码规范](references/Admin编码规范.md)
- PYTHON: [Python编码规范](references/Python编码规范.md)
- FLUTTER: [Flutter编码规范](references/Flutter编码规范.md)

| 技术栈 | 🔴 严重问题 | 🟡 重要问题 |
|--------|-------------|-------------|
| JAVA | SQL注入、XSS、硬编码密钥、NPE风险、资源泄漏、并发问题 | 异常处理不完善、魔法值、重复代码、方法过长(>50行)、缺单元测试 |
| 小程序 | XSS、硬编码密钥、页面崩溃、资源泄漏、高频setState无节流、事件监听未清理、使用原生HTML标签代替Taro组件 | 状态设计混乱、超长组件(>200行)、滥用any、重复代码 |
| ADMIN | XSS、CSRF、SQL注入、敏感信息泄露、内存泄漏、竞态条件、未授权访问、跨层导入 | 性能瓶颈、错误处理缺失、类型安全问题、测试缺失 |
| PYTHON | SQL拼接注入、硬编码密钥、文件/DB连接未用`with`、裸`except:pass`、循环导入 | 循环内IO/DB调用、同步阻塞置于异步函数、`print`代替`logger`、超大函数(>50行)、缺类型注解 |
| FLUTTER | 硬编码密钥、资源泄漏(自己创建未在`dispose()`释放)、生产环境使用`print`、未处理Dart Analysis错误 | 弱命名(`a`/`b`/`c`)、超长方法(>100行)、多层嵌套Widget未拆分、未使用封装扩展方法(`isEmpty`/`isNotEmpty`等)、魔法值未用常量/枚举 |

## 工作流

获取MR信息 → 快速扫描 → 逐行评审 → 生成报告 → 发布行内评审 → 发布评审报告

### 步骤1: 获取MR信息

使用 GitLab API 获取 MR 详情:
```bash
MR_INFO=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}")
```

从返回的 JSON 中提取:
- `source_branch` / `target_branch` - 分支信息
- `author.username` / `author.name` - 作者信息
- `title` / `description` - MR 标题和描述
- `changes_count` - 变更文件数量

确定 `ProjectType`(根据项目技术栈)和 `ReviewMode`(全量/增量)

### 步骤2: 快速扫描

扫描变更范围:
- 使用 `git diff` 获取变更文件列表
- 过滤 `/cicd` 目录(不参与评审)
- 根据 `ProjectType` 加载对应编码规范(见各类型问题分级章节)

**ReviewMode 说明**:
- `full`(全量): 评审整个MR的所有变更文件
- `incremental`(增量): 仅评审自上次评审后的新增变更

**DiffRange 使用**:
- 当 `ReviewMode=incremental` 时,使用 `DiffRange` 参数限定diff范围
- 示例: `git diff origin/master...HEAD -- <文件列表>`

### 步骤3: 逐行评审

对照「问题分级」标准逐行评审:
- 🔴 严重问题: 必须指出并提供修复方案
- 🟡 重要问题: 建议修复并说明原因
- ⚪ 可选问题: 作为优化建议
- ❌ 忽略问题: 个人风格差异不评

### 步骤4: 生成报告

使用「评审报告模板」格式生成报告:
- 汇总 🔴 和 🟡 问题数量
- 给出风险等级评估(低/中/高)
- 提供合并建议(可合并/需修改/需返工)

### 步骤5: 发布行内评审

针对 🔴严重 / 🟡重要 问题,使用 GitLab API 发布行内评论:

```bash
curl -s --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/discussions" \
  --data '{
    "body": "🔴 **严重问题**: [问题描述]\n\n**风险**: [后果]\n\n**方案**: [修复方法]",
    "position": {
      "base_sha": "[base_sha]",
      "start_sha": "[start_sha]",
      "head_sha": "[head_sha]",
      "position_type": "text",
      "old_path": "[文件路径]",
      "new_path": "[文件路径]",
      "old_line": [行号],
      "new_line": [行号]
    }
  }'
```

⚠️ `position` 参数用于定位具体代码位置,需要从 MR diff 中获取 SHA 信息

### 步骤6: 发布评审报告

使用 GitLab API 发布完整评审报告到 MR 顶部:

```bash
curl -s --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes" \
  --data '{"body": "[评审报告内容]"}'
```

报告内容使用「评审报告模板」格式

### 异常处理

| 异常场景 | 处理策略 |
|----------|----------|
| GitLab API 调用失败 | 重试3次,失败后在CI日志输出错误信息并终止评审 |
| MR 无法访问 | 检查 `$GITLAB_TOKEN` 权限,输出错误并终止 |
| 无变更文件 | 跳过评审,CI输出 "无变更文件,跳过评审" |
| `/cicd` 目录变更 | 过滤 `/cicd` 目录,仅评审其他目录的变更 |

### 评审报告模板

```markdown
## 🌱 AI评审报告

> Last Commit: [信息]（[MM-dd HH:mm] by [用户]）

### 📊 概览
- **风险**: 🔴严重 / 🟡中等 / 🟢低
- **建议**: ✅可合并 / ⏸需修改 / ❌需返工
- **变更范围**: [DiffRange]

### 🔴 严重问题(必须修复)
**[标题]**
- **问题**: [描述]
- **风险**: [后果]
- **方案**: [修复方法]
- **位置**: `文件:行号`

### 🟡 重要问题(建议修复)
**[标题]**
- **问题**: [描述]
- **建议**: [改进方案]
- **位置**: `文件:行号`

### 💡 其他建议
- ✨ **亮点**: [好的设计]
- 📈 **优化**: [非阻塞建议]
```

## 关键提醒

**任务完成标准**: 必须使用AI评审报告模板,通过 GitLab API 发布到GitLab MR

**评审态度**
- ✅ 专业尊重、建设性反馈、解释原因、认可亮点
- ❌ 人身攻击、过度挑剔风格、不给方案

**CI输出**
```json
{
  "status": "success",
  "message": "评审已发布到 MR",
  "mr_id": 367,
  "risk_level": "低",
  "issues": { "severe": 0, "important": 0 },
  "api_result": { "status": "success", "reason": "" }
}
```

- ❌ 禁止在CI日志中复述MR详细内容
- 📌 详细内容在MR中查看，CI日志只做状态确认