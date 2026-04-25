package com.fengqun.scm.platform.entity;

import com.baomidou.mybatisplus.annotation.InterceptorIgnore;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fengqun.scm.common.base.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 菜单实体（全局菜单，不受租户隔离）
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_menu")
@InterceptorIgnore(tenantLine = "true")
public class SysMenu extends BaseEntity {
    /**
     * 菜单是全局资源，不需要租户隔离。
     * 使用 exist=false 排除数据库映射。
     */
    @TableField(exist = false)
    private String tenantId;
    private Long parentId; // 父菜单 ID，根菜单为 0
    private String menuName; // 菜单名称
    private String menuPath; // 菜单路由路径
    private String component; // 对应的组件路径
    private String icon; // 菜单图标
    private Integer sort; // 排序号
    private Integer visible; // 是否可见 (1=可见, 0=隐藏)
    private String permissionCode; // 权限码
    private Integer status; // 状态 (1=启用, 0=禁用)
}
