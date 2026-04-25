package com.fengqun.scm.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.fengqun.scm.platform.entity.SysUser;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
    @Select("SELECT * FROM sys_user WHERE username = #{username} AND deleted = 0")
    SysUser selectByUsername(String username);

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
