package com.your_group_name.your_project_name.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.your_group_name.your_project_name.common.tenant.TenantConstants;
import com.your_group_name.your_project_name.common.tenant.TenantContext;
import com.your_group_name.your_project_name.platform.dto.MenuDTO;
import com.your_group_name.your_project_name.platform.entity.SysMenu;
import com.your_group_name.your_project_name.platform.entity.SysRoleMenu;
import com.your_group_name.your_project_name.platform.entity.SysTenant;
import com.your_group_name.your_project_name.platform.mapper.SysMenuMapper;
import com.your_group_name.your_project_name.platform.mapper.SysRoleMenuMapper;
import com.your_group_name.your_project_name.platform.mapper.SysTenantMapper;
import com.your_group_name.your_project_name.platform.service.MenuService;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 菜单服务实现
 */
@Service
public class MenuServiceImpl extends ServiceImpl<SysMenuMapper, SysMenu> implements MenuService {

    @Autowired
    private SysRoleMenuMapper roleMenuMapper;

    @Autowired
    private SysTenantMapper tenantMapper;

    @Override
    public List<SysMenu> listMenus() {
        return this.list(new LambdaQueryWrapper<SysMenu>()
                .eq(SysMenu::getStatus, 1)
                .orderByAsc(SysMenu::getSort));
    }

    @Override
    public List<MenuDTO> buildMenuTree() {
        List<SysMenu> menus = this.baseMapper.selectAllEnabledMenus();
        return buildTree(menus, 0L);
    }

    @Override
    public List<MenuDTO> buildMenuTreeForAssign() {
        String tenantType = TenantContext.getTenantType();
        Long userId = TenantContext.getUserId();

        // 超级管理员：返回所有菜单
        if (TenantConstants.isPlatformType(tenantType)) {
            List<SysMenu> menus = this.baseMapper.selectAllEnabledMenus();
            return buildTree(menus, 0L);
        }

        // 租户管理员/租户用户：只返回已拥有的菜单
        if (userId != null) {
            List<SysMenu> menus = this.baseMapper.selectMenusByUserId(userId);
            return buildTree(menus, 0L);
        }

        return new ArrayList<>();
    }

    @Override
    public List<MenuDTO> buildMenuTreeByUserId(Long userId) {
        List<SysMenu> menus = this.baseMapper.selectMenusByUserId(userId);
        return buildTree(menus, 0L);
    }

    @Override
    public Long createMenu(SysMenu menu) {
        // 菜单是全局的，查询平台租户（tenant_code='default'）的 ID
        SysTenant platformTenant = tenantMapper.selectOne(
                new LambdaQueryWrapper<SysTenant>().eq(SysTenant::getTenantCode, TenantConstants.PLATFORM_TENANT_CODE));
        if (platformTenant != null) {
            menu.setTenantId(String.valueOf(platformTenant.getId()));
        }
        menu.setStatus(1);
        this.save(menu);
        return menu.getId();
    }

    @Override
    public void updateMenu(SysMenu menu) {
        this.updateById(menu);
    }

    @Override
    public void deleteMenu(Long id) {
        this.removeById(id);
    }

    @Override
    public void assignMenuToRole(Long roleId, List<Long> menuIds) {
        // 删除该角色已有的所有菜单关联
        roleMenuMapper.deleteByRoleId(roleId);

        // 添加新的菜单关联
        if (menuIds != null && !menuIds.isEmpty()) {
            for (Long menuId : menuIds) {
                SysRoleMenu roleMenu = new SysRoleMenu();
                roleMenu.setRoleId(roleId);
                roleMenu.setMenuId(menuId);
                roleMenuMapper.insert(roleMenu);
            }
        }
    }

    @Override
    public List<SysMenu> getMenusByRoleId(Long roleId) {
        List<Long> menuIds = roleMenuMapper.selectMenuIdsByRoleId(roleId);
        if (menuIds == null || menuIds.isEmpty()) {
            return new ArrayList<>();
        }
        return this.list(new LambdaQueryWrapper<SysMenu>()
                .in(SysMenu::getId, menuIds)
                .eq(SysMenu::getStatus, 1)
                .orderByAsc(SysMenu::getSort));
    }

    /**
     * 递归构建菜单树
     */
    private List<MenuDTO> buildTree(List<SysMenu> menus, Long parentId) {
        return menus.stream()
                .filter(menu -> menu.getParentId().equals(parentId))
                .map(menu -> {
                    MenuDTO dto = new MenuDTO();
                    dto.setId(menu.getId());
                    dto.setParentId(menu.getParentId());
                    dto.setName(menu.getMenuName());
                    dto.setPath(menu.getMenuPath());
                    dto.setComponent(menu.getComponent());
                    dto.setIcon(menu.getIcon());
                    dto.setSort(menu.getSort());
                    dto.setVisible(menu.getVisible());
                    dto.setStatus(menu.getStatus());
                    dto.setPermissionCode(menu.getPermissionCode());
                    // 递归查找子菜单
                    dto.setChildren(buildTree(menus, menu.getId()));
                    return dto;
                })
                .sorted(Comparator.comparingInt(dto -> dto.getSort() != null ? dto.getSort() : 0))
                .collect(Collectors.toList());
    }
}
