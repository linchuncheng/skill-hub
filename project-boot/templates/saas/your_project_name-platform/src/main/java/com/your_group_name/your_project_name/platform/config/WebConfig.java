package com.your_group_name.your_project_name.platform.config;

import com.your_group_name.your_project_name.common.tenant.TenantInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC 配置
 *
 * 注意：CORS 由 Gateway 统一处理，此处不再配置
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new TenantInterceptor())
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/auth/**"); // 登录接口不需要租户拦截
    }
}
