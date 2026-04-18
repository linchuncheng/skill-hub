package com.your_group_name.your_project_name.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.your_group_name.your_project_name.common.base.BaseEntity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 权限实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_permission")
public class SysPermission extends BaseEntity {

    private Long parentId; // 父权限ID
    private String permissionCode; // 权限编码
    private String permissionName; // 权限名称
    private String resourceType; // 资源类型（MENU/BUTTON）
    private Integer sort; // 排序
    private Integer status; // 状态（1-启用，0-禁用）
}
