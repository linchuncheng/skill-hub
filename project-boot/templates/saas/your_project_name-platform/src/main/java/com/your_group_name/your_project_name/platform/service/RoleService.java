package com.your_group_name.your_project_name.platform.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.your_group_name.your_project_name.platform.dto.DefaultPermissionsDTO;
import com.your_group_name.your_project_name.platform.dto.RoleRespDTO;
import com.your_group_name.your_project_name.platform.entity.SysRole;

import java.util.List;

public interface RoleService extends IService<SysRole> {
    List<RoleRespDTO> listRoles();

    /**
     * 根据租户ID查询角色列表（超级管理员使用）
     */
    List<RoleRespDTO> listRolesByTenantId(String tenantId);

    Long createRole(SysRole role);

    void updateRole(SysRole role);

    void deleteRole(Long id);

    void enableRole(Long id);

    void disableRole(Long id);

    void assignPermissions(Long roleId, List<Long> permissionIds);

    List<Long> getPermissionIdsByRoleId(Long roleId);

    void assignMenus(Long roleId, List<Long> menuIds);

    List<Long> getMenuIdsByRoleId(Long roleId);

    /**
     * 获取角色的默认权限配置
     * 根据角色的 tenantId 和 roleCode 决定默认拥有的菜单和权限
     * 规则：
     * - PLATFORM 角色（roleCode='SUPER_ADMIN'）：无默认禁用
     * - PLATFORM_USER 角色（tenantId='0'）：首页默认
     * - TENANT 角色（tenantId!='0'）：首页、用户管理、角色管理默认
     */
    DefaultPermissionsDTO getDefaultPermissions(Long roleId);
}
