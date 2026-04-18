package com.your_group_name.your_project_name.platform.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.your_group_name.your_project_name.platform.dto.MenuDTO;
import com.your_group_name.your_project_name.platform.entity.SysMenu;

import java.util.List;

/**
 * 菜单服务接口
 */
public interface MenuService extends IService<SysMenu> {

    /**
     * 查询所有菜单列表
     */
    List<SysMenu> listMenus();

    /**
     * 查询菜单树形结构
     */
    List<MenuDTO> buildMenuTree();

    /**
     * 查询菜单树形结构（用于权限分配）
     * 超级管理员返回所有菜单，租户管理员只返回已拥有的菜单
     */
    List<MenuDTO> buildMenuTreeForAssign();

    /**
     * 根据用户 ID 查询用户菜单树
     */
    List<MenuDTO> buildMenuTreeByUserId(Long userId);

    /**
     * 创建菜单
     */
    Long createMenu(SysMenu menu);

    /**
     * 更新菜单
     */
    void updateMenu(SysMenu menu);

    /**
     * 删除菜单
     */
    void deleteMenu(Long id);

    /**
     * 分配菜单权限给角色
     */
    void assignMenuToRole(Long roleId, List<Long> menuIds);

    /**
     * 查询角色拥有的菜单
     */
    List<SysMenu> getMenusByRoleId(Long roleId);
}
