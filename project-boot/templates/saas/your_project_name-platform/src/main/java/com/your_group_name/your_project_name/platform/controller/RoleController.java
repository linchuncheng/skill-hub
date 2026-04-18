package com.your_group_name.your_project_name.platform.controller;

import com.your_group_name.your_project_name.common.base.BaseController;
import com.your_group_name.your_project_name.common.response.R;
import com.your_group_name.your_project_name.platform.dto.DefaultPermissionsDTO;
import com.your_group_name.your_project_name.platform.dto.RoleRespDTO;
import com.your_group_name.your_project_name.platform.entity.SysRole;
import com.your_group_name.your_project_name.platform.service.RoleService;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/platform/role")
public class RoleController extends BaseController {

    @Autowired
    private RoleService roleService;

    @GetMapping("/list")
    public R<List<RoleRespDTO>> listRoles(@RequestParam(required = false) String tenantId) {
        if (tenantId != null && !tenantId.isEmpty()) {
            return success(roleService.listRolesByTenantId(tenantId));
        }
        return success(roleService.listRoles());
    }

    @PostMapping
    public R<Long> createRole(@RequestBody SysRole role) {
        return success(roleService.createRole(role));
    }

    @PutMapping
    public R<Void> updateRole(@RequestBody SysRole role) {
        roleService.updateRole(role);
        return success();
    }

    @DeleteMapping("/{id}")
    public R<Void> deleteRole(@PathVariable Long id) {
        roleService.deleteRole(id);
        return success();
    }

    @PutMapping("/{id}/enable")
    public R<Void> enableRole(@PathVariable Long id) {
        roleService.enableRole(id);
        return success();
    }

    @PutMapping("/{id}/disable")
    public R<Void> disableRole(@PathVariable Long id) {
        roleService.disableRole(id);
        return success();
    }

    @PostMapping("/permission/assign")
    public R<Void> assignPermissions(@RequestBody Map<String, Object> params) {
        Long roleId = Long.valueOf(params.get("roleId").toString());
        @SuppressWarnings("unchecked")
        List<Long> permissionIds = ((List<?>) params.get("permissionIds")).stream()
                .map(obj -> Long.valueOf(obj.toString()))
                .toList();
        roleService.assignPermissions(roleId, permissionIds);
        return success();
    }

    @GetMapping("/{roleId}/permissions")
    public R<List<Long>> getRolePermissions(@PathVariable Long roleId) {
        return success(roleService.getPermissionIdsByRoleId(roleId));
    }

    @PostMapping("/menu/assign")
    public R<Void> assignMenus(@RequestBody Map<String, Object> params) {
        Long roleId = Long.valueOf(params.get("roleId").toString());
        @SuppressWarnings("unchecked")
        List<Long> menuIds = ((List<?>) params.get("menuIds")).stream()
                .map(obj -> Long.valueOf(obj.toString()))
                .toList();
        roleService.assignMenus(roleId, menuIds);
        return success();
    }

    @GetMapping("/{roleId}/menus")
    public R<List<Long>> getRoleMenus(@PathVariable Long roleId) {
        return success(roleService.getMenuIdsByRoleId(roleId));
    }

    /**
     * 获取角色的默认权限配置
     * 用于前端分配权限时显示禁用勾选
     */
    @GetMapping("/{roleId}/default-permissions")
    public R<DefaultPermissionsDTO> getDefaultPermissions(@PathVariable Long roleId) {
        return success(roleService.getDefaultPermissions(roleId));
    }
}
