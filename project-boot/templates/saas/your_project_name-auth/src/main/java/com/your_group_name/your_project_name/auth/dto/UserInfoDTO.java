package com.your_group_name.your_project_name.auth.dto;

import lombok.Data;

import java.util.List;

/**
 * 用户信息 DTO
 */
@Data
public class UserInfoDTO {

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 用户名
     */
    private String username;

    /**
     * 真实姓名
     */
    private String realName;

    /**
     * 头像
     */
    private String avatar;

    /**
     * 手机号
     */
    private String phone;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 用户类型：PLATFORM=平台用户，TENANT=租户用户
     */
    private String tenantType;

    /**
     * 角色列表
     */
    private List<String> roles;
}
