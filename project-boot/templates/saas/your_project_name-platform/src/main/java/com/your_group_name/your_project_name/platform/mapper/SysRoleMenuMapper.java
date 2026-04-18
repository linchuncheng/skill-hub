package com.your_group_name.your_project_name.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your_group_name.your_project_name.platform.entity.SysRoleMenu;

import java.util.List;

import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Select;

/**
 * 角色菜单关联 Mapper
 */
public interface SysRoleMenuMapper extends BaseMapper<SysRoleMenu> {

    @Delete("DELETE FROM sys_role_menu WHERE role_id = #{roleId}")
    void deleteByRoleId(Long roleId);

    @Select("SELECT menu_id FROM sys_role_menu WHERE role_id = #{roleId}")
    List<Long> selectMenuIdsByRoleId(Long roleId);

    @Select({
            "SELECT DISTINCT m.* FROM sys_menu m",
            "INNER JOIN sys_role_menu rm ON m.id = rm.menu_id",
            "WHERE rm.role_id = #{roleId} AND m.status = 1 AND m.deleted = 0"
    })
    List<SysRoleMenu> selectMenusByRoleId(Long roleId);
}
