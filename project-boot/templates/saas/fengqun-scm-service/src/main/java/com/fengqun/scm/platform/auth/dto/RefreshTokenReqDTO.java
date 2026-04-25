package com.fengqun.scm.platform.auth.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

/**
 * 刷新Token请求 DTO
 */
@Data
public class RefreshTokenReqDTO {

    /**
     * 刷新令牌
     */
    @JsonProperty("refresh_token")
    private String refreshToken;
}
