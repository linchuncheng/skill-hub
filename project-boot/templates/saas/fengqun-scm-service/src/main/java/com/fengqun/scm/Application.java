package com.fengqun.scm;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 平台管理核心服务启动类
 */
@SpringBootApplication(scanBasePackages = { "com.fengqun.scm" })
@MapperScan({ "com.fengqun.scm.**.mapper" })
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
