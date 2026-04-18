package com.your_group_name.your_project_name.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.your_group_name.your_project_name.common.base.BaseEntity;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_user")
public class SysUser extends BaseEntity {
    private String tenantId;
    private String username;
    private String password;
    private String realName;
    private String avatar;
    private String phone;
    private String email;
    private String remark;
    private String tenantType;
    private Integer status;
}
