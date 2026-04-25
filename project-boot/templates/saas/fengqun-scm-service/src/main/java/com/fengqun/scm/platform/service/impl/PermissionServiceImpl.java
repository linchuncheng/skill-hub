package com.fengqun.scm.platform.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fengqun.scm.platform.entity.SysPermission;
import com.fengqun.scm.platform.mapper.SysPermissionMapper;
import com.fengqun.scm.platform.service.PermissionService;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 权限服务实现
 */
@Service
public class PermissionServiceImpl extends ServiceImpl<SysPermissionMapper, SysPermission>
        implements PermissionService {

    @Autowired
    private SysPermissionMapper permissionMapper;

    @Override
    public List<Map<String, Object>> buildPermissionTree() {
        List<SysPermission> permissions = permissionMapper.selectAllEnabledPermissions();
        return buildTree(permissions, 0L);
    }

    @Override
    public List<Map<String, Object>> buildPermissionTreeForAssign(Long roleId) {
        // 查询角色已有的权限
        List<SysPermission> rolePermissions = permissionMapper.selectPermissionsByRoleId(roleId);

        // 查询所有可用权限
        List<SysPermission> allPermissions = permissionMapper.selectAllEnabledPermissions();

        // 构建权限树，标记角色已拥有的权限
        return buildTreeWithChecked(allPermissions, rolePermissions, 0L);
    }

    @Override
    public List<Map<String, Object>> getPermissionsByRoleId(Long roleId) {
        List<SysPermission> permissions = permissionMapper.selectPermissionsByRoleId(roleId);
        return buildTree(permissions, 0L);
    }

    /**
     * 构建权限树
     */
    private List<Map<String, Object>> buildTree(List<SysPermission> permissions, Long parentId) {
        return permissions.stream()
                .filter(p -> parentId.equals(p.getParentId() != null ? p.getParentId() : 0L))
                .map(p -> {
                    Map<String, Object> node = new HashMap<>();
                    node.put("id", p.getId().toString());
                    node.put("parentId", p.getParentId() != null ? p.getParentId().toString() : "0");
                    node.put("permissionCode", p.getPermissionCode());
                    node.put("permissionName", p.getPermissionName());
                    node.put("resourceType", p.getResourceType());
                    node.put("sort", p.getSort());
                    node.put("status", p.getStatus() == 1);

                    List<Map<String, Object>> children = buildTree(permissions, p.getId());
                    if (!children.isEmpty()) {
                        node.put("children", children);
                    }
                    return node;
                })
                .collect(Collectors.toList());
    }

    /**
     * 构建权限树，并标记角色已拥有的权限
     */
    private List<Map<String, Object>> buildTreeWithChecked(List<SysPermission> allPermissions,
            List<SysPermission> rolePermissions,
            Long parentId) {
        // 角色已拥有的权限 ID 集合
        java.util.Set<Long> checkedIds = rolePermissions.stream()
                .map(SysPermission::getId)
                .collect(java.util.stream.Collectors.toSet());

        return allPermissions.stream()
                .filter(p -> parentId.equals(p.getParentId() != null ? p.getParentId() : 0L))
                .map(p -> {
                    Map<String, Object> node = new HashMap<>();
                    node.put("id", p.getId().toString());
                    node.put("parentId", p.getParentId() != null ? p.getParentId().toString() : "0");
                    node.put("permissionCode", p.getPermissionCode());
                    node.put("permissionName", p.getPermissionName());
                    node.put("resourceType", p.getResourceType());
                    node.put("sort", p.getSort());
                    node.put("status", p.getStatus() == 1);
                    node.put("checked", checkedIds.contains(p.getId())); // 标记是否已选中

                    List<Map<String, Object>> children = buildTreeWithChecked(allPermissions, rolePermissions,
                            p.getId());
                    if (!children.isEmpty()) {
                        node.put("children", children);
                    }
                    return node;
                })
                .collect(Collectors.toList());
    }
}
