package com.your_group_name.your_project_name.gateway.security;

import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

import javax.crypto.SecretKey;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;

/**
 * JWT Token 工具类。
 *
 * 提供 Token 的生成、解析和验证功能。
 */
@Slf4j
public class TokenKit {

    /**
     * 生成 JWT Token。
     *
     * @param subject          主题（通常是用户ID）
     * @param claims           自定义声明
     * @param expirationMillis 过期时间（毫秒）
     * @param secretKey        密钥
     * @return JWT Token
     */
    public static String generateToken(String subject, Map<String, Object> claims, long expirationMillis,
            String secretKey) {
        Date now = new Date();
        Date expiration = new Date(now.getTime() + expirationMillis);

        SecretKey key = Keys.hmacShaKeyFor(secretKey.getBytes(StandardCharsets.UTF_8));

        return Jwts.builder()
                .subject(subject)
                .claims(claims)
                .issuedAt(now)
                .expiration(expiration)
                .signWith(key)
                .compact();
    }

    /**
     * 解析 JWT Token。
     *
     * @param token     JWT Token
     * @param secretKey 密钥
     * @return Claims（失败返回 null）
     */
    public static Claims parseToken(String token, String secretKey) {
        try {
            SecretKey key = Keys.hmacShaKeyFor(secretKey.getBytes(StandardCharsets.UTF_8));
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (Exception e) {
            log.warn("Token 解析失败：{}", e.getMessage());
            return null;
        }
    }

    /**
     * 验证 Token 是否有效。
     *
     * @param token     JWT Token
     * @param secretKey 密钥
     * @return true=有效，false=无效
     */
    public static boolean validateToken(String token, String secretKey) {
        try {
            Claims claims = parseToken(token, secretKey);
            if (claims == null) {
                return false;
            }
            // 检查是否过期
            Date expiration = claims.getExpiration();
            return expiration != null && expiration.after(new Date());
        } catch (Exception e) {
            log.warn("Token 验证失败：{}", e.getMessage());
            return false;
        }
    }
}
