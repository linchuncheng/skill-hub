# Project Boot - 项目脚手架生成器

基于模板快速生成微服务项目脚手架，自动替换项目名、包名等关键信息。

## 功能特性

- ✅ **多模板支持** - 提供多种项目模板（目前只有SaaS）
- ✅ **一键生成** - 自动替换项目名、组织名、包名等占位符
- ✅ **完整结构** - 生成包含前后端、Docker、数据库迁移的完整项目
- ✅ **即开即用** - 生成的项目可直接编译运行

## 使用方式

```bash
# 1. 查看可用模板
python3 scripts/list_templates.py --detail

# 2. 生成项目
python3 scripts/init_project.py \
  --template saas \
  --group-name fengqun \
  --project-name fms \
  --project-desc "财务管理系统" \
  --target-path ~/Projects
```

## 生成的项目结构

```
your_project/
├── xxx-api/          # Dubbo RPC 接口
├── xxx-auth/         # 认证授权服务
├── xxx-gateway/      # API 网关
├── xxx-platform/     # 平台管理
├── xxx-server/       # 业务服务
├── xxx-admin/        # 管理后台前端
├── docker/           # Docker 配置
├── sql/              # 数据库迁移脚本
└── pom.xml           # Maven 父 POM
```

## 快速开始

```bash
# 初始化项目
cd your-project && git init

# 启动基础设施
docker-compose up -d

# 执行数据库迁移
# 使用 /dbmate 技能

# 编译后端
mvn clean install

# 安装前端依赖
cd xxx-admin && pnpm install
```

## 技术栈

- **后端**: Java 21 | Spring Boot 3.5 | MyBatis-Plus | Dubbo | MySQL | Redis
- **前端**: React 18 | TypeScript | Ant Design 5 | Vite
- **DevOps**: Docker | Nacos | dbmate
