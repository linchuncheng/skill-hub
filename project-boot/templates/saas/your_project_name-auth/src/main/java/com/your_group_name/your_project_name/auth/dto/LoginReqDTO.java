package com.your_group_name.your_project_name.auth.dto;

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
