package com.your_group_name.your_project_name.gateway.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 路由配置属性
 */
@Data
@Component
@ConfigurationProperties(prefix = "gateway")
public class RouteProperties {

    /**
     * 路由列表
     */
    private List<Route> routes;

    /**
     * 路由定义
     */
    @Data
    public static class Route {
        /**
         * 路由ID
         */
        private String id;

        /**
         * 目标服务 URI
         */
        private String uri;

        /**
         * 路径匹配规则
         */
        private List<String> predicates;

        /**
         * 是否去除路径前缀
         */
        private Boolean stripPrefix = false;

        /**
         * 是否需要认证
         */
        private Boolean authRequired = true;
    }
}
