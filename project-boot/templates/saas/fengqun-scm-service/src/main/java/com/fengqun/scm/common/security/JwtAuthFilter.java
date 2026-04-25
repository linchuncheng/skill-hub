package com.fengqun.scm.common.security;

import com.fengqun.scm.common.tenant.TenantContext;

import java.io.IOException;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

/**
 * JWT 认证过滤器
 *
 * 职责：
 * 1. 验证 JWT Token 有效性
 * 2. 提取 tenant_id、tenant_type 和 user_id
 * 3. 注入到请求属性，供后续业务使用
 */
@Slf4j
@Component
@Order(100)
public class JwtAuthFilter extends OncePerRequestFilter {

    private final String jwtSecret;

    // 健康检查/心跳接口路径前缀，无需认证
    private static final List<String> HEALTH_PATHS = List.of(
            "/actuator",
            "/api/status");

    // 公开接口路径前缀，无需认证
    private static final List<String> PUBLIC_PATHS = List.of(
            "/api/auth/login",
            "/api/auth/refresh-token");

    public JwtAuthFilter(@Value("${jwt.secret}") String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String requestURI = request.getRequestURI();

        // 1. 判断当前请求是否需要认证
        if (!isAuthRequired(requestURI)) {
            filterChain.doFilter(request, response);
            return;
        }

        // 2. 提取 Authorization Header
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            log.warn("未携带 Authorization Header：{}", requestURI);
            sendUnauthorizedResponse(response, "缺少认证 Token");
            return;
        }

        String token = authHeader.substring(7); // 去掉 "Bearer "

        // 3. 验证 Token
        Claims claims = TokenKit.parseToken(token, jwtSecret);
        if (claims == null) {
            log.warn("Token 验证失败：{}", requestURI);
            sendUnauthorizedResponse(response, "Token 无效或已过期");
            return;
        }

        // 4. 提取租户 ID、租户类型和用户 ID，注入到请求属性 和 TenantContext
        String tenantId = claims.get("tenant_id", String.class);
        String tenantType = claims.get("tenant_type", String.class);
        String userId = claims.getSubject();

        if (tenantId != null) {
            request.setAttribute("X-Tenant-Id", tenantId);
            TenantContext.setTenantId(tenantId);
        }
        if (tenantType != null) {
            request.setAttribute("X-Tenant-Type", tenantType);
            TenantContext.setTenantType(tenantType);
        }
        if (userId != null) {
            request.setAttribute("X-User-Id", userId);
            try {
                TenantContext.setUserId(Long.parseLong(userId));
            } catch (NumberFormatException e) {
                log.warn("User ID 解析失败：{}", userId);
            }
        }

        // 5. 放行
        filterChain.doFilter(request, response);
    }

    /**
     * 判断当前请求是否需要认证
     */
    private boolean isAuthRequired(String requestURI) {
        // 健康检查/心跳接口直接放行
        for (String healthPath : HEALTH_PATHS) {
            if (requestURI.equals(healthPath) || requestURI.startsWith(healthPath + "/")) {
                return false;
            }
        }

        // 公开接口直接放行
        for (String publicPath : PUBLIC_PATHS) {
            if (requestURI.equals(publicPath) || requestURI.startsWith(publicPath + "/")) {
                return false;
            }
        }

        return true; // 默认需要认证
    }

    /**
     * 返回 401 未授权响应
     */
    private void sendUnauthorizedResponse(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(String.format("{\"code\":401,\"msg\":\"%s\"}", message));
    }
}
