package com.your_group_name.your_project_name.platform.dto;

import java.util.List;

import lombok.Data;

/**
 * 角色默认权限配置 DTO
 * 用于返回某个角色类型默认拥有的菜单和权限（这些在分配时显示为禁用勾选）
 */
@Data
public class DefaultPermissionsDTO {
    /**
     * 默认拥有的菜单 ID 列表（显示为已勾选且禁用）
     */
    private List<Long> defaultMenuIds;

    /**
     * 默认拥有的权限 ID 列表（显示为已勾选且禁用）
     */
    private List<Long> defaultPermissionIds;

    /**
     * 禁止分配的菜单 ID 列表（不显示或完全禁用，如：租户管理、菜单管理）
     */
    private List<Long> forbiddenMenuIds;

    /**
     * 禁止分配的权限 ID 列表（不显示或完全禁用）
     */
    private List<Long> forbiddenPermissionIds;
}
