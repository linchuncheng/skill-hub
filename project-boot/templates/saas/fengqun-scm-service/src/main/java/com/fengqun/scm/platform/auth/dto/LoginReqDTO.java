package com.fengqun.scm.platform.auth.dto;

import lombok.Data;

/**
 * 登录请求 DTO
 */
@Data
public class LoginReqDTO {

    /**
     * 用户名
     */
    private String username;

    /**
     * 密码
     */
    private String password;
}
