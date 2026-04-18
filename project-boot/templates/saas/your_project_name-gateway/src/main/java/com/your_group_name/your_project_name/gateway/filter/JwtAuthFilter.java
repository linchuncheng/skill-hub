package com.your_group_name.your_project_name.gateway.filter;

import com.your_group_name.your_project_name.gateway.config.RouteProperties;
import com.your_group_name.your_project_name.gateway.security.TokenKit;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
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
 * 2. 提取 tenant_id 和 user_id
 * 3. 注入到请求属性，供后续代理转发使用
 */
@Slf4j
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 100) // 确保在 GatewayProxyFilter 之前执行
public class JwtAuthFilter extends OncePerRequestFilter {

    private final RouteProperties routeProperties;
    private final String jwtSecret;

    // 构造函数注入（用于单元测试 Mock）
    public JwtAuthFilter(RouteProperties routeProperties, @Value("${jwt.secret}") String jwtSecret) {
        this.routeProperties = routeProperties;
        this.jwtSecret = jwtSecret;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String requestURI = request.getRequestURI();

        // 1. 判断当前路由是否需要认证
        boolean authRequired = isAuthRequired(requestURI);

        if (!authRequired) {
            // 公开接口，直接放行
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

        // 4. 提取租户 ID、租户类型和用户 ID，注入到请求属性
        String tenantId = claims.get("tenant_id", String.class);
        String tenantType = claims.get("tenant_type", String.class);
        String userId = claims.getSubject();

        if (tenantId != null) {
            request.setAttribute("X-Tenant-Id", tenantId);
        }
        if (tenantType != null) {
            request.setAttribute("X-Tenant-Type", tenantType);
        }
        if (userId != null) {
            request.setAttribute("X-User-Id", userId);
        }

        log.debug("Token 验证成功：tenant_id={}, tenant_type={}, user_id={}, path={}", tenantId, tenantType, userId,
                requestURI);

        // 5. 放行
        filterChain.doFilter(request, response);
    }

    /**
     * 健康检查/心跳接口路径前缀，无需认证
     */
    private static final java.util.List<String> HEALTH_PATHS = java.util.List.of(
            "/actuator",
            "/api/status");

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

        if (routeProperties.getRoutes() == null) {
            return true; // 默认需要认证
        }

        for (RouteProperties.Route route : routeProperties.getRoutes()) {
            if (route.getPredicates() != null) {
                for (String predicate : route.getPredicates()) {
                    if (predicate.startsWith("Path=")) {
                        String pathPattern = predicate.substring(5); // 去掉 "Path="
                        if (matchPath(requestURI, pathPattern)) {
                            return route.getAuthRequired() != null && route.getAuthRequired();
                        }
                    }
                }
            }
        }

        return true; // 默认需要认证
    }

    /**
     * 简单的路径匹配（支持 /** 通配符）
     */
    private boolean matchPath(String requestURI, String pathPattern) {
        if (pathPattern.endsWith("/**")) {
            String prefix = pathPattern.substring(0, pathPattern.length() - 3);
            return requestURI.startsWith(prefix);
        }
        return requestURI.equals(pathPattern);
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
