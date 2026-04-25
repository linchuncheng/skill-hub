package com.fengqun.scm.platform.service;

import java.util.List;
import java.util.Map;

/**
 * 权限服务接口
 */
public interface PermissionService {

    /**
     * 查询权限树形结构
     */
    List<Map<String, Object>> buildPermissionTree();

    /**
     * 查询权限树形结构（用于权限分配）
     * 返回所有权限，并标记角色已拥有的权限
     * 
     * @param roleId 角色ID
     */
    List<Map<String, Object>> buildPermissionTreeForAssign(Long roleId);

    /**
     * 根据角色ID查询权限树
     */
    List<Map<String, Object>> getPermissionsByRoleId(Long roleId);
}
