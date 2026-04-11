# GitLab API 参考

## 认证方式

使用 `$GITLAB_TOKEN` 环境变量认证：
```bash
--header "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

## API 列表

### 获取MR详情

```bash
GET /api/v4/projects/:id/merge_requests/:iid
```

**用途**：获取MR的详细信息，包括分支、作者、标题、变更文件数量等

**示例**：
```bash
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}"
```

**返回字段**：
- `source_branch` / `target_branch` - 分支信息
- `author.username` / `author.name` - 作者信息
- `title` / `description` - MR 标题和描述
- `changes_count` - 变更文件数量

### 发布行内评审

```bash
POST /api/v4/projects/:id/merge_requests/:iid/discussions
```

**用途**：针对MR中特定代码位置发布评论

**示例**：
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

**position 参数说明**：
- `base_sha` / `start_sha` / `head_sha` - 从MR diff中获取的SHA信息
- `position_type` - 固定为 "text"
- `old_path` / `new_path` - 文件路径
- `old_line` / `new_line` - 代码行号

### 发布顶级报告

```bash
POST /api/v4/projects/:id/merge_requests/:iid/notes
```

**用途**：在MR顶部发布完整的评审报告

**示例**：
```bash
curl -s --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes" \
  --data '{"body": "[评审报告内容]"}'
```
