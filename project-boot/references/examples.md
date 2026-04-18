# 使用示例

## 示例 1：创建财务管理系统

### 第一步：查看可用模板

```bash
python3 project-boot/scripts/list_templates.py
```

输出：
```
============================================================
📦 可用的项目模板
============================================================

1. saas (v1.0.0)
   描述: SaaS 多租户微服务架构模板，包含完整的认证、网关、平台管理和业务模块
   作者: 林春成
   路径: /Users/jensen/.skills/project-boot/templates/saas

============================================================
共 1 个模板
============================================================

模板列表: saas
```

### 第二步：生成项目

```bash
python3 project-boot/scripts/init_project.py \
  --template saas \
  --group-name fengqun \
  --project-name fms \
  --project-desc "财务管理系统" \
  --target-path ~/projects/fms
```

### 生成结果

脚本会自动完成：
1. 复制 `templates/saas` 到 `~/projects/fms`
2. 替换 Maven 配置：`groupId=com.fengqun`，`artifactId=fengqun-fms`
3. 替换 Java 包名：`com.your_group_name.your_project_name.*` → `com.fengqun.fms.*`
4. 重命名模块目录：`your_project_name-api` → `fms-api`
5. 替换数据库和 Docker 配置：`fengqun_fms` 数据库、`fengqun-infra-*` 容器

### 验证结果

```bash
cd ~/projects/fms

# 查看项目结构（一级目录）
ls -1
# 输出: fms-admin, fms-api, fms-auth, fms-common, fms-gateway, fms-platform, fms-server

# 查看 Java 包名
find fms-gateway -name "*.java" -type f | head -1 | xargs head -3
# 输出: package com.fengqun.fms.gateway.filter;

# 查看 POM 文件
head -15 pom.xml
# 输出: <groupId>com.fengqun</groupId>
#       <artifactId>fengqun-fms</artifactId>
```

---

## 示例 2：创建 CRM 系统

```bash
python3 project-boot/scripts/init_project.py \
  --template saas \
  --group-name yourcompany \
  --project-name crm \
  --project-desc "客户关系管理系统" \
  --target-path ~/projects/crm
```

生成的项目：
- 项目名：`fengqun-crm`
- Java 包名：`com.yourcompany.crm.*`
- 模块目录：`crm-gateway`, `crm-auth`, `crm-platform` 等
- 前端目录：`crm-admin`

---

## 示例 3：创建 OMS 订单系统

```bash
python3 project-boot/scripts/init_project.py \
  --template saas \
  --group-name fengqun \
  --project-name oms \
  --project-desc "订单管理系统" \
  --target-path /data/projects/oms
```

---

## 常见问题

### Q1: 如何添加自定义模板？

1. 在 `templates/` 目录下创建新目录
2. 将完整的项目结构复制到该目录
3. 使用占位符命名：`your_project_name-*` 目录、`com.your_group_name.your_project_name.*` 包名
4. 创建 `_project.json` 文件描述模板信息

详见 SKILL.md 的"添加新模板"章节。

### Q2: 生成的项目可以直接运行吗？

生成的项目是完整的脚手架，需要：
1. 启动基础设施：`docker-compose up -d`
2. 初始化数据库（使用 `/dbmate` 技能）
3. 编译后端：`mvn clean install`
4. 安装前端依赖：`cd fms-admin && pnpm install`
5. 配置 Nacos 地址（根据实际环境）

### Q3: 如何删除不需要的模块？

直接删除对应的模块目录，然后在父 `pom.xml` 中移除模块引用即可。

例如删除 `xxx` 模块：
```bash
rm -rf fms-xxx
# 编辑 pom.xml，删除 <module>fms-xxx</module>
```

### Q4: 前端项目如何启动？

```bash
cd fms-admin
pnpm install
pnpm dev
```

前端会启动在 `http://localhost:5173`

### Q5: group-name 和 project-name 有什么区别？

- **group-name**：组织/公司英文名，用于 Java 包名（如 `com.fengqun`）
- **project-name**：项目英文名，用于模块命名（如 `fms`）

示例：`group-name=fengqun`, `project-name=fms`
- Java 包名：`com.fengqun.fms.*`
- 模块名：`fms-api`, `fms-gateway` 等
- Maven artifactId：`fengqun-fms`
