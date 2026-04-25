package com.fengqun.scm.platform.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 用户列表响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserRespDTO {
    private Long id;
    private String tenantId;
    private String tenantName;
    private String username;
    private String realName;
    private String avatar;
    private String phone;
    private String email;
    private String remark;
    private String tenantType;
    private Integer status;
    private String createdAt;
    private String updatedAt;
    private String roles; // 已分配角色名称，逗号分隔
}
