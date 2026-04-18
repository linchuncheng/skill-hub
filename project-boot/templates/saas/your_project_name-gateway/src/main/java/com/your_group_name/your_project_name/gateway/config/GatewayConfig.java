package com.your_group_name.your_project_name.gateway.config;

import java.time.Duration;
import java.util.Arrays;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import jakarta.servlet.Filter;

/**
 * 网关配置
 */
@Configuration
public class GatewayConfig {

    /**
     * RestTemplate（用于代理转发）
     */
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofMillis(3000)) // 3秒连接超时
                .setReadTimeout(Duration.ofMillis(10000)) // 10秒读取超时
                .build();
    }

    /**
     * CORS 过滤器 - 使用 FilterRegistrationBean 注册，避免重复
     */
    @Bean
    public FilterRegistrationBean<Filter> corsFilterRegistration() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOriginPatterns(Arrays.asList("*"));
        config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(Arrays.asList("*"));
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);

        FilterRegistrationBean<Filter> registration = new FilterRegistrationBean<>(new CorsFilter(source));
        registration.setOrder(Integer.MIN_VALUE); // 最高优先级
        registration.setName("corsFilter");
        // 禁用 Spring Boot 的默认 CORS Filter
        registration.setEnabled(true);
        return registration;
    }
}
