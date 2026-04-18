package com.your_group_name.your_project_name.platform;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 平台管理核心服务启动类
 */
@SpringBootApplication(scanBasePackages = { "com.your_group_name.your_project_name" })
@MapperScan("com.your_group_name.your_project_name.platform.mapper")
public class PlatformApplication {
    public static void main(String[] args) {
        SpringApplication.run(PlatformApplication.class, args);
    }
}
