package com.fengqun.scm.platform.auth.dto;

import java.util.List;

import lombok.Data;

/**
 * 登录响应 DTO
 */
@Data
public class LoginRespDTO {

    /**
     * 访问令牌（2小时）
     */
    private String accessToken;

    /**
     * 刷新令牌（7天）
     */
    private String refreshToken;

    /**
     * 用户信息
     */
    private UserInfoDTO userInfo;

    /**
     * 权限码列表
     */
    private List<String> permissions;

    /**
     * 菜单树
     */
    private List<MenuDTO> menus;
}
