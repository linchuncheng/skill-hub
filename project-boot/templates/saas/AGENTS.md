# AI Agent 开发指南

## 语言设置
- 始终使用**简体中文**交流和编写注释
- 代码变量/函数名使用英文（遵循编程规范）

## 技术栈

**后端**：Java 21 | Spring Boot 3.5 | MyBatis-Plus | Dubbo | MySQL 8 | Redis 7
**前端**：React 18 | TypeScript 5.3 | Ant Design 5 | Vite 6 | Zustand
**测试**：JUnit 5 + Mockito | Vitest + Playwright

## 核心规范

### 1. 定时任务租户上下文处理

**推荐写法**（函数式，自动管理生命周期）：
```java
@Scheduled(fixedDelay = 30000)
public void scheduledTask() {
    // 使用 skip() 自动管理开关生命周期
    List<String> tenantIds = TenantContext.skip(() -> getAllTenantIds());
    
    for (String tenantId : tenantIds) {
        TenantContext.setTenantId(tenantId);
        try {
            List<Entity> list = mapper.selectList(wrapper);
            processData(list);
        } finally {
            TenantContext.clear();
        }
    }
}
```

**关键要点**：
- 优先使用 `TenantContext.skip(() -> ...)` 函数式写法，自动管理生命周期
- 跳过期间不会自动填充 `tenant_id`
- `MyBatisPlusMetaObjectHandler` 会在INSERT时自动填充 `tenant_id`（从TenantContext获取）
- 普通业务请求仍需保持租户隔离，此方案仅适用于定时任务

### 2. 常见问题速查

| 问题 | 检查方法 |
|------|----------|
| 数据查不到 | SQL 日志中是否有 `tenant_id = '0'` |
| 权限不足 | `SELECT * FROM sys_permission WHERE permission_code = 'xxx'` |
| 前端按钮不显示 | 检查 `sys_permission` 表 → 使用 `dbmate` SKILL创建迁移SQL → 重启 Service → 重新登录 |
| Dubbo服务找不到 | 检查提供者是否启动并注册到 Nacos |
| 定时任务数据异常 | 检查 TenantContext 是否正确设置/clear，是否使用了 skip() |
| 时间格式带T | 后端JacksonConfig已统一配置，VO直接返回LocalDateTime/LocalDate，禁止手动.toString() |
| 数据库DML操作 | 优先使用dba技能访问数据库 |
| 数据库DDL操作 | 在工程根目录的sql目录下编写DDL，写完后使用`dbmate`技能执行，不要直接用dba技能执行 |
| 启动/重启服务 | **修改完Java代码后，必须自动执行 `./start.sh` 重新启动服务**（脚本会自动构建并运行前后端服务） |

## 开发规范

**必须**：
1. Service/算法/状态机先写测试（TDD）
2. 本地数据库使用`fengqun`，数据库变更用 `dbmate` SKILL 迁移（时间戳命名，包含 -- migrate:up/down 注释）
3. 业务表必须有 tenant_id
4. Controller 返回 `R<T>` 格式
5. 定时任务使用 `TenantContext.skip()` 函数式写法，自动管理生命周期
6. VO 直接返回 LocalDateTime/LocalDate，禁止手动 .toString()（JacksonConfig已统一配置）
7. 异常处理后，确保恢复租户上下文（使用 `TenantContext.clear()`）

**禁止**：
1. 直接执行数据库DDL不维护/sql/dbmate_scm脚本
2. 在定时任务中手动管理租户拦截器开关（必须使用 skip() 函数式）
3. 忽略 TenantContext 的生命周期管理（必须 try-finally 或 skip() 自动管理）