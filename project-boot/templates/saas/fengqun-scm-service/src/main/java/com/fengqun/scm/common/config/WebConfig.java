package com.fengqun.scm.common.config;

import java.util.Arrays;

import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import jakarta.servlet.Filter;

/**
 * Web 通用配置
 * 
 * 包含：CORS 跨域配置
 */
@Configuration
public class WebConfig {

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
        registration.setEnabled(true);
        return registration;
    }
}
