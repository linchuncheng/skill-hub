package com.your_group_name.your_project_name.auth.dto;

import lombok.Data;

/**
 * 刷新Token请求 DTO
 */
@Data
public class RefreshTokenReqDTO {

    /**
     * 刷新令牌
     */
    private String refreshToken;
}
