package com.your_group_name.your_project_name.platform.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 角色列表响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RoleRespDTO {
    private Long id;
    private String tenantId;
    private String tenantName;
    private String roleCode;
    private String roleName;
    private Integer sort;
    private Integer status;
    private String createdAt;
    private String updatedAt;
}
