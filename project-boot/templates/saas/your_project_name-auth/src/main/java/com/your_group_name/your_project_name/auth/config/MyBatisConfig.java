package com.your_group_name.your_project_name.auth.config;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis-Plus 配置类
 */
@Configuration
@MapperScan("com.your_group_name.your_project_name.auth.mapper")
public class MyBatisConfig {
}
