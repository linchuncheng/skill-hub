package com.fengqun.scm.platform.entity;

import com.baomidou.mybatisplus.annotation.InterceptorIgnore;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fengqun.scm.common.base.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 租户实体（全局表，不做租户隔离）
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_tenant")
@InterceptorIgnore(tenantLine = "true")
public class SysTenant extends BaseEntity {
    /**
     * 租户表是全局资源，不需要租户隔离。
     */
    @TableField(exist = false)
    private String tenantId;

    private String tenantCode;
    private String tenantName;
    private String logo;
    private String contactName;
    private String contactPhone;
    private Integer status;
}
