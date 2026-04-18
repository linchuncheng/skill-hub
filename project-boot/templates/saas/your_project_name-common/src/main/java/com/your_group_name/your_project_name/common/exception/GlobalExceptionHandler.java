package com.your_group_name.your_project_name.common.exception;

import com.your_group_name.your_project_name.common.response.R;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理器。
 *
 * 捕获所有 Controller 抛出的异常，统一转换为标准响应格式。
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 是否为开发环境（显示详细错误信息）
     */
    @Value("${spring.profiles.active:prod}")
    private String activeProfile;

    /**
     * 处理业务异常。
     *
     * @param e 业务异常
     * @return 失败响应
     */
    @ExceptionHandler(BusinessException.class)
    public R<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常：code={}, message={}", e.getCode(), e.getMessage());
        return R.fail(e.getCode(), e.getMessage());
    }

    /**
     * 处理参数校验异常。
     *
     * @param e 参数异常
     * @return 失败响应
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public R<Void> handleIllegalArgumentException(IllegalArgumentException e) {
        log.warn("参数校验失败：{}", e.getMessage());
        return R.fail(BusinessCode.PARAM_INVALID.getCode(), e.getMessage());
    }

    /**
     * 处理空指针异常（常见的数据缺失问题）。
     *
     * @param e 空指针异常
     * @return 失败响应
     */
    @ExceptionHandler(NullPointerException.class)
    public R<Void> handleNullPointerException(NullPointerException e) {
        log.error("空指针异常：", e);
        String message = isDevEnvironment()
                ? "空指针异常：" + e.getMessage()
                : BusinessCode.SYSTEM_ERROR.getMsg();
        return R.fail(BusinessCode.SYSTEM_ERROR.getCode(), message);
    }

    /**
     * 处理其他未捕获异常。
     *
     * @param e 异常
     * @return 失败响应
     */
    @ExceptionHandler(Exception.class)
    public R<Void> handleException(Exception e) {
        log.error("系统异常：", e);
        // 开发环境返回详细错误信息
        String message = isDevEnvironment()
                ? e.getClass().getSimpleName() + ": " + e.getMessage()
                : BusinessCode.SYSTEM_ERROR.getMsg();
        return R.fail(BusinessCode.SYSTEM_ERROR.getCode(), message);
    }

    /**
     * 判断是否为开发环境。
     */
    private boolean isDevEnvironment() {
        return "dev".equalsIgnoreCase(activeProfile) || "local".equalsIgnoreCase(activeProfile);
    }
}
