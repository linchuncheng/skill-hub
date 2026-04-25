package com.fengqun.scm.common.exception;

import lombok.Getter;

/**
 * 通用业务错误码枚举。
 */
@Getter
public enum BusinessCode {

    // 通用错误 (50000-50099)
    BUSINESS_ERROR(50000, "业务处理失败"),
    SYSTEM_ERROR(50001, "系统内部错误"),

    // 参数错误 (40000-40099)
    PARAM_INVALID(40000, "参数校验失败"),
    PARAM_MISSING(40001, "缺少必要参数"),

    // 认证授权错误 (40100-40199)
    UNAUTHORIZED(40100, "未认证"),
    FORBIDDEN(40101, "无权限访问"),
    TOKEN_INVALID(40102, "Token 无效"),
    TOKEN_EXPIRED(40103, "Token 已过期"),

    // 数据错误 (40200-40299)
    DATA_NOT_FOUND(40200, "数据不存在"),
    DATA_ALREADY_EXISTS(40201, "数据已存在"),
    DATA_IN_USE(40202, "数据正在使用中，无法删除"),
    ORDER_DUPLICATE(40203, "订单已存在，请勿重复提交"),

    // 租户错误 (40300-40399)
    TENANT_NOT_FOUND(40300, "租户不存在"),
    TENANT_DISABLED(40301, "租户已禁用"),
    ;

    /**
     * 错误码。
     */
    private final Integer code;

    /**
     * 错误消息。
     */
    private final String msg;

    BusinessCode(Integer code, String msg) {
        this.code = code;
        this.msg = msg;
    }
}
