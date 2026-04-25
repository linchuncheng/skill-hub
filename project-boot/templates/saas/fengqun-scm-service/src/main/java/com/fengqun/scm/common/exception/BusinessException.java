package com.fengqun.scm.common.exception;

import lombok.Getter;

/**
 * 业务异常基类。
 */
@Getter
public class BusinessException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /**
     * 错误码。
     */
    private final Integer code;

    /**
     * 构造函数（仅消息）。
     *
     * @param message 异常消息
     */
    public BusinessException(String message) {
        super(message);
        this.code = BusinessCode.BUSINESS_ERROR.getCode();
    }

    /**
     * 构造函数（错误码 + 消息）。
     *
     * @param code    错误码
     * @param message 异常消息
     */
    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }

    /**
     * 构造函数（业务错误码枚举）。
     *
     * @param businessCode 业务错误码枚举
     */
    public BusinessException(BusinessCode businessCode) {
        super(businessCode.getMsg());
        this.code = businessCode.getCode();
    }

    /**
     * 构造函数（业务错误码枚举 + 自定义消息）。
     *
     * @param businessCode 业务错误码枚举
     * @param message      异常消息
     */
    public BusinessException(BusinessCode businessCode, String message) {
        super(message);
        this.code = businessCode.getCode();
    }
}
