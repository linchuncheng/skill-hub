package com.your_group_name.your_project_name.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.your_group_name.your_project_name.common.tenant.TenantConstants;
import com.your_group_name.your_project_name.common.tenant.TenantContext;
import com.your_group_name.your_project_name.platform.dto.UserRespDTO;
import com.your_group_name.your_project_name.platform.entity.SysRole;
import com.your_group_name.your_project_name.platform.entity.SysTenant;
import com.your_group_name.your_project_name.platform.entity.SysUser;
import com.your_group_name.your_project_name.platform.entity.SysUserRole;
import com.your_group_name.your_project_name.platform.mapper.SysRoleMapper;
import com.your_group_name.your_project_name.platform.mapper.SysTenantMapper;
import com.your_group_name.your_project_name.platform.mapper.SysUserMapper;
import com.your_group_name.your_project_name.platform.mapper.SysUserRoleMapper;
import com.your_group_name.your_project_name.platform.service.UserService;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements UserService {

    @Autowired
    private SysUserRoleMapper userRoleMapper;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private SysTenantMapper tenantMapper;

    @Autowired
    private SysRoleMapper roleMapper;

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 将 SysUser 转换为 UserRespDTO
     */
    private UserRespDTO convertToDTO(SysUser user, Map<Long, SysTenant> tenantMap, Map<Long, String> userRolesMap) {
        String tenantName = null;
        if (user.getTenantId() != null) {
            // tenantId 是 String，需要转换为 Long 查询
            try {
                Long tenantIdLong = Long.valueOf(user.getTenantId());
                SysTenant tenant = tenantMap.get(tenantIdLong);
                if (tenant != null) {
                    // tenant_code 为 "default" 表示平台
                    tenantName = "default".equals(tenant.getTenantCode()) ? "平台" : tenant.getTenantName();
                }
            } catch (NumberFormatException e) {
                tenantName = null;
            }
        }

        // 获取用户角色名称
        String roles = userRolesMap.getOrDefault(user.getId(), "");

        return UserRespDTO.builder()
                .id(user.getId())
                .tenantId(user.getTenantId())
                .tenantName(tenantName)
                .username(user.getUsername())
                .realName(user.getRealName())
                .avatar(user.getAvatar())
                .phone(user.getPhone())
                .email(user.getEmail())
                .remark(user.getRemark())
                .tenantType(user.getTenantType())
                .status(user.getStatus())
                .createdAt(user.getCreatedAt() != null ? user.getCreatedAt().format(DATE_FORMATTER) : null)
                .updatedAt(user.getUpdatedAt() != null ? user.getUpdatedAt().format(DATE_FORMATTER) : null)
                .roles(roles)
                .build();
    }

    @Override
    public List<UserRespDTO> listUsers() {
        // 获取当前登录用户的租户ID和租户类型
        String currentTenantId = TenantContext.getTenantId();
        String currentTenantType = TenantContext.getTenantType();

        List<SysUser> users;
        // 如果当前用户是超级管理员（tenant_type=PLATFORM），可以查看所有用户
        // 否则只能查看自己租户的用户
        if ("PLATFORM".equals(currentTenantType)) {
            users = this.list();
        } else {
            users = this.list(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getTenantId, currentTenantId));
        }

        // 批量查询租户信息 - 将 String tenantId 转为 Long
        List<Long> tenantIds = users.stream()
                .map(SysUser::getTenantId)
                .filter(id -> id != null && !id.isEmpty())
                .map(Long::valueOf)
                .distinct()
                .collect(Collectors.toList());

        // 如果租户ID列表为空，直接返回转换后的结果（不查询租户表）
        if (tenantIds.isEmpty()) {
            return users.stream()
                    .map(user -> convertToDTO(user, java.util.Collections.emptyMap(), java.util.Collections.emptyMap()))
                    .collect(Collectors.toList());
        }

        Map<Long, SysTenant> tenantMap = tenantMapper.selectList(
                new LambdaQueryWrapper<SysTenant>().in(SysTenant::getId, tenantIds)).stream()
                .collect(Collectors.toMap(SysTenant::getId, t -> t, (t1, t2) -> t1));

        // 批量查询用户角色信息
        List<Long> userIds = users.stream().map(SysUser::getId).collect(Collectors.toList());
        Map<Long, String> userRolesMap = queryUserRoles(userIds);

        return users.stream()
                .map(user -> convertToDTO(user, tenantMap, userRolesMap))
                .collect(Collectors.toList());
    }

    /**
     * 批量查询用户角色信息
     */
    private Map<Long, String> queryUserRoles(List<Long> userIds) {
        if (userIds.isEmpty()) {
            return java.util.Collections.emptyMap();
        }

        // 查询用户角色关联
        List<SysUserRole> userRoles = userRoleMapper.selectList(
                new LambdaQueryWrapper<SysUserRole>().in(SysUserRole::getUserId, userIds));

        if (userRoles.isEmpty()) {
            return java.util.Collections.emptyMap();
        }

        // 查询角色信息
        List<Long> roleIds = userRoles.stream()
                .map(SysUserRole::getRoleId)
                .distinct()
                .collect(Collectors.toList());

        Map<Long, SysRole> roleMap = roleMapper.selectList(
                new LambdaQueryWrapper<SysRole>().in(SysRole::getId, roleIds)).stream()
                .collect(Collectors.toMap(SysRole::getId, r -> r, (r1, r2) -> r1));

        // 构建用户ID到角色名称的映射
        Map<Long, String> userRolesMap = new java.util.HashMap<>();
        for (SysUserRole ur : userRoles) {
            SysRole role = roleMap.get(ur.getRoleId());
            if (role != null) {
                userRolesMap.merge(ur.getUserId(), role.getRoleName(), (oldVal, newVal) -> oldVal + ", " + newVal);
            }
        }

        return userRolesMap;
    }

    @Override
    public List<UserRespDTO> listUsersByTenantId(String tenantId) {
        // 获取当前登录用户的租户ID和租户类型
        String currentTenantId = TenantContext.getTenantId();
        String currentTenantType = TenantContext.getTenantType();

        List<SysUser> users;
        // 如果当前用户是超级管理员（tenant_type=PLATFORM）
        if ("PLATFORM".equals(currentTenantType)) {
            // 超级管理员可以按租户筛选，如果不传租户ID则查看所有用户
            if (tenantId == null || tenantId.isEmpty()) {
                users = this.list();
            } else {
                users = this.list(new LambdaQueryWrapper<SysUser>()
                        .eq(SysUser::getTenantId, tenantId));
            }
        } else {
            // 租户管理员/用户只能查看自己租户的用户，忽略传入的tenantId参数
            users = this.list(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getTenantId, currentTenantId));
        }
        // 批量查询租户信息
        List<Long> tenantIds = users.stream()
                .map(SysUser::getTenantId)
                .filter(id -> id != null && !id.isEmpty())
                .map(Long::valueOf)
                .distinct()
                .collect(Collectors.toList());

        // 如果租户ID列表为空，直接返回转换后的结果（不查询租户表）
        if (tenantIds.isEmpty()) {
            return users.stream()
                    .map(user -> convertToDTO(user, java.util.Collections.emptyMap(), java.util.Collections.emptyMap()))
                    .collect(Collectors.toList());
        }

        Map<Long, SysTenant> tenantMap = tenantMapper.selectList(
                new LambdaQueryWrapper<SysTenant>().in(SysTenant::getId, tenantIds)).stream()
                .collect(Collectors.toMap(SysTenant::getId, t -> t, (t1, t2) -> t1));

        // 批量查询用户角色信息
        List<Long> userIds = users.stream().map(SysUser::getId).collect(Collectors.toList());
        Map<Long, String> userRolesMap = queryUserRoles(userIds);

        return users.stream()
                .map(user -> convertToDTO(user, tenantMap, userRolesMap))
                .collect(Collectors.toList());
    }

    @Override
    public Long createUser(SysUser user) {
        user.setStatus(1);

        // 获取当前登录用户的租户类型
        String currentTenantType = TenantContext.getTenantType();
        String currentTenantId = TenantContext.getTenantId();

        // 如果是租户管理员创建用户，默认使用当前租户ID
        if (!TenantConstants.TENANT_TYPE_PLATFORM.equals(currentTenantType) && currentTenantId != null) {
            user.setTenantId(currentTenantId);
        }

        // 通过 tenantId 查询租户的 tenant_code
        String tenantCode = null;
        if (user.getTenantId() != null && !user.getTenantId().isEmpty()) {
            try {
                SysTenant tenant = tenantMapper.selectById(Long.valueOf(user.getTenantId()));
                if (tenant != null) {
                    tenantCode = tenant.getTenantCode();
                }
            } catch (NumberFormatException e) {
                // 忽略转换错误
            }
        }

        // 如果未指定tenantType，根据 tenant_code 设置默认值
        if (user.getTenantType() == null || user.getTenantType().isEmpty()) {
            if (tenantCode != null && !TenantConstants.isPlatformTenant(tenantCode)) {
                user.setTenantType(TenantConstants.TENANT_TYPE_TENANT_USER);
            } else {
                user.setTenantType(TenantConstants.TENANT_TYPE_PLATFORM);
            }
        }

        // 如果指定了tenantId且不为平台租户，则检查是否已有租户管理员
        if (tenantCode != null && !TenantConstants.isPlatformTenant(tenantCode)
                && TenantConstants.TENANT_TYPE_TENANT_ADMIN.equals(user.getTenantType())) {
            boolean hasAdmin = this.exists(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getTenantId, user.getTenantId())
                    .eq(SysUser::getTenantType, TenantConstants.TENANT_TYPE_TENANT_ADMIN));
            if (hasAdmin) {
                throw new RuntimeException("该租户已存在租户管理员，不能重复创建");
            }
        }

        // 如果是平台租户，强制设置tenantType为PLATFORM
        if (TenantConstants.isPlatformTenant(tenantCode)) {
            user.setTenantType(TenantConstants.TENANT_TYPE_PLATFORM);
        }

        // 对密码进行BCrypt加密
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        }

        this.save(user);
        return user.getId();
    }

    @Override
    public void updateUser(SysUser user) {
        this.updateById(user);
    }

    @Override
    public void deleteUser(Long id) {
        this.removeById(id);
    }

    @Override
    public void enableUser(Long id) {
        SysUser user = this.getById(id);
        user.setStatus(1);
        this.updateById(user);
    }

    @Override
    public void disableUser(Long id) {
        SysUser user = this.getById(id);
        user.setStatus(0);
        this.updateById(user);
    }

    @Override
    public void assignRoles(Long userId, List<Long> roleIds) {
        // 删除该用户已有的所有角色关联
        userRoleMapper.deleteByUserId(userId);

        // 从用户表中获取租户ID(而不是当前登录用户的租户ID)
        // 这样可以支持超级管理员代为初始化租户数据的场景
        SysUser user = this.getById(userId);
        if (user == null) {
            throw new IllegalArgumentException("用户不存在: " + userId);
        }
        String tenantId = user.getTenantId();

        // 添加新的角色关联
        if (roleIds != null && !roleIds.isEmpty()) {
            for (Long roleId : roleIds) {
                SysUserRole userRole = new SysUserRole();
                userRole.setTenantId(tenantId);
                userRole.setUserId(userId);
                userRole.setRoleId(roleId);
                userRoleMapper.insert(userRole);
            }
        }
    }

    @Override
    public List<SysRole> getRolesByUserId(Long userId) {
        return userRoleMapper.selectRolesByUserId(userId);
    }

    @Override
    public void resetPassword(Long userId, String newPassword) {
        SysUser user = this.getById(userId);
        if (user != null) {
            user.setPassword(passwordEncoder.encode(newPassword));
            this.updateById(user);
        }
    }
}
