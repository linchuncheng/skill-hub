package com.fengqun.scm.common.config;

import com.fengqun.scm.common.tenant.TenantInterceptor;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC 配置
 * 
 * 注册租户拦截器,从 HTTP Header 中提取租户信息并注入到 TenantContext
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    private final TenantInterceptor tenantInterceptor;

    public WebMvcConfig(TenantInterceptor tenantInterceptor) {
        this.tenantInterceptor = tenantInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 注册租户拦截器,拦截所有请求
        registry.addInterceptor(tenantInterceptor)
                .addPathPatterns("/**")
                .excludePathPatterns("/api/auth/**") // 认证接口不需要租户拦截
                .order(1); // 设置优先级,确保在其他拦截器之前执行
    }
}
