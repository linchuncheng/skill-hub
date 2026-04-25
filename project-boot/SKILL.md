---
name: project-boot
description: 基于模板快速生成新的微服务项目脚手架。支持多种项目模板（如 SaaS、CRM 等），自动替换项目名、包名等关键信息。使用场景：创建新项目、初始化工程、脚手架生成、微服务项目初始化。
---

# 项目脚手架生成器

基于预置的项目模板，快速生成新的微服务项目。支持模板选择、项目命名、自动替换等完整工作流。

## 技能工作流

调用 `todo_write` 工具创建待办任务：

列出模板 → 收集信息 → 生成项目 → 验证结果 → 后续引导

### 步骤 1：列出可用模板

执行模板列表脚本：

```bash
python3 project-boot/scripts/list_templates.py --detail
```

脚本输出：
- 模板名称和版本
- 模板描述和技术栈
- 模块列表和特性
- **需要提供的变量列表**（从 `_project.json` 的 `replacements` 字段读取）
- 模板路径

从输出中获取可用模板列表和变量清单，供用户选择和填写。

### 步骤 2：收集项目信息

根据步骤 1 的变量列表，向用户收集信息。

> **重要：** 不同模板的变量名称和用途不同，以 `list_templates.py --detail` 输出的变量说明为准。
> 
> **变量顺序规则：** 脚本会严格按照 `_project.json` 中 `replacements` 字段的顺序来识别变量：
> - **第一个变量**：通常是项目英文名（用于模块命名）
> - **第二个变量**：通常是组织英文名（用于 Java 包名）
> 
> 在组装 `--vars` 参数时，必须按照这个顺序传递变量值。

通常包括：
- **项目英文名**（如 `your_project_name` 或模板自定义名称）：
  - 用途：模块命名（如 `fms-server`、`fms-api`）
  - 示例：`fms`、`crm`、`oms`
  - 要求：小写字母，简短明了

- **组织英文名**（如 `your_group_name` 或模板自定义名称）：
  - 用途：Java 包名 `com.{group_name}.{project_name}.*`
  - 示例：`fengqun`、`yourcompany`
  - 要求：小写字母，简短明了

还需要收集：
- **目标代码工作区**（target-path）：
  - 新项目将创建在该工作区下
  - 最终路径：`{target-path}/{group_name}-{project_name}`
  - 示例：`~/Projects` → `~/Projects/fengqun-fms`

### 步骤 3：生成项目脚手架

将收集到的信息组装成 JSON，执行项目生成脚本：

```bash
python3 project-boot/scripts/init_project.py \
  --template {模板名} \
  --target-path {目标路径} \
  --vars '{"第一个变量名": "值1", "第二个变量名": "值2"}'
```

**示例（saas 模板）：**
```bash
python3 project-boot/scripts/init_project.py \
  --template saas \
  --target-path ~/Projects \
  --vars '{"scm": "fms", "fengqun": "fengqun"}'
```

> **注意：** `--vars` 中的变量名必须与模板 `_project.json` 中 `replacements` 字段的键名完全一致。

脚本自动完成：
1. 读取模板的 `_project.json` 配置
2. 在工作区下创建项目目录（命名规则：`{第二个变量值}-{第一个变量值}`）
3. 复制模板到该目录
4. 按顺序替换所有占位符（文件内容 → 文件名 → 目录名）
5. 验证生成结果

### 步骤 4：验证生成结果

脚本会自动验证以下项：
- ✅ Java 文件中的包名和 import 已替换
- ✅ Maven 配置中的项目名已替换
- ✅ 目录名称已更新（一级目录结构）
- ✅ Maven 多模块结构完整
- ✅ Docker 配置中的名称已更新
- ✅ 数据库名称已替换

如有问题，脚本会列出所有验证失败的项。

### 步骤 5：后续引导

项目生成完成后，引导用户执行后续步骤：

1. 进入项目目录
2. 初始化 Git 仓库
3. 启动基础设施（Docker）
4. 初始化数据库（使用 `/dbmate` 技能）
5. 编译后端
6. 安装前端依赖

详见"使用说明"章节。

## 替换规则

脚本根据模板的 `_project.json` 中 `replacements` 字段动态替换：

- **小写占位符**（如 `your_project_name`）：替换为用户输入的原值
- **大写占位符**（如 `YOUR_PROJECT_NAME`）：自动转换为用户输入的大写值
- **其他自定义占位符**：按模板配置的顺序依次替换

替换范围：
- 文件内容（按占位符长度降序替换，避免冲突）
- 文件名（支持包含占位符的前缀/后缀）
- 目录名（从深到浅重命名，避免路径错误）

## 可用模板

### saas - SaaS 多租户微服务架构

**技术栈**：
- 后端：Java 21 | Spring Boot 3.5 | MyBatis-Plus | Dubbo | MySQL 8 | Redis 7
- 前端：React 18 | TypeScript 5.3 | Ant Design 5 | Vite 6
- DevOps：Docker | Nacos | dbmate

**模块结构**：
- `{project-name}-common`：公共基础模块、Dubbo RPC 接口定义
- `{project-name}-gateway`：API 网关服务
- `{project-name}-service`：平台管理、认证授权、业务模块
- `{project-name}-admin`：管理后台前端

## 使用说明

### 快速开始

```bash
# 1. 查看可用模板（包含变量列表）
cd /Users/username/.skills/project-boot
python3 scripts/list_templates.py --detail

# 2. 生成项目（根据步骤 1 的变量收集用户输入后执行）
python3 scripts/init_project.py \
  --template saas \
  --target-path /Users/username/Projects \
  --vars '{"your_project_name": "fms", "your_group_name": "fengqun"}'

# 项目将创建在: /Users/username/Projects/fengqun-fms
```

### 生成后操作

```bash
# 初始化 Git
git init && git add . && git commit -m "Initial commit"

# 启动基础设施
docker-compose up -d

# 初始化数据库（使用 dbmate 技能）
# 执行: /dbmate: 初始化数据库迁移

# 编译后端
mvn clean install

# 安装前端依赖（如果模板包含前端）
cd {project-name}-admin && pnpm install
```

### 添加新项目模板

1. 在 `templates/` 下创建新目录
2. 复制完整项目结构
3. 使用占位符命名变量（如 `your_project_name`、`your_company_name` 等）
4. 创建 `_project.json` 描述模板信息和替换规则

**`_project.json` 示例**：
```json
{
  "name": "saas",
  "description": "SaaS 多租户微服务架构",
  "version": "1.0.0",
  "replacements": {
    "your_project_name": "项目英文名",
    "your_group_name": "组织英文名"
  }
}
```

脚本会根据 `replacements` 字段自动生成问题列表并执行替换。

## 注意事项

- 生成的项目包含示例代码，可按需删除或修改
- 租户管理机制已内置（saas 模板）
- 所有模块使用统一依赖版本（父 POM 管理）
- 前端路由和菜单需根据实际业务重新定义
- 数据库连接和 Nacos 配置需根据实际环境调整