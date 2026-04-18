package com.your_group_name.your_project_name.platform.dto;

import lombok.Data;

/**
 * 登录请求 DTO
 */
@Data
public class LoginReqDTO {
    private String username;
    private String password;
}
