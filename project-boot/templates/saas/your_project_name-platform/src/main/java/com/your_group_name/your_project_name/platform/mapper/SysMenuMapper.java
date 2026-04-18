package com.your_group_name.your_project_name.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your_group_name.your_project_name.platform.entity.SysMenu;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

/**
 * 菜单 Mapper
 */
@Mapper
public interface SysMenuMapper extends BaseMapper<SysMenu> {

    /**
     * 查询用户有权限访问的菜单列表
     */
    @Select({
            "SELECT DISTINCT m.* FROM sys_menu m",
            "LEFT JOIN sys_role_menu rm ON m.id = rm.menu_id",
            "LEFT JOIN sys_user_role ur ON rm.role_id = ur.role_id",
            "WHERE ur.user_id = #{userId} AND m.status = 1 AND m.deleted = 0 AND m.visible = 1"
    })
    List<SysMenu> selectMenusByUserId(Long userId);

    /**
     * 查询所有启用的菜单
     */
    @Select("SELECT * FROM sys_menu WHERE status = 1 AND deleted = 0 ORDER BY sort ASC")
    List<SysMenu> selectAllEnabledMenus();
}
