package com.fengqun.scm.platform.controller;

import com.fengqun.scm.common.base.BaseController;
import com.fengqun.scm.common.response.R;
import com.fengqun.scm.platform.service.PermissionService;

import java.util.List;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

/**
 * 权限 Controller
 */
@RestController
@RequestMapping("/api/platform/permission")
@RequiredArgsConstructor
public class PermissionController extends BaseController {

    private final PermissionService permissionService;

    /**
     * 查询权限树
     */
    @GetMapping("/tree")
    public R<List<Map<String, Object>>> buildPermissionTree() {
        return success(permissionService.buildPermissionTree());
    }

    /**
     * 查询权限树（用于权限分配）
     * 返回所有权限，并标记角色已拥有的权限
     */
    @GetMapping("/tree/assign")
    public R<List<Map<String, Object>>> buildPermissionTreeForAssign(Long roleId) {
        return success(permissionService.buildPermissionTreeForAssign(roleId));
    }

    /**
     * 根据角色ID查询权限树
     */
    @GetMapping("/role/{roleId}")
    public R<List<Map<String, Object>>> getPermissionsByRoleId(@PathVariable Long roleId) {
        return success(permissionService.getPermissionsByRoleId(roleId));
    }
}
