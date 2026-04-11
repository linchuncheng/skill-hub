# dbmate 数据库迁移工具

自动化执行 dbmate 数据库迁移，支持多模块动态发现、环境配置管理、迁移和回滚操作。

## 触发词

"执行迁移"、"数据库升级"、"dbmate"、"迁移状态"、"新增SQL"、"查看迁移历史"、"回滚迁移"

## 使用示例

```bash
# 执行所有模块迁移
执行迁移

# 查看迁移状态
查看 dbmate_erp 的迁移状态

# 回滚最后一个迁移
回滚 dbmate_platform 的迁移

# 新增迁移文件
新增 SQL 文件 V1.2.0__add_user_table
```

## 核心能力

- ✅ **动态模块发现** - 自动扫描 sql/ 目录，无需硬编码模块列表
- ✅ **多环境支持** - local/test 配置自动切换
- ✅ **一键迁移** - 自动遍历所有模块执行迁移
- ✅ **状态查询** - 查看迁移历史、回滚操作
- ✅ **安全可靠** - 必须编写 migrate:down 回滚 SQL
- ✅ **标准格式** - 支持 dbmate 时间戳格式和 .env 配置

## 前置要求

- 安装 dbmate CLI：`brew install dbmate`
- 项目根目录包含 `sql/` 目录及配置文件

## 目录结构

```
项目根目录/
├── sql/
│   ├── local.env             # 本地配置
│   ├── test.env              # 测试配置（可选）
│   └── dbmate_*/             # 模块目录
│       └── *.sql             # 迁移文件（含 migrate:up/down 标记）
```

## 工作流程

1. **环境检查** - 验证 CLI、目录结构、配置文件
2. **配置选择** - 确定使用哪个环境的配置
3. **执行迁移** - 调用脚本执行迁移命令
4. **验证结果** - 检查迁移状态和错误
5. **错误处理** - 根据错误类型提供解决方案

## SQL 文件格式

每个 SQL 文件必须包含 `-- migrate:up` 和 `-- migrate:down` 标记：

```sql
-- 20260410120000_create_users_table.sql

-- migrate:up
CREATE TABLE users (id BIGINT PRIMARY KEY, name VARCHAR(100));

-- migrate:down
DROP TABLE users;
```

**命名规范：**
- 使用时间戳格式：`YYYYMMDDHHMMSS_description.sql`
- 描述使用小写英文，多个单词用下划线分隔
- 示例：`20260410120000_create_user_table.sql`
