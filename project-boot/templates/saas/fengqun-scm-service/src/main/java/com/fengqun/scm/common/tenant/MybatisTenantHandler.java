package com.fengqun.scm.common.tenant;

import com.baomidou.mybatisplus.extension.plugins.handler.TenantLineHandler;

import java.util.Arrays;
import java.util.List;

import lombok.extern.slf4j.Slf4j;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.StringValue;

/**
 * MyBatis-Plus 租户处理器。
 *
 * 自动在 SQL 中追加 tenant_id 过滤条件。
 */
@Slf4j
public class MybatisTenantHandler implements TenantLineHandler {

    /**
     * 平台级表（不做租户隔离）。
     */
    private static final List<String> IGNORE_TABLES = Arrays.asList(
            "sys_tenant", // 租户表本身
            "sys_menu", // 菜单表（全局资源）
            "sys_role", // 角色表（在Service层根据业务逻辑处理）
            "sys_role_menu", // 角色菜单关联表
            "sys_permission", // 权限表（全局资源）
            "sys_role_permission", // 角色权限关联表
            "sys_user_role", // 用户角色关联表
            "sys_login_log", // 登录日志表
            "sys_user" // 用户表（在Service层根据业务逻辑处理）
    );

    @Override
    public Expression getTenantId() {
        String tenantId = TenantContext.getTenantId();
        if (tenantId == null) {
            return new StringValue("0");
        }
        return new StringValue(tenantId);
    }

    @Override
    public boolean ignoreTable(String tableName) {
        // 如果设置了跳过租户拦截器，则所有表都不添加租户条件
        if (TenantContext.isSkipTenantInterceptor()) {
            return true;
        }
        // 平台级表不做租户隔离
        return IGNORE_TABLES.contains(tableName);
    }

    @Override
    public String getTenantIdColumn() {
        return "tenant_id";
    }
}
