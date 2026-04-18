package com.your_group_name.your_project_name.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.your_group_name.your_project_name.common.tenant.TenantConstants;
import com.your_group_name.your_project_name.common.tenant.TenantContext;
import com.your_group_name.your_project_name.platform.dto.DefaultPermissionsDTO;
import com.your_group_name.your_project_name.platform.dto.RoleRespDTO;
import com.your_group_name.your_project_name.platform.entity.SysMenu;
import com.your_group_name.your_project_name.platform.entity.SysPermission;
import com.your_group_name.your_project_name.platform.entity.SysRole;
import com.your_group_name.your_project_name.platform.entity.SysRoleMenu;
import com.your_group_name.your_project_name.platform.entity.SysRolePermission;
import com.your_group_name.your_project_name.platform.entity.SysTenant;
import com.your_group_name.your_project_name.platform.mapper.SysMenuMapper;
import com.your_group_name.your_project_name.platform.mapper.SysPermissionMapper;
import com.your_group_name.your_project_name.platform.mapper.SysRoleMapper;
import com.your_group_name.your_project_name.platform.mapper.SysRoleMenuMapper;
import com.your_group_name.your_project_name.platform.mapper.SysRolePermissionMapper;
import com.your_group_name.your_project_name.platform.mapper.SysTenantMapper;
import com.your_group_name.your_project_name.platform.mapper.SysUserRoleMapper;
import com.your_group_name.your_project_name.platform.service.RoleService;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class RoleServiceImpl extends ServiceImpl<SysRoleMapper, SysRole> implements RoleService {

    @Autowired
    private SysRolePermissionMapper rolePermissionMapper;

    @Autowired
    private SysRoleMenuMapper roleMenuMapper;

    @Autowired
    private SysTenantMapper tenantMapper;

    @Autowired
    private SysMenuMapper menuMapper;

    @Autowired
    private SysPermissionMapper permissionMapper;

    @Autowired
    private SysUserRoleMapper userRoleMapper;

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 将 SysRole 转换为 RoleRespDTO
     */
    private RoleRespDTO convertToDTO(SysRole role, Map<Long, SysTenant> tenantMap) {
        String tenantName = null;
        if (role.getTenantId() != null) {
            // tenant_id='0' 表示平台角色
            if ("0".equals(role.getTenantId())) {
                tenantName = "平台";
            } else {
                // tenantId 是 String，需要转换为 Long 查询
                try {
                    Long tenantIdLong = Long.valueOf(role.getTenantId());
                    SysTenant tenant = tenantMap.get(tenantIdLong);
                    if (tenant != null) {
                        // tenant_code 为 "default" 表示平台
                        tenantName = "default".equals(tenant.getTenantCode()) ? "平台" : tenant.getTenantName();
                    } else {
                        // 如果租户不在tenantMap中，单独查询判断是否为平台租户
                        SysTenant singleTenant = tenantMapper.selectById(tenantIdLong);
                        if (singleTenant != null && "default".equals(singleTenant.getTenantCode())) {
                            tenantName = "平台";
                        }
                    }
                } catch (NumberFormatException e) {
                    tenantName = null;
                }
            }
        }

        return RoleRespDTO.builder()
                .id(role.getId())
                .tenantId(role.getTenantId())
                .tenantName(tenantName)
                .roleCode(role.getRoleCode())
                .roleName(role.getRoleName())
                .sort(role.getSort())
                .status(role.getStatus())
                .createdAt(role.getCreatedAt() != null ? role.getCreatedAt().format(DATE_FORMATTER) : null)
                .updatedAt(role.getUpdatedAt() != null ? role.getUpdatedAt().format(DATE_FORMATTER) : null)
                .build();
    }

    @Override
    public List<RoleRespDTO> listRoles() {
        List<SysRole> roles = this.list();
        // 批量查询租户信息 - 将 String tenantId 转为 Long
        List<Long> tenantIds = roles.stream()
                .map(SysRole::getTenantId)
                .filter(id -> id != null && !id.isEmpty())
                .map(Long::valueOf)
                .distinct()
                .collect(Collectors.toList());

        // 如果租户ID列表为空，直接返回转换后的结果（不查询租户表）
        if (tenantIds.isEmpty()) {
            return roles.stream()
                    .map(role -> convertToDTO(role, java.util.Collections.emptyMap()))
                    .collect(Collectors.toList());
        }

        Map<Long, SysTenant> tenantMap = tenantMapper.selectList(
                new LambdaQueryWrapper<SysTenant>().in(SysTenant::getId, tenantIds)).stream()
                .collect(Collectors.toMap(SysTenant::getId, t -> t, (t1, t2) -> t1));

        return roles.stream()
                .map(role -> convertToDTO(role, tenantMap))
                .collect(Collectors.toList());
    }

    @Override
    public List<RoleRespDTO> listRolesByTenantId(String tenantId) {
        List<SysRole> roles;
        if (tenantId == null || tenantId.isEmpty()) {
            roles = this.list();
        } else {
            roles = this.list(new LambdaQueryWrapper<SysRole>()
                    .eq(SysRole::getTenantId, tenantId));
        }
        // 批量查询租户信息
        List<Long> tenantIds = roles.stream()
                .map(SysRole::getTenantId)
                .filter(id -> id != null && !id.isEmpty())
                .map(Long::valueOf)
                .distinct()
                .collect(Collectors.toList());

        // 如果租户ID列表为空，直接返回转换后的结果（不查询租户表）
        if (tenantIds.isEmpty()) {
            return roles.stream()
                    .map(role -> convertToDTO(role, java.util.Collections.emptyMap()))
                    .collect(Collectors.toList());
        }

        Map<Long, SysTenant> tenantMap = tenantMapper.selectList(
                new LambdaQueryWrapper<SysTenant>().in(SysTenant::getId, tenantIds)).stream()
                .collect(Collectors.toMap(SysTenant::getId, t -> t, (t1, t2) -> t1));

        return roles.stream()
                .map(role -> convertToDTO(role, tenantMap))
                .collect(Collectors.toList());
    }

    @Override
    public Long createRole(SysRole role) {
        role.setStatus(1);
        // 如果没有指定租户ID，默认使用当前上下文的租户ID或平台租户ID
        if (role.getTenantId() == null || role.getTenantId().isEmpty()) {
            String tenantId = TenantContext.getTenantId();
            if (tenantId != null) {
                role.setTenantId(tenantId);
            } else {
                // 查询平台租户（tenant_code='default'）的 ID
                SysTenant platformTenant = tenantMapper.selectOne(
                        new LambdaQueryWrapper<SysTenant>().eq(SysTenant::getTenantCode,
                                TenantConstants.PLATFORM_TENANT_CODE));
                if (platformTenant != null) {
                    role.setTenantId(String.valueOf(platformTenant.getId()));
                }
            }
        }
        this.save(role);
        return role.getId();
    }

    @Override
    public void updateRole(SysRole role) {
        this.updateById(role);
    }

    @Override
    public void deleteRole(Long id) {
        // 删除角色关联的权限
        rolePermissionMapper.deleteByRoleId(id);
        // 删除角色关联的菜单
        roleMenuMapper.deleteByRoleId(id);
        // 删除用户与角色的关联
        userRoleMapper.deleteByRoleId(id);
        // 删除角色本身
        this.removeById(id);
    }

    @Override
    public void enableRole(Long id) {
        SysRole role = this.getById(id);
        if (role != null) {
            role.setStatus(1);
            this.updateById(role);
        }
    }

    @Override
    public void disableRole(Long id) {
        SysRole role = this.getById(id);
        if (role != null) {
            role.setStatus(0);
            this.updateById(role);
        }
    }

    @Override
    public void assignPermissions(Long roleId, List<Long> permissionIds) {
        // 删除该角色已有的所有权限关联
        rolePermissionMapper.deleteByRoleId(roleId);

        // 从角色表中获取租户ID(而不是当前登录用户的租户ID)
        // 这样可以支持超级管理员代为初始化租户数据的场景
        SysRole role = this.getById(roleId);
        if (role == null) {
            throw new IllegalArgumentException("角色不存在: " + roleId);
        }
        String tenantId = role.getTenantId();

        // 添加新的权限关联
        if (permissionIds != null && !permissionIds.isEmpty()) {
            for (Long permissionId : permissionIds) {
                SysRolePermission rolePermission = new SysRolePermission();
                rolePermission.setTenantId(tenantId);
                rolePermission.setRoleId(roleId);
                rolePermission.setPermissionId(permissionId);
                rolePermissionMapper.insert(rolePermission);
            }
        }
    }

    @Override
    public List<Long> getPermissionIdsByRoleId(Long roleId) {
        return rolePermissionMapper.selectPermissionIdsByRoleId(roleId);
    }

    @Override
    public void assignMenus(Long roleId, List<Long> menuIds) {
        // 删除该角色已有的所有菜单关联
        roleMenuMapper.deleteByRoleId(roleId);

        // 从角色表中获取租户ID(而不是当前登录用户的租户ID)
        // 这样可以支持超级管理员代为初始化租户数据的场景
        SysRole role = this.getById(roleId);
        if (role == null) {
            throw new IllegalArgumentException("角色不存在: " + roleId);
        }
        String tenantId = role.getTenantId();

        // 添加新的菜单关联
        if (menuIds != null && !menuIds.isEmpty()) {
            for (Long menuId : menuIds) {
                SysRoleMenu roleMenu = new SysRoleMenu();
                roleMenu.setTenantId(tenantId);
                roleMenu.setRoleId(roleId);
                roleMenu.setMenuId(menuId);
                roleMenuMapper.insert(roleMenu);
            }
        }
    }

    @Override
    public List<Long> getMenuIdsByRoleId(Long roleId) {
        return roleMenuMapper.selectMenuIdsByRoleId(roleId);
    }

    /**
     * 获取角色的默认权限配置
     * 基于 permissionCode 前缀匹配，而非硬编码 ID
     */
    @Override
    public DefaultPermissionsDTO getDefaultPermissions(Long roleId) {
        DefaultPermissionsDTO dto = new DefaultPermissionsDTO();
        List<Long> defaultMenuIds = new ArrayList<>();
        List<Long> defaultPermissionIds = new ArrayList<>();
        List<Long> forbiddenMenuIds = new ArrayList<>();
        List<Long> forbiddenPermissionIds = new ArrayList<>();

        // 查询角色信息
        SysRole role = this.getById(roleId);
        if (role == null) {
            dto.setDefaultMenuIds(defaultMenuIds);
            dto.setDefaultPermissionIds(defaultPermissionIds);
            dto.setForbiddenMenuIds(forbiddenMenuIds);
            dto.setForbiddenPermissionIds(forbiddenPermissionIds);
            return dto;
        }

        // 通过 tenantId 查询租户的 tenant_code
        String tenantCode = null;
        if (role.getTenantId() != null && !role.getTenantId().isEmpty()) {
            try {
                SysTenant tenant = tenantMapper.selectById(Long.valueOf(role.getTenantId()));
                if (tenant != null) {
                    tenantCode = tenant.getTenantCode();
                }
            } catch (NumberFormatException e) {
                // 忽略转换错误
            }
        }

        // 超级管理员角色：无默认禁用（通过 tenant_code == 'default' 判断）
        if (TenantConstants.isPlatformTenant(tenantCode) && "SUPER_ADMIN".equals(role.getRoleCode())) {
            dto.setDefaultMenuIds(defaultMenuIds);
            dto.setDefaultPermissionIds(defaultPermissionIds);
            dto.setForbiddenMenuIds(forbiddenMenuIds);
            dto.setForbiddenPermissionIds(forbiddenPermissionIds);
            return dto;
        }

        // 查询所有菜单和权限
        List<SysMenu> allMenus = menuMapper.selectAllEnabledMenus();
        List<SysPermission> allPermissions = permissionMapper.selectAllEnabledPermissions();

        // 所有角色（除平台超管外）：首页隐藏（登录后默认有，不需要分配）
        for (SysMenu menu : allMenus) {
            String path = menu.getMenuPath();
            String permCode = menu.getPermissionCode();
            // 首页菜单 - 隐藏
            if ("/dashboard".equals(path) || "dashboard".equals(path) ||
                    "platform:dashboard:view".equals(permCode)) {
                forbiddenMenuIds.add(menu.getId());
            }
        }
        for (SysPermission perm : allPermissions) {
            String permCode = perm.getPermissionCode();
            // 首页权限 - 隐藏
            if (permCode != null && (permCode.startsWith("platform:dashboard:") ||
                    "platform:dashboard:view".equals(permCode))) {
                forbiddenPermissionIds.add(perm.getId());
            }
        }

        // 租户角色的特殊处理(通过 tenant_code != 'default' 判断)
        if (tenantCode != null && !TenantConstants.isPlatformTenant(tenantCode)) {
            for (SysMenu menu : allMenus) {
                String permCode = menu.getPermissionCode();
                String path = menu.getMenuPath();

                // 系统管理父菜单 - 默认已有(不需要分配)
                if ("/system".equals(path) || "system".equals(path)) {
                    defaultMenuIds.add(menu.getId());
                }

                // 用户管理、角色管理菜单 - 默认已有(不需要分配)
                if (permCode != null
                        && (permCode.startsWith("platform:user:") || permCode.startsWith("platform:role:"))) {
                    defaultMenuIds.add(menu.getId());
                }

                // 租户管理、菜单管理 - 禁止分配(租户管理员无权操作)
                if (permCode != null
                        && (permCode.startsWith("platform:tenant:") || permCode.startsWith("platform:menu:"))) {
                    forbiddenMenuIds.add(menu.getId());
                }
            }

            for (SysPermission perm : allPermissions) {
                String permCode = perm.getPermissionCode();

                // 用户管理、角色管理权限 - 默认已有(不需要分配)
                if (permCode != null
                        && (permCode.startsWith("platform:user:") || permCode.startsWith("platform:role:"))) {
                    defaultPermissionIds.add(perm.getId());
                }

                // 租户管理、菜单管理权限 - 禁止分配
                if (permCode != null
                        && (permCode.startsWith("platform:tenant:") || permCode.startsWith("platform:menu:"))) {
                    forbiddenPermissionIds.add(perm.getId());
                }
            }
        } else if (tenantCode != null && TenantConstants.isPlatformTenant(tenantCode)) {
            // 平台角色(非超管)给租户角色分配权限时
            // 也需要处理系统管理相关(用户管理、角色管理)
            for (SysMenu menu : allMenus) {
                String permCode = menu.getPermissionCode();
                String path = menu.getMenuPath();

                // 系统管理父菜单 - 默认已有
                if ("/system".equals(path) || "system".equals(path)) {
                    defaultMenuIds.add(menu.getId());
                }

                // 用户管理、角色管理菜单 - 默认已有
                if (permCode != null
                        && (permCode.startsWith("platform:user:") || permCode.startsWith("platform:role:"))) {
                    defaultMenuIds.add(menu.getId());
                }
            }

            for (SysPermission perm : allPermissions) {
                String permCode = perm.getPermissionCode();

                // 用户管理、角色管理权限 - 默认已有
                if (permCode != null
                        && (permCode.startsWith("platform:user:") || permCode.startsWith("platform:role:"))) {
                    defaultPermissionIds.add(perm.getId());
                }
            }
        }

        dto.setDefaultMenuIds(defaultMenuIds);
        dto.setDefaultPermissionIds(defaultPermissionIds);
        dto.setForbiddenMenuIds(forbiddenMenuIds);
        dto.setForbiddenPermissionIds(forbiddenPermissionIds);
        return dto;
    }
}
