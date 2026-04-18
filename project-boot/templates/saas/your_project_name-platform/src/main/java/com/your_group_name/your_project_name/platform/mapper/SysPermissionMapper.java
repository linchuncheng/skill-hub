package com.your_group_name.your_project_name.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your_group_name.your_project_name.platform.entity.SysPermission;

import java.util.List;

import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 权限 Mapper
 */
public interface SysPermissionMapper extends BaseMapper<SysPermission> {

        /**
         * 查询所有启用的权限
         */
        @Select("SELECT * FROM sys_permission WHERE status = 1 AND deleted = 0 ORDER BY sort ASC")
        List<SysPermission> selectAllEnabledPermissions();

        /**
         * 根据角色ID查询权限列表
         */
        @Select("SELECT DISTINCT p.* FROM sys_permission p " +
                        "JOIN sys_role_permission rp ON p.id = rp.permission_id " +
                        "WHERE rp.role_id = #{roleId} AND p.status = 1 AND p.deleted = 0 " +
                        "ORDER BY p.sort ASC")
        List<SysPermission> selectPermissionsByRoleId(@Param("roleId") Long roleId);

        /**
         * 根据用户ID查询权限列表（通过角色获取）
         */
        @Select("SELECT DISTINCT p.* FROM sys_permission p " +
                        "JOIN sys_role_permission rp ON p.id = rp.permission_id " +
                        "JOIN sys_user_role ur ON rp.role_id = ur.role_id " +
                        "WHERE ur.user_id = #{userId} AND p.status = 1 AND p.deleted = 0 " +
                        "ORDER BY p.sort ASC")
        List<SysPermission> selectPermissionsByUserId(@Param("userId") Long userId);
}
