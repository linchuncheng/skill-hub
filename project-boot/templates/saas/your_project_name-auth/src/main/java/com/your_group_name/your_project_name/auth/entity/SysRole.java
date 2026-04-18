package com.your_group_name.your_project_name.auth.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.your_group_name.your_project_name.common.base.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_role")
public class SysRole extends BaseEntity {
    private String tenantId;
    private String roleCode;
    private String roleName;
    private Integer sort;
    private Integer status;
}
