---
name: dbmate
description: dbmate 数据库迁移工具，支持多模块动态发现、环境配置管理、迁移和回滚操作
---

# 数据库迁移工具

## 使用方式

当用户需要执行数据库迁移、查看迁移状态或管理 SQL 脚本时触发此技能。

**自动触发词：** "执行迁移"、"数据库升级"、"dbmate"、"迁移状态"、"编写SQL"、"查看迁移历史"

**使用场景引导：**
- 当需要编写 DDL 语句（CREATE/ALTER/DROP TABLE 等）时，推荐使用此工具进行版本化管理
- 将 DDL 写入 `sql/<模块>/` 目录下的迁移文件中，而不是直接执行 SQL
- 通过 dbmate 迁移机制确保数据库变更可追踪、可回滚

---

## 技能工作流

调用 `todo_write` 工具创建待办任务：

配置选择 → 执行迁移 → 验证结果 → 错误处理

### 步骤 1：配置选择（步骤 1）

确定使用哪个环境的配置文件（local/test）。

### 步骤 2：执行迁移（步骤 2）

调用 `scripts/migrate.sh` 脚本执行迁移命令，支持全模块或单模块迁移。

### 步骤 3：验证结果（步骤 3）

查看迁移状态、回滚操作。使用 `--command=status/down` 参数。

### 步骤 4：错误处理（步骤 4）

根据错误类型执行对应解决方案。参考 [错误处理表格](#步骤-4错误处理步骤-4)。

---

## 核心工作流

> **工作目录**：项目根目录（包含 `sql/` 目录的文件夹）

### 步骤 1：配置选择（步骤 1）

#### 步骤 1.1：确定使用的配置文件（步骤 1）
列出可用的配置文件：
```bash
cd <项目根目录>  # 包含 sql/ 目录的项目文件夹
ls sql/*.env
```

> **注意**：脚本会自动检查并安装 dbmate（如果未安装），无需手动操作。

**预期目录结构：**
```
sql/
├── local.env                # 本地环境配置
├── test.env                 # 测试环境配置（可选）
├── dbmate_platform/         # 子文件夹名 = 迁移表名称
│   ├── 20260410100000_init.sql
│   └── 20260410100100_xxx.sql
├── dbmate_erp/
│   └── 20260410100000_init.sql
├── dbmate_wms/
│   └── 20260410100000_init.sql
└── dbmate_tms/
    └── 20260410120000_init.sql
```

**配置优先级：**
1. 用户指定：`--config=test`（使用 test.env）
2. 自动选择：优先 `local.env`，其次 `.env`
3. 环境变量覆盖：`DATABASE_URL`

**读取配置：**
```bash
cat sql/local.env
```

#### 步骤 1.2：动态读取模块列表（步骤 1）
```bash
# 读取 sql/ 下所有子文件夹（即模块列表）
MODULES=$(find sql -mindepth 1 -maxdepth 1 -type d -not -name '.*' | xargs -I{} basename {})
echo "检测到模块：$MODULES"
```

### 步骤 2：执行迁移（步骤 2）

#### 步骤 2.1：执行迁移命令（步骤 2）

**读取配置文件：**
```bash
CONFIG_FILE="sql/local.env"  # 或用户指定的配置
```

**执行所有模块迁移：**
```bash
bash <SKILL目录>/scripts/migrate.sh
```

**常用命令：**
```bash
# 执行迁移
bash <SKILL目录>/scripts/migrate.sh

# 查看迁移状态
bash <SKILL目录>/scripts/migrate.sh --command=status

# 回滚最后一个迁移
bash <SKILL目录>/scripts/migrate.sh --command=down

# 只迁移特定模块
bash <SKILL目录>/scripts/migrate.sh --module=dbmate_erp

# 指定配置
bash <SKILL目录>/scripts/migrate.sh --config=test
```

### 步骤 3：验证结果（步骤 3）

查看迁移状态、回滚操作：

```bash
# 查看迁移状态
bash <SKILL目录>/scripts/migrate.sh --command=status

# 回滚最后一个迁移
bash <SKILL目录>/scripts/migrate.sh --command=down

# 查看特定模块状态
bash <SKILL目录>/scripts/migrate.sh --module=dbmate_erp --command=status
```

### 步骤 4：错误处理（步骤 4）

| 错误现象 | 原因 | 解决方案 |
|---------|------|----------|
| `brew: command not found` | 未安装 Homebrew | 先安装 Homebrew: https://brew.sh |
| `dbmate 安装失败` | 网络或权限问题 | 检查网络连接或手动执行 `brew install dbmate` |
| `Unable to connect` | 数据库连接失败 | 检查配置文件中的 DATABASE_URL |
| `No migration files found` | sql/ 目录下没有 SQL 文件 | 检查目录结构是否正确 |
| `Found more than one migration` | 版本号重复 | 修改 SQL 文件版本号确保唯一 |
| `部分模块迁移失败` | 某个模块的 SQL 有错误 | 检查失败模块的 SQL 语法，查看上方错误信息 |

### 附录：配置文件管理（参考）

#### 配置文件格式（.env）
```env
DATABASE_URL="<数据库类型>://<用户名>:<密码>@<主机>:<端口>/<数据库名>"
```

**数据库类型：**
- MySQL：`mysql://`
- PostgreSQL：`postgres://`

**示例：**
```env
# MySQL
DATABASE_URL="mysql://root:fengqun123@localhost:3306/fengqun_scm"

# PostgreSQL
DATABASE_URL="postgres://username:password@localhost:5432/database_name"
```

**注意事项：**
- 使用 dbmate 标准 URL 格式（非 JDBC 格式）
- URL 值必须加双引号
- 不需要单独的 username/password 字段

#### 多环境配置
- `local.env` - 本地开发环境（默认）
- `test.env` - 测试环境
- `.env` - 默认配置（备用）

---

### 附录：新增迁移文件指南

> 以下为独立章节，非工作流步骤，按需参考。

#### 文件命名
dbmate 使用时间戳格式命名：
```
sql/<module>/<时间戳>_<描述>.sql
```
- 时间戳格式：`YYYYMMDDHHMMSS`（14位数字）
- 描述：小写英文，多个单词用下划线分隔
- 示例：`20260410120000_create_user_table.sql`

**时间戳生成：**
```bash
date +%Y%m%d%H%M%S  # 输出：20260410120000
```

#### 文件内容（必须包含 migrate 标记）
```sql
-- 20260410120000_create_user_table.sql

-- migrate:up
CREATE TABLE IF NOT EXISTS sys_login_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    login_time DATETIME NOT NULL,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_login_log_user_id ON sys_login_log(user_id);

-- migrate:down
DROP TABLE IF EXISTS sys_login_log;
```

#### 版本号规则
- 使用时间戳确保唯一性（精确到秒）
- 同一秒内创建多个文件时，手动调整最后几位
- **不同模块可以有相同时间戳**（因为使用独立的迁移表）

### 附录：模块说明（参考）

> 以下为示例模块列表，实际模块以 `sql/` 目录下的子文件夹为准。

| 模块文件夹 | 迁移表名 | 说明 | 文件数 |
|-----------|---------|------|--------|
| dbmate_platform | dbmate_platform | 平台管理（权限/菜单/字典） | 10 |
| dbmate_erp | dbmate_erp | ERP业务（采购/供应商/商品） | 3 |
| dbmate_wms | dbmate_wms | 仓库管理（入库/出库/库存） | 2 |
| dbmate_tms | dbmate_tms | 运输管理（配送/线路） | 1 |

---

## 禁止事项

- ❌ 不要修改已执行的 SQL 文件（会导致 checksum 校验失败）
- ❌ 不要手动修改迁移历史表数据
- ❌ 不要在配置文件中使用明文密码（生产环境使用环境变量）
- ❌ 不要混用不同的配置目录
- ❌ 不要忘记写 `-- migrate:down` 回滚 SQL

## 快速参考

```bash
# 执行所有模块迁移（使用本地配置）
cd <项目根目录>
bash <SKILL目录>/scripts/migrate.sh

# 查看某个模块的迁移状态
bash <SKILL目录>/scripts/migrate.sh --module=dbmate_erp --command=status

# 回滚最后一个迁移
bash <SKILL目录>/scripts/migrate.sh --module=dbmate_platform --command=down
```
