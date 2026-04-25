package com.fengqun.scm.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.fengqun.scm.platform.entity.SysMenu;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 菜单 Mapper
 */
@Mapper
public interface SysMenuMapper extends BaseMapper<SysMenu> {

        /**
         * 根据用户ID查询菜单列表
         * 超级管理员（SUPER_ADMIN）拥有所有菜单
         *
         * @param userId 用户ID
         * @return 菜单列表
         */
        @Select("SELECT DISTINCT m.* FROM sys_menu m " +
                        "WHERE m.status = 1 AND m.deleted = 0 " +
                        "AND (" +
                        "  EXISTS (" +
                        "    SELECT 1 FROM sys_user_role ur " +
                        "    JOIN sys_role r ON ur.role_id = r.id " +
                        "    WHERE ur.user_id = #{userId} AND r.role_code = 'SUPER_ADMIN' AND r.deleted = 0" +
                        "  ) " +
                        "  OR EXISTS (" +
                        "    SELECT 1 FROM sys_role_menu rm " +
                        "    JOIN sys_user_role ur ON rm.role_id = ur.role_id " +
                        "    WHERE ur.user_id = #{userId} AND rm.menu_id = m.id" +
                        "  ) " +
                        ") " +
                        "ORDER BY m.sort ASC")
        List<SysMenu> selectMenusByUserId(@Param("userId") Long userId);

        /**
         * 查询所有启用的菜单
         */
        @Select("SELECT * FROM sys_menu WHERE status = 1 AND deleted = 0 ORDER BY sort ASC")
        List<SysMenu> selectAllEnabledMenus();

        /**
         * 根据用户ID查询菜单列表，包含默认菜单
         * 用于租户管理员，包含角色分配菜单 + 默认菜单（租户管理、角色管理）
         *
         * @param userId       用户ID
         * @param defaultPaths 默认菜单路径列表
         * @return 菜单列表
         */
        List<SysMenu> selectMenusByUserIdWithDefault(@Param("userId") Long userId,
                        @Param("defaultPaths") List<String> defaultPaths);
}
