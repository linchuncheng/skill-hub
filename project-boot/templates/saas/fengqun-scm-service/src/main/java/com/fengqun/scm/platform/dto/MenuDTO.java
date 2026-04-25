package com.fengqun.scm.platform.dto;

import lombok.Data;

import java.util.List;

/**
 * 菜单树形 DTO（用于前端展示和 API 返回）
 */
@Data
public class MenuDTO {
    private Long id;
    private Long parentId;
    private String name;
    private String path;
    private String component;
    private String icon;
    private Integer sort;
    private Integer visible;
    private Integer status;
    private String permissionCode; // 权限码
    private List<MenuDTO> children;

    public MenuDTO() {
    }

    public MenuDTO(Long id, String name, String path) {
        this.id = id;
        this.name = name;
        this.path = path;
    }
}
