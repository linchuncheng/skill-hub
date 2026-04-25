package com.fengqun.scm.platform.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.fengqun.scm.common.base.BaseEntity;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 登录日志实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_login_log")
public class SysLoginLog extends BaseEntity {

    private String tenantId;
    private Long userId;
    private String username;
    private String loginIp;
    private String loginLocation;
    private String browser;
    private String os;
    private Integer status;
    private String message;
    private LocalDateTime loginTime;
}
