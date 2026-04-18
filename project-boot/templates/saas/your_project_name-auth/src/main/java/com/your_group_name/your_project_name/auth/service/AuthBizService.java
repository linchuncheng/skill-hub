package com.your_group_name.your_project_name.auth.service;

import com.your_group_name.your_project_name.auth.config.JwtProperties;
import com.your_group_name.your_project_name.auth.dto.LoginReqDTO;
import com.your_group_name.your_project_name.auth.dto.LoginRespDTO;
import com.your_group_name.your_project_name.auth.dto.MenuDTO;
import com.your_group_name.your_project_name.auth.dto.UserInfoDTO;
import com.your_group_name.your_project_name.auth.entity.SysLoginLog;
import com.your_group_name.your_project_name.auth.entity.SysMenu;
import com.your_group_name.your_project_name.auth.entity.SysUser;
import com.your_group_name.your_project_name.auth.mapper.SysLoginLogMapper;
import com.your_group_name.your_project_name.auth.mapper.SysMenuMapper;
import com.your_group_name.your_project_name.auth.mapper.SysPermissionMapper;
import com.your_group_name.your_project_name.auth.mapper.SysUserMapper;
import com.your_group_name.your_project_name.common.exception.BusinessCode;
import com.your_group_name.your_project_name.common.exception.BusinessException;
import com.your_group_name.your_project_name.common.security.TokenKit;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import org.redisson.api.RBucket;
import org.redisson.api.RedissonClient;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import cn.hutool.core.util.IdUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * 认证业务服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthBizService {

    private final SysUserMapper sysUserMapper;
    private final SysPermissionMapper sysPermissionMapper;
    private final SysMenuMapper sysMenuMapper;
    private final SysLoginLogMapper sysLoginLogMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtProperties jwtProperties;
    private final RedissonClient redissonClient;

    /**
     * 登录
     */
    public LoginRespDTO login(LoginReqDTO req) {
        // 1. 查询用户
        SysUser user = sysUserMapper.selectByUsername(req.getUsername());
        if (user == null) {
            recordLoginLog(null, req.getUsername(), 0, "用户不存在");
            throw new BusinessException(BusinessCode.UNAUTHORIZED, "用户名或密码错误");
        }

        // 2. 验证状态
        if (user.getStatus() != 1) {
            recordLoginLog(user.getTenantId(), req.getUsername(), 0, "账号已被禁用");
            throw new BusinessException(BusinessCode.FORBIDDEN, "账号已被禁用");
        }

        // 3. 验证密码
        if (!passwordEncoder.matches(req.getPassword(), user.getPassword())) {
            recordLoginLog(user.getTenantId(), req.getUsername(), 0, "密码错误");
            throw new BusinessException(BusinessCode.UNAUTHORIZED, "用户名或密码错误");
        }

        // 4. 签发 JWT Token
        Map<String, Object> claims = new HashMap<>();
        claims.put("user_id", user.getId().toString());
        claims.put("username", user.getUsername());
        claims.put("tenant_id", user.getTenantId());
        claims.put("tenant_type", user.getTenantType());

        String accessToken = TokenKit.generateToken(
                user.getId().toString(),
                claims,
                jwtProperties.getAccessTokenExpiration(),
                jwtProperties.getSecret());

        String refreshToken = IdUtil.simpleUUID();

        // 5. 存储 refresh_token 到 Redis（7天过期）
        RBucket<String> bucket = redissonClient.getBucket("refresh_token:" + refreshToken);
        bucket.set(user.getId().toString(), 7, TimeUnit.DAYS);

        // 6. 根据用户类型查询权限和菜单
        List<String> permissions;
        List<MenuDTO> menuTree;

        String tenantType = user.getTenantType();
        if ("PLATFORM".equals(tenantType)) {
            // 超级管理员：拥有所有菜单和权限
            permissions = sysPermissionMapper.selectAllPermissionCodes();
            List<SysMenu> allMenus = sysMenuMapper.selectAllEnabledMenus();
            menuTree = buildMenuTree(allMenus);
        } else if ("PLATFORM_USER".equals(tenantType)) {
            // 平台用户：默认只有首页，其他根据角色分配
            permissions = sysPermissionMapper.selectPermissionCodesByUserId(user.getId());
            // 添加首页权限
            Set<String> defaultPermissions = new HashSet<>(Arrays.asList("platform:dashboard:view"));
            defaultPermissions.addAll(permissions);
            permissions = new ArrayList<>(defaultPermissions);

            // 获取菜单 - 角色分配的（首页由前端硬编码，不需要后端返回）
            List<SysMenu> allMenus = sysMenuMapper.selectAllEnabledMenus();
            List<SysMenu> roleMenus = sysMenuMapper.selectMenusByUserId(user.getId());
            Set<Long> menuIds = roleMenus.stream().map(SysMenu::getId).collect(Collectors.toSet());
            // 不再添加首页菜单，前端已硬编码
            List<SysMenu> filteredMenus = allMenus.stream()
                    .filter(m -> menuIds.contains(m.getId()))
                    .collect(Collectors.toList());
            menuTree = buildMenuTree(filteredMenus);
        } else if ("TENANT_ADMIN".equals(tenantType)) {
            // 租户管理员：默认有用户管理、角色管理权限和菜单，其余按角色分配
            // 1. 获取角色分配的权限
            permissions = sysPermissionMapper.selectPermissionCodesByUserId(user.getId());
            // 2. 添加默认权限（用户管理 + 角色管理）
            Set<String> defaultPermissions = new HashSet<>(Arrays.asList(
                    "platform:user:list", "platform:user:create", "platform:user:edit", "platform:user:delete",
                    "platform:role:list", "platform:role:create", "platform:role:edit", "platform:role:delete",
                    "platform:role:assign-menu"));
            defaultPermissions.addAll(permissions);
            permissions = new ArrayList<>(defaultPermissions);

            // 3. 获取菜单 - 角色分配的 + 默认的系统管理菜单（首页由前端硬编码，不需要后端返回）
            List<SysMenu> allMenus = sysMenuMapper.selectAllEnabledMenus();
            List<SysMenu> roleMenus = sysMenuMapper.selectMenusByUserId(user.getId());
            Set<Long> menuIds = roleMenus.stream().map(SysMenu::getId).collect(Collectors.toSet());
            // 添加默认菜单：系统管理(id=1)、用户管理(id=12)、角色管理(id=21)
            menuIds.add(1L); // 系统管理
            menuIds.add(12L); // 用户管理
            menuIds.add(21L); // 角色管理
            // 不再添加首页菜单，前端已硬编码
            List<SysMenu> filteredMenus = allMenus.stream()
                    .filter(m -> menuIds.contains(m.getId()))
                    .collect(Collectors.toList());
            menuTree = buildMenuTree(filteredMenus);
        } else {
            // 租户用户：默认只有首页，其他按租户管理员分配的角色返回
            permissions = sysPermissionMapper.selectPermissionCodesByUserId(user.getId());
            // 添加首页权限
            Set<String> defaultPermissions = new HashSet<>(Arrays.asList("platform:dashboard:view"));
            defaultPermissions.addAll(permissions);
            permissions = new ArrayList<>(defaultPermissions);

            // 获取菜单 - 角色分配的（首页由前端硬编码，不需要后端返回）
            List<SysMenu> allMenus = sysMenuMapper.selectAllEnabledMenus();
            List<SysMenu> roleMenus = sysMenuMapper.selectMenusByUserId(user.getId());
            Set<Long> menuIds = roleMenus.stream().map(SysMenu::getId).collect(Collectors.toSet());
            // 不再添加首页菜单，前端已硬编码
            List<SysMenu> filteredMenus = allMenus.stream()
                    .filter(m -> menuIds.contains(m.getId()))
                    .collect(Collectors.toList());
            menuTree = buildMenuTree(filteredMenus);
        }

        // 8. 记录登录日志
        recordLoginLog(user.getTenantId(), req.getUsername(), 1, "登录成功");

        // 9. 构造响应
        LoginRespDTO resp = new LoginRespDTO();
        resp.setAccessToken(accessToken);
        resp.setRefreshToken(refreshToken);

        // 查询用户角色名称列表
        List<String> roleNames = sysUserMapper.selectRoleNamesByUserId(user.getId());

        UserInfoDTO userInfo = new UserInfoDTO();
        userInfo.setUserId(user.getId().toString());
        userInfo.setUsername(user.getUsername());
        userInfo.setRealName(user.getRealName());
        userInfo.setAvatar(user.getAvatar());
        userInfo.setPhone(user.getPhone());
        userInfo.setEmail(user.getEmail());
        userInfo.setTenantId(user.getTenantId());
        userInfo.setTenantType(user.getTenantType());
        userInfo.setRoles(roleNames);
        resp.setUserInfo(userInfo);

        resp.setPermissions(permissions);
        resp.setMenus(menuTree);

        return resp;
    }

    /**
     * 刷新 Token
     */
    public LoginRespDTO refreshToken(String refreshToken) {
        // 1. 验证 refresh_token
        RBucket<String> bucket = redissonClient.getBucket("refresh_token:" + refreshToken);
        String userId = bucket.get();

        if (userId == null) {
            throw new BusinessException(BusinessCode.TOKEN_INVALID, "Refresh Token 无效或已过期");
        }

        // 2. 查询用户
        SysUser user = sysUserMapper.selectById(Long.parseLong(userId));
        if (user == null || user.getStatus() != 1) {
            throw new BusinessException(BusinessCode.FORBIDDEN, "用户不存在或已被禁用");
        }

        // 3. 签发新 Token
        Map<String, Object> claims = new HashMap<>();
        claims.put("user_id", user.getId().toString());
        claims.put("username", user.getUsername());
        claims.put("tenant_id", user.getTenantId());
        claims.put("tenant_type", user.getTenantType());

        String newAccessToken = TokenKit.generateToken(
                user.getId().toString(),
                claims,
                jwtProperties.getAccessTokenExpiration(),
                jwtProperties.getSecret());

        String newRefreshToken = IdUtil.simpleUUID();

        // 4. 删除旧 refresh_token，存储新 refresh_token
        bucket.delete();
        RBucket<String> newBucket = redissonClient.getBucket("refresh_token:" + newRefreshToken);
        newBucket.set(user.getId().toString(), 7, TimeUnit.DAYS);

        // 5. 构造响应（刷新 Token 不返回权限和菜单）
        LoginRespDTO resp = new LoginRespDTO();
        resp.setAccessToken(newAccessToken);
        resp.setRefreshToken(newRefreshToken);

        // 查询用户角色名称列表
        List<String> roleNames = sysUserMapper.selectRoleNamesByUserId(user.getId());

        UserInfoDTO userInfo = new UserInfoDTO();
        userInfo.setUserId(user.getId().toString());
        userInfo.setUsername(user.getUsername());
        userInfo.setRealName(user.getRealName());
        userInfo.setAvatar(user.getAvatar());
        userInfo.setPhone(user.getPhone());
        userInfo.setEmail(user.getEmail());
        userInfo.setTenantId(user.getTenantId());
        userInfo.setTenantType(user.getTenantType());
        userInfo.setRoles(roleNames);
        resp.setUserInfo(userInfo);

        return resp;
    }

    /**
     * 登出
     */
    public void logout(String refreshToken) {
        if (refreshToken != null && !refreshToken.isEmpty()) {
            RBucket<String> bucket = redissonClient.getBucket("refresh_token:" + refreshToken);
            bucket.delete();
        }
    }

    /**
     * 构建菜单树
     */
    private List<MenuDTO> buildMenuTree(List<SysMenu> menus) {
        // 按 parent_id 分组
        Map<Long, List<SysMenu>> menuMap = menus.stream()
                .collect(Collectors.groupingBy(SysMenu::getParentId));

        // 构建顶级菜单
        return menuMap.getOrDefault(0L, Collections.emptyList()).stream()
                .map(menu -> convertToMenuDTO(menu, menuMap))
                .sorted(Comparator.comparing(MenuDTO::getSort))
                .collect(Collectors.toList());
    }

    /**
     * 递归转换菜单 DTO
     */
    private MenuDTO convertToMenuDTO(SysMenu menu, Map<Long, List<SysMenu>> menuMap) {
        MenuDTO dto = new MenuDTO();
        dto.setId(menu.getId());
        dto.setName(menu.getMenuName());
        dto.setPath(menu.getMenuPath());
        dto.setComponent(menu.getComponent());
        dto.setIcon(menu.getIcon());
        dto.setSort(menu.getSort());

        // 递归构建子菜单
        List<MenuDTO> children = menuMap.getOrDefault(menu.getId(), Collections.emptyList()).stream()
                .map(childMenu -> convertToMenuDTO(childMenu, menuMap))
                .sorted(Comparator.comparing(MenuDTO::getSort))
                .collect(Collectors.toList());

        if (!children.isEmpty()) {
            dto.setChildren(children);
        }

        return dto;
    }

    /**
     * 记录登录日志
     */
    private void recordLoginLog(String tenantId, String username, Integer status, String message) {
        try {
            SysLoginLog log = new SysLoginLog();
            log.setTenantId(tenantId != null ? tenantId : "0");
            log.setUsername(username);
            log.setStatus(status);
            log.setMessage(message);
            log.setLoginTime(LocalDateTime.now());
            sysLoginLogMapper.insert(log);
        } catch (Exception e) {
            log.warn("Failed to record login log", e);
        }
    }
}
