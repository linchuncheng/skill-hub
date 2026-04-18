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
- 模板路径

从输出中获取可用模板列表，供用户选择。

### 步骤 2：收集项目信息

向用户收集以下必需信息：

1. **选择模板**：从步骤 1 的模板列表中选择
2. **组织英文名**（group-name）：
   - 用途：Java 包名 `com.{group_name}.{project_name}.*`
   - 示例：`fengqun`、`yourcompany`
   - 要求：小写字母，简短明了
3. **项目英文名**（project-name）：
   - 用途：模块命名（如 `fms-server`、`fms-api`）
   - 示例：`fms`、`crm`、`oms`
   - 要求：小写字母，简短明了
4. **项目中文名**（project-desc）：
   - 用途：项目描述
   - 示例："财务管理系统"、"客户关系管理系统"
5. **目标代码工作区**（target-path）：
   - 新项目将创建在该工作区下
   - 最终路径：`{target-path}/{group-name}-{project-name}`
   - 示例：`~/Projects` → `~/Projects/fengqun-fms`

### 步骤 3：生成项目脚手架

使用收集的信息执行项目生成脚本：

```bash
python3 project-boot/scripts/init_project.py \
  --template {模板名} \
  --group-name {组织英文名} \
  --project-name {项目英文名} \
  --project-desc "{项目中文名}" \
  --target-path {目标路径}
```

脚本自动完成：
1. 在工作区下创建 `{group-name}-{project-name}` 目录
2. 复制模板到该目录
3. 替换所有占位符（Maven、Java、Docker 等）
4. 重命名模块目录
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

脚本自动替换以下内容：

| 类型 | 示例 |
|------|------|
| Maven 配置 | `your_project_name` → `fengqun-fms` |
| Java 包名 | `com.your_group_name.your_project_name.*` → `com.fengqun.fms.*` |
| 模块目录 | `your_project_name-api` → `fms-api` |
| 数据库名 | `your_group_name` → `fengqun` |
| Docker 容器 | `your_project_name-infra-mysql` → `fengqun-infra-mysql` |

## 可用模板

### saas - SaaS 多租户微服务架构

**技术栈**：
- 后端：Java 21 | Spring Boot 3.5 | MyBatis-Plus | Dubbo | MySQL 8 | Redis 7
- 前端：React 18 | TypeScript 5.3 | Ant Design 5 | Vite 6
- DevOps：Docker | Nacos | dbmate

**模块结构**：
- `{project-name}-common`：公共基础模块
- `{project-name}-api`：Dubbo RPC 接口定义
- `{project-name}-auth`：认证授权服务
- `{project-name}-gateway`：API 网关服务
- `{project-name}-platform`：平台管理服务
- `{project-name}-server`：业务服务模块（示例）
- `{project-name}-admin`：管理后台前端

## 使用说明

### 快速开始

```bash
# 1. 查看可用模板
cd /Users/jensen/.skills/project-boot
python3 scripts/list_templates.py --detail

# 2. 生成项目
python3 scripts/init_project.py \
  --template saas \
  --group-name fengqun \
  --project-name fms \
  --project-desc "财务管理系统" \
  --target-path /Users/jensen/Code

# 项目将创建在: /Users/jensen/Code/fengqun-fms
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

# 安装前端依赖
cd fms-admin && pnpm install
```

### 添加新项目模板

1. 在 `templates/` 下创建新目录
2. 复制完整项目结构
3. 使用占位符命名：`your_project_name-*`、`com.your_group_name.your_project_name.*`
4. 创建 `_project.json` 描述模板信息

详见 `references/_project.json.tpl` 模板文件。

## 注意事项

- 生成的项目包含示例代码，可按需删除或修改
- 租户管理机制已内置（saas 模板）
- 所有模块使用统一依赖版本（父 POM 管理）
- 前端路由和菜单需根据实际业务重新定义
- 数据库连接和 Nacos 配置需根据实际环境调整