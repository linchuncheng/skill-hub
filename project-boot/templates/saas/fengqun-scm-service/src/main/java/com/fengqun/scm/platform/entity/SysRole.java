package com.fengqun.scm.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.fengqun.scm.common.base.BaseEntity;
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
