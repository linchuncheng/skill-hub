package com.your_group_name.your_project_name.common.response;

import lombok.Data;

import java.io.Serializable;

/**
 * 统一响应体。
 *
 * @param <T> 响应数据类型
 */
@Data
public class R<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 响应码。
     * - "200": 成功
     * - "4xx": 客户端错误
     * - "5xx": 服务端错误
     */
    private String code;

    /**
     * 响应消息。
     */
    private String msg;

    /**
     * 响应数据。
     */
    private T data;

    /**
     * 成功响应码。
     */
    public static final int SUCCESS_CODE = 200;

    /**
     * 失败响应码。
     */
    public static final int FAIL_CODE = 500;

    /**
     * 默认成功消息。
     */
    public static final String SUCCESS_MSG = "操作成功";

    /**
     * 默认失败消息。
     */
    public static final String FAIL_MSG = "操作失败";

    /**
     * 判断是否成功。
     *
     * @return true if code == "200", false otherwise
     */
    public boolean isSuccess() {
        return String.valueOf(SUCCESS_CODE).equals(this.code);
    }

    /**
     * 创建成功响应（无数据）。
     *
     * @param <T> 数据类型
     * @return 成功响应
     */
    public static <T> R<T> ok() {
        return ok(null);
    }

    /**
     * 创建成功响应（带数据）。
     *
     * @param data 响应数据
     * @param <T>  数据类型
     * @return 成功响应
     */
    public static <T> R<T> ok(T data) {
        return ok(data, SUCCESS_MSG);
    }

    /**
     * 创建成功响应（带数据和自定义消息）。
     *
     * @param data 响应数据
     * @param msg  自定义消息
     * @param <T>  数据类型
     * @return 成功响应
     */
    public static <T> R<T> ok(T data, String msg) {
        R<T> r = new R<>();
        r.setCode(String.valueOf(SUCCESS_CODE)); // 返回字符串
        r.setMsg(msg);
        r.setData(data);
        return r;
    }

    /**
     * 创建失败响应（无参，使用默认失败消息）。
     *
     * @param <T> 数据类型
     * @return 失败响应
     */
    public static <T> R<T> fail() {
        return fail(FAIL_MSG);
    }

    /**
     * 创建失败响应（使用默认错误码 500）。
     *
     * @param msg 错误消息
     * @param <T> 数据类型
     * @return 失败响应
     */
    public static <T> R<T> fail(String msg) {
        return fail(FAIL_CODE, msg);
    }

    /**
     * 创建失败响应（带错误码）。
     *
     * @param code 错误码
     * @param msg  错误消息
     * @param <T>  数据类型
     * @return 失败响应
     */
    public static <T> R<T> fail(Integer code, String msg) {
        R<T> r = new R<>();
        r.setCode(String.valueOf(code)); // 返回字符串
        r.setMsg(msg);
        r.setData(null);
        return r;
    }
}
