# 脚本详细说明

## list_templates.py - 模板列表脚本

### 功能
列出 `templates/` 目录下所有可用的项目模板，支持读取 `_project.json` 元信息。

### 使用方法
```bash
# 基本模式
python3 project-boot/scripts/list_templates.py

# 详细模式（显示技术栈、特性、模块信息）
python3 project-boot/scripts/list_templates.py --detail
```

### 输出格式
脚本会输出：
1. 模板名称和版本
2. 模板描述（从 `_project.json` 读取）
3. 作者信息
4. 模板路径
5. 技术栈、模块、特性（仅 `--detail` 模式）
6. 模板列表（逗号分隔，供其他脚本调用）

---

## init_project.py - 项目生成脚本

### 功能
基于模板生成新的微服务项目，自动完成：
1. 复制模板文件
2. 替换 Maven 配置、Java 包名、模块名
3. 替换数据库和 Docker 配置
4. 重命名目录
5. 验证生成结果

### 参数说明

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--template` | 是 | 模板名称 | `saas` |
| `--group-name` | 是 | 组织英文名 | `fengqun`, `yourcompany` |
| `--project-name` | 是 | 项目英文名 | `fms`, `crm`, `oms` |
| `--project-desc` | 是 | 项目中文名 | "财务管理系统" |
| `--target-path` | 是 | 目标路径 | `~/projects/fms` |

### 替换内容

脚本会自动替换以下内容：

1. **Maven 配置**
   - 父 POM：`groupId`, `artifactId`, `name`
   - 子模块：`artifactId`

2. **Java 包名**
   - package 声明
   - import 语句

3. **目录名称**
   - 所有一级模块目录

4. **Docker 配置**
   - 容器名称
   - 数据库名称
   - 环境变量

5. **项目描述**
   - 模板描述 → 用户自定义描述

### 执行流程

1. **验证模板**
   - 检查模板是否存在
   - 如果不存在，列出可用模板

2. **构建替换规则**
   - 根据 group-name 和 project-name 生成所有替换规则
   - 按长度排序，避免短规则先替换

3. **复制文件**
   - 跳过 `.git`, `node_modules`, `target` 等目录
   - 跳过二进制文件
   - 复制所有文本文件

4. **替换内容**
   - 遍历所有复制的文件
   - 应用所有替换规则
   - 统计替换次数

5. **重命名目录**
   - 重命名模块目录（如 `your_project_name-api` → `fms-api`）
   - 从深到浅排序，避免父目录先重命名

6. **验证项目**
   - 检查关键目录是否存在
   - 检查 POM 文件中的项目名
   - 检查 Java 文件中的包名
   - 检查 docker-compose.yml 中的配置

### 输出统计

```
✅ 项目生成完成!
📄 复制文件: 532
✏️  修改文件: 308
📁 重命名目录: 7
```

### 验证检查

- ✅ 关键目录存在（`fms-api`, `fms-gateway`, `fms-admin` 等）
- ✅ POM 文件中包含正确的项目名
- ✅ Java 文件中使用新的包名
- ✅ docker-compose.yml 中配置正确

### 跳过文件

#### 跳过的目录
- `.git` - Git 版本控制
- `node_modules` - Node.js 依赖
- `target` - Maven 编译输出
- `dist` - 前端构建输出
- `.idea` - IDE 配置
- `.vscode` - IDE 配置
- `__pycache__` - Python 缓存
- `.planning` - 规划文件

#### 跳过的文件
- `.DS_Store` - macOS 系统文件
- `init_project.py` - 脚本本身
- `README.md` - 说明文档

### 错误处理

- 文件无法读取时跳过（二进制文件、权限问题）
- 目录重命名失败时显示错误但继续
- 目标路径已存在时询问是否覆盖
- 验证失败时列出所有问题

### 注意事项

1. **替换顺序**：按字符串长度降序替换，避免短字符串先替换导致长字符串无法匹配
2. **目录重命名顺序**：从深到浅重命名，避免父目录先重命名导致子目录路径错误
3. **文件编码**：只处理 UTF-8 编码的文本文件
4. **覆盖确认**：目标路径已存在时会询问是否覆盖
