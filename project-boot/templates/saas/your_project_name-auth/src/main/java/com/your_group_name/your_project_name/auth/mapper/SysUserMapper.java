package com.your_group_name.your_project_name.auth.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your_group_name.your_project_name.auth.entity.SysUser;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 用户 Mapper
 */
public interface SysUserMapper extends BaseMapper<SysUser> {

    /**
     * 根据用户名查询用户（不受租户隔离限制）
     *
     * @param username 用户名
     * @return 用户实体
     */
    @Select("SELECT * FROM sys_user WHERE username = #{username} AND deleted = 0 LIMIT 1")
    SysUser selectByUsername(@Param("username") String username);

    /**
     * 查询用户的角色名称列表
     *
     * @param userId 用户ID
     * @return 角色名称列表
     */
    @Select("SELECT r.role_name FROM sys_role r " +
            "JOIN sys_user_role ur ON r.id = ur.role_id " +
            "WHERE ur.user_id = #{userId} AND r.deleted = 0")
    List<String> selectRoleNamesByUserId(@Param("userId") Long userId);
}
