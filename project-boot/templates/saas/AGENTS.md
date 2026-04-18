# AI Agent 开发指南

## 语言设置
- 始终使用**简体中文**交流和编写注释
- 代码变量/函数名使用英文（遵循编程规范）

---

## 技术栈

**后端**：Java 21 | Spring Boot 3.5 | MyBatis-Plus | Dubbo | MySQL 8 | Redis 7
**前端**：React 18 | TypeScript 5.3 | Ant Design 5 | Vite 6 | Zustand
**测试**：JUnit 5 + Mockito | Vitest + Playwright

---

## 核心经验教训

### 1. 定时任务租户上下文处理

**问题**：定时任务中 TenantContext 为 null，MyBatis-Plus 自动添加 `tenant_id = '0'` 条件，查不到其他租户数据。

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
- 优先使用 `TenantContext.skip(() -> ...)` 函数式写法
- 跳过期间不会自动填充 `tenant_id`
- `MyBatisPlusMetaObjectHandler` 会在INSERT时自动填充 `tenant_id`（从TenantContext获取）
- 普通业务请求仍需保持租户隔离，此方案仅适用于定时任务

### 2. 服务管理

**端口清单**：Gateway:8080 | Auth:8001 | Platform:8082

**检查服务**：`lsof -i :端口 | grep LISTEN`

**网关启动方式**（JAR 模式，单进程，不用 mvn）：
```bash
# 构建网关 JAR（仅在网关代码变更时执行）
mvn package -pl your_project_name-gateway -DskipTests -q

# 启动网关
nohup java -jar your_project_name-gateway/target/your_project_name-gateway-1.0.0-SNAPSHOT.jar --spring.profiles.active=dev > /dev/null 2>&1 & disown
```

**重启业务服务**：
```bash
# 1. 重启业务服务
lsof -ti:8084 | xargs kill -9 && cd your_project_name-server && nohup mvn spring-boot:run > /dev/null 2>&1 &

# 2. 等待服务启动
sleep 10 && lsof -i :8084 | grep LISTEN
```

**注意事项**：
- **网关必须用 `java -jar` 启动**，禁止用 `mvn spring-boot:run`（Maven 会 fork 子进程，终端会话清理时会导致网关异常退出）
- **重启业务服务时，不需要重启网关**（网关使用 RestTemplate 无状态转发，下游服务重启后自动恢复）
- 遇到 `Network Error` 时，先检查目标服务是否启动完成，再检查网关（8080）

### 5. 租户拦截器注意事项

**问题本质**：
- MyBatis-Plus 租户拦截器在 `getTenantId()` 返回 null 时自动 fallback 为 `'0'`
- `ignoreTable()` 配置无法绕过此行为
- 拦截器作用于**所有 Mapper 操作**（包括 `@Select` 注解）

**绕过方法优先级**（从高到低）：
1. ✅ **TenantContext.skip() 函数式**（推荐，自动管理生命周期）
2. ⚠️ **原生 SQL**（`@Select` 手动写 SQL，但会被拦截器注入 tenant_id）
3. ⚠️ **QueryWrapper.apply()**（执行原生片段，绕过拦截器）
4. ❌ **ignoreTable 配置**（不推荐，影响全局）

**Dubbo 异常处理**：
```java
try {
    dubboService.call();
} catch (Exception e) {
    // 异常处理后，确保恢复租户上下文
    TenantContext.clear();  // 清除可能被污染的上下文
    throw e;
}
```

### 4. 常见问题速查

| 问题 | 检查方法 |
|------|----------|
| Network Error | 检查目标服务是否启动完成 → 检查网关（8080） → 查看日志 |
| 数据查不到 | SQL 日志中是否有 `tenant_id = '0'` |
| 权限不足 | `SELECT * FROM sys_permission WHERE permission_code = 'xxx'` |
| 前端按钮不显示 | 检查 `sys_permission` 表 → 使用 `dbmate` SKILL创建迁移SQL → 重启 Platform → 重新登录 |
| Dubbo服务找不到 | 检查提供者是否启动并注册到 Nacos |
| 定时任务数据异常 | 检查 TenantContext 是否正确设置/clear，是否使用了 skip() |
| 时间格式带T | 后端JacksonConfig已统一配置，VO直接返回LocalDateTime/LocalDate，禁止手动.toString() |
| 数据库操作 | 本地若没有安装mysql，请使用SKILL:/dba访问数据库，禁止使用mysql命令 |

---

## 开发规范

**必须**：
1. Service/算法/状态机先写测试（TDD）
2. 本地数据库使用`your_group_name`，数据库变更用 `dbmate` SKILL 迁移（时间戳命名，包含 -- migrate:up/down 注释）
3. 业务表必须有 tenant_id
4. Controller 返回 `R<T>` 格式
5. 定时任务使用 `TenantContext.skip()` 函数式写法
6. VO 直接返回 LocalDateTime/LocalDate，禁止手动 .toString()（JacksonConfig已统一配置）

**禁止**：
1. 跳过测试直接写实现
2. 手动执行 SQL 改表结构
3. 假设服务在运行（操作前先检查）
4. 使用SKILL: /dbmate 执行数据库DDL
5. 在定时任务中手动管理租户拦截器开关（必须使用 skip() 函数式）
6. 忽略 TenantContext 的生命周期管理（必须 try-finally 或 skip() 自动管理）