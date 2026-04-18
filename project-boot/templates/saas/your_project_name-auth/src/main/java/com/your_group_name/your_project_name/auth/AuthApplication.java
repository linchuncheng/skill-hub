package com.your_group_name.your_project_name.auth;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 认证服务启动类
 */
@SpringBootApplication(scanBasePackages = { "com.your_group_name.your_project_name.auth",
        "com.your_group_name.your_project_name.common" })
public class AuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(AuthApplication.class, args);
    }
}
