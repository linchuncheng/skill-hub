package com.your_group_name.your_project_name.platform.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.your_group_name.your_project_name.platform.dto.UserRespDTO;
import com.your_group_name.your_project_name.platform.entity.SysRole;
import com.your_group_name.your_project_name.platform.entity.SysUser;

import java.util.List;

public interface UserService extends IService<SysUser> {
    List<UserRespDTO> listUsers();

    /**
     * 根据租户ID查询用户列表（超级管理员使用）
     */
    List<UserRespDTO> listUsersByTenantId(String tenantId);

    Long createUser(SysUser user);

    void updateUser(SysUser user);

    void deleteUser(Long id);

    void enableUser(Long id);

    void disableUser(Long id);

    void assignRoles(Long userId, List<Long> roleIds);

    List<SysRole> getRolesByUserId(Long userId);

    void resetPassword(Long userId, String newPassword);
}
