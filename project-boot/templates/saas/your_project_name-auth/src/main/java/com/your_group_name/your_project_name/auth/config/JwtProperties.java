package com.your_group_name.your_project_name.auth.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * JWT 配置属性
 */
@Data
@Component
@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {

    /**
     * JWT 签名密钥
     */
    private String secret;

    /**
     * Access Token 过期时间（毫秒）
     */
    private Long accessTokenExpiration;

    /**
     * Refresh Token 过期时间（毫秒）
     */
    private Long refreshTokenExpiration;
}
