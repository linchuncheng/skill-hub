package com.your_group_name.your_project_name.common.tenant;

import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

/**
 * 租户拦截器。
 *
 * 从 HTTP Header 中解析 X-Tenant-Id 和 X-Tenant-Type，注入到 TenantContext。
 */
@Slf4j
@Component
public class TenantInterceptor implements HandlerInterceptor {

    /**
     * Header 名称。
     */
    public static final String TENANT_ID_HEADER = "X-Tenant-Id";
    public static final String TENANT_TYPE_HEADER = "X-Tenant-Type";
    public static final String USER_ID_HEADER = "X-User-Id";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String tenantId = request.getHeader(TENANT_ID_HEADER);
        if (tenantId != null && !tenantId.isEmpty()) {
            TenantContext.setTenantId(tenantId);
            log.debug("Tenant ID 已注入上下文：{}", tenantId);
        }

        String tenantType = request.getHeader(TENANT_TYPE_HEADER);
        if (tenantType != null && !tenantType.isEmpty()) {
            TenantContext.setTenantType(tenantType);
            log.debug("Tenant Type 已注入上下文：{}", tenantType);
        }

        String userId = request.getHeader(USER_ID_HEADER);
        if (userId != null && !userId.isEmpty()) {
            try {
                TenantContext.setUserId(Long.parseLong(userId));
                log.debug("User ID 已注入上下文：{}", userId);
            } catch (NumberFormatException e) {
                log.warn("User ID 解析失败：{}", userId);
            }
        }
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler,
            Exception ex) {
        // 请求结束后清理上下文，防止内存泄漏
        TenantContext.clear();
        log.debug("Tenant 上下文已清理");
    }
}
