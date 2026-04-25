package com.fengqun.scm.platform.auth.dto;

import java.util.List;

import lombok.Data;

/**
 * 菜单 DTO（树形结构）
 */
@Data
public class MenuDTO {

    /**
     * 菜单ID
     */
    private Long id;

    /**
     * 菜单名称
     */
    private String name;

    /**
     * 路由路径
     */
    private String path;

    /**
     * 前端组件路径
     */
    private String component;

    /**
     * 图标
     */
    private String icon;

    /**
     * 排序号
     */
    private Integer sort;

    /**
     * 子菜单
     */
    private List<MenuDTO> children;
}
