package com.your_group_name.your_project_name.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 角色权限关联表
 */
@Data
@TableName("sys_role_permission")
public class SysRolePermission {

    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;

    private String tenantId; // 租户ID
    private Long roleId; // 角色ID
    private Long permissionId; // 权限ID
    private LocalDateTime createdAt;
}
