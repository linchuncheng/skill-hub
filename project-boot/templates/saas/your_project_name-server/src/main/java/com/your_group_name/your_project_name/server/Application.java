package com.your_group_name.your_project_name;

import org.apache.dubbo.config.spring.context.annotation.EnableDubbo;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 服务启动类
 */
@SpringBootApplication(scanBasePackages = { "com.your_group_name.your_project_name.server" })
@MapperScan("com.your_group_name.your_project_name.server.mapper")
@EnableScheduling
@EnableDubbo
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
