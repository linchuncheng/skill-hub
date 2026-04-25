package com.fengqun.scm.platform.dto;

import lombok.Data;

/**
 * 登录请求 DTO
 */
@Data
public class LoginReqDTO {
    private String username;
    private String password;
}
