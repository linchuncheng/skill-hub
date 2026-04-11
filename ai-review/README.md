# AI 代码评审技能

提供渐进式、领域化的 AI 代码评审能力，可集成到 GitLab CI/CD 流程中。

## 功能特性

- **多语言支持**：JAVA、小程序、ADMIN、PYTHON、FLUTTER
- **问题分级**：严重🔴 / 重要🟡 / 可选⚪ / 忽略❌
- **自动化评审**：通过 GitLab API 自动发布行内评论和评审报告
- **规范驱动**：基于编码规范、接口设计规范、数据库规范等

## 使用方式

### 输入参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `GitLabProject` | GitLab工程ID | `12345` |
| `MR` | MR IID | `367` |
| `ReviewMode` | `full`(全量) / `incremental`(增量) | `full` |
| `ProjectType` | 项目类型 | `JAVA` |

### 工作流

获取MR信息 → 快速扫描 → 逐行评审 → 生成报告 → 发布行内评审 → 发布评审报告

## 目录结构

```
ai-review/
├── manifest.json           # 技能元数据
├── SKILL.md                # 核心工作流
└── references/             # 参考文档
    ├── Java编码规范.md
    ├── 小程序编码规范.md
    ├── Admin编码规范.md
    ├── Python编码规范.md
    ├── Flutter编码规范.md
    ├── 接口设计规范.md
    ├── 数据库设计规范.md
    ├── 缓存设计规范.md
    └── gitlab-api.md
```

## 环境变量

需要 GitLab CI 提供以下环境变量：
- `$GITLAB_TOKEN` - API Token
- `$CI_API_V4_URL` - API 地址
- `$CI_PROJECT_ID` - 项目ID
- `$CI_MERGE_REQUEST_IID` - MR IID

## 评审报告

评审完成后自动在 MR 中发布：
- **行内评论**：针对🔴严重和🟡重要问题的具体代码位置
- **顶级报告**：完整的评审报告，包含风险等级和合并建议