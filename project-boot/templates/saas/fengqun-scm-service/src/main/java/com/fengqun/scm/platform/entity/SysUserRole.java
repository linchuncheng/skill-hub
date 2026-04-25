package com.fengqun.scm.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户角色关联表
 */
@Data
@TableName("sys_user_role")
public class SysUserRole {

    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;

    private String tenantId; // 租户ID
    private Long userId; // 用户ID
    private Long roleId; // 角色ID
    private LocalDateTime createdAt;
}
