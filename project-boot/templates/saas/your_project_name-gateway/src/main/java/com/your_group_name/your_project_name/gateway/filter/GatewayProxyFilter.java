package com.your_group_name.your_project_name.gateway.filter;

import com.your_group_name.your_project_name.gateway.config.RouteProperties;

import java.io.IOException;
import java.util.Enumeration;

import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

/**
 * 网关代理转发过滤器
 *
 * 职责：根据路由配置转发请求到下游服务，注入租户相关 Header
 */
@Slf4j
@Component
@Order(Ordered.LOWEST_PRECEDENCE)
public class GatewayProxyFilter extends OncePerRequestFilter {

    private final RouteProperties routeProperties;
    private final RestTemplate restTemplate;

    public GatewayProxyFilter(RouteProperties routeProperties, RestTemplate restTemplate) {
        this.routeProperties = routeProperties;
        this.restTemplate = restTemplate;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        // CORS 由 CorsFilter 统一处理，此处不再处理

        String requestURI = request.getRequestURI();
        RouteProperties.Route matchedRoute = findMatchedRoute(requestURI);

        if (matchedRoute == null) {
            sendNotFoundResponse(response);
            return;
        }

        try {
            String targetUrl = buildTargetUrl(matchedRoute, requestURI, request.getQueryString());
            HttpHeaders headers = buildHeaders(request);
            byte[] body = StreamUtils.copyToByteArray(request.getInputStream());
            HttpEntity<byte[]> httpEntity = new HttpEntity<>(body, headers);

            HttpMethod method = HttpMethod.valueOf(request.getMethod());
            ResponseEntity<String> downstreamResponse = restTemplate.exchange(targetUrl, method, httpEntity,
                    String.class);

            response.setStatus(downstreamResponse.getStatusCode().value());
            response.setCharacterEncoding("UTF-8");

            if (downstreamResponse.getHeaders() != null) {
                downstreamResponse.getHeaders().forEach((key, values) -> {
                    // 跳过 hop-by-hop 头部和 CORS 头（由 CorsFilter 统一处理）
                    String lowerKey = key.toLowerCase();
                    if (!lowerKey.equals("transfer-encoding") &&
                            !lowerKey.equals("connection") &&
                            !lowerKey.equals("keep-alive") &&
                            !lowerKey.startsWith("access-control-")) {
                        values.forEach(value -> response.addHeader(key, value));
                    }
                });
            }
            if (downstreamResponse.getBody() != null) {
                response.getWriter().write(downstreamResponse.getBody());
                response.getWriter().flush();
            }
        } catch (org.springframework.web.client.ResourceAccessException e) {
            // 连接超时/拒绝 - 快速失败，不记录完整堆栈
            if (e.getMessage().contains("Connection refused")) {
                log.warn("下游服务未启动：{} -> {}", requestURI, matchedRoute.getUri());
                sendErrorResponse(response, "服务暂时不可用，请稍后重试");
            } else if (e.getMessage().contains("Read timed out") || e.getMessage().contains("Connect timed out")) {
                log.warn("下游服务响应超时：{} -> {}", requestURI, matchedRoute.getUri());
                sendErrorResponse(response, "服务响应超时，请稍后重试");
            } else {
                log.error("代理转发失败（网络异常）：{}", requestURI);
                sendErrorResponse(response, "网关转发失败：网络异常");
            }
        } catch (Exception e) {
            // 其他异常 - 记录完整堆栈
            log.error("代理转发失败：{}", requestURI, e);
            sendErrorResponse(response, "网关转发失败：" + e.getMessage());
        }
    }

    private RouteProperties.Route findMatchedRoute(String requestURI) {
        if (routeProperties.getRoutes() == null)
            return null;
        for (RouteProperties.Route route : routeProperties.getRoutes()) {
            if (route.getPredicates() != null) {
                for (String predicate : route.getPredicates()) {
                    if (predicate.startsWith("Path=") && matchPath(requestURI, predicate.substring(5))) {
                        return route;
                    }
                }
            }
        }
        return null;
    }

    private boolean matchPath(String requestURI, String pathPattern) {
        if (pathPattern.endsWith("/**")) {
            return requestURI.startsWith(pathPattern.substring(0, pathPattern.length() - 3));
        }
        return requestURI.equals(pathPattern);
    }

    private String buildTargetUrl(RouteProperties.Route route, String requestURI, String queryString) {
        StringBuilder url = new StringBuilder(route.getUri()).append(requestURI);
        if (queryString != null && !queryString.isEmpty()) {
            url.append("?").append(queryString);
        }
        return url.toString();
    }

    private HttpHeaders buildHeaders(HttpServletRequest request) {
        HttpHeaders headers = new HttpHeaders();
        Enumeration<String> headerNames = request.getHeaderNames();
        if (headerNames != null) {
            while (headerNames.hasMoreElements()) {
                String name = headerNames.nextElement();
                Enumeration<String> values = request.getHeaders(name);
                if (values != null) {
                    while (values.hasMoreElements()) {
                        headers.add(name, values.nextElement());
                    }
                }
            }
        }

        String tenantId = (String) request.getAttribute("X-Tenant-Id");
        if (tenantId != null)
            headers.set("X-Tenant-Id", tenantId);

        String tenantType = (String) request.getAttribute("X-Tenant-Type");
        if (tenantType != null)
            headers.set("X-Tenant-Type", tenantType);

        String userId = (String) request.getAttribute("X-User-Id");
        if (userId != null)
            headers.set("X-User-Id", userId);

        return headers;
    }

    private void sendNotFoundResponse(HttpServletResponse response) throws IOException {
        response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":404,\"msg\":\"未找到匹配的路由\"}");
    }

    private void sendErrorResponse(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(String.format("{\"code\":500,\"msg\":\"%s\"}", message));
    }
}
