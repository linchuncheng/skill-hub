package com.fengqun.scm.platform.controller;

import com.fengqun.scm.common.base.BaseController;
import com.fengqun.scm.common.response.R;
import com.fengqun.scm.platform.dto.MenuDTO;
import com.fengqun.scm.platform.entity.SysMenu;
import com.fengqun.scm.platform.service.MenuService;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 菜单 API 控制器
 */
@RestController
@RequestMapping("/api/platform/menu")
public class MenuController extends BaseController {

    @Autowired
    private MenuService menuService;

    @GetMapping("/list")
    public R<List<SysMenu>> listMenus() {
        return success(menuService.listMenus());
    }

    @GetMapping("/tree")
    public R<List<MenuDTO>> buildMenuTree() {
        return success(menuService.buildMenuTree());
    }

    /**
     * 获取菜单树（用于权限分配）
     * 超级管理员返回所有菜单，租户管理员只返回已拥有的菜单
     */
    @GetMapping("/tree/assign")
    public R<List<MenuDTO>> buildMenuTreeForAssign() {
        return success(menuService.buildMenuTreeForAssign());
    }

    @GetMapping("/tree/user/{userId}")
    public R<List<MenuDTO>> buildMenuTreeByUserId(@PathVariable Long userId) {
        return success(menuService.buildMenuTreeByUserId(userId));
    }

    @PostMapping
    public R<Long> createMenu(@RequestBody SysMenu menu) {
        Long menuId = menuService.createMenu(menu);
        return success(menuId);
    }

    @PutMapping
    public R<Void> updateMenu(@RequestBody SysMenu menu) {
        menuService.updateMenu(menu);
        return success();
    }

    @DeleteMapping("/{id}")
    public R<Void> deleteMenu(@PathVariable Long id) {
        menuService.deleteMenu(id);
        return success();
    }

    @PostMapping("/role/{roleId}/assign")
    public R<Void> assignMenuToRole(@PathVariable Long roleId, @RequestBody List<Long> menuIds) {
        menuService.assignMenuToRole(roleId, menuIds);
        return success();
    }

    @GetMapping("/role/{roleId}")
    public R<List<SysMenu>> getMenusByRoleId(@PathVariable Long roleId) {
        return success(menuService.getMenusByRoleId(roleId));
    }
}
